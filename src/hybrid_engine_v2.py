"""Bộ suy diễn lai tối ưu: Random Forest + Hệ chuyên gia + Caching."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.config import (
    COURSE_LABELS_VI,
    HISTORY_DB,
    HYBRID_AI_WEIGHT,
    HYBRID_EXPERT_WEIGHT,
    MAJOR_LABELS_VI,
    MAJORS,
)
from src.cache import prediction_cache
from src.database import open_db
from src.expert_system_v2 import ExpertSystem
from src.ml_model_v2 import MajorClassifier


class HybridRecommendationEngine:
    def __init__(
        self,
        classifier: MajorClassifier | None = None,
        expert: ExpertSystem | None = None,
    ):
        self.classifier = classifier or MajorClassifier.load()
        self.expert = expert or ExpertSystem()
        
        # SQLite database cho history
        history_db_path = HISTORY_DB.with_suffix(".db")
        history_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_db = open_db(history_db_path)

    def _combine(
        self, ai_proba: dict[str, float], expert_proba: dict[str, float]
    ) -> dict[str, float]:
        """Kết hợp xác suất từ AI và hệ chuyên gia."""
        combined = {}
        for major in MAJORS:
            ai_p = ai_proba.get(major, 0.0)
            ex_p = expert_proba.get(major, 0.0)
            combined[major] = (
                HYBRID_AI_WEIGHT * ai_p + HYBRID_EXPERT_WEIGHT * ex_p
            )

        total = sum(combined.values())
        if total > 0:
            combined = {k: round(v / total, 4) for k, v in combined.items()}
        return combined

    def recommend(
        self, scores: dict, student_id: str = "", save_history: bool = True
    ) -> dict[str, Any]:
        """
        Gợi ý chuyên ngành với caching.
        
        Args:
            scores: dict với điểm các môn học
            student_id: ID sinh viên (optional)
            save_history: có lưu vào history không
        
        Returns:
            dict với gợi ý, xác suất, lời giải thích, ...
        """
        # Kiểm tra cache trước
        cached_result = prediction_cache.get(scores)
        if cached_result is not None:
            # Lấy từ cache (bỏ qua student_id và save_history)
            return cached_result

        # Không có cache → tính toán
        ai_proba = self.classifier.predict_proba(scores)
        expert_proba, fired_rules = self.expert.infer(scores)
        final_proba = self._combine(ai_proba, expert_proba)

        ranked = sorted(final_proba.items(), key=lambda x: x[1], reverse=True)
        top_major = ranked[0][0]
        top_features = self.classifier.get_top_features(scores, top_n=3)

        explanations = self._build_explanations(
            top_major, ai_proba, expert_proba, final_proba, fired_rules, top_features
        )

        result = {
            "recommended_major": top_major,
            "recommended_major_vi": MAJOR_LABELS_VI.get(top_major, top_major),
            "confidence": final_proba[top_major],
            "ranking": [
                {
                    "major": m,
                    "major_vi": MAJOR_LABELS_VI.get(m, m),
                    "final_score": final_proba[m],
                    "ai_score": ai_proba.get(m, 0),
                    "expert_score": expert_proba.get(m, 0),
                }
                for m, _ in ranked
            ],
            "ai_prediction": max(ai_proba, key=ai_proba.get),
            "ai_proba": ai_proba,
            "expert_proba": expert_proba,
            "final_proba": final_proba,
            "fired_rules": fired_rules,
            "explanations": explanations,
            "top_features": [
                {
                    "course": c,
                    "course_vi": COURSE_LABELS_VI.get(c, c),
                    "score": s,
                    "importance": imp,
                }
                for c, s, imp in top_features
            ],
        }

        # Cache result trước khi save history
        prediction_cache.set(scores, result)

        if save_history:
            self._save_history(student_id, scores, result)

        return result

    def _build_explanations(
        self,
        top_major: str,
        ai_proba: dict,
        expert_proba: dict,
        final_proba: dict,
        fired_rules: list,
        top_features: list,
    ) -> list[str]:
        """Xây dựng lời giải thích cho gợi ý."""
        lines = []
        ai_pct = ai_proba.get(top_major, 0) * 100
        ex_pct = expert_proba.get(top_major, 0) * 100
        final_pct = final_proba.get(top_major, 0) * 100

        lines.append(
            f"🤖 **AI (Random Forest)** dự đoán **{MAJOR_LABELS_VI.get(top_major, top_major)}** "
            f"với xác suất {ai_pct:.1f}%."
        )

        relevant_rules = [r for r in fired_rules if r["target_major"] == top_major]
        if relevant_rules:
            rule_names = ", ".join(f"Luật #{r['rule_id']}: {r['name']}" for r in relevant_rules)
            lines.append(
                f"📋 **Hệ chuyên gia** xác nhận qua {len(relevant_rules)} luật ({rule_names}), "
                f"đóng góp {ex_pct:.1f}%."
            )
        else:
            lines.append(
                f"📋 **Hệ chuyên gia** không kích hoạt luật trực tiếp cho ngành này (đóng góp {ex_pct:.1f}%)."
            )

        feat_desc = ", ".join(
            f"{COURSE_LABELS_VI.get(c, c)} ({s:.0f}đ)" for c, s, _ in top_features
        )
        lines.append(f"📊 Các môn ảnh hưởng mạnh: {feat_desc}.")

        lines.append(
            f"⚖️ **Kết hợp lai** ({HYBRID_AI_WEIGHT*100:.0f}% AI + {HYBRID_EXPERT_WEIGHT*100:.0f}% Chuyên gia): "
            f"**{final_pct:.1f}%** cho {MAJOR_LABELS_VI.get(top_major, top_major)}."
        )

        exclude_rules = [r for r in fired_rules if r["action_type"] == "exclude"]
        if exclude_rules:
            excluded = ", ".join(
                MAJOR_LABELS_VI.get(r["target_major"], r["target_major"]) for r in exclude_rules
            )
            lines.append(f"🚫 Các ngành bị loại trừ bởi luật chuyên gia: {excluded}.")

        return lines

    def _save_history(self, student_id: str, scores: dict, result: dict) -> None:
        """Lưu lịch sử gợi ý vào SQLite history database."""
        self.history_db.insert(
            {
                "timestamp": datetime.now().isoformat(),
                "student_id": student_id,
                "scores": scores,
                "recommended_major": result["recommended_major"],
                "confidence": result["confidence"],
                "ranking": result["ranking"],
                "fired_rules": result["fired_rules"],
                "explanations": result["explanations"],
            }
        )

    def get_cache_stats(self) -> dict:
        """Lấy thống kê cache."""
        return {
            "prediction_cache": prediction_cache.stats(),
        }

    def clear_cache(self) -> None:
        """Xóa cache."""
        prediction_cache.clear()

    def get_history(self, limit: int = 50) -> list[dict]:
        """Lấy lịch sử gợi ý (mới nhất trước)."""
        records = self.history_db.all()
        # SQLite returns in order, so reverse to get newest first
        return list(reversed(records[-limit:]))

    def compare_methods(self, scores: dict) -> dict:
        """So sánh 3 phương pháp: chỉ AI, chỉ chuyên gia, lai."""
        ai_proba = self.classifier.predict_proba(scores)
        expert_proba, _ = self.expert.infer(scores)
        hybrid_proba = self._combine(ai_proba, expert_proba)

        return {
            "ai_only": max(ai_proba, key=ai_proba.get),
            "expert_only": max(expert_proba, key=expert_proba.get),
            "hybrid": max(hybrid_proba, key=hybrid_proba.get),
            "ai_proba": ai_proba,
            "expert_proba": expert_proba,
            "hybrid_proba": hybrid_proba,
        }
