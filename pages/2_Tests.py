"""Finance Genie - Tests Page
Local test suite for verifying system health and functionality.
"""

import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Tests - Finance Genie",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Local Test Suite")
st.markdown("*Verify system health and component functionality*")

# Initialize session state for test results
if "test_results" not in st.session_state:
    st.session_state.test_results = None
if "test_running" not in st.session_state:
    st.session_state.test_running = False


def run_all_tests():
    """Run all local tests and return results."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "summary": {"passed": 0, "failed": 0, "total": 0}
    }
    
    # Test 1: Import world_model_agent
    test_1 = {
        "name": "Import world_model_agent",
        "description": "Verify all world model agent functions can be imported",
        "passed": False,
        "error": None
    }
    try:
        from world_model_agent import (
            search_trading_news,
            download_trading_video,
            get_daily_ohlcv,
            recall_vector_store,
            create_world_model_agent
        )
        test_1["passed"] = True
    except Exception as e:
        test_1["error"] = str(e)
    results["tests"].append(test_1)
    
    # Test 2: Import database utilities
    test_2 = {
        "name": "Import database utilities",
        "description": "Verify database utility functions can be imported",
        "passed": False,
        "error": None
    }
    try:
        from utils.db_util import (
            DB_AVAILABLE,
            get_trading_runs,
            get_db_stats,
            TradingRun,
            TradingDecision,
            PerformanceMetric
        )
        test_2["passed"] = True
    except Exception as e:
        test_2["error"] = str(e)
    results["tests"].append(test_2)
    
    # Test 3: Database connection
    test_3 = {
        "name": "Database connection",
        "description": "Verify database connectivity and availability",
        "passed": False,
        "error": None,
        "details": {}
    }
    try:
        from utils.db_util import DB_AVAILABLE, get_db_stats
        stats = get_db_stats()
        test_3["details"] = stats
        if DB_AVAILABLE:
            test_3["passed"] = True
        else:
            test_3["error"] = "Database not configured"
    except Exception as e:
        test_3["error"] = str(e)
    results["tests"].append(test_3)
    
    # Test 4: API keys
    test_4 = {
        "name": "API key configuration",
        "description": "Verify all required API keys are configured",
        "passed": False,
        "error": None,
        "details": {}
    }
    try:
        required_keys = ['GOOGLE_API_KEY', 'TAVILY_API_KEY', 'EODHD_API_KEY']
        configured_keys = {k: bool(os.getenv(k)) for k in required_keys}
        test_4["details"] = configured_keys
        
        missing_keys = [k for k in required_keys if not os.getenv(k)]
        if not missing_keys:
            test_4["passed"] = True
        else:
            test_4["error"] = f"Missing keys: {', '.join(missing_keys)}"
    except Exception as e:
        test_4["error"] = str(e)
    results["tests"].append(test_4)
    
    # Test 5: Streamlit pages
    test_5 = {
        "name": "Streamlit pages",
        "description": "Verify all Streamlit pages are present",
        "passed": False,
        "error": None,
        "details": {}
    }
    try:
        pages_dir = Path("pages")
        pages = list(pages_dir.glob("*.py"))
        test_5["details"]["pages_found"] = len(pages)
        test_5["details"]["pages"] = [p.name for p in sorted(pages)]
        
        if len(pages) >= 2:
            test_5["passed"] = True
        else:
            test_5["error"] = f"Expected at least 2 pages, found {len(pages)}"
    except Exception as e:
        test_5["error"] = str(e)
    results["tests"].append(test_5)
    
    # Test 6: Configuration files
    test_6 = {
        "name": "Configuration files",
        "description": "Verify all required configuration files exist",
        "passed": False,
        "error": None,
        "details": {}
    }
    try:
        required_files = ['requirements.txt', 'Home.py', 'world_model_agent.py', 'cli.py']
        file_status = {f: Path(f).exists() for f in required_files}
        test_6["details"] = file_status
        
        missing_files = [f for f in required_files if not Path(f).exists()]
        if not missing_files:
            test_6["passed"] = True
        else:
            test_6["error"] = f"Missing files: {', '.join(missing_files)}"
    except Exception as e:
        test_6["error"] = str(e)
    results["tests"].append(test_6)
    
    # Test 7: Python version
    test_7 = {
        "name": "Python version",
        "description": "Verify Python version is 3.11+",
        "passed": False,
        "error": None,
        "details": {}
    }
    try:
        version = sys.version_info
        test_7["details"]["version"] = f"{version.major}.{version.minor}.{version.micro}"
        if version.major >= 3 and version.minor >= 11:
            test_7["passed"] = True
        else:
            test_7["error"] = f"Python 3.11+ required, found {version.major}.{version.minor}"
    except Exception as e:
        test_7["error"] = str(e)
    results["tests"].append(test_7)
    
    # Test 8: Project structure
    test_8 = {
        "name": "Project structure",
        "description": "Verify project directory structure is correct",
        "passed": False,
        "error": None,
        "details": {}
    }
    try:
        required_dirs = ['pages', 'utils', 'tests', 'sql']
        dir_status = {d: Path(d).exists() for d in required_dirs}
        test_8["details"] = dir_status
        
        missing_dirs = [d for d in required_dirs if not Path(d).exists()]
        if not missing_dirs:
            test_8["passed"] = True
        else:
            test_8["error"] = f"Missing directories: {', '.join(missing_dirs)}"
    except Exception as e:
        test_8["error"] = str(e)
    results["tests"].append(test_8)
    
    # Calculate summary
    results["summary"]["total"] = len(results["tests"])
    results["summary"]["passed"] = sum(1 for t in results["tests"] if t["passed"])
    results["summary"]["failed"] = results["summary"]["total"] - results["summary"]["passed"]
    
    return results


# Main content
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("Run the local test suite to verify system health and component functionality.")

with col2:
    if st.button("🚀 Run Tests", use_container_width=True, type="primary"):
        st.session_state.test_running = True

# Run tests if button clicked
if st.session_state.test_running:
    with st.spinner("🔄 Running tests..."):
        st.session_state.test_results = run_all_tests()
    st.session_state.test_running = False
    st.rerun()

# Display results
if st.session_state.test_results:
    results = st.session_state.test_results
    
    # Summary metrics
    st.divider()
    st.subheader("📊 Test Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tests", results["summary"]["total"])
    
    with col2:
        st.metric("✅ Passed", results["summary"]["passed"], 
                 delta=None, delta_color="off")
    
    with col3:
        st.metric("❌ Failed", results["summary"]["failed"],
                 delta=None, delta_color="off")
    
    with col4:
        pass_rate = (results["summary"]["passed"] / results["summary"]["total"] * 100) if results["summary"]["total"] > 0 else 0
        st.metric("Pass Rate", f"{pass_rate:.0f}%")
    
    st.divider()
    
    # Detailed results
    st.subheader("🔍 Detailed Test Results")
    
    for i, test in enumerate(results["tests"], 1):
        status_emoji = "✅" if test["passed"] else "❌"
        
        with st.expander(f"{status_emoji} Test {i}: {test['name']}", expanded=test["passed"] is False):
            st.write(f"**Description:** {test['description']}")
            
            if test["passed"]:
                st.success("PASSED")
            else:
                st.error(f"FAILED: {test['error']}")
            
            if test.get("details"):
                st.write("**Details:**")
                for key, value in test["details"].items():
                    if isinstance(value, dict):
                        st.write(f"  {key}:")
                        for k, v in value.items():
                            st.write(f"    - {k}: {v}")
                    elif isinstance(value, list):
                        st.write(f"  {key}:")
                        for item in value:
                            st.write(f"    - {item}")
                    else:
                        st.write(f"  {key}: {value}")
    
    st.divider()
    
    # Test timestamp
    st.caption(f"Tests run at: {results['timestamp']}")
    
    # Overall status
    if results["summary"]["failed"] == 0:
        st.success("🎉 All tests passed! System is healthy.")
    else:
        st.warning(f"⚠️ {results['summary']['failed']} test(s) failed. Please review the details above.")

else:
    st.info("👆 Click 'Run Tests' to start the test suite")

# Additional information
st.divider()

with st.expander("ℹ️ About These Tests"):
    st.markdown("""
    The test suite verifies:
    
    1. **Imports**: All Python modules can be imported successfully
    2. **Database**: PostgreSQL connection and availability
    3. **API Keys**: Required API keys are configured
    4. **Pages**: Streamlit pages are present
    5. **Files**: Configuration files exist
    6. **Python**: Correct Python version installed
    7. **Structure**: Project directory structure is correct
    
    These tests help ensure the system is properly configured and ready to use.
    """)

with st.expander("🔧 CLI Tests"):
    st.markdown("""
    You can also run tests from the command line:
    
    ```bash
    python cli.py --test
    ```
    
    This will run the same tests and display results in your terminal.
    """)

with st.expander("📋 Test Troubleshooting"):
    st.markdown("""
    **If tests fail:**
    
    1. **Import Errors**: Check that all dependencies are installed
       ```bash
       pip install -r requirements.txt
       ```
    
    2. **Database Errors**: Ensure PostgreSQL is running and configured
       ```bash
       python -c "from utils.db_util import init_db; init_db()"
       ```
    
    3. **API Key Errors**: Verify API keys in `.env` file
       ```bash
       cat .env
       ```
    
    4. **File Not Found**: Ensure you're running from the project root directory
       ```bash
       cd /path/to/finance-genie
       ```
    """)
