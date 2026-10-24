#!/usr/bin/env python
"""
ScamGraph AI - Run Script
Entry point for running the Streamlit application.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    import streamlit.web.cli as stcli

    # Get the app path
    app_path = src_path / "scamgraph" / "app.py"

    # Run streamlit
    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.port=8501",
        "--server.address=localhost",
        "--browser.gatherUsageStats=false",
    ]

    sys.exit(stcli.main())