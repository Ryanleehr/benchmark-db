"""业务查询集合。每个函数返回一个 DataFrame。"""

import pandas as pd


def lowest_labor_cost_recent(conn, limit=3):
    """近三年平均人工成本率最低的公司。"""
    sql = """
    SELECT 
        c.name,
        ROUND(AVG(f.labor_cash * 100.0 / f.revenue), 2) AS avg_ratio
    FROM financials f
    JOIN companies c ON f.code = c.code
    WHERE f.report_date % 10000 = 1231 AND f.report_date >= 20230000
    GROUP BY c.code, c.name
    ORDER BY avg_ratio ASC
    LIMIT ?
    """
    return pd.read_sql(sql, conn, params=(limit,))


def labor_cost_by_segment(conn):
    """各赛道六年平均人工成本率。"""
    sql = """
    SELECT
        c.segment,
        ROUND(AVG(f.labor_cash * 100.0 / f.revenue), 2) AS avg_ratio
    FROM financials f
    JOIN companies c ON f.code = c.code
    WHERE f.report_date % 10000 = 1231
    GROUP BY c.segment
    ORDER BY avg_ratio ASC
    """
    return pd.read_sql(sql, conn)


def top_profit_margin(conn, report_date=20251231, limit=3):
    """指定报告期净利率最高的公司。"""
    sql = """
    SELECT
        c.name,
        ROUND(f.net_profit / f.revenue * 100, 2) AS profit_margin
    FROM financials f
    JOIN companies c ON f.code = c.code
    WHERE f.report_date = ?
    ORDER BY profit_margin DESC
    LIMIT ?
    """
    return pd.read_sql(sql, conn, params=(report_date, limit))