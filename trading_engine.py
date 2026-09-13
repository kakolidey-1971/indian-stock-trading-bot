import logging
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from config import TRADING_SYMBOL, STRATEGIES
from data_fetcher import DataFetcher

logger = logging.getLogger(__name__)

class TradingEngine:
    def __init__(self, symbol: str) -> None:
        if not symbol:
            raise ValueError("Symbol cannot be empty")
        
        self.symbol = symbol
        self.strategies = []
        self.position: Optional[str] = None
        self.entry_price: float = 0.0
        self.trade_history: List[Dict] = []
        self.data_fetcher = DataFetcher()
    
    def analyze_all_strategies(self, df: pd.DataFrame) -> Dict:
        if df is None or df.empty:
            return {'signal': 'HOLD', 'buy_votes': 0, 'sell_votes': 0, 'individual_signals': {}}
        
        signals = {}
        buy_count = 0
        sell_count = 0
        
        try:
            # MA Crossover
            if len(df) >= 50:
                ma20 = df['close'].rolling(window=20).mean()
                ma50 = df['close'].rolling(window=50).mean()
                if len(ma20) > 1 and len(ma50) > 1:
                    if ma20.iloc[-2] <= ma50.iloc[-2] and ma20.iloc[-1] > ma50.iloc[-1]:
                        signals['MA Crossover'] = {'signal': 'BUY', 'confidence': 0.7}
                        buy_count += 1
                    elif ma20.iloc[-2] >= ma50.iloc[-2] and ma20.iloc[-1] < ma50.iloc[-1]:
                        signals['MA Crossover'] = {'signal': 'SELL', 'confidence': 0.7}
                        sell_count += 1
                    else:
                        signals['MA Crossover'] = {'signal': 'HOLD', 'confidence': 0.0}
            
            # RSI
            if len(df) >= 14:
                delta = df['close'].diff()
                gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]
                
                if current_rsi < 30:
                    signals['RSI'] = {'signal': 'BUY', 'confidence': 0.6}
                    buy_count += 1
                elif current_rsi > 70:
                    signals['RSI'] = {'signal': 'SELL', 'confidence': 0.6}
                    sell_count += 1
                else:
                    signals['RSI'] = {'signal': 'HOLD', 'confidence': 0.0}
            
            # Bollinger Bands
            if len(df) >= 20:
                sma = df['close'].rolling(window=20).mean()
                std = df['close'].rolling(window=20).std()
                upper = sma + (std * 2)
                lower = sma - (std * 2)
                
                current_price = df['close'].iloc[-1]
                if current_price <= lower.iloc[-1]:
                    signals['Bollinger Bands'] = {'signal': 'BUY', 'confidence': 0.6}
                    buy_count += 1
                elif current_price >= upper.iloc[-1]:
                    signals['Bollinger Bands'] = {'signal': 'SELL', 'confidence': 0.6}
                    sell_count += 1
                else:
                    signals['Bollinger Bands'] = {'signal': 'HOLD', 'confidence': 0.0}
            
            # MACD
            if len(df) >= 26:
                ema12 = df['close'].ewm(span=12).mean()
                ema26 = df['close'].ewm(span=26).mean()
                macd = ema12 - ema26
                signal_line = macd.ewm(span=9).mean()
                
                if len(macd) > 1 and len(signal_line) > 1:
                    if macd.iloc[-2] <= signal_line.iloc[-2] and macd.iloc[-1] > signal_line.iloc[-1]:
                        signals['MACD'] = {'signal': 'BUY', 'confidence': 0.7}
                        buy_count += 1
                    elif macd.iloc[-2] >= signal_line.iloc[-2] and macd.iloc[-1] < signal_line.iloc[-1]:
                        signals['MACD'] = {'signal': 'SELL', 'confidence': 0.7}
                        sell_count += 1
                    else:
                        signals['MACD'] = {'signal': 'HOLD', 'confidence': 0.0}
            
            if buy_count > sell_count:
                final_signal = 'BUY'
            elif sell_count > buy_count:
                final_signal = 'SELL'
            else:
                final_signal = 'HOLD'
            
            return {
                'signal': final_signal,
                'buy_votes': buy_count,
                'sell_votes': sell_count,
                'individual_signals': signals
            }
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return {'signal': 'HOLD', 'buy_votes': 0, 'sell_votes': 0, 'individual_signals': signals}
    
    def run_backtest(self, df: pd.DataFrame, quantity: int = 1, initial_capital: float = 100000.0) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()
        
        results = []
        position = None
        entry_price = 0.0
        
        try:
            for i in range(len(df)):
                window = df.iloc[:i+1]
                analysis = self.analyze_all_strategies(window)
                signal = analysis['signal']
                current_price = window['close'].iloc[-1]
                
                if signal == 'BUY' and position is None:
                    position = 'LONG'
                    entry_price = current_price
                    results.append({'action': 'BUY', 'price': current_price, 'pnl': 0})
                
                elif signal == 'SELL' and position == 'LONG':
                    pnl = (current_price - entry_price) * quantity
                    position = None
                    results.append({'action': 'SELL', 'price': current_price, 'pnl': pnl})
            
            return pd.DataFrame(results)
        except Exception as e:
            logger.error(f"Backtest error: {str(e)}")
            return pd.DataFrame(results) if results else pd.DataFrame()
    
    def get_trade_statistics(self) -> Dict:
        if not self.trade_history:
            return {'total_trades': 0, 'win_rate': 0.0, 'total_pnl': 0.0}
        
        try:
            buy_trades = [t for t in self.trade_history if t['signal'] == 'BUY']
            sell_trades = [t for t in self.trade_history if t['signal'] == 'SELL']
            total_trades = min(len(buy_trades), len(sell_trades))
            
            pnls = [(sell_trades[i]['price'] - buy_trades[i]['price']) for i in range(total_trades)]
            winning = len([p for p in pnls if p > 0])
            win_rate = (winning / len(pnls) * 100) if pnls else 0.0
            total_pnl = sum(pnls)
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning,
                'win_rate': win_rate,
                'total_pnl': total_pnl
            }
        except Exception as e:
            logger.error(f"Stats error: {str(e)}")
            return {}
