def calc_labor_cost_ratio(labor_cost, revenue):
    if labor_cost is None or revenue == 0 or revenue is None:
        return None
    return labor_cost / revenue * 100


def calc_revenue_per_employee(revenue, headcount):
    if headcount is None or headcount == 0 or revenue is None:
        return None
    return revenue / headcount