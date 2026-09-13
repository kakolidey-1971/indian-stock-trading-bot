import yfinance as yf
import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DataFetcher:
    @staticmethod
    def get_historical_data(symbol: str, period: str = '1mo', interval: str = '5m') -> pd.DataFrame:
        try:
            ticker = f"{symbol}.NS" if not symbol.endswith('.NS') else symbol
            data = yf.download(ticker, period=period, interval=interval, progress=False, timeout=10)
            
            if data.empty:
                return pd.DataFrame()
            
            data.columns = ['open', 'high', 'low', 'close', 'adj_close', 'volume']
            data = data.reset_index()
            
            if 'Date' in data.columns:
                data['timestamp'] = pd.to_datetime(data['Date'])
                data = data.drop('Date', axis=1)
            elif 'Datetime' in data.columns:
                data['timestamp'] = pd.to_datetime(data['Datetime'])
                data = data.drop('Datetime', axis=1)
            
            numeric_cols = ['open', 'high', 'low', 'close', 'adj_close', 'volume']
            for col in numeric_cols:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
            
            return data
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def get_intraday_data(symbol: str, interval: str = '5m', days: int = 1) -> pd.DataFrame:
        try:
            ticker = f"{symbol}.NS" if not symbol.endswith('.NS') else symbol
            data = yf.download(ticker, period=f"{days}d", interval=interval, progress=False, timeout=10)
            
            if data.empty:
                return pd.DataFrame()
            
            data.columns = ['open', 'high', 'low', 'close', 'adj_close', 'volume']
            data = data.reset_index()
            
            if 'Date' in data.columns:
                data['timestamp'] = pd.to_datetime(data['Date'])
                data = data.drop('Date', axis=1)
            elif 'Datetime' in data.columns:
                data['timestamp'] = pd.to_datetime(data['Datetime'])
                data = data.drop('Datetime', axis=1)
            
            numeric_cols = ['open', 'high', 'low', 'close', 'adj_close', 'volume']
            for col in numeric_cols:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
            
            return data
        except Exception as e:
            logger.error(f"Error fetching intraday data: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def get_latest_price(symbol: str) -> Optional[float]:
        try:
            ticker = f"{symbol}.NS" if not symbol.endswith('.NS') else symbol
            data = yf.download(ticker, period='1d', progress=False, timeout=10)
            return float(data['Close'].iloc[-1]) if not data.empty else None
        except Exception as e:
            logger.error(f"Error fetching price: {str(e)}")
            return None
