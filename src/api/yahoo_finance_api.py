"""
Yahoo Finance API Integration Module

This module provides integration with Yahoo Finance API for accessing
comprehensive stock market data, insider trading information, technical indicators,
SEC filings, and analyst opinions.
"""

import os
import logging
import json
import pandas as pd
from datetime import datetime, timedelta
import sys
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Add path for data API access
sys.path.append('/opt/.manus/.sandbox-runtime')
try:
    from data_api import ApiClient
    logger.info("Successfully imported data_api module")
except ImportError as e:
    logger.warning(f"Could not import data_api module: {e}")
    # Create a mock ApiClient for development/testing environments
    class ApiClient:
        def call_api(self, api_name, query=None):
            logger.warning(f"Mock API call to {api_name} with query {query}")
            return {"error": "This is a mock response. Data API not available."}

class YahooFinanceAPI:
    """
    Yahoo Finance API integration for accessing comprehensive stock market data.
    """
    
    def __init__(self):
        """Initialize the Yahoo Finance API integration."""
        # Initialize API client
        self.client = ApiClient()
        logger.info("Yahoo Finance API integration initialized")
        
        # Initialize cache
        self.cache = {}
        self.cache_expiry = {}
    
    def _get_cached_data(self, cache_key, cache_duration=3600):
        """
        Get data from cache if available and not expired.
        
        Args:
            cache_key (str): Cache key
            cache_duration (int, optional): Cache duration in seconds
            
        Returns:
            tuple: (is_cached, cached_data)
        """
        current_time = datetime.now()
        if cache_key in self.cache and self.cache_expiry.get(cache_key, datetime.min) > current_time:
            logger.debug(f"Using cached data for {cache_key}")
            return True, self.cache[cache_key]
        return False, None
    
    def _set_cached_data(self, cache_key, data, cache_duration=3600):
        """
        Set data in cache with expiry.
        
        Args:
            cache_key (str): Cache key
            data (any): Data to cache
            cache_duration (int, optional): Cache duration in seconds
        """
        self.cache[cache_key] = data
        self.cache_expiry[cache_key] = datetime.now() + timedelta(seconds=cache_duration)
    
    def get_stock_chart(self, symbol, region="US", interval="1mo", range="1mo", include_adjusted_close=True):
        """
        Get comprehensive stock market data including meta information and time-series data.
        
        Args:
            symbol (str): Stock ticker symbol
            region (str, optional): Region code (US, BR, AU, CA, FR, DE, HK, IN, IT, ES, GB, SG)
            interval (str, optional): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
            range (str, optional): Time range (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            include_adjusted_close (bool, optional): Whether to include adjusted close data
            
        Returns:
            dict: Stock chart data
        """
        try:
            # Create cache key
            cache_key = f"stock_chart_{symbol}_{region}_{interval}_{range}"
            
            # Check cache
            is_cached, cached_data = self._get_cached_data(cache_key)
            if is_cached:
                return cached_data
            
            # Prepare query parameters
            query = {
                "symbol": symbol,
                "region": region,
                "interval": interval,
                "range": range,
                "includeAdjustedClose": include_adjusted_close
            }
            
            # Call the API
            response = self.client.call_api("YahooFinance/get_stock_chart", query=query)
            
            # Process the response
            if "error" in response and response["error"] is not None:
                logger.error(f"Error retrieving stock chart for {symbol}: {response['error']}")
                return {"success": False, "error": str(response["error"])}
            
            # Extract relevant data
            result = {
                "symbol": symbol,
                "success": True,
                "data": response
            }
            
            # Process time series data if available
            if "chart" in response and "result" in response["chart"] and response["chart"]["result"]:
                chart_data = response["chart"]["result"][0]
                
                # Extract metadata
                if "meta" in chart_data:
                    result["meta"] = chart_data["meta"]
                
                # Extract time series data
                if "timestamp" in chart_data and "indicators" in chart_data:
                    timestamps = chart_data["timestamp"]
                    indicators = chart_data["indicators"]
                    
                    # Create a DataFrame from time series data
                    time_series = []
                    
                    if "quote" in indicators and indicators["quote"]:
                        quote = indicators["quote"][0]
                        
                        for i, ts in enumerate(timestamps):
                            data_point = {
                                "timestamp": datetime.fromtimestamp(ts).isoformat(),
                                "open": quote.get("open", [])[i] if i < len(quote.get("open", [])) else None,
                                "high": quote.get("high", [])[i] if i < len(quote.get("high", [])) else None,
                                "low": quote.get("low", [])[i] if i < len(quote.get("low", [])) else None,
                                "close": quote.get("close", [])[i] if i < len(quote.get("close", [])) else None,
                                "volume": quote.get("volume", [])[i] if i < len(quote.get("volume", [])) else None
                            }
                            
                            # Add adjusted close if available
                            if "adjclose" in indicators and indicators["adjclose"]:
                                adjclose = indicators["adjclose"][0].get("adjclose", [])
                                if i < len(adjclose):
                                    data_point["adjclose"] = adjclose[i]
                            
                            time_series.append(data_point)
                    
                    result["time_series"] = time_series
            
            # Cache the result
            self._set_cached_data(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving stock chart for {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stock_holders(self, symbol, region="US"):
        """
        Get insider trading information including details about company insiders' holdings.
        
        Args:
            symbol (str): Stock ticker symbol
            region (str, optional): Region code
            
        Returns:
            dict: Stock holders data
        """
        try:
            # Create cache key
            cache_key = f"stock_holders_{symbol}_{region}"
            
            # Check cache
            is_cached, cached_data = self._get_cached_data(cache_key, cache_duration=86400)  # Cache for 24 hours
            if is_cached:
                return cached_data
            
            # Prepare query parameters
            query = {
                "symbol": symbol,
                "region": region
            }
            
            # Call the API
            response = self.client.call_api("YahooFinance/get_stock_holders", query=query)
            
            # Process the response
            if "error" in response and response["error"] is not None:
                logger.error(f"Error retrieving stock holders for {symbol}: {response['error']}")
                return {"success": False, "error": str(response["error"])}
            
            # Extract relevant data
            result = {
                "symbol": symbol,
                "success": True,
                "data": response
            }
            
            # Process holders data if available
            if ("quoteSummary" in response and "result" in response["quoteSummary"] and 
                response["quoteSummary"]["result"]):
                
                holders_data = response["quoteSummary"]["result"][0]
                
                if "insiderHolders" in holders_data and "holders" in holders_data["insiderHolders"]:
                    # Extract and format insider holders
                    insiders = []
                    
                    for holder in holders_data["insiderHolders"]["holders"]:
                        insider = {
                            "name": holder.get("name", ""),
                            "relation": holder.get("relation", ""),
                            "url": holder.get("url", ""),
                            "transaction_description": holder.get("transactionDescription", "")
                        }
                        
                        # Add date if available
                        if "latestTransDate" in holder and "fmt" in holder["latestTransDate"]:
                            insider["transaction_date"] = holder["latestTransDate"]["fmt"]
                        
                        # Add position if available
                        if "positionDirect" in holder and "fmt" in holder["positionDirect"]:
                            insider["position"] = holder["positionDirect"]["fmt"]
                        
                        insiders.append(insider)
                    
                    result["insiders"] = insiders
            
            # Cache the result
            self._set_cached_data(cache_key, result, cache_duration=86400)
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving stock holders for {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stock_insights(self, symbol):
        """
        Get comprehensive financial analysis data including technical indicators and company metrics.
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            dict: Stock insights data
        """
        try:
            # Create cache key
            cache_key = f"stock_insights_{symbol}"
            
            # Check cache
            is_cached, cached_data = self._get_cached_data(cache_key, cache_duration=43200)  # Cache for 12 hours
            if is_cached:
                return cached_data
            
            # Prepare query parameters
            query = {
                "symbol": symbol
            }
            
            # Call the API
            response = self.client.call_api("YahooFinance/get_stock_insights", query=query)
            
            # Process the response
            if "error" in response and response["error"] is not None:
                logger.error(f"Error retrieving stock insights for {symbol}: {response['error']}")
                return {"success": False, "error": str(response["error"])}
            
            # Extract relevant data
            result = {
                "symbol": symbol,
                "success": True,
                "data": response
            }
            
            # Process insights data if available
            if "finance" in response and "result" in response["finance"]:
                insights_data = response["finance"]["result"]
                
                # Extract technical events
                if ("instrumentInfo" in insights_data and 
                    "technicalEvents" in insights_data["instrumentInfo"]):
                    
                    tech_events = insights_data["instrumentInfo"]["technicalEvents"]
                    result["technical_events"] = {
                        "provider": tech_events.get("provider", ""),
                        "sector": tech_events.get("sector", "")
                    }
                    
                    # Extract outlook data
                    for outlook_type in ["shortTermOutlook", "intermediateTermOutlook", "longTermOutlook"]:
                        if outlook_type in tech_events:
                            outlook_key = outlook_type.replace("Outlook", "_outlook")
                            result["technical_events"][outlook_key] = {
                                "direction": tech_events[outlook_type].get("direction", ""),
                                "score": tech_events[outlook_type].get("score", 0),
                                "description": tech_events[outlook_type].get("scoreDescription", "")
                            }
                
                # Extract company snapshot
                if "companySnapshot" in insights_data:
                    snapshot = insights_data["companySnapshot"]
                    
                    if "company" in snapshot:
                        result["company_metrics"] = {
                            "innovativeness": snapshot["company"].get("innovativeness", 0),
                            "hiring": snapshot["company"].get("hiring", 0),
                            "sustainability": snapshot["company"].get("sustainability", 0),
                            "insider_sentiments": snapshot["company"].get("insiderSentiments", 0),
                            "earnings_reports": snapshot["company"].get("earningsReports", 0),
                            "dividends": snapshot["company"].get("dividends", 0)
                        }
                    
                    if "sector" in snapshot:
                        result["sector_metrics"] = {
                            "innovativeness": snapshot["sector"].get("innovativeness", 0),
                            "hiring": snapshot["sector"].get("hiring", 0),
                            "sustainability": snapshot["sector"].get("sustainability", 0),
                            "insider_sentiments": snapshot["sector"].get("insiderSentiments", 0),
                            "earnings_reports": snapshot["sector"].get("earningsReports", 0),
                            "dividends": snapshot["sector"].get("dividends", 0)
                        }
            
            # Cache the result
            self._set_cached_data(cache_key, result, cache_duration=43200)
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving stock insights for {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stock_sec_filing(self, symbol, region="US"):
        """
        Get a company's SEC filing history including filing dates, types, and titles.
        
        Args:
            symbol (str): Stock ticker symbol
            region (str, optional): Region code
            
        Returns:
            dict: SEC filing data
        """
        try:
            # Create cache key
            cache_key = f"stock_sec_filing_{symbol}_{region}"
            
            # Check cache
            is_cached, cached_data = self._get_cached_data(cache_key, cache_duration=86400)  # Cache for 24 hours
            if is_cached:
                return cached_data
            
            # Prepare query parameters
            query = {
                "symbol": symbol,
                "region": region
            }
            
            # Call the API
            response = self.client.call_api("YahooFinance/get_stock_sec_filing", query=query)
            
            # Process the response
            if "error" in response and response["error"] is not None:
                logger.error(f"Error retrieving SEC filings for {symbol}: {response['error']}")
                return {"success": False, "error": str(response["error"])}
            
            # Extract relevant data
            result = {
                "symbol": symbol,
                "success": True,
                "data": response
            }
            
            # Process SEC filing data if available
            if ("quoteSummary" in response and "result" in response["quoteSummary"] and 
                response["quoteSummary"]["result"]):
                
                filing_data = response["quoteSummary"]["result"][0]
                
                if "secFilings" in filing_data and "filings" in filing_data["secFilings"]:
                    # Extract and format SEC filings
                    filings = []
                    
                    for filing in filing_data["secFilings"]["filings"]:
                        filing_info = {
                            "date": filing.get("date", ""),
                            "type": filing.get("type", ""),
                            "title": filing.get("title", ""),
                            "edgar_url": filing.get("edgarUrl", "")
                        }
                        
                        # Add exhibits if available
                        if "exhibits" in filing:
                            filing_info["exhibits"] = [
                                {
                                    "type": exhibit.get("type", ""),
                                    "url": exhibit.get("url", "")
                                }
                                for exhibit in filing["exhibits"]
                            ]
                        
                        filings.append(filing_info)
                    
                    result["filings"] = filings
            
            # Cache the result
            self._set_cached_data(cache_key, result, cache_duration=86400)
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving SEC filings for {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stock_analyst_opinions(self, symbol, region="US"):
        """
        Get research report search results for a stock.
        
        Args:
            symbol (str): Stock ticker symbol
            region (str, optional): Region code
            
        Returns:
            dict: Analyst opinions data
        """
        try:
            # Create cache key
            cache_key = f"stock_analyst_opinions_{symbol}_{region}"
            
            # Check cache
            is_cached, cached_data = self._get_cached_data(cache_key, cache_duration=43200)  # Cache for 12 hours
            if is_cached:
                return cached_data
            
            # Prepare query parameters
            query = {
                "symbol": symbol,
                "region": region
            }
            
            # Call the API
            response = self.client.call_api("YahooFinance/get_stock_what_analyst_are_saying", query=query)
            
            # Process the response
            if "error" in response and response["error"] is not None:
                logger.error(f"Error retrieving analyst opinions for {symbol}: {response['error']}")
                return {"success": False, "error": str(response["error"])}
            
            # Extract relevant data
            result = {
                "symbol": symbol,
                "success": True,
                "data": response
            }
            
            # Process analyst opinions data if available
            if "result" in response:
                # Extract and format research reports
                reports = []
                
                for entity in response["result"]:
                    if "hits" in entity:
                        for hit in entity["hits"]:
                            report = {
                                "title": hit.get("report_title", ""),
                                "provider": hit.get("provider", ""),
                                "author": hit.get("author", ""),
                                "report_type": hit.get("report_type", ""),
                                "abstract": hit.get("abstract", "")
                            }
                            
                            # Add date if available
                            if "report_date" in hit:
                                try:
                                    report["date"] = datetime.fromtimestamp(hit["report_date"]).isoformat()
                                except:
                                    report["date"] = str(hit["report_date"])
                            
                            # Add URLs if available
                            if "pdf_url" in hit:
                                report["pdf_url"] = hit["pdf_url"]
                            if "snapshot_url" in hit:
                                report["snapshot_url"] = hit["snapshot_url"]
                            
                            reports.append(report)
                
                result["reports"] = reports
            
            # Cache the result
            self._set_cached_data(cache_key, result, cache_duration=43200)
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving analyst opinions for {symbol}: {e}")
            return {"success": False, "error": str(e)}
