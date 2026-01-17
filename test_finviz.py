#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：使用 finvizfinance 作为主要数据源测试 MarketFetcher
当 yfinance API 被限流时使用此脚本

此脚本主要测试 finvizfinance 数据源的功能，包括:
- 新闻数据获取
- 基本财务数据获取
"""

import logging
import time
from finvizfinance.quote import finvizfinance
from finvizfinance.screener.overview import Overview

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_stock_fundamentals(ticker: str) -> dict:
    """获取股票基本面数据"""
    try:
        stock = finvizfinance(ticker.upper())
        fundament = stock.ticker_fundament()
        return fundament
    except Exception as e:
        logger.error(f"获取 {ticker} 基本面数据失败: {e}")
        return {}


def get_stock_news(ticker: str, limit: int = 5) -> list:
    """获取股票新闻"""
    try:
        stock = finvizfinance(ticker.upper())
        news_df = stock.ticker_news()
        if news_df is None or news_df.empty:
            return []
        
        news_list = []
        for _, row in news_df.head(limit).iterrows():
            news_list.append({
                'title': str(row.get('Title', '')),
                'publisher': str(row.get('Source', '')),
                'link': str(row.get('Link', '')),
                'published': str(row.get('Date', ''))
            })
        return news_list
    except Exception as e:
        logger.error(f"获取 {ticker} 新闻失败: {e}")
        return []


def main():
    """主测试函数"""
    test_tickers = ["AAPL", "GOOGL", "MSFT", "NVDA", "TSLA"]
    
    print("\n" + "=" * 70)
    print("美股量化分析系统 - finvizfinance 数据源测试")
    print("=" * 70)
    
    for ticker in test_tickers:
        print(f"\n{'=' * 70}")
        print(f"股票代码: {ticker}")
        print("=" * 70)
        
        # 1. 基本面数据
        print("\n--- 基本面数据 ---")
        fundamentals = get_stock_fundamentals(ticker)
        
        if fundamentals:
            # 提取关键指标
            key_metrics = [
                ('公司名称', 'Company'),
                ('行业', 'Industry'),
                ('板块', 'Sector'),
                ('市值', 'Market Cap'),
                ('市盈率(P/E)', 'P/E'),
                ('远期市盈率', 'Forward P/E'),
                ('市净率(P/B)', 'P/B'),
                ('市销率(P/S)', 'P/S'),
                ('EPS (TTM)', 'EPS (ttm)'),
                ('EPS下季预估', 'EPS next Q'),
                ('营收', 'Sales'),
                ('净利润率', 'Profit Margin'),
                ('运营利润率', 'Oper. Margin'),
                ('ROE', 'ROE'),
                ('ROA', 'ROA'),
                ('ROI', 'ROI'),
                ('负债/权益', 'Debt/Eq'),
                ('流通股', 'Shs Outstand'),
                ('机构持股', 'Inst Own'),
                ('内部持股', 'Insider Own'),
                ('52周高点', '52W High'),
                ('52周低点', '52W Low'),
                ('当前价格', 'Price'),
                ('目标价格', 'Target Price'),
                ('分析师建议', 'Recom'),
            ]
            
            for label, key in key_metrics:
                value = fundamentals.get(key, 'N/A')
                if value and value != '-':
                    print(f"  {label}: {value}")
        else:
            print("  未获取到数据")
        
        # 2. 新闻数据
        print("\n--- 最新新闻 (5条) ---")
        news = get_stock_news(ticker, limit=5)
        if news:
            for i, item in enumerate(news, 1):
                title = item['title'][:65] + '...' if len(item['title']) > 65 else item['title']
                print(f"  [{i}] {title}")
                print(f"      来源: {item['publisher']} | 时间: {item['published']}")
        else:
            print("  未获取到新闻")
        
        # 请求间隔
        time.sleep(1.5)
    
    print("\n" + "=" * 70)
    print("测试完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
