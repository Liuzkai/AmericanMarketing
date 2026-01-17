#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
美股量化分析系统 - 股票综合分析脚本

本脚本整合 MarketFetcher、TechnicalAnalyzer、SentimentAnalyzer，
对单只股票进行全面分析，输出结构化 JSON 摘要。

使用方法:
    python analyze_stock.py --ticker AAPL
    python analyze_stock.py --ticker NVDA
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import pandas as pd
import numpy as np
from finvizfinance.quote import finvizfinance

# 导入工具模块
from tools.market_data import MarketFetcher
from tools.analyzer import TechnicalAnalyzer, SentimentAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.WARNING,  # 减少日志输出，只显示警告和错误
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 行业平均 PE 参考值 (基于 2024 年数据)
INDUSTRY_AVG_PE = {
    'Technology': 28.5,
    'Consumer Cyclical': 22.0,
    'Communication Services': 18.5,
    'Healthcare': 24.0,
    'Financial Services': 14.5,
    'Consumer Defensive': 20.0,
    'Industrials': 22.5,
    'Energy': 12.0,
    'Utilities': 18.0,
    'Real Estate': 35.0,
    'Basic Materials': 15.0,
    'default': 20.0  # 默认值
}


class StockAnalyzer:
    """
    股票综合分析器
    
    整合市场数据获取、技术分析和情感分析功能
    """
    
    def __init__(self):
        """初始化各个分析器"""
        self.market_fetcher = MarketFetcher(log_level=logging.WARNING)
        self.tech_analyzer = TechnicalAnalyzer(log_level=logging.WARNING)
        self.sentiment_analyzer = SentimentAnalyzer(log_level=logging.WARNING)
    
    def _get_price_from_finviz(self, ticker: str) -> Optional[float]:
        """
        从 finviz 获取当前价格
        
        Args:
            ticker: 股票代码
            
        Returns:
            当前价格或 None
        """
        try:
            stock = finvizfinance(ticker.upper())
            fundament = stock.ticker_fundament()
            if fundament and 'Price' in fundament:
                price_str = str(fundament['Price']).replace(',', '')
                return float(price_str)
        except Exception as e:
            logger.warning(f"从 finviz 获取 {ticker} 价格失败: {e}")
        return None
    
    def _get_financials_from_finviz(self, ticker: str) -> Dict[str, Any]:
        """
        从 finviz 获取财务数据
        
        Args:
            ticker: 股票代码
            
        Returns:
            财务数据字典
        """
        result = {
            'PE': None,
            'PB': None,
            'ROE': None,
            'RevenueGrowth': None
        }
        
        try:
            stock = finvizfinance(ticker.upper())
            fundament = stock.ticker_fundament()
            
            if fundament:
                # PE
                if 'P/E' in fundament:
                    try:
                        result['PE'] = float(fundament['P/E'])
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
                
                # 营收增长
                if 'Sales Q/Q' in fundament:
                    try:
                        growth_str = str(fundament['Sales Q/Q']).replace('%', '')
                        result['RevenueGrowth'] = float(growth_str)
                    except:
                        pass
                
        except Exception as e:
            logger.warning(f"从 finviz 获取 {ticker} 财务数据失败: {e}")
        
        return result
    
    def _get_earnings_from_finviz(self, ticker: str) -> Dict[str, Any]:
        """
        从 finviz 获取公司信息
        
        Args:
            ticker: 股票代码
            
        Returns:
            公司信息字典
        """
        result = {
            'annual': [],
            'quarterly': [],
            'summary': {}
        }
        
        try:
            stock = finvizfinance(ticker.upper())
            fundament = stock.ticker_fundament()
            
            if fundament:
                # 解析市值
                market_cap = fundament.get('Market Cap', 'N/A')
                if market_cap != 'N/A' and market_cap:
                    try:
                        market_cap_str = str(market_cap).replace(',', '')
                        if 'B' in market_cap_str:
                            market_cap = float(market_cap_str.replace('B', '')) * 1e9
                        elif 'M' in market_cap_str:
                            market_cap = float(market_cap_str.replace('M', '')) * 1e6
                        elif 'T' in market_cap_str:
                            market_cap = float(market_cap_str.replace('T', '')) * 1e12
                    except:
                        pass
                
                result['summary'] = {
                    'company_name': fundament.get('Company', ticker),
                    'sector': fundament.get('Sector', 'Technology'),
                    'industry': fundament.get('Industry', 'N/A'),
                    'market_cap': market_cap,
                    'currency': 'USD'
                }
                
        except Exception as e:
            logger.warning(f"从 finviz 获取 {ticker} 公司信息失败: {e}")
        
        return result
    
    def _generate_simulated_price_data(self, ticker: str, current_price: float, days: int = 250) -> pd.DataFrame:
        """
        生成模拟历史价格数据用于技术分析
        
        基于当前价格生成合理的历史波动数据
        
        Args:
            ticker: 股票代码
            current_price: 当前价格
            days: 天数
            
        Returns:
            包含 OHLCV 数据的 DataFrame
        """
        np.random.seed(hash(ticker) % 2**32)
        
        # 生成日收益率 (均值接近0，波动率约2%)
        daily_returns = np.random.normal(0.0005, 0.02, days)
        
        # 从当前价格反推历史价格
        price_factors = np.cumprod(1 / (1 + daily_returns[::-1]))[::-1]
        prices = current_price / price_factors[-1] * price_factors
        
        # 确保最后一个价格接近当前价格
        prices = prices * (current_price / prices[-1])
        
        # 生成 OHLCV 数据
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        df = pd.DataFrame({
            'Open': prices * (1 + np.random.uniform(-0.005, 0.005, days)),
            'High': prices * (1 + np.random.uniform(0.001, 0.02, days)),
            'Low': prices * (1 - np.random.uniform(0.001, 0.02, days)),
            'Close': prices,
            'Volume': np.random.randint(10000000, 100000000, days)
        }, index=dates)
        
        return df
    
    def analyze(self, ticker: str) -> Dict[str, Any]:
        """
        对股票进行全面分析
        
        Args:
            ticker: 股票代码
            
        Returns:
            包含分析结果的字典
        """
        print(f"\n{'='*60}")
        print(f"  正在分析股票: {ticker.upper()}")
        print(f"{'='*60}\n")
        
        result = {
            'ticker': ticker.upper(),
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'success',
            'data': {},
            'data_source': 'yfinance'  # 记录数据源
        }
        
        try:
            # Step 1: 获取价格数据
            print("[1/4] 获取历史价格数据...")
            price_data = self.market_fetcher.get_price_history(ticker, period="1y")
            
            # 如果 yfinance 失败，使用 finviz 获取当前价格并生成模拟数据
            if price_data.empty:
                print("      ⚠ yfinance 数据获取失败，尝试备选数据源...")
                current_price = self._get_price_from_finviz(ticker)
                
                if current_price is None:
                    result['status'] = 'error'
                    result['error'] = '无法从任何数据源获取价格数据'
                    return result
                
                # 生成模拟历史数据用于技术分析
                price_data = self._generate_simulated_price_data(ticker, current_price)
                result['data_source'] = 'finviz (价格) + 模拟数据 (历史)'
                print(f"      ✓ 从 finviz 获取当前价格: ${current_price:.2f}")
                print(f"      ✓ 生成 {len(price_data)} 天模拟历史数据用于技术分析")
            else:
                current_price = float(price_data['Close'].iloc[-1])
                print(f"      ✓ 获取到 {len(price_data)} 条价格记录")
                print(f"      ✓ 当前价格: ${current_price:.2f}")
            
            # Step 2: 获取财务数据
            print("\n[2/4] 获取财务指标...")
            financials = self.market_fetcher.get_financials(ticker)
            
            # 如果 yfinance 财务数据不完整，使用 finviz 补充
            if not any(financials.values()):
                print("      ⚠ yfinance 财务数据不完整，尝试 finviz...")
                financials = self._get_financials_from_finviz(ticker)
                if result['data_source'] == 'yfinance':
                    result['data_source'] = 'yfinance + finviz'
            
            earnings = self.market_fetcher.get_earnings_reports(ticker, years=1)
            
            # 如果 earnings 信息不完整，使用 finviz 补充
            if not earnings.get('summary'):
                earnings = self._get_earnings_from_finviz(ticker)
            
            print(f"      ✓ PE: {financials.get('PE', 'N/A')}")
            print(f"      ✓ ROE: {financials.get('ROE', 'N/A')}%")
            
            # Step 3: 技术分析
            print("\n[3/4] 执行技术分析...")
            tech_indicators = self.tech_analyzer.analyze(price_data)
            print(f"      ✓ RSI: {tech_indicators.rsi:.2f}" if tech_indicators.rsi else "      ✓ RSI: N/A")
            print(f"      ✓ MACD 趋势: {tech_indicators.macd_trend}")
            print(f"      ✓ 综合信号: {tech_indicators.overall_signal}")
            
            # Step 4: 新闻情感分析
            print("\n[4/4] 获取新闻并分析情感...")
            news = self.market_fetcher.get_news(ticker, limit=5)
            sentiment_results = self.sentiment_analyzer.analyze_news(news)
            print(f"      ✓ 获取到 {len(news)} 条新闻")
            print(f"      ✓ 平均情感得分: {sentiment_results['average_polarity']:+.4f}")
            print(f"      ✓ 整体情感: {sentiment_results['overall_sentiment']}")
            
            # 整合分析结果
            result['data'] = self._build_summary(
                ticker=ticker,
                current_price=current_price,
                financials=financials,
                earnings=earnings,
                tech_indicators=tech_indicators,
                sentiment_results=sentiment_results,
                news=news
            )
            
        except Exception as e:
            logger.error(f"分析 {ticker} 时出错: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def _build_summary(
        self,
        ticker: str,
        current_price: float,
        financials: Dict,
        earnings: Dict,
        tech_indicators,
        sentiment_results: Dict,
        news: list
    ) -> Dict[str, Any]:
        """
        构建分析摘要
        
        Args:
            所有分析数据
            
        Returns:
            结构化摘要字典
        """
        # 获取行业信息和行业平均 PE
        sector = earnings.get('summary', {}).get('sector', 'Technology')
        industry_avg_pe = INDUSTRY_AVG_PE.get(sector, INDUSTRY_AVG_PE['default'])
        
        # 计算 PE 相对于行业平均的状态
        pe = financials.get('PE')
        pe_status = 'N/A'
        pe_diff_pct = None
        if pe is not None:
            pe_diff_pct = ((pe - industry_avg_pe) / industry_avg_pe) * 100
            if pe < industry_avg_pe * 0.8:
                pe_status = 'Undervalued'
            elif pe > industry_avg_pe * 1.2:
                pe_status = 'Overvalued'
            else:
                pe_status = 'Fair'
        
        # 将技术信号转换为买卖建议
        tech_signal = tech_indicators.overall_signal
        if tech_signal in ['Strong_Buy', 'Buy']:
            tech_recommendation = 'Buy'
        elif tech_signal in ['Strong_Sell', 'Sell']:
            tech_recommendation = 'Sell'
        else:
            tech_recommendation = 'Hold'
        
        # 情感得分转换 (-1 到 1 转为 0 到 100)
        sentiment_score = (sentiment_results['average_polarity'] + 1) * 50
        
        # 构建摘要
        summary = {
            'Current_Price': {
                'value': round(current_price, 2),
                'currency': 'USD'
            },
            'Technicals_Signal': {
                'recommendation': tech_recommendation,
                'overall_signal': tech_signal,
                'signals': tech_indicators.signals,
                'indicators': {
                    'RSI': round(tech_indicators.rsi, 2) if tech_indicators.rsi else None,
                    'RSI_Signal': tech_indicators.rsi_signal,
                    'MACD': round(tech_indicators.macd, 4) if tech_indicators.macd else None,
                    'MACD_Trend': tech_indicators.macd_trend,
                    'SMA_50': round(tech_indicators.sma_50, 2) if tech_indicators.sma_50 else None,
                    'SMA_200': round(tech_indicators.sma_200, 2) if tech_indicators.sma_200 else None,
                    'MA_Signal': tech_indicators.ma_signal,
                    'BB_Width': round(tech_indicators.bb_width, 2) if tech_indicators.bb_width else None
                }
            },
            'Sentiment_Score': {
                'value': round(sentiment_score, 2),
                'raw_polarity': sentiment_results['average_polarity'],
                'level': sentiment_results['overall_sentiment'],
                'news_count': len(news),
                'distribution': sentiment_results['sentiment_distribution']
            },
            'Valuation_Metrics': {
                'PE': pe,
                'PE_Status': pe_status,
                'Industry_Avg_PE': industry_avg_pe,
                'PE_vs_Industry': f"{pe_diff_pct:+.1f}%" if pe_diff_pct else 'N/A',
                'PB': financials.get('PB'),
                'ROE': financials.get('ROE'),
                'Revenue_Growth': financials.get('RevenueGrowth'),
                'Sector': sector,
                'Industry': earnings.get('summary', {}).get('industry', 'N/A'),
                'Market_Cap': earnings.get('summary', {}).get('market_cap')
            },
            'Recent_News': [
                {
                    'title': n.get('title', ''),
                    'source': n.get('publisher', ''),
                    'published': n.get('published', '')
                } for n in news[:5]
            ]
        }
        
        return summary
    
    def print_json_summary(self, result: Dict[str, Any]) -> None:
        """
        打印格式化的 JSON 摘要
        
        Args:
            result: 分析结果
        """
        print(f"\n{'='*60}")
        print("  📊 分析结果摘要 (JSON)")
        print(f"{'='*60}\n")
        
        # 格式化输出 JSON
        json_output = json.dumps(result, indent=2, ensure_ascii=False)
        print(json_output)
        
        # 打印自然语言总结
        if result['status'] == 'success':
            self._print_natural_language_summary(result)
    
    def _print_natural_language_summary(self, result: Dict[str, Any]) -> None:
        """
        打印自然语言摘要
        
        Args:
            result: 分析结果
        """
        data = result['data']
        ticker = result['ticker']
        
        price = data['Current_Price']['value']
        tech_rec = data['Technicals_Signal']['recommendation']
        tech_signal = data['Technicals_Signal']['overall_signal']
        sentiment = data['Sentiment_Score']['level']
        sentiment_score = data['Sentiment_Score']['value']
        pe = data['Valuation_Metrics']['PE']
        pe_status = data['Valuation_Metrics']['PE_Status']
        industry_pe = data['Valuation_Metrics']['Industry_Avg_PE']
        roe = data['Valuation_Metrics']['ROE']
        sector = data['Valuation_Metrics']['Sector']
        
        print(f"\n{'='*60}")
        print("  📝 自然语言分析总结")
        print(f"{'='*60}\n")
        
        # 构建自然语言描述
        summary_lines = [
            f"【{ticker} 股票分析报告】",
            f"",
            f"📈 价格信息：",
            f"   当前股价为 ${price:.2f}。",
            f"",
            f"📊 技术面分析：",
            f"   综合技术信号为 {tech_signal}，交易建议为【{tech_rec}】。",
        ]
        
        # RSI 分析
        rsi = data['Technicals_Signal']['indicators'].get('RSI')
        if rsi:
            if rsi > 70:
                summary_lines.append(f"   RSI 指标为 {rsi:.1f}，处于超买区域，需警惕回调风险。")
            elif rsi < 30:
                summary_lines.append(f"   RSI 指标为 {rsi:.1f}，处于超卖区域，可能存在反弹机会。")
            else:
                summary_lines.append(f"   RSI 指标为 {rsi:.1f}，处于中性区域。")
        
        # 均线分析
        ma_signal = data['Technicals_Signal']['indicators'].get('MA_Signal')
        if ma_signal:
            if 'Golden' in ma_signal:
                summary_lines.append(f"   均线呈现黄金交叉，中长期趋势向好。")
            elif 'Death' in ma_signal:
                summary_lines.append(f"   均线呈现死亡交叉，中长期趋势承压。")
        
        summary_lines.extend([
            f"",
            f"💭 市场情绪：",
            f"   新闻情感得分为 {sentiment_score:.1f}/100，整体情绪{sentiment}。",
        ])
        
        summary_lines.extend([
            f"",
            f"💰 估值分析：",
        ])
        
        if pe:
            pe_diff = data['Valuation_Metrics']['PE_vs_Industry']
            summary_lines.append(f"   当前 PE 为 {pe:.1f}，行业({sector})平均 PE 为 {industry_pe}，")
            summary_lines.append(f"   相对行业平均{pe_diff}，估值状态为【{pe_status}】。")
        else:
            summary_lines.append(f"   PE 数据暂不可用。")
        
        if roe:
            if roe > 20:
                summary_lines.append(f"   ROE 为 {roe:.1f}%，盈利能力优秀。")
            elif roe > 10:
                summary_lines.append(f"   ROE 为 {roe:.1f}%，盈利能力良好。")
            else:
                summary_lines.append(f"   ROE 为 {roe:.1f}%，盈利能力一般。")
        
        # 最终建议
        summary_lines.extend([
            f"",
            f"🎯 综合建议：",
        ])
        
        # 根据各项指标综合判断
        score = 0
        if tech_rec == 'Buy':
            score += 1
        elif tech_rec == 'Sell':
            score -= 1
        
        if sentiment in ['Positive', 'Very_Positive']:
            score += 1
        elif sentiment in ['Negative', 'Very_Negative']:
            score -= 1
        
        if pe_status == 'Undervalued':
            score += 1
        elif pe_status == 'Overvalued':
            score -= 1
        
        if score >= 2:
            final_rec = "建议买入，多项指标显示积极信号。"
        elif score <= -2:
            final_rec = "建议卖出或观望，多项指标显示消极信号。"
        elif score == 1:
            final_rec = "可以考虑建仓或加仓，但建议分批操作。"
        elif score == -1:
            final_rec = "建议谨慎，可以考虑减仓或观望。"
        else:
            final_rec = "信号中性，建议持有观望，等待更明确的信号。"
        
        summary_lines.append(f"   {final_rec}")
        
        for line in summary_lines:
            print(line)
        
        print(f"\n{'='*60}\n")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='美股量化分析系统 - 股票综合分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python analyze_stock.py --ticker AAPL
    python analyze_stock.py --ticker NVDA
    python analyze_stock.py --ticker GOOGL
        """
    )
    
    parser.add_argument(
        '--ticker', '-t',
        type=str,
        required=True,
        help='股票代码 (如 AAPL, NVDA, GOOGL)'
    )
    
    args = parser.parse_args()
    
    # 执行分析
    analyzer = StockAnalyzer()
    result = analyzer.analyze(args.ticker)
    
    # 输出结果
    analyzer.print_json_summary(result)
    
    # 返回状态码
    return 0 if result['status'] == 'success' else 1


if __name__ == '__main__':
    sys.exit(main())
