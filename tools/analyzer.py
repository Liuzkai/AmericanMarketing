#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
美股量化分析系统 - 分析工具模块

本模块提供:
- TechnicalAnalyzer: 技术指标计算与信号生成
- SentimentAnalyzer: 新闻情感分析

依赖库:
- ta: 技术分析库 (GitHub 上最成熟的技术分析库)
- textblob: 基础 NLP 情感分析
- pandas: 数据处理
"""

import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

import pandas as pd
import numpy as np

# 技术分析库
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands

# 情感分析库
from textblob import TextBlob

# 配置日志
logger = logging.getLogger(__name__)


# ==================== 信号枚举 ====================

class TechnicalSignal(Enum):
    """技术分析信号枚举"""
    # RSI 信号
    RSI_OVERBOUGHT = "RSI_Overbought"          # RSI > 70，超买
    RSI_OVERSOLD = "RSI_Oversold"              # RSI < 30，超卖
    RSI_NEUTRAL = "RSI_Neutral"                # 30 <= RSI <= 70，中性
    
    # 均线交叉信号
    GOLDEN_CROSS = "Golden_Cross"              # MA50 上穿 MA200，黄金交叉
    DEATH_CROSS = "Death_Cross"                # MA50 下穿 MA200，死亡交叉
    
    # MACD 信号
    MACD_BULLISH = "MACD_Bullish"              # MACD 金叉
    MACD_BEARISH = "MACD_Bearish"              # MACD 死叉
    
    # 布林带信号
    BB_UPPER_BREAK = "BB_Upper_Break"          # 价格突破布林带上轨
    BB_LOWER_BREAK = "BB_Lower_Break"          # 价格跌破布林带下轨
    BB_SQUEEZE = "BB_Squeeze"                  # 布林带收窄
    
    # 综合信号
    STRONG_BUY = "Strong_Buy"                  # 强烈买入
    BUY = "Buy"                                # 买入
    NEUTRAL = "Neutral"                        # 中性
    SELL = "Sell"                              # 卖出
    STRONG_SELL = "Strong_Sell"                # 强烈卖出


class SentimentLevel(Enum):
    """情感级别枚举"""
    VERY_POSITIVE = "Very_Positive"    # 非常积极 (> 0.5)
    POSITIVE = "Positive"              # 积极 (0.1 ~ 0.5)
    NEUTRAL = "Neutral"                # 中性 (-0.1 ~ 0.1)
    NEGATIVE = "Negative"              # 消极 (-0.5 ~ -0.1)
    VERY_NEGATIVE = "Very_Negative"    # 非常消极 (< -0.5)


# ==================== 数据类 ====================

@dataclass
class TechnicalIndicators:
    """技术指标数据类"""
    # RSI
    rsi: Optional[float] = None
    rsi_signal: Optional[str] = None
    
    # MACD
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    macd_trend: Optional[str] = None
    
    # 布林带
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_width: Optional[float] = None
    bb_signal: Optional[str] = None
    
    # 均线
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ma_signal: Optional[str] = None
    
    # 当前价格
    current_price: Optional[float] = None
    
    # 综合信号
    signals: List[str] = None
    overall_signal: Optional[str] = None
    
    def __post_init__(self):
        if self.signals is None:
            self.signals = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'rsi': self.rsi,
            'rsi_signal': self.rsi_signal,
            'macd': self.macd,
            'macd_signal': self.macd_signal,
            'macd_histogram': self.macd_histogram,
            'macd_trend': self.macd_trend,
            'bb_upper': self.bb_upper,
            'bb_middle': self.bb_middle,
            'bb_lower': self.bb_lower,
            'bb_width': self.bb_width,
            'bb_signal': self.bb_signal,
            'sma_50': self.sma_50,
            'sma_200': self.sma_200,
            'ma_signal': self.ma_signal,
            'current_price': self.current_price,
            'signals': self.signals,
            'overall_signal': self.overall_signal
        }


@dataclass
class SentimentResult:
    """情感分析结果数据类"""
    text: str
    polarity: float          # 极性 (-1 到 1)
    subjectivity: float      # 主观性 (0 到 1)
    sentiment_level: str     # 情感级别
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'text': self.text,
            'polarity': self.polarity,
            'subjectivity': self.subjectivity,
            'sentiment_level': self.sentiment_level
        }


# ==================== TechnicalAnalyzer 类 ====================

class TechnicalAnalyzer:
    """
    技术指标分析器
    
    使用 ta 库计算各种技术指标并生成交易信号
    
    支持的指标:
    - RSI (相对强弱指数)
    - MACD (移动平均收敛/发散)
    - Bollinger Bands (布林带)
    - SMA (简单移动平均)
    
    示例:
        analyzer = TechnicalAnalyzer()
        indicators = analyzer.analyze(df)
        print(indicators.signals)
    """
    
    # RSI 阈值
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    
    # RSI 默认周期
    RSI_PERIOD = 14
    
    # MACD 默认参数
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    # 布林带默认参数
    BB_PERIOD = 20
    BB_STD = 2
    
    # 均线周期
    SMA_SHORT = 50
    SMA_LONG = 200
    
    def __init__(self, log_level: int = logging.INFO):
        """
        初始化技术分析器
        
        Args:
            log_level: 日志级别
        """
        logging.basicConfig(level=log_level)
        logger.info("TechnicalAnalyzer 初始化完成")
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = None) -> pd.Series:
        """
        计算 RSI (相对强弱指数)
        
        Args:
            df: 包含 'Close' 列的 DataFrame
            period: RSI 周期，默认 14
            
        Returns:
            RSI 值的 Series
        """
        period = period or self.RSI_PERIOD
        
        try:
            close = df['Close']
            rsi_indicator = RSIIndicator(close=close, window=period)
            return rsi_indicator.rsi()
        except Exception as e:
            logger.error(f"计算 RSI 失败: {e}")
            return pd.Series([np.nan] * len(df), index=df.index)
    
    def calculate_macd(self, df: pd.DataFrame, 
                       fast: int = None, 
                       slow: int = None, 
                       signal: int = None) -> Dict[str, pd.Series]:
        """
        计算 MACD (移动平均收敛/发散)
        
        Args:
            df: 包含 'Close' 列的 DataFrame
            fast: 快线周期，默认 12
            slow: 慢线周期，默认 26
            signal: 信号线周期，默认 9
            
        Returns:
            包含 macd, signal, histogram 的字典
        """
        fast = fast or self.MACD_FAST
        slow = slow or self.MACD_SLOW
        signal = signal or self.MACD_SIGNAL
        
        try:
            close = df['Close']
            macd_indicator = MACD(close=close, 
                                  window_fast=fast, 
                                  window_slow=slow, 
                                  window_sign=signal)
            
            return {
                'macd': macd_indicator.macd(),
                'signal': macd_indicator.macd_signal(),
                'histogram': macd_indicator.macd_diff()
            }
        except Exception as e:
            logger.error(f"计算 MACD 失败: {e}")
            empty = pd.Series([np.nan] * len(df), index=df.index)
            return {'macd': empty, 'signal': empty, 'histogram': empty}
    
    def calculate_bollinger_bands(self, df: pd.DataFrame,
                                   period: int = None,
                                   std: int = None) -> Dict[str, pd.Series]:
        """
        计算布林带
        
        Args:
            df: 包含 'Close' 列的 DataFrame
            period: 周期，默认 20
            std: 标准差倍数，默认 2
            
        Returns:
            包含 upper, middle, lower, width 的字典
        """
        period = period or self.BB_PERIOD
        std = std or self.BB_STD
        
        try:
            close = df['Close']
            bb = BollingerBands(close=close, window=period, window_dev=std)
            
            upper = bb.bollinger_hband()
            lower = bb.bollinger_lband()
            middle = bb.bollinger_mavg()
            
            # 计算布林带宽度 (归一化)
            width = (upper - lower) / middle * 100
            
            return {
                'upper': upper,
                'middle': middle,
                'lower': lower,
                'width': width
            }
        except Exception as e:
            logger.error(f"计算布林带失败: {e}")
            empty = pd.Series([np.nan] * len(df), index=df.index)
            return {'upper': empty, 'middle': empty, 'lower': empty, 'width': empty}
    
    def calculate_sma(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        计算简单移动平均线
        
        Args:
            df: 包含 'Close' 列的 DataFrame
            period: 周期
            
        Returns:
            SMA 值的 Series
        """
        try:
            close = df['Close']
            sma = SMAIndicator(close=close, window=period)
            return sma.sma_indicator()
        except Exception as e:
            logger.error(f"计算 SMA{period} 失败: {e}")
            return pd.Series([np.nan] * len(df), index=df.index)
    
    def _get_rsi_signal(self, rsi: float) -> str:
        """根据 RSI 值获取信号"""
        if pd.isna(rsi):
            return TechnicalSignal.RSI_NEUTRAL.value
        if rsi > self.RSI_OVERBOUGHT:
            return TechnicalSignal.RSI_OVERBOUGHT.value
        elif rsi < self.RSI_OVERSOLD:
            return TechnicalSignal.RSI_OVERSOLD.value
        return TechnicalSignal.RSI_NEUTRAL.value
    
    def _get_macd_signal(self, macd: float, signal: float, 
                         prev_macd: float, prev_signal: float) -> str:
        """根据 MACD 获取信号"""
        if pd.isna(macd) or pd.isna(signal):
            return TechnicalSignal.NEUTRAL.value
        
        # 判断金叉/死叉
        if prev_macd <= prev_signal and macd > signal:
            return TechnicalSignal.MACD_BULLISH.value
        elif prev_macd >= prev_signal and macd < signal:
            return TechnicalSignal.MACD_BEARISH.value
        elif macd > signal:
            return TechnicalSignal.MACD_BULLISH.value
        else:
            return TechnicalSignal.MACD_BEARISH.value
    
    def _get_bb_signal(self, price: float, upper: float, 
                       lower: float, width: float) -> str:
        """根据布林带获取信号"""
        if pd.isna(price) or pd.isna(upper) or pd.isna(lower):
            return TechnicalSignal.NEUTRAL.value
        
        if price > upper:
            return TechnicalSignal.BB_UPPER_BREAK.value
        elif price < lower:
            return TechnicalSignal.BB_LOWER_BREAK.value
        elif width < 5:  # 布林带收窄阈值
            return TechnicalSignal.BB_SQUEEZE.value
        return TechnicalSignal.NEUTRAL.value
    
    def _get_ma_signal(self, sma_50: float, sma_200: float,
                       prev_sma_50: float, prev_sma_200: float) -> str:
        """根据均线获取信号 (黄金交叉/死亡交叉)"""
        if pd.isna(sma_50) or pd.isna(sma_200):
            return TechnicalSignal.NEUTRAL.value
        
        # 判断黄金交叉/死亡交叉
        if prev_sma_50 <= prev_sma_200 and sma_50 > sma_200:
            return TechnicalSignal.GOLDEN_CROSS.value
        elif prev_sma_50 >= prev_sma_200 and sma_50 < sma_200:
            return TechnicalSignal.DEATH_CROSS.value
        elif sma_50 > sma_200:
            return TechnicalSignal.GOLDEN_CROSS.value
        else:
            return TechnicalSignal.DEATH_CROSS.value
    
    def _calculate_overall_signal(self, signals: List[str]) -> str:
        """
        计算综合信号
        
        根据各个信号综合判断整体趋势
        """
        bullish_signals = [
            TechnicalSignal.RSI_OVERSOLD.value,
            TechnicalSignal.GOLDEN_CROSS.value,
            TechnicalSignal.MACD_BULLISH.value,
            TechnicalSignal.BB_LOWER_BREAK.value
        ]
        
        bearish_signals = [
            TechnicalSignal.RSI_OVERBOUGHT.value,
            TechnicalSignal.DEATH_CROSS.value,
            TechnicalSignal.MACD_BEARISH.value,
            TechnicalSignal.BB_UPPER_BREAK.value
        ]
        
        bullish_count = sum(1 for s in signals if s in bullish_signals)
        bearish_count = sum(1 for s in signals if s in bearish_signals)
        
        score = bullish_count - bearish_count
        
        if score >= 3:
            return TechnicalSignal.STRONG_BUY.value
        elif score >= 1:
            return TechnicalSignal.BUY.value
        elif score <= -3:
            return TechnicalSignal.STRONG_SELL.value
        elif score <= -1:
            return TechnicalSignal.SELL.value
        else:
            return TechnicalSignal.NEUTRAL.value
    
    def analyze(self, df: pd.DataFrame) -> TechnicalIndicators:
        """
        对价格数据进行完整的技术分析
        
        Args:
            df: 包含 OHLCV 数据的 DataFrame (至少需要 'Close' 列)
            
        Returns:
            TechnicalIndicators 对象，包含所有指标和信号
        """
        result = TechnicalIndicators()
        
        if df.empty or 'Close' not in df.columns:
            logger.warning("数据为空或缺少 Close 列")
            return result
        
        # 确保有足够的数据
        min_periods = max(self.SMA_LONG, self.MACD_SLOW + self.MACD_SIGNAL)
        if len(df) < min_periods:
            logger.warning(f"数据量不足 ({len(df)} < {min_periods})，部分指标可能无法计算")
        
        try:
            # 当前价格
            result.current_price = float(df['Close'].iloc[-1])
            
            # 计算 RSI
            rsi_series = self.calculate_rsi(df)
            result.rsi = float(rsi_series.iloc[-1]) if not rsi_series.isna().all() else None
            result.rsi_signal = self._get_rsi_signal(result.rsi)
            
            # 计算 MACD
            macd_data = self.calculate_macd(df)
            if not macd_data['macd'].isna().all():
                result.macd = float(macd_data['macd'].iloc[-1])
                result.macd_signal = float(macd_data['signal'].iloc[-1])
                result.macd_histogram = float(macd_data['histogram'].iloc[-1])
                
                # 获取前一个值用于判断交叉
                prev_macd = float(macd_data['macd'].iloc[-2]) if len(df) > 1 else result.macd
                prev_signal = float(macd_data['signal'].iloc[-2]) if len(df) > 1 else result.macd_signal
                result.macd_trend = self._get_macd_signal(
                    result.macd, result.macd_signal, prev_macd, prev_signal
                )
            
            # 计算布林带
            bb_data = self.calculate_bollinger_bands(df)
            if not bb_data['upper'].isna().all():
                result.bb_upper = float(bb_data['upper'].iloc[-1])
                result.bb_middle = float(bb_data['middle'].iloc[-1])
                result.bb_lower = float(bb_data['lower'].iloc[-1])
                result.bb_width = float(bb_data['width'].iloc[-1])
                result.bb_signal = self._get_bb_signal(
                    result.current_price, result.bb_upper, 
                    result.bb_lower, result.bb_width
                )
            
            # 计算均线
            sma_50_series = self.calculate_sma(df, self.SMA_SHORT)
            sma_200_series = self.calculate_sma(df, self.SMA_LONG)
            
            if not sma_50_series.isna().all():
                result.sma_50 = float(sma_50_series.iloc[-1])
            if not sma_200_series.isna().all():
                result.sma_200 = float(sma_200_series.iloc[-1])
            
            if result.sma_50 and result.sma_200:
                prev_sma_50 = float(sma_50_series.iloc[-2]) if len(df) > 1 else result.sma_50
                prev_sma_200 = float(sma_200_series.iloc[-2]) if len(df) > 1 else result.sma_200
                result.ma_signal = self._get_ma_signal(
                    result.sma_50, result.sma_200, prev_sma_50, prev_sma_200
                )
            
            # 汇总所有信号
            signals = []
            if result.rsi_signal and result.rsi_signal != TechnicalSignal.RSI_NEUTRAL.value:
                signals.append(result.rsi_signal)
            if result.macd_trend:
                signals.append(result.macd_trend)
            if result.bb_signal and result.bb_signal != TechnicalSignal.NEUTRAL.value:
                signals.append(result.bb_signal)
            if result.ma_signal:
                signals.append(result.ma_signal)
            
            result.signals = signals
            result.overall_signal = self._calculate_overall_signal(signals)
            
            logger.info(f"技术分析完成，综合信号: {result.overall_signal}")
            return result
            
        except Exception as e:
            logger.error(f"技术分析失败: {e}")
            return result


# ==================== SentimentAnalyzer 类 ====================

class SentimentAnalyzer:
    """
    情感分析器
    
    使用 TextBlob 对英文文本进行情感分析
    
    功能:
    - 对单条文本进行情感打分
    - 批量分析多条文本
    - 计算平均情感得分
    
    示例:
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_text("Apple stock soars to new highs!")
        print(f"极性: {result.polarity}, 级别: {result.sentiment_level}")
    """
    
    # 情感阈值
    VERY_POSITIVE_THRESHOLD = 0.5
    POSITIVE_THRESHOLD = 0.1
    NEGATIVE_THRESHOLD = -0.1
    VERY_NEGATIVE_THRESHOLD = -0.5
    
    def __init__(self, log_level: int = logging.INFO):
        """
        初始化情感分析器
        
        Args:
            log_level: 日志级别
        """
        logging.basicConfig(level=log_level)
        logger.info("SentimentAnalyzer 初始化完成")
    
    def _get_sentiment_level(self, polarity: float) -> str:
        """根据极性值获取情感级别"""
        if polarity > self.VERY_POSITIVE_THRESHOLD:
            return SentimentLevel.VERY_POSITIVE.value
        elif polarity > self.POSITIVE_THRESHOLD:
            return SentimentLevel.POSITIVE.value
        elif polarity < self.VERY_NEGATIVE_THRESHOLD:
            return SentimentLevel.VERY_NEGATIVE.value
        elif polarity < self.NEGATIVE_THRESHOLD:
            return SentimentLevel.NEGATIVE.value
        else:
            return SentimentLevel.NEUTRAL.value
    
    def analyze_text(self, text: str) -> SentimentResult:
        """
        分析单条文本的情感
        
        Args:
            text: 英文文本
            
        Returns:
            SentimentResult 对象
        """
        try:
            # 清理文本
            cleaned_text = text.strip()
            if not cleaned_text:
                return SentimentResult(
                    text=text,
                    polarity=0.0,
                    subjectivity=0.0,
                    sentiment_level=SentimentLevel.NEUTRAL.value
                )
            
            # 使用 TextBlob 分析
            blob = TextBlob(cleaned_text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            sentiment_level = self._get_sentiment_level(polarity)
            
            return SentimentResult(
                text=text,
                polarity=round(polarity, 4),
                subjectivity=round(subjectivity, 4),
                sentiment_level=sentiment_level
            )
            
        except Exception as e:
            logger.error(f"分析文本情感失败: {e}")
            return SentimentResult(
                text=text,
                polarity=0.0,
                subjectivity=0.0,
                sentiment_level=SentimentLevel.NEUTRAL.value
            )
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """
        批量分析多条文本的情感
        
        Args:
            texts: 英文文本列表
            
        Returns:
            SentimentResult 对象列表
        """
        results = []
        for text in texts:
            result = self.analyze_text(text)
            results.append(result)
        
        logger.info(f"批量分析完成，共 {len(results)} 条文本")
        return results
    
    def analyze_news(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析新闻列表的情感
        
        Args:
            news_items: 新闻列表，每项包含 'title' 字段
            
        Returns:
            包含分析结果和统计信息的字典
        """
        if not news_items:
            return {
                'results': [],
                'average_polarity': 0.0,
                'average_subjectivity': 0.0,
                'sentiment_distribution': {},
                'overall_sentiment': SentimentLevel.NEUTRAL.value
            }
        
        # 提取标题并分析
        titles = [item.get('title', '') for item in news_items if item.get('title')]
        results = self.analyze_batch(titles)
        
        # 计算统计信息
        polarities = [r.polarity for r in results]
        subjectivities = [r.subjectivity for r in results]
        
        avg_polarity = sum(polarities) / len(polarities) if polarities else 0.0
        avg_subjectivity = sum(subjectivities) / len(subjectivities) if subjectivities else 0.0
        
        # 情感分布
        distribution = {}
        for result in results:
            level = result.sentiment_level
            distribution[level] = distribution.get(level, 0) + 1
        
        # 整体情感
        overall = self._get_sentiment_level(avg_polarity)
        
        logger.info(f"新闻情感分析完成，平均极性: {avg_polarity:.4f}, 整体情感: {overall}")
        
        return {
            'results': [r.to_dict() for r in results],
            'average_polarity': round(avg_polarity, 4),
            'average_subjectivity': round(avg_subjectivity, 4),
            'sentiment_distribution': distribution,
            'overall_sentiment': overall
        }
    
    def get_sentiment_score(self, texts: List[str]) -> float:
        """
        计算文本列表的平均情感得分
        
        Args:
            texts: 英文文本列表
            
        Returns:
            平均情感得分 (-1 到 1)
        """
        if not texts:
            return 0.0
        
        results = self.analyze_batch(texts)
        polarities = [r.polarity for r in results]
        
        return round(sum(polarities) / len(polarities), 4) if polarities else 0.0


# ==================== 测试代码 ====================

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "=" * 70)
    print("美股量化分析系统 - 分析工具测试")
    print("=" * 70)
    
    # ========== 测试 SentimentAnalyzer ==========
    print("\n" + "-" * 70)
    print("1. SentimentAnalyzer 情感分析测试")
    print("-" * 70)
    
    sentiment_analyzer = SentimentAnalyzer()
    
    # 测试新闻标题
    test_headlines = [
        "Apple stock soars to all-time high on strong iPhone sales",
        "Tesla faces challenges as competition intensifies in EV market",
        "NVIDIA reports record revenue, beats analyst expectations",
        "Tech stocks tumble amid fears of economic recession",
        "Microsoft announces major AI partnership, shares jump 5%",
        "Market uncertainty grows as Fed signals potential rate hikes",
        "Amazon's cloud business shows strong growth momentum",
        "Cryptocurrency crash sparks concerns about tech valuations"
    ]
    
    print("\n--- 新闻标题情感分析 ---\n")
    
    news_items = [{'title': h} for h in test_headlines]
    sentiment_results = sentiment_analyzer.analyze_news(news_items)
    
    for i, result in enumerate(sentiment_results['results'], 1):
        title = result['text'][:55] + '...' if len(result['text']) > 55 else result['text']
        print(f"[{i}] {title}")
        print(f"    极性: {result['polarity']:+.4f} | 主观性: {result['subjectivity']:.4f} | 级别: {result['sentiment_level']}")
    
    print(f"\n--- 情感统计 ---")
    print(f"平均极性: {sentiment_results['average_polarity']:+.4f}")
    print(f"平均主观性: {sentiment_results['average_subjectivity']:.4f}")
    print(f"整体情感: {sentiment_results['overall_sentiment']}")
    print(f"情感分布: {sentiment_results['sentiment_distribution']}")
    
    # ========== 测试 TechnicalAnalyzer ==========
    print("\n" + "-" * 70)
    print("2. TechnicalAnalyzer 技术指标测试")
    print("-" * 70)
    
    tech_analyzer = TechnicalAnalyzer()
    
    # 生成模拟数据 (250 个交易日)
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=250, freq='D')
    
    # 模拟价格走势 (带趋势和波动)
    base_price = 150
    returns = np.random.normal(0.001, 0.02, 250)  # 日收益率
    prices = base_price * np.cumprod(1 + returns)
    
    # 创建 OHLCV DataFrame
    test_df = pd.DataFrame({
        'Open': prices * (1 + np.random.uniform(-0.01, 0.01, 250)),
        'High': prices * (1 + np.random.uniform(0, 0.02, 250)),
        'Low': prices * (1 - np.random.uniform(0, 0.02, 250)),
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, 250)
    }, index=dates)
    
    print(f"\n模拟数据: {len(test_df)} 个交易日")
    print(f"价格范围: ${test_df['Close'].min():.2f} - ${test_df['Close'].max():.2f}")
    
    # 执行技术分析
    indicators = tech_analyzer.analyze(test_df)
    
    print(f"\n--- 技术指标 ---")
    print(f"当前价格: ${indicators.current_price:.2f}" if indicators.current_price else "当前价格: N/A")
    print(f"RSI: {indicators.rsi:.2f} ({indicators.rsi_signal})" if indicators.rsi else "RSI: N/A")
    print(f"MACD: {indicators.macd:.4f}" if indicators.macd else "MACD: N/A")
    print(f"MACD Signal: {indicators.macd_signal:.4f}" if indicators.macd_signal else "MACD Signal: N/A")
    print(f"MACD Histogram: {indicators.macd_histogram:.4f}" if indicators.macd_histogram else "MACD Histogram: N/A")
    print(f"MACD 趋势: {indicators.macd_trend}" if indicators.macd_trend else "MACD 趋势: N/A")
    print(f"布林带上轨: ${indicators.bb_upper:.2f}" if indicators.bb_upper else "布林带上轨: N/A")
    print(f"布林带中轨: ${indicators.bb_middle:.2f}" if indicators.bb_middle else "布林带中轨: N/A")
    print(f"布林带下轨: ${indicators.bb_lower:.2f}" if indicators.bb_lower else "布林带下轨: N/A")
    print(f"布林带宽度: {indicators.bb_width:.2f}%" if indicators.bb_width else "布林带宽度: N/A")
    print(f"布林带信号: {indicators.bb_signal}" if indicators.bb_signal else "布林带信号: N/A")
    print(f"SMA 50: ${indicators.sma_50:.2f}" if indicators.sma_50 else "SMA 50: N/A")
    print(f"SMA 200: ${indicators.sma_200:.2f}" if indicators.sma_200 else "SMA 200: N/A")
    print(f"均线信号: {indicators.ma_signal}" if indicators.ma_signal else "均线信号: N/A")
    
    print(f"\n--- 信号汇总 ---")
    print(f"活跃信号: {indicators.signals}")
    print(f"综合信号: {indicators.overall_signal}")
    
    print("\n" + "=" * 70)
    print("测试完成!")
    print("=" * 70)
