import streamlit as st
import pandas as pd
import yaml
import os

from Category import CategoryManager

# ========== Streamlit 主体 ==========
st.title("📂 分类管理工具")

# 默认数据 + 配置路径
DEFAULT_CATEGORY_MAP = {
    "餐饮": ["肯德基", "麦当劳", "奶茶", "面馆", "早餐"],
    "商超零售": ["超市", "水果", "零食", "便利店"],
    "通信": ["中国联通", "移动", "电信", "宽带"],
}
CONFIG_PATH = "category_config.yaml"

# 初始化 manager
if "manager" not in st.session_state:
    st.session_state.manager = CategoryManager(CONFIG_PATH, DEFAULT_CATEGORY_MAP)

manager: CategoryManager = st.session_state.manager

# 表格编辑
df = manager.to_dataframe()

edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "分类": st.column_config.TextColumn(disabled=False),
        "关键词（逗号分隔）": st.column_config.TextColumn(),
    }
)

# 保存
if st.button("💾 保存配置"):
    try:
        manager.from_dataframe(edited_df)
        manager.save()
        print(manager.to_dict())
        st.success("✅ 配置保存成功！")
    except Exception as e:
        st.error(f"❌ 保存失败: {e}")
