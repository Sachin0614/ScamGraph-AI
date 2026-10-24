"""
ScamGraph AI - Basic Tests
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_imports():
    """Test that all modules can be imported."""
    import scamgraph
    from scamgraph.config import config, setup_logging, get_logger
    from scamgraph.database import db, get_db
    from scamgraph.utils import (
        generate_id,
        sanitize_text,
        extract_emails,
        extract_phones,
        extract_domains,
        extract_urls,
        calculate_risk_score,
    )
    from scamgraph.ui import (
        get_theme,
        get_risk_level,
        get_risk_color,
        render_sidebar,
    )

    print("[OK] All imports successful")


def test_config():
    """Test configuration loading."""
    from scamgraph.config import config

    assert config.app.name == "ScamGraph AI"
    assert config.app.version == "1.0.0"
    assert config.database.path == "data/scamgraph.db"
    assert config.streamlit.port == 8501

    print("[OK] Configuration loading works")


def test_database():
    """Test database initialization."""
    from scamgraph.database import Database

    # Use in-memory database for testing
    db = Database(":memory:")

    # Test connection
    with db.get_connection() as conn:
        result = conn.execute("SELECT 1 as test").fetchone()
        assert result["test"] == 1

    print("[OK] Database initialization works")


def test_utils():
    """Test utility functions."""
    from scamgraph.utils import (
        generate_id,
        sanitize_text,
        extract_emails,
        extract_phones,
        extract_domains,
        extract_urls,
        calculate_risk_score,
    )

    # Test ID generation
    id1 = generate_id("test_")
    import time
    time.sleep(0.001)
    id2 = generate_id("test_")
    assert id1 != id2
    assert id1.startswith("test_")

    # Test sanitize
    assert sanitize_text("  hello  ") == "hello"
    assert sanitize_text("") == ""
    assert "\x00" not in sanitize_text("test\x00null")

    # Test extractors
    text = "Contact john@example.com or call (555) 123-4567. Visit https://evil-site.com"
    assert "john@example.com" in extract_emails(text)
    assert "(555) 123-4567" in extract_phones(text)
    assert "evil-site.com" in extract_domains(text)
    assert "https://evil-site.com" in extract_urls(text)

    # Test risk score
    score = calculate_risk_score({"phishing": 0.9, "malware": 0.8}, {"phishing": 2.0, "malware": 1.0})
    assert 0 <= score <= 100

    print("[OK] Utility functions work")


def test_theme():
    """Test theme functions."""
    from scamgraph.ui import get_theme, get_risk_level, get_risk_color

    theme = get_theme()
    assert theme["primary"] == "#00D4AA"
    assert theme["background"] == "#0E1117"

    assert get_risk_level(90) == "critical"
    assert get_risk_level(70) == "high"
    assert get_risk_level(50) == "medium"
    assert get_risk_level(30) == "low"
    assert get_risk_level(10) == "none"

    assert get_risk_color(90) == "#FC8181"
    assert get_risk_color(30) == "#00D4AA"

    print("[OK] Theme functions work")


if __name__ == "__main__":
    print("Running ScamGraph AI tests...\n")

    test_imports()
    test_config()
    test_database()
    test_utils()
    test_theme()

    print("\n[OK] All tests passed!")