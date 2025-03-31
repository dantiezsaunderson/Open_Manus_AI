"""
Enhanced Financial Analysis Module

This module provides advanced financial data analysis, visualization, and trading
capabilities for the Open Manus AI system, leveraging multiple financial data sources.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import seaborn as sns
from datetime import datetime, timedelta
import os
import json
import tempfile

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedFinancialAnalysisModule:
    """
    Enhanced Financial Analysis Module for analyzing financial data and markets
    using multiple data sources.
    """
    
    def __init__(self, financialdata_net_api=None, yahoo_finance_api=None):
        """
        Initialize the Enhanced Financial Analysis Module.
        
        Args:
            financialdata_net_api (FinancialdataNetAPI, optional): FinancialdataNet API instance
            yahoo_finance_api (YahooFinanceAPI, optional): Yahoo Finance API instance
        """
        self.financialdata_net_api = financialdata_net_api
        self.yahoo_finance_api = yahoo_finance_api
        self.data_cache = {}
        logger.info("Enhanced Financial Analysis Module initialized")
    
    def get_stock_data(self, symbol, period="1mo", data_source="yahoo"):
        """
        Retrieve stock data for a given symbol from the specified data source.
        
        Args:
            symbol (str): Stock ticker symbol
            period (str, optional): Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            data_source (str, optional): Data source to use ('yahoo', 'financialdata', 'both')
            
        Returns:
            dict: Stock data and metadata
        """
        try:
            # Check cache first
            cache_key = f"{symbol}_{period}_{data_source}"
            if cache_key in self.data_cache:
                cache_time, data = self.data_cache[cache_key]
                # Use cache if less than 1 hour old
                if datetime.now() - cache_time < timedelta(hours=1):
                    logger.info(f"Using cached data for {symbol}")
                    return data
            
            result = {
                'symbol': symbol,
                'period': period,
                'data_source': data_source,
                'success': False
            }
            
            # Get data from Yahoo Finance
            if data_source in ["yahoo", "both"]:
                if self.yahoo_finance_api:
                    # Map period to Yahoo Finance range and interval
                    range_map = {
                        "1d": {"range": "1d", "interval": "5m"},
                        "5d": {"range": "5d", "interval": "15m"},
                        "1mo": {"range": "1mo", "interval": "1d"},
                        "3mo": {"range": "3mo", "interval": "1d"},
                        "6mo": {"range": "6mo", "interval": "1d"},
                        "1y": {"range": "1y", "interval": "1d"},
                        "2y": {"range": "2y", "interval": "1wk"},
                        "5y": {"range": "5y", "interval": "1wk"},
                        "10y": {"range": "10y", "interval": "1mo"},
                        "ytd": {"range": "ytd", "interval": "1d"},
                        "max": {"range": "max", "interval": "1mo"}
                    }
                    
                    range_param = range_map.get(period, {"range": "1mo", "interval": "1d"})
                    
                    yahoo_data = self.yahoo_finance_api.get_stock_chart(
                        symbol, 
                        interval=range_param["interval"], 
                        range=range_param["range"]
                    )
                    
                    if yahoo_data["success"]:
                        result["yahoo_data"] = yahoo_data
                        result["success"] = True
                        
                        # Extract company info if available
                        if "meta" in yahoo_data:
                            result["company_name"] = yahoo_data["meta"].get("shortName", symbol)
                            result["exchange"] = yahoo_data["meta"].get("exchangeName", "Unknown")
                            result["currency"] = yahoo_data["meta"].get("currency", "USD")
                        
                        # Process time series data
                        if "time_series" in yahoo_data:
                            result["data"] = yahoo_data["time_series"]
            
            # Get data from FinancialData.net
            if data_source in ["financialdata", "both"]:
                if self.financialdata_net_api:
                    financialdata_data = self.financialdata_net_api.get_stock_prices(symbol)
                    
                    if financialdata_data["success"]:
                        result["financialdata_net_data"] = financialdata_data
                        result["success"] = True
                        
                        # If we don't have data from Yahoo, use this as primary data
                        if "data" not in result and "data" in financialdata_data:
                            result["data"] = financialdata_data["data"]
            
            # If we have data from both sources, merge them
            if data_source == "both" and "yahoo_data" in result and "financialdata_net_data" in result:
                result["data_sources"] = ["yahoo", "financialdata_net"]
                # Use Yahoo data as primary but could implement more sophisticated merging
            
            # Calculate basic statistics if we have data
            if result["success"] and "data" in result:
                df = pd.DataFrame(result["data"])
                
                # Ensure we have the necessary columns
                required_cols = ["close", "open", "high", "low", "volume"]
                if all(col in df.columns for col in required_cols):
                    latest_price = df['close'].iloc[-1] if not df.empty else None
                    price_change = df['close'].iloc[-1] - df['close'].iloc[0] if not df.empty else None
                    price_change_pct = (price_change / df['close'].iloc[0]) * 100 if price_change is not None and df['close'].iloc[0] != 0 else None
                    avg_volume = df['volume'].mean() if 'volume' in df.columns else None
                    
                    result["stats"] = {
                        'latest_price': latest_price,
                        'price_change': price_change,
                        'price_change_pct': price_change_pct,
                        'avg_volume': avg_volume
                    }
            
            # Update cache
            if result["success"]:
                self.data_cache[cache_key] = (datetime.now(), result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving stock data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'success': False
            }
    
    def get_company_fundamentals(self, symbol):
        """
        Get comprehensive fundamental data for a company.
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: Fundamental data including financial statements and ratios
        """
        try:
            result = {
                'symbol': symbol,
                'success': False
            }
            
            # Get financial statements from FinancialData.net
            if self.financialdata_net_api:
                # Get income statement
                income_statement = self.financialdata_net_api.get_income_statement(symbol)
                if income_statement["success"]:
                    result["income_statement"] = income_statement["data"]
                    result["success"] = True
                
                # Get balance sheet
                balance_sheet = self.financialdata_net_api.get_balance_sheet(symbol)
                if balance_sheet["success"]:
                    result["balance_sheet"] = balance_sheet["data"]
                    result["success"] = True
                
                # Get cash flow statement
                cash_flow = self.financialdata_net_api.get_cash_flow(symbol)
                if cash_flow["success"]:
                    result["cash_flow"] = cash_flow["data"]
                    result["success"] = True
                
                # Get financial ratios
                ratios = self.financialdata_net_api.get_financial_ratios(symbol)
                if ratios["success"]:
                    result["financial_ratios"] = ratios["data"]
                    result["success"] = True
            
            # Get insights from Yahoo Finance
            if self.yahoo_finance_api:
                insights = self.yahoo_finance_api.get_stock_insights(symbol)
                if insights["success"]:
                    result["insights"] = insights
                    result["success"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving company fundamentals for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'success': False
            }
    
    def get_insider_trading(self, symbol):
        """
        Get insider trading data for a company.
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: Insider trading data
        """
        try:
            result = {
                'symbol': symbol,
                'success': False
            }
            
            # Get insider trading data from FinancialData.net
            if self.financialdata_net_api:
                financialdata_insiders = self.financialdata_net_api.get_insider_trading(symbol)
                if financialdata_insiders["success"]:
                    result["financialdata_insiders"] = financialdata_insiders["data"]
                    result["success"] = True
            
            # Get insider holdings from Yahoo Finance
            if self.yahoo_finance_api:
                yahoo_insiders = self.yahoo_finance_api.get_stock_holders(symbol)
                if yahoo_insiders["success"] and "insiders" in yahoo_insiders:
                    result["yahoo_insiders"] = yahoo_insiders["insiders"]
                    result["success"] = True
            
            # Combine data if we have both sources
            if "financialdata_insiders" in result and "yahoo_insiders" in result:
                # This would require more sophisticated merging based on the actual data structure
                result["combined"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving insider trading data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'success': False
            }
    
    def get_sec_filings(self, symbol):
        """
        Get SEC filings for a company.
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: SEC filing data
        """
        try:
            if self.yahoo_finance_api:
                return self.yahoo_finance_api.get_stock_sec_filing(symbol)
            else:
                return {
                    'symbol': symbol,
                    'error': "Yahoo Finance API not available",
                    'success': False
                }
                
        except Exception as e:
            logger.error(f"Error retrieving SEC filings for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'success': False
            }
    
    def get_analyst_opinions(self, symbol):
        """
        Get analyst opinions for a company.
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: Analyst opinions data
        """
        try:
            if self.yahoo_finance_api:
                return self.yahoo_finance_api.get_stock_analyst_opinions(symbol)
            else:
                return {
                    'symbol': symbol,
                    'error': "Yahoo Finance API not available",
                    'success': False
                }
                
        except Exception as e:
            logger.error(f"Error retrieving analyst opinions for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'success': False
            }
    
    def generate_stock_chart(self, symbol, period="1mo", chart_type="line", output_dir=None, include_volume=True, include_indicators=False):
        """
        Generate an enhanced stock chart and save it to a file.
        
        Args:
            symbol (str): Stock ticker symbol
            period (str, optional): Time period
            chart_type (str, optional): Chart type (line, candle, ohlc)
            output_dir (str, optional): Directory to save the chart
            include_volume (bool, optional): Whether to include volume subplot
            include_indicators (bool, optional): Whether to include technical indicators
            
        Returns:
            dict: Chart information including file path
        """
        try:
            # Get stock data
            stock_data = self.get_stock_data(symbol, period=period, data_source="both")
            
            if not stock_data['success']:
                return {
                    'success': False,
                    'error': stock_data.get('error', 'Failed to retrieve stock data')
                }
            
            # Convert data to DataFrame
            df = pd.DataFrame(stock_data['data'])
            
            # Ensure we have date/timestamp column
            date_col = None
            for col in ['date', 'timestamp']:
                if col in df.columns:
                    date_col = col
                    break
            
            if date_col is None:
                return {
                    'success': False,
                    'error': 'No date or timestamp column found in data'
                }
            
            # Convert date to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
                df[date_col] = pd.to_datetime(df[date_col])
            
            # Sort by date
            df = df.sort_values(date_col)
            
            # Set up the figure with style
            plt.style.use('seaborn-v0_8-darkgrid')
            
            # Determine figure size and layout based on options
            if include_volume:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
            else:
                fig, ax1 = plt.subplots(figsize=(12, 6))
            
            # Format the x-axis to show dates nicely
            if (df[date_col].max() - df[date_col].min()).days > 365:
                date_format = mdates.DateFormatter('%Y-%m')
                ax1.xaxis.set_major_formatter(date_format)
            else:
                date_format = mdates.DateFormatter('%Y-%m-%d')
                ax1.xaxis.set_major_formatter(date_format)
                plt.xticks(rotation=45)
            
            # Get company name if available
            company_name = stock_data.get('company_name', symbol)
            
            # Plot based on chart type
            if chart_type.lower() == 'candle':
                try:
                    import mplfinance as mpf
                    
                    # Convert DataFrame to format required by mplfinance
                    df_mpf = df.rename(columns={
                        date_col: 'Date',
                        'open': 'Open',
                        'high': 'High',
                        'low': 'Low',
                        'close': 'Close',
                        'volume': 'Volume'
                    }).set_index('Date')
                    
                    # Create a temporary file for the candlestick chart
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
                        mpf.plot(
                            df_mpf,
                            type='candle',
                            style='yahoo',
                            title=f"{company_name} ({symbol}) - {period}",
                            volume=include_volume,
                            savefig=dict(fname=tmpfile.name, dpi=300, bbox_inches='tight')
                        )
                        
                        # Save the chart
                        if output_dir is None:
                            output_dir = os.path.expanduser("~")
                        
                        os.makedirs(output_dir, exist_ok=True)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{symbol}_{period}_{timestamp}.png"
                        filepath = os.path.join(output_dir, filename)
                        
                        # Copy the temporary file to the final location
                        import shutil
                        shutil.copy(tmpfile.name, filepath)
                    
                    return {
                        'success': True,
                        'symbol': symbol,
                        'company_name': company_name,
                        'period': period,
                        'chart_type': 'candle',
                        'filepath': filepath
                    }
                    
                except ImportError:
                    logger.warning("mplfinance not available, falling back to OHLC chart")
                    chart_type = 'ohlc'
            
            if chart_type.lower() == 'ohlc':
                try:
                    from mplfinance.original_flavor import candlestick_ohlc
                    
                    # Convert date to matplotlib format
                    df['mpl_date'] = df[date_col].map(mdates.date2num)
                    
                    # Create OHLC data
                    ohlc = df[['mpl_date', 'open', 'high', 'low', 'close']]
                    
                    # Plot OHLC chart
                    candlestick_ohlc(ax1, ohlc.values, width=0.6, colorup='green', colordown='red')
                    
                except ImportError:
                    logger.warning("mplfinance not available, falling back to line chart")
                    chart_type = 'line'
            
            # Default to line chart
            if chart_type.lower() == 'line':
                ax1.plot(df[date_col], df['close'], label='Close Price', color='#1f77b4', linewidth=2)
                ax1.fill_between(df[date_col], df['close'], alpha=0.2, color='#1f77b4')
            
            # Add moving averages if indicators are requested
            if include_indicators:
                # 20-day moving average
                df['MA20'] = df['close'].rolling(window=20).mean()
                ax1.plot(df[date_col], df['MA20'], label='20-day MA', color='#ff7f0e', linewidth=1.5)
                
                # 50-day moving average
                df['MA50'] = df['close'].rolling(window=50).mean()
                ax1.plot(df[date_col], df['MA50'], label='50-day MA', color='#2ca02c', linewidth=1.5)
                
                # 200-day moving average if we have enough data
                if len(df) > 200:
                    df['MA200'] = df['close'].rolling(window=200).mean()
                    ax1.plot(df[date_col], df['MA200'], label='200-day MA', color='#d62728', linewidth=1.5)
            
            # Format y-axis with currency
            currency = stock_data.get('currency', 'USD')
            ax1.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'${y:.2f}'))
            
            # Add volume subplot if requested
            if include_volume and 'volume' in df.columns:
                # Plot volume bars
                ax2.bar(df[date_col], df['volume'], color='#1f77b4', alpha=0.5)
                
                # Format y-axis for volume (in millions or billions)
                def volume_formatter(x, pos):
                    if x >= 1e9:
                        return f'{x/1e9:.1f}B'
                    elif x >= 1e6:
                        return f'{x/1e6:.1f}M'
                    else:
                        return f'{x:.0f}'
                
                ax2.yaxis.set_major_formatter(FuncFormatter(volume_formatter))
                ax2.set_ylabel('Volume')
                
                # Add grid to volume subplot
                ax2.grid(True, alpha=0.3)
            
            # Add chart details
            ax1.set_title(f"{company_name} ({symbol}) - {period}", fontsize=16, fontweight='bold')
            ax1.set_ylabel(f'Price ({currency})')
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc='best')
            
            # Add price change annotation
            if 'stats' in stock_data and stock_data['stats']['price_change'] is not None:
                price_change = stock_data['stats']['price_change']
                price_change_pct = stock_data['stats']['price_change_pct']
                latest_price = stock_data['stats']['latest_price']
                
                change_text = f"Price: ${latest_price:.2f}\nChange: ${price_change:.2f} ({price_change_pct:.2f}%)"
                color = 'green' if price_change >= 0 else 'red'
                
                # Position the text in the upper left with a small offset
                ax1.text(0.02, 0.95, change_text, transform=ax1.transAxes, 
                        verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', 
                        facecolor='white', alpha=0.8, edgecolor=color), 
                        color=color, fontsize=10)
            
            plt.tight_layout()
            
            # Save the chart
            if output_dir is None:
                output_dir = os.path.expanduser("~")
            
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{symbol}_{period}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                'success': True,
                'symbol': symbol,
                'company_name': company_name,
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
            result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'success': False
            }
            
            # Get stock data for different time periods
            data_1d = self.get_stock_data(symbol, period="1d", data_source="both")
            data_1mo = self.get_stock_data(symbol, period="1mo", data_source="both")
            data_6mo = self.get_stock_data(symbol, period="6mo", data_source="both")
            data_1y = self.get_stock_data(symbol, period="1y", data_source="both")
            
            if not data_1mo['success']:
                return {
                    'success': False,
                    'error': data_1mo.get('error', 'Failed to retrieve stock data')
                }
            
            # Get company fundamentals
            fundamentals = self.get_company_fundamentals(symbol)
            
            # Get insider trading data
            insider_trading = self.get_insider_trading(symbol)
            
            # Get SEC filings
            sec_filings = self.get_sec_filings(symbol)
            
            # Get analyst opinions
            analyst_opinions = self.get_analyst_opinions(symbol)
            
            # Prepare data for analysis
            company_info = {
                'symbol': symbol,
                'company_name': data_1mo.get('company_name', symbol),
                'exchange': data_1mo.get('exchange', 'Unknown'),
                'currency': data_1mo.get('currency', 'USD')
            }
            
            # Calculate performance metrics
            performance = {}
            
            if data_1d['success'] and 'stats' in data_1d:
                performance['1d'] = {
                    'change': data_1d['stats']['price_change'],
                    'change_pct': data_1d['stats']['price_change_pct']
                }
            
            if data_1mo['success'] and 'stats' in data_1mo:
                performance['1mo'] = {
                    'change': data_1mo['stats']['price_change'],
                    'change_pct': data_1mo['stats']['price_change_pct']
                }
            
            if data_6mo['success'] and 'stats' in data_6mo:
                performance['6mo'] = {
                    'change': data_6mo['stats']['price_change'],
                    'change_pct': data_6mo['stats']['price_change_pct']
                }
            
            if data_1y['success'] and 'stats' in data_1y:
                performance['1y'] = {
                    'change': data_1y['stats']['price_change'],
                    'change_pct': data_1y['stats']['price_change_pct']
                }
            
            # Calculate technical indicators (using 1-month data)
            technical_indicators = {}
            
            if data_1mo['success'] and 'data' in data_1mo:
                df = pd.DataFrame(data_1mo['data'])
                
                # Ensure we have the necessary columns
                if 'close' in df.columns:
                    # Moving Averages
                    df['MA20'] = df['close'].rolling(window=20).mean()
                    df['MA50'] = df['close'].rolling(window=50).mean()
                    df['MA200'] = df['close'].rolling(window=200).mean()
                    
                    # Get the latest values
                    latest_close = df['close'].iloc[-1] if not df.empty else None
                    latest_ma20 = df['MA20'].iloc[-1] if not df.empty and 'MA20' in df else None
                    latest_ma50 = df['MA50'].iloc[-1] if not df.empty and 'MA50' in df else None
                    latest_ma200 = df['MA200'].iloc[-1] if not df.empty and 'MA200' in df else None
                    
                    # Moving Average Analysis
                    ma_analysis = {}
                    
                    if latest_close is not None and latest_ma20 is not None:
                        ma_analysis['ma20'] = {
                            'value': latest_ma20,
                            'position': 'above' if latest_close > latest_ma20 else 'below',
                            'signal': 'bullish' if latest_close > latest_ma20 else 'bearish'
                        }
                    
                    if latest_close is not None and latest_ma50 is not None:
                        ma_analysis['ma50'] = {
                            'value': latest_ma50,
                            'position': 'above' if latest_close > latest_ma50 else 'below',
                            'signal': 'bullish' if latest_close > latest_ma50 else 'bearish'
                        }
                    
                    if latest_close is not None and latest_ma200 is not None:
                        ma_analysis['ma200'] = {
                            'value': latest_ma200,
                            'position': 'above' if latest_close > latest_ma200 else 'below',
                            'signal': 'bullish' if latest_close > latest_ma200 else 'bearish'
                        }
                    
                    technical_indicators['moving_averages'] = ma_analysis
                    
                    # Relative Strength Index (RSI)
                    try:
                        # Calculate daily returns
                        df['returns'] = df['close'].pct_change()
                        
                        # Calculate gains and losses
                        df['gain'] = np.where(df['returns'] > 0, df['returns'], 0)
                        df['loss'] = np.where(df['returns'] < 0, -df['returns'], 0)
                        
                        # Calculate average gains and losses over 14 periods
                        avg_gain = df['gain'].rolling(window=14).mean()
                        avg_loss = df['loss'].rolling(window=14).mean()
                        
                        # Calculate RS and RSI
                        rs = avg_gain / avg_loss
                        df['RSI'] = 100 - (100 / (1 + rs))
                        
                        latest_rsi = df['RSI'].iloc[-1] if not df.empty and not pd.isna(df['RSI'].iloc[-1]) else None
                        
                        if latest_rsi is not None:
                            rsi_signal = 'oversold' if latest_rsi < 30 else 'overbought' if latest_rsi > 70 else 'neutral'
                            
                            technical_indicators['rsi'] = {
                                'value': latest_rsi,
                                'signal': rsi_signal
                            }
                    except Exception as e:
                        logger.warning(f"Error calculating RSI: {e}")
                    
                    # MACD (Moving Average Convergence Divergence)
                    try:
                        # Calculate MACD components
                        df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
                        df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
                        df['MACD'] = df['EMA12'] - df['EMA26']
                        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
                        df['Histogram'] = df['MACD'] - df['Signal']
                        
                        latest_macd = df['MACD'].iloc[-1] if not df.empty and 'MACD' in df else None
                        latest_signal = df['Signal'].iloc[-1] if not df.empty and 'Signal' in df else None
                        latest_histogram = df['Histogram'].iloc[-1] if not df.empty and 'Histogram' in df else None
                        
                        if latest_macd is not None and latest_signal is not None:
                            macd_signal = 'bullish' if latest_macd > latest_signal else 'bearish'
                            
                            technical_indicators['macd'] = {
                                'macd': latest_macd,
                                'signal': latest_signal,
                                'histogram': latest_histogram,
                                'trend': macd_signal
                            }
                    except Exception as e:
                        logger.warning(f"Error calculating MACD: {e}")
            
            # Combine all analysis components
            result = {
                'symbol': symbol,
                'company_info': company_info,
                'performance': performance,
                'technical_indicators': technical_indicators,
                'success': True
            }
            
            # Add fundamental data if available
            if fundamentals['success']:
                result['fundamentals'] = fundamentals
            
            # Add insider trading data if available
            if insider_trading['success']:
                result['insider_trading'] = insider_trading
            
            # Add SEC filings if available
            if sec_filings['success']:
                result['sec_filings'] = sec_filings
            
            # Add analyst opinions if available
            if analyst_opinions['success']:
                result['analyst_opinions'] = analyst_opinions
            
            # Generate overall analysis summary
            summary = []
            
            # Price performance summary
            if performance:
                perf_text = "Price Performance: "
                for period, data in performance.items():
                    if 'change_pct' in data:
                        direction = "up" if data['change_pct'] > 0 else "down"
                        perf_text += f"{period}: {direction} {abs(data['change_pct']):.2f}%, "
                summary.append(perf_text.rstrip(", "))
            
            # Technical indicators summary
            if 'moving_averages' in technical_indicators:
                ma_text = "Moving Averages: "
                for ma, data in technical_indicators['moving_averages'].items():
                    ma_text += f"{ma} signal is {data['signal']}, "
                summary.append(ma_text.rstrip(", "))
            
            if 'rsi' in technical_indicators:
                rsi_data = technical_indicators['rsi']
                summary.append(f"RSI: {rsi_data['value']:.2f} ({rsi_data['signal']})")
            
            if 'macd' in technical_indicators:
                macd_data = technical_indicators['macd']
                summary.append(f"MACD: {macd_data['trend']} signal")
            
            # Add Yahoo Finance insights if available
            if fundamentals['success'] and 'insights' in fundamentals:
                insights = fundamentals['insights']
                if 'technical_events' in insights:
                    tech_events = insights['technical_events']
                    for outlook in ['short_term_outlook', 'intermediate_outlook', 'long_outlook']:
                        if outlook in tech_events:
                            outlook_name = outlook.replace('_', ' ').title()
                            outlook_data = tech_events[outlook]
                            summary.append(f"{outlook_name}: {outlook_data['description']} ({outlook_data['direction']})")
            
            result['summary'] = summary
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing stock {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'success': False
            }
    
    def analyze_portfolio(self, portfolio):
        """
        Analyze a portfolio of stocks.
        
        Args:
            portfolio (list): List of dicts with symbol and optionally shares and cost_basis
            
        Returns:
            dict: Portfolio analysis results
        """
        try:
            result = {
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'holdings': []
            }
            
            total_value = 0
            total_cost = 0
            
            # Analyze each holding
            for holding in portfolio:
                symbol = holding['symbol']
                shares = holding.get('shares', 0)
                cost_basis = holding.get('cost_basis', 0)
                
                # Get current stock data
                stock_data = self.get_stock_data(symbol, period="1mo", data_source="both")
                
                if stock_data['success'] and 'stats' in stock_data:
                    latest_price = stock_data['stats']['latest_price']
                    
                    # Calculate holding value and performance
                    current_value = shares * latest_price if shares > 0 else 0
                    cost_value = shares * cost_basis if shares > 0 and cost_basis > 0 else 0
                    gain_loss = current_value - cost_value if cost_value > 0 else 0
                    gain_loss_pct = (gain_loss / cost_value) * 100 if cost_value > 0 else 0
                    
                    holding_result = {
                        'symbol': symbol,
                        'company_name': stock_data.get('company_name', symbol),
                        'shares': shares,
                        'latest_price': latest_price,
                        'current_value': current_value,
                        'success': True
                    }
                    
                    if cost_basis > 0:
                        holding_result.update({
                            'cost_basis': cost_basis,
                            'cost_value': cost_value,
                            'gain_loss': gain_loss,
                            'gain_loss_pct': gain_loss_pct
                        })
                    
                    # Add performance data
                    if 'stats' in stock_data:
                        holding_result['performance'] = {
                            'price_change': stock_data['stats']['price_change'],
                            'price_change_pct': stock_data['stats']['price_change_pct']
                        }
                    
                    result['holdings'].append(holding_result)
                    
                    # Update portfolio totals
                    total_value += current_value
                    total_cost += cost_value
                else:
                    result['holdings'].append({
                        'symbol': symbol,
                        'success': False,
                        'error': stock_data.get('error', 'Failed to retrieve stock data')
                    })
            
            # Calculate portfolio performance
            if total_cost > 0:
                portfolio_gain_loss = total_value - total_cost
                portfolio_gain_loss_pct = (portfolio_gain_loss / total_cost) * 100
                
                result.update({
                    'total_value': total_value,
                    'total_cost': total_cost,
                    'gain_loss': portfolio_gain_loss,
                    'gain_loss_pct': portfolio_gain_loss_pct
                })
            else:
                result['total_value'] = total_value
            
            # Calculate portfolio diversification
            if result['holdings']:
                sectors = {}
                for holding in result['holdings']:
                    if holding['success']:
                        # This would require additional API calls to get sector information
                        # For now, we'll just use the symbol as a placeholder
                        sector = "Unknown"  # Would need to be retrieved from API
                        if sector not in sectors:
                            sectors[sector] = 0
                        sectors[sector] += holding.get('current_value', 0)
                
                # Calculate sector percentages
                if total_value > 0:
                    sector_allocation = {
                        sector: (value / total_value) * 100
                        for sector, value in sectors.items()
                    }
                    result['sector_allocation'] = sector_allocation
            
            result['success'] = True
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def export_analysis_to_pdf(self, analysis, output_dir=None):
        """
        Export stock analysis to a PDF report.
        
        Args:
            analysis (dict): Stock analysis data
            output_dir (str, optional): Directory to save the PDF
            
        Returns:
            dict: Export result including file path
        """
        try:
            # This would require additional libraries like reportlab or fpdf
            # For now, we'll just return a placeholder
            
            if output_dir is None:
                output_dir = os.path.expanduser("~")
            
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{analysis['symbol']}_analysis_{timestamp}.txt"
            filepath = os.path.join(output_dir, filename)
            
            # Write analysis to a text file as a placeholder
            with open(filepath, 'w') as f:
                f.write(f"Stock Analysis Report for {analysis['symbol']}\n")
                f.write(f"Generated on {analysis['timestamp']}\n\n")
                
                if 'company_info' in analysis:
                    f.write("Company Information:\n")
                    for key, value in analysis['company_info'].items():
                        f.write(f"  {key}: {value}\n")
                    f.write("\n")
                
                if 'performance' in analysis:
                    f.write("Performance:\n")
                    for period, data in analysis['performance'].items():
                        f.write(f"  {period}: {data['change_pct']:.2f}%\n")
                    f.write("\n")
                
                if 'technical_indicators' in analysis:
                    f.write("Technical Indicators:\n")
                    for indicator, data in analysis['technical_indicators'].items():
                        f.write(f"  {indicator}:\n")
                        if isinstance(data, dict):
                            for k, v in data.items():
                                f.write(f"    {k}: {v}\n")
                        else:
                            f.write(f"    {data}\n")
                    f.write("\n")
                
                if 'summary' in analysis:
                    f.write("Analysis Summary:\n")
                    for item in analysis['summary']:
                        f.write(f"  {item}\n")
            
            return {
                'success': True,
                'symbol': analysis['symbol'],
                'filepath': filepath
            }
            
        except Exception as e:
            logger.error(f"Error exporting analysis to PDF: {e}")
            return {
                'success': False,
                'error': str(e)
            }
