import pandas as pd
from metrics import calc_labor_cost_ratio_series

def main():
    df = pd.read_csv("data/benchmark_raw.csv", dtype={"code": str})
    
    annual = df[df["报告日"] % 10000 == 1231].copy()
    annual["year"] = annual["报告日"] // 10000

    annual["人工成本率"] = calc_labor_cost_ratio_series(
        annual["支付给职工以及为职工支付的现金"],
        annual["营业收入"]
    )

    by_company = annual.groupby("name")["人工成本率"].agg(["mean", "std", "min", "max"])
    print("各公司人工成本率统计(%)：")
    print(by_company)

    print()

    by_year = annual.groupby("year")["人工成本率"].agg(["mean", "std", "min", "max"])
    print("各年度人工成本率统计(%):")
    print(by_year)

if __name__ == "__main__":
    main()
