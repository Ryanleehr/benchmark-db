"""不依赖 AKShare, 直接用 requests 抓取新浪财经财报数据。"""
import time
import requests

BASE_URL = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"

REPORT_TYPE_MAP = {
    "资产负债表": "fzb",
    "利润表": "lrb",
    "现金流量表": "llb",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    )
}


def fetch_one_page(stock_code, report_type, page=1, num=50):
    """抓取一页财报数据，返回解析后的 JSON 字典。"""
    params = {
        "paperCode": stock_code,
        "source": REPORT_TYPE_MAP[report_type],
        "type": "0",
        "page": str(page),
        "num": str(num),
    }
    r = requests.get(BASE_URL, params=params, timeout=10)
    r.raise_for_status()

    data = r.json()
    status_code = data["result"]["status"]["code"]
    if status_code != 0:
        raise RuntimeError(f"接口返回错误，code={status_code}")

    result_data = data["result"]["data"]
    if result_data is None:
        raise RuntimeError(f"未查询到数据：{stock_code}{report_type}")
        
    return data


def fetch_with_retry(stock_code, report_type, page=1, num=50, max_retries=5):
    """带重试和指数退避的抓取。"""
    delay = 1
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            return fetch_one_page(stock_code, report_type, page, num)
        except requests.HTTPError as e:
            last_error = e
            if e.response.status_code == 429 or e.response.status_code >= 500:
                if attempt < max_retries:
                    print(f"第 {attempt} 次失败({e.response.status_code}),{delay}秒后重试")
            else:
                raise
        except requests.RequestException as e:
            last_error = e
            if attempt < max_retries:
                print(f"第  {attempt} 次失败({type(e).__name__}),{delay}秒后重试")
        
        if attempt < max_retries:
            time.sleep(delay)
            delay = delay * 2
    raise RuntimeError(f"重试 {max_retries} 次后仍然失败: {last_error}")
    

def fetch_all_reports(stock_code, report_type,page_size=50):
    """抓取某公司某张报表的全部数据，自动翻页。

    返回 {报告期：数据} 的字典。
    """
    first = fetch_one_page(stock_code, report_type, page=1, num=page_size)
    total = int(first["result"]["data"]["report_count"])

    all_reports = dict(first["result"]["data"]["report_list"])

    total_pages = (total + page_size - 1) // page_size

    for page in range(2, total_pages + 1):
        time.sleep(0.5)
        data = fetch_one_page(stock_code, report_type, page=page, num=page_size)
        all_reports.update(data["result"]["data"]["report_list"])

    return all_reports

if __name__ == "__main__":
    data = fetch_one_page("sh603866", "利润表", page=1, num=5)
    print(data["result"]["data"]["report_count"])

    # 测试错误情况
    try:
        fetch_one_page("sh999999", "利润表", page=1, num=5)
    except Exception as e:
        print(f"捕获到异常: {type(e).__name__}: {e}")

    # 测试翻页
    reports = fetch_all_reports("sh603866", "利润表", page_size=50)
    print(f"共抓取 {len(reports)} 期报表")
    print(sorted(reports.keys())[:5])

    d = fetch_with_retry("sh603866", "利润表", page=1, num=5)
    print("重试版本抓取成功:", d["result"]["data"]["report_count"])

