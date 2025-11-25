"""Finance Genie - Home Page
Main Streamlit dashboard for viewing trading runs and performance metrics.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json

from utils.db_util import (
    get_trading_runs,
    get_trading_run_details,
    get_performance_summary,
    get_session,
    TradingRun,
    TradingDecision,
    PerformanceMetric
)

# Configure page
st.set_page_config(
    page_title="Finance Genie",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .decision-buy {
        color: #06a77d;
        font-weight: bold;
    }
    .decision-sell {
        color: #d62828;
        font-weight: bold;
    }
    .decision-hold {
        color: #f77f00;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("💰 Finance Genie - World Model Trading Dashboard")
st.markdown("*AI-powered trading decisions using Gemini and LangGraph*")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Select View", ["Dashboard", "Recent Runs", "Performance Analysis"])
    
    st.divider()
    st.header("Filters")
    refresh_interval = st.slider("Auto-refresh (seconds)", 30, 300, 60)
    
    if st.button("🔄 Refresh Data"):
        st.rerun()


# ============ DASHBOARD PAGE ============
if page == "Dashboard":
    st.header("Trading Dashboard")
    
    # Get recent runs
    recent_runs = get_trading_runs(limit=10)
    
    if not recent_runs:
        st.info("📊 No trading runs yet. Go to 'Run Agent' to start trading analysis.")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Runs", len(recent_runs))
        
        with col2:
            buy_count = sum(1 for run in recent_runs if run.decisions and any(d.action == "BUY" for d in run.decisions))
            st.metric("BUY Signals", buy_count)
        
        with col3:
            sell_count = sum(1 for run in recent_runs if run.decisions and any(d.action == "SELL" for d in run.decisions))
            st.metric("SELL Signals", sell_count)
        
        with col4:
            hold_count = sum(1 for run in recent_runs if run.decisions and any(d.action == "HOLD" for d in run.decisions))
            st.metric("HOLD Signals", hold_count)
        
        st.divider()
        
        # Recent trading decisions
        st.subheader("Recent Trading Decisions")
        
        decisions_data = []
        for run in recent_runs:
            if run.decisions:
                for decision in run.decisions:
                    decisions_data.append({
                        "Run ID": run.run_id[:8] + "...",
                        "Symbol": decision.symbol,
                        "Action": decision.action,
                        "Median Return": f"{decision.median_return:.2f}%" if decision.median_return else "N/A",
                        "Q25 (Downside)": f"{decision.q25_return:.2f}%" if decision.q25_return else "N/A",
                        "Q75 (Upside)": f"{decision.q75_return:.2f}%" if decision.q75_return else "N/A",
                        "Time": run.created_at.strftime("%Y-%m-%d %H:%M")
                    })
        
        if decisions_data:
            df_decisions = pd.DataFrame(decisions_data)
            st.dataframe(df_decisions, use_container_width=True, hide_index=True)
        
        # Distribution chart
        st.subheader("Return Distribution by Symbol")
        
        session = get_session()
        try:
            all_decisions = session.query(TradingDecision).all()
            
            if all_decisions:
                chart_data = []
                for d in all_decisions:
                    chart_data.append({
                        "Symbol": d.symbol,
                        "Median": d.median_return,
                        "Q25": d.q25_return,
                        "Q75": d.q75_return
                    })
                
                df_chart = pd.DataFrame(chart_data)
                
                fig = go.Figure()
                
                for symbol in df_chart["Symbol"].unique():
                    symbol_data = df_chart[df_chart["Symbol"] == symbol]
                    
                    fig.add_trace(go.Box(
                        y=[symbol_data["Q25"].values[0], symbol_data["Median"].values[0], symbol_data["Q75"].values[0]],
                        name=symbol,
                        boxmean="sd"
                    ))
                
                fig.update_layout(
                    title="Return Distribution by Symbol",
                    yaxis_title="Return (%)",
                    xaxis_title="Symbol",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        finally:
            session.close()


# ============ RECENT RUNS PAGE ============
elif page == "Recent Runs":
    st.header("Recent Trading Runs")
    
    recent_runs = get_trading_runs(limit=50)
    
    if not recent_runs:
        st.info("📊 No trading runs yet.")
    else:
        # Create tabs for each run
        for i, run in enumerate(recent_runs[:10]):  # Show top 10
            with st.expander(f"🔍 {run.symbol} - {run.created_at.strftime('%Y-%m-%d %H:%M')} (ID: {run.run_id[:8]})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Symbol:** {run.symbol}")
                    st.write(f"**Run ID:** {run.run_id}")
                    st.write(f"**Created:** {run.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                
                with col2:
                    if run.youtube_url:
                        st.write(f"**YouTube URL:** [Link]({run.youtube_url})")
                
                st.divider()
                
                # Show decisions
                if run.decisions:
                    st.subheader("Trading Decisions")
                    for decision in run.decisions:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            action_color = {
                                "BUY": "🟢",
                                "SELL": "🔴",
                                "HOLD": "🟡"
                            }.get(decision.action, "⚪")
                            st.metric("Action", f"{action_color} {decision.action}")
                        
                        with col2:
                            st.metric("Median Return", f"{decision.median_return:.2f}%" if decision.median_return else "N/A")
                        
                        with col3:
                            st.metric("Upside (Q75)", f"{decision.q75_return:.2f}%" if decision.q75_return else "N/A")
                        
                        st.write(f"**Downside (Q25):** {decision.q25_return:.2f}%" if decision.q25_return else "N/A")
                else:
                    st.info("No decisions recorded for this run.")


# ============ PERFORMANCE ANALYSIS PAGE ============
elif page == "Performance Analysis":
    st.header("Performance Analysis")
    
    session = get_session()
    try:
        all_metrics = session.query(PerformanceMetric).all()
        
        if not all_metrics:
            st.info("📊 No performance metrics recorded yet.")
        else:
            # Convert to DataFrame
            metrics_data = []
            for m in all_metrics:
                metrics_data.append({
                    "Symbol": m.symbol,
                    "Predicted Action": m.predicted_action,
                    "Actual Return": m.actual_return,
                    "Predicted Median": m.predicted_median,
                    "Accuracy": "✓" if m.accuracy_flag else "✗",
                    "Date": m.created_at.strftime("%Y-%m-%d")
                })
            
            df_metrics = pd.DataFrame(metrics_data)
            
            # Summary stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                accuracy = (df_metrics["Accuracy"] == "✓").sum() / len(df_metrics) * 100
                st.metric("Overall Accuracy", f"{accuracy:.1f}%")
            
            with col2:
                avg_actual = df_metrics["Actual Return"].mean()
                st.metric("Avg Actual Return", f"{avg_actual:.2f}%")
            
            with col3:
                avg_predicted = df_metrics["Predicted Median"].mean()
                st.metric("Avg Predicted Return", f"{avg_predicted:.2f}%")
            
            st.divider()
            
            # Performance table
            st.subheader("Detailed Performance Metrics")
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)
            
            # Performance chart
            st.subheader("Actual vs Predicted Returns")
            
            fig = px.scatter(
                df_metrics,
                x="Predicted Median",
                y="Actual Return",
                color="Symbol",
                title="Predicted vs Actual Returns",
                labels={"Predicted Median": "Predicted Return (%)", "Actual Return": "Actual Return (%)"}
            )
            
            fig.add_shape(
                type="line",
                x0=df_metrics["Predicted Median"].min(),
                y0=df_metrics["Predicted Median"].min(),
                x1=df_metrics["Predicted Median"].max(),
                y1=df_metrics["Predicted Median"].max(),
                line=dict(dash="dash", color="gray"),
                name="Perfect Prediction"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    finally:
        session.close()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    Finance Genie v1.0 | Powered by Gemini + LangGraph | Last updated: 2025
</div>
""", unsafe_allow_html=True)
