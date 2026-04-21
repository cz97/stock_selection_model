# 数据源调用速查

> 所有代码片段均经过实测（2026-04-21）。如果某个接口报错，先查这里有没有备用接口。

---

## 环境前置

```bash
# 检测 Python 版本（需 3.10-3.12 64 位）
py --version

# 装 akshare（如未安装）
py -m pip install akshare --quiet
```

**已知坑**：
- Python 3.14 装不上 pandas → akshare 也装不上
- 32 位 Python 装不上 pandas → 必须 64 位
- WorkBuddy 自带的 install_binary 安装 Python 不可靠，让用户自己装

---

## 核心数据接口

### 1. 主营业务构成（第 2 维 业务纯度）

```python
import akshare as ak

# 接口：东财主营业务构成
df = ak.stock_zyjg_em(symbol="603308")  # A 股直接传 6 位代码，不带后缀

# 输出字段：
# 报告日期 / 分类类型 / 主营构成 / 主营收入 / 收入比例 / 主营成本 / 成本比例 / 主营利润 / 利润比例 / 毛利率
```

**示例输出**（应流股份 2025 H1）：
```
分类类型 = 按行业分类
高温合金 + 精密铸钢件: 60.8% 营收, 毛利率 38.4%
核电及中大型铸钢件: 23.5% 营收
新型材料与装备: 10.6% 营收
```

**用法**：
- 取最新一期（一般是 H1 或 Q3）
- 找"按行业分类"或"按产品分类"的细分
- 算目标景气赛道占总营收比例 → 判断纯度门槛

---

### 2. 近 4-5 年财务（第 4 维拐点判别 + 笨韭双击）

```python
# 接口：财务摘要
df = ak.stock_financial_abstract(symbol="688213")  # 6 位代码

# 输出会包含：归母净利润、扣非净利润、营业收入、毛利率等多年数据
# 数据格式：宽表，列名是日期（如 20251231 / 20250930）
```

**示例输出**（思特威）：
```
归母净利润：
2021: 3.98 亿
2022: -0.83 亿  ← 大额亏损
2023: 0.14 亿   ← 扭亏
2024: 3.93 亿   ← 加速
2025: 10.01 亿  ← 暴增
```

**用法**：
- 取近 4-5 年归母净利润 + 营收
- 识别 V 型反转（连续亏损 → 转盈 → 加速）
- 这是判断"笨韭双击企业基本面拐点"的核心数据

---

### 3. 当前股价 + 近 3 年价格区间（第 5 维参考用）

```python
# ⚠️ 优先用新浪源（稳定）
df = ak.stock_zh_a_daily(
    symbol="sh603308",  # 注意：sh/sz 前缀小写
    start_date="20230101",
    end_date="20260421",
    adjust="qfq"  # 前复权
)

# 字段：date, open, high, low, close, volume, amount, outstanding_share, turnover
```

**备用**（东财源，可能被反爬）：
```python
df = ak.stock_zh_a_hist(
    symbol="603308",
    period="daily",
    start_date="20230101",
    end_date="20260421",
    adjust="qfq"
)
```

**用法**：
- 算当前价 vs 近 3 年最低价的涨幅（仅供参考，不机械扣分）
- 算近 60 日涨幅判断短期是否过热

---

### 4. 公司公告（第 3 维风险扫描）

```python
df = ak.stock_notice_report(symbol="全部", date="20260421")

# 字段：代码, 名称, 公告标题, 公告类型, 公告时间, 网址
# ⚠️ 这接口返回的是"全市场当日所有公告"，要自己筛选
filtered = df[df['代码'] == '603308']
```

**用法**：
- 扫描标题里的关键词："减持"、"诉讼"、"立案"、"重组"、"业绩预告"、"控股股东"
- 一票否决项识别 → 第 3 维门槛

**局限**：只能查最近若干天，要查历史公告要用其他接口或直接 web_fetch 巨潮。

---

### 5. 当前 A 股两市成交额（第 7 维流动性环境）

```python
# 上证指数日线
sh = ak.stock_zh_index_daily(symbol="sh000001")
# 深证成指日线
sz = ak.stock_zh_index_daily(symbol="sz399001")

# 当日两市成交额 = sh.amount[-1] + sz.amount[-1]
```

**判档**（参考）：
- < 2 万亿 → 冰点
- 2-2.5 万亿 → 冷淡
- 2.5-3 万亿 → 常态
- 3-3.5 万亿 → 活跃
- 3.5-4 万亿 → 危险
- ≥ 4 万亿 → 极度危险

**Web Search 兜底**：搜 "今日两市成交额 万亿" 也能拿到。

---

## 港股 / 美股数据

### 港股（2026-04-21 实测验证）

**⚠️ 踩坑记录**：akshare 港股接口签名不统一，容易传错参数。下面列的都是验证过的：

```python
# 1. 港股日线（✅ 稳定，偶发反爬，重试即可）
df = ak.stock_hk_hist(
    symbol="02498",          # 5 位代码，不带 .HK
    period="daily",
    start_date="20230101",
    end_date="20260421",
    adjust="qfq"
)
# 字段：日期, 开盘, 收盘, 最高, 最低, 成交量, 成交额, 振幅, 涨跌幅, 涨跌额, 换手率

# 2. 港股利润表/资产负债表/现金流量表（✅ 多年历史，强力推荐）
df = ak.stock_financial_hk_report_em(
    stock="02498",           # ⚠️ 参数名是 stock 不是 symbol
    symbol="利润表",         # 或 "资产负债表" / "现金流量表"
    indicator="年度"         # 或 "报告期"
)
# 返回长表：SECUCODE / REPORT_DATE / STD_ITEM_NAME / AMOUNT
# 筛选用法：df[df["STD_ITEM_NAME"] == "营业额"]
# 常用项目名：营业额、毛利、销售成本、研发费用、经营溢利、除税前溢利、本公司股东应占溢利

# 3. 港股财务分析主要指标（✅ 一次性拿多年 毛利率/净利率/ROE，推荐）
df = ak.stock_financial_hk_analysis_indicator_em(
    symbol="02498",          # ⚠️ 这个接口参数名又是 symbol
    indicator="年度"
)
# 字段：OPERATE_INCOME（营收）, GROSS_PROFIT_RATIO（毛利率%）,
#       NET_PROFIT_RATIO（净利率%）, HOLDER_PROFIT（股东应占）,
#       ROE_AVG, DEBT_ASSET_RATIO 等

# 4. 港股最新指标快照（⚠️ 只有快照一行，不是历史）
df = ak.stock_hk_financial_indicator_em(symbol="02498")  # 只接受 symbol

# 5. 港股公司资料
ak.stock_hk_company_profile_em(symbol="02498")

# 6. 港股实时快照（⚠️ 经常被反爬，失败降级到同花顺 F10 网页）
ak.stock_hk_spot_em()
ak.stock_hk_main_board_spot_em()
```

**港股年报正文**：
- 首选：港交所披露易 `hkexnews.hk`（权威原文）
- 次选：同花顺港股 F10 页面 `https://stockpage.10jqka.com.cn/HK{代码}/`（不反爬，机构评级+业绩数据齐全）
- **禁用**：雪球 `xueqiu.com`（严格反爬，`web_fetch` 拿到的是验证页）

### 美股

### 美股

```python
# 美股日线
ak.stock_us_hist(symbol="HSAI", period="daily", start_date="20230101", end_date="20260421")

# 美股财务（覆盖度低）
ak.stock_us_fundamental(symbol="HSAI")  # 不一定能用
```

**美股年报**：用 `web_fetch` 抓 SEC EDGAR 的 20-F 年报。

---

## 禁用/污染源清单（⚠️ 必读）

**以下数据源已验证不可用或污染严重，禁止在 /score 流程里依赖**：

| 源 | 禁用原因 | 替代方案 |
|---|---|---|
| **finance-data-retrieval**（Tushare 209 接口）| 2026-04 排查确认外部通道不通，鉴权走插件内部，脚本化外调失败率 100% | 对 A 股：用 akshare；对港股：用 akshare 港股接口栈 |
| **Tushare.pro 付费 API** | 付费，用户明确不走 | 同上 |
| **雪球** `xueqiu.com` | 严格反爬，`web_fetch` 拿到的是验证页；个人专栏观点倾向强 | 对官方数据走同花顺 F10 / 东财；对观点不用 |
| **知乎专栏** `zhuanlan.zhihu.com` | 自媒体污染，观点严重偏向 | 只引述原始数据，观点一律不采用 |

**信任分级原则**：
1. **权威源**：港交所披露易、SEC EDGAR、公司自己的业绩公告 PDF
2. **高可信**：东财/同花顺 F10（机构聚合官方数据）、akshare（封装前两者）
3. **中等可信**：主流财媒引用官方公告的报道（红星资本局、新浪财经-记者署名稿）
4. **低可信**：自媒体转述、公司 PR 稿（PR 稿特征：大量自媒体同步转载、措辞夸张、robosense.cn 这种 corp 子域 PR 页）
5. **禁用**：雪球/知乎个人观点、微信公众号小自媒体

**反爬处理的正确姿势**（不要一遇反爬就换 MCP）：
- `RemoteDisconnected` → `time.sleep(5)` 重试 2-3 次，多数能过
- 反复失败 → 换另一个 akshare 接口（同数据东财/新浪双源）
- 还不行 → 用 `web_fetch` 抓同花顺 F10 页面（该站不反爬）
- 最后兜底 → Web Search 拿官方新闻，**不是**自媒体评论

---

## 年报正文抓取（第 5 维"经营计划"指引提取）

**akshare 不覆盖年报全文**，必须用 `web_fetch`。

### A 股：新浪财经网页版

URL 模板（思特威 2024 年报为例）：
```
https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?stockid={6位代码}&id={公告ID}
```

**问题**：公告 ID 要先查到。两条路：
1. 用 `ak.stock_notice_report` 拿到公告标题 + 网址
2. 直接 Web Search "{公司名} 2025 年度报告 新浪 财经"

抓下来后用关键词定位段落：
- "经营计划" / "未来发展展望" / "公司战略" / "经营目标"
- 提取数字：销量 / 产能 / 出货量 / 在手订单

### 港股：港交所披露易

URL：`https://www.hkexnews.hk/`，搜公司代码找年报 PDF。
**注意**：PDF 不能用 `web_fetch` 直接读，要找 HTML 版。

### 美股：SEC EDGAR

URL：`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=20-F`

20-F 通常有 HTML 版本，可以 `web_fetch` 直接读 Risk Factors / Business 章节。

---

## 反爬应对

akshare 偶尔被反爬（特征：`RemoteDisconnected`、`ConnectionError`），处理：

1. **隔几秒重试**：`time.sleep(5)` 后重试
2. **换数据源**：`stock_zh_a_daily`（新浪）↔ `stock_zh_a_hist`（东财）
3. **换网络环境**：换 wifi 或开/关 VPN
4. **降级到 Web Search**：实在不行就让 AI 用 Web Search 查

---

## 测试模板

每次写新查询代码，先用这个模板验证：

```python
import akshare as ak
import sys
import os

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')

try:
    df = ak.<接口名>(<参数>)
    print(f"✅ 拉到 {len(df)} 条")
    print(df.head(3).to_string())
except Exception as e:
    print(f"❌ {type(e).__name__}: {e}")
```

**Windows PowerShell 输出建议**：把脚本输出重定向到文件再读，避免进度条刷屏：
```powershell
py test.py > test_result.txt 2>&1
```
