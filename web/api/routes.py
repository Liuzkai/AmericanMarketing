"""
API 路由模块
提供 RESTful API 接口供前端调用
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import logging
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tools.market_data import MarketFetcher
from tools.analyzer import TechnicalAnalyzer, SentimentAnalyzer
from finvizfinance.screener.overview import Overview as FinvizScreener
import pandas as pd

# 配置日志
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# 创建 API 蓝图
api_bp = Blueprint('api', __name__)


# 复用 analyze_stock.py 中的 StockAnalyzer 逻辑
class APIStockAnalyzer:
    """API 股票分析器（复用现有分析逻辑）"""

    def __init__(self):
        self.market_fetcher = MarketFetcher(log_level=logging.WARNING)
        self.tech_analyzer = TechnicalAnalyzer(log_level=logging.WARNING)
        self.sentiment_analyzer = SentimentAnalyzer(log_level=logging.WARNING)

    def analyze(self, ticker: str) -> dict:
        """
        对股票进行全面分析

        Returns:
            包含分析结果的字典
        """
        result = {
            'ticker': ticker.upper(),
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data': {}
        }

        # 1. 获取价格数据
        price_data = self.market_fetcher.get_price_history(ticker, period="1y")
        if price_data.empty:
            raise ValueError(f"无法获取 {ticker} 的价格数据")

        current_price = float(price_data['Close'].iloc[-1])
        prev_price = float(price_data['Close'].iloc[-2]) if len(price_data) > 1 else current_price
        price_change = current_price - prev_price
        price_change_percent = (price_change / prev_price * 100) if prev_price > 0 else 0

        result['data']['current_price'] = round(current_price, 2)
        result['data']['price_change'] = round(price_change, 2)
        result['data']['price_change_percent'] = round(price_change_percent, 2)

        # 2. 技术分析
        tech_result = self.tech_analyzer.analyze(price_data)

        # 提取技术指标
        last_row = tech_result.data.iloc[-1]
        result['data']['technical_indicators'] = {
            'rsi': {
                'value': round(last_row['RSI'], 2) if pd.notna(last_row['RSI']) else None,
                'signal': tech_result.rsi_signal
            },
            'macd': {
                'value': round(last_row['MACD'], 2) if pd.notna(last_row['MACD']) else None,
                'signal': round(last_row['MACD_Signal'], 2) if pd.notna(last_row['MACD_Signal']) else None,
                'histogram': round(last_row['MACD_Hist'], 2) if pd.notna(last_row['MACD_Hist']) else None,
                'trend': tech_result.macd_trend
            },
            'bollinger_bands': {
                'upper': round(last_row['BB_Upper'], 2) if pd.notna(last_row['BB_Upper']) else None,
                'middle': round(last_row['BB_Middle'], 2) if pd.notna(last_row['BB_Middle']) else None,
                'lower': round(last_row['BB_Lower'], 2) if pd.notna(last_row['BB_Lower']) else None,
                'signal': tech_result.bb_signal
            },
            'sma_50': round(last_row['SMA_50'], 2) if pd.notna(last_row['SMA_50']) else None,
            'sma_200': round(last_row['SMA_200'], 2) if pd.notna(last_row['SMA_200']) else None,
            'ma_signal': tech_result.ma_signal,
            'overall_signal': tech_result.overall_signal
        }

        # 3. 财务数据
        financials = self.market_fetcher.get_financials(ticker)
        result['data']['financial_metrics'] = {
            'pe_ratio': financials.get('PE'),
            'pb_ratio': financials.get('PB'),
            'roe': financials.get('ROE'),
            'revenue_growth': financials.get('RevenueGrowth'),
            'market_cap': 'N/A',  # 从 earnings 获取
            'valuation_status': 'Fair'  # 简化版本，默认合理
        }

        # 4. 获取新闻并进行情绪分析
        news = self.market_fetcher.get_news(ticker, limit=10)
        sentiment_result = self.sentiment_analyzer.analyze_news(news)

        result['data']['sentiment'] = {
            'average_polarity': round(sentiment_result['average_polarity'], 2),
            'overall_sentiment': sentiment_result['overall_sentiment'],
            'distribution': sentiment_result['distribution']
        }

        # 5. 生成投资建议
        recommendation = self._generate_recommendation(
            tech_result.overall_signal,
            sentiment_result['overall_sentiment'],
            financials.get('PE')
        )
        result['data']['recommendation'] = recommendation

        # 6. 价格历史（用于图表，最近90天）
        price_history = price_data.tail(90)
        result['data']['price_history'] = []
        for idx, row in price_history.iterrows():
            result['data']['price_history'].append({
                'date': idx.strftime('%Y-%m-%d'),
                'open': round(row['Open'], 2),
                'high': round(row['High'], 2),
                'low': round(row['Low'], 2),
                'close': round(row['Close'], 2),
                'volume': int(row['Volume'])
            })

        # 7. 新闻列表
        result['data']['news'] = news[:5]  # 只返回前5条

        return result

    def _generate_recommendation(self, tech_signal: str, sentiment: str, pe: float) -> dict:
        """生成投资建议"""
        score = 50  # 基础分50
        reasons = []

        # 技术信号评分
        if tech_signal == 'Strong_Buy':
            score += 20
            reasons.append("强劲的技术指标")
        elif tech_signal == 'Buy':
            score += 10
            reasons.append("看涨的技术指标")
        elif tech_signal == 'Sell':
            score -= 10
            reasons.append("看跌的技术指标")
        elif tech_signal == 'Strong_Sell':
            score -= 20
            reasons.append("弱势的技术指标")

        # 情绪评分
        if sentiment in ['Very_Positive', 'Positive']:
            score += 15
            reasons.append("正面新闻情绪")
        elif sentiment in ['Negative', 'Very_Negative']:
            score -= 15
            reasons.append("负面新闻情绪")

        # PE 估值评分（简化版）
        if pe and pe > 0:
            if pe < 15:
                score += 10
                reasons.append("低估值")
            elif pe > 40:
                score -= 10
                reasons.append("高估值")

        # 确定行动建议
        if score >= 70:
            action = "强烈买入"
        elif score >= 60:
            action = "买入"
        elif score >= 40:
            action = "持有"
        elif score >= 30:
            action = "卖出"
        else:
            action = "强烈卖出"

        return {
            'action': action,
            'score': score,
            'reasons': reasons if reasons else ["市场中性"]
        }


# 实例化分析器（单例模式，提高性能）
stock_analyzer = APIStockAnalyzer()


@api_bp.route('/stock/<ticker>/analyze', methods=['GET'])
def analyze_stock(ticker):
    """
    单股分析 API

    GET /api/v1/stock/AAPL/analyze
    """
    try:
        result = stock_analyzer.analyze(ticker)
        return jsonify({
            'success': True,
            'data': result['data'],
            'timestamp': result['analysis_time']
        })
    except Exception as e:
        logger.error(f"分析 {ticker} 时出错: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/stock/<ticker>/quote', methods=['GET'])
def get_quote(ticker):
    """
    快速报价 API

    GET /api/v1/stock/AAPL/quote
    """
    try:
        fetcher = MarketFetcher(log_level=logging.WARNING)
        price_data = fetcher.get_price_history(ticker, period="5d")

        if price_data.empty:
            raise ValueError(f"无法获取 {ticker} 的价格数据")

        last_row = price_data.iloc[-1]
        prev_row = price_data.iloc[-2] if len(price_data) > 1 else last_row

        current_price = float(last_row['Close'])
        prev_price = float(prev_row['Close'])
        change = current_price - prev_price
        change_percent = (change / prev_price * 100) if prev_price > 0 else 0

        return jsonify({
            'success': True,
            'data': {
                'ticker': ticker.upper(),
                'price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': int(last_row['Volume']),
                'market_cap': 'N/A'
            }
        })
    except Exception as e:
        logger.error(f"获取 {ticker} 报价时出错: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/market/scan', methods=['GET'])
def market_scan():
    """
    市场扫描 API

    GET /api/v1/market/scan?index=sp500&max_pe=25&max_peg=1&limit=50
    """
    try:
        # 获取查询参数
        index = request.args.get('index', 'sp500')
        max_pe = int(float(request.args.get('max_pe', 25)))  # 转换为整数
        max_peg = int(float(request.args.get('max_peg', 1)))  # PEG 也必须是整数
        limit = int(request.args.get('limit', 50))

        # 使用 finviz 筛选器
        screener = FinvizScreener()

        # 映射指数名称到 finviz 接受的格式
        index_mapping = {
            'sp500': 'S&P 500',
            'nasdaq': 'NASDAQ 100',
            'dow': 'DJIA',
            'russell': 'RUSSELL 2000',
            'any': 'Any'
        }

        finviz_index = index_mapping.get(index.lower(), 'S&P 500')

        # 设置筛选条件（finviz 要求整数值）
        filters_dict = {
            'Index': finviz_index,
            'P/E': f'Under {max_pe}',
            'PEG': f'Under {max_peg}'
        }

        screener.set_filter(filters_dict=filters_dict)
        df = screener.screener_view()

        if df.empty:
            return jsonify({
                'success': True,
                'data': {
                    'total_scanned': 0,
                    'opportunities': [],
                    'statistics': {}
                }
            })

        # 限制结果数量
        df = df.head(limit)

        # 转换为 API 响应格式
        opportunities = []
        for _, row in df.iterrows():
            opportunities.append({
                'ticker': row.get('Ticker', 'N/A'),
                'price': row.get('Price', 0),
                'opportunity_score': 75,  # 简化版，固定分数
                'pe': row.get('P/E', None),
                'peg': row.get('PEG', None),
                'pb': row.get('P/B', None),
                'market_cap': row.get('Market Cap', 'N/A'),
                'sector': row.get('Sector', 'N/A'),
                'industry': row.get('Industry', 'N/A'),
                'rsi': None,
                'tech_signal': 'Neutral',
                'sentiment_score': 0.0,
                'sentiment_level': 'Neutral'
            })

        # 统计信息
        statistics = {
            'sector_distribution': df['Sector'].value_counts().to_dict() if 'Sector' in df.columns else {},
            'signal_distribution': {'Neutral': len(opportunities)}
        }

        return jsonify({
            'success': True,
            'data': {
                'total_scanned': len(df),
                'opportunities': opportunities,
                'statistics': statistics
            },
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        logger.error(f"市场扫描时出错: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
