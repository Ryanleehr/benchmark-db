"""对标数据库 HTTP 服务。"""

import os
import sqlite3

import pandas as pd
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException

from src import queries

load_dotenv()

app = FastAPI(title="食品行业人效对标 API")

DB_PATH = "data/benchmark.db"
API_TOKEN = os.getenv("API_TOKEN")


def verify_token(authorization: str = Header(None)):
    """校验请求头里的 Authorization。"""
    if authorization is None:
        raise HTTPException(status_code=401, detail="缺少 Authorization 请求头")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization 格式错误，应为 'Bearer <token>'")

    token = authorization[7:]
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="token 无效")

    return token


def get_conn():
    """每次请求创建一个新连接。"""
    return sqlite3.connect(DB_PATH)


@app.get("/health")
def health_check():
    """健康检查接口。"""
    return {"status": "ok"}


@app.get("/companies")
def list_companies():
    """返回所有对标公司列表。"""
    conn = get_conn()
    try:
        df = pd.read_sql("SELECT * FROM companies", conn)
        return df.to_dict(orient="records")
    finally:
        conn.close()

@app.get("/metrics/{code}")
def company_metrics(code: str, token: str = Depends(verify_token)):
    """返回指定公司的历年人工成本率。"""
    conn = get_conn()
    try:
        sql = """
        SELECT 
            f.report_date / 10000 AS year,
            ROUND(f.labor_cash * 100.0 / f.revenue, 2) AS labor_cost_ratio,
            ROUND(f.net_profit * 100.0 / f.revenue, 2) AS profit_margin
        FROM financials f
        WHERE f.code = ? AND f.report_date % 10000 = 1231
        ORDER BY year DESC
        """
        df = pd.read_sql(sql, conn, params=(code,))
        return df.to_dict(orient="records")
    finally:
        conn.close()