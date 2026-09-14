"""把手工维护的员工人数导入数据库。"""

import sqlite3

import pandas as pd

DB_PATH = "data/benchmark.db"
CSV_PATH = "data/headcount.csv"


def load():
    df = pd.read_csv(CSV_PATH, dtype={"code": str})
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
        INSERT INTO headcount (code, year, headcount, source)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(code, year) DO UPDATE SET
            headcount = excluded.headcount,
            source = excluded.source
        """, (row["code"], int(row["year"]), int(row["headcount"]), row["source"]))

    conn.commit()
    count = pd.read_sql("SELECT COUNT(*) AS cnt FROM headcount", conn)
    conn.close()
    print(f"导入完成，headcount 表当前共 {count.iloc[0]['cnt']} 行")


if __name__ == "__main__":
    load()