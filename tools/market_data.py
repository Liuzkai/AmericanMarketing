# -*- coding: utf-8 -*-
"""
美股市场数据获取模块
US Stock Market Data Fetcher

本模块提供 MarketFetcher 类，用于获取美股市场数据，包括：
- 历史价格数据 (OHLCV)
- 财务指标 (PE, PB, ROE, 营收增长率)
- 新闻数据
- 财报数据

基于 GitHub 成熟方案，使用 yfinance 和 finvizfinance 作为数据源。
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

import pandas as pd
import yfinance as yf
from finvizfinance.quote import finvizfinance

# 默认请求间隔时间 (秒)
DEFAULT_REQUEST_DELAY = 1.0
# 默认重试次数
DEFAULT_MAX_RETRIES = 3
# 重试间隔基数 (秒)
RETRY_DELAY_BASE = 2.0

# 配置模块级日志
logger = logging.getLogger(__name__)


class MarketFetcher:
    """
    市场数据获取器
    
    提供统一的接口获取美股市场数据，支持：
    - 历史价格数据 (OHLCV)
    - 财务指标 (PE, PB, ROE, 营收增长率)
    - 新闻数据
    - 财报数据
    
    示例用法:
        >>> fetcher = MarketFetcher()
        >>> price_data = fetcher.get_price_history("AAPL")
        >>> financials = fetcher.get_financials("AAPL")
        >>> news = fetcher.get_news("AAPL")
        >>> earnings = fetcher.get_earnings_reports("AAPL", years=1)
    """
    
    def __init__(self, log_level: int = logging.INFO, request_delay: float = DEFAULT_REQUEST_DELAY):
        """
        初始化 MarketFetcher
        
        Args:
            log_level: 日志级别，默认为 INFO
            request_delay: 请求间隔时间 (秒)，用于避免 API 限流
        """
        self._setup_logging(log_level)
        self._request_delay = request_delay
        self._last_request_time = 0
        logger.info("MarketFetcher 初始化完成")
    
    def _wait_for_rate_limit(self) -> None:
        """
        等待以遵守 API 限流
        """
        elapsed = time.time() - self._last_request_time
        if elapsed < self._request_delay:
            sleep_time = self._request_delay - elapsed
            time.sleep(sleep_time)
        self._last_request_time = time.time()
    
    def _retry_on_rate_limit(self, func, *args, max_retries: int = DEFAULT_MAX_RETRIES, **kwargs):
        """
        带重试机制的函数调用
        
        Args:
            func: 要调用的函数
            *args: 位置参数
            max_retries: 最大重试次数
            **kwargs: 关键字参数
            
        Returns:
            函数返回值
        """
        last_exception = None
        for attempt in range(max_retries):
            try:
                self._wait_for_rate_limit()
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                error_msg = str(e).lower()
                if 'rate limit' in error_msg or 'too many requests' in error_msg:
                    wait_time = RETRY_DELAY_BASE * (attempt + 1)
                    logger.warning(f"API 限流，等待 {wait_time} 秒后重试 (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise e
        raise last_exception
    
    def _setup_logging(self, log_level: int) -> None:
        """
        配置日志
        
        Args:
            log_level: 日志级别
        """
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(log_level)
    
    def _get_ticker(self, ticker: str) -> yf.Ticker:
        """
        获取 yfinance Ticker 对象
        
        Args:
            ticker: 股票代码
            
        Returns:
            yfinance Ticker 对象
        """
        return yf.Ticker(ticker.upper())
    
    # ==================== 历史价格数据 ====================
    
    def get_price_history(
        self, 
        ticker: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        获取股票历史价格数据 (OHLCV)
        
        Args:
            ticker: 股票代码 (如 "AAPL", "GOOGL")
            period: 时间范围，可选值：1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
                   默认为 "1y" (1年)
            interval: 数据间隔，可选值：1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
                     默认为 "1d" (日线)
        
        Returns:
            包含 Open, High, Low, Close, Volume 列的 pandas DataFrame
            如果获取失败，返回空 DataFrame
        
        Raises:
            无异常抛出，失败时返回空 DataFrame 并记录警告
        """
        logger.info(f"获取 {ticker} 的历史价格数据，周期: {period}，间隔: {interval}")
        
        try:
            stock = self._get_ticker(ticker)
            # 使用重试机制获取数据
            df = self._retry_on_rate_limit(stock.history, period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"股票 {ticker} 没有可用的历史数据")
                return pd.DataFrame()
            
            # 只保留 OHLCV 列
            columns_to_keep = ['Open', 'High', 'Low', 'Close', 'Volume']
            available_columns = [col for col in columns_to_keep if col in df.columns]
            df = df[available_columns]
            
            logger.info(f"成功获取 {ticker} 的 {len(df)} 条历史数据")
            return df
            
        except Exception as e:
            logger.error(f"获取 {ticker} 历史数据失败: {str(e)}")
            return pd.DataFrame()
    
    # ==================== 财务指标 ====================
    
    def get_financials(self, ticker: str) -> Dict[str, Optional[float]]:
        """
        获取股票关键财务指标
        
        Args:
            ticker: 股票代码 (如 "AAPL", "GOOGL")
        
        Returns:
            包含以下键的字典:
            - PE: 市盈率 (Price to Earnings)
            - PB: 市净率 (Price to Book)
            - ROE: 净资产收益率 (Return on Equity)
            - RevenueGrowth: 营收增长率
            
            不可用的数据返回 None
        """
        logger.info(f"获取 {ticker} 的财务指标")
        
        result = {
            'PE': None,
            'PB': None,
            'ROE': None,
            'RevenueGrowth': None
        }
        
        try:
            stock = self._get_ticker(ticker)
            # 使用重试机制获取数据
            self._wait_for_rate_limit()
            info = stock.info
            
            # 获取 PE (市盈率)
            result['PE'] = info.get('trailingPE') or info.get('forwardPE')
            
            # 获取 PB (市净率)
            result['PB'] = info.get('priceToBook')
            
            # 获取 ROE (净资产收益率)
            result['ROE'] = info.get('returnOnEquity')
            if result['ROE'] is not None:
                result['ROE'] = round(result['ROE'] * 100, 2)  # 转为百分比
            
            # 获取营收增长率
            result['RevenueGrowth'] = info.get('revenueGrowth')
            if result['RevenueGrowth'] is not None:
                result['RevenueGrowth'] = round(result['RevenueGrowth'] * 100, 2)  # 转为百分比
            
            logger.info(f"成功获取 {ticker} 的财务指标: {result}")
            return result
            
        except Exception as e:
            logger.error(f"获取 {ticker} 财务指标失败: {str(e)}")
            return result
    
    # ==================== 新闻数据 ====================
    
    def get_news(self, ticker: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        获取股票相关新闻
        
        优先使用 yfinance 获取新闻，如果失败则使用 finvizfinance 作为备选
        
        Args:
            ticker: 股票代码 (如 "AAPL", "GOOGL")
            limit: 返回新闻条数，默认 5 条
        
        Returns:
            新闻列表，每条新闻包含:
            - title: 新闻标题
            - publisher: 新闻来源
            - link: 新闻链接
            - published: 发布时间 (如可用)
            
            如果无新闻，返回空列表
        """
        logger.info(f"获取 {ticker} 的新闻数据，限制 {limit} 条")
        
        # 首先尝试 yfinance
        news = self._get_news_from_yfinance(ticker, limit)
        
        # 如果 yfinance 失败，尝试 finvizfinance
        if not news:
            logger.info(f"yfinance 未获取到 {ticker} 新闻，尝试 finvizfinance")
            news = self._get_news_from_finviz(ticker, limit)
        
        logger.info(f"共获取 {ticker} 的 {len(news)} 条新闻")
        return news
    
    def _get_news_from_yfinance(self, ticker: str, limit: int) -> List[Dict[str, str]]:
        """
        从 yfinance 获取新闻
        
        Args:
            ticker: 股票代码
            limit: 返回条数
            
        Returns:
            新闻列表
        """
        try:
            stock = self._get_ticker(ticker)
            self._wait_for_rate_limit()
            raw_news = stock.news
            
            if not raw_news:
                return []
            
            news_list = []
            for item in raw_news[:limit]:
                news_item = {
                    'title': item.get('title', ''),
                    'publisher': item.get('publisher', ''),
                    'link': item.get('link', ''),
                    'published': ''
                }
                
                # 转换时间戳
                if 'providerPublishTime' in item:
                    try:
                        timestamp = item['providerPublishTime']
                        news_item['published'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        pass
                
                news_list.append(news_item)
            
            return news_list
            
        except Exception as e:
            logger.warning(f"从 yfinance 获取 {ticker} 新闻失败: {str(e)}")
            return []
    
    def _get_news_from_finviz(self, ticker: str, limit: int) -> List[Dict[str, str]]:
        """
        从 finvizfinance 获取新闻 (备选数据源)
        
        Args:
            ticker: 股票代码
            limit: 返回条数
            
        Returns:
            新闻列表
        """
        try:
            stock = finvizfinance(ticker.upper())
            news_df = stock.ticker_news()
            
            if news_df is None or news_df.empty:
                return []
            
            news_list = []
            for _, row in news_df.head(limit).iterrows():
                news_item = {
                    'title': str(row.get('Title', '')),
                    'publisher': str(row.get('Source', '')),
                    'link': str(row.get('Link', '')),
                    'published': str(row.get('Date', ''))
                }
                news_list.append(news_item)
            
            return news_list
            
        except Exception as e:
            logger.warning(f"从 finvizfinance 获取 {ticker} 新闻失败: {str(e)}")
            return []
    
    # ==================== 财报数据 ====================
    
    def get_earnings_reports(
        self, 
        ticker: str, 
        years: int = 1
    ) -> Dict[str, Any]:
        """
        获取公司财报数据
        
        Args:
            ticker: 股票代码 (如 "AAPL", "GOOGL")
            years: 获取最近几年的数据，默认 1 年
        
        Returns:
            包含财报数据的字典:
            - annual: 年度财报数据列表
            - quarterly: 季度财报数据列表
            - summary: 财报摘要信息
            
            每条财报包含:
            - report_date: 财报日期
            - report_type: 财报类型 (Annual/Q1/Q2/Q3/Q4)
            - revenue: 营收
            - net_income: 净利润
            - eps: 每股收益
            - gross_margin: 毛利率 (如可用)
            - operating_income: 运营利润 (如可用)
        """
        logger.info(f"获取 {ticker} 最近 {years} 年的财报数据")
        
        result = {
            'annual': [],
            'quarterly': [],
            'summary': {}
        }
        
        try:
            stock = self._get_ticker(ticker)
            
            # 获取年度财报 (带重试)
            self._wait_for_rate_limit()
            result['annual'] = self._parse_income_statement(
                stock.income_stmt, 
                'Annual',
                years
            )
            
            # 获取季度财报 (带重试)
            self._wait_for_rate_limit()
            result['quarterly'] = self._parse_income_statement(
                stock.quarterly_income_stmt,
                'Quarterly',
                years * 4  # 季度数据
            )
            
            # 添加摘要信息
            info = stock.info
            result['summary'] = {
                'company_name': info.get('longName', ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap'),
                'currency': info.get('currency', 'USD')
            }
            
            logger.info(f"成功获取 {ticker} 的财报数据: "
                       f"{len(result['annual'])} 条年报, "
                       f"{len(result['quarterly'])} 条季报")
            
        except Exception as e:
            logger.error(f"获取 {ticker} 财报数据失败: {str(e)}")
            # 尝试使用 finviz 作为备选
            result = self._get_earnings_from_finviz(ticker)
        
        return result
    
    def _parse_income_statement(
        self, 
        df: pd.DataFrame, 
        report_type: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        解析损益表数据
        
        Args:
            df: 损益表 DataFrame
            report_type: 报告类型 (Annual/Quarterly)
            limit: 限制条数
            
        Returns:
            解析后的财报数据列表
        """
        reports = []
        
        if df is None or df.empty:
            return reports
        
        # 获取最近的几列数据
        columns = df.columns[:limit] if len(df.columns) > limit else df.columns
        
        for col in columns:
            try:
                report = {
                    'report_date': col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col),
                    'report_type': report_type
                }
                
                # 确定季度类型
                if report_type == 'Quarterly' and hasattr(col, 'month'):
                    quarter_map = {1: 'Q1', 2: 'Q1', 3: 'Q1', 
                                   4: 'Q2', 5: 'Q2', 6: 'Q2',
                                   7: 'Q3', 8: 'Q3', 9: 'Q3',
                                   10: 'Q4', 11: 'Q4', 12: 'Q4'}
                    report['report_type'] = quarter_map.get(col.month, 'Quarterly')
                
                # 提取关键财务数据
                report['revenue'] = self._safe_get_value(df, 'Total Revenue', col)
                report['net_income'] = self._safe_get_value(df, 'Net Income', col)
                report['gross_profit'] = self._safe_get_value(df, 'Gross Profit', col)
                report['operating_income'] = self._safe_get_value(df, 'Operating Income', col)
                report['ebit'] = self._safe_get_value(df, 'EBIT', col)
                
                # 计算毛利率
                if report['revenue'] and report['gross_profit']:
                    report['gross_margin'] = round(report['gross_profit'] / report['revenue'] * 100, 2)
                else:
                    report['gross_margin'] = None
                
                # 计算运营利润率
                if report['revenue'] and report['operating_income']:
                    report['operating_margin'] = round(report['operating_income'] / report['revenue'] * 100, 2)
                else:
                    report['operating_margin'] = None
                
                # EPS 需要从其他数据源获取
                report['eps'] = None
                
                reports.append(report)
                
            except Exception as e:
                logger.warning(f"解析财报数据出错: {str(e)}")
                continue
        
        return reports
    
    def _safe_get_value(
        self, 
        df: pd.DataFrame, 
        row_name: str, 
        col: Any
    ) -> Optional[float]:
        """
        安全地从 DataFrame 获取值
        
        Args:
            df: DataFrame
            row_name: 行名
            col: 列名
            
        Returns:
            数值或 None
        """
        try:
            if row_name in df.index:
                value = df.loc[row_name, col]
                if pd.notna(value):
                    return float(value)
        except Exception:
            pass
        return None
    
    def _get_earnings_from_finviz(self, ticker: str) -> Dict[str, Any]:
        """
        从 finvizfinance 获取财务数据 (备选数据源)
        
        Args:
            ticker: 股票代码
            
        Returns:
            财务数据字典
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
                result['summary'] = {
                    'company_name': fundament.get('Company', ticker),
                    'sector': fundament.get('Sector', 'N/A'),
                    'industry': fundament.get('Industry', 'N/A'),
                    'market_cap': fundament.get('Market Cap', 'N/A'),
                    'eps': fundament.get('EPS (ttm)'),
                    'pe': fundament.get('P/E'),
                    'revenue': fundament.get('Sales'),
                    'profit_margin': fundament.get('Profit Margin')
                }
                
            logger.info(f"从 finvizfinance 获取 {ticker} 基本财务数据成功")
            
        except Exception as e:
            logger.warning(f"从 finvizfinance 获取 {ticker} 数据失败: {str(e)}")
        
        return result
    
    # ==================== JSON 序列化支持 ====================
    
    def to_json_serializable(self, data: Any) -> Any:
        """
        将数据转换为 JSON 可序列化格式
        
        支持转换:
        - pandas DataFrame -> dict
        - pandas Timestamp -> str
        - numpy 类型 -> Python 原生类型
        
        Args:
            data: 需要转换的数据
            
        Returns:
            JSON 可序列化的数据
        """
        if isinstance(data, pd.DataFrame):
            # DataFrame 转换为字典列表
            data = data.reset_index()
            result = data.to_dict(orient='records')
            # 递归处理每个值
            return [self.to_json_serializable(record) for record in result]
        
        elif isinstance(data, pd.Series):
            return self.to_json_serializable(data.to_dict())
        
        elif isinstance(data, dict):
            return {k: self.to_json_serializable(v) for k, v in data.items()}
        
        elif isinstance(data, list):
            return [self.to_json_serializable(item) for item in data]
        
        elif isinstance(data, (pd.Timestamp, datetime)):
            return data.strftime('%Y-%m-%d %H:%M:%S')
        
        elif hasattr(data, 'item'):  # numpy 标量类型
            return data.item()
        
        elif pd.isna(data):
            return None
        
        return data
    
    def get_price_history_json(
        self, 
        ticker: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> List[Dict]:
        """
        获取历史价格数据并返回 JSON 可序列化格式
        
        Args:
            ticker: 股票代码
            period: 时间范围
            interval: 数据间隔
            
        Returns:
            JSON 可序列化的价格数据列表
        """
        df = self.get_price_history(ticker, period, interval)
        return self.to_json_serializable(df)
    
    def get_earnings_reports_json(
        self, 
        ticker: str, 
        years: int = 1
    ) -> Dict[str, Any]:
        """
        获取财报数据并返回 JSON 可序列化格式
        
        Args:
            ticker: 股票代码
            years: 年数
            
        Returns:
            JSON 可序列化的财报数据
        """
        data = self.get_earnings_reports(ticker, years)
        return self.to_json_serializable(data)


# ==================== 测试代码 ====================

if __name__ == "__main__":
    # 配置日志输出到控制台
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建 MarketFetcher 实例，设置较长的请求间隔避免限流
    fetcher = MarketFetcher(request_delay=2.0)
    
    # 只测试一只股票以避免 API 限流
    test_ticker = "AAPL"
    
    print("\n" + "="*60)
    print("美股量化分析系统 - MarketFetcher 功能测试")
    print(f"测试股票: {test_ticker}")
    print("="*60)
    
    # 1. 测试历史价格数据
    print(f"\n--- 1. 历史价格数据 (最近 5 天) ---")
    price_data = fetcher.get_price_history(test_ticker, period="5d")
    if not price_data.empty:
        print(price_data)
    else:
        print("未获取到数据")
    
    # 2. 测试财务指标
    print(f"\n--- 2. 财务指标 ---")
    financials = fetcher.get_financials(test_ticker)
    for key, value in financials.items():
        unit = '%' if key in ['ROE', 'RevenueGrowth'] and value else ''
        print(f"  {key}: {value}{unit}")
    
    # 3. 测试新闻数据
    print(f"\n--- 3. 最近新闻 (5条) ---")
    news = fetcher.get_news(test_ticker, limit=5)
    if news:
        for i, item in enumerate(news, 1):
            title = item['title'][:70] + '...' if len(item['title']) > 70 else item['title']
            print(f"  [{i}] {title}")
            print(f"      来源: {item['publisher']} | 时间: {item['published']}")
    else:
        print("  未获取到新闻")
    
    # 4. 测试财报数据
    print(f"\n--- 4. 财报数据 (最近 1 年) ---")
    earnings = fetcher.get_earnings_reports(test_ticker, years=1)
    print(f"  公司: {earnings['summary'].get('company_name', 'N/A')}")
    print(f"  行业: {earnings['summary'].get('industry', 'N/A')}")
    print(f"  板块: {earnings['summary'].get('sector', 'N/A')}")
    market_cap = earnings['summary'].get('market_cap')
    if market_cap and isinstance(market_cap, (int, float)):
        print(f"  市值: ${market_cap:,.0f}")
    else:
        print(f"  市值: {market_cap if market_cap else 'N/A'}")
    print(f"  年报数量: {len(earnings['annual'])}")
    print(f"  季报数量: {len(earnings['quarterly'])}")
    
    if earnings['quarterly']:
        print(f"\n  --- 季度财报详情 ---")
        for i, report in enumerate(earnings['quarterly'][:4], 1):
            print(f"\n  [{i}] {report['report_type']} ({report['report_date']}):")
            print(f"      营收: ${report['revenue']:,.0f}" if report['revenue'] else "      营收: N/A")
            print(f"      净利润: ${report['net_income']:,.0f}" if report['net_income'] else "      净利润: N/A")
            print(f"      毛利率: {report['gross_margin']}%" if report['gross_margin'] else "      毛利率: N/A")
            print(f"      运营利润率: {report['operating_margin']}%" if report['operating_margin'] else "      运营利润率: N/A")
    
    print("\n" + "="*60)
    print("测试完成!")
    print("="*60)
