"""
ScamGraph AI - Safety and Response Assistant Service
Generates incident response playbooks and tailored mitigation guidance based on victim state:
- NOT_PAID
- PAID
- SHARED_OTP_CREDENTIALS
- SHARED_ID_DOCUMENTS
- CLICKED_MALICIOUS_LINK
Provides verified Indian cybercrime reporting portals, emergency hotlines, and explicit disclaimers.
"""

from typing import List, Dict, Any, Optional


class SafetyService:
    """
    Expert incident response engine for cyber fraud and employment scam victims.
    """

    OFFICIAL_PORTALS = [
        {
            "name": "National Cyber Crime Reporting Portal (NCRP)",
            "url": "https://cybercrime.gov.in",
            "helpline": "1930",
            "jurisdiction": "India (All States & UTs)",
            "description": "Official Ministry of Home Affairs (MHA) portal for reporting cyber fraud, financial fraud, and online scams. Operates the Citizen Financial Cyber Fraud Reporting and Management System (CFCFRMS).",
            "type": "GOVERNMENT",
        },
        {
            "name": "Chakshu - Sanchar Saathi (DoT)",
            "url": "https://sancharsaathi.gov.in/sfc/",
            "helpline": "Toll-Free 1800-110-420",
            "jurisdiction": "India (Telecom & Mobile)",
            "description": "Citizen-centric portal by Department of Telecommunications for reporting suspected fraud communications received via SMS, voice calls, or WhatsApp (fake job offers, lottery, KYC expiry).",
            "type": "TELECOM_REGULATOR",
        },
        {
            "name": "RBI Complaint Management System (CMS)",
            "url": "https://cms.rbi.org.in",
            "helpline": "14440",
            "jurisdiction": "India (Banks & NBFCs)",
            "description": "Reserve Bank of India Ombudsman portal to lodge formal grievances against banks or payment service providers for unauthorized transactions or lack of timely response.",
            "type": "CENTRAL_BANK",
        },
        {
            "name": "UIDAI Biometric Lock / Aadhaar Security",
            "url": "https://myaadhaar.uidai.gov.in",
            "helpline": "1947",
            "jurisdiction": "India",
            "description": "Instantly lock your Aadhaar biometrics to prevent unauthorized authentication or fraudulent SIM card issuance in your name.",
            "type": "IDENTITY_PROTECTION",
        },
        {
            "name": "National Consumer Helpline (NCH)",
            "url": "https://consumerhelpline.gov.in",
            "helpline": "1915",
            "jurisdiction": "India",
            "description": "Grievance redressal for fraudulent training institutes, fake recruitment agencies, and non-refund of application fees.",
            "type": "CONSUMER_AFFAIRS",
        },
    ]

    DISCLAIMER = (
        "IMPORTANT LEGAL DISCLAIMER: ScamGraph AI provides defensive guidance and intelligence recommendations for educational and safety purposes. "
        "ScamGraph AI cannot guarantee the recovery of stolen funds, account restoration, or specific law enforcement actions. "
        "If you have suffered a financial loss, immediately contact your financial institution and report the crime to your local cyber police station or via national hotline 1930."
    )

    def generate_recommendations(
        self,
        has_paid: bool = False,
        shared_otp: bool = False,
        shared_id: bool = False,
        clicked_link: bool = False,
        amount_lost: Optional[float] = None,
        payment_reference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Builds a prioritized, step-by-step mitigation checklist tailored to the exact compromise scenario.
        """
        actions = []

        # Scenario 1: Financial Transaction Occurred (PAID)
        if has_paid:
            actions.append({
                "priority": "CRITICAL_URGENT",
                "title": "Call 1930 Helpline Immediately (Golden Hour Window)",
                "description": (
                    "Call the National Cyber Financial Fraud Helpline at 1930 within the first 2-4 hours ('golden hour'). "
                    "Provide the transaction UTR number, bank account details, and suspect UPI ID. "
                    "Law enforcement and nodal banks can freeze the fraudulent money in the recipient account before it is withdrawn at an ATM."
                ),
                "portal_name": "NCRP / CFCFRMS",
                "portal_url": "https://cybercrime.gov.in",
                "helpline": "1930",
            })
            actions.append({
                "priority": "CRITICAL_URGENT",
                "title": "Contact Your Bank Fraud Desk",
                "description": (
                    "Immediately call your debit/credit card or bank customer care to report an unauthorized/fraudulent transaction. "
                    "Request a transaction dispute / chargeback ticket and ask to freeze your debit card or UPI handle if compromised."
                ),
                "portal_name": "RBI Complaint Management System",
                "portal_url": "https://cms.rbi.org.in",
                "helpline": "14440",
            })
            actions.append({
                "priority": "HIGH",
                "title": "Preserve All Transaction & Chat Evidence",
                "description": (
                    "Take screenshots of payment confirmation (showing UPI reference/UTR number, date, time), WhatsApp/Telegram chat history, "
                    "and the fraudulent job offer letter. Do not delete chats or leave groups until exported."
                ),
                "portal_name": None,
                "portal_url": None,
                "helpline": None,
            })

        # Scenario 2: Credentials or OTP Shared
        if shared_otp:
            actions.append({
                "priority": "CRITICAL_URGENT",
                "title": "Immediately Change Banking & Primary Email Passwords",
                "description": (
                    "Change the passwords for your email, netbanking, and payment apps from a different, secure device. "
                    "Terminate all active login sessions in your Google/Microsoft/Apple account settings."
                ),
                "portal_name": "Account Security Central",
                "portal_url": "https://myaccount.google.com/security",
                "helpline": None,
            })
            actions.append({
                "priority": "HIGH",
                "title": "Enable Hardware or Authenticator App 2FA",
                "description": (
                    "Replace SMS-based OTP verification with an authenticator app (Google Authenticator, Microsoft Authenticator) "
                    "or FIDO2 security keys to defend against SIM-swap attacks."
                ),
                "portal_name": None,
                "portal_url": None,
                "helpline": None,
            })

        # Scenario 3: Identity Documents (Aadhaar, PAN) Shared
        if shared_id:
            actions.append({
                "priority": "HIGH",
                "title": "Lock Your Aadhaar Biometrics on myAadhaar Portal",
                "description": (
                    "Log into the UIDAI myAadhaar portal (myaadhaar.uidai.gov.in) or mAadhaar app and enable 'Biometric Lock'. "
                    "This blocks anyone from misusing your fingerprint or iris data for fraudulent bank accounts or SIM cards."
                ),
                "portal_name": "UIDAI myAadhaar Portal",
                "portal_url": "https://myaadhaar.uidai.gov.in",
                "helpline": "1947",
            })
            actions.append({
                "priority": "MEDIUM",
                "title": "Check Active Mobile Connections via TAFCOP",
                "description": (
                    "Visit the DoT Sanchar Saathi TAFCOP portal (sancharsaathi.gov.in) to verify all mobile numbers currently registered against your Aadhaar ID. "
                    "Report and disconnect any unknown mobile numbers immediately."
                ),
                "portal_name": "Sanchar Saathi TAFCOP",
                "portal_url": "https://sancharsaathi.gov.in",
                "helpline": None,
            })

        # Scenario 4: Malicious Link Clicked or File Downloaded
        if clicked_link:
            actions.append({
                "priority": "HIGH",
                "title": "Disconnect Device from Wi-Fi & Scan for APK/Malware",
                "description": (
                    "Immediately check your device 'Downloads' folder for any newly downloaded .apk or .exe files. "
                    "Run a reputable endpoint security / anti-malware scan. Check accessibility permissions in Android settings to ensure no remote-access tools (AnyDesk, TeamViewer, RustDesk) were granted access."
                ),
                "portal_name": None,
                "portal_url": None,
                "helpline": None,
            })

        # Default preventive recommendations if no financial loss has occurred yet
        if not has_paid:
            actions.append({
                "priority": "HIGH",
                "title": "Do NOT Send Any Money or Training Deposit",
                "description": (
                    "Legitimate companies and authorized placement consultancies never ask candidates to pay for interviews, tests, uniforms, training kits, or laptops. "
                    "Cease all further communication with the sender."
                ),
                "portal_name": None,
                "portal_url": None,
                "helpline": None,
            })
            actions.append({
                "priority": "MEDIUM",
                "title": "Report Fraud Number & URL on Chakshu Portal",
                "description": (
                    "Help protect fellow job seekers by reporting the sender's mobile number, WhatsApp handle, and website link on the Government of India Chakshu portal."
                ),
                "portal_name": "Chakshu - Sanchar Saathi",
                "portal_url": "https://sancharsaathi.gov.in/sfc/",
                "helpline": "1800-110-420",
            })
            actions.append({
                "priority": "MEDIUM",
                "title": "Verify Directly with Company HR",
                "description": (
                    "Navigate independently to the company's verified website (e.g. careers.tcs.com, infosys.com/careers) "
                    "and email their official recruitment integrity desk to report fraudulent impersonation."
                ),
                "portal_name": None,
                "portal_url": None,
                "helpline": None,
            })

        return {
            "compromise_summary": {
                "has_paid": has_paid,
                "shared_otp": shared_otp,
                "shared_id": shared_id,
                "clicked_link": clicked_link,
                "amount_lost": amount_lost,
                "payment_reference": payment_reference,
            },
            "actions": actions,
            "official_portals": self.OFFICIAL_PORTALS,
            "disclaimer": self.DISCLAIMER,
        }


safety_service = SafetyService()
