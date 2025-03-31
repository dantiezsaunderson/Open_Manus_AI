import unittest
import os
import sys
import json
from unittest.mock import MagicMock, patch
import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import modules to test
from api.financialdata_net_api import FinancialDataNetAPI
from api.yahoo_finance_api import YahooFinanceAPI
from modules.enhanced_financial_analysis import EnhancedFinancialAnalysis
from modules.enhanced_multi_agent import EnhancedMultiAgentSystem, EnhancedAgent
from core.enhanced_memory_manager import EnhancedMemoryManager
from modules.enhanced_conversation import EnhancedConversationModule

class TestFinancialDataNetAPI(unittest.TestCase):
    """Test cases for the FinancialData.net API integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.api = FinancialDataNetAPI(api_key="test_key")
    
    @patch('api.financialdata_net_api.requests.get')
    def test_get_stock_price(self, mock_get):
        """Test getting stock price data."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "AAPL",
            "price": 150.25,
            "change": 2.5,
            "change_percent": 1.69,
            "volume": 75000000
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.api.get_stock_price("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["price"], 150.25)
        self.assertEqual(result["change"], 2.5)
        self.assertEqual(result["change_percent"], 1.69)
    
    @patch('api.financialdata_net_api.requests.get')
    def test_get_financial_statements(self, mock_get):
        """Test getting financial statements."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "AAPL",
            "statements": [
                {
                    "date": "2023-12-31",
                    "revenue": 120000000000,
                    "net_income": 30000000000,
                    "eps": 1.88
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.api.get_financial_statements("AAPL", "income", "annual")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(len(result["statements"]), 1)
        self.assertEqual(result["statements"][0]["revenue"], 120000000000)
    
    @patch('api.financialdata_net_api.requests.get')
    def test_get_financial_ratios(self, mock_get):
        """Test getting financial ratios."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "symbol": "AAPL",
            "ratios": {
                "pe_ratio": 25.6,
                "price_to_book": 35.2,
                "debt_to_equity": 1.5,
                "return_on_equity": 0.85
            }
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.api.get_financial_ratios("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["ratios"]["pe_ratio"], 25.6)
        self.assertEqual(result["ratios"]["price_to_book"], 35.2)
    
    @patch('api.financialdata_net_api.requests.get')
    def test_api_error_handling(self, mock_get):
        """Test API error handling."""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid API key"}
        mock_get.return_value = mock_response
        
        # Call method
        result = self.api.get_stock_price("AAPL")
        
        # Assertions
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "API Error: 401 - Invalid API key")


class TestYahooFinanceAPI(unittest.TestCase):
    """Test cases for the Yahoo Finance API integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.api = YahooFinanceAPI()
    
    @patch('api.yahoo_finance_api.ApiClient')
    def test_get_stock_chart(self, mock_api_client):
        """Test getting stock chart data."""
        # Mock response
        mock_client = MagicMock()
        mock_api_client.return_value = mock_client
        
        mock_response = {
            "chart": {
                "result": [
                    {
                        "meta": {
                            "symbol": "AAPL",
                            "currency": "USD",
                            "regularMarketPrice": 150.25
                        },
                        "timestamp": [1617000000, 1617086400],
                        "indicators": {
                            "quote": [
                                {
                                    "open": [145.0, 147.5],
                                    "close": [147.5, 150.25],
                                    "high": [148.0, 151.0],
                                    "low": [144.5, 147.0],
                                    "volume": [75000000, 80000000]
                                }
                            ]
                        }
                    }
                ]
            }
        }
        mock_client.call_api.return_value = mock_response
        
        # Call method
        result = self.api.get_stock_chart("AAPL", interval="1d", range="1mo")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["meta"]["currency"], "USD")
        self.assertEqual(len(result["data"]), 2)
    
    @patch('api.yahoo_finance_api.ApiClient')
    def test_get_stock_holders(self, mock_api_client):
        """Test getting stock holders data."""
        # Mock response
        mock_client = MagicMock()
        mock_api_client.return_value = mock_client
        
        mock_response = {
            "quoteSummary": {
                "result": [
                    {
                        "insiderHolders": {
                            "holders": [
                                {
                                    "name": "Tim Cook",
                                    "relation": "CEO",
                                    "positionDirect": {
                                        "raw": 100000
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
        mock_client.call_api.return_value = mock_response
        
        # Call method
        result = self.api.get_stock_holders("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(len(result["holders"]), 1)
        self.assertEqual(result["holders"][0]["name"], "Tim Cook")
    
    @patch('api.yahoo_finance_api.ApiClient')
    def test_get_stock_insights(self, mock_api_client):
        """Test getting stock insights."""
        # Mock response
        mock_client = MagicMock()
        mock_api_client.return_value = mock_client
        
        mock_response = {
            "finance": {
                "result": {
                    "symbol": "AAPL",
                    "instrumentInfo": {
                        "technicalEvents": {
                            "shortTermOutlook": {
                                "direction": "up",
                                "score": 0.8
                            }
                        }
                    }
                }
            }
        }
        mock_client.call_api.return_value = mock_response
        
        # Call method
        result = self.api.get_stock_insights("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["insights"]["technicalEvents"]["shortTermOutlook"]["direction"], "up")
    
    @patch('api.yahoo_finance_api.ApiClient')
    def test_api_error_handling(self, mock_api_client):
        """Test API error handling."""
        # Mock client that raises an exception
        mock_client = MagicMock()
        mock_api_client.return_value = mock_client
        mock_client.call_api.side_effect = Exception("API Error")
        
        # Call method
        result = self.api.get_stock_chart("AAPL")
        
        # Assertions
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "API Error")


class TestEnhancedFinancialAnalysis(unittest.TestCase):
    """Test cases for the Enhanced Financial Analysis module."""
    
    def setUp(self):
        """Set up test environment."""
        self.financialdata_api = MagicMock()
        self.yahoo_finance_api = MagicMock()
        self.financial_analysis = EnhancedFinancialAnalysis(
            financialdata_api=self.financialdata_api,
            yahoo_finance_api=self.yahoo_finance_api
        )
    
    def test_get_stock_data(self):
        """Test getting stock data."""
        # Mock API responses
        self.financialdata_api.get_stock_price.return_value = {
            "success": True,
            "symbol": "AAPL",
            "price": 150.25,
            "change": 2.5,
            "change_percent": 1.69
        }
        
        self.yahoo_finance_api.get_stock_chart.return_value = {
            "success": True,
            "symbol": "AAPL",
            "meta": {"currency": "USD"},
            "data": [
                {"timestamp": 1617000000, "open": 145.0, "close": 147.5},
                {"timestamp": 1617086400, "open": 147.5, "close": 150.25}
            ]
        }
        
        # Call method
        result = self.financial_analysis.get_stock_data("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["stats"]["latest_price"], 150.25)
        self.assertEqual(result["stats"]["price_change"], 2.5)
        self.assertEqual(result["stats"]["price_change_pct"], 1.69)
    
    def test_analyze_stock(self):
        """Test analyzing a stock."""
        # Mock API responses
        self.financialdata_api.get_stock_price.return_value = {
            "success": True,
            "symbol": "AAPL",
            "price": 150.25,
            "change": 2.5,
            "change_percent": 1.69
        }
        
        self.financialdata_api.get_financial_ratios.return_value = {
            "success": True,
            "symbol": "AAPL",
            "ratios": {
                "pe_ratio": 25.6,
                "price_to_book": 35.2
            }
        }
        
        self.yahoo_finance_api.get_stock_chart.return_value = {
            "success": True,
            "symbol": "AAPL",
            "meta": {"currency": "USD"},
            "data": [
                {"timestamp": 1617000000, "open": 145.0, "close": 147.5},
                {"timestamp": 1617086400, "open": 147.5, "close": 150.25}
            ]
        }
        
        self.yahoo_finance_api.get_stock_insights.return_value = {
            "success": True,
            "symbol": "AAPL",
            "insights": {
                "technicalEvents": {
                    "shortTermOutlook": {
                        "direction": "up",
                        "score": 0.8
                    }
                }
            }
        }
        
        # Call method
        result = self.financial_analysis.analyze_stock("AAPL")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["symbol"], "AAPL")
        self.assertIn("company_info", result)
        self.assertIn("performance", result)
        self.assertIn("technical_indicators", result)
        self.assertIn("fundamentals", result)
    
    def test_analyze_portfolio(self):
        """Test analyzing a portfolio."""
        # Mock portfolio
        portfolio = [
            {"symbol": "AAPL", "shares": 10, "cost_basis": 140.0},
            {"symbol": "MSFT", "shares": 5, "cost_basis": 250.0}
        ]
        
        # Mock API responses
        self.financialdata_api.get_stock_price.side_effect = [
            {
                "success": True,
                "symbol": "AAPL",
                "price": 150.25,
                "change": 2.5,
                "change_percent": 1.69
            },
            {
                "success": True,
                "symbol": "MSFT",
                "price": 280.50,
                "change": 5.0,
                "change_percent": 1.82
            }
        ]
        
        # Call method
        result = self.financial_analysis.analyze_portfolio(portfolio)
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(len(result["holdings"]), 2)
        self.assertGreater(result["total_value"], 0)
        self.assertGreater(result["total_cost"], 0)
        self.assertEqual(result["holdings"][0]["symbol"], "AAPL")
        self.assertEqual(result["holdings"][0]["shares"], 10)
        self.assertEqual(result["holdings"][0]["cost_basis"], 140.0)
        self.assertEqual(result["holdings"][0]["latest_price"], 150.25)
    
    def test_generate_stock_chart(self):
        """Test generating a stock chart."""
        # Mock API response
        self.yahoo_finance_api.get_stock_chart.return_value = {
            "success": True,
            "symbol": "AAPL",
            "meta": {"currency": "USD"},
            "data": [
                {"timestamp": 1617000000, "open": 145.0, "close": 147.5, "high": 148.0, "low": 144.5, "volume": 75000000},
                {"timestamp": 1617086400, "open": 147.5, "close": 150.25, "high": 151.0, "low": 147.0, "volume": 80000000}
            ]
        }
        
        # Mock matplotlib and save_fig
        with patch('modules.enhanced_financial_analysis.plt') as mock_plt:
            mock_plt.figure.return_value = MagicMock()
            mock_plt.savefig.return_value = None
            
            # Call method
            result = self.financial_analysis.generate_stock_chart("AAPL", period="1mo")
            
            # Assertions
            self.assertTrue(result["success"])
            self.assertEqual(result["symbol"], "AAPL")
            self.assertIn("filepath", result)


class TestEnhancedMultiAgentSystem(unittest.TestCase):
    """Test cases for the Enhanced Multi-Agent System."""
    
    def setUp(self):
        """Set up test environment."""
        self.ai_engine = MagicMock()
        self.memory_manager = MagicMock()
        self.financial_analysis = MagicMock()
        
        self.multi_agent_system = EnhancedMultiAgentSystem(
            ai_engine=self.ai_engine,
            memory_manager=self.memory_manager,
            financial_analysis=self.financial_analysis
        )
    
    def test_agent_creation(self):
        """Test agent creation."""
        # Create agents
        self.multi_agent_system.create_agent("research", "ResearchAgent")
        self.multi_agent_system.create_agent("coding", "CodingAgent")
        self.multi_agent_system.create_agent("financial", "FinancialAgent")
        
        # Assertions
        self.assertEqual(len(self.multi_agent_system.agents), 3)
        self.assertIn("research", self.multi_agent_system.agents)
        self.assertIn("coding", self.multi_agent_system.agents)
        self.assertIn("financial", self.multi_agent_system.agents)
    
    def test_task_assignment(self):
        """Test task assignment."""
        # Create agents
        self.multi_agent_system.create_agent("research", "ResearchAgent")
        
        # Mock agent process_task method
        self.multi_agent_system.agents["research"].process_task = MagicMock()
        
        # Create task
        task_params = {
            "task_type": "research",
            "query": "Test query"
        }
        
        # Assign task
        task_id = self.multi_agent_system.assign_task(task_params, agent_type="research")
        
        # Assertions
        self.assertIsNotNone(task_id)
        self.assertIn(task_id, self.multi_agent_system.tasks)
        self.assertEqual(self.multi_agent_system.tasks[task_id]["status"], "assigned")
        self.assertEqual(self.multi_agent_system.tasks[task_id]["agent_type"], "research")
    
    def test_get_task_result(self):
        """Test getting task results."""
        # Create task
        task_id = "test_task_id"
        self.multi_agent_system.tasks[task_id] = {
            "id": task_id,
            "status": "completed",
            "agent_type": "research",
            "params": {"query": "Test query"},
            "result": {"summary": "Test result"},
            "created_at": "2023-01-01T00:00:00",
            "completed_at": "2023-01-01T00:01:00"
        }
        
        # Get result
        result = self.multi_agent_system.get_task_result(task_id)
        
        # Assertions
        self.assertEqual(result["id"], task_id)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["result"]["summary"], "Test result")
    
    def test_get_system_status(self):
        """Test getting system status."""
        # Create agents
        self.multi_agent_system.create_agent("research", "ResearchAgent")
        self.multi_agent_system.create_agent("coding", "CodingAgent")
        
        # Create tasks
        self.multi_agent_system.tasks["task1"] = {
            "id": "task1",
            "status": "processing",
            "agent_type": "research"
        }
        self.multi_agent_system.tasks["task2"] = {
            "id": "task2",
            "status": "completed",
            "agent_type": "coding"
        }
        
        # Get status
        status = self.multi_agent_system.get_system_status()
        
        # Assertions
        self.assertEqual(status["agent_count"], 2)
        self.assertEqual(status["active_tasks"], 1)
        self.assertEqual(len(status["agents"]), 2)


class TestEnhancedMemoryManager(unittest.TestCase):
    """Test cases for the Enhanced Memory Manager."""
    
    def setUp(self):
        """Set up test environment."""
        # Use in-memory SQLite for testing
        self.memory_manager = EnhancedMemoryManager(storage_dir=":memory:")
        
        # Mock the database initialization
        self.memory_manager.init_database = MagicMock()
        
        # Create a mock connection and cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        
        # Mock sqlite3.connect to return our mock connection
        with patch('sqlite3.connect', return_value=self.mock_conn):
            self.memory_manager.init_database()
    
    def test_create_user(self):
        """Test creating a user."""
        # Mock cursor.execute and conn.commit
        self.mock_cursor.execute = MagicMock()
        self.mock_conn.commit = MagicMock()
        
        # Mock sqlite3.connect to return our mock connection
        with patch('sqlite3.connect', return_value=self.mock_conn):
            user_id = self.memory_manager.create_user("Test User")
        
        # Assertions
        self.assertIsNotNone(user_id)
        self.mock_cursor.execute.assert_called()
        self.mock_conn.commit.assert_called()
    
    def test_get_user(self):
        """Test getting a user."""
        # Mock cursor.execute and cursor.fetchone
        self.mock_cursor.execute = MagicMock()
        self.mock_cursor.fetchone.return_value = ("user123", "Test User", "2023-01-01T00:00:00", "2023-01-01T00:00:00", None)
        
        # Mock sqlite3.connect to return our mock connection
        with patch('sqlite3.connect', return_value=self.mock_conn):
            user = self.memory_manager.get_user("user123")
        
        # Assertions
        self.assertIsNotNone(user)
        self.assertEqual(user["user_id"], "user123")
        self.assertEqual(user["name"], "Test User")
        self.mock_cursor.execute.assert_called()
    
    def test_add_message(self):
        """Test adding a message."""
        # Mock cursor.execute and conn.commit
        self.mock_cursor.execute = MagicMock()
        self.mock_conn.commit = MagicMock()
        
        # Mock sqlite3.connect to return our mock connection
        with patch('sqlite3.connect', return_value=self.mock_conn):
            message_id = self.memory_manager.add_message("conv123", "user123", "user", "Test message")
        
        # Assertions
        self.assertIsNotNone(message_id)
        self.mock_cursor.execute.assert_called()
        self.mock_conn.commit.assert_called()
    
    def test_set_preference(self):
        """Test setting a preference."""
        # Mock cursor.execute, cursor.fetchone, and conn.commit
        self.mock_cursor.execute = MagicMock()
        self.mock_cursor.fetchone = MagicMock(return_value=None)
        self.mock_conn.commit = MagicMock()
        
        # Mock sqlite3.connect to return our mock connection
        with patch('sqlite3.connect', return_value=self.mock_conn):
            result = self.memory_manager.set_preference("user123", "test_category", "test_key", "test_value")
        
        # Assertions
        self.assertTrue(result)
        self.mock_cursor.execute.assert_called()
        self.mock_conn.commit.assert_called()
    
    def test_get_preference(self):
        """Test getting a preference."""
        # Mock cursor.execute and cursor.fetchone
        self.mock_cursor.execute = MagicMock()
        self.mock_cursor.fetchone.return_value = ('{"value": "test_value"}',)
        
        # Mock sqlite3.connect to return our mock connection
        with patch('sqlite3.connect', return_value=self.mock_conn):
            value = self.memory_manager.get_preference("user123", "test_category", "test_key", "default_value")
        
        # Assertions
        self.assertEqual(value, {"value": "test_value"})
        self.mock_cursor.execute.assert_called()


class TestEnhancedConversationModule(unittest.TestCase):
    """Test cases for the Enhanced Conversation Module."""
    
    def setUp(self):
        """Set up test environment."""
        self.ai_engine = MagicMock()
        self.memory_manager = MagicMock()
        
        self.conversation_module = EnhancedConversationModule(
            ai_engine=self.ai_engine,
            memory_manager=self.memory_manager
        )
    
    def test_start_conversation(self):
        """Test starting a conversation."""
        # Mock memory_manager.create_conversation
        self.memory_manager.create_conversation.return_value = "conv123"
        
        # Start conversation
        result = self.conversation_module.start_conversation("user123")
        
        # Assertions
        self.assertEqual(result["conversation_id"], "conv123")
        self.assertEqual(result["user_id"], "user123")
        self.memory_manager.create_conversation.assert_called_with("user123")
    
    def test_process_message(self):
        """Test processing a message."""
        # Set up conversation context
        self.conversation_module.conversation_contexts["conv123"] = {
            "user_id": "user123",
            "start_time": "2023-01-01T00:00:00",
            "last_update_time": "2023-01-01T00:00:00",
            "topics": [],
            "entities": {},
            "sentiment": "neutral",
            "message_count": 0
        }
        
        # Mock memory_manager.add_message and memory_manager.get_context
        self.memory_manager.add_message.return_value = "msg123"
        self.memory_manager.get_context.return_value = {
            "user": {"user_id": "user123", "name": "Test User"},
            "preferences": {},
            "recent_messages": [],
            "relevant_facts": []
        }
        
        # Mock ai_engine.generate_response
        self.ai_engine.generate_response.return_value = "Test response"
        
        # Process message
        result = self.conversation_module.process_message("conv123", "Test message")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["conversation_id"], "conv123")
        self.assertEqual(result["user_id"], "user123")
        self.assertEqual(result["response"], "Test response")
        self.memory_manager.add_message.assert_called_with("conv123", "user123", "user", "Test message")
        self.ai_engine.generate_response.assert_called()
    
    def test_analyze_message(self):
        """Test analyzing a message."""
        # Set up conversation context
        self.conversation_module.conversation_contexts["conv123"] = {
            "user_id": "user123",
            "start_time": "2023-01-01T00:00:00",
            "last_update_time": "2023-01-01T00:00:00",
            "topics": [],
            "entities": {},
            "sentiment": "neutral",
            "message_count": 0
        }
        
        # Analyze message
        self.conversation_module._analyze_message("conv123", "I am happy with the excellent service provided by Apple Inc.")
        
        # Get updated context
        context = self.conversation_module.conversation_contexts["conv123"]
        
        # Assertions
        self.assertIn("happy", context["topics"])
        self.assertIn("excellent", context["topics"])
        self.assertIn("service", context["topics"])
        self.assertEqual(context["sentiment"], "positive")
        self.assertIn("Apple", context["entities"])
    
    def test_end_conversation(self):
        """Test ending a conversation."""
        # Set up conversation context
        self.conversation_module.conversation_contexts["conv123"] = {
            "user_id": "user123",
            "start_time": "2023-01-01T00:00:00",
            "last_update_time": "2023-01-01T00:00:00",
            "topics": ["topic1", "topic2"],
            "entities": {"Entity1": 1},
            "sentiment": "positive",
            "message_count": 5
        }
        
        # Add to active conversations
        self.conversation_module.active_conversations["conv123"] = {
            "user_id": "user123",
            "start_time": "2023-01-01T00:00:00",
            "last_update_time": "2023-01-01T00:00:00",
            "message_count": 5
        }
        
        # Mock memory_manager.summarize_conversation
        self.memory_manager.summarize_conversation.return_value = "Test summary"
        
        # End conversation
        result = self.conversation_module.end_conversation("conv123")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["conversation_id"], "conv123")
        self.assertEqual(result["user_id"], "user123")
        self.assertEqual(result["message_count"], 5)
        self.assertEqual(result["summary"], "Test summary")
        self.assertNotIn("conv123", self.conversation_module.active_conversations)
        self.memory_manager.summarize_conversation.assert_called_with("conv123", self.ai_engine)


if __name__ == '__main__':
    unittest.main()
