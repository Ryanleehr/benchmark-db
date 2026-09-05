from metrics import calc_labor_cost_ratio, calc_revenue_per_employee

companies = [
    {"name": "桃李面包", "revenue": 6000000, "labor_cost": 1200000, "headcount": 100},
    {"name": "立高食品", "revenue": 4000000, "labor_cost": 800000, "headcount": 0},
    {"name": "元祖股份", "revenue": 3000000, "labor_cost": None, "headcount": 50},
]

results = []
for company in companies:
    ratio = calc_labor_cost_ratio(company["labor_cost"], company["revenue"])
    per_employee = calc_revenue_per_employee(company["revenue"], company["headcount"])
    results.append({
        "name": company["name"],
        "labor_cost_ratio": ratio,
        "revenue_per_employee": per_employee,
    })

total_ratio = 0
valid_count = 0
for r in results:
    if r["labor_cost_ratio"] is not None:
        total_ratio = total_ratio + r["labor_cost_ratio"]
        valid_count = valid_count + 1
average_ratio = total_ratio / valid_count

print("各公司指标:")
for r in results:
    print(r)

print(f"平均人工成本率: {average_ratio}")