import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from art_investment_model import ArtInvestmentModel

st.set_page_config(page_title="艺术品投资回报预测", layout="wide")
st.title("🎨 艺术品投资回报预测系统")

# 年份设定
years = ["Y1", "Y2", "Y3", "Y4", "Y5"]

# --------------------
# 1. Assumptions 输入
# --------------------
st.sidebar.header("📋 输入 Assumptions")
assumption_labels = [
    "一级市场单价(元/平尺)",
    "一级市场销售平尺(当年)",
    "二级市场单价(元/平尺)",
    "二级市场预估释放(当年)",
    "二级市场拍卖成交率(%)",
    "衍生品/跨界收入(万RMB)",
    "一级市场采购成本(%)",
    "二级市场销售成本(%)",
    "团队与行政(万RMB)",
    "市场推广(万RMB)",
    "其他运营(万RMB)",
    "衍生品成本(%)",
    "所得税税率(%)"
]

assumptions_input = {}
for label in assumption_labels:
    st.sidebar.markdown(f"**{label}**")
    inputs = [st.sidebar.number_input(f"{label} {year}", value=0.0, key=f"{label}_{year}") for year in years]
    assumptions_input[label] = inputs

df_assumptions = pd.DataFrame({"假设项目": list(assumptions_input.keys())})
for i, year in enumerate(years):
    df_assumptions[year] = [v[i] for v in assumptions_input.values()]
df_assumptions["T"] = df_assumptions[years].sum(axis=1)
df_assumptions["备注"] = ""

# --------------------
# 2. CashFlow 输入
# --------------------
st.sidebar.header("💸 输入 CashFlow (净利润)")
cashflow_values = [st.sidebar.number_input(f"净利润 {year} (元)", value=0.0, key=f"cashflow_{year}") for year in years]
df_cashflow = pd.DataFrame({"项目": ["净利润(元)"], **{year: [val] for year, val in zip(years, cashflow_values)}})

# --------------------
# 3. ScenarioAnalysis 输入
# --------------------
st.sidebar.header("📉 输入 Scenario 分析")
st.sidebar.markdown("设置不同价格和面积情境")

price_steps = st.sidebar.slider("价格层级数量", 3, 10, 5)
area_steps = st.sidebar.slider("面积层级数量", 3, 10, 5)
price_range = st.sidebar.slider("价格范围（万元/平尺）", 1, 100, (30, 70))
area_range = st.sidebar.slider("面积范围（平尺）", 500, 3000, (1000, 2000))

price_levels = np.linspace(price_range[0], price_range[1], price_steps)
area_levels = np.linspace(area_range[0], area_range[1], area_steps)

scenario_matrix = pd.DataFrame(index=price_levels, columns=area_levels)
for price in price_levels:
    for area in area_levels:
        scenario_matrix.loc[price, area] = price * area

scenario_matrix = scenario_matrix.astype(float)
df_scenario = pd.DataFrame([["价格/面积"] + list(area_levels)] + [[price] + list(scenario_matrix.loc[price]) for price in price_levels])
df_scenario.columns = df_scenario.iloc[0]
df_scenario = df_scenario[1:]

# --------------------
# 模型运行与展示
# --------------------
model = ArtInvestmentModel(df_assumptions, df_cashflow, df_scenario)

investment = st.number_input("💰 初始投资额（元）", min_value=1000, max_value=10000000, value=2500)

col1, col2 = st.columns(2)
with col1:
    irr = model.calculate_irr(investment)
    st.metric("📈 IRR（内部收益率）", f"{irr*100:.2f}%")
with col2:
    payback = model.calculate_payback_period(investment)
    st.metric("📅 投资回收期", payback)

st.subheader("📊 一级市场年度销售预测")
primary = model.predict_primary_revenue()
st.line_chart(pd.Series(primary, index=years))

st.subheader("📉 敏感性分析：价格 × 面积 → 销售额")
scenario_numeric = model.scenario_revenue_matrix()
st.dataframe(scenario_numeric.style.background_gradient(cmap='YlGnBu'), use_container_width=True)
