"""数据同步：抓取财报并写入数据库。"""

import sqlite3

import pandas as pd

from fetcher_raw import fetch_all_reports
from log_config import setup_logger

logger = setup_logger("sync", log_file="logs/sync.log")

DB_PATH = "data/benchmark.db"
COMPANIES_CSV = "data/companies.csv"

FIELD_MAP = {
    "营业收入": "revenue",
    "净利润": "net_profit",
    "支付给职工以及为职工支付的现金": "labor_cash",
}


def to_ak_symbol(code):
    """6 位代码转成带交易所前缀的格式。"""
    code = str(code).strip()
    if code.startswith("6"):
        return f"sh{code}"
    if code.startswith(("0", "3")):
        return f"sz{code}"
    raise ValueError(f"无法判断交易所前缀: {code}")


def sync_one_company(conn, code, name):
    """同步单家公司的财务数据，返回写入条数。"""
    symbol = to_ak_symbol(code)

    income = fetch_all_reports(symbol, "利润表")
    cashflow = fetch_all_reports(symbol, "现金流量表")

    rows = {}
    for report_date, payload in income.items():
        rows.setdefault(report_date, {})
        for item in payload["data"]:
            field = FIELD_MAP.get(item["item_title"])
            if field:
                rows[report_date][field] = pd.to_numeric(
                    item["item_value"], errors="coerce"
                )

    for report_date, payload in cashflow.items():
        rows.setdefault(report_date, {})
        for item in payload["data"]:
            field = FIELD_MAP.get(item["item_title"])
            if field:
                rows[report_date][field] = pd.to_numeric(
                    item["item_value"], errors="coerce"
                )

    cursor = conn.cursor()
    written = 0
    for report_date, values in rows.items():
        cursor.execute("""
        INSERT INTO financials (code, report_date, revenue, net_profit, labor_cash)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(code, report_date) DO UPDATE SET
            revenue = excluded.revenue,
            net_profit = excluded.net_profit,
            labor_cash = excluded.labor_cash
        """, (
            code,
            int(report_date),
            values.get("revenue"),
            values.get("net_profit"),
            values.get("labor_cash"),
        ))
        written += 1

    conn.commit()
    logger.info(f"{name}({code}): 写入 {written} 条")
    return written


def sync_all():
    """同步全部公司。"""
    companies = pd.read_csv(COMPANIES_CSV, dtype={"code": str})
    conn = sqlite3.connect(DB_PATH)

    total = 0
    failed = []
    try:
        for _, row in companies.iterrows():
            try:
                total += sync_one_company(conn, row["code"], row["name"])
            except Exception as e:
                logger.error(f"{row['name']}({row['code']}) 同步失败: {e}")
                failed.append(row["name"])
    finally:
        conn.close()

    logger.info(f"同步完成，共写入 {total} 条，失败 {len(failed)} 家")
    return {"written": total, "failed": failed}


if __name__ == "__main__":
    print(sync_all())