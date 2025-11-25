# Finance Genie - Quick Start Guide

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/kaljuvee/finance-genie.git
cd finance-genie
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file with your API keys:
```bash
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
EODHD_API_KEY=your_eodhd_api_key
PGVECTOR_CONNECTION=postgresql://user:password@localhost:5432/genie
DB_SCHEMA=genie
```

### 4. Initialize Database (Optional)
```bash
python -c "from utils.db_util import init_db; init_db()"
```

## Running the Application

### Start Streamlit Dashboard
```bash
streamlit run Home.py
```

The dashboard will be available at `http://localhost:8501`

## Features

### 📊 Dashboard
View trading runs, decisions, and performance metrics in real-time.

### 🤖 Run Agent
Generate trading decisions for individual stocks using the world model.

### 📈 Batch Analysis
Analyze multiple stocks at once with CSV upload support.

### 🔧 System Status
Monitor database connectivity, API configuration, and system health.

## API Keys Required

1. **Google Gemini API**: https://ai.google.dev/
2. **Tavily Search API**: https://tavily.com/
3. **EODHD Stock Data**: https://eodhd.com/

## Database Setup

### PostgreSQL with pgvector

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

# Create database
CREATE DATABASE genie;

# Create schema
CREATE SCHEMA genie;
```

## Testing

```bash
# Run unit tests
pytest tests/ -v

# Run specific test
pytest tests/test_world_model.py::test_search_trading_news -v
```

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check PGVECTOR_CONNECTION in .env
- Verify database and schema exist

### API Key Errors
- Verify all required API keys in .env
- Check API key validity and rate limits
- Ensure environment variables are loaded

### Streamlit Port Already in Use
```bash
streamlit run Home.py --server.port 8502
```

## Architecture

### Components
- **Streamlit Frontend**: Multi-page dashboard
- **LangGraph Agent**: React pattern trading agent
- **Gemini LLM**: Reasoning and decision making
- **PostgreSQL**: Data persistence with pgvector
- **Tavily API**: Web search for market news
- **EODHD API**: Stock price data

### Data Flow
1. User inputs stock symbol
2. Agent collects data (OHLCV, news, videos)
3. Agent analyzes using LLM reasoning
4. Agent predicts 5-day return distribution
5. Agent makes BUY/SELL/HOLD decision
6. Results stored in PostgreSQL
7. Dashboard displays results

## Performance

- **Page Load**: < 2 seconds
- **Agent Runtime**: 15-25 seconds per symbol
- **Database Query**: < 500ms
- **Memory Usage**: 200-300 MB

## Support

For issues and questions:
1. Check TESTING_REPORT.md for known issues
2. Review inline code documentation
3. Check .env configuration
4. Verify API key validity

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

---

**Version**: 1.0 MVP  
**Last Updated**: November 25, 2025
