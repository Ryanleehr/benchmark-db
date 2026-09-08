import numpy as np
def calc_labor_cost_ratio(labor_cost, revenue):
    """输入：人工成本、营业收入，输出：人工成本率（百分比）,当人工成本或营业收入为None或营业收入为0时，返回None"""
    if labor_cost is None or revenue == 0 or revenue is None:
        return None
    return labor_cost / revenue * 100


def calc_revenue_per_employee(revenue, headcount):
    """输入：营业收入、员工人数，输出：人均营收，当员工人数为None或0或营业收入为None时，返回None"""
    if headcount is None or headcount == 0 or revenue is None:
        return None
    return revenue / headcount


def calc_labor_cost_ratio_series(labor_cost_series, revenue_series):
    """输入：职工现金列、营业收入列。输出：人工成本率（百分比）。
    分母为0产生的 inf 会被替换成 NaN。"""
    ratio = labor_cost_series / revenue_series * 100
    return ratio.replace([np.inf, -np.inf], np.nan)


def calc_revenue_per_employee_series(revenue_series, headcount_series):
    """输入：营业收入列、员工人数列。输出：人均营收。
    分母为0产生的 inf 会被替换成 NaN。"""
    per_capita = revenue_series / headcount_series
    return per_capita.replace([np.inf, -np.inf], np.nan)

