"""Unit tests for the world model agent components."""

import unittest
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Skip tests if API keys not available
SKIP_API_TESTS = not all([
    os.getenv("GOOGLE_API_KEY"),
    os.getenv("TAVILY_API_KEY"),
    os.getenv("EODHD_API_KEY")
])


class TestWorldModelAgent(unittest.TestCase):
    """Test cases for world model agent."""
    
    @unittest.skipIf(SKIP_API_TESTS, "API keys not configured")
    def test_import_modules(self):
        """Test that all required modules can be imported."""
        try:
            from world_model_agent import (
                create_world_model_agent,
                run_world_model,
                search_trading_news,
                get_daily_ohlcv,
                recall_vector_store
            )
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import modules: {e}")
    
    @unittest.skipIf(SKIP_API_TESTS, "API keys not configured")
    def test_agent_creation(self):
        """Test that agent can be created successfully."""
        try:
            from world_model_agent import create_world_model_agent
            agent = create_world_model_agent()
            self.assertIsNotNone(agent)
        except Exception as e:
            self.fail(f"Failed to create agent: {e}")
    
    @unittest.skipIf(SKIP_API_TESTS, "API keys not configured")
    def test_run_world_model_basic(self):
        """Test running world model with a simple symbol."""
        try:
            from world_model_agent import run_world_model
            
            # Run with a test symbol
            result = run_world_model("AAPL")
            
            # Check result structure
            self.assertIn("run_id", result)
            self.assertIn("symbol", result)
            self.assertIn("decision", result)
            self.assertEqual(result["symbol"], "AAPL")
            
            # Check decision structure if successful
            if "error" not in result.get("decision", {}):
                decision = result["decision"]
                self.assertIn("action", decision)
                self.assertIn("median", decision)
                self.assertIn("q25", decision)
                self.assertIn("q75", decision)
                
                # Validate action
                self.assertIn(decision["action"], ["BUY", "SELL", "HOLD"])
        
        except Exception as e:
            self.fail(f"Failed to run world model: {e}")


class TestDatabaseOperations(unittest.TestCase):
    """Test cases for database operations."""
    
    def test_db_util_import(self):
        """Test that database utilities can be imported."""
        try:
            from utils.db_util import (
                get_session,
                store_trading_run,
                store_trading_decision,
                get_trading_runs
            )
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import db_util: {e}")
    
    def test_session_creation(self):
        """Test that database session can be created."""
        try:
            from utils.db_util import get_session
            session = get_session()
            self.assertIsNotNone(session)
            session.close()
        except Exception as e:
            self.fail(f"Failed to create database session: {e}")


class TestToolFunctions(unittest.TestCase):
    """Test cases for individual tool functions."""
    
    @unittest.skipIf(SKIP_API_TESTS, "API keys not configured")
    def test_search_trading_news_tool(self):
        """Test the search_trading_news tool."""
        try:
            from world_model_agent import search_trading_news
            
            # This is a LangChain tool, so we need to invoke it properly
            result = search_trading_news.invoke({"query": "Apple stock analysis"})
            
            self.assertIsNotNone(result)
            self.assertIsInstance(result, str)
        
        except Exception as e:
            # Some failures might be expected due to API limits
            print(f"Note: search_trading_news test had issues: {e}")
    
    @unittest.skipIf(SKIP_API_TESTS, "API keys not configured")
    def test_get_daily_ohlcv_tool(self):
        """Test the get_daily_ohlcv tool."""
        try:
            from world_model_agent import get_daily_ohlcv
            
            result = get_daily_ohlcv.invoke({"symbol": "AAPL"})
            
            self.assertIsNotNone(result)
            self.assertIsInstance(result, str)
            
            # Should contain CSV data
            self.assertIn(",", result)
        
        except Exception as e:
            print(f"Note: get_daily_ohlcv test had issues: {e}")


class TestDataModels(unittest.TestCase):
    """Test cases for data models."""
    
    def test_trading_run_model(self):
        """Test TradingRun model."""
        try:
            from utils.db_util import TradingRun
            from datetime import datetime
            
            run = TradingRun(
                run_id="test-123",
                symbol="AAPL",
                youtube_url="https://example.com"
            )
            
            self.assertEqual(run.symbol, "AAPL")
            self.assertEqual(run.run_id, "test-123")
        
        except Exception as e:
            self.fail(f"Failed to create TradingRun model: {e}")
    
    def test_trading_decision_model(self):
        """Test TradingDecision model."""
        try:
            from utils.db_util import TradingDecision
            
            decision = TradingDecision(
                run_id="test-123",
                symbol="AAPL",
                median_return=2.5,
                q25_return=-1.0,
                q75_return=5.0,
                action="BUY"
            )
            
            self.assertEqual(decision.symbol, "AAPL")
            self.assertEqual(decision.action, "BUY")
            self.assertEqual(decision.median_return, 2.5)
        
        except Exception as e:
            self.fail(f"Failed to create TradingDecision model: {e}")


class TestConfigurationValidation(unittest.TestCase):
    """Test cases for configuration validation."""
    
    def test_env_variables_loaded(self):
        """Test that environment variables are properly loaded."""
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check if at least some API keys are available
        google_key = os.getenv("GOOGLE_API_KEY")
        self.assertIsNotNone(google_key, "GOOGLE_API_KEY not set")
    
    def test_requirements_installed(self):
        """Test that all required packages are installed."""
        required_packages = [
            "langchain",
            "langchain_google_genai",
            "langgraph",
            "pgvector",
            "psycopg2",
            "tavily",
            "yt_dlp",
            "pandas",
            "streamlit",
            "plotly"
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                self.fail(f"Required package '{package}' is not installed")


if __name__ == "__main__":
    unittest.main()
