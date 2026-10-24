"""
ScamGraph AI - TinyFish Web Intelligence Adapter
================================================
Uses TinyFish API (when TINYFISH_API_KEY is configured in .env)
to perform automated OSINT verification of URLs and domains.
Strict rule: Never fabricates results or claims search succeeded when it failed.
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
    from tinyfish import TinyFish
    TINYFISH_AVAILABLE = True
except ImportError:
    TinyFish = None
    TINYFISH_AVAILABLE = False


def get_tinyfish_key() -> str | None:
    key = os.getenv("TINYFISH_API_KEY", "").strip()
    if not key or key == "your_tinyfish_api_key_here":
        return None
    return key


def is_tinyfish_active() -> bool:
    return TINYFISH_AVAILABLE and bool(get_tinyfish_key())


def inspect_url_with_tinyfish(url: str) -> dict | None:
    """
    Verifies a target URL using TinyFish AI agent.
    Returns analysis or None if TinyFish is unconfigured.
    """
    api_key = get_tinyfish_key()
    if not api_key or not TINYFISH_AVAILABLE:
        return None

    try:
        client = TinyFish(api_key=api_key)
        resp = client.agent.run(
            goal=f"Verify if this URL represents a legitimate entity or suspicious phishing/scam clone: {url}",
            url=url,
            output_schema={
                "type": "object",
                "properties": {
                    "is_suspicious": {"type": "boolean"},
                    "risk_score": {"type": "number"},
                    "summary": {"type": "string"}
                },
                "required": ["is_suspicious", "risk_score", "summary"]
            }
        )
        data = resp.result if hasattr(resp, "result") else {}
        return {
            "verified": True,
            "is_suspicious": bool(data.get("is_suspicious", False)),
            "risk_score": float(data.get("risk_score", 0.5)),
            "summary": data.get("summary", "TinyFish web verification completed.")
        }
    except Exception as e:
        return {
            "verified": False,
            "error": str(e),
            "summary": f"TinyFish OSINT query failed ({e})."
        }
