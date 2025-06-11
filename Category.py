import pandas as pd
import yaml
import os


# ========== Category 类 ==========
class Category:
    def __init__(self, name: str, keywords: list[str]):
        self.name = name
        self.keywords = keywords

    def to_dict(self):
        return {
            "分类": self.name,
            "关键词（逗号分隔）": ",".join(self.keywords)
        }

    @staticmethod
    def from_row(row: dict):
        return Category(
            name=row["分类"],
            keywords=[kw.strip() for kw in row["关键词（逗号分隔）"].split(",") if kw.strip()]
        )

    def update_keywords_from_text(self, text: str):
        self.keywords = [kw.strip() for kw in text.split(",") if kw.strip()]


# ========== CategoryManager 类 ==========
class CategoryManager:
    def __init__(self, config_path: str, default_data: dict):
        self.config_path = config_path
        self.default_data = default_data
        self.categories: list[Category] = self.load()
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f)
        else:
            raw_data = self.default_data

        return [Category(name, keywords) for name, keywords in raw_data.items()]

    def save(self):
        data = {cat.name: cat.keywords for cat in self.categories}
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)

    def to_dataframe(self):
        return pd.DataFrame([cat.to_dict() for cat in self.categories])

    def to_dict(self) -> dict:
        return {cat.name: cat.keywords for cat in self.categories}

    def from_dataframe(self, df: pd.DataFrame):
        self.categories = [Category.from_row(row) for _, row in df.iterrows() if row["分类"]]
