"""World Model Agent - GENIE-3-FINANCE trading agent using LangGraph and Gemini."""

import os
import json
import requests
import pandas as pd
import ta as ta_lib
from typing import List, Dict, Any
from datetime import datetime
import uuid

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from tavily import TavilyClient
import yt_dlp
from dotenv import load_dotenv

from utils.db_util import (
    store_trading_run, 
    store_trading_decision,
    get_session,
    TradingRun
)

load_dotenv()

# ---------- Load API Keys ----------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AV_KEY = os.getenv("EODHD_API_KEY")
PGVECTOR_CONNECTION = os.getenv("PGVECTOR_CONNECTION")

if not all([GOOGLE_API_KEY, TAVILY_API_KEY, PGVECTOR_CONNECTION]):
    raise ValueError("Missing required environment variables")

# ---------- Initialize Embeddings & Vector Store ----------
embed = None
vectorstore = None

def get_vectorstore():
    """Lazily initialize vector store on first use."""
    global embed, vectorstore
    if vectorstore is None:
        embed = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=GOOGLE_API_KEY
        )
        vectorstore = PGVector(
            connection_string=PGVECTOR_CONNECTION,
            embedding_function=embed,
            collection_name="world_docs",
            distance_strategy="cosine"
        )
    return vectorstore

# ---------- Initialize External Services ----------
tavily = TavilyClient(api_key=TAVILY_API_KEY)


def av_daily(symbol: str):
    """Fetch daily OHLCV data from Alpha Vantage."""
    try:
        # Using EODHD API as fallback
        url = f"https://eodhd.com/api/eod/{symbol}.US"
        params = {"api_token": AV_KEY, "fmt": "json"}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


# ---------- LangGraph Tools ----------
@tool
def search_trading_news(query: str) -> str:
    """Search web for recent trading-related news and analysis."""
    try:
        ans = tavily.search(query, max_results=5, include_answer=True)
        # Store in vector database for retrieval later
        try:
            vs = get_vectorstore()
            vs.add_texts([json.dumps(ans)])
        except Exception as db_err:
            print(f"Warning: Could not store to vector DB: {db_err}")
        return json.dumps(ans)
    except Exception as e:
        return f"Error searching news: {e}"


@tool
def download_trading_video(youtube_url: str) -> str:
    """Download and extract transcript from a trading YouTube video."""
    try:
        ydl_opts = {
            "skip_download": True,
            "writeautomaticsub": True,
            "subformat": "vtt"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            vtt_path = ydl.prepare_filename(info).replace(".webm", ".en.vtt")
        
        with open(vtt_path, errors="ignore") as f:
            text = " ".join([l for l in f if "-->" not in l and not l.startswith("WEBVTT")])
        
        # Store in vector database
        try:
            vs = get_vectorstore()
            vs.add_texts([text])
        except Exception as db_err:
            print(f"Warning: Could not store to vector DB: {db_err}")
        return text[:10_000]
    except Exception as e:
        return f"Error downloading video: {e}"


@tool
def get_daily_ohlcv(symbol: str) -> str:
    """Return 120-day OHLCV + SMA20 + RSI14 as CSV string."""
    try:
        data = av_daily(symbol)
        if not data or isinstance(data, dict) and "error" in data:
            return f"Error: Unable to fetch data for {symbol}"
        
        # Parse EODHD format
        if isinstance(data, list):
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index(ascending=False).head(120)[::-1]
            df = df.astype(float)
        else:
            return "Error: Unexpected data format"
        
        # Add technical indicators
        df['SMA_20'] = ta_lib.trend.sma_indicator(df['close'], window=20)
        df['RSI_14'] = ta_lib.momentum.rsi(df['close'], window=14)
        
        return df.to_csv()
    except Exception as e:
        return f"Error getting OHLCV data: {e}"


@tool
def recall_vector_store(query: str) -> List[str]:
    """Semantic search over past news, videos, and analysis."""
    try:
        vs = get_vectorstore()
        docs = vs.similarity_search(query, k=4)
        return [d.page_content for d in docs]
    except Exception as e:
        return [f"Error recalling vector store: {e}"]


# ---------- World Model System Prompt ----------
WORLD_MODEL_SYSTEM = """You are GENIE-3-FINANCE, a world-model trading agent.

You receive:
- Recent news snippets and market analysis
- Transcript of a trading video (if provided)
- 120-day OHLCV data with SMA20 and RSI14 indicators
- Optionally, retrieved memories from past trading cycles

Your job:
1. Inside <think>…</think> reason step-by-step about:
   - Market sentiment from news
   - Technical trend analysis from OHLCV + indicators
   - Video insights if available
   - Historical context from vector store memories

2. Predict the 5-day ahead return distribution for the symbol:
   - median return % (expected value)
   - 25-percentile (downside risk)
   - 75-percentile (upside potential)

3. Decide one ACTION: {BUY, SELL, HOLD}
   - BUY if median > 2% and upside > downside risk
   - SELL if median < -2% or downside risk is extreme
   - HOLD otherwise

4. Output ONLY valid JSON (no other text):
{"median":float,"q25":float,"q75":float,"action":"BUY|SELL|HOLD"}
"""


# ---------- Initialize LLM and Agent ----------
def create_world_model_agent():
    """Create and return the world model agent."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.15,
        google_api_key=GOOGLE_API_KEY
    )
    
    tools = [
        search_trading_news,
        download_trading_video,
        get_daily_ohlcv,
        recall_vector_store
    ]
    
    agent = create_react_agent(
        llm.bind(system=WORLD_MODEL_SYSTEM),
        tools,
        checkpointer=MemorySaver()
    )
    
    return agent


# ---------- Main Trading Logic ----------
def run_world_model(symbol: str, youtube_url: str = None) -> Dict[str, Any]:
    """
    Run the world model agent for a given symbol.
    
    Args:
        symbol: Stock symbol (e.g., 'NVDA')
        youtube_url: Optional YouTube URL for trading video
    
    Returns:
        Dictionary with trading decision and metadata
    """
    # Generate unique run ID
    run_id = str(uuid.uuid4())
    
    # Store trading run
    store_trading_run(run_id, symbol, youtube_url)
    
    # Create agent
    agent = create_world_model_agent()
    
    # Prepare input message
    user_message = f"Symbol: {symbol}"
    if youtube_url:
        user_message += f"\nYouTube: {youtube_url}"
    
    # Run agent
    thread = {"configurable": {"thread_id": run_id}}
    
    try:
        print(f"[{run_id}] Running world model for {symbol}...")
        
        for step in agent.stream(
            {"messages": [("user", user_message)]},
            thread
        ):
            pass
        
        # Extract decision from last message
        last_message = step["messages"][-1].content
        
        # Parse JSON from response
        try:
            json_part = "{" + last_message.split("{", 1)[1].rsplit("}", 1)[0] + "}"
            decision = json.loads(json_part)
        except Exception as e:
            decision = {"error": "Failed to parse JSON", "raw": last_message}
        
        # Store decision in database
        if "error" not in decision:
            store_trading_decision(
                run_id=run_id,
                symbol=symbol,
                median=decision.get("median"),
                q25=decision.get("q25"),
                q75=decision.get("q75"),
                action=decision.get("action"),
                raw_response=last_message
            )
        
        return {
            "run_id": run_id,
            "symbol": symbol,
            "decision": decision,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        print(f"[{run_id}] Error running world model: {e}")
        return {
            "run_id": run_id,
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    # CLI interface
    symbol = input("Symbol (e.g., NVDA): ").upper().strip()
    yt = input("YouTube URL (or ENTER to skip): ").strip()
    
    result = run_world_model(symbol, yt if yt else None)
    
    print("\n----- WORLD-MODEL DECISION -----")
    print(json.dumps(result, indent=2))
