# 艺术品投资回报预测模型：基于 Excel 假设和现金流构建的核心函数模型
import pandas as pd
import numpy as np

class ArtInvestmentModel:
    def __init__(self, assumptions_df, cashflow_df, scenario_df):
        self.assumptions = assumptions_df
        self.cashflow = cashflow_df
        self.scenario = scenario_df

    def get_price_series(self, label):
        row = self.assumptions[self.assumptions['假设项目'] == label]
        return row.iloc[0, 1:6].astype(float).values  # Y1~Y5

    def get_volume_series(self, label):
        row = self.assumptions[self.assumptions['假设项目'] == label]
        return row.iloc[0, 1:6].astype(float).values

    def predict_primary_revenue(self):
        price = self.get_price_series('一级市场单价(元/平尺)')
        volume = self.get_volume_series('一级市场销售平尺(当年)')
        return price * volume  # 每年一级市场销售额

    def predict_secondary_revenue(self):
        price = self.get_price_series('二级市场单价(元/平尺)')
        volume = self.get_volume_series('一级市场销售平尺(当年)')  # 默认比例相同
        return price * volume

    def get_cashflow(self):
        return self.cashflow[self.cashflow['项目'] == '净利润(元)'].iloc[0, 1:6].astype(float).values

    def calculate_irr(self, initial_investment):
        cashflows = [-initial_investment] + list(self.get_cashflow())
        irr = np.irr(cashflows)
        return irr

    def calculate_payback_period(self, initial_investment):
        profits = self.get_cashflow()
        cumulative = 0
        for i, p in enumerate(profits):
            cumulative += p
            if cumulative >= initial_investment:
                return i + 1
        return '无法回本'

    def scenario_revenue_matrix(self):
        matrix = self.scenario.iloc[1:, 1:].astype(float)
        matrix.index = self.scenario.iloc[1:, 0].astype(float)
        matrix.columns = self.scenario.columns[1:].astype(float)
        return matrix
