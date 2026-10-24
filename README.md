# ScamGraph AI

A modern, dark-themed AI-powered scam investigation platform built with Python and Streamlit.

## Overview

ScamGraph AI is designed for security researchers, fraud analysts, and cybersecurity professionals to investigate, visualize, and mitigate scam campaigns. The platform provides a modular architecture ready for AI agent integration, graph-based analysis, and automated evidence collection.

## Current Status: Phase 1 - Foundation ✅

- [x] Project structure & configuration management
- [x] Dark theme dashboard UI with Streamlit
- [x] SQLite database with investigation schema
- [x] Logging & error handling
- [x] Modular architecture for future features
- [x] Environment-based configuration

## Planned Phases

| Phase | Features |
|-------|----------|
| **Phase 2** | Gmail API integration, evidence ingestion pipeline |
| **Phase 3** | Supervisor Agent with specialist agents (Email, Header, URL, Crypto, Attribution) |
| **Phase 4** | TinyFish research integration, evidence-based risk scoring |
| **Phase 5** | Interactive ScamGraph visualization (Plotly/NetworkX) |
| **Phase 6** | Safe email actions (report phishing, block sender, archive) |

## Quick Start

### Prerequisites

- Python 3.10+
- Windows PowerShell (or any terminal)

### Installation

```powershell
# Navigate to project directory
cd E:\ScamGraph_AI

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env

# Run the application
python run.py
```

The application will open at `http://localhost:8501`

### Alternative Run Command

```powershell
# Direct streamlit command
streamlit run src\scamgraph\app.py
```

## Project Structure

```
ScamGraph_AI/
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
├── run.py              # Application entry point
├── README.md           # This file
├── data/               # Database files (gitignored)
├── logs/               # Application logs (gitignored)
├── src/
│   └── scamgraph/
│       ├── __init__.py
│       ├── app.py              # Main Streamlit app
│       ├── config/
│       │   ├── __init__.py
│       │   ├── config.py       # Configuration management
│       │   └── logging.py      # Logging setup
│       ├── database/
│       │   ├── __init__.py
│       │   └── database.py     # SQLite database wrapper
│       ├── utils/
│       │   ├── __init__.py
│       │   └── helpers.py      # Utility functions
│       └── ui/
│           ├── __init__.py
│           ├── theme.py        # Dark theme configuration
│           ├── sidebar.py      # Navigation sidebar
│           └── pages/
│               ├── __init__.py
│               ├── dashboard.py
│               ├── investigations.py
│               ├── evidence.py
│               ├── graph.py
│               └── settings.py
└── tests/              # Test files
```

## Configuration

All configuration is managed through environment variables. Copy `.env.example` to `.env` and customize:

```bash
# Application
APP_NAME=ScamGraph AI
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_PATH=data/scamgraph.db

# Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
STREAMLIT_THEME_BASE=dark

# Future Integrations (add when needed)
# GMAIL_CLIENT_ID=your_client_id
# GMAIL_CLIENT_SECRET=your_client_secret
# OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key
# TINYFISH_API_KEY=your_tinyfish_key
```

## Database Schema

The SQLite database includes tables for:

- **users** - User accounts (future auth)
- **investigations** - Scam investigation cases
- **evidence** - Collected artifacts (emails, phones, domains, etc.)
- **entities** - Graph nodes (extracted indicators)
- **relationships** - Graph edges (connections between entities)
- **agent_runs** - AI agent execution tracking

## Development

### Code Style

```powershell
# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

### Testing

```powershell
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/scamgraph --cov-report=html
```

## Security Notes

- **Never commit `.env` file** - It contains API keys and secrets
- Use strong, unique `SECRET_KEY` in production
- Rotate API keys regularly
- Database files in `data/` are gitignored
- Log files in `logs/` are gitignored

## Disclaimer

This is a development framework. **No real investigation results are generated in Phase 1.** All data shown in the UI is placeholder/sample data for UI demonstration purposes only. Future phases will implement actual AI-powered analysis.

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

- Issues: [GitHub Issues](https://github.com/scamgraph/scamgraph-ai/issues)
- Documentation: [Wiki](https://github.com/scamgraph/scamgraph-ai/wiki)