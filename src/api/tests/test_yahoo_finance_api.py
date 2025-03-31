"""
Unit tests for the Yahoo Finance API integration.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import pandas as pd
from datetime import datetime

# Import the API class
from src.api.yahoo_finance_api import YahooFinanceAPI

class TestYahooFinanceAPI(unittest.TestCase):
    """Test cases for the Yahoo Finance API integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = YahooFinanceAPI()
    
    @patch('src.api.yahoo_finance_api.ApiClient')
    def test_get_stock_chart(self, mock_api_client):
        """Test getting stock chart data."""
        # Mock response data
        mock_data = {
            "chart": {
                "result": [
                    {
                        "meta": {
                            "currency": "USD",
                            "symbol": "AAPL",
                            "exchangeName": "NMS",
                            "regularMarketPrice": 175.50
                        },
                        "timestamp": [1609459200, 1609545600],
                        "indicators": {
                            "quote": [
                                {
                                    "open": [170.0, 172.5],
                                    "high": [175.0, 176.0],
                                    "low": [169.0, 171.0],
                                    "close": [172.0, 175.5],
                                    "volume": [25000000, 30000000]
                                }
                            ],
                            "adjclose": [
                                {
                                    "adjclose": [172.0, 175.5]
                                }
                            ]
                        }
                    }
                ],
                "error": None
            }
        }
        
        # Configure the mock
        mock_client_instance = MagicMock()
        mock_client_instance.call_api.return_value = mock_data
        mock_api_client.return_value = mock_client_instance
        
        # Call the method
        result = self.api.get_stock_chart("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(len(result["time_series"]), 2)
        
        # Verify the API call
        mock_client_instance.call_api.assert_called_once_with(
            "YahooFinance/get_stock_chart", 
            query={
                "symbol": "AAPL",
                "region": "US",
                "interval": "1mo",
                "range": "1mo",
                "includeAdjustedClose": True
            }
        )
    
    @patch('src.api.yahoo_finance_api.ApiClient')
    def test_get_stock_holders(self, mock_api_client):
        """Test getting stock holders data."""
        # Mock response data
        mock_data = {
            "quoteSummary": {
                "result": [
                    {
                        "insiderHolders": {
                            "holders": [
                                {
                                    "name": "John Doe",
                                    "relation": "CEO",
                                    "url": "https://example.com",
                                    "transactionDescription": "Sale",
                                    "latestTransDate": {
                                        "fmt": "2023-12-01"
                                    },
                                    "positionDirect": {
                                        "fmt": "100,000"
                                    }
                                }
                            ]
                        }
                    }
                ],
                "error": None
            }
        }
        
        # Configure the mock
        mock_client_instance = MagicMock()
        mock_client_instance.call_api.return_value = mock_data
        mock_api_client.return_value = mock_client_instance
        
        # Call the method
        result = self.api.get_stock_holders("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(len(result["insiders"]), 1)
        self.assertEqual(result["insiders"][0]["name"], "John Doe")
        
        # Verify the API call
        mock_client_instance.call_api.assert_called_once_with(
            "YahooFinance/get_stock_holders", 
            query={
                "symbol": "AAPL",
                "region": "US"
            }
        )
    
    @patch('src.api.yahoo_finance_api.ApiClient')
    def test_get_stock_insights(self, mock_api_client):
        """Test getting stock insights data."""
        # Mock response data
        mock_data = {
            "finance": {
                "result": {
                    "instrumentInfo": {
                        "technicalEvents": {
                            "provider": "Trading Central",
                            "sector": "Technology",
                            "shortTermOutlook": {
                                "direction": "up",
                                "score": 7,
                                "scoreDescription": "Bullish"
                            }
                        }
                    },
                    "companySnapshot": {
                        "company": {
                            "innovativeness": 8,
                            "hiring": 7,
                            "sustainability": 6
                        },
                        "sector": {
                            "innovativeness": 7,
                            "hiring": 6,
                            "sustainability": 5
                        }
                    }
                }
            }
        }
        
        # Configure the mock
        mock_client_instance = MagicMock()
        mock_client_instance.call_api.return_value = mock_data
        mock_api_client.return_value = mock_client_instance
        
        # Call the method
        result = self.api.get_stock_insights("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["technical_events"]["provider"], "Trading Central")
        self.assertEqual(result["company_metrics"]["innovativeness"], 8)
        
        # Verify the API call
        mock_client_instance.call_api.assert_called_once_with(
            "YahooFinance/get_stock_insights", 
            query={
                "symbol": "AAPL"
            }
        )
    
    @patch('src.api.yahoo_finance_api.ApiClient')
    def test_get_stock_sec_filing(self, mock_api_client):
        """Test getting SEC filing data."""
        # Mock response data
        mock_data = {
            "quoteSummary": {
                "result": [
                    {
                        "secFilings": {
                            "filings": [
                                {
                                    "date": "2023-12-01",
                                    "type": "10-K",
                                    "title": "Annual Report",
                                    "edgarUrl": "https://example.com/10k",
                                    "exhibits": [
                                        {
                                            "type": "EX-101",
                                            "url": "https://example.com/ex101"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ],
                "error": None
            }
        }
        
        # Configure the mock
        mock_client_instance = MagicMock()
        mock_client_instance.call_api.return_value = mock_data
        mock_api_client.return_value = mock_client_instance
        
        # Call the method
        result = self.api.get_stock_sec_filing("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(len(result["filings"]), 1)
        self.assertEqual(result["filings"][0]["type"], "10-K")
        
        # Verify the API call
        mock_client_instance.call_api.assert_called_once_with(
            "YahooFinance/get_stock_sec_filing", 
            query={
                "symbol": "AAPL",
                "region": "US"
            }
        )
    
    @patch('src.api.yahoo_finance_api.ApiClient')
    def test_get_stock_analyst_opinions(self, mock_api_client):
        """Test getting analyst opinions data."""
        # Mock response data
        mock_data = {
            "result": [
                {
                    "hits": [
                        {
                            "report_title": "Apple Q4 Analysis",
                            "provider": "Example Research",
                            "author": "Jane Smith",
                            "report_type": "Earnings",
                            "abstract": "Analysis of Apple's Q4 results",
                            "report_date": 1640995200,
                            "pdf_url": "https://example.com/report.pdf",
                            "snapshot_url": "https://example.com/snapshot"
                        }
                    ]
                }
            ]
        }
        
        # Configure the mock
        mock_client_instance = MagicMock()
        mock_client_instance.call_api.return_value = mock_data
        mock_api_client.return_value = mock_client_instance
        
        # Call the method
        result = self.api.get_stock_analyst_opinions("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(len(result["reports"]), 1)
        self.assertEqual(result["reports"][0]["title"], "Apple Q4 Analysis")
        
        # Verify the API call
        mock_client_instance.call_api.assert_called_once_with(
            "YahooFinance/get_stock_what_analyst_are_saying", 
            query={
                "symbol": "AAPL",
                "region": "US"
            }
        )
    
    @patch('src.api.yahoo_finance_api.ApiClient')
    def test_caching_mechanism(self, mock_api_client):
        """Test the caching mechanism."""
        # Mock response data
        mock_data = {
            "chart": {
                "result": [
                    {
                        "meta": {"symbol": "AAPL"},
                        "timestamp": [1609459200],
                        "indicators": {
                            "quote": [{"close": [172.0]}]
                        }
                    }
                ],
                "error": None
            }
        }
        
        # Configure the mock
        mock_client_instance = MagicMock()
        mock_client_instance.call_api.return_value = mock_data
        mock_api_client.return_value = mock_client_instance
        
        # First call should make an API request
        self.api.get_stock_chart("AAPL")
        self.assertEqual(mock_client_instance.call_api.call_count, 1)
        
        # Second call should use cache
        self.api.get_stock_chart("AAPL")
        self.assertEqual(mock_client_instance.call_api.call_count, 1)  # Still 1, not 2

if __name__ == '__main__':
    unittest.main()
