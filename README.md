# 美股量化分析系统

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Flask Version](https://img.shields.io/badge/flask-2.3%2B-green)
![License](https://img.shields.io/badge/license-MIT-yellow)
![Status](https://img.shields.io/badge/status-Beta-yellow)

**专业的美股技术分析与市场扫描工具**

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用文档](#使用文档) • [API 文档](#api-文档) • [开发指南](#开发指南)

</div>

---

## 📖 项目简介

美股量化分析系统是一个基于 Python 的股票分析工具，提供技术指标分析、基本面分析、新闻情绪分析和市场扫描功能。支持命令行工具和 Web 界面两种使用方式。

### 核心功能

- 📊 **技术分析**: RSI、MACD、布林带、SMA 等多种技术指标
- 💰 **基本面分析**: PE、PB、ROE、营收增长等财务指标
- 📰 **情绪分析**: 基于 NLP 的新闻情绪分析
- 🔍 **市场扫描**: 自定义筛选条件，发现投资机会
- 🌐 **Web 界面**: 专业的金融风格 UI，支持深色/浅色主题
- 📈 **图表可视化**: 交互式 K线图和技术指标图表

### 技术栈

**后端:**
- Python 3.10+
- Flask 2.3+ (Web 框架)
- yfinance (Yahoo Finance 数据)
- pandas (数据处理)
- ta (技术分析)
- TextBlob (情绪分析)

**前端:**
- 原生 HTML/CSS/JavaScript (无构建工具)
- ECharts 5.x (图表库)
- CSS Variables (主题系统)
- Responsive Design (响应式设计)

---

## ✨ 功能特性

### 1. 单股分析

完整的股票分析报告，包括：
- ✅ 实时价格和涨跌幅
- ✅ 技术指标计算和信号生成
- ✅ K线图和成交量图表
- ✅ 财务指标汇总
- ✅ 新闻情绪分析
- ✅ 综合投资建议

**示例输出：**
```
股票代码: AAPL
当前价格: $175.50 (↑ +2.35, +1.36%)

技术指标:
  RSI: 65.3 (中性)
  MACD: 1.25 (看涨)
  布林带: $170.23 - $180.45
  SMA: 50日均线 $172.50, 200日均线 $165.80 (金叉)

综合建议: 买入 (评分: 75/100)
```

### 2. 市场扫描

批量筛选股票，发现投资机会：
- 🔍 自定义筛选条件（PE、PEG、指数）
- 📊 机会评分排序
- 🏢 行业分布统计
- 📥 导出 CSV 格式数据

支持的指数：
- S&P 500
- NASDAQ 100
- Dow Jones (DJIA)
- Russell 2000

**示例输出：**
```
扫描条件: NASDAQ 100, PE < 25, PEG < 1
找到 10 只机会股票:

排名  股票代码  价格      PE     PEG    评分  行业
1     CHTR    $189.76   5.23   N/A    85    Communication Services
2     GILD    $124.91   19.35  N/A    82    Healthcare
3     PYPL    $56.89    11.41  N/A    78    Technology

行业分布: Technology (40%), Healthcare (30%), Financial (20%), Other (10%)
```

### 3. 专业 UI 设计

参考 Bloomberg Terminal 和 TradingView 设计：
- 🌓 深色/浅色主题切换
- 📱 响应式布局（桌面/平板/手机）
- 📊 专业金融图表
- 💾 数据导出（CSV + JSON）

---

## 🚀 快速开始

### 前置要求

- Python 3.10 或更高版本
- pip 或 uv (包管理器)
- Git

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/Liuzkai/AmericanMarketing.git
cd AmericanMarketing
```

2. **创建虚拟环境**

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

3. **安装依赖**

```bash
# 使用 pip
pip install -r requirements.txt

# 或使用 uv (推荐，更快)
uv pip install -r requirements.txt
```

### 使用方式

#### 方式一：命令行工具

**单股分析:**
```bash
python analyze_stock.py --ticker AAPL
```

**市场扫描:**
```bash
python market_scanner.py
```

#### 方式二：Web 界面

**启动服务器:**
```bash
python run_web.py
```

**访问页面:**
- 首页: http://localhost:5001/
- 单股分析: http://localhost:5001/analyze
- 市场扫描: http://localhost:5001/scanner
- 关于页面: http://localhost:5001/about

---

## 📚 使用文档

### CLI 工具使用

#### 单股分析

```bash
# 基本用法
python analyze_stock.py --ticker AAPL

# 简写形式
python analyze_stock.py -t NVDA

# 分析多只股票
python analyze_stock.py -t MSFT
python analyze_stock.py -t GOOGL
```

**输出内容:**
- JSON 格式的完整数据
- 中文分析报告
- 投资建议和评分

#### 市场扫描

```bash
python market_scanner.py
```

**默认筛选条件:**
- 指数: S&P 500
- PE 比率: < 25
- PEG 比率: < 1.0
- 价格: > SMA(20)

**输出文件:** `market_opportunity.csv`

### Web 界面使用

#### 单股分析页面

1. 访问 http://localhost:5001/analyze
2. 输入股票代码（如 AAPL、TSLA、NVDA）
3. 点击"分析"按钮
4. 等待 15-30 秒获取数据
5. 查看完整分析结果

**功能:**
- 实时价格和涨跌幅
- 交互式 K线图
- 技术指标详情
- 财务指标表格
- 新闻情绪仪表盘
- 导出 CSV/JSON

#### 市场扫描页面

1. 访问 http://localhost:5001/scanner
2. 设置筛选条件：
   - 选择指数
   - 设置最大 PE
   - 设置最大 PEG
   - 设置结果数量
3. 点击"开始扫描"
4. 查看扫描结果

**功能:**
- 机会股票列表
- 行业分布饼图
- 点击股票代码查看详情
- 导出 CSV

---

## 🔌 API 文档

所有 API 端点使用 `/api/v1` 前缀。

### 健康检查

```bash
GET /api/v1/health
```

**响应:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-17 20:00:00"
}
```

### 股票分析

```bash
GET /api/v1/stock/<TICKER>/analyze
```

**示例:**
```bash
curl http://localhost:5001/api/v1/stock/AAPL/analyze
```

**响应格式:**
```json
{
  "success": true,
  "data": {
    "ticker": "AAPL",
    "current_price": 175.50,
    "price_change": 2.35,
    "price_change_percent": 1.36,
    "technical_indicators": {
      "rsi": 65.3,
      "macd": 1.25,
      "signal": "Buy"
    },
    "financial_metrics": {
      "pe_ratio": 28.5,
      "pb_ratio": 45.2,
      "roe": 0.72
    },
    "sentiment": {
      "average_polarity": 0.42,
      "sentiment": "Positive"
    },
    "recommendation": {
      "action": "买入",
      "score": 75
    }
  },
  "timestamp": "2026-01-17 20:00:00"
}
```

### 快速报价

```bash
GET /api/v1/stock/<TICKER>/quote
```

**示例:**
```bash
curl http://localhost:5001/api/v1/stock/MSFT/quote
```

### 市场扫描

```bash
GET /api/v1/market/scan?index=<INDEX>&max_pe=<PE>&max_peg=<PEG>&limit=<LIMIT>
```

**参数:**
- `index`: 指数 (sp500, nasdaq, dow, russell)
- `max_pe`: 最大 PE 比率 (整数)
- `max_peg`: 最大 PEG 比率 (整数)
- `limit`: 返回结果数量 (默认 50)

**示例:**
```bash
curl "http://localhost:5001/api/v1/market/scan?index=nasdaq&max_pe=25&max_peg=1&limit=10"
```

**响应格式:**
```json
{
  "success": true,
  "data": {
    "total_scanned": 10,
    "opportunities": [
      {
        "ticker": "AAPL",
        "price": 175.50,
        "opportunity_score": 85,
        "pe": 28.5,
        "peg": 2.1,
        "sector": "Technology"
      }
    ],
    "statistics": {
      "sector_distribution": {
        "Technology": 5,
        "Healthcare": 3
      }
    }
  },
  "timestamp": "2026-01-17 20:00:00"
}
```

---

## 🛠️ 开发指南

### 项目结构

```
AmericanMarketing/
├── analyze_stock.py          # 单股分析 CLI 工具
├── market_scanner.py         # 市场扫描 CLI 工具
├── run_web.py               # Web 服务启动脚本
├── requirements.txt         # 项目依赖
├── CLAUDE.md               # 开发文档（架构、设计模式）
├── README.md               # 本文件
├── TEST_REPORT.md          # 测试报告
├── BUGFIX_REPORT.md        # Bug 修复记录
├── WEB_README.md           # Web 界面详细文档
│
├── tools/                   # 核心分析模块
│   ├── __init__.py
│   ├── market_data.py      # 数据获取（715 行）
│   └── analyzer.py         # 技术分析 + 情绪分析（784 行）
│
└── web/                     # Web 应用
    ├── __init__.py
    ├── app.py              # Flask 应用工厂
    ├── api/
    │   ├── __init__.py
    │   └── routes.py       # RESTful API 路由（349 行）
    ├── templates/          # Jinja2 模板
    │   ├── base.html      # 基础模板
    │   ├── index.html     # 首页
    │   ├── analyze.html   # 分析页
    │   ├── scanner.html   # 扫描页
    │   └── about.html     # 关于页
    └── static/            # 静态资源
        ├── css/
        │   ├── themes.css  # 主题样式
        │   └── main.css    # 主样式
        └── js/
            ├── api.js      # API 客户端
            ├── charts.js   # 图表配置
            ├── theme.js    # 主题管理
            ├── analyzer.js # 分析页逻辑
            └── scanner.js  # 扫描页逻辑
```

### 架构设计

**三层架构:**

```
┌─────────────────────────────────────┐
│     Application Layer               │
│  (CLI Tools + Web Interface)        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     Analysis Layer                  │
│  (TechnicalAnalyzer + Sentiment)    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     Data Layer                      │
│  (MarketFetcher + yfinance)         │
└─────────────────────────────────────┘
```

### 核心类说明

#### MarketFetcher (tools/market_data.py)

数据获取接口，支持：
- 价格历史数据（OHLCV）
- 财务指标（PE、PB、ROE）
- 新闻数据
- 公司信息

**特性:**
- 容错降级（yfinance → finvizfinance → 模拟数据）
- 速率限制和重试机制
- 请求延迟（1 秒）

#### TechnicalAnalyzer (tools/analyzer.py)

技术分析引擎，计算：
- RSI (相对强弱指数)
- MACD (移动平均收敛/发散)
- Bollinger Bands (布林带)
- SMA 50/200 (简单移动平均线)

**信号生成:**
- 多指标综合评分
- Buy/Sell/Neutral 分类
- 详细信号说明

#### SentimentAnalyzer (tools/analyzer.py)

情绪分析引擎，基于 TextBlob：
- 新闻标题极性分析
- 情绪分类（Very Positive → Very Negative）
- 批量处理

### 数据流

```
用户请求
    ↓
MarketFetcher.get_stock_price_history()
    ↓
yfinance API (主数据源)
    ↓ (失败)
finvizfinance (备用数据源)
    ↓ (仍失败)
生成模拟数据
    ↓
TechnicalAnalyzer.analyze()
    ↓
计算技术指标 + 生成信号
    ↓
SentimentAnalyzer.analyze_news()
    ↓
分析新闻情绪
    ↓
聚合结果 → JSON 响应
```

### 运行测试

```bash
# 测试数据获取模块
python tools/market_data.py

# 测试分析模块
python tools/analyzer.py

# 测试 finviz 数据源
python test_finviz.py
```

### 部署到生产环境

**不要使用 Flask 开发服务器！请使用 Gunicorn:**

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动生产服务器（4 个 worker）
gunicorn -w 4 -b 0.0.0.0:8000 "web.app:create_app()"

# 使用配置文件
gunicorn -c gunicorn_config.py "web.app:create_app()"
```

**生产环境检查清单:**
- [ ] 禁用 Flask debug 模式
- [ ] 添加 Redis 缓存层
- [ ] 实现 API 速率限制
- [ ] 配置 HTTPS (使用 Nginx 反向代理)
- [ ] 设置环境变量（不要硬编码密钥）
- [ ] 配置日志（使用 logging 模块）
- [ ] 添加监控（Prometheus + Grafana）

---

## ⚠️ 注意事项

### API 速率限制

**Yahoo Finance API:**
- 速率限制: ~2000 请求/小时（共享 IP）
- 建议: 添加 Redis 缓存（TTL: 5 分钟）

**Finviz:**
- 速率限制: ~100 请求/小时（免费版）
- 建议: 减少扫描频率

### 网络要求

- 需要访问国际网络（API 服务器在境外）
- ECharts 通过 CDN 加载（首次需要网络）
- 建议使用稳定的网络连接

### 数据准确性

- 数据来源: Yahoo Finance + Finviz
- 实时性: 延迟约 15 分钟
- 模拟数据: 当真实数据不可用时，系统会生成确定性模拟数据（用于技术分析演示）

**重要:** 本系统提供的信息仅供参考，不构成投资建议。

---

## 🐛 已知问题

### 1. API 速率限制

**现象:** 频繁请求会触发 429 错误

**临时解决方案:**
- 等待 5-10 分钟后重试
- 减少请求频率

**永久解决方案:**
- 添加 Redis 缓存层
- 实现请求队列

**优先级:** 高

### 2. 市场扫描速度慢

**现象:** 扫描 50 只股票需要 30-60 秒

**原因:** 同步处理，每次 API 调用需要等待

**解决方案:**
- 使用 Celery 异步任务队列
- 添加 WebSocket 进度推送

**优先级:** 中

详细问题列表请查看 [BUGFIX_REPORT.md](BUGFIX_REPORT.md)

---

## 📈 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 服务器启动时间 | ~2s | Flask 开发服务器 |
| Health Check | ~10ms | 无数据库查询 |
| 页面加载 | ~50-60ms | 模板渲染 |
| 单股分析 | 15-30s | 受限于外部 API |
| 市场扫描 (50只) | 30-60s | 同步处理 |
| 内存占用 | ~150MB | 包括 pandas/numpy |
| CPU 使用率 | 30-50% | 计算密集型任务时 |

---

## 🗺️ 路线图

### 短期目标 (1-2周)

- [x] ~~Web 界面开发~~
- [x] ~~市场扫描功能~~
- [ ] 添加 Redis 缓存层
- [ ] 优化错误提示和加载状态
- [ ] 添加单元测试

### 中期目标 (1个月)

- [ ] Celery 异步任务队列
- [ ] PostgreSQL 数据库集成
- [ ] 用户认证系统（JWT）
- [ ] 更多技术指标（KDJ、威廉指标、OBV）
- [ ] API 文档（Swagger/OpenAPI）

### 长期目标 (3个月+)

- [ ] 回测框架
- [ ] 实时数据推送（WebSocket）
- [ ] 投资组合跟踪
- [ ] 邮件/短信提醒系统
- [ ] 移动端应用（React Native）
- [ ] 机器学习价格预测模型

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

**代码规范:**
- 遵循 PEP 8 (Python)
- 添加类型提示
- 编写文档字符串（中文）
- 添加单元测试

---

## 📄 许可证

© 2025 美股量化分析系统。

本仓库中 Liuzkai 的原创代码及其原创配套文档采用 [MIT 许可](LICENSE)，允许使用、复制、修改和商业分发；分发软件副本或实质性部分时，须保留版权声明及完整许可声明。无需在产品界面署名。第三方组件或内容仍遵循各自的原许可，相关版权及许可声明必须保留。

本 MIT 授权限于本项目原创实现，不授予 Yahoo Finance／Finviz 行情、新闻等第三方数据的商业使用或再分发权；数据和服务须另遵循提供方条款。`requirements.txt` 中的依赖及 CDN 加载的 ECharts 保留原许可。尤其应区分 [yfinance 的开源代码许可与数据使用条件](https://github.com/ranaroussi/yfinance#legal-stuff)。

---

## 🙏 致谢

**数据来源:**
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance API wrapper
- [finvizfinance](https://github.com/lit26/finvizfinance) - Finviz data and screener

**技术库:**
- [ta](https://github.com/bukosabino/ta) - Technical analysis library
- [TextBlob](https://github.com/sloria/TextBlob) - NLP sentiment analysis
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [ECharts](https://echarts.apache.org/) - Charting library
- [pandas](https://pandas.pydata.org/) - Data analysis library

**设计灵感:**
- Bloomberg Terminal
- TradingView

---

## 📞 联系方式

**项目维护者:** Liu Zhongkai

**GitHub:** https://github.com/Liuzkai/AmericanMarketing

**问题反馈:** https://github.com/Liuzkai/AmericanMarketing/issues

---

## 📊 项目统计

![GitHub stars](https://img.shields.io/github/stars/Liuzkai/AmericanMarketing?style=social)
![GitHub forks](https://img.shields.io/github/forks/Liuzkai/AmericanMarketing?style=social)
![GitHub issues](https://img.shields.io/github/issues/Liuzkai/AmericanMarketing)
![GitHub last commit](https://img.shields.io/github/last-commit/Liuzkai/AmericanMarketing)

**代码统计:**
- 总代码行数: ~4,800 行
- 后端 Python: ~3,144 行
- 前端 HTML/CSS/JS: ~1,700 行
- 文档: ~2,000 行

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star！**

Made with ❤️ by Liu Zhongkai

</div>
