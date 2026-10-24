"""
ScamGraph AI - Spam Protection Classification Engine
====================================================
Uses TF-IDF + Naive Bayes ML classifier with evidence extraction.
Enforces uncertainty safety: borderline emails (< 80% confidence) are treated as SAFE.
"""

import os
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from scamgraph.config import config, get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODEL_FILE = os.path.join(BASE_DIR, "spam_model.pkl")
SPAM_CONFIDENCE_THRESHOLD = 0.80

# Spam and threat trigger patterns for explicit forensic evidence extraction
SPAM_EVIDENCE_PATTERNS = [
    (r"\blottery\b|\bmillion\s+dollars?\b|\bwon\s+\$\d+", "Lottery / High-Value Cash Award Lure"),
    (r"\bwire\s+transfer\b|\bbank\s+transfer\b|\bwestern\s+union\b", "Unsolicited Wire Transfer Request"),
    (r"\b(account|card|access)\s+(suspended|blocked|locked|disabled)\b", "Account Suspension / Coercive Alert"),
    (r"\bverify\s+your\s+(password|identity|account|credentials|otp)\b", "Credential Harvesting / Verification Lure"),
    (r"\b(urgent|immediate)\s+(action|notice|response)\b|\bwithin\s+24\s+hours\b", "Artificial Time Urgency"),
    (r"\b(crypto|bitcoin|ethereum|usdt|roi)\b", "High-Risk Cryptocurrency Investment Proposition"),
    (r"\b(pre-?approved|unsecured)\s+loan\b", "Unsolicited Pre-Approved Credit Offer"),
    (r"\bwork\s+from\s+home\s+\$\d+|\bearn\s+\$\d+\s+weekly\b", "Predatory Work-From-Home / Task Scam"),
    (r"\b(prince|inheritance|barrister|bequest)\b", "Advance-Fee Inheritance / Royal Beneficiary Lure"),
    (r"\bfree\s+(gift|iphone|voucher|walmart|amazon)\b", "Deceptive Gift / Free Hardware Bait"),
    (r"\b(overdue\s+invoice|unpaid\s+bill)\b", "Fake Invoice / Urgent Billing Claim"),
    (r"\b(verification|onboarding|registration|processing)\s+fee\b|\bfee\s+(of|is)\s+(₹|rs\.?|\$)\d+", "Advance-Fee / Fake Job Onboarding Fee Lure"),
    (r"\b(internship|job)\s+offer\b|\bselected\s+for\s+the\s+position\b", "Unsolicited Job / Internship Selection Lure"),
    (r"\bstipend\s*:\s*(₹|rs\.?|\$)\d+|\bsalary\s*:\s*(₹|rs\.?|\$)\d+", "High-Stipend Recruitment Bait"),
]

DEFAULT_TRAINING_DATA = [
    ("Congratulations! You have won $1,000,000 in the international mega lottery. Click here to claim your cash prize.", 1),
    ("Urgent: Your bank account has been suspended due to suspicious activity. Verify your password now to restore access.", 1),
    ("Earn $5,000 weekly working from home with no experience needed! Start immediately by clicking this link.", 1),
    ("Guaranteed 500% ROI in Bitcoin in just 24 hours. Invest in our crypto platform today.", 1),
    ("Final Notice: Unauthorized wire transfer detected on your debit card. Call 1-800-XXX-XXXX immediately.", 1),
    ("Cheap Viagra and Cialis online! No prescription required with discreet overnight shipping.", 1),
    ("You have been pre-approved for a personal loan of $50,000 with 0% interest. Apply within 24 hours.", 1),
    ("Dear Friend, I am Prince Abubakar with $25 Million USD seeking an urgent offshore account to transfer funds.", 1),
    ("Exclusive offer: Free iPhone 15 Pro Max giveaway for selected users. Confirm your shipping address now.", 1),
    ("Reset your Microsoft Office 365 password immediately. Your session will expire in 10 minutes.", 1),
    ("Hot single girls in your neighborhood want to chat with you tonight! Click here to meet them.", 1),
    ("Overdue Invoice Notification: Find attached invoice #84920. Pay immediately to avoid legal prosecution.", 1),
    ("Get rich quick with this one secret trading bot. Wall Street doesn't want you to know this!", 1),
    ("Virus Alert: Your Windows PC is infected with Trojan spyware. Call Microsoft Tech Support now.", 1),
    ("Congratulations! You won Walmart gift card worth $500. Click to claim your reward.", 1),
    ("Crypto giveaway: Elon Musk is doubling all Ethereum sent to this wallet address in the next hour.", 1),
    ("Urgent security notification: Someone tried to login to your PayPal account from Russia. Click here.", 1),
    ("Lose 20 pounds in 7 days without diet or exercise! Secret miracle weight loss pill exposed.", 1),
    ("Action Required: Your Netflix subscription has expired. Update credit card billing details here.", 1),
    ("You have 1 pending parcel from FedEx. Pay customs clearance fee of $2.99 to receive delivery.", 1),
    ("Refinance your mortgage at historic low rates! No credit check required. Apply online now.", 1),
    ("Attention! Your Apple ID has been locked for security reasons. Verify your identity now.", 1),
    ("Earn passive income every day while you sleep! Guaranteed returns guaranteed payout.", 1),
    ("Free Casino Chips: 100 free spins with 500% welcome deposit bonus at royal vegas casino.", 1),
    ("Important notice from tax department: You are entitled to a tax refund of $1,420. Submit info.", 1),
    ("Work from home data entry operator urgently required salary 40,000 per month.", 1),
    ("Urgent: update your KYC details immediately or your bank account will be permanently blocked.", 1),
    ("Win exciting gifts and brand new car in lucky draw contest enter now.", 1),
    ("Congratulations! You have been selected for the position of AI/ML Intern. A refundable onboarding and verification fee of Rs 1499 is required.", 1),
    ("Job Offer: Selected for Remote Python Developer. Pay registration fee to confirm offer letter and employee ID.", 1),
    ("HR Recruitment: Offer letter issued. Submit payment confirmation and onboarding fee immediately.", 1),

    ("RBMI Mini Project review and presentation scheduled for Monday morning in Lab 3.", 0),
    ("Assignment submission deadline extended by Professor Sharma until Friday 5 PM.", 0),
    ("Lecture notes and study materials for Python Data Structures and Algorithms unit 4.", 0),
    ("Weekly team sprint planning meeting tomorrow at 10:00 AM on Google Meet.", 0),
    ("Your Amazon order #402-9182312 has been dispatched and will arrive on Thursday.", 0),
    ("Here is the updated syllabus and exam schedule for the upcoming semester examinations.", 0),
    ("Can you please review the pull request on GitHub and leave your feedback on the code?", 0),
    ("IRCTC Booking Confirmation: PNR 2849201923 for your train journey from Bareilly to Delhi.", 0),
    ("Hey, are we still meeting in the college cafeteria after the second lecture?", 0),
    ("Your Google verification code is 492019. It will expire in 10 minutes. Do not share with anyone.", 0),
    ("Monthly electricity bill generated for consumer number 9182049. Amount due is Rs 1,450.", 0),
    ("Uber receipt: Thanks for riding with us. Your trip fare was Rs 240.", 0),
    ("GitHub: Dependabot alerts fixed in repository mail-popup-notifier.", 0),
    ("LinkedIn: Rahul and 2 other connections viewed your profile this week.", 0),
    ("Medium Daily Digest: Top 5 architectural patterns in modern distributed systems.", 0),
    ("Meeting notes from today's faculty meeting regarding academic calendar and holidays.", 0),
    ("Please find attached the project documentation and architecture diagram for our review.", 0),
    ("Happy Birthday! Wishing you a wonderful year ahead filled with happiness and success.", 0),
    ("Your SBI Account has been credited with Rs 5,000 via UPI from Mohit on 24-Oct-2026.", 0),
    ("College notice: Campus placement drive by TCS and Infosys starting from next month.", 0),
    ("Here are the photos from our weekend trip to Nainital. Download the shared album link.", 0),
    ("Reminder: Annual college sports meet registration closes this Wednesday.", 0),
    ("Doctor appointment confirmation with Dr. Verma for tomorrow 4:30 PM at Apollo Clinic.", 0),
    ("Swiggy order delivered! Enjoy your meal. Rate the delivery partner in the app.", 0),
    ("Library reminder: Please return or renew the borrowed books before the due date.", 0),
    ("Invitation: National level coding hackathon organized by Computer Science Department.", 0),
    ("Discussion on database schema normalization and ER diagrams for project report.", 0),
    ("Resume and cover letter draft for software engineering internship application.", 0),
    ("Class cancellation notice: Chemistry lecture today at 2 PM is postponed to Thursday.", 0),
]


class SpamClassifier:
    def __init__(self, model_path=MODEL_FILE):
        self.model_path = model_path
        self.model = None
        self._load_or_train()

    def _train(self):
        texts, labels = zip(*DEFAULT_TRAINING_DATA)
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True, sublinear_tf=True)),
            ("nb", MultinomialNB(alpha=0.1))
        ])
        pipeline.fit(texts, labels)
        self.model = pipeline
        try:
            with open(self.model_path, "wb") as f:
                pickle.dump(self.model, f)
        except Exception:
            pass

    def _load_or_train(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
                    return
            except Exception:
                pass
        self._train()

    def classify(self, subject: str = "", body: str = "", sender: str = "") -> dict:
        full_text = f"{subject} {subject} {body}".strip()
        if not full_text:
            return {
                "is_spam": False,
                "label": "SAFE",
                "spam_score": 5.0,
                "confidence": 95.0,
                "evidence": ["Standard communication pattern. No suspicious indicators."],
                "is_uncertain": False
            }

        try:
            probs = self.model.predict_proba([full_text])[0]
            spam_prob = float(probs[1])
        except Exception:
            spam_prob = 0.5

        # Extract specific matched forensic evidence
        text_lower = full_text.lower()
        matched_evidence = []
        for pattern, label in SPAM_EVIDENCE_PATTERNS:
            if re.search(pattern, text_lower):
                matched_evidence.append(label)

        # Boost spam probability if explicit triggers present
        if matched_evidence:
            spam_prob = min(0.999, spam_prob + 0.35)

        spam_percentage = round(spam_prob * 100, 1)

        # Uncertainty handling: If < 80%, protected as SAFE
        if spam_percentage >= 80.0:
            is_spam = True
            label = "SPAM"
            confidence = spam_percentage
            if not matched_evidence:
                matched_evidence.append("Statistical text analysis indicates high similarity to verified fraudulent/spam campaigns.")
        else:
            is_spam = False
            label = "SAFE"
            confidence = round(100.0 - spam_percentage, 1)
            if spam_percentage >= 50.0:
                matched_evidence = [f"Borderline indicator score ({spam_percentage}%) below 80% threshold. Protected as Safe."]
            else:
                matched_evidence = ["Standard legitimate communication patterns confirmed. No malicious triggers."]

        return {
            "is_spam": is_spam,
            "label": label,
            "spam_score": spam_percentage,
            "confidence": confidence,
            "evidence": matched_evidence,
            "is_uncertain": (50.0 <= spam_percentage < 80.0)
        }


# Singleton instance
spam_classifier = SpamClassifier()
