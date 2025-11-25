# Finance Genie 💰

**AI-powered trading agent using Gemini, LangGraph, and PostgreSQL vector embeddings**

Finance Genie is a Python Streamlit MVP application that implements the GENIE-3-FINANCE world-model trading agent. It uses Google's Gemini API with LangGraph to analyze market data, news, and video transcripts to generate probabilistic trading decisions.

## Features

- **World Model Agent**: Predicts 5-day return distributions (median, Q25, Q75) using Gemini
- **Multi-Modal Analysis**: Combines OHLCV data, technical indicators, news, and video transcripts
- **Vector Memory**: PostgreSQL with pgvector for semantic search over past trading cycles
- **Streamlit Dashboard**: Interactive UI for viewing trading runs and performance metrics
- **Batch Analysis**: Run analysis on multiple symbols simultaneously
- **Audit Trail**: All trading decisions stored in PostgreSQL for compliance and backtesting
- **React Pattern Agent**: LangGraph-based agent with tool use and memory

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│  (Home.py, Run_Agent.py, Batch_Analysis.py)                │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              World Model Agent                              │
│  (LangGraph + Gemini 2.5 Flash)                            │
│                                                              │
│  Tools:                                                      │
│  - search_trading_news (Tavily)                            │
│  - download_trading_video (yt-dlp)                         │
│  - get_daily_ohlcv (EODHD API)                             │
│  - recall_vector_store (PostgreSQL)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│         PostgreSQL with pgvector Extension                  │
│                                                              │
│  Tables:                                                     │
│  - trading_runs: Run metadata                              │
│  - trading_decisions: Agent decisions (JSON output)        │
│  - performance_metrics: Backtesting results                │
│  - vecs: Vector embeddings (768-dim Gemini)               │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+ with pgvector extension
- API Keys:
  - Google Gemini API key
  - Tavily API key (for web search)
  - EODHD API key (for stock data)

### Step 1: Clone Repository

```bash
git clone https://github.com/kaljuvee/finance-genie.git
cd finance-genie
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
TAVILY_API_KEY=your_tavily_api_key
EODHD_API_KEY=your_eodhd_api_key
PGVECTOR_CONNECTION=postgresql://user:password@host:port/database
DB_SCHEMA=genie
ALPACA_PAPER_API_KEY=your_alpaca_key
ALPACA_PAPER_SECRET_KEY=your_alpaca_secret
```

### Step 5: Initialize Database

```bash
# Connect to PostgreSQL and run:
psql -U postgres -d your_database -f sql/init_schema.sql

# Or use Python:
python -c "from utils.db_util import init_db; init_db()"
```

## Usage

### CLI Mode (Single Symbol)

```bash
python world_model_agent.py
```

Then enter:
- Symbol: `NVDA`
- YouTube URL: (optional)

Example output:
```json
{
  "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "symbol": "NVDA",
  "decision": {
    "median": 3.1,
    "q25": -1.5,
    "q75": 6.8,
    "action": "BUY"
  },
  "timestamp": "2025-11-25T15:30:00.000000"
}
```

### Streamlit Dashboard

```bash
streamlit run Home.py
```

Then navigate to:
- **Dashboard**: View recent trading decisions and performance metrics
- **Run Agent**: Execute the world model for a single symbol
- **Batch Analysis**: Analyze multiple symbols simultaneously
- **Recent Runs**: Browse historical trading runs with details
- **Performance Analysis**: Review backtesting results and accuracy

## Project Structure

```
finance-genie/
├── Home.py                          # Main Streamlit dashboard
├── world_model_agent.py             # Core agent implementation
├── requirements.txt                 # Python dependencies
├── .env                             # Environment configuration
├── .env.sample                      # Environment template
├── README.md                        # This file
│
├── pages/
│   ├── 0_Run_Agent.py              # Single symbol analysis
│   └── 1_Batch_Analysis.py         # Batch processing
│
├── sql/
│   └── init_schema.sql             # PostgreSQL schema
│
├── utils/
│   └── db_util.py                  # SQLAlchemy models and DB operations
│
├── tests/
│   └── test_world_model.py         # Unit tests
│
├── data/                            # Output data storage
└── test-data/                       # Test datasets
```

## World Model Decision Logic

The GENIE-3-FINANCE agent follows this process:

1. **Data Collection**
   - Fetches 120-day OHLCV data with SMA20 and RSI14 indicators
   - Searches for recent trading news and analysis
   - Downloads YouTube video transcripts (if provided)
   - Recalls relevant memories from vector store

2. **Analysis** (Inside `<think>` tags)
   - Evaluates market sentiment from news and videos
   - Analyzes technical trends using indicators
   - Considers historical context from vector store
   - Reasons about potential 5-day outcomes

3. **Prediction**
   - Median return: Expected 5-day return percentage
   - Q25 (Downside): 25th percentile (worst case)
   - Q75 (Upside): 75th percentile (best case)

4. **Decision**
   - **BUY**: Median > 2% AND upside > downside risk
   - **SELL**: Median < -2% OR extreme downside risk
   - **HOLD**: All other cases

## Testing

Run unit tests to validate components:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_world_model.py::TestWorldModelAgent::test_agent_creation -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

Test categories:
- **Agent Creation**: Verify LangGraph agent initialization
- **Tool Functions**: Test individual tools (news search, data fetching, etc.)
- **Database Operations**: Validate SQLAlchemy models and CRUD operations
- **Configuration**: Check environment variables and dependencies
- **Data Models**: Verify data model structure and relationships

## Performance Optimization

### Vector Store Optimization
- Uses cosine distance for similarity search
- Caches embeddings in PostgreSQL
- Indexes on creation timestamp for efficient queries

### Agent Optimization
- Memory saver for checkpoint persistence
- Temperature set to 0.15 for consistent decisions
- Gemini 2.5 Flash for fast inference

### Database Optimization
- Indexes on `symbol`, `run_id`, and `created_at`
- Schema isolation in `genie` namespace
- Connection pooling via SQLAlchemy

## Improvements and Suggestions

### Completed Features
✅ World model with probabilistic predictions
✅ Multi-modal context (news, video, OHLCV)
✅ PostgreSQL vector store for memory
✅ Streamlit dashboard with performance tracking
✅ Batch analysis capability
✅ Comprehensive unit tests
✅ Database audit trail

### Future Enhancements
- [ ] Real-time trading execution via Alpaca API
- [ ] Daily scheduled runs with 24-hour sleep loop
- [ ] Custom LangGraph nodes for fetch/analyze/risk/trade separation
- [ ] Backtesting engine for strategy validation
- [ ] Risk management module (position sizing, stop-loss)
- [ ] Multi-symbol portfolio optimization
- [ ] Performance attribution analysis
- [ ] Alert system for significant signals
- [ ] API endpoint for external integration
- [ ] Advanced charting with technical analysis overlays

### Configuration Flexibility
- Model selection via `GEMINI_MODEL` environment variable
- Configurable vector store distance strategy
- Adjustable agent temperature for risk tolerance
- Customizable decision thresholds (BUY/SELL/HOLD)

## API Keys and Credentials

### Required Services

| Service | Key | Purpose |
|---------|-----|---------|
| Google Gemini | `GOOGLE_API_KEY` | LLM and embeddings |
| Tavily | `TAVILY_API_KEY` | Web search for news |
| EODHD | `EODHD_API_KEY` | Stock market data |
| PostgreSQL | `PGVECTOR_CONNECTION` | Vector store and audit trail |

### Optional Services

| Service | Key | Purpose |
|---------|-----|---------|
| Alpaca | `ALPACA_PAPER_API_KEY` | Paper trading execution |
| Alpaca | `ALPACA_PAPER_SECRET_KEY` | Paper trading authentication |

## Troubleshooting

### PostgreSQL Connection Issues
```bash
# Test connection
psql -U user -h host -d database -c "SELECT version();"

# Check pgvector extension
psql -U user -d database -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### API Key Errors
```bash
# Verify .env file is loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GOOGLE_API_KEY'))"
```

### Streamlit Issues
```bash
# Clear cache
streamlit cache clear

# Run with debug logging
streamlit run Home.py --logger.level=debug
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

**This is an educational and research tool. It is not financial advice.** Use at your own risk. Always conduct your own due diligence and consult with a financial advisor before making trading decisions.

## Support

For issues, questions, or suggestions:
1. Check existing GitHub issues
2. Review the troubleshooting section above
3. Create a new GitHub issue with detailed information

## Authors

- **Original Concept**: Genie-3 framework
- **Implementation**: Finance Genie Team
- **Contributors**: Community

## Changelog

### v1.0 (2025-11-25)
- Initial release
- World model agent with LangGraph
- Streamlit dashboard
- PostgreSQL vector store
- Batch analysis capability
- Comprehensive test suite
- Full documentation

---

**Last Updated**: 2025-11-25
**Status**: Active Development
