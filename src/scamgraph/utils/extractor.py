"""
ScamGraph AI - Forensic Indicator Extractor
===========================================
Extracts authentic digital indicators (RFC emails, domains, URLs, phones, IPs)
from incoming email content. Strictly extracts only evidence actually present.
"""

import re
from urllib.parse import urlparse


EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
URL_REGEX = re.compile(r"https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+91[-.\s]?\d{10}")
IPV4_REGEX = re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")


def extract_sender_email(sender_raw: str) -> tuple[str, str, str]:
    """
    Extracts display name, clean email address, and domain from a From header.
    Example: "PayPal Support <security@paypal-update.xyz>" -> ("PayPal Support", "security@paypal-update.xyz", "paypal-update.xyz")
    """
    if not sender_raw:
        return "Unknown Sender", "unknown@domain.com", "domain.com"

    match = re.search(r"<([^>]+)>", sender_raw)
    if match:
        email_addr = match.group(1).strip().lower()
        display_name = sender_raw.split("<")[0].strip().strip('"').strip("'")
        if not display_name:
            display_name = email_addr
    else:
        email_match = EMAIL_REGEX.search(sender_raw)
        if email_match:
            email_addr = email_match.group(0).strip().lower()
            display_name = sender_raw.strip()
        else:
            email_addr = sender_raw.strip().lower()
            display_name = sender_raw.strip()

    # Domain
    domain = email_addr.split("@")[-1] if "@" in email_addr else "unknown.com"
    return display_name, email_addr, domain


def extract_forensic_indicators(text: str) -> dict:
    """
    Extracts all real forensic indicators actually present in the text.
    Never invents or fabricates entities.
    """
    if not text:
        return {
            "urls": [],
            "domains": [],
            "phones": [],
            "ips": []
        }

    # URLs
    raw_urls = URL_REGEX.findall(text)
    urls = list(dict.fromkeys([u.rstrip(".,;!?'\")>]") for u in raw_urls]))

    # Domains from URLs
    domains = set()
    for u in urls:
        try:
            parsed = urlparse(u)
            if parsed.netloc:
                clean_netloc = parsed.netloc.split(":")[0].lower()
                domains.add(clean_netloc)
        except Exception:
            pass

    # Phone numbers
    phones = list(dict.fromkeys(PHONE_REGEX.findall(text)))

    # IPs (filter out common local/subnet like 127.0.0.1)
    raw_ips = IPV4_REGEX.findall(text)
    ips = [ip for ip in dict.fromkeys(raw_ips) if not ip.startswith(("127.", "0.", "255."))]

    return {
        "urls": urls,
        "domains": sorted(list(domains)),
        "phones": phones,
        "ips": ips
    }
