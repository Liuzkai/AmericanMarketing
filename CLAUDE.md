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
