import streamlit as st
import pandas as pd
import camelot
import plotly.express as px

from Category import CategoryManager

st.set_page_config(page_title="PDF 交易记录分析", layout="wide")

# --------------- 🧭 侧边栏 ---------------
st.sidebar.title("📋 分类管理")
# 默认数据 + 配置路径
DEFAULT_CATEGORY_MAP = {
    "餐饮": ["肯德基", "麦当劳", "奶茶", "面馆", "早餐"],
    "商超零售": ["超市", "水果", "零食", "便利店"],
    "通信": ["中国联通", "移动", "电信", "宽带", "刘猛"],
}
CONFIG_PATH = "category_config.yaml"

# 初始化 manager
if "manager" not in st.session_state:
    st.session_state.manager = CategoryManager(CONFIG_PATH, DEFAULT_CATEGORY_MAP)

manager: CategoryManager = st.session_state.manager

# 表格编辑
df = manager.to_dataframe()

edited_df = st.sidebar.data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "分类": st.column_config.TextColumn(disabled=False),
        "关键词（逗号分隔）": st.column_config.TextColumn(),
    }
)

# 保存
if st.sidebar.button("💾 保存配置"):
    try:
        manager.from_dataframe(edited_df)
        manager.save()
        st.success("✅ 配置保存成功！")
    except Exception as e:
        st.error(f"❌ 保存失败: {e}")


@st.cache_data
def extract_filtered_data(pdf_path):
    columns = [3.01, 4.32, 5.61, 7.12, 8.75, 11.12, 12.43, 13.73]
    scaled_columns = [str(int(round(x * 28.3))) for x in columns]
    columns_string = ",".join(scaled_columns)

    tables = camelot.read_pdf(
        pdf_path,
        flavor="stream",
        pages="all",
        row_tol=10,
        strip_text="\n",
        columns=[columns_string],
    )
    filtered_tables = []

    def classify_opponent(opponent):
        if not isinstance(opponent, str) or not opponent.strip():
            return "其他"

        opponent = opponent.strip()
        for category, keywords in manager.to_dict().items():
            for keyword in keywords:
                if keyword in opponent:
                    return category
        return "其他"

    KANGXI_MAP = {"⼀": "一", "⼄": "乙", "⼆": "二", "⼈": "人", "⼉": "儿", "⼊": "入", "⼋": "八", "⼏": "几", "⼑": "刀",
                  "⼒": "力", "⼔": "匕", "⼗": "十", "⼘": "卜", "⼚": "厂", "⼜": "又", "⼝": "口", "⼞": "口", "⼟": "土",
                  "⼠": "士", "⼣": "夕", "⼤": "大", "⼥": "女", "⼦": "子", "⼨": "寸", "⼩": "小", "⼫": "尸", "⼭": "山",
                  "⼯": "工", "⼰": "己", "⼲": "干", "⼴": "广", "⼸": "弓", "⼼": "心", "⼽": "戈", "⼿": "手", "⽀": "支",
                  "⽂": "文", "⽃": "斗", "⽄": "斤", "⽅": "方", "⽆": "无", "⽇": "日", "⽈": "曰", "⽉": "月", "⽊": "木",
                  "⽋": "欠", "⽌": "止", "⽍": "歹", "⽏": "毋", "⽐": "比", "⽑": "毛", "⽒": "氏", "⽓": "气", "⽔": "水",
                  "⽕": "火", "⽖": "爪", "⽗": "父", "⽚": "片", "⽛": "牙", "⽜": "牛", "⽝": "犬", "⽞": "玄", "⽟": "玉",
                  "⽠": "瓜", "⽡": "瓦", "⽢": "甘", "⽣": "生", "⽤": "用", "⽥": "田", "⽩": "白", "⽪": "皮", "⽫": "皿",
                  "⽬": "目", "⽭": "矛", "⽮": "矢", "⽯": "石", "⽰": "示", "⽲": "禾", "⽳": "穴", "⽴": "立", "⽵": "竹",
                  "⽶": "米", "⽸": "缶", "⽹": "网", "⽺": "羊", "⽻": "羽", "⽼": "老", "⽽": "而", "⽿": "耳", "⾁": "肉",
                  "⾂": "臣", "⾃": "自", "⾄": "至", "⾆": "舌", "⾈": "舟", "⾉": "艮", "⾊": "色", "⾍": "虫", "⾎": "血",
                  "⾏": "行", "⾐": "衣", "⾒": "儿", "⾓": "角", "⾔": "言", "⾕": "谷", "⾖": "豆", "⾚": "赤", "⾛": "走",
                  "⾜": "足", "⾝": "身", "⾞": "车", "⾟": "辛", "⾠": "辰", "⾢": "邑", "⾣": "酉", "⾤": "采", "⾥": "里",
                  "⾦": "金", "⾧": "长", "⾨": "门", "⾩": "阜", "⾪": "隶", "⾬": "雨", "⾭": "青", "⾮": "非", "⾯": "面",
                  "⾰": "革", "⾲": "韭", "⾳": "音", "⾴": "页", "⾵": "风", "⾶": "飞", "⾷": "食", "⾸": "首", "⾹": "香",
                  "⾺": "马", "⾻": "骨", "⾼": "高", "⿁": "鬼", "⿂": "鱼", "⿃": "鸟", "⿄": "卤", "⿅": "鹿", "⿇": "麻",
                  "⿉": "黍", "⿊": "黑", "⿍": "鼎", "⿎": "鼓", "⿏": "鼠", "⿐": "鼻", "⿒": "齿", "⿓": "龙", "⿔": "龟",
                  "⿕": "仑", "⻝": "食", "⻥": "鱼"}

    # 构造 translate 字典
    TRANSLATION_TABLE = str.maketrans(KANGXI_MAP)

    def normalize_text(text):
        if not isinstance(text, str):
            return text
        return text.translate(TRANSLATION_TABLE)

    def update_cols(row):
        val7 = row[6]
        if isinstance(val7, str) and " " in val7:
            parts = val7.split(" ", 1)  # 只分割第一个空格
            row[5] = parts[0]
            row[6] = parts[1]
        return row

    for table in tables:
        df = table.df

        df = df.apply(update_cols, axis=1)
        filtered_df = df[df.iloc[:, 0].str.match(r"^\d{8}$", na=False)]
        filtered_tables.append(filtered_df)

    result_df = pd.concat(filtered_tables, ignore_index=True)
    result_df.columns = ["日期", "时间", "收支方式", "金额", "余额", "对手信息", "对手账号", "交易渠道", "交易附言"]
    result_df["金额"] = result_df["金额"].str.replace(",", "").astype(float)
    for col in ["对手信息"]:
        result_df[col] = result_df[col].apply(normalize_text)
    for col in ["收支方式"]:
        result_df[col] = result_df[col].apply(normalize_text)
    result_df["消费类别"] = result_df["对手信息"].apply(classify_opponent)
    result_df["日期"] = pd.to_datetime(result_df["日期"], format="%Y%m%d")

    return result_df


st.title("📊 PDF 交易记录分析工具")

# 文件上传
uploaded_file = st.file_uploader("上传 PDF 文件", type="pdf")

if uploaded_file:
    with st.spinner("正在解析 PDF..."):
        df = extract_filtered_data(uploaded_file)

    st.success(f"成功提取 {len(df)} 条记录")

    # 筛选项
    st.sidebar.header("🔍 筛选条件")

    # 日期范围
    min_date = df["日期"].min()
    max_date = df["日期"].max()
    date_range = st.sidebar.date_input("日期范围", (min_date, max_date))

    # 收支方式
    iu_options = df["收支方式"].unique().tolist()
    # 排除 "正常还款"
    exclude_items = ["正常还款", "程支付"]
    iu_default = [item for item in iu_options if item not in exclude_items]
    iu_channels = st.sidebar.multiselect("收支方式", iu_options, default=iu_default)

    # 对手
    opponent_options = df["对手信息"].unique().tolist()
    opponent_channels = st.sidebar.multiselect("对手信息", opponent_options, default=[])

    # 渠道
    channel_options = df["交易渠道"].unique().tolist()
    selected_channels = st.sidebar.multiselect("交易渠道", channel_options, default=[])

    # 类别
    category_options = df["消费类别"].unique().tolist()
    selected_categories = st.sidebar.multiselect("消费类别", category_options, default=[])

    # 应用筛选
    filtered_df = df[
        (df["日期"] >= pd.to_datetime(date_range[0])) &
        (df["日期"] <= pd.to_datetime(
            date_range[1] if date_range and len(date_range) >= 2 and date_range[1] else pd.Timestamp.today()))

        ]

    if opponent_channels:
        filtered_df = filtered_df[filtered_df["对手信息"].isin(opponent_channels)]

    if selected_channels:
        filtered_df = filtered_df[filtered_df["交易渠道"].isin(selected_channels)]

    if selected_categories:
        filtered_df = filtered_df[filtered_df["消费类别"].isin(selected_categories)]

    if iu_channels:
        filtered_df = filtered_df[filtered_df["收支方式"].isin(iu_channels)]

    # 显示结果
    st.subheader("📌 统计结果")
    st.metric("总金额", f"{filtered_df['金额'].sum():,.2f}")
    st.metric("交易笔数", f"{len(filtered_df)}")

    st.subheader("📈 各类消费汇总")

    # 分组统计金额和笔数
    category_summary = (
        filtered_df.groupby("消费类别")
        .agg(总金额=("金额", "sum"), 笔数=("金额", "count"), 平均单笔=("金额", "mean"))
        .sort_values("总金额", ascending=False)
        .reset_index()
    )

    # 显示结果表格
    st.dataframe(category_summary, use_container_width=True)

    st.subheader("📈 各类消费汇总饼图")
    # 仅保留支出类数据（总金额 < 0）
    expense_summary = category_summary[
        (category_summary["总金额"] < 0)
    ].copy()
    expense_summary["支出金额"] = expense_summary["总金额"].abs()  # 转为正数用于饼图显示

    # 饼图展示
    fig = px.pie(
        expense_summary,
        names="消费类别",
        values="支出金额",
        title="各类消费占比（按总金额）",
        hole=0.3  # 可选：让饼图中间有空洞变成环形图
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 交易明细")
    columns_to_show = [col for col in filtered_df.columns if col != "余额"]
    st.dataframe(filtered_df[columns_to_show], use_container_width=True)

    st.download_button("下载结果 CSV", filtered_df.to_csv(index=False), "筛选结果.csv", "text/csv")

else:
    st.info("请上传一份 PDF 文件以开始分析。")
