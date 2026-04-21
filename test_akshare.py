"""测试 akshare 接口覆盖度 + 稳定性（v2：股价用新浪源）"""
import akshare as ak
import pandas as pd
import sys
import io
import time
import os

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_rows', 30)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)


def retry(fn, max_tries=3, sleep_s=2):
    for i in range(max_tries):
        try:
            return fn()
        except Exception as e:
            if i == max_tries - 1:
                raise
            time.sleep(sleep_s)


def get_price_history(code, exchange_prefix):
    """用多个数据源兜底"""
    # 方法 1: 新浪 stock_zh_a_daily（symbol 需带 sh/sz 前缀）
    try:
        prefix_lower = exchange_prefix.lower()
        df = ak.stock_zh_a_daily(symbol=prefix_lower + code,
                                  start_date="20230101", end_date="20260421",
                                  adjust="qfq")
        return df, "新浪"
    except Exception as e1:
        pass

    # 方法 2: 东财带重试
    try:
        df = retry(lambda: ak.stock_zh_a_hist(symbol=code, period="daily",
                                              start_date="20230101", end_date="20260421",
                                              adjust="qfq"), max_tries=2, sleep_s=3)
        return df, "东财"
    except Exception as e2:
        raise Exception(f"新浪失败 + 东财失败: {e2}")


def test_stock(code, name, exchange_prefix="SH"):
    print("\n" + "=" * 70)
    print(f"📊 {name} ({exchange_prefix}{code})")
    print("=" * 70, flush=True)

    # 1. 主营构成
    print("\n[1] 主营构成（第 2 维纯度）", flush=True)
    try:
        df = retry(lambda: ak.stock_zygc_em(symbol=exchange_prefix + code))
        latest_date = df['报告日期'].iloc[0]
        latest = df[(df['报告日期'] == latest_date) & (df['分类类型'] == '按行业分类')]
        if len(latest) == 0:
            latest = df[(df['报告日期'] == latest_date) & (df['分类类型'] == '按产品分类')]
        print(f"  ✅ 最新报告期: {latest_date}", flush=True)
        for _, r in latest.iterrows():
            print(f"    {r['主营构成']:<30} 收入 {r['主营收入']/1e8:>7.2f}亿 占比 {r['收入比例']*100:>5.1f}% 毛利 {r['毛利率']*100:>5.1f}%", flush=True)
    except Exception as e:
        print(f"  ❌ 失败: {e}", flush=True)

    # 2. 近几年归母净利润
    print("\n[2] 近 4 年归母净利润（笨韭双击检测）", flush=True)
    try:
        df = retry(lambda: ak.stock_financial_abstract(symbol=code))
        row = df[df['指标'] == '归母净利润']
        if len(row) > 0:
            year_cols = [c for c in df.columns if c.endswith('1231') and c[:4] in ['2021', '2022', '2023', '2024']]
            year_cols.sort()
            latest_q = sorted([c for c in df.columns if c.startswith('2025')])[-1] if any(c.startswith('2025') for c in df.columns) else None
            for c in year_cols:
                val = row[c].values[0]
                print(f"    {c[:4]} 全年归母净利: {val/1e8:>7.2f} 亿", flush=True)
            if latest_q:
                val = row[latest_q].values[0]
                quarter = int(latest_q[4:6])//3
                q_label = f"{latest_q[:4]}Q{quarter}累计" if quarter < 4 else f"{latest_q[:4]}全年"
                print(f"    {q_label} 归母:    {val/1e8:>7.2f} 亿  ← 最新", flush=True)
    except Exception as e:
        print(f"  ❌ 失败: {e}", flush=True)

    # 3. 股价（新浪 + 东财兜底）
    print("\n[3] 近 3 年股价历史低点与当前位置（第 3 维估值位置）", flush=True)
    try:
        df, source = get_price_history(code, exchange_prefix)
        # 字段名：新浪用 'low'/'high'/'close'/'date'，东财用中文
        low_col = '最低' if '最低' in df.columns else 'low'
        high_col = '最高' if '最高' in df.columns else 'high'
        close_col = '收盘' if '收盘' in df.columns else 'close'
        date_col = '日期' if '日期' in df.columns else 'date'

        min_price = df[low_col].min()
        min_date = df.loc[df[low_col].idxmin(), date_col]
        latest_close = df.iloc[-1][close_col]
        latest_date = df.iloc[-1][date_col]
        涨幅 = (latest_close - min_price) / min_price * 100
        max_price = df[high_col].max()
        max_date = df.loc[df[high_col].idxmax(), date_col]
        print(f"  ✅ 数据源: {source}  共 {len(df)} 个交易日", flush=True)
        print(f"      近3年最低: {min_price:>7.2f} ({min_date})", flush=True)
        print(f"      近3年最高: {max_price:>7.2f} ({max_date})", flush=True)
        print(f"      最新收盘: {latest_close:>7.2f} ({latest_date})", flush=True)
        print(f"      距最低点涨幅: {涨幅:>6.1f}%  ← ≤20%=满分，每多1%扣1分", flush=True)
    except Exception as e:
        print(f"  ❌ 失败: {e}", flush=True)


STOCKS = [
    ("603308", "应流股份", "SH"),
    ("688213", "思特威",   "SH"),
]

for code, name, ex in STOCKS:
    test_stock(code, name, ex)
    time.sleep(1)

print("\n" + "=" * 70, flush=True)
print("测试完成", flush=True)
print("=" * 70, flush=True)
