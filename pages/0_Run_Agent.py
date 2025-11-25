"""Finance Genie - Run Agent Page
Interface to run the world model trading agent.
"""

import streamlit as st
import json
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from world_model_agent import run_world_model
from utils.db_util import DB_AVAILABLE, get_trading_run_details

st.set_page_config(
    page_title="Run Agent - Finance Genie",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Run World Model Agent")
st.markdown("*Generate trading decisions using AI-powered world model analysis*")

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    symbol = st.text_input(
        "Stock Symbol",
        value="NVDA",
        placeholder="e.g., NVDA, AMD, TSLA",
        help="Enter the stock ticker symbol"
    ).upper().strip()

with col2:
    youtube_url = st.text_input(
        "YouTube URL (Optional)",
        value="",
        placeholder="https://youtu.be/...",
        help="Optional: Provide a YouTube URL for trading analysis"
    ).strip()

st.divider()

# Run button
if st.button("🚀 Run Agent", type="primary", use_container_width=True):
    if not symbol:
        st.error("❌ Please enter a stock symbol")
    else:
        with st.spinner(f"🔄 Running world model for {symbol}..."):
            try:
                # Run the agent
                result = run_world_model(symbol, youtube_url if youtube_url else None)
                
                # Display results
                st.success("✅ Agent execution completed!")
                
                st.divider()
                st.subheader("📊 Trading Decision")
                
                # Display decision
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    decision = result.get("decision", {})
                    
                    # Create columns for key metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        action = decision.get("action", "N/A")
                        action_emoji = {
                            "BUY": "🟢",
                            "SELL": "🔴",
                            "HOLD": "🟡"
                        }.get(action, "⚪")
                        st.metric("Action", f"{action_emoji} {action}")
                    
                    with col2:
                        median = decision.get("median", None)
                        if median is not None:
                            st.metric("Median Return", f"{median:.2f}%")
                        else:
                            st.metric("Median Return", "N/A")
                    
                    with col3:
                        q25 = decision.get("q25", None)
                        if q25 is not None:
                            st.metric("Downside (Q25)", f"{q25:.2f}%")
                        else:
                            st.metric("Downside (Q25)", "N/A")
                    
                    with col4:
                        q75 = decision.get("q75", None)
                        if q75 is not None:
                            st.metric("Upside (Q75)", f"{q75:.2f}%")
                        else:
                            st.metric("Upside (Q75)", "N/A")
                    
                    st.divider()
                    
                    # Display full JSON response
                    st.subheader("📋 Full Response")
                    st.json(result)
                    
                    # Store run ID for reference
                    st.info(f"📌 Run ID: `{result['run_id']}`")
                    st.caption(f"Timestamp: {result['timestamp']}")
                    
                    # Database status
                    if DB_AVAILABLE:
                        st.success("✓ Result saved to database")
                    else:
                        st.warning("⚠️ Database not available - result not persisted")
            
            except Exception as e:
                st.error(f"❌ Error running agent: {str(e)}")
                st.exception(e)

st.divider()

# Information section
with st.expander("ℹ️ How the World Model Works"):
    st.markdown("""
    The **GENIE-3-FINANCE** world model agent performs the following steps:
    
    1. **Data Collection**
       - Fetches 120-day OHLCV data with technical indicators (SMA20, RSI14)
       - Searches for recent trading news and market analysis
       - Downloads YouTube video transcripts if provided
       - Recalls relevant memories from past trading cycles
    
    2. **Analysis**
       - Analyzes market sentiment from news and videos
       - Evaluates technical trends using OHLCV + indicators
       - Considers historical context from vector store
       - Reasons through potential market movements
    
    3. **Prediction**
       - Predicts 5-day ahead return distribution
       - Estimates median return (expected value)
       - Calculates downside risk (25th percentile)
       - Calculates upside potential (75th percentile)
    
    4. **Decision**
       - **BUY**: Median > 2% with favorable risk/reward
       - **SELL**: Median < -2% or extreme downside risk
       - **HOLD**: All other cases
    
    All decisions are stored in PostgreSQL for audit trail and performance tracking.
    """)

with st.expander("🔧 Configuration"):
    st.markdown("""
    **Environment Variables Required:**
    - `GOOGLE_API_KEY`: Gemini API key
    - `TAVILY_API_KEY`: Web search API
    - `EODHD_API_KEY`: Stock data API
    - `PGVECTOR_CONNECTION`: PostgreSQL connection string (optional for testing)
    
    **Models Used:**
    - **LLM**: Gemini 2.5 Flash (reasoning + decision making)
    - **Embeddings**: Gemini Text-Embedding-004 (768 dimensions)
    - **Framework**: LangGraph with React pattern
    - **Vector Store**: PostgreSQL with pgvector extension (optional)
    """)
