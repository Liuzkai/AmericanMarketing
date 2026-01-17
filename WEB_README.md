# 美股量化分析系统 - Web 界面

专业的股票分析 Web 应用，提供技术分析、基本面分析、新闻情绪分析和市场扫描功能。

## 功能特性

### 🎨 专业金融风格界面
- **深色模式**（默认）：参考 Bloomberg Terminal、TradingView 设计
- **浅色模式**：清爽明亮的日间模式
- **主题切换**：点击右上角月亮/太阳图标即可切换，设置自动保存

### 📊 单股分析
- **技术指标**：RSI、MACD、布林带、SMA 50/200
- **K线图表**：专业蜡烛图，带成交量显示
- **财务指标**：PE、PB、ROE、营收增长
- **情绪分析**：基于新闻的 NLP 情绪评分
- **投资建议**：综合评分和操作建议
- **数据导出**：支持 CSV 和 JSON 格式

### 🔍 市场扫描
- **自定义筛选**：按 PE、PEG、指数等条件筛选
- **机会排行**：自动计算并排序机会评分
- **行业分布**：可视化行业统计
- **批量分析**：一次扫描 50+ 支股票

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv (推荐)
uv pip install -r requirements.txt

# 或使用 pip
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python run_web.py
```

服务将在 http://localhost:5001 启动

### 3. 访问页面

- **首页**: http://localhost:5001/
- **单股分析**: http://localhost:5001/analyze
- **市场扫描**: http://localhost:5001/scanner
- **关于页面**: http://localhost:5001/about

## API 接口

所有 API 端点都以 `/api/v1` 为前缀。

### 股票分析

```bash
GET /api/v1/stock/<TICKER>/analyze

# 示例
curl http://localhost:5001/api/v1/stock/AAPL/analyze
```

**响应格式**:
```json
{
  "success": true,
  "data": {
    "ticker": "AAPL",
    "current_price": 175.50,
    "price_change": 2.35,
    "price_change_percent": 1.36,
    "technical_indicators": { ... },
    "financial_metrics": { ... },
    "sentiment": { ... },
    "recommendation": { ... },
    "price_history": [ ... ],
    "news": [ ... ]
  },
  "timestamp": "2026-01-17 10:30:00"
}
```

### 快速报价

```bash
GET /api/v1/stock/<TICKER>/quote

# 示例
curl http://localhost:5001/api/v1/stock/AAPL/quote
```

### 市场扫描

```bash
GET /api/v1/market/scan?index=sp500&max_pe=25&max_peg=1&limit=50

# 示例
curl "http://localhost:5001/api/v1/market/scan?max_pe=25&limit=10"
```

**查询参数**:
- `index`: 指数筛选（sp500, nasdaq, dow）
- `max_pe`: 最大市盈率
- `max_peg`: 最大 PEG
- `limit`: 返回结果数量

### 健康检查

```bash
GET /api/v1/health

# 示例
curl http://localhost:5001/api/v1/health
```

## 项目结构

```
AmericanMarketing/
├── web/                        # Web 应用目录
│   ├── app.py                 # Flask 应用主入口
│   ├── api/
│   │   └── routes.py          # RESTful API 路由
│   ├── templates/             # Jinja2 模板
│   │   ├── base.html         # 基础模板（导航栏、主题系统）
│   │   ├── index.html        # 首页
│   │   ├── analyze.html      # 单股分析页面
│   │   ├── scanner.html      # 市场扫描页面
│   │   └── about.html        # 关于页面
│   └── static/               # 静态资源
│       ├── css/
│       │   ├── themes.css    # 主题样式（CSS 变量）
│       │   └── main.css      # 主要样式
│       └── js/
│           ├── api.js        # API 客户端封装
│           ├── charts.js     # ECharts 图表配置
│           ├── theme.js      # 主题切换逻辑
│           ├── analyzer.js   # 分析页面逻辑
│           └── scanner.js    # 扫描页面逻辑
├── tools/                     # 分析工具模块
│   ├── market_data.py        # 数据获取
│   └── analyzer.py           # 技术/情绪分析
├── run_web.py                # Web 服务启动脚本
└── requirements.txt          # 项目依赖
```

## 技术栈

### 后端
- **Flask** - 轻量级 Web 框架
- **Flask-CORS** - 跨域支持
- **yfinance** - Yahoo Finance 数据
- **finvizfinance** - Finviz 数据和筛选
- **ta** - 技术分析库
- **TextBlob** - 情绪分析

### 前端
- **原生 HTML/CSS/JavaScript** - 无构建工具，开箱即用
- **ECharts** - 专业图表库（CDN 引入）
- **CSS Variables** - 动态主题系统
- **Responsive Design** - 响应式布局

## 使用说明

### 单股分析

1. 访问首页或分析页面
2. 输入股票代码（如 AAPL、MSFT、GOOGL）
3. 点击"分析"按钮
4. 查看完整分析结果：
   - 实时价格和涨跌幅
   - K线图和技术指标
   - 财务指标表格
   - 新闻情绪仪表盘
   - 投资建议
5. 可导出 CSV 或 JSON 格式数据

### 市场扫描

1. 访问市场扫描页面
2. 设置筛选条件：
   - 选择指数（S&P 500、NASDAQ、Dow Jones）
   - 设置最大 PE 比率
   - 设置最大 PEG 比率
   - 设置返回结果数量
3. 点击"开始扫描"
4. 查看扫描结果：
   - 机会股票列表
   - 行业分布图
   - 点击股票代码查看详细分析
5. 可导出结果为 CSV 文件

### 主题切换

- 点击右上角的月亮/太阳图标
- 主题设置会自动保存到浏览器
- 所有图表会自动更新配色

## 注意事项

### 数据源限制

- **Yahoo Finance API** 有速率限制
- 建议在请求之间留出合理间隔
- 如遇到 "Too Many Requests" 错误，请等待几分钟后重试

### 网络要求

- 需要访问国际网络获取股票数据
- ECharts 通过 CDN 加载（首次访问需要网络）
- 建议使用稳定的网络连接

### 浏览器兼容性

推荐使用现代浏览器：
- Chrome / Edge (最新版)
- Firefox (最新版)
- Safari (最新版)

## 常见问题

### Q: 为什么获取数据失败？

A: 可能原因：
1. Yahoo Finance API 速率限制 - 等待几分钟后重试
2. 网络连接问题 - 检查网络设置
3. 股票代码错误 - 确认输入正确的美股代码

### Q: 如何修改端口？

A: 编辑 `run_web.py`，修改：
```python
app.run(host='0.0.0.0', port=5001)  # 修改 port 参数
```

### Q: 如何部署到生产环境？

A: 不要直接使用 Flask 开发服务器，请使用 Gunicorn 或 uWSGI：
```bash
# 安装 Gunicorn
pip install gunicorn

# 启动生产服务器
gunicorn -w 4 -b 0.0.0.0:8000 "web.app:create_app()"
```

## 命令行工具

Web 界面不影响原有 CLI 工具的使用：

```bash
# 单股分析
python analyze_stock.py --ticker AAPL

# 市场扫描
python market_scanner.py
```

## 贡献

欢迎提交 Issue 和 Pull Request！

项目地址: https://github.com/Liuzkai/AmericanMarketing

## 许可证

© 2025 美股量化分析系统. All rights reserved.

## 免责声明

本系统提供的信息仅供参考，不构成投资建议。所有数据和分析结果基于历史信息，过往表现不代表未来结果。投资有风险，入市需谨慎。
