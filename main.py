#!/usr/bin/env python
"""
ScamGraph AI - Main Entry Point
===============================
Supports running directly via:
- python main.py
- streamlit run main.py
- python run.py
"""

import os
import sys
from pathlib import Path

# Add src to Python path
BASE_DIR = Path(__file__).resolve().parent
src_path = BASE_DIR / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

app_path = src_path / "scamgraph" / "app.py"

if __name__ == "__main__":
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    # If not running in Streamlit, invoke Streamlit CLI
    if get_script_run_ctx() is None:
        import streamlit.web.cli as stcli
        sys.argv = [
            "streamlit",
            "run",
            str(app_path),
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false",
        ]
        sys.exit(stcli.main())
    else:
        # If already inside Streamlit (`streamlit run main.py`)
        import runpy
        runpy.run_path(str(app_path), run_name="__main__")
