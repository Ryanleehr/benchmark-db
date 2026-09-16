"""指标计算的单元测试。"""

import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, "src")

from metrics import calc_labor_cost_ratio_series


def test_normal_calculation():
    """正常情况：150 / 1000 = 15%"""
    labor = pd.Series([150.0])
    revenue = pd.Series([1000.0])
    result = calc_labor_cost_ratio_series(labor, revenue)
    assert result.iloc[0] == 15.0

def test_revenue_is_zero():
    """分母为 0 应返回 NaN，不能是 inf。"""
    labor = pd.Series([200.0])
    revenue = pd.Series([0.0])
    result = calc_labor_cost_ratio_series(labor, revenue)
    assert pd.isna(result.iloc[0])


def test_labor_is_nan():
    """分子缺失应返回 NaN。"""
    labor = pd.Series([np.nan])
    revenue = pd.Series([1000.0])
    result = calc_labor_cost_ratio_series(labor, revenue)
    assert pd.isna(result.iloc[0])


def test_revenue_is_nan():
    """分母缺失应返回 NaN。"""
    labor = pd.Series([150.0])
    revenue = pd.Series([np.nan])
    result = calc_labor_cost_ratio_series(labor, revenue)
    assert pd.isna(result.iloc[0])


def test_inf_does_not_pollute_mean():
    """有除零行时，平均值仍应正常计算。"""
    labor = pd.Series([150.0, 200.0, 300.0])
    revenue = pd.Series([1000.0, 0.0, 2000.0])
    result = calc_labor_cost_ratio_series(labor, revenue)
    assert result.mean() == 15.0


@pytest.mark.parametrize("labor, revenue, expected", [
    (150.0, 1000.0, 15.0),
    (200.0, 1000.0, 20.0),
    (0.0, 1000.0, 0.0),
    (1000.0, 1000.0, 100.0),
    (2500.0, 10000.0, 25.0),
])
def test_various_ratios(labor, revenue, expected):
    """多组正常输入的计算结果。"""
    result = calc_labor_cost_ratio_series(
        pd.Series([labor]), pd.Series([revenue])
    )
    assert result.iloc[0] == expected