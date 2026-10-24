"""
ScamGraph AI - TinyFish Web Intelligence Adapter Service
Provides a clean, unified interface for external public web research, domain reconnaissance,
and company career verification.
Includes strict SSRF checks, rate limiting, retry controls, and clear fallback states when unconfigured.
"""

import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.config import settings
from app.services.normalizer import normalizer, SSRFValidationError


class TinyFishService:
    """
    Adapter for TinyFish research API.
    All external OSINT / web extraction passes through this service.
    """

    def __init__(self):
        self.api_key = settings.TINYFISH_API_KEY
        self.base_url = settings.TINYFISH_API_BASE_URL.rstrip("/")
        self.is_enabled = settings.TINYFISH_ENABLED and bool(self.api_key)
        self.timeout = settings.TINYFISH_TIMEOUT_SECONDS
        self.max_retries = settings.TINYFISH_MAX_RETRIES

    def get_status(self) -> Dict[str, Any]:
        """Returns the operational status of the TinyFish service."""
        return {
            "enabled": self.is_enabled,
            "configured": bool(self.api_key),
            "base_url": self.base_url,
            "message": "TinyFish Intelligence Service is online" if self.is_enabled else "TinyFish research integration is disabled or API key is not configured. Falling back to local offline heuristic and database correlation.",
        }

    async def investigate_website(self, url: str) -> Dict[str, Any]:
        """
        Investigates a submitted website URL:
        - Performs SSRF validation
        - If enabled, queries TinyFish endpoint
        - If disabled or failed, returns structured fallback response
        """
        # 1. Strict SSRF check
        try:
            norm_url, norm_domain = normalizer.validate_and_normalize_url(url)
        except SSRFValidationError as e:
            return {
                "success": False,
                "error": str(e),
                "is_ssrf_blocked": True,
                "evidence": None,
            }
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid URL: {e}",
                "is_ssrf_blocked": False,
                "evidence": None,
            }

        # 2. If disabled, return clear message without pretending
        if not self.is_enabled:
            return {
                "success": False,
                "available": False,
                "service_status": "DISABLED",
                "message": "TinyFish API is not enabled. External live web scraping was skipped. Operating in offline rule-based mode.",
                "target_url": norm_url,
                "domain": norm_domain,
                "evidence": None,
            }

        # 3. Call TinyFish API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"ScamGraphAI/{settings.VERSION} (Threat Intelligence Ingest)",
            "Content-Type": "application/json",
        }
        payload = {
            "url": norm_url,
            "extract_contact_info": True,
            "extract_company_claims": True,
        }

        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/research/website",
                        headers=headers,
                        json=payload,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            "success": True,
                            "available": True,
                            "retrieval_timestamp": datetime.utcnow().isoformat(),
                            "source_url": norm_url,
                            "page_title": data.get("title", f"Webpage: {norm_domain}"),
                            "extracted_text": data.get("content_summary", ""),
                            "discovered_emails": data.get("emails", []),
                            "discovered_phones": data.get("phones", []),
                            "claims_supported": data.get("claims", []),
                            "evidence": {
                                "source_type": "TINYFISH_WEB_RESEARCH",
                                "url": norm_url,
                                "page_title": data.get("title", f"Recon: {norm_domain}"),
                                "retrieved_at": datetime.utcnow(),
                                "raw_content": data.get("raw_text", ""),
                                "claims": f"Live reconnaissance of {norm_domain}",
                            },
                        }
                    else:
                        if attempt == self.max_retries:
                            return {
                                "success": False,
                                "available": True,
                                "error": f"TinyFish API returned status code {response.status_code}: {response.text[:200]}",
                                "evidence": None,
                            }
            except (httpx.RequestError, httpx.TimeoutException) as exc:
                if attempt == self.max_retries:
                    return {
                        "success": False,
                        "available": True,
                        "error": f"TinyFish network request failed after {self.max_retries} retries: {str(exc)}",
                        "evidence": None,
                    }

        return {"success": False, "error": "Unknown error during TinyFish lookup", "evidence": None}

    async def verify_recruiter_company(self, company_name: str, recruiter_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Cross-checks corporate identity against public directories and career pages.
        """
        if not self.is_enabled:
            return {
                "success": False,
                "available": False,
                "service_status": "DISABLED",
                "message": "External public web intelligence disabled.",
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"company_name": company_name, "recruiter_name": recruiter_name}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/research/verify-company", headers=headers, json=payload)
                if res.status_code == 200:
                    return {"success": True, "data": res.json()}
                return {"success": False, "error": f"TinyFish returned HTTP {res.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


tinyfish_service = TinyFishService()
