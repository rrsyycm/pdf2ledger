import streamlit as st
import pandas as pd
import yaml
import os

# 配置路径
CONFIG_PATH = "category_config.yaml"

# 默认数据
DEFAULT_CATEGORY_MAP = {
    "餐饮": ["肯德基", "麦当劳", "奶茶", "面馆", "早餐"],
    "商超零售": ["超市", "水果", "零食", "便利店"],
    "通信": ["中国联通", "移动", "电信", "宽带"],
}


# 加载配置
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return DEFAULT_CATEGORY_MAP


# 保存配置
def save_config(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True)

# 初始化 session 状态
