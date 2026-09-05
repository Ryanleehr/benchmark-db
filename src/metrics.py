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