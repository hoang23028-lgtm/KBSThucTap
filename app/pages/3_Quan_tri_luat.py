"""Quản trị tập luật hệ chuyên gia (TinyDB CRUD)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import utils  # noqa: F401

import streamlit as st

from src.config import ADMIN_PASSWORD, COURSE_LABELS_VI, COURSES, MAJOR_LABELS_VI, MAJORS
from src.expert_system_v2 import ExpertSystem, OPERATORS

st.set_page_config(page_title="Quản trị luật", page_icon="⚙️", layout="wide")

st.title("⚙️ Quản trị Tập luật Chuyên gia")
st.caption("CRUD luật suy diễn lưu trên TinyDB — không cần sửa code")


def check_admin() -> bool:
    if st.session_state.get("admin_authenticated"):
        return True
    st.warning("🔒 Khu vực quản trị — yêu cầu xác thực")
    pwd = st.text_input("Mật khẩu quản trị", type="password")
    if st.button("Đăng nhập"):
        if pwd == ADMIN_PASSWORD:
            st.session_state["admin_authenticated"] = True
            st.rerun()
        else:
            st.error("Mật khẩu không đúng")
    return False


if not check_admin():
    st.stop()

if st.sidebar.button("Đăng xuất"):
    st.session_state.pop("admin_authenticated", None)
    st.rerun()

expert = ExpertSystem()
rules = expert.get_all_rules()

st.sidebar.metric("Tổng số luật", len(rules))
active_count = sum(1 for r in rules if r.get("active", True))
st.sidebar.metric("Luật đang bật", active_count)

tab_list, tab_add, tab_search = st.tabs(["📋 Danh sách luật", "➕ Thêm luật mới", "🔍 Tìm kiếm"])

with tab_list:
    if st.button("🔄 Khôi phục luật mặc định", type="secondary"):
        n = expert.seed_default_rules()
        st.success(f"Đã khôi phục {n} luật mặc định")
        st.rerun()

    for rule in rules:
        rid = rule.get("doc_id") or rule.get("id")
        status = "🟢" if rule.get("active", True) else "🔴"
        action_label = "Cộng điểm" if rule["action_type"] == "boost" else "Loại trừ"
        major_vi = MAJOR_LABELS_VI.get(rule["target_major"], rule["target_major"])

        with st.expander(f"{status} #{rid} — {rule['name']} → {major_vi} ({action_label})"):
            st.markdown(f"**Mô tả:** {rule.get('description', '—')}")
            st.markdown(f"**Logic:** {rule.get('logic', 'AND')} | **Trọng số:** {rule.get('weight', 0)}")

            # Parse conditions if it's a string (from SQLite)
            conditions = rule.get("conditions", [])
            if isinstance(conditions, str):
                import json
                try:
                    conditions = json.loads(conditions)
                except:
                    conditions = []
            
            cond_text = []
            for c in conditions:
                if isinstance(c, dict):
                    course_vi = COURSE_LABELS_VI.get(c.get("course", ""), c.get("course", ""))
                    cond_text.append(f"{course_vi} {c.get('operator', '')} {c.get('value', '')}")
            st.markdown("**Điều kiện:** " + (" AND ".join(cond_text) if rule.get("logic", "AND") == "AND" else " OR ".join(cond_text)))

            c1, c2, c3 = st.columns(3)
            with c1:
                new_active = st.toggle("Kích hoạt", value=rule.get("active", True), key=f"toggle_{rid}")
                if new_active != rule.get("active", True):
                    expert.toggle_rule(rid, new_active)
                    st.rerun()
            with c2:
                if st.button("✏️ Sửa", key=f"edit_{rid}"):
                    st.session_state["edit_rule_id"] = rid
            with c3:
                if st.button("🗑️ Xóa", key=f"del_{rid}"):
                    expert.delete_rule(rid)
                    st.success(f"Đã xóa luật #{rid}")
                    st.rerun()

    if "edit_rule_id" in st.session_state:
        edit_id = st.session_state["edit_rule_id"]
        edit_rule = expert.get_rule(edit_id)
        if edit_rule:
            st.divider()
            st.subheader(f"Sửa luật #{edit_id}")
            with st.form("edit_form"):
                name = st.text_input("Tên luật", value=edit_rule["name"])
                description = st.text_area("Mô tả", value=edit_rule.get("description", ""))
                target = st.selectbox(
                    "Chuyên ngành đích",
                    MAJORS,
                    index=MAJORS.index(edit_rule["target_major"]),
                    format_func=lambda m: MAJOR_LABELS_VI.get(m, m),
                )
                action = st.selectbox(
                    "Loại hành động",
                    ["boost", "exclude"],
                    index=0 if edit_rule["action_type"] == "boost" else 1,
                    format_func=lambda x: "Cộng điểm (boost)" if x == "boost" else "Loại trừ (exclude)",
                )
                weight = st.number_input(
                    "Trọng số (0–1)",
                    min_value=0.0,
                    max_value=1.0,
                    value=float(edit_rule.get("weight", 0.1)),
                    step=0.01,
                )
                logic = st.selectbox("Logic điều kiện", ["AND", "OR"], index=0 if edit_rule.get("logic", "AND") == "AND" else 1)

                st.markdown("**Điều kiện 1**")
                c1, c2, c3 = st.columns(3)
                cond0 = edit_rule["conditions"][0] if edit_rule.get("conditions") else {}
                course1 = c1.selectbox(
                    "Môn 1",
                    COURSES,
                    index=COURSES.index(cond0.get("course", COURSES[0])) if cond0.get("course") in COURSES else 0,
                    format_func=lambda c: COURSE_LABELS_VI.get(c, c),
                    key="edit_c1",
                )
                op1 = c2.selectbox("Toán tử 1", list(OPERATORS.keys()), index=list(OPERATORS.keys()).index(cond0.get("operator", ">=")), key="edit_o1")
                val1 = c3.number_input("Ngưỡng 1", value=float(cond0.get("value", 70)), key="edit_v1")

                use_cond2 = st.checkbox("Thêm điều kiện 2", value=len(edit_rule.get("conditions", [])) > 1)
                conditions = [{"course": course1, "operator": op1, "value": val1}]
                if use_cond2:
                    cond1 = edit_rule["conditions"][1] if len(edit_rule.get("conditions", [])) > 1 else {}
                    c1, c2, c3 = st.columns(3)
                    course2 = c1.selectbox(
                        "Môn 2",
                        COURSES,
                        index=COURSES.index(cond1.get("course", COURSES[1])) if cond1.get("course") in COURSES else 1,
                        format_func=lambda c: COURSE_LABELS_VI.get(c, c),
                        key="edit_c2",
                    )
                    op2 = c2.selectbox("Toán tử 2", list(OPERATORS.keys()), index=list(OPERATORS.keys()).index(cond1.get("operator", ">=")), key="edit_o2")
                    val2 = c3.number_input("Ngưỡng 2", value=float(cond1.get("value", 70)), key="edit_v2")
                    conditions.append({"course": course2, "operator": op2, "value": val2})

                if st.form_submit_button("💾 Lưu thay đổi", type="primary"):
                    updated = {
                        "name": name,
                        "description": description,
                        "conditions": conditions,
                        "logic": logic,
                        "action_type": action,
                        "target_major": target,
                        "weight": weight if action == "boost" else 0.0,
                        "active": edit_rule.get("active", True),
                    }
                    ok, msg = expert.validate_rule(updated)
                    if ok:
                        expert.update_rule(edit_id, updated)
                        del st.session_state["edit_rule_id"]
                        st.success("Cập nhật thành công!")
                        st.rerun()
                    else:
                        st.error(msg)

with tab_add:
    st.subheader("Thêm luật mới")
    with st.form("add_rule_form"):
        name = st.text_input("Tên luật *", placeholder="VD: DS - Thống kê cao")
        description = st.text_area("Mô tả", placeholder="Mô tả luật cho hội đồng / giải thích XAI")
        target = st.selectbox("Chuyên ngành đích *", MAJORS, format_func=lambda m: MAJOR_LABELS_VI.get(m, m))
        action = st.selectbox(
            "Loại hành động *",
            ["boost", "exclude"],
            format_func=lambda x: "Cộng điểm (boost)" if x == "boost" else "Loại trừ (exclude)",
        )
        weight = st.number_input("Trọng số cộng (0–1)", min_value=0.0, max_value=1.0, value=0.12, step=0.01)
        logic = st.selectbox("Logic", ["AND", "OR"])

        st.markdown("**Điều kiện**")
        c1, c2, c3 = st.columns(3)
        course1 = c1.selectbox("Môn học", COURSES, format_func=lambda c: COURSE_LABELS_VI.get(c, c), key="add_c1")
        op1 = c2.selectbox("Toán tử", list(OPERATORS.keys()), key="add_o1")
        val1 = c3.number_input("Ngưỡng điểm", value=75.0, key="add_v1")

        add_cond2 = st.checkbox("Thêm điều kiện thứ 2")
        conditions = [{"course": course1, "operator": op1, "value": val1}]
        if add_cond2:
            c1, c2, c3 = st.columns(3)
            course2 = c1.selectbox("Môn học 2", COURSES, format_func=lambda c: COURSE_LABELS_VI.get(c, c), key="add_c2")
            op2 = c2.selectbox("Toán tử 2", list(OPERATORS.keys()), key="add_o2")
            val2 = c3.number_input("Ngưỡng 2", value=75.0, key="add_v2")
            conditions.append({"course": course2, "operator": op2, "value": val2})

        if st.form_submit_button("➕ Thêm luật", type="primary"):
            new_rule = {
                "name": name,
                "description": description,
                "conditions": conditions,
                "logic": logic,
                "action_type": action,
                "target_major": target,
                "weight": weight if action == "boost" else 0.0,
                "active": True,
            }
            ok, msg = expert.validate_rule(new_rule)
            if ok:
                new_id = expert.add_rule(new_rule)
                st.success(f"Đã thêm luật #{new_id}: {name}")
                st.rerun()
            else:
                st.error(msg)

with tab_search:
    keyword = st.text_input("Từ khóa", placeholder="VD: Data Science, Mạng, loại trừ...")
    if keyword:
        found = expert.search_rules(keyword)
        if found:
            for r in found:
                st.markdown(
                    f"**#{r.doc_id} — {r['name']}** → "
                    f"{MAJOR_LABELS_VI.get(r['target_major'], r['target_major'])} | "
                    f"{r.get('description', '')}"
                )
        else:
            st.info("Không tìm thấy luật phù hợp.")

st.divider()
st.caption(f"📁 Tập luật lưu tại: `data/rules/rules.json` (TinyDB)")
