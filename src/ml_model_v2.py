"""Mô hình Random Forest với hyperparameter tuning tối ưu."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
    cross_val_score,
    train_test_split,
)

from src.config import COURSES, MAJORS, MODELS_DIR
from src.data_loader import build_training_dataset


class MajorClassifier:
    def __init__(self):
        self.model: RandomForestClassifier | None = None
        self.metrics: dict = {}
        self.feature_importance: dict = {}
        self.confusion: np.ndarray | None = None
        self.classification_report_str: str = ""
        self.best_params: dict = {}

    def tune_hyperparameters(
        self,
        search_type: str = "random",
        n_iter: int = 20,
        cv_folds: int = 5,
        random_state: int = 42,
    ) -> dict:
        """
        Tuning hyperparameters dùng GridSearchCV hoặc RandomizedSearchCV.
        
        Args:
            search_type: 'grid' cho GridSearchCV (tuần tự, chậm), 
                        'random' cho RandomizedSearchCV (nhanh hơn)
            n_iter: số combinations để test (nếu random search)
            cv_folds: số folds cho cross-validation
            random_state: seed for reproducibility
        
        Returns:
            dict với best_params và best_score
        """
        X, y, _ = build_training_dataset()
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state, stratify=y
        )

        # Parameter grid để tìm best hyperparameters
        param_grid = {
            "n_estimators": [100, 150, 200, 250, 300],
            "max_depth": [10, 12, 14, 15, 16, 18, 20],
            "min_samples_split": [2, 3, 5, 7],
            "min_samples_leaf": [1, 2, 3, 4],
            "max_features": ["sqrt", "log2"],
            "class_weight": ["balanced", "balanced_subsample"],
        }

        base_model = RandomForestClassifier(
            random_state=random_state,
            n_jobs=-1,
        )

        if search_type == "grid":
            print(f"Running GridSearchCV with {cv_folds}-fold CV...")
            searcher = GridSearchCV(
                base_model,
                param_grid,
                cv=cv_folds,
                scoring="f1_macro",
                n_jobs=-1,
                verbose=2,
            )
        else:  # random search (default - faster)
            print(f"Running RandomizedSearchCV ({n_iter} iterations, {cv_folds}-fold CV)...")
            searcher = RandomizedSearchCV(
                base_model,
                param_grid,
                n_iter=n_iter,
                cv=cv_folds,
                scoring="f1_macro",
                random_state=random_state,
                n_jobs=-1,
                verbose=2,
            )

        searcher.fit(X_train, y_train)

        self.best_params = searcher.best_params_
        self.model = searcher.best_estimator_

        # Evaluate trên test set
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="macro")

        return {
            "best_params": self.best_params,
            "best_cv_score": round(searcher.best_score_, 4),
            "test_accuracy": round(accuracy, 4),
            "test_f1_macro": round(f1, 4),
        }

    def train(
        self,
        test_size: float = 0.2,
        random_state: int = 42,
        use_tuned_params: bool = False,
        tune_search: str = "random",
    ) -> dict:
        """
        Huấn luyện model.
        
        Args:
            test_size: tỉ lệ test set
            random_state: seed
            use_tuned_params: nếu True, sẽ tuning hyperparameters trước
            tune_search: 'random' (nhanh) hoặc 'grid' (chính xác hơn, chậm)
        """
        X, y, _ = build_training_dataset()
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        if use_tuned_params:
            print("Tuning hyperparameters...")
            tune_result = self.tune_hyperparameters(
                search_type=tune_search,
                random_state=random_state,
            )
            print(f"Best params: {self.best_params}")
            print(f"Best CV F1-macro: {tune_result['best_cv_score']}")
        else:
            # Default optimized params (từ baseline tuning)
            self.best_params = {
                "n_estimators": 200,
                "max_depth": 15,
                "min_samples_split": 5,
                "min_samples_leaf": 2,
                "max_features": "sqrt",
                "class_weight": "balanced",
            }
            self.model = RandomForestClassifier(
                **self.best_params,
                random_state=random_state,
                n_jobs=-1,
            )
            self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)

        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring="accuracy")

        self.metrics = {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "f1_macro": round(f1_score(y_test, y_pred, average="macro"), 4),
            "cv_mean": round(cv_scores.mean(), 4),
            "cv_std": round(cv_scores.std(), 4),
            "train_size": len(X_train),
            "test_size": len(X_test),
        }
        self.confusion = confusion_matrix(y_test, y_pred, labels=MAJORS)
        self.classification_report_str = classification_report(
            y_test, y_pred, labels=MAJORS, zero_division=0
        )
        self.feature_importance = dict(
            zip(COURSES, self.model.feature_importances_.round(4))
        )
        return self.metrics

    def predict_proba(self, scores: dict | pd.Series) -> dict[str, float]:
        if self.model is None:
            raise RuntimeError("Mô hình chưa được huấn luyện. Chạy train_model.py trước.")

        if isinstance(scores, dict):
            row = pd.DataFrame([[scores.get(c, 0.0) for c in COURSES]], columns=COURSES)
        else:
            row = pd.DataFrame([[scores.get(c, 0.0) for c in COURSES]], columns=COURSES)

        proba = self.model.predict_proba(row)[0]
        classes = list(self.model.classes_)
        return {cls: round(float(p), 4) for cls, p in zip(classes, proba)}

    def predict(self, scores: dict | pd.Series) -> str:
        proba = self.predict_proba(scores)
        return max(proba, key=proba.get)

    def get_top_features(
        self, scores: dict, top_n: int = 3
    ) -> list[tuple[str, float, float]]:
        """Trả về các môn có điểm cao và quan trọng với mô hình."""
        ranked = sorted(
            self.feature_importance.items(), key=lambda x: x[1], reverse=True
        )[:top_n]
        return [(course, scores.get(course, 0), imp) for course, imp in ranked]

    def save(self, path: Path | None = None) -> Path:
        path = path or MODELS_DIR / "random_forest.joblib"
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model": self.model,
            "metrics": self.metrics,
            "feature_importance": self.feature_importance,
            "confusion": self.confusion,
            "classification_report": self.classification_report_str,
            "best_params": self.best_params,
        }
        joblib.dump(payload, path)
        return path

    @classmethod
    def load(cls, path: Path | None = None) -> "MajorClassifier":
        path = path or MODELS_DIR / "random_forest.joblib"
        if not path.exists():
            clf = cls()
            clf.train()
            clf.save(path)
            return clf

        payload = joblib.load(path)
        clf = cls()
        clf.model = payload["model"]
        clf.metrics = payload.get("metrics", {})
        clf.feature_importance = payload.get("feature_importance", {})
        clf.confusion = payload.get("confusion")
        clf.classification_report_str = payload.get("classification_report", "")
        clf.best_params = payload.get("best_params", {})
        return clf
