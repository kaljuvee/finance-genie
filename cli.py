#!/usr/bin/env python3
"""
Finance Genie CLI - Command-line interface for running the world model trading agent.

Usage:
    python cli.py --symbol NVDA
    python cli.py --symbol NVDA --youtube "https://youtu.be/..."
    python cli.py --batch symbols.txt
    python cli.py --test
"""

import argparse
import sys
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from world_model_agent import run_world_model
from utils.db_util import (
    DB_AVAILABLE,
    get_trading_runs,
    get_db_stats,
    store_trading_run,
    store_trading_decision
)


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_section(text: str):
    """Print a formatted section header."""
    print(f"\n📊 {text}")
    print("-" * 80)


def print_decision(result: dict):
    """Pretty print a trading decision result."""
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    decision = result.get("decision", {})
    
    # Decision action with emoji
    action = decision.get("action", "N/A")
    action_emoji = {
        "BUY": "🟢",
        "SELL": "🔴",
        "HOLD": "🟡"
    }.get(action, "⚪")
    
    print(f"\n{action_emoji} Action: {action}")
    
    # Return predictions
    median = decision.get("median")
    q25 = decision.get("q25")
    q75 = decision.get("q75")
    
    if median is not None:
        print(f"📈 Median Return: {median:.2f}%")
    if q25 is not None:
        print(f"📉 Downside Risk (Q25): {q25:.2f}%")
    if q75 is not None:
        print(f"📈 Upside Potential (Q75): {q75:.2f}%")
    
    # Run ID and timestamp
    print(f"\n📌 Run ID: {result['run_id']}")
    print(f"⏰ Timestamp: {result['timestamp']}")
    
    # Database status
    if DB_AVAILABLE:
        print("💾 Status: Saved to database")
    else:
        print("⚠️  Status: Database not available (result not persisted)")


def run_single_symbol(symbol: str, youtube_url: Optional[str] = None):
    """Run analysis for a single symbol."""
    print_header(f"Running World Model Agent for {symbol}")
    
    print(f"\n📊 Input Parameters:")
    print(f"  Symbol: {symbol}")
    if youtube_url:
        print(f"  YouTube URL: {youtube_url}")
    
    print(f"\n🔄 Running agent (this may take 15-25 seconds)...")
    
    try:
        result = run_world_model(symbol, youtube_url)
        print_decision(result)
        
        # Save to file
        output_file = f"results_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Results saved to: {output_file}")
        
        return result
    
    except Exception as e:
        print(f"\n❌ Error running agent: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def run_batch_analysis(symbols: List[str]):
    """Run analysis for multiple symbols."""
    print_header(f"Batch Analysis: {len(symbols)} Symbols")
    
    print(f"\n📊 Symbols to analyze:")
    for i, symbol in enumerate(symbols, 1):
        print(f"  {i}. {symbol}")
    
    results = []
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\n\n{'='*80}")
        print(f"  Processing {i}/{len(symbols)}: {symbol}")
        print(f"{'='*80}")
        
        try:
            result = run_world_model(symbol)
            results.append(result)
            
            decision = result.get("decision", {})
            action = decision.get("action", "N/A")
            median = decision.get("median", "N/A")
            
            if isinstance(median, float):
                print(f"✅ {symbol}: {action} (Median: {median:.2f}%)")
            else:
                print(f"✅ {symbol}: {action}")
        
        except Exception as e:
            print(f"❌ {symbol}: Error - {str(e)}")
            results.append({"symbol": symbol, "error": str(e)})
    
    # Summary
    print_section("Batch Analysis Summary")
    
    successful = sum(1 for r in results if "error" not in r)
    buy_count = sum(1 for r in results if r.get("decision", {}).get("action") == "BUY")
    sell_count = sum(1 for r in results if r.get("decision", {}).get("action") == "SELL")
    hold_count = sum(1 for r in results if r.get("decision", {}).get("action") == "HOLD")
    
    print(f"✅ Successful: {successful}/{len(symbols)}")
    print(f"🟢 BUY Signals: {buy_count}")
    print(f"🔴 SELL Signals: {sell_count}")
    print(f"🟡 HOLD Signals: {hold_count}")
    
    # Save batch results
    output_file = f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Batch results saved to: {output_file}")
    
    return results


def show_system_status():
    """Display system status and configuration."""
    print_header("Finance Genie - System Status")
    
    print(f"\n🔧 System Information:")
    print(f"  Python Version: {sys.version.split()[0]}")
    print(f"  Platform: {sys.platform}")
    
    print(f"\n📊 Database Status:")
    if DB_AVAILABLE:
        stats = get_db_stats()
        if stats.get("available"):
            print(f"  ✅ Database Available: Yes")
            print(f"  📍 Schema: {stats.get('schema', 'N/A')}")
            print(f"  📈 Trading Runs: {stats.get('total_runs', 0)}")
            print(f"  🎯 Trading Decisions: {stats.get('total_decisions', 0)}")
            print(f"  📊 Performance Metrics: {stats.get('total_metrics', 0)}")
        else:
            print(f"  ⚠️  Database Error: {stats.get('error', 'Unknown')}")
    else:
        print(f"  ❌ Database Available: No")
        print(f"  💡 Tip: Set PGVECTOR_CONNECTION in .env to enable database")
    
    print(f"\n🔑 API Configuration:")
    print(f"  GOOGLE_API_KEY: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Not set'}")
    print(f"  TAVILY_API_KEY: {'✅ Set' if os.getenv('TAVILY_API_KEY') else '❌ Not set'}")
    print(f"  EODHD_API_KEY: {'✅ Set' if os.getenv('EODHD_API_KEY') else '❌ Not set'}")
    print(f"  PGVECTOR_CONNECTION: {'✅ Set' if os.getenv('PGVECTOR_CONNECTION') else '❌ Not set'}")


def run_tests():
    """Run local tests and display results."""
    print_header("Finance Genie - Local Tests")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Import world_model_agent
    print("\n🧪 Test 1: Importing world_model_agent...")
    try:
        from world_model_agent import (
            search_trading_news,
            download_trading_video,
            get_daily_ohlcv,
            recall_vector_store,
            create_world_model_agent
        )
        print("   ✅ PASSED: All functions imported successfully")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        tests_failed += 1
    
    # Test 2: Import database utilities
    print("\n🧪 Test 2: Importing database utilities...")
    try:
        from utils.db_util import (
            DB_AVAILABLE,
            get_trading_runs,
            get_db_stats,
            TradingRun,
            TradingDecision,
            PerformanceMetric
        )
        print("   ✅ PASSED: Database utilities imported successfully")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        tests_failed += 1
    
    # Test 3: Database connection
    print("\n🧪 Test 3: Database availability...")
    try:
        from utils.db_util import DB_AVAILABLE, get_db_stats
        if DB_AVAILABLE:
            stats = get_db_stats()
            if stats.get("available"):
                print(f"   ✅ PASSED: Database connected")
            else:
                print(f"   ⚠️  WARNING: Database configured but not accessible")
        else:
            print(f"   ℹ️  INFO: Database not configured (demo mode)")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        tests_failed += 1
    
    # Test 4: API keys
    print("\n🧪 Test 4: API key configuration...")
    try:
        required_keys = ['GOOGLE_API_KEY', 'TAVILY_API_KEY', 'EODHD_API_KEY']
        missing_keys = [k for k in required_keys if not os.getenv(k)]
        
        if not missing_keys:
            print(f"   ✅ PASSED: All required API keys configured")
            tests_passed += 1
        else:
            print(f"   ⚠️  WARNING: Missing keys: {', '.join(missing_keys)}")
            tests_passed += 1  # Not a hard failure
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        tests_failed += 1
    
    # Test 5: Streamlit pages
    print("\n🧪 Test 5: Checking Streamlit pages...")
    try:
        pages_dir = Path("pages")
        pages = list(pages_dir.glob("*.py"))
        if len(pages) >= 2:
            print(f"   ✅ PASSED: Found {len(pages)} Streamlit pages")
            for page in sorted(pages):
                print(f"      - {page.name}")
            tests_passed += 1
        else:
            print(f"   ❌ FAILED: Expected at least 2 pages, found {len(pages)}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        tests_failed += 1
    
    # Test 6: Configuration files
    print("\n🧪 Test 6: Checking configuration files...")
    try:
        required_files = ['requirements.txt', 'Home.py', 'world_model_agent.py']
        missing_files = [f for f in required_files if not Path(f).exists()]
        
        if not missing_files:
            print(f"   ✅ PASSED: All required files present")
            tests_passed += 1
        else:
            print(f"   ❌ FAILED: Missing files: {', '.join(missing_files)}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)}")
        tests_failed += 1
    
    # Summary
    print_section("Test Summary")
    total = tests_passed + tests_failed
    print(f"✅ Passed: {tests_passed}/{total}")
    print(f"❌ Failed: {tests_failed}/{total}")
    
    if tests_failed == 0:
        print(f"\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Please review the output above.")
        return 1


def show_recent_runs():
    """Show recent trading runs from database."""
    print_header("Recent Trading Runs")
    
    if not DB_AVAILABLE:
        print("\n❌ Database not available. Cannot retrieve recent runs.")
        return
    
    try:
        runs = get_trading_runs(limit=10)
        
        if not runs:
            print("\n📊 No trading runs found in database.")
            return
        
        print(f"\n📊 Found {len(runs)} recent trading runs:\n")
        
        for i, run in enumerate(runs, 1):
            print(f"{i}. Run ID: {run.run_id}")
            print(f"   Symbol: {run.symbol}")
            print(f"   Created: {run.created_at}")
            if run.youtube_url:
                print(f"   YouTube: {run.youtube_url}")
            if run.decisions:
                for decision in run.decisions:
                    print(f"   Decision: {decision.action} (Median: {decision.median_return}%)")
            print()
    
    except Exception as e:
        print(f"\n❌ Error retrieving runs: {str(e)}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Finance Genie - AI-Powered Trading Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --symbol NVDA
  python cli.py --symbol NVDA --youtube "https://youtu.be/..."
  python cli.py --batch symbols.txt
  python cli.py --status
  python cli.py --test
  python cli.py --recent
        """
    )
    
    parser.add_argument(
        "--symbol",
        type=str,
        help="Stock symbol to analyze (e.g., NVDA, AMD, TSLA)"
    )
    parser.add_argument(
        "--youtube",
        type=str,
        help="YouTube URL for trading video analysis (optional)"
    )
    parser.add_argument(
        "--batch",
        type=str,
        help="Path to file with symbols (one per line)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show system status and configuration"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run local tests"
    )
    parser.add_argument(
        "--recent",
        action="store_true",
        help="Show recent trading runs from database"
    )
    
    args = parser.parse_args()
    
    # Handle different commands
    if args.test:
        return run_tests()
    
    elif args.status:
        show_system_status()
        return 0
    
    elif args.recent:
        show_recent_runs()
        return 0
    
    elif args.symbol:
        result = run_single_symbol(args.symbol, args.youtube)
        return 0 if result else 1
    
    elif args.batch:
        try:
            with open(args.batch, 'r') as f:
                symbols = [line.strip().upper() for line in f if line.strip()]
            
            if not symbols:
                print(f"❌ Error: No symbols found in {args.batch}")
                return 1
            
            run_batch_analysis(symbols)
            return 0
        
        except FileNotFoundError:
            print(f"❌ Error: File not found: {args.batch}")
            return 1
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return 1
    
    else:
        # Show help if no arguments
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
