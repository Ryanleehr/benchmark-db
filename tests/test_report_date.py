"""报告期口径的单元测试。"""

import sys

import pytest

sys.path.insert(0, "src")

from metrics import is_annual_report, extract_year, year_to_report_date


@pytest.mark.parametrize("report_date, expected", [
    (20251231, True),
    (20250930, False),
    (20250630, False),
    (20250331, False),
    (20111231, True),
])
def test_is_annual_report(report_date, expected):
    assert is_annual_report(report_date) == expected


@pytest.mark.parametrize("report_date, expected", [
    (20251231, 2025),
    (20250331, 2025),
    (20111231, 2011),
    (20260630, 2026),
])
def test_extract_year(report_date, expected):
    assert extract_year(report_date) == expected


def test_year_to_report_date():
    assert year_to_report_date(2025) == 20251231


def test_roundtrip():
    """年份转报告期再转回来，应该一致。"""
    for year in [2020, 2023, 2025]:
        assert extract_year(year_to_report_date(year)) == year