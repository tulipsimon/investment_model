# art_investment_model.py
import pandas as pd
import numpy as np
import numpy_financial as npf

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
        try:
            return self.cashflow[self.cashflow['项目'] == '净利润(元)'].iloc[0, 1:6].astype(float).fillna(0).values
        except Exception as e:
            print(f"获取现金流出错: {e}")
            return [0, 0, 0, 0, 0]

    def calculate_irr(self, initial_investment):
        cashflows = [-initial_investment] + list(self.get_cashflow())
        try:
            irr = npf.irr(cashflows)
            return irr if irr is not None else 0
        except Exception as e:
            print(f"IRR 计算出错: {e}")
            return 0

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

    def irr_vs_investment(self, investment_range):
        result = []
        for invest in investment_range:
            try:
                irr = npf.irr([-invest] + list(self.get_cashflow()))
                result.append(irr * 100 if irr is not None else 0)
            except:
                result.append(0)
        return pd.Series(result, index=investment_range)
