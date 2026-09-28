"""初始化数据库表结构。可重复执行。"""

import sqlite3

from log_config import setup_logger

logger = setup_logger("init_db")

DB_PATH = "data/benchmark.db"

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS companies (
        code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        segment TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS financials (
        code TEXT NOT NULL,
        report_date INTEGER NOT NULL,
        revenue REAL,
        net_profit REAL,
        labor_cash REAL,
        PRIMARY KEY (code, report_date)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS headcount (
        code TEXT NOT NULL,
        year INTEGER NOT NULL,
        headcount INTEGER,
        source TEXT,
        PRIMARY KEY (code, year)
    )
    """,
]


def init():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        for statement in SCHEMA:
            cursor.execute(statement)
        conn.commit()
        logger.info(f"表结构初始化完成，共 {len(SCHEMA)} 张表")
    finally:
        conn.close()


if __name__ == "__main__":
    init()