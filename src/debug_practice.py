def calc_average_revenue(companies_data):
    total = 0
    count = 0
    for company in companies_data:
        total = total + company["revenue"]
        count = count + 1
    average = total / count
    return average


data = [
    {"name": "桃李面包", "revenue": 5000},
    {"name": "立高食品", "revenue": 3000},
    {"name": "元祖股份", "revenue": 4000},
]

result = calc_average_revenue(data)
print(f"平均营收: {result}")
