import akshare as ak
df = ak.stock_financial_report_sina(stock="sh603866", symbol="利润表")
print(df.head())