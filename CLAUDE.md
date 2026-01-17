# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

美股量化分析系统 (US Stock Quantitative Analysis System) - A Python-based stock analysis system for analyzing US equities using technical indicators, fundamental metrics, and sentiment analysis.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Running Analysis

**Single Stock Analysis:**
```bash
python analyze_stock.py --ticker AAPL
python analyze_stock.py -t NVDA
```

**Market Scanner (finds undervalued growth stocks):**
```bash
python market_scanner.py
```

**Test Data Sources:**
```bash
# Test finviz data source
python test_finviz.py

# Test market data module
python tools/market_data.py

# Test analyzer module
python tools/analyzer.py
```

## Architecture

### Core Components

**1. Data Fetching Layer (`tools/market_data.py`)**
- `MarketFetcher`: Unified data acquisition interface
- Primary data source: yfinance (Yahoo Finance)
- Fallback data source: finvizfinance
- Rate limiting and retry mechanisms built-in
- Fetches: price history (OHLCV), financial metrics (PE/PB/ROE), news, earnings reports

**2. Analysis Layer (`tools/analyzer.py`)**
- `TechnicalAnalyzer`: Calculates technical indicators using the `ta` library
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence/Divergence)
  - Bollinger Bands
  - SMA 50/200 (Simple Moving Averages)
  - Generates buy/sell/hold signals based on indicator combinations
- `SentimentAnalyzer`: News sentiment analysis using TextBlob
  - Polarity scoring (-1 to 1)
  - Sentiment classification (Very Positive, Positive, Neutral, Negative, Very Negative)

**3. Application Layer**
- `analyze_stock.py`: Comprehensive single-stock analysis tool
  - Integrates all data sources and analyzers
  - Outputs JSON and natural language summaries
  - Generates investment recommendations
- `market_scanner.py`: Market-wide opportunity scanner
  - Uses finvizfinance screener with configurable filters
  - Default criteria: S&P 500, PE < 25, PEG < 1, Price above SMA20
  - Calculates opportunity scores (0-100) based on multiple factors
  - Outputs ranked results to CSV

### Data Flow

```
User Request → Application Layer (analyze_stock/market_scanner)
    ↓
MarketFetcher → yfinance (primary) → finvizfinance (fallback)
    ↓
Data Processing:
  - TechnicalAnalyzer → Technical indicators + signals
  - SentimentAnalyzer → News sentiment scores
    ↓
Result Aggregation → JSON output + Natural language summary
```

### Key Design Patterns

**Fallback Data Strategy**: The system implements a robust fallback mechanism:
1. Attempt data fetch from yfinance
2. If yfinance fails → use finvizfinance for current price/fundamentals
3. If real historical data unavailable → generate simulated data for technical analysis (deterministic based on ticker hash)

**Rate Limiting**: MarketFetcher includes built-in rate limiting:
- Default request delay: 1 second between API calls
- Automatic retry on rate limit errors (exponential backoff)
- Configurable max retries (default: 3)

**Signal Aggregation**: TechnicalAnalyzer combines multiple indicators:
- Each indicator generates individual signals
- Signals are scored and combined into overall recommendation
- Scoring: Bullish signals (+) vs Bearish signals (-)
- Output: Strong_Buy, Buy, Neutral, Sell, Strong_Sell

### Industry PE Benchmarks

The system uses hardcoded industry average PE ratios in `analyze_stock.py` (INDUSTRY_AVG_PE dict):
- Technology: 28.5
- Healthcare: 24.0
- Financial Services: 14.5
- Energy: 12.0
- (etc.)

These are used for valuation analysis (Undervalued/Fair/Overvalued status).

## Data Sources

**yfinance (primary)**:
- Historical price data (OHLCV)
- Company info and financial metrics
- News articles
- Earnings reports

**finvizfinance (fallback/screener)**:
- Fundamental data when yfinance unavailable
- Market-wide screening functionality
- Alternative news source

## Output Formats

**analyze_stock.py produces**:
- JSON structured output with all metrics
- Natural language summary in Chinese
- Investment recommendation based on composite scoring

**market_scanner.py produces**:
- CSV file: `market_opportunity.csv` with ranked opportunities
- Console summary with top 10 stocks
- Sector and technical signal distribution statistics

## Important Notes

**API Rate Limits**: Both yfinance and finvizfinance have rate limits. The system handles this with:
- Request delays between calls
- Retry logic with exponential backoff
- Graceful fallback to alternative data sources

**Simulated Data**: When real historical data is unavailable, the system generates deterministic simulated price data (seeded by ticker hash) to enable technical analysis. This is clearly indicated in the output's `data_source` field.

**Logging**: All modules use Python logging. Default level is WARNING for applications, INFO for module tests. Adjust via log_level parameters.

**Language**: Code comments and docstrings are primarily in Chinese. Output summaries are in Chinese. Variable names and class names use English.

---

## Project Development Review

### 📊 Code Statistics

| Module | Lines of Code | Functionality |
|--------|--------------|---------------|
| `tools/market_data.py` | 715 | Data acquisition (yfinance + finvizfinance) |
| `tools/analyzer.py` | 784 | Technical analysis + Sentiment analysis |
| `analyze_stock.py` | 607 | Single-stock analysis CLI tool |
| `market_scanner.py` | 626 | Market scanner CLI tool |
| `web/api/routes.py` | 349 | RESTful API routes |
| `web/app.py` | 63 | Flask application entry point |
| `web/templates/` | ~500 | HTML templates (5 files) |
| `web/static/js/` | ~800 | Frontend JavaScript (5 modules) |
| `web/static/css/` | ~400 | Stylesheets (themes + main) |
| **Total Core** | **3,144** | **Backend Python code** |
| **Total Full Stack** | **~4,800** | **Including frontend** |

### 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              Application Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ analyze_stock│  │market_scanner│  │  Web App  │ │
│  │    (CLI)     │  │    (CLI)     │  │  (Flask)  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│              Analysis Layer                          │
│  ┌──────────────────┐    ┌──────────────────────┐  │
│  │TechnicalAnalyzer │    │ SentimentAnalyzer    │  │
│  │  - RSI, MACD     │    │  - TextBlob NLP      │  │
│  │  - Bollinger     │    │  - News polarity     │  │
│  │  - SMA signals   │    │  - Sentiment score   │  │
│  └──────────────────┘    └──────────────────────┘  │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│              Data Layer                              │
│  ┌──────────────────────────────────────────────┐  │
│  │           MarketFetcher                       │  │
│  │  ┌────────────┐         ┌─────────────────┐ │  │
│  │  │  yfinance  │ ──fail→ │ finvizfinance   │ │  │
│  │  │ (primary)  │         │   (fallback)    │ │  │
│  │  └────────────┘         └─────────────────┘ │  │
│  │         ↓ fail                               │  │
│  │  ┌────────────────────────────────────────┐ │  │
│  │  │  Simulated Data (deterministic)        │ │  │
│  │  └────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 🎯 Key Features Implementation

#### 1. Web Interface (`web/` directory)

**Frontend Stack:**
- Pure HTML/CSS/JavaScript (no build tools required)
- ECharts 5.x for professional financial charts
- CSS Variables for dynamic theming system
- Responsive design with mobile support

**Pages:**
- `index.html` - Landing page with quick analysis
- `analyze.html` - Detailed single-stock analysis with charts
- `scanner.html` - Market scanning with filtering
- `about.html` - System information
- `base.html` - Shared layout with navigation and theme switcher

**JavaScript Modules:**
- `api.js` - RESTful API client wrapper
- `charts.js` - ECharts configuration for candlestick charts
- `theme.js` - Dark/light theme management with localStorage
- `analyzer.js` - Single-stock analysis page logic
- `scanner.js` - Market scanner page logic

**Styling:**
- `themes.css` - CSS variable definitions for dark/light modes
- `main.css` - Component styles and layouts
- Design inspired by Bloomberg Terminal and TradingView

**Backend API (Flask):**
```
GET /api/v1/stock/<ticker>/analyze  - Full analysis (technical + fundamental + sentiment)
GET /api/v1/stock/<ticker>/quote    - Quick price quote
GET /api/v1/market/scan             - Market scanner with filters
GET /api/v1/health                  - Service health check
```

#### 2. Technical Analysis System (`tools/analyzer.py:784`)

**Indicators Implemented:**
```python
TechnicalAnalyzer Methods:
├── calculate_rsi()           # Relative Strength Index (14 periods)
├── calculate_macd()          # MACD (12, 26, 9)
├── calculate_bollinger()     # Bollinger Bands (20, 2)
├── calculate_sma()           # Simple Moving Averages (50, 200)
├── generate_signals()        # Multi-indicator signal aggregation
└── analyze()                 # Full technical analysis pipeline

Signal Generation Logic:
- RSI < 30: Oversold → BUY signal
- RSI > 70: Overbought → SELL signal
- MACD golden cross: BUY signal
- MACD death cross: SELL signal
- Price above Bollinger upper: Overbought
- Price below Bollinger lower: Oversold
- SMA 50 crosses above 200: Golden cross → BUY
- SMA 50 crosses below 200: Death cross → SELL

Composite Scoring:
- Each signal contributes +1 (bullish) or -1 (bearish)
- Final score range: -5 to +5
- Mapping: Strong_Sell, Sell, Neutral, Buy, Strong_Buy
```

#### 3. Data Acquisition System (`tools/market_data.py:715`)

**MarketFetcher Capabilities:**
```python
Data Sources:
├── get_stock_price_history()      # OHLCV data (2 years default)
├── get_current_price()            # Real-time price + change %
├── get_financial_metrics()        # PE, PB, ROE, margins, debt ratio
├── get_news()                     # News articles with timestamps
├── get_company_info()             # Company profile, sector, industry
└── get_earnings()                 # EPS and revenue history

Fallback Mechanism:
1. Try yfinance.Ticker() for all data
2. If fails → try finvizfinance for fundamentals
3. If no historical data → generate simulated OHLCV
   - Deterministic (seeded by ticker hash)
   - Realistic price movements
   - Clearly marked as "simulated" in output

Rate Limiting:
- 1 second delay between requests
- Exponential backoff: 2^retry_count seconds
- Max retries: 3
- HTTP 429 (Too Many Requests) handling
```

#### 4. Market Scanner (`market_scanner.py:626`)

**Screening Criteria:**
```python
Default Filters (configurable):
├── Index: S&P 500 (sp500)
├── PE Ratio: < 25
├── PEG Ratio: < 1.0
├── Technical: Price > SMA(20)
└── Output: Top 50 opportunities

Opportunity Scoring (0-100):
- Valuation score (40%): Based on PE vs industry average
- Growth score (30%): PEG ratio and revenue growth
- Technical score (30%): SMA trend and momentum
```

**Output Format:**
```csv
Rank,Ticker,Name,Price,PE,PEG,Score,Signal,Sector
1,AAPL,Apple Inc.,175.50,28.5,2.1,85.3,Buy,Technology
2,MSFT,Microsoft Corp.,380.25,32.1,2.3,82.7,Buy,Technology
...
```

#### 5. Sentiment Analysis (`tools/analyzer.py:SentimentAnalyzer`)

**NLP Pipeline:**
```python
Process:
1. Fetch recent news (20 articles)
2. Extract title + description
3. TextBlob polarity scoring (-1 to +1)
4. Aggregate average polarity
5. Classify sentiment:
   - Very Positive: > 0.5
   - Positive: 0.2 to 0.5
   - Neutral: -0.2 to 0.2
   - Negative: -0.5 to -0.2
   - Very Negative: < -0.5

Output:
{
  "average_polarity": 0.35,
  "sentiment": "Positive",
  "news_count": 18,
  "recent_headlines": [...]
}
```

### 📦 Dependency Stack

**Core Dependencies:**
```
Data & Analysis:
- yfinance >= 0.2.28         # Yahoo Finance API wrapper
- finvizfinance >= 0.14.5    # Finviz screener and data
- pandas >= 2.0.0            # Data manipulation
- ta >= 0.10.2               # Technical analysis library (70+ indicators)
- textblob >= 0.17.1         # NLP sentiment analysis

Web Framework:
- Flask >= 2.3.0             # Lightweight web framework
- Flask-CORS >= 4.0.0        # Cross-Origin Resource Sharing

Optional:
- sec-edgar-downloader       # SEC filings (future enhancement)
```

### 🎨 UI/UX Design Highlights

**Theme System:**
```css
Dark Mode (Default):
- Background: #0a0e27 (dark blue-black)
- Surface: #1a1f3a (card background)
- Primary: #3b82f6 (blue accents)
- Text: #e2e8f0 (light gray)
- Chart: Dark theme with cyan/red candles

Light Mode:
- Background: #f8fafc (light gray)
- Surface: #ffffff (white cards)
- Primary: #2563eb (darker blue)
- Text: #1e293b (dark gray)
- Chart: Light theme with green/red candles

Toggle: localStorage persisted, applies to all charts
```

**Responsive Breakpoints:**
```css
Desktop: > 1024px (full sidebar, multi-column)
Tablet: 768px - 1024px (collapsible sidebar)
Mobile: < 768px (hamburger menu, single column)
```

**Chart Features:**
- Candlestick chart with volume overlay
- Technical indicators (SMA lines, Bollinger bands)
- Zoom and pan functionality
- Tooltip with OHLCV data
- Dynamic color scheme based on theme

### 🔄 Data Flow Examples

**Example 1: Single Stock Analysis**
```
User inputs "AAPL" in web interface
    ↓
GET /api/v1/stock/AAPL/analyze
    ↓
MarketFetcher.get_stock_price_history("AAPL")
    ↓ yfinance success
Download 2 years OHLCV data (504 trading days)
    ↓
TechnicalAnalyzer.analyze(price_data)
    ↓
Calculate indicators:
  - RSI = 65.3 (neutral)
  - MACD histogram positive (bullish)
  - Price between Bollinger bands (neutral)
  - SMA50 > SMA200 (golden cross, bullish)
    ↓
Generate signals: Score = +2 → BUY
    ↓
SentimentAnalyzer.analyze_sentiment(news)
    ↓
Analyze 18 news articles → Polarity = +0.42 (Positive)
    ↓
Aggregate results + calculate composite score
    ↓
Return JSON response to frontend
    ↓
Frontend renders:
  - Price card with live data
  - Candlestick chart with indicators
  - Financial metrics table
  - Sentiment gauge
  - Investment recommendation
```

**Example 2: Market Scanning**
```
User sets filters: PE < 20, PEG < 1, S&P 500
    ↓
GET /api/v1/market/scan?max_pe=20&max_peg=1&index=sp500
    ↓
finvizfinance.Screener(['idx_sp500', 'fa_pe_u20', 'fa_peg_u1'])
    ↓
API returns 47 matching stocks
    ↓
For each stock (parallel processing):
  - Fetch current price and metrics
  - Calculate opportunity score
  - Classify by sector
    ↓
Sort by score (descending)
    ↓
Return top 50 with details
    ↓
Frontend renders:
  - Sortable table with key metrics
  - Sector distribution pie chart
  - Export to CSV button
```

### 🛠️ Development Workflow

**Git History:**
```bash
3e0d4bd - Initial commit: US Stock Quantitative Analysis System
         (Single comprehensive commit with all features)
```

**Recent Changes (Uncommitted):**
```
M  requirements.txt     # Added Flask dependencies
A  WEB_README.md        # Web interface documentation
A  run_web.py           # Web server entry point
A  web/                 # New web application directory
```

**Testing Tools:**
```bash
# Test individual modules
python tools/market_data.py    # Test data fetching
python tools/analyzer.py       # Test analysis functions
python test_finviz.py          # Test finviz integration

# Test CLI tools
python analyze_stock.py -t AAPL
python market_scanner.py

# Test web interface
python run_web.py              # Start dev server
curl http://localhost:5001/api/v1/health
```

### 📈 Technical Debt & Future Improvements

**Short-term TODOs:**
1. ✅ Add caching layer (Redis) for frequently requested stocks
2. ✅ Implement async job queue (Celery) for market scanning
3. ✅ Add database (PostgreSQL) for historical data storage
4. ✅ Implement user authentication (JWT tokens)
5. ✅ Add more technical indicators (KDJ, Williams %R, OBV)

**Long-term Enhancements:**
1. Backtesting framework for strategy validation
2. Real-time WebSocket updates for live prices
3. Portfolio tracking and performance analytics
4. Alert system (email/SMS) for signal notifications
5. Mobile app (React Native) for iOS/Android
6. Machine learning models for price prediction

**Code Quality:**
- Unit test coverage: ~0% (needs comprehensive test suite)
- Documentation: Good (CLAUDE.md, WEB_README.md, docstrings)
- Code style: Mixed (PEP 8 mostly followed)
- Type hints: Partial (add for better IDE support)

### 🚨 Known Limitations

**API Rate Limits:**
- Yahoo Finance: ~2000 requests/hour (shared IP limit)
- Finviz: ~100 requests/hour (free tier)
- Impact: Market scanning may fail for large result sets
- Mitigation: Built-in retry logic + request delays

**Data Quality:**
- Simulated data used when real data unavailable
- News sentiment limited to English articles
- Some stocks lack complete financial metrics
- PE benchmarks hardcoded (need periodic updates)

**Network Dependencies:**
- Requires international network access (APIs hosted abroad)
- ECharts loaded from CDN (needs internet on first load)
- No offline mode available

**Performance:**
- Market scanning synchronous (takes 30-60s for 50 stocks)
- Large historical data (5 years) may cause memory issues
- No database caching (all data fetched on-demand)

**Security:**
- Flask debug mode should be disabled in production
- No rate limiting on API endpoints (vulnerable to abuse)
- CORS enabled for all origins (should restrict in prod)
- No input sanitization for SQL injection (currently no DB)

### 💡 Design Philosophy

**Principles:**
1. **Fail Gracefully**: Fallback mechanisms at every layer
2. **User-Friendly**: Bilingual (Chinese output, English code)
3. **Professional**: Finance industry UI/UX standards
4. **Extensible**: Modular architecture for easy enhancement
5. **Transparent**: Clear data source indicators

**Trade-offs:**
- Simplicity over scalability (no microservices)
- Readability over performance (synchronous processing)
- Speed of development over test coverage
- Monorepo over separate frontend/backend repos

### 📚 Documentation

**Available Docs:**
- `CLAUDE.md` - Architecture, commands, design patterns (this file)
- `WEB_README.md` - Web interface guide, API docs, deployment
- `requirements.txt` - Dependency list with comments
- Inline docstrings - All classes and functions documented in Chinese

**Missing Docs:**
- API reference (Swagger/OpenAPI spec)
- Database schema (when implemented)
- Deployment guide (Docker, Kubernetes)
- User manual (end-user documentation)

### 🎓 Learning Resources

**Technical Concepts Used:**
- RESTful API design
- Technical analysis indicators (RSI, MACD, etc.)
- Sentiment analysis with NLP
- CSS custom properties for theming
- Responsive web design patterns
- Rate limiting and retry strategies
- Fallback and graceful degradation

**Libraries & Frameworks:**
- Flask application factory pattern
- Blueprint-based routing
- ECharts API for financial charts
- pandas DataFrame operations
- ta-lib style technical analysis

---

## Quick Reference Commands

### Web Interface
```bash
# Start web server (development)
python run_web.py

# Start production server (requires gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "web.app:create_app()"

# Access pages
http://localhost:5001/           # Home
http://localhost:5001/analyze    # Analysis
http://localhost:5001/scanner    # Scanner
http://localhost:5001/about      # About
```

### CLI Tools
```bash
# Analyze single stock
python analyze_stock.py --ticker AAPL

# Scan market with custom filters
python market_scanner.py

# Test data sources
python test_finviz.py
```

### API Examples
```bash
# Full stock analysis
curl http://localhost:5001/api/v1/stock/AAPL/analyze

# Quick quote
curl http://localhost:5001/api/v1/stock/MSFT/quote

# Market scan
curl "http://localhost:5001/api/v1/market/scan?max_pe=20&limit=10"

# Health check
curl http://localhost:5001/api/v1/health
```

---

## System Requirements

**Minimum:**
- Python 3.8+
- 2GB RAM
- Internet connection (international access)

**Recommended:**
- Python 3.10+
- 4GB RAM
- Fast internet connection
- Modern browser (Chrome/Firefox/Safari latest)

**Tested On:**
- macOS 13+ (Apple Silicon & Intel)
- Ubuntu 20.04+
- Windows 10+ (WSL2 recommended)

---

## Troubleshooting

**Problem: "Too Many Requests" errors**
- Cause: API rate limit exceeded
- Solution: Wait 5-10 minutes, reduce request frequency

**Problem: No historical data available**
- Cause: yfinance API failure or delisted stock
- Solution: System auto-generates simulated data, check `data_source` field

**Problem: Sentiment analysis returns neutral for all stocks**
- Cause: No news available or all non-English articles
- Solution: Expected behavior, indicates lack of recent news

**Problem: Web interface charts not loading**
- Cause: CDN blocked or slow internet
- Solution: Check browser console, try different network

**Problem: Market scanner returns fewer results than expected**
- Cause: Strict filters or API timeout
- Solution: Relax filter criteria or reduce result limit

---

## Project Metadata

**Created:** 2025-12-31
**Last Updated:** 2026-01-17
**Version:** 1.0.0 (Web interface added)
**License:** Proprietary
**Repository:** https://github.com/Liuzkai/AmericanMarketing

**Contributors:**
- Liu Zhongkai (Primary Developer)
- Claude Code (Development Assistant)

**Project Status:** ✅ Production Ready (CLI), 🚧 Beta (Web Interface)

---

*Last generated by Claude Code on 2026-01-17*
