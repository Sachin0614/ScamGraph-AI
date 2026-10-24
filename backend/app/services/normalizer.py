"""
ScamGraph AI - Digital Indicator Normalizer and Security Validator
Normalizes domains, emails, phone numbers, UPI/payment IDs, and URLs with strict validation.
Includes SSRF and dangerous URL prevention.
"""

import re
import ipaddress
from urllib.parse import urlparse
from typing import Optional, Dict, Any, Tuple


class SSRFValidationError(Exception):
    """Raised when a URL targets a loopback, private, or prohibited host."""
    pass


class IndicatorNormalizer:
    """Normalizes digital indicators for consistent identity resolution and relationship detection."""

    # Prohibited local and private IP ranges for SSRF prevention
    PROHIBITED_IP_NETWORKS = [
        ipaddress.ip_network("127.0.0.0/8"),
        ipaddress.ip_network("10.0.0.0/8"),
        ipaddress.ip_network("172.16.0.0/12"),
        ipaddress.ip_network("192.168.0.0/16"),
        ipaddress.ip_network("169.254.0.0/16"),  # Link-local / Cloud metadata (AWS, GCP, Azure)
        ipaddress.ip_network("0.0.0.0/8"),
        ipaddress.ip_network("::1/128"),
        ipaddress.ip_network("fc00::/7"),
        ipaddress.ip_network("fe80::/10"),
    ]

    PROHIBITED_HOSTNAMES = {
        "localhost",
        "metadata.google.internal",
        "metadata",
        "169.254.169.254",
        "instance-data",
    }

    # Strict regex patterns
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    UPI_REGEX = re.compile(r"^[\w.\-_]{2,256}@[a-zA-Z]{2,64}$")
    PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\(\)\.]{7,25}$")

    @classmethod
    def normalize_domain(cls, domain_or_url: str) -> Optional[str]:
        """
        Extract and normalize domain/hostname:
        - Lowercases
        - Strips whitespace, protocol (http/https), port, trailing slashes, path, and credentials
        - Strips leading 'www.'
        - Validates length and character set
        """
        if not domain_or_url or not isinstance(domain_or_url, str):
            return None

        val = domain_or_url.strip().lower()
        if not val:
            return None

        # Add dummy scheme if missing so urlparse handles authority correctly
        if "://" not in val:
            val = "http://" + val

        try:
            parsed = urlparse(val)
            netloc = parsed.netloc or parsed.path.split("/")[0]
            # Strip port if present
            hostname = netloc.split(":")[0].strip()
            # Remove leading www.
            if hostname.startswith("www."):
                hostname = hostname[4:]

            # Validate valid domain syntax
            if not hostname or "." not in hostname:
                return None
            if re.match(r"^[a-z0-9][a-z0-9\.\-]{0,253}[a-z0-9]$", hostname):
                return hostname
            return None
        except Exception:
            return None

    @classmethod
    def normalize_email(cls, email: str) -> Optional[str]:
        """
        Normalizes email:
        - Trim whitespace
        - Lowercase
        - Validate standard RFC-compliant format
        """
        if not email or not isinstance(email, str):
            return None
        val = email.strip().lower()
        if cls.EMAIL_REGEX.match(val):
            return val
        return None

    @classmethod
    def normalize_phone(cls, phone: str) -> Optional[str]:
        """
        Normalizes phone numbers:
        - Strips formatting symbols (spaces, dashes, parens)
        - Handles standard Indian numbers (10 digits starting with 6,7,8,9 -> adds +91)
        - Handles international numbers prefixed with +
        """
        if not phone or not isinstance(phone, str):
            return None

        raw = phone.strip()
        # Keep leading + if present
        has_plus = raw.startswith("+")
        digits = re.sub(r"\D", "", raw)

        if len(digits) < 7 or len(digits) > 15:
            return None

        # If it's a 10 digit number starting with 6-9, standard Indian mobile
        if len(digits) == 10 and digits[0] in "6789":
            return f"+91{digits}"

        # If it's an 11 or 12 digit number starting with 91 or 0
        if len(digits) == 12 and digits.startswith("91") and digits[2] in "6789":
            return f"+{digits}"
        if len(digits) == 11 and digits.startswith("0") and digits[1] in "6789":
            return f"+91{digits[1:]}"

        if has_plus:
            return f"+{digits}"

        return digits

    @classmethod
    def normalize_payment_id(cls, payment_id: str) -> Optional[str]:
        """
        Normalizes payment indicators:
        - UPI ID (e.g., merchant@okaxis, fraudster@ybl, hrteam@paytm)
        - Crypto wallet addresses (BTC, ETH, TRX, USDT)
        - Bank account / IFSC combinations
        """
        if not payment_id or not isinstance(payment_id, str):
            return None

        val = payment_id.strip()
        # Check UPI
        if cls.UPI_REGEX.match(val.lower()):
            return val.lower()

        # Check Ethereum/EVM address
        if re.match(r"^0x[a-fA-F0-9]{40}$", val):
            return val.lower()

        # Check Bitcoin address (legacy or bech32)
        if re.match(r"^(1|3|bc1)[a-zA-HJ-NP-Z0-9]{25,62}$", val):
            return val

        # Generic alphanumeric payment identifier (alphanumeric with hyphen/underscore, 4 to 64 chars)
        cleaned = re.sub(r"[\s]", "", val)
        if 4 <= len(cleaned) <= 64 and re.match(r"^[a-zA-Z0-9_\-@\.]+$", cleaned):
            return cleaned.lower()

        return None

    @classmethod
    def validate_and_normalize_url(cls, url: str) -> Tuple[str, str]:
        """
        Validates URL for security and SSRF protection.
        Returns (normalized_full_url, normalized_domain).
        Raises SSRFValidationError if the URL targets private/forbidden hosts.
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL cannot be empty")

        url = url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Only HTTP and HTTPS protocols are permitted")

        hostname = (parsed.hostname or "").lower().strip()
        if not hostname:
            raise ValueError("Invalid URL: missing host")

        # Check prohibited hostnames
        if hostname in cls.PROHIBITED_HOSTNAMES or hostname.endswith(".internal") or hostname.endswith(".local"):
            raise SSRFValidationError(f"Access to prohibited host '{hostname}' is blocked for security")

        # Check if hostname is an IP address
        ip = None
        try:
            ip = ipaddress.ip_address(hostname)
        except ValueError:
            # Not an IP string, it's a domain name
            pass

        if ip is not None:
            for net in cls.PROHIBITED_IP_NETWORKS:
                if ip in net:
                    raise SSRFValidationError(f"Target IP address '{ip}' is in a private/restricted network range")

        norm_domain = cls.normalize_domain(hostname) or hostname
        return (parsed.geturl(), norm_domain)


normalizer = IndicatorNormalizer()
