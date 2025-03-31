"""
Financial Analysis Module

This module provides financial data analysis, visualization, and optional
trading capabilities for the Open Manus AI system.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta
import os
import json

# Configure logging
logger = logging.getLogger(__name__)

class FinancialAnalysisModule:
    """
    Financial Analysis Module for analyzing financial data and markets.
    """
    
    def __init__(self):
        """Initialize the Financial Analysis Module."""
        self.data_cache = {}
        logger.info("Financial Analysis Module initialized")
    
    def get_stock_data(self, symbol, period="1mo", interval="1d"):
        """
        Retrieve stock data for a given symbol.
        
        Args:
            symbol (str): Stock ticker symbol
            period (str, optional): Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval (str, optional): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            dict: Stock data and metadata
        """
        try:
            # Check cache first
            cache_key = f"{symbol}_{period}_{interval}"
            if cache_key in self.data_cache:
                cache_time, data = self.data_cache[cache_key]
                # Use cache if less than 1 hour old
                if datetime.now() - cache_time < timedelta(hours=1):
                    logger.info(f"Using cached data for {symbol}")
                    return data
            
            # Fetch data from yfinance
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period, interval=interval)
            
            # Get company info
            try:
                info = ticker.info
                company_name = info.get('longName', symbol)
                sector = info.get('sector', 'Unknown')
                industry = info.get('industry', 'Unknown')
                market_cap = info.get('marketCap', 0)
                
                # Format market cap
                if market_cap >= 1_000_000_000_000:
                    market_cap_str = f"${market_cap / 1_000_000_000_000:.2f}T"
                elif market_cap >= 1_000_000_000:
                    market_cap_str = f"${market_cap / 1_000_000_000:.2f}B"
                elif market_cap >= 1_000_000:
                    market_cap_str = f"${market_cap / 1_000_000:.2f}M"
                else:
                    market_cap_str = f"${market_cap:,.2f}"
                
            except Exception as e:
                logger.warning(f"Could not retrieve company info for {symbol}: {e}")
                company_name = symbol
                sector = "Unknown"
                industry = "Unknown"
                market_cap_str = "Unknown"
            
            # Convert to dict for easier serialization
            df = history.reset_index()
            data_dict = df.to_dict(orient='records')
            
            # Calculate basic statistics
            if not df.empty:
                latest_price = df['Close'].iloc[-1]
                price_change = df['Close'].iloc[-1] - df['Close'].iloc[0]
                price_change_pct = (price_change / df['Close'].iloc[0]) * 100
                avg_volume = df['Volume'].mean()
                
                stats = {
                    'latest_price': latest_price,
                    'price_change': price_change,
                    'price_change_pct': price_change_pct,
                    'avg_volume': avg_volume
                }
            else:
                stats = {
                    'latest_price': None,
                    'price_change': None,
                    'price_change_pct': None,
                    'avg_volume': None
                }
            
            result = {
                'symbol': symbol,
                'company_name': company_name,
                'sector': sector,
                'industry': industry,
                'market_cap': market_cap_str,
                'period': period,
                'interval': interval,
                'data': data_dict,
                'stats': stats,
                'success': True
            }
            
            # Update cache
            self.data_cache[cache_key] = (datetime.now(), result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving stock data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'success': False
            }
    
    def generate_stock_chart(self, symbol, period="1mo", chart_type="line", output_dir=None):
        """
        Generate a stock chart and save it to a file.
        
        Args:
            symbol (str): Stock ticker symbol
            period (str, optional): Time period
            chart_type (str, optional): Chart type (line, candle)
            output_dir (str, optional): Directory to save the chart
            
        Returns:
            dict: Chart information including file path
        """
        try:
            # Get stock data
            stock_data = self.get_stock_data(symbol, period=period)
            
            if not stock_data['success']:
                return {
                    'success': False,
                    'error': stock_data.get('error', 'Failed to retrieve stock data')
                }
            
            # Convert data to DataFrame
            df = pd.DataFrame(stock_data['data'])
            
            # Set up the figure
            plt.figure(figsize=(12, 6))
            
            if chart_type.lower() == 'candle':
                # Create candlestick chart
                from mplfinance.original_flavor import candlestick_ohlc
                import matplotlib.dates as mpdates
                
                # Convert date to matplotlib format
                df['Date'] = pd.to_datetime(df['Date'])
                df['Date'] = df['Date'].map(mpdates.date2num)
                
                # Create OHLC data
                ohlc = df[['Date', 'Open', 'High', 'Low', 'Close']]
                
                # Plot candlestick chart
                ax = plt.subplot()
                candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='green', colordown='red')
                ax.xaxis.set_major_formatter(mpdates.DateFormatter('%Y-%m-%d'))
                
            else:  # Default to line chart
                plt.plot(df['Date'], df['Close'], label='Close Price')
                plt.fill_between(df['Date'], df['Close'], alpha=0.2)
            
            # Add chart details
            plt.title(f"{stock_data['company_name']} ({symbol}) - {period}")
            plt.xlabel('Date')
            plt.ylabel('Price ($)')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            
            # Save the chart
            if output_dir is None:
                output_dir = os.path.expanduser("~")
            
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{symbol}_{period}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)
            
            plt.savefig(filepath)
            plt.close()
            
            return {
                'success': True,
                'symbol': symbol,
                'company_name': stock_data['company_name'],
                'period': period,
                'chart_type': chart_type,
                'filepath': filepath
            }
            
        except Exception as e:
            logger.error(f"Error generating stock chart for {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_stock(self, symbol):
        """
        Perform comprehensive analysis of a stock.
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: Analysis results
        """
        try:
            # Get stock data for different time periods
            data_1d = self.get_stock_data(symbol, period="1d", interval="5m")
            data_1mo = self.get_stock_data(symbol, period="1mo")
            data_6mo = self.get_stock_data(symbol, period="6mo")
            data_1y = self.get_stock_data(symbol, period="1y")
            
            if not data_1mo['success']:
                return {
                    'success': False,
                    'error': data_1mo.get('error', 'Failed to retrieve stock data')
                }
            
            # Prepare data for analysis
            company_info = {
                'symbol': symbol,
                'company_name': data_1mo['company_name'],
                'sector': data_1mo['sector'],
                'industry': data_1mo['industry'],
                'market_cap': data_1mo['market_cap']
            }
            
            # Calculate performance metrics
            performance = {}
            
            if data_1d['success']:
                df_1d = pd.DataFrame(data_1d['data'])
                if not df_1d.empty:
                    performance['1d'] = {
                        'change': data_1d['stats']['price_change'],
                        'change_pct': data_1d['stats']['price_change_pct']
                    }
            
            if data_1mo['success']:
                df_1mo = pd.DataFrame(data_1mo['data'])
                if not df_1mo.empty:
                    performance['1mo'] = {
                        'change': data_1mo['stats']['price_change'],
                        'change_pct': data_1mo['stats']['price_change_pct']
                    }
            
            if data_6mo['success']:
                df_6mo = pd.DataFrame(data_6mo['data'])
                if not df_6mo.empty:
                    performance['6mo'] = {
                        'change': data_6mo['stats']['price_change'],
                        'change_pct': data_6mo['stats']['price_change_pct']
                    }
            
            if data_1y['success']:
                df_1y = pd.DataFrame(data_1y['data'])
                if not df_1y.empty:
                    performance['1y'] = {
                        'change': data_1y['stats']['price_change'],
                        'change_pct': data_1y['stats']['price_change_pct']
                    }
            
            # Calculate technical indicators (using 1-month data)
            technical_indicators = {}
            
            if data_1mo['success']:
                df = pd.DataFrame(data_1mo['data'])
                if not df.empty:
                    # Moving Averages
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    df['MA50'] = df['Close'].rolling(window=50).mean()
                    
                    # Relative Strength Index (RSI)
                    delta = df['Close'].diff()
                    gain = delta.where(delta > 0, 0)
                    loss = -delta.where(delta < 0, 0)
                    avg_gain = gain.rolling(window=14).mean()
                    avg_loss = loss.rolling(window=14).mean()
                    rs = avg_gain / avg_loss
                    df['RSI'] = 100 - (100 / (1 + rs))
                    
                    # MACD
                    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
                    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
                    df['MACD'] = df['EMA12'] - df['EMA26']
                    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
                    
                    # Get latest values
                    latest = df.iloc[-1]
                    
                    technical_indicators = {
                        'price': latest['Close'],
                        'ma20': latest['MA20'],
                        'ma50': latest['MA50'],
                        'rsi': latest['RSI'],
                        'macd': latest['MACD'],
                        'macd_signal': latest['Signal'],
                        'above_ma20': latest['Close'] > latest['MA20'],
                        'above_ma50': latest['Close'] > latest['MA50'],
                        'rsi_oversold': latest['RSI'] < 30,
                        'rsi_overbought': latest['RSI'] > 70,
                        'macd_bullish': latest['MACD'] > latest['Signal']
                    }
            
            # Compile analysis results
            analysis = {
                'company_info': company_info,
                'performance': performance,
                'technical_indicators': technical_indicators,
                'success': True
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing stock {symbol}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_market_overview(self):
        """
        Get an overview of major market indices.
        
        Returns:
            dict: Market overview data
        """
        try:
            # List of major indices to track
            indices = [
                '^GSPC',    # S&P 500
                '^DJI',     # Dow Jones Industrial Average
                '^IXIC',    # NASDAQ Composite
                '^RUT',     # Russell 2000
                '^FTSE',    # FTSE 100
                '^N225',    # Nikkei 225
                '^HSI'      # Hang Seng Index
            ]
            
            # Get data for each index
            market_data = {}
            for index in indices:
                data = self.get_stock_data(index, period="5d")
                if data['success']:
                    market_data[index] = {
                        'name': data['company_name'],
                        'latest_price': data['stats']['latest_price'],
                        'change': data['stats']['price_change'],
                        'change_pct': data['stats']['price_change_pct']
                    }
            
            return {
                'data': market_data,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {
                'success': False,
                'error': str(e)
            }
