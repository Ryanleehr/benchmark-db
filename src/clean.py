KNOWN_COLUMNS = ["营业收入", "净利润", "支付给职工以及为职工支付的现金"]

def clean_column_name(raw_name):
    raw_name = raw_name.strip()
    if raw_name.startswith("其中："):
        raw_name = raw_name.replace("其中：", "")
    if raw_name in KNOWN_COLUMNS:
        return raw_name
    else:
        return "[未知] " + raw_name