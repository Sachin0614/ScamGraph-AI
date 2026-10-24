"""
ScamGraph AI - Scam Analysis Engine
Deep behavioral and linguistic rule-based threat vector detection engine.
Analyzes suspicious job offers, internships, and recruiter messages across 8 key scam threat vectors.
Produces explainable indicators, exact quotes, missing information matrices, and confidence explanations.
"""

import re
from typing import Dict, List, Any, Optional
from app.models.investigation import SeverityLevel


class ScamAnalysisEngine:
    """
    Multilayer scam detection engine that scans offer text, URLs, contacts, and metadata
    for fraudulent patterns.
    """

    # 1. UPFRONT_FEES: Demanding payment for registration, training, uniform, laptop, ID card, or security deposit
    UPFRONT_FEE_PATTERNS = [
        (r"(?:registration|processing|onboarding|application|kit|uniform|training|material|exam|laptop|id[\s\-]?card|security)\s+(?:fee|charge|deposit|amount|cost|payment|sum)", "Demands upfront registration, training, or deposit fee"),
        (r"(?:pay|transfer|deposit|send)\s+(?:rs\.?|inr|\$|usd|₹)?\s*\d{2,6}\s*(?:refundable|security|registration|deposit)", "Requests monetary payment with promise of refund"),
        (r"(?:refundable\s+(?:security\s+)?deposit|refundable\s+amount)", "Promise of refundable security deposit (classic recruitment fraud tactic)"),
        (r"(?:pay\s+before|advance\s+payment|mandatory\s+charge)", "Advance mandatory payment required before joining/interview"),
    ]

    # 2. URGENT_PAYMENT: Pressure to pay quickly
    URGENT_DEMAND_PATTERNS = [
        (r"(?:within\s+\d{1,2}\s+(?:hour|hr|minute|min)s?|within\s+24\s+hours|today\s+only|last\s+day\s+to\s+pay)", "Strict deadline requiring fast payment or action"),
        (r"(?:slots?\s+(?:are\s+)?filling\s+fast|only\s+\d+\s+seats?\s+left|limited\s+seats?\s+remaining)", "Artificial scarcity / FOMO tactic to rush victim"),
        (r"(?:immediate\s+(?:payment|transfer|response|action)|act\s+fast|urgent\s+hiring\s+today)", "Urgent pressure demanding immediate action"),
    ]

    # 3. THREATS_PRESSURE: Legal threats, blacklisting, forfeiting placement
    THREAT_PATTERNS = [
        (r"(?:legal\s+action|lawyer|court|police|fir|penalty|punishable|under\s+section|breach\s+of\s+contract)", "Threat of legal action or legal intimidation"),
        (r"(?:blacklist(?:ed)?|ban(?:ned)?|forfeit(?:ed)?|cancel\s+candidacy|permanent\s+ban)", "Threat to blacklist or permanently ban applicant from future recruitment"),
        (r"(?:fine\s+of|recovery\s+amount|damage\s+charges)", "Threat of financial fines or arbitrary damage recovery charges"),
    ]

    # 4. SENSITIVE_INFO_REQUESTS: OTP, password, banking, Aadhaar with OTP
    SENSITIVE_INFO_PATTERNS = [
        (r"(?:otp|one[\s\-]?time[\s\-]?password|verification\s+code)", "Explicit request for OTP / SMS verification code"),
        (r"(?:netbanking|internet\s+banking|password|atm\s+pin|upi\s+pin|cvv|card\s+expiry)", "Direct request for passwords, PINs, or banking credentials"),
        (r"(?:aadhaar\s+(?:otp|linked\s+number)|pan\s+card\s+photo|blank\s+cheque|passbook\s+copy)", "Request for sensitive personal identity documents or financial instruments"),
    ]

    # 5. MISLEADING_DOMAINS_URLS: Free hosting subdomains, typosquatting, URL shorteners
    FREE_HOSTING_DOMAINS = [
        "vercel.app", "pages.dev", "web.app", "firebaseapp.com", "blogspot.com",
        "wixsite.com", "weebly.com", "wordpress.com", "tinyurl.com", "bit.ly",
        "cutt.ly", "is.gd", "t.co", "glitch.me", "surge.sh", "000webhostapp.com"
    ]

    SUSPICIOUS_TLDS = [".xyz", ".top", ".work", ".click", ".link", ".buzz", ".live", ".guru", ".tk", ".ml", ".ga", ".cf"]

    # 6. UNREALISTIC_CLAIMS: Guaranteed selection without interview, exorbitant payouts for zero skill
    UNREALISTIC_CLAIMS_PATTERNS = [
        (r"(?:100%\s+selection|guaranteed\s+selection|no\s+interview\s+required|direct\s+selection|direct\s+joining\s+letter)", "Guaranteed job selection without standard technical or formal interview"),
        (r"(?:earn\s+(?:rs\.?|inr|₹|\$)?\s*\d{3,6}\s*(?:daily|per\s+day|per\s+hour|per\s+task))", "Unrealistically high daily/hourly payout promise"),
        (r"(?:data\s+entry|like\s+and\s+subscribe|youtube\s+task|copy\s+paste|ad\s+posting|typing\s+job)\s+earn", "Classic task-based / YouTube like / data entry scam scheme"),
        (r"(?:part[\s\-]?time\s+earn\s+(?:3000|5000|10000|50000)\s+from\s+home)", "Exorbitant part-time work from home income claim"),
    ]

    # 7. UNUSUAL_CHANNELS: Telegram bot, WhatsApp only, personal Gmail/Outlook
    UNUSUAL_CHANNEL_PATTERNS = [
        (r"(?:contact\s+(?:on|via)\s+telegram|telegram\s+username|@[\w_]+bot|t\.me/[\w_]+)", "Directs applicant to anonymous Telegram channels or bots"),
        (r"(?:whatsapp\s+(?:only|me|at|number)|wa\.me/\d+)", "Directs applicant exclusively to WhatsApp instead of official HR portals"),
        (r"(?:signal\s+(?:app|group)|viber)", "Directs applicant to encrypted third-party chat without audit trail"),
    ]

    FREE_MAIL_PROVIDERS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com", "mail.com", "rediffmail.com"}

    def analyze(
        self,
        text: Optional[str] = None,
        website_url: Optional[str] = None,
        recruiter_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        payment_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Runs deep analysis on submitted data.
        Returns a structured dictionary with verdict, indicators, exact quotes,
        inconsistencies, recommended actions, and confidence explanations.
        """
        combined_text = " ".join([t for t in [text, notes] if t])
        lower_text = combined_text.lower()

        detected_indicators = []
        exact_snippets = {}
        missing_inconsistencies = []
        verification_steps = []
        score_points = 0.0

        # 1. Evaluate Upfront Fees
        for pattern, explanation in self.UPFRONT_FEE_PATTERNS:
            match = re.search(pattern, lower_text)
            if match:
                snippet = combined_text[max(0, match.start() - 25):min(len(combined_text), match.end() + 25)]
                detected_indicators.append({
                    "category": "UPFRONT_PAYMENT_DEMAND",
                    "title": "Advance Fee / Deposit Requirement",
                    "severity": SeverityLevel.CRITICAL.value,
                    "explanation": explanation,
                    "weight": 35.0,
                    "snippet": snippet.strip(),
                })
                exact_snippets["UPFRONT_PAYMENT_DEMAND"] = snippet.strip()
                score_points += 35.0
                break

        # 2. Evaluate Urgent Payment / Pressure
        for pattern, explanation in self.URGENT_DEMAND_PATTERNS:
            match = re.search(pattern, lower_text)
            if match:
                snippet = combined_text[max(0, match.start() - 25):min(len(combined_text), match.end() + 25)]
                detected_indicators.append({
                    "category": "URGENT_DEMAND",
                    "title": "Artificial Urgency & Time Pressure",
                    "severity": SeverityLevel.HIGH.value,
                    "explanation": explanation,
                    "weight": 18.0,
                    "snippet": snippet.strip(),
                })
                exact_snippets["URGENT_DEMAND"] = snippet.strip()
                score_points += 18.0
                break

        # 3. Evaluate Threats / Legal Coercion
        for pattern, explanation in self.THREAT_PATTERNS:
            match = re.search(pattern, lower_text)
            if match:
                snippet = combined_text[max(0, match.start() - 25):min(len(combined_text), match.end() + 25)]
                detected_indicators.append({
                    "category": "COERCION_OR_THREAT",
                    "title": "Threat or Legal Coercion Language",
                    "severity": SeverityLevel.CRITICAL.value,
                    "explanation": explanation,
                    "weight": 30.0,
                    "snippet": snippet.strip(),
                })
                exact_snippets["COERCION_OR_THREAT"] = snippet.strip()
                score_points += 30.0
                break

        # 4. Evaluate Sensitive Info / OTP Requests
        for pattern, explanation in self.SENSITIVE_INFO_PATTERNS:
            match = re.search(pattern, lower_text)
            if match:
                snippet = combined_text[max(0, match.start() - 25):min(len(combined_text), match.end() + 25)]
                detected_indicators.append({
                    "category": "SENSITIVE_CREDENTIALS_REQUEST",
                    "title": "Request for OTP, Passwords, or Banking Data",
                    "severity": SeverityLevel.CRITICAL.value,
                    "explanation": explanation,
                    "weight": 40.0,
                    "snippet": snippet.strip(),
                })
                exact_snippets["SENSITIVE_CREDENTIALS_REQUEST"] = snippet.strip()
                score_points += 40.0
                break

        # 5. Evaluate Unrealistic Claims / Guaranteed Selection
        for pattern, explanation in self.UNREALISTIC_CLAIMS_PATTERNS:
            match = re.search(pattern, lower_text)
            if match:
                snippet = combined_text[max(0, match.start() - 25):min(len(combined_text), match.end() + 25)]
                detected_indicators.append({
                    "category": "UNREALISTIC_CLAIMS",
                    "title": "Guaranteed Selection or Unrealistic Payout",
                    "severity": SeverityLevel.HIGH.value,
                    "explanation": explanation,
                    "weight": 22.0,
                    "snippet": snippet.strip(),
                })
                exact_snippets["UNREALISTIC_CLAIMS"] = snippet.strip()
                score_points += 22.0
                break

        # 6. Evaluate Unusual Channels (Telegram, WhatsApp)
        for pattern, explanation in self.UNUSUAL_CHANNEL_PATTERNS:
            match = re.search(pattern, lower_text)
            if match:
                snippet = combined_text[max(0, match.start() - 25):min(len(combined_text), match.end() + 25)]
                detected_indicators.append({
                    "category": "UNUSUAL_COMMUNICATION_CHANNEL",
                    "title": "Off-Platform / Encrypted Chat Redirection",
                    "severity": SeverityLevel.MEDIUM.value,
                    "explanation": explanation,
                    "weight": 15.0,
                    "snippet": snippet.strip(),
                })
                exact_snippets["UNUSUAL_COMMUNICATION_CHANNEL"] = snippet.strip()
                score_points += 15.0
                break

        # 7. Check Inconsistencies between Recruiter / Corporate Domain and Email
        if email:
            domain_part = email.split("@")[-1].lower() if "@" in email else ""
            if domain_part in self.FREE_MAIL_PROVIDERS:
                if recruiter_name or "company" in lower_text or "tcs" in lower_text or "infosys" in lower_text or "wipro" in lower_text or "google" in lower_text:
                    missing_inconsistencies.append(
                        f"Corporate entity representation claimed, but contact email uses free personal mail service (@{domain_part}) instead of verified enterprise domain."
                    )
                    detected_indicators.append({
                        "category": "INCONSISTENT_RECRUITER_DOMAIN",
                        "title": "Free Public Webmail Used For Enterprise Recruitment",
                        "severity": SeverityLevel.HIGH.value,
                        "explanation": f"Claiming to represent an established brand while recruiting through generic @{domain_part}.",
                        "weight": 20.0,
                        "snippet": f"Email: {email}",
                    })
                    score_points += 20.0

        # 8. Check Website / Domain Indicators
        if website_url:
            norm_url = website_url.lower()
            for fh in self.FREE_HOSTING_DOMAINS:
                if fh in norm_url:
                    detected_indicators.append({
                        "category": "SUSPICIOUS_HOSTING_SERVICE",
                        "title": f"Recruitment Portal Hosted on Free/Temporary Subdomain ({fh})",
                        "severity": SeverityLevel.HIGH.value,
                        "explanation": f"Legitimate corporate recruitment platforms host on dedicated top-level domains, not on free public hosting ({fh}).",
                        "weight": 25.0,
                        "snippet": f"URL: {website_url}",
                    })
                    missing_inconsistencies.append(f"Portal is hosted on free hosting service '{fh}' instead of official company infrastructure.")
                    score_points += 25.0
                    break

            for tld in self.SUSPICIOUS_TLDS:
                if norm_url.endswith(tld) or f"{tld}/" in norm_url:
                    detected_indicators.append({
                        "category": "HIGH_RISK_TLD",
                        "title": f"Domain Uses High-Risk Disposable TLD ({tld})",
                        "severity": SeverityLevel.MEDIUM.value,
                        "explanation": f"The top-level domain {tld} is frequently favored in transient phishing and spam campaigns.",
                        "weight": 14.0,
                        "snippet": f"URL: {website_url}",
                    })
                    score_points += 14.0
                    break

        # 9. Payment ID present in a recruitment offer is an immediate high red flag
        if payment_id:
            detected_indicators.append({
                "category": "SOLICITED_PAYMENT_IDENTIFIER",
                "title": f"Personal UPI / Payment Destination Provided: {payment_id}",
                "severity": SeverityLevel.CRITICAL.value,
                "explanation": "Legitimate enterprise employers never solicit personal UPI or bank transfers during hiring.",
                "weight": 35.0,
                "snippet": f"Payment ID: {payment_id}",
            })
            missing_inconsistencies.append(f"Payment destination provided directly in hiring communication: {payment_id}")
            score_points += 35.0

        # General missing information checks
        if not website_url and not email:
            missing_inconsistencies.append("No verifiable corporate website or official email address provided in offer.")
        if "interview" not in lower_text and "test" not in lower_text and "assessment" not in lower_text:
            missing_inconsistencies.append("No formal assessment, interview rounds, or technical evaluation mentioned before selection.")

        # Cap score between 0.0 and 100.0
        normalized_score = min(100.0, round(score_points, 1))

        # Determine Verdict
        if normalized_score >= 65.0 or any(i["severity"] == SeverityLevel.CRITICAL.value for i in detected_indicators):
            risk_verdict = "CONFIRMED_SCAM_PATTERNS"
            confidence_level = "HIGH"
        elif normalized_score >= 35.0:
            risk_verdict = "SUSPICIOUS_ACTIVITY"
            confidence_level = "MEDIUM"
        elif len(detected_indicators) > 0:
            risk_verdict = "UNVERIFIED_INDICATORS"
            confidence_level = "LOW"
        else:
            risk_verdict = "INSUFFICIENT_RED_FLAGS"
            confidence_level = "LOW"

        # Verification steps
        if website_url:
            verification_steps.append("Check the domain registration date using WHOIS; newly registered domains (< 6 months) posing as established companies are high risk.")
        if recruiter_name:
            verification_steps.append(f"Search LinkedIn for '{recruiter_name}' to check if they actually hold an active HR position at the named organization.")
        verification_steps.append("Cross-check the job ID on the official company careers portal directly (without clicking links in the message).")
        verification_steps.append("Never send registration money, training fees, or OTP verification codes to any recruiter under any circumstance.")

        # Summary generation
        summary = (
            f"Analysis identified {len(detected_indicators)} suspicious indicator(s) with an overall risk score of {normalized_score}/100. "
            + ("High-risk signals detected including upfront financial requests or impersonation patterns. " if normalized_score >= 50 else "Limited overt red flags detected, but ongoing vigilance is recommended. ")
            + f"Verdict: {risk_verdict}."
        )

        confidence_explanation = (
            f"The risk assessment score ({normalized_score}/100) is derived from documented rule-based behavioral patterns. "
            f"Signals with direct financial demands or credential harvesting carry higher weight ({sum(1 for i in detected_indicators if i['severity'] == SeverityLevel.CRITICAL.value)} critical indicators identified). "
            f"This evaluation measures indicator presence, not judicial culpability."
        )

        limitations = (
            "Heuristic rules cannot guarantee 100% classification of novel social engineering attacks. "
            "Corroborating public records or official recruiter confirmation remains recommended before taking irreversible actions."
        )

        return {
            "risk_verdict": risk_verdict,
            "overall_risk_score": normalized_score,
            "confidence_level": confidence_level,
            "detected_indicators": detected_indicators,
            "exact_snippets": exact_snippets,
            "missing_inconsistencies": missing_inconsistencies,
            "recommended_verification_steps": verification_steps,
            "summary": summary,
            "confidence_explanation": confidence_explanation,
            "limitations_and_uncertainty": limitations,
            "ai_engine_used": "rule-engine-v2",
        }


scam_engine = ScamAnalysisEngine()
