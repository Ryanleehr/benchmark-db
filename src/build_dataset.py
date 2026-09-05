"""
build_dataset.py

一次性从 AKShare 拉取 8 家公司的利润表和现金流量表，
提取营业收入、净利润、支付给职工以及为职工支付的现金三个字段，
合并成一张表，存为 data/benchmark_raw.csv。

这是 Week 2 唯一一次由 AI 生成的业务代码。之后请把它当作
学习材料读透，而不是继续在它基础上迭代的起点。
"""

import akshare as ak
import pandas as pd
from pathlib import Path

# ---------- 配置 ----------

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COMPANIES_CSV = DATA_DIR / "companies.csv"
OUTPUT_CSV = DATA_DIR / "benchmark_raw.csv"

MAX_PERIODS = 24  # 近 5 年按季度算最多 20 期，多留几期做缓冲

TARGET_COLUMNS = {
    "利润表": ["营业收入", "净利润"],
    "现金流量表": ["支付给职工以及为职工支付的现金"],
}

def to_ak_symbol(code: str) -> str:
    """把 6 位股票代码转换成 AKShare 要求的 sh/sz 前缀格式。"""
    code = code.strip()
    if code.startswith("6"):
        return f"sh{code}"
    if code.startswith(("0", "3")):
        return f"sz{code}"
    raise ValueError(f"无法判断交易所前缀: {code}")


def fetch_report(symbol: str, report_type: str) -> pd.DataFrame:
    """拉取单家公司单张报表的原始数据。"""
    df = ak.stock_financial_report_sina(stock=symbol, symbol=report_type)
    return df.head(MAX_PERIODS)


def extract_fields(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """从原始报表里只挑出我们关心的列，连同报告日一起返回。"""
    keep = ["报告日"] + [c for c in columns if c in df.columns]
    missing = [c for c in columns if c not in df.columns]
    if missing:
        print(f"  ⚠️  未找到列: {missing}（原始表共 {len(df.columns)} 列，科目名称可能不一致）")
    return df[keep]


def fetch_company(code: str, name: str) -> pd.DataFrame:
    """拉取单家公司的利润表 + 现金流量表，按报告日合并成一张表。"""
    symbol = to_ak_symbol(code)
    print(f"抓取 {name}（{code}）...")

    income = fetch_report(symbol, "利润表")
    income = extract_fields(income, TARGET_COLUMNS["利润表"])
   

    cashflow = fetch_report(symbol, "现金流量表")
    cashflow = extract_fields(cashflow, TARGET_COLUMNS["现金流量表"])
    

    merged = pd.merge(income, cashflow, on="报告日", how="outer")
    merged.insert(0, "code", code)
    merged.insert(1, "name", name)
  
    
    return merged


def main():
    companies = pd.read_csv(COMPANIES_CSV, dtype={"code": str})

    all_data = []
    for _, row in companies.iterrows():
        try:
            df = fetch_company(row["code"], row["name"])
            all_data.append(df)
        except Exception as e:
            print(f"  ❌ {row['name']} 抓取失败: {e}")

    result = pd.concat(all_data, ignore_index=True)
    result = result.sort_values(["code", "报告日"], ascending=[True, False])

    DATA_DIR.mkdir(exist_ok=True)
    result.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n完成，共 {len(result)} 行，已存到 {OUTPUT_CSV}")


if __name__ == "__main__":
    main()