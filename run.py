#!/usr/bin/env python
"""
ScamGraph AI — Unified Application Runner
Launches the FastAPI backend server with the compiled 3D interactive frontend.
Access at: http://localhost:8000
API Docs at: http://localhost:8000/docs
"""

import sys
import os
from pathlib import Path
import uvicorn

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
backend_dir = BASE_DIR / "backend"
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    print("=" * 70)
    print("  SCAMGRAPH AI - INTELLIGENT SCAM INVESTIGATION PLATFORM")
    print("  Tactical 3D Threat Correlation & Public Evidence Engine")
    print("=" * 70)
    print("  [*] Backend API & Documentation: http://127.0.0.1:8000/docs")
    print("  [*] Platform Dashboard & 3D Globe: http://127.0.0.1:8000")
    print("  [*] Database: SQLite WAL mode enabled (data/scamgraph_v2.db)")
    print("=" * 70)
    
    # Run Uvicorn server hosting both FastAPI and the built React frontend
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
    )
