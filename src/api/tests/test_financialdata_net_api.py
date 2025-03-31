"""
Unit tests for the Financial Data Net API integration.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import pandas as pd
from datetime import datetime

# Import the API class
from src.api.financialdata_net_api import FinancialdataNetAPI

class TestFinancialdataNetAPI(unittest.TestCase):
    """Test cases for the Financial Data Net API integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = FinancialdataNetAPI()
        # Mock the API key
        self.api.api_key = "test_api_key"
    
    @patch('requests.get')
    def test_get_stock_symbols(self, mock_get):
        """Test getting stock symbols."""
        # Mock response data
        mock_data = [
            {"trading_symbol": "AAPL", "registrant_name": "APPLE INC."},
            {"trading_symbol": "MSFT", "registrant_name": "MICROSOFT CORP"}
        ]
        
        # Configure the mock
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.api.get_stock_symbols()
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbols"], mock_data)
        mock_get.assert_called_once()
        
        # Verify the URL and parameters
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://financialdata.net/api/v1/stock-symbols")
        self.assertEqual(kwargs["params"]["key"], "test_api_key")
        self.assertEqual(kwargs["params"]["offset"], 0)
        self.assertEqual(kwargs["params"]["format"], "json")
    
    @patch('requests.get')
    def test_get_stock_prices(self, mock_get):
        """Test getting stock prices."""
        # Mock response data
        mock_data = [
            {
                "trading_symbol": "AAPL",
                "date": "2024-12-01",
                "open": "150.00",
                "high": "155.00",
                "low": "149.00",
                "close": "153.00",
                "volume": "10000000"
            },
            {
                "trading_symbol": "AAPL",
                "date": "2024-12-02",
                "open": "153.00",
                "high": "158.00",
                "low": "152.00",
                "close": "157.00",
                "volume": "12000000"
            }
        ]
        
        # Configure the mock
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.api.get_stock_prices("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(len(result["data"]), 2)
        
        # Verify the URL and parameters
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://financialdata.net/api/v1/stock-prices")
        self.assertEqual(kwargs["params"]["key"], "test_api_key")
        self.assertEqual(kwargs["params"]["identifier"], "AAPL")
    
    @patch('requests.get')
    def test_get_income_statement(self, mock_get):
        """Test getting income statement."""
        # Mock response data
        mock_data = [
            {
                "symbol": "AAPL",
                "fiscal_year": "2023",
                "fiscal_period": "FY",
                "revenue": "394328000000",
                "cost_of_revenue": "223546000000",
                "gross_profit": "170782000000",
                "net_income": "96995000000"
            }
        ]
        
        # Configure the mock
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.api.get_income_statement("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["period"], "annual")
        self.assertEqual(result["data"], mock_data)
        
        # Verify the URL and parameters
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://financialdata.net/api/v1/income-statement")
        self.assertEqual(kwargs["params"]["key"], "test_api_key")
        self.assertEqual(kwargs["params"]["identifier"], "AAPL")
        self.assertEqual(kwargs["params"]["period"], "annual")
    
    @patch('requests.get')
    def test_get_balance_sheet(self, mock_get):
        """Test getting balance sheet."""
        # Mock response data
        mock_data = [
            {
                "symbol": "AAPL",
                "fiscal_year": "2023",
                "fiscal_period": "FY",
                "total_assets": "352755000000",
                "total_liabilities": "290815000000",
                "total_equity": "61940000000"
            }
        ]
        
        # Configure the mock
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.api.get_balance_sheet("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["data"], mock_data)
        
        # Verify the URL and parameters
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://financialdata.net/api/v1/balance-sheet")
        self.assertEqual(kwargs["params"]["key"], "test_api_key")
        self.assertEqual(kwargs["params"]["identifier"], "AAPL")
    
    @patch('requests.get')
    def test_request_error_handling(self, mock_get):
        """Test error handling in API requests."""
        # Configure the mock to raise an exception
        mock_get.side_effect = Exception("API request failed")
        
        # Call the method
        result = self.api.get_stock_symbols()
        
        # Assertions
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "API request failed")
    
    @patch('requests.get')
    def test_caching_mechanism(self, mock_get):
        """Test the caching mechanism."""
        # Mock response data
        mock_data = [
            {"trading_symbol": "AAPL", "registrant_name": "APPLE INC."}
        ]
        
        # Configure the mock
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # First call should make a request
        self.api.get_stock_symbols()
        self.assertEqual(mock_get.call_count, 1)
        
        # Second call should use cache
        self.api.get_stock_symbols()
        self.assertEqual(mock_get.call_count, 1)  # Still 1, not 2

if __name__ == '__main__':
    unittest.main()
