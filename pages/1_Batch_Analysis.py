"""Finance Genie - Batch Analysis Page
Run analysis on multiple symbols at once.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from world_model_agent import run_world_model
from utils.db_util import get_session, TradingDecision

st.set_page_config(
    page_title="Batch Analysis - Finance Genie",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Batch Analysis")
st.markdown("*Run world model analysis on multiple symbols*")

# Input method selection
input_method = st.radio("Select input method:", ["Manual Entry", "Upload CSV"])

symbols_to_analyze = []

if input_method == "Manual Entry":
    symbols_text = st.text_area(
        "Enter symbols (one per line or comma-separated)",
        value="NVDA\nAMD\nTSLA",
        height=100,
        help="Enter stock symbols to analyze"
    )
    
    # Parse symbols
    if "," in symbols_text:
        symbols_to_analyze = [s.strip().upper() for s in symbols_text.split(",")]
    else:
        symbols_to_analyze = [s.strip().upper() for s in symbols_text.split("\n")]
    
    symbols_to_analyze = [s for s in symbols_to_analyze if s]

else:  # Upload CSV
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        # Try to find symbol column
        symbol_col = None
        for col in df.columns:
            if col.lower() in ["symbol", "ticker", "stock"]:
                symbol_col = col
                break
        
        if symbol_col:
            symbols_to_analyze = df[symbol_col].str.upper().tolist()
            st.success(f"✅ Found {len(symbols_to_analyze)} symbols")
        else:
            st.error("❌ Could not find symbol column. Expected: 'symbol', 'ticker', or 'stock'")

st.divider()

# Display symbols to analyze
if symbols_to_analyze:
    st.subheader(f"Symbols to Analyze ({len(symbols_to_analyze)})")
    st.write(", ".join(symbols_to_analyze))
    
    # Run batch analysis
    if st.button("🚀 Run Batch Analysis", type="primary", use_container_width=True):
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        for i, symbol in enumerate(symbols_to_analyze):
            status_text.text(f"Processing {i+1}/{len(symbols_to_analyze)}: {symbol}")
            progress_bar.progress((i + 1) / len(symbols_to_analyze))
            
            try:
                result = run_world_model(symbol)
                
                if "error" not in result:
                    decision = result.get("decision", {})
                    results.append({
                        "Symbol": symbol,
                        "Action": decision.get("action", "N/A"),
                        "Median": decision.get("median", None),
                        "Q25": decision.get("q25", None),
                        "Q75": decision.get("q75", None),
                        "Run ID": result["run_id"][:8],
                        "Status": "✅ Success"
                    })
                else:
                    results.append({
                        "Symbol": symbol,
                        "Action": "ERROR",
                        "Median": None,
                        "Q25": None,
                        "Q75": None,
                        "Run ID": result.get("run_id", "N/A")[:8],
                        "Status": f"❌ {result['error']}"
                    })
            
            except Exception as e:
                results.append({
                    "Symbol": symbol,
                    "Action": "ERROR",
                    "Median": None,
                    "Q25": None,
                    "Q75": None,
                    "Run ID": "N/A",
                    "Status": f"❌ {str(e)}"
                })
        
        status_text.text("✅ Batch analysis completed!")
        progress_bar.empty()
        
        # Display results
        st.divider()
        st.subheader("📈 Batch Analysis Results")
        
        df_results = pd.DataFrame(results)
        st.dataframe(df_results, use_container_width=True, hide_index=True)
        
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            successful = (df_results["Status"] == "✅ Success").sum()
            st.metric("Successful", successful)
        
        with col2:
            buy_count = (df_results["Action"] == "BUY").sum()
            st.metric("BUY Signals", buy_count)
        
        with col3:
            sell_count = (df_results["Action"] == "SELL").sum()
            st.metric("SELL Signals", sell_count)
        
        with col4:
            hold_count = (df_results["Action"] == "HOLD").sum()
            st.metric("HOLD Signals", hold_count)
        
        # Export results
        st.divider()
        st.subheader("💾 Export Results")
        
        csv = df_results.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        json_data = json.dumps(results, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

else:
    st.info("👆 Enter symbols above to start batch analysis")
