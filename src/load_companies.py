"""把公司清单导入数据库。可重复执行。"""

import sqlite3

import pandas as pd

from log_config import setup_logger

logger = setup_logger("load_companies")

DB_PATH = "data/benchmark.db"
CSV_PATH = "data/companies.csv"
SEGMENTS = {
    "603866": "烘焙-批发",
    "300973": "烘焙-原料",
    "603886": "烘焙-门店",
    "603345": "速冻-多渠道",
    "002216": "速冻-传统",
    "001215": "餐饮供应链",
    "603043": "食品+餐饮",
    "603517": "卤味连锁",
}

def load():
    df = pd.read_csv(CSV_PATH, dtype={"code": str})
    df["segment"] = df["code"].map(SEGMENTS)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        for _, row in df.iterrows():
            cursor.execute("""
            INSERT INTO companies (code, name, segment)
            VALUES (?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
                name = excluded.name,
                segment = excluded.segment
            """, (row["code"], row["name"], row["segment"]))
        conn.commit()
        logger.info(f"导入完成，共 {len(df)} 家公司")
    finally:
        conn.close()

if __name__ == "__main__":
    load()