"""
Financial Data API Integration Module

This module provides integration with financial data APIs for the Open Manus AI system.
"""

import os
import logging
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class FinancialDataAPI:
    """
    Financial Data API integration for accessing market data and financial information.
    """
    
    def __init__(self):
        """Initialize the Financial Data API integration."""
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.finnhub_key = os.getenv("FINNHUB_API_KEY")
        
        if not self.alpha_vantage_key:
            logger.warning("Alpha Vantage API key not found in environment variables")
        else:
            logger.info("Alpha Vantage API integration initialized")
            
        if not self.finnhub_key:
            logger.warning("Finnhub API key not found in environment variables")
        else:
            logger.info("Finnhub API integration initialized")
    
    def get_stock_data(self, symbol, interval="daily", output_size="compact"):
        """
        Get stock time series data using Alpha Vantage API.
        
        Args:
            symbol (str): Stock ticker symbol
            interval (str, optional): Time interval (intraday, daily, weekly, monthly)
            output_size (str, optional): Output size (compact or full)
            
        Returns:
            dict: Stock data and metadata
        """
        try:
            if not self.alpha_vantage_key:
                return {"success": False, "error": "Alpha Vantage API key not configured"}
            
            # Determine the function based on interval
            if interval == "intraday":
                function = "TIME_SERIES_INTRADAY"
                params = {
                    "function": function,
                    "symbol": symbol,
                    "interval": "5min",
                    "outputsize": output_size,
                    "apikey": self.alpha_vantage_key
                }
            elif interval == "daily":
                function = "TIME_SERIES_DAILY"
                params = {
                    "function": function,
                    "symbol": symbol,
                    "outputsize": output_size,
                    "apikey": self.alpha_vantage_key
                }
            elif interval == "weekly":
                function = "TIME_SERIES_WEEKLY"
                params = {
                    "function": function,
                    "symbol": symbol,
                    "apikey": self.alpha_vantage_key
                }
            elif interval == "monthly":
                function = "TIME_SERIES_MONTHLY"
                params = {
                    "function": function,
                    "symbol": symbol,
                    "apikey": self.alpha_vantage_key
                }
            else:
                return {"success": False, "error": f"Invalid interval: {interval}"}
            
            # Make API request
            url = "https://www.alphavantage.co/query"
            response = requests.get(url, params=params)
            data = response.json()
            
            # Check for error messages
            if "Error Message" in data:
                return {"success": False, "error": data["Error Message"]}
            
            # Extract metadata and time series data
            metadata = data.get("Meta Data", {})
            
            # Determine the time series key based on the function
            time_series_key = None
            for key in data.keys():
                if "Time Series" in key:
                    time_series_key = key
                    break
            
            if not time_series_key:
                return {"success": False, "error": "No time series data found in response"}
            
            time_series = data[time_series_key]
            
            # Convert to pandas DataFrame for easier processing
            df = pd.DataFrame.from_dict(time_series, orient="index")
            
            # Rename columns to remove numeric prefixes
            df.columns = [col.split(". ")[1] if ". " in col else col for col in df.columns]
            
            # Convert string values to float
            for col in df.columns:
                df[col] = pd.to_numeric(df[col])
            
            # Reset index to make date a column and convert to datetime
            df.reset_index(inplace=True)
            df.rename(columns={"index": "date"}, inplace=True)
            df["date"] = pd.to_datetime(df["date"])
            
            # Sort by date
            df = df.sort_values("date")
            
            return {
                "symbol": symbol,
                "interval": interval,
                "metadata": metadata,
                "data": df.to_dict(orient="records"),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving stock data for {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_company_overview(self, symbol):
        """
        Get company overview data using Alpha Vantage API.
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: Company overview data
        """
        try:
            if not self.alpha_vantage_key:
                return {"success": False, "error": "Alpha Vantage API key not configured"}
            
            # Set up parameters
            params = {
                "function": "OVERVIEW",
                "symbol": symbol,
                "apikey": self.alpha_vantage_key
            }
            
            # Make API request
            url = "https://www.alphavantage.co/query"
            response = requests.get(url, params=params)
            data = response.json()
            
            # Check for error messages
            if "Error Message" in data:
                return {"success": False, "error": data["Error Message"]}
            
            # Check if data is empty
            if not data or len(data) <= 1:
                return {"success": False, "error": f"No company overview data found for {symbol}"}
            
            return {
                "symbol": symbol,
                "overview": data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving company overview for {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stock_quote(self, symbol):
        """
        Get real-time stock quote using Finnhub API.
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: Real-time stock quote data
        """
        try:
            if not self.finnhub_key:
                return {"success": False, "error": "Finnhub API key not configured"}
            
            # Make API request
            url = f"https://finnhub.io/api/v1/quote"
            params = {
                "symbol": symbol,
                "token": self.finnhub_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            # Check if data is valid
            if "error" in data:
                return {"success": False, "error": data["error"]}
            
            # Add timestamp to data
            data["timestamp"] = datetime.now().isoformat()
            
            return {
                "symbol": symbol,
                "quote": data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving stock quote for {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_company_news(self, symbol, from_date=None, to_date=None):
        """
        Get company news using Finnhub API.
        
        Args:
            symbol (str): Stock ticker symbol
            from_date (str, optional): Start date in YYYY-MM-DD format
            to_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            dict: Company news data
        """
        try:
            if not self.finnhub_key:
                return {"success": False, "error": "Finnhub API key not configured"}
            
            # Set default dates if not provided
            if not from_date:
                from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            if not to_date:
                to_date = datetime.now().strftime("%Y-%m-%d")
            
            # Make API request
            url = f"https://finnhub.io/api/v1/company-news"
            params = {
                "symbol": symbol,
                "from": from_date,
                "to": to_date,
                "token": self.finnhub_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            # Check if data is valid
            if isinstance(data, dict) and "error" in data:
                return {"success": False, "error": data["error"]}
            
            return {
                "symbol": symbol,
                "from_date": from_date,
                "to_date": to_date,
                "news": data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving company news for {symbol}: {e}")
            return {"success": False, "error": str(e)}
