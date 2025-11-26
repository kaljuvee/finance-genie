# Finance Genie CLI Guide

The Finance Genie CLI provides command-line access to the world model trading agent without requiring the Streamlit dashboard.

## Installation

```bash
cd /path/to/finance-genie
pip install -r requirements.txt
```

## Quick Start

### Run tests
```bash
python cli.py --test
```

### Check system status
```bash
python cli.py --status
```

### Analyze a single stock
```bash
python cli.py --symbol NVDA
```

### Analyze with YouTube video
```bash
python cli.py --symbol NVDA --youtube "https://youtu.be/..."
```

### Batch analysis
```bash
python cli.py --batch symbols.txt
```

## Commands

### `--test`
Run the local test suite to verify system health.

**Output:**
- Tests 8 components (imports, database, API keys, etc.)
- Shows pass/fail status for each test
- Displays overall pass rate

**Example:**
```bash
$ python cli.py --test
================================================================================
  Finance Genie - Local Tests
================================================================================
🧪 Test 1: Importing world_model_agent...
   ✅ PASSED: All functions imported successfully
...
🎉 All tests passed!
```

### `--status`
Display system status and configuration.

**Output:**
- Python version and platform
- Database connectivity status
- API key configuration status
- Database statistics (trading runs, decisions, metrics)

**Example:**
```bash
$ python cli.py --status
================================================================================
  Finance Genie - System Status
================================================================================
🔧 System Information:
  Python Version: 3.11.0rc1
  Platform: linux

📊 Database Status:
  ✅ Database Available: Yes
  📍 Schema: genie
  📈 Trading Runs: 0
  🎯 Trading Decisions: 0
  📊 Performance Metrics: 0

🔑 API Configuration:
  GOOGLE_API_KEY: ✅ Set
  TAVILY_API_KEY: ✅ Set
  EODHD_API_KEY: ✅ Set
  PGVECTOR_CONNECTION: ✅ Set
```

### `--symbol SYMBOL`
Analyze a single stock symbol.

**Parameters:**
- `SYMBOL`: Stock ticker symbol (e.g., NVDA, AAPL, TSLA)
- `--youtube` (optional): YouTube URL for video analysis

**Output:**
- Trading decision (BUY/SELL/HOLD)
- Predicted median return
- Downside risk (Q25)
- Upside potential (Q75)
- Run ID and timestamp
- Results saved to JSON file

**Example:**
```bash
$ python cli.py --symbol NVDA
================================================================================
  Running World Model Agent for NVDA
================================================================================

📊 Input Parameters:
  Symbol: NVDA

🔄 Running agent (this may take 15-25 seconds)...

🟢 Action: BUY
📈 Median Return: 3.45%
📉 Downside Risk (Q25): -2.15%
📈 Upside Potential (Q75): 8.90%

📌 Run ID: run_20251126_075230_nvda
⏰ Timestamp: 2025-11-26T07:52:30.123456
💾 Status: Saved to database

💾 Results saved to: results_NVDA_20251126_075230.json
```

### `--batch BATCH`
Analyze multiple symbols from a file.

**Parameters:**
- `BATCH`: Path to file with symbols (one per line)

**Output:**
- Progress for each symbol
- Summary statistics (successful runs, BUY/SELL/HOLD counts)
- Results saved to JSON file

**Example:**
```bash
$ python cli.py --batch symbols.txt
================================================================================
  Batch Analysis: 5 Symbols
================================================================================

📊 Symbols to analyze:
  1. NVDA
  2. AAPL
  3. TSLA
  4. AMD
  5. MSFT

================================================================================
  Processing 1/5: NVDA
================================================================================
✅ NVDA: BUY (Median: 3.45%)

================================================================================
  Processing 2/5: AAPL
================================================================================
✅ AAPL: HOLD (Median: 0.82%)

...

📊 Batch Analysis Summary
--------------------------------------------------------------------------------
✅ Successful: 5/5
🟢 BUY Signals: 2
🔴 SELL Signals: 1
🟡 HOLD Signals: 2

💾 Batch results saved to: batch_results_20251126_075230.json
```

### `--recent`
Show recent trading runs from the database.

**Output:**
- List of recent trading runs (up to 10)
- Symbol, timestamp, and decision for each run
- YouTube URL if provided

**Example:**
```bash
$ python cli.py --recent
================================================================================
  Recent Trading Runs
================================================================================

📊 Found 3 recent trading runs:

1. Run ID: run_20251126_075230_nvda
   Symbol: NVDA
   Created: 2025-11-26 07:52:30
   Decision: BUY (Median: 3.45%)

2. Run ID: run_20251126_075145_aapl
   Symbol: AAPL
   Created: 2025-11-26 07:51:45
   Decision: HOLD (Median: 0.82%)

3. Run ID: run_20251126_075100_tsla
   Symbol: TSLA
   Created: 2025-11-26 07:51:00
   Decision: SELL (Median: -1.23%)
```

## Output Files

### Single Symbol Results
- **Filename**: `results_{SYMBOL}_{TIMESTAMP}.json`
- **Contents**: Complete analysis results including decision, predictions, and reasoning

### Batch Results
- **Filename**: `batch_results_{TIMESTAMP}.json`
- **Contents**: Array of results for all analyzed symbols

### JSON Structure

```json
{
  "run_id": "run_20251126_075230_nvda",
  "symbol": "NVDA",
  "timestamp": "2025-11-26T07:52:30.123456",
  "youtube_url": null,
  "decision": {
    "action": "BUY",
    "median": 3.45,
    "q25": -2.15,
    "q75": 8.90,
    "reasoning": "..."
  },
  "data": {
    "ohlcv": {...},
    "technical_indicators": {...},
    "news_sentiment": {...}
  }
}
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
EODHD_API_KEY=your_eodhd_api_key
PGVECTOR_CONNECTION=postgresql://user:password@localhost:5432/genie
DB_SCHEMA=genie
```

### API Keys

1. **Google Gemini API**: https://ai.google.dev/
2. **Tavily Search API**: https://tavily.com/
3. **EODHD Stock Data**: https://eodhd.com/

## Examples

### Example 1: Run Tests
```bash
python cli.py --test
```

### Example 2: Check System Status
```bash
python cli.py --status
```

### Example 3: Analyze Single Stock
```bash
python cli.py --symbol NVDA
```

### Example 4: Analyze with YouTube Video
```bash
python cli.py --symbol NVDA --youtube "https://youtu.be/dQw4w9WgXcQ"
```

### Example 5: Batch Analysis
```bash
# Create symbols.txt with one symbol per line
echo "NVDA" > symbols.txt
echo "AAPL" >> symbols.txt
echo "TSLA" >> symbols.txt

# Run batch analysis
python cli.py --batch symbols.txt
```

### Example 6: View Recent Runs
```bash
python cli.py --recent
```

## Performance

- **Single Symbol Analysis**: 15-25 seconds
- **Batch Analysis**: 15-25 seconds per symbol
- **Test Suite**: < 5 seconds
- **Status Check**: < 2 seconds

## Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt
```

### Database Connection Error
```bash
python -c "from utils.db_util import init_db; init_db()"
```

### API Key Errors
```bash
# Verify API keys in .env
cat .env

# Check environment variables
echo $GOOGLE_API_KEY
```

### File Not Found
```bash
# Ensure you're in the project directory
cd /path/to/finance-genie
pwd
```

## Advanced Usage

### Redirect Output to File
```bash
python cli.py --symbol NVDA > results.txt 2>&1
```

### Run Batch Analysis with Logging
```bash
python cli.py --batch symbols.txt 2>&1 | tee batch_analysis.log
```

### Schedule Regular Analysis
```bash
# Run daily at 9 AM
0 9 * * * cd /path/to/finance-genie && python cli.py --batch symbols.txt
```

## Integration with Other Tools

### Use Results in Python
```python
import json

# Load results
with open('results_NVDA_20251126_075230.json') as f:
    results = json.load(f)

# Access decision
action = results['decision']['action']
median_return = results['decision']['median']

print(f"Action: {action}, Median Return: {median_return}%")
```

### Export to CSV
```bash
python cli.py --batch symbols.txt
python << 'EOF'
import json
import csv

with open('batch_results_*.json') as f:
    results = json.load(f)

with open('results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Symbol', 'Action', 'Median', 'Q25', 'Q75'])
    for r in results:
        d = r['decision']
        writer.writerow([r['symbol'], d['action'], d['median'], d['q25'], d['q75']])
EOF
```

## Support

For issues and questions:
1. Run `python cli.py --test` to verify system health
2. Check `.env` configuration
3. Review error messages and logs
4. See TESTING_REPORT.md for known issues

## Version

CLI Version: 1.0  
Last Updated: November 26, 2025
