"""
Financial Data Net API Integration Module

This module provides integration with financialdata.net API for accessing
comprehensive financial data including stock prices, financial statements,
and other market information.
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

class FinancialdataNetAPI:
    """
    Financial Data Net API integration for accessing comprehensive financial data.
    """
    
    def __init__(self):
        """Initialize the Financial Data Net API integration."""
        self.api_key = os.getenv("FINANCIALDATA_NET_API_KEY")
        self.base_url = "https://financialdata.net/api/v1"
        
        if not self.api_key:
            logger.warning("Financial Data Net API key not found in environment variables")
        else:
            logger.info("Financial Data Net API integration initialized")
        
        # Initialize cache
        self.cache = {}
        self.cache_expiry = {}
    
    def _make_request(self, endpoint, params=None, cache_duration=3600):
        """
        Make a request to the Financial Data Net API with caching.
        
        Args:
            endpoint (str): API endpoint path
            params (dict, optional): Query parameters
            cache_duration (int, optional): Cache duration in seconds
            
        Returns:
            dict: API response data
        """
        try:
            # Initialize params if None
            if params is None:
                params = {}
            
            # Add API key to params
            params["key"] = self.api_key
            
            # Create cache key from endpoint and params
            cache_key = f"{endpoint}_{str(params)}"
            
            # Check cache
            current_time = datetime.now()
            if cache_key in self.cache and self.cache_expiry.get(cache_key, datetime.min) > current_time:
                logger.debug(f"Using cached data for {endpoint}")
                return self.cache[cache_key]
            
            # Make API request
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, params=params)
            
            # Check for errors
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Update cache
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = current_time + timedelta(seconds=cache_duration)
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {endpoint}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stock_symbols(self, offset=0, format="json"):
        """
        Get a list of stock symbols for publicly traded companies.
        
        Args:
            offset (int, optional): Number of records to skip
            format (str, optional): Response format (json or csv)
            
        Returns:
            dict: Stock symbols data
        """
        try:
            params = {
                "offset": offset,
                "format": format
            }
            
            data = self._make_request("stock-symbols", params, cache_duration=86400)  # Cache for 24 hours
            
            return {
                "symbols": data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving stock symbols: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stock_prices(self, identifier, offset=0, format="json"):
        """
        Get historical stock prices for a specific symbol.
        
        Args:
            identifier (str): Stock ticker symbol
            offset (int, optional): Number of records to skip
            format (str, optional): Response format (json or csv)
            
        Returns:
            dict: Historical stock price data
        """
        try:
            params = {
                "identifier": identifier,
                "offset": offset,
                "format": format
            }
            
            data = self._make_request("stock-prices", params)
            
            # Convert to pandas DataFrame for easier processing if data is available
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                
                # Convert date strings to datetime objects
                if "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"])
                
                # Convert numeric strings to float
                numeric_columns = ["open", "high", "low", "close", "volume"]
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                
                # Sort by date
                if "date" in df.columns:
                    df = df.sort_values("date")
                
                return {
                    "symbol": identifier,
                    "data": df.to_dict(orient="records"),
                    "success": True
                }
            else:
                return {
                    "symbol": identifier,
                    "data": data,
                    "success": True
                }
            
        except Exception as e:
            logger.error(f"Error retrieving stock prices for {identifier}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_etf_prices(self, identifier, offset=0, format="json"):
        """
        Get historical ETF prices for a specific symbol.
        
        Args:
            identifier (str): ETF ticker symbol
            offset (int, optional): Number of records to skip
            format (str, optional): Response format (json or csv)
            
        Returns:
            dict: Historical ETF price data
        """
        try:
            params = {
                "identifier": identifier,
                "offset": offset,
                "format": format
            }
            
            data = self._make_request("etf-prices", params)
            
            # Convert to pandas DataFrame for easier processing if data is available
            if isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                
                # Convert date strings to datetime objects
                if "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"])
                
                # Convert numeric strings to float
                numeric_columns = ["open", "high", "low", "close", "volume"]
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                
                # Sort by date
                if "date" in df.columns:
                    df = df.sort_values("date")
                
                return {
                    "symbol": identifier,
                    "data": df.to_dict(orient="records"),
                    "success": True
                }
            else:
                return {
                    "symbol": identifier,
                    "data": data,
                    "success": True
                }
            
        except Exception as e:
            logger.error(f"Error retrieving ETF prices for {identifier}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_income_statement(self, identifier, period="annual", format="json"):
        """
        Get income statement data for a specific company.
        
        Args:
            identifier (str): Stock ticker symbol
            period (str, optional): Period type (annual or quarterly)
            format (str, optional): Response format (json or csv)
            
        Returns:
            dict: Income statement data
        """
        try:
            params = {
                "identifier": identifier,
                "period": period,
                "format": format
            }
            
            data = self._make_request("income-statement", params, cache_duration=86400)  # Cache for 24 hours
            
            return {
                "symbol": identifier,
                "period": period,
                "data": data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving income statement for {identifier}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_balance_sheet(self, identifier, period="annual", format="json"):
        """
        Get balance sheet data for a specific company.
        
        Args:
            identifier (str): Stock ticker symbol
            period (str, optional): Period type (annual or quarterly)
            format (str, optional): Response format (json or csv)
            
        Returns:
            dict: Balance sheet data
        """
        try:
            params = {
                "identifier": identifier,
                "period": period,
                "format": format
            }
            
            data = self._make_request("balance-sheet", params, cache_duration=86400)  # Cache for 24 hours
            
            return {
                "symbol": identifier,
                "period": period,
                "data": data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving balance sheet for {identifier}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_cash_flow(self, identifier, period="annual", format="json"):
        """
        Get cash flow statement data for a specific company.
        
        Args:
            identifier (str): Stock ticker symbol
            period (str, optional): Period type (annual or quarterly)
            format (str, optional): Response format (json or csv)
            
        Returns:
            dict: Cash flow statement data
        """
        try:
            params = {
                "identifier": identifier,
                "period": period,
                "format": format
            }
            
            data = self._make_request("cash-flow", params, cache_duration=86400)  # Cache for 24 hours
            
            return {
                "symbol": identifier,
                "period": period,
                "data": data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving cash flow statement for {identifier}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_financial_ratios(self, identifier, format="json"):
        """
        Get financial ratios for a specific company.
        
        Args:
            identifier (str): Stock ticker symbol
            format (str, optional): Response format (json or csv)
            
        Returns:
            dict: Financial ratios data
        """
        try:
            params = {
                "identifier": identifier,
                "format": format
            }
            
            data = self._make_request("financial-ratios", params, cache_duration=86400)  # Cache for 24 hours
            
            return {
                "symbol": identifier,
                "data": data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving financial ratios for {identifier}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_insider_trading(self, identifier, offset=0, format="json"):
        """
        Get insider trading data for a specific company.
        
        Args:
            identifier (str): Stock ticker symbol
            offset (int, optional): Number of records to skip
            format (str, optional): Response format (json or csv)
            
        Returns:
            dict: Insider trading data
        """
        try:
            params = {
                "identifier": identifier,
                "offset": offset,
                "format": format
            }
            
            data = self._make_request("insider-trading", params)
            
            return {
                "symbol": identifier,
                "data": data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving insider trading data for {identifier}: {e}")
            return {"success": False, "error": str(e)}
