# 数据源调用速查

> 2026-06-04 更新：主数据源已切换为 WorkBuddy 内置股票数据（westock-data）。不再依赖外部 Python 数据库。

---

## 0. 调用方式

当前环境里 `westock-data` 未必在 PATH 中。如果直接命令不可用，用脚本路径调用：

```bash
"C:/Users/dylanyuan/.workbuddy/binaries/node/versions/22.22.2/node.exe" \
"C:/Users/dylanyuan/.workbuddy/plugins/marketplaces/cb_teams_marketplace/plugins/finance-data/skills/westock-data/scripts/index.js" \
quote sh688213
```

为了可读，下文统一写成：

```bash
westock-data <command> <args>
```

实际执行时，如果 `westock-data: command not found`，就换成上面的 Node 脚本调用形式。

---

## 1. 股票搜索与代码确认

```bash
westock-data search 思特威
westock-data search 腾讯控股
westock-data search 禾赛
```

代码格式：

| 市场 | 格式 | 示例 |
|---|---|---|
| A 股沪市/科创板 | `sh` + 6 位代码 | `sh688213` |
| A 股深市/创业板 | `sz` + 6 位代码 | `sz300750` |
| 北交所 | `bj` + 6 位代码 | `bj430047` |
| 港股 | `hk` + 5 位代码 | `hk02498` |
| 美股 | `us` + ticker | `usHSAI` |

---

## 2. 实时行情与估值快照

```bash
westock-data quote sh688213
westock-data quote sh688213,hk02498,usHSAI
westock-data quote sh000001,sz399001
```

可用字段：价格、涨跌幅、成交额、换手率、PE/PB/PS/PCF、总市值、流通市值、52 周高低、多日涨跌幅等。

**用途**：
- 当前市值
- 当前 PE / PB / PS
- 近 5/10/20/60 日涨跌幅
- 流动性环境辅助判断

---

## 3. K 线与历史价格区间

```bash
westock-data kline sh688213 --period day --limit 800
westock-data kline hk02498 --period day --limit 800
westock-data kline usHSAI --period day --limit 800
```

**用途**：
- 近 3 年最低价 / 最高价
- 当前价相对历史区间位置
- 近 60 日是否过热

注意：历史涨幅只作为参考，不机械扣分。动态预测估值优先。

---

## 4. 技术指标

```bash
westock-data technical sh688213 --group all
```

**用途**：
- 获取 MACD、KDJ、RSI、布林带、均线系统

---

## 5. 资金流向

```bash
westock-data asfund sh688213 
westock-data hkfund hk00700
```

**用途**：
- 资金流向主要用于判断主力是在进场还是出货，对于短线操作很有参考价值。

---

## 6. 当前热搜股票（市场关注度指标）

```bash
westock-data hot stock
```

**用途**：
- 查看市场当前热点股票，短线可供参考，越热越代表资金面/消息面活跃。

---

## 7. 财务报表

A 股：

```bash
westock-data finance sh688213 --type lrb --num 8
westock-data finance sh688213 --type zcfz --num 4
westock-data finance sh688213 --type xjll --num 4
```

港股：

```bash
westock-data finance hk02498 --num 4
westock-data finance hk02498 --type zhsy --num 4
```

美股：

```bash
westock-data finance usHSAI --type income --num 4
westock-data finance usHSAI --type balance --num 4
westock-data finance usHSAI --type cashflow --num 4
```

**用途**：
- 近 4-8 期营收与净利润曲线
- 判断企业基本面拐点：亏损 → 扭亏 → 加速
- 判断毛利率、研发费用、现金流变化

**实测样例：思特威 `finance sh688213 --type lrb --num 4` 可以返回 2025 全年与季度利润表。**

---

## 8. 公司简况与业务描述

```bash
westock-data profile sh688213
westock-data profile hk02498
westock-data profile usHSAI
```

**用途**：
- 公司主营业务描述
- 行业归属
- 上市日期
- 董事长、注册地址、官网等基础信息

局限：`profile` 不能替代年报里的主营构成。若需要细分收入占比，优先查年报/公告正文。

---

## 9. 公告列表与公告全文

公告列表：

```bash
westock-data notice sh688213
westock-data notice sh688213 --type 1     # 财务公告
westock-data notice sh688213 --type 6     # 风险公告
```

公告全文 / PDF 链接：

```bash
westock-data ncontent nos1225047323
```

实测：A 股公告全文有时返回 `content` 为空，但会返回 PDF 链接。遇到这种情况：
1. 用返回的 PDF 链接作为权威来源；
2. 需要正文时，用 `web_fetch` 抓公告网页或下载 PDF 后读取；
3. 不要用自媒体转述替代公告。

---

## 10. 风险事件

```bash
westock-data risk sh688213
westock-data risk sz300750 --types pledge,unlock,lawsuit,st,addition
```

限制：风险事件仅支持 A 股。

**用途**：
- 股权质押
- 解禁
- 诉讼仲裁
- 增发
- ST 风险
- 其他风险事件

风险事件结果为“暂无”不代表完全无风险，仍需做反向证伪 Web Search。

---

## 11. 一致预期

```bash
westock-data consensus sh688213
```

实测：思特威可以返回 2026-2028 一致预期，包括 revenue、netProfit、EPS、PE、PS、PB 等。

**用途**：
- 动态预测估值的参考锚
- 与自己从年报指引拆出来的估算做交叉验证

注意：一致预期是卖方预期，不是事实；只能作为参考。

---

## 12. 股东结构

```bash
westock-data shareholder sh688213
westock-data shareholder hk00700
```

**用途**：
- 十大股东 / 十大流通股东
- 股东户数变化
- 机构持仓变化
- 辅助判断筹码变化和潜在减持风险

---

## 13. 新闻、研报、评级

```bash
westock-data news sh688213 --limit 20 --type 3
westock-data report sh688213 --limit 20
westock-data rating sh688213
westock-data newsdetail <news_id>
```

**用途**：
- 新闻只作为线索，不作为独立证据
- 研报用于查一致预期和产业链信息，但结论要打折
- 评级用于观察市场共识，不作为买入理由

---

## 14. 板块与概念成份股

搜索板块：

```bash
westock-data sector --search 人工智能
westock-data sector --search 华为
westock-data sector --search 固态电池
```

查成份股：

```bash
westock-data sector <板块代码>
```

**用途**：
- `/analyze-theme` 产业链候选股初筛
- 判断赛道内纯正标的数量
- 市场辨识度里的“稀缺性”参考

---

## 15. 市场环境与流动性

指数行情：

```bash
westock-data quote sh000001
westock-data quote sz399001
```

市场资讯：

```bash
westock-data marketnews hs
westock-data hot board --limit 10
```

成交额分档参考：

| 两市成交额 | 状态 |
|---|---|
| < 2 万亿 | 冰点 |
| 2-2.5 万亿 | 冷淡 |
| 2.5-3 万亿 | 常态 |
| 3-3.5 万亿 | 活跃 |
| 3.5-4 万亿 | 危险 |
| ≥ 4 万亿 | 极度危险 |

如内置数据难以直接合成两市成交额，用 Web Search 搜“今日两市成交额 万亿”兜底。

---

## 16. 年报“经营计划 / 未来展望”抓取

内置股票数据可以给公告列表和 PDF 链接，但不一定直接给年报正文。

推荐顺序：
1. `notice <symbol> --type 1` 找年度报告；
2. `ncontent <notice_id>` 获取 PDF 链接；
3. 用 `web_fetch` 抓公告网页，或下载 PDF 后用文件读取工具分析；
4. 搜索关键词：“预计 / 计划 / 目标 / 规划 / 展望 / 指引 / 产能 / 销量 / 出货 / 订单”。

目标不是找精确净利润预测，而是提取运营指标，用于动态预测估值。

---

## 17. 数据源信任分级

| 信息源 | 可信度 | 用法 |
|---|---|---|
| 公司年报 / 季报 / 交易所公告 | 🟢 高 | 直接采信 |
| 港交所披露易 / SEC EDGAR | 🟢 高 | 直接采信 |
| WorkBuddy 内置股票数据 | 🟢 高 | 结构化查询首选 |
| 第三方权威机构（Yole / TSR / TrendForce） | 🟡 中 | 大体可信，但注意口径和付费报告偏向 |
| 卖方研报 / 一致预期 | 🟡 中 | 参考，结论打折 |
| 财经媒体 | 🟡 中 | 只采事实，不采主观结论 |
| 自媒体 / 公众号 | 🔴 低 | 仅作线索 |
| 公司 PR 稿 | 🔴 低 | 必须用年报/公告/交付数据交叉验证 |

---

## 18. 已验证结论

2026-06-04 实测通过：

```bash
quote sh688213
finance sh688213 --type lrb --num 4
notice sh688213 --type 1
risk sh688213
consensus sh688213
profile sh688213
shareholder sh688213
```

可覆盖：行情、财务、公告、风险事件、一致预期、公司简况、股东结构。

**结论**：内置股票数据已足以作为主数据源；旧的 Python 数据方案不再写入主流程。
