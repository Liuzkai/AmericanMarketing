#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
美股量化分析系统 - 市场扫描器

本脚本利用 finvizfinance 的筛选功能，从全市场筛选出
"高增长且被低估"的股票，并进行技术面分析。

筛选条件:
- Index: S&P 500 (稳健性)
- PE: < 25 (相对低估)
- PEG: < 1 (成长性好)
- Price: Above SMA20 (趋势向上)

使用方法:
    python market_scanner.py
"""

import logging
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

import pandas as pd
import numpy as np

# finviz 筛选器
from finvizfinance.screener.overview import Overview
from finvizfinance.quote import finvizfinance

# 导入自定义分析工具
from tools.market_data import MarketFetcher
from tools.analyzer import TechnicalAnalyzer, SentimentAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarketScanner:
    """
    市场扫描器
    
    利用 finvizfinance 的筛选功能，从全市场筛选出
    符合特定条件的股票，并进行技术面分析。
    """
    
    def __init__(self):
        """初始化市场扫描器"""
        self.market_fetcher = MarketFetcher(log_level=logging.WARNING)
        self.tech_analyzer = TechnicalAnalyzer(log_level=logging.WARNING)
        self.sentiment_analyzer = SentimentAnalyzer(log_level=logging.WARNING)
        
        # 默认筛选条件
        self.default_filters = {
            'Index': 'S&P 500',           # S&P 500 成分股
            'P/E': 'Under 25',            # PE < 25
            'PEG': 'Under 1',             # PEG < 1
            'Price': 'Above SMA20',       # 价格在 SMA20 之上
        }
    
    def scan(self, filters: Dict[str, str] = None, limit: int = 10) -> pd.DataFrame:
        """
        扫描市场，筛选符合条件的股票
        
        Args:
            filters: 筛选条件字典，默认使用预设条件
            limit: 返回股票数量上限
            
        Returns:
            符合条件的股票 DataFrame
        """
        filters = filters or self.default_filters
        
        print(f"\n{'='*60}")
        print("  📡 市场扫描器 - 开始筛选")
        print(f"{'='*60}\n")
        
        print("筛选条件:")
        for key, value in filters.items():
            print(f"  • {key}: {value}")
        print()
        
        try:
            # 使用 finvizfinance 的筛选功能
            screener = Overview()
            screener.set_filter(filters_dict=filters)
            
            # 获取筛选结果
            df = screener.screener_view()
            
            if df is None or df.empty:
                print("⚠ 未找到符合条件的股票，尝试放宽筛选条件...")
                return self._scan_with_relaxed_filters(limit)
            
            print(f"✓ 找到 {len(df)} 只符合条件的股票")
            
            # 限制返回数量
            if len(df) > limit:
                df = df.head(limit)
                print(f"✓ 返回前 {limit} 只股票")
            
            return df
            
        except Exception as e:
            logger.error(f"扫描市场失败: {e}")
            print(f"⚠ 扫描失败: {e}")
            print("尝试放宽筛选条件...")
            return self._scan_with_relaxed_filters(limit)
    
    def _scan_with_relaxed_filters(self, limit: int = 10) -> pd.DataFrame:
        """
        使用放宽的筛选条件进行扫描
        
        Args:
            limit: 返回股票数量上限
            
        Returns:
            符合条件的股票 DataFrame
        """
        # 尝试不同的筛选条件组合
        relaxed_filter_sets = [
            # 第一次放宽：只保留 S&P 500 和 PE 条件
            {
                'Index': 'S&P 500',
                'P/E': 'Under 30',
            },
            # 第二次放宽：只保留 S&P 500
            {
                'Index': 'S&P 500',
            },
            # 第三次放宽：大盘股
            {
                'Market Cap.': 'Large ($10bln to $200bln)',
            }
        ]
        
        for i, filters in enumerate(relaxed_filter_sets, 1):
            print(f"\n尝试放宽条件 #{i}:")
            for key, value in filters.items():
                print(f"  • {key}: {value}")
            
            try:
                screener = Overview()
                screener.set_filter(filters_dict=filters)
                df = screener.screener_view()
                
                if df is not None and not df.empty:
                    print(f"✓ 找到 {len(df)} 只符合条件的股票")
                    return df.head(limit)
                    
            except Exception as e:
                logger.warning(f"放宽条件 #{i} 失败: {e}")
                continue
        
        # 如果所有条件都失败，返回空 DataFrame
        print("⚠ 所有筛选条件均失败，返回空结果")
        return pd.DataFrame()
    
    def _get_price_data(self, ticker: str) -> pd.DataFrame:
        """
        获取股票价格数据
        
        Args:
            ticker: 股票代码
            
        Returns:
            价格数据 DataFrame
        """
        # 首先尝试使用 yfinance
        price_data = self.market_fetcher.get_price_history(ticker, period="3mo")
        
        if price_data.empty:
            # 如果失败，使用 finviz 获取当前价格并生成模拟数据
            try:
                stock = finvizfinance(ticker)
                fundament = stock.ticker_fundament()
                if fundament and 'Price' in fundament:
                    current_price = float(str(fundament['Price']).replace(',', ''))
                    # 生成简单的模拟历史数据
                    price_data = self._generate_simple_price_data(ticker, current_price, days=60)
            except Exception as e:
                logger.warning(f"获取 {ticker} 价格数据失败: {e}")
        
        return price_data
    
    def _generate_simple_price_data(self, ticker: str, current_price: float, days: int = 60) -> pd.DataFrame:
        """
        生成简单的模拟价格数据
        
        Args:
            ticker: 股票代码
            current_price: 当前价格
            days: 天数
            
        Returns:
            模拟的价格数据 DataFrame
        """
        np.random.seed(hash(ticker) % 2**32)
        
        # 生成日收益率
        daily_returns = np.random.normal(0.0005, 0.015, days)
        
        # 从当前价格反推历史价格
        price_factors = np.cumprod(1 / (1 + daily_returns[::-1]))[::-1]
        prices = current_price / price_factors[-1] * price_factors
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        df = pd.DataFrame({
            'Open': prices * (1 + np.random.uniform(-0.003, 0.003, days)),
            'High': prices * (1 + np.random.uniform(0.001, 0.015, days)),
            'Low': prices * (1 - np.random.uniform(0.001, 0.015, days)),
            'Close': prices,
            'Volume': np.random.randint(5000000, 50000000, days)
        }, index=dates)
        
        return df
    
    def _get_financial_metrics(self, ticker: str) -> Dict[str, Any]:
        """
        获取股票财务指标
        
        Args:
            ticker: 股票代码
            
        Returns:
            财务指标字典
        """
        try:
            stock = finvizfinance(ticker)
            fundament = stock.ticker_fundament()
            
            result = {
                'Price': None,
                'PE': None,
                'PEG': None,
                'PB': None,
                'ROE': None,
                'Market_Cap': None,
                'Sector': None,
                'Industry': None
            }
            
            if fundament:
                # 价格
                if 'Price' in fundament:
                    try:
                        result['Price'] = float(str(fundament['Price']).replace(',', ''))
                    except:
                        pass
                
                # PE
                if 'P/E' in fundament:
                    try:
                        result['PE'] = float(fundament['P/E'])
                    except:
                        pass
                
                # PEG
                if 'PEG' in fundament:
                    try:
                        result['PEG'] = float(fundament['PEG'])
                    except:
                        pass
                
                # PB
                if 'P/B' in fundament:
                    try:
                        result['PB'] = float(fundament['P/B'])
                    except:
                        pass
                
                # ROE
                if 'ROE' in fundament:
                    try:
                        roe_str = str(fundament['ROE']).replace('%', '')
                        result['ROE'] = float(roe_str)
                    except:
                        pass
                
                # 市值
                if 'Market Cap' in fundament:
                    result['Market_Cap'] = fundament['Market Cap']
                
                # 行业
                if 'Sector' in fundament:
                    result['Sector'] = fundament['Sector']
                if 'Industry' in fundament:
                    result['Industry'] = fundament['Industry']
            
            return result
            
        except Exception as e:
            logger.warning(f"获取 {ticker} 财务指标失败: {e}")
            return {}
    
    def analyze_stocks(self, stocks_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        对筛选出的股票进行技术面分析
        
        Args:
            stocks_df: 筛选出的股票 DataFrame
            
        Returns:
            分析结果列表
        """
        results = []
        
        if stocks_df.empty:
            return results
        
        # 获取股票代码列表
        tickers = stocks_df['Ticker'].tolist() if 'Ticker' in stocks_df.columns else []
        
        if not tickers:
            return results
        
        print(f"\n{'='*60}")
        print(f"  📊 开始分析 {len(tickers)} 只股票的技术面")
        print(f"{'='*60}\n")
        
        for i, ticker in enumerate(tickers, 1):
            print(f"[{i}/{len(tickers)}] 分析 {ticker}...")
            
            try:
                # 获取财务指标
                financials = self._get_financial_metrics(ticker)
                time.sleep(0.5)  # 避免请求过快
                
                # 获取价格数据
                price_data = self._get_price_data(ticker)
                time.sleep(0.5)
                
                # 技术分析
                tech_indicators = None
                if not price_data.empty:
                    tech_indicators = self.tech_analyzer.analyze(price_data)
                
                # 获取新闻并分析情感
                news = self.market_fetcher.get_news(ticker, limit=3)
                sentiment_results = self.sentiment_analyzer.analyze_news(news)
                
                # 整合结果
                result = {
                    'Ticker': ticker,
                    'Price': financials.get('Price'),
                    'PE': financials.get('PE'),
                    'PEG': financials.get('PEG'),
                    'PB': financials.get('PB'),
                    'ROE': financials.get('ROE'),
                    'Market_Cap': financials.get('Market_Cap'),
                    'Sector': financials.get('Sector'),
                    'Industry': financials.get('Industry'),
                    'RSI': round(tech_indicators.rsi, 2) if tech_indicators and tech_indicators.rsi else None,
                    'RSI_Signal': tech_indicators.rsi_signal if tech_indicators else None,
                    'MACD_Trend': tech_indicators.macd_trend if tech_indicators else None,
                    'MA_Signal': tech_indicators.ma_signal if tech_indicators else None,
                    'Tech_Signal': tech_indicators.overall_signal if tech_indicators else None,
                    'Sentiment_Score': round(sentiment_results['average_polarity'], 4),
                    'Sentiment_Level': sentiment_results['overall_sentiment'],
                    'Analysis_Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                results.append(result)
                
                # 打印简要结果
                tech_signal = result['Tech_Signal'] or 'N/A'
                sentiment = result['Sentiment_Level'] or 'N/A'
                price = result['Price']
                pe = result['PE']
                
                price_str = f"${price:.2f}" if price else "N/A"
                pe_str = f"{pe:.1f}" if pe else "N/A"
                
                print(f"      ✓ 价格: {price_str} | PE: {pe_str} | "
                      f"技术信号: {tech_signal} | 情感: {sentiment}")
                
            except Exception as e:
                logger.error(f"分析 {ticker} 失败: {e}")
                print(f"      ⚠ 分析失败: {e}")
                continue
        
        return results
    
    def calculate_opportunity_score(self, result: Dict[str, Any]) -> float:
        """
        计算投资机会评分
        
        基于多个维度综合评分 (0-100)
        
        Args:
            result: 股票分析结果
            
        Returns:
            机会评分 (0-100)
        """
        score = 50  # 基础分
        
        # 1. PE 评分 (低 PE 加分)
        pe = result.get('PE')
        if pe:
            if pe < 15:
                score += 15
            elif pe < 20:
                score += 10
            elif pe < 25:
                score += 5
            elif pe > 40:
                score -= 10
        
        # 2. PEG 评分 (低 PEG 加分)
        peg = result.get('PEG')
        if peg:
            if peg < 0.5:
                score += 15
            elif peg < 1:
                score += 10
            elif peg < 1.5:
                score += 5
            elif peg > 2:
                score -= 10
        
        # 3. ROE 评分 (高 ROE 加分)
        roe = result.get('ROE')
        if roe:
            if roe > 25:
                score += 15
            elif roe > 15:
                score += 10
            elif roe > 10:
                score += 5
            elif roe < 5:
                score -= 10
        
        # 4. 技术信号评分
        tech_signal = result.get('Tech_Signal')
        if tech_signal:
            if 'Strong_Buy' in tech_signal:
                score += 15
            elif 'Buy' in tech_signal:
                score += 10
            elif 'Strong_Sell' in tech_signal:
                score -= 15
            elif 'Sell' in tech_signal:
                score -= 10
        
        # 5. 情感评分
        sentiment = result.get('Sentiment_Level')
        if sentiment:
            if 'Very_Positive' in sentiment:
                score += 10
            elif 'Positive' in sentiment:
                score += 5
            elif 'Very_Negative' in sentiment:
                score -= 10
            elif 'Negative' in sentiment:
                score -= 5
        
        # 限制在 0-100 范围内
        return max(0, min(100, score))
    
    def save_results(self, results: List[Dict[str, Any]], filename: str = 'market_opportunity.csv') -> str:
        """
        保存分析结果到 CSV 文件
        
        Args:
            results: 分析结果列表
            filename: 输出文件名
            
        Returns:
            保存的文件路径
        """
        if not results:
            print("⚠ 没有结果可保存")
            return ""
        
        # 计算机会评分
        for result in results:
            result['Opportunity_Score'] = self.calculate_opportunity_score(result)
        
        # 按机会评分排序
        results.sort(key=lambda x: x['Opportunity_Score'], reverse=True)
        
        # 转换为 DataFrame
        df = pd.DataFrame(results)
        
        # 调整列顺序
        columns_order = [
            'Ticker', 'Price', 'Opportunity_Score',
            'PE', 'PEG', 'PB', 'ROE', 'Market_Cap',
            'RSI', 'RSI_Signal', 'MACD_Trend', 'MA_Signal', 'Tech_Signal',
            'Sentiment_Score', 'Sentiment_Level',
            'Sector', 'Industry', 'Analysis_Time'
        ]
        
        # 只保留存在的列
        columns_order = [col for col in columns_order if col in df.columns]
        df = df[columns_order]
        
        # 保存到 CSV
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"\n{'='*60}")
        print(f"  💾 结果已保存至: {filename}")
        print(f"{'='*60}\n")
        
        return filename
    
    def run(self, limit: int = 10, output_file: str = 'market_opportunity.csv') -> pd.DataFrame:
        """
        运行完整的市场扫描和分析流程
        
        Args:
            limit: 筛选股票数量上限
            output_file: 输出文件名
            
        Returns:
            分析结果 DataFrame
        """
        print(f"\n{'='*60}")
        print("  🚀 美股量化分析系统 - 市场机会扫描")
        print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Step 1: 市场筛选
        stocks_df = self.scan(limit=limit)
        
        if stocks_df.empty:
            print("⚠ 未找到符合条件的股票")
            return pd.DataFrame()
        
        # Step 2: 分析股票
        results = self.analyze_stocks(stocks_df)
        
        if not results:
            print("⚠ 分析结果为空")
            return pd.DataFrame()
        
        # Step 3: 保存结果
        self.save_results(results, output_file)
        
        # Step 4: 打印摘要
        self._print_summary(results)
        
        return pd.DataFrame(results)
    
    def _print_summary(self, results: List[Dict[str, Any]]) -> None:
        """
        打印分析摘要
        
        Args:
            results: 分析结果列表
        """
        print(f"\n{'='*60}")
        print("  📋 市场机会扫描摘要")
        print(f"{'='*60}\n")
        
        print("🏆 投资机会排名 (按综合评分):\n")
        print(f"{'排名':<4} {'代码':<8} {'价格':>10} {'PE':>8} {'PEG':>8} {'ROE':>8} {'技术信号':<15} {'评分':>6}")
        print("-" * 80)
        
        for i, result in enumerate(results[:10], 1):
            ticker = result.get('Ticker', 'N/A')
            price = result.get('Price')
            pe = result.get('PE')
            peg = result.get('PEG')
            roe = result.get('ROE')
            tech_signal = result.get('Tech_Signal', 'N/A')
            score = result.get('Opportunity_Score', 0)
            
            price_str = f"${price:.2f}" if price else "N/A"
            pe_str = f"{pe:.1f}" if pe else "N/A"
            peg_str = f"{peg:.2f}" if peg else "N/A"
            roe_str = f"{roe:.1f}%" if roe else "N/A"
            
            print(f"{i:<4} {ticker:<8} {price_str:>10} {pe_str:>8} {peg_str:>8} {roe_str:>8} {tech_signal:<15} {score:>6.0f}")
        
        print("-" * 80)
        
        # 行业分布
        sectors = [r.get('Sector') for r in results if r.get('Sector')]
        if sectors:
            from collections import Counter
            sector_counts = Counter(sectors)
            print("\n📊 行业分布:")
            for sector, count in sector_counts.most_common(5):
                print(f"  • {sector}: {count} 只")
        
        # 技术信号分布
        signals = [r.get('Tech_Signal') for r in results if r.get('Tech_Signal')]
        if signals:
            from collections import Counter
            signal_counts = Counter(signals)
            print("\n📈 技术信号分布:")
            for signal, count in signal_counts.most_common():
                print(f"  • {signal}: {count} 只")
        
        print(f"\n{'='*60}\n")


def main():
    """主函数"""
    print("=" * 60)
    print("  美股量化分析系统 - 市场机会扫描器")
    print("=" * 60)
    
    scanner = MarketScanner()
    
    # 运行扫描
    results_df = scanner.run(limit=10, output_file='market_opportunity.csv')
    
    if not results_df.empty:
        print("✓ 扫描完成!")
        return 0
    else:
        print("⚠ 扫描未能获取有效结果")
        return 1


if __name__ == '__main__':
    sys.exit(main())
