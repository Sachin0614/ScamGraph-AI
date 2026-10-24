# ScamGraph AI — Real-Time Threat Investigation Platform

An upgraded, AI-powered cyber-threat investigation platform featuring real-time Gmail monitoring (INBOX + SPAM), automated desktop spam notifications with interactive action buttons, and a live forensic threat relationship network graph.

---

## 📌 Core Upgraded Features

### 1. Real-Time Dual-Folder Email Monitoring
- Continuously monitors the connected Gmail account (`shrishtiraghav66@gmail.com`).
- **Monitors both INBOX and SPAM folders:** Captures emails that Gmail pre-filters directly into Spam so threats are never missed.
- Baseline sync at startup ensures historical emails never trigger alerts.
- Persistent SQLite tracking prevents duplicate notifications across application restarts.
- Auto-reconnects on network disconnections every 15 seconds without crashing.

### 2. Desktop Spam Notifications with Action Buttons
Whenever a new spam email arrives (in either INBOX or SPAM folder):
- **Title:** `ScamGraph AI — Spam Detected`
- **Message:** `A suspicious email has been received.`
- **[View] Button:** Opens the application directly into the comprehensive forensic investigation view for that email.
- **[Network] Button:** Opens the interactive real-time Threat Relationship Graph centered on that email and its evidence indicators.
- **Safe Emails:** Simple notification: `📩 You received a new email!`

### 3. Forensic Investigation View ([View] Action)
- Displays genuine metadata: Sender display name, RFC email address, domain, timestamp, Gmail mailbox folder.
- Real-time spam score, confidence percentage, and specific matched forensic evidence triggers.
- Authentic extracted indicators: verified domains, hyperlinks, and phone numbers actually present in the email.
- **"Open in Gmail"** button to jump directly into the original message in webmail.
- Zero mock or fabricated sender details.

### 4. Live Threat Relationship Network Graph ([Network] Action)
- Built with **Cytoscape.js** on a dark cybersecurity dashboard palette (`#030712`, `#0F172A`).
- **Color Coding:**
  - 🔴 **Red Nodes (`#EF4444`):** Suspicious indicators supported by evidence (high-risk email, malicious URL/phone).
  - 🔷 **Cyan Nodes (`#00F0FF`):** Verified evidence, domains, and links.
  - 🟣 **Purple/Blue Nodes (`#8B5CF6`):** Related entities (e.g. sender email account).
- **Strict Evidence Rules:**
  - Zero mock data or placeholder nodes.
  - Links multiple emails only when real evidence establishes a relationship (same exact sender address, verified shared domain, or matching URL).
  - If an email has no verified cross-case relationships, displays only its authentic indicators and states: *"No verified relationships found"*.
  - Interactive Inspector Drawer: Click any node to reveal its type, threat status, evidence source, and relations.

---

## 🚀 How to Run ScamGraph AI

### Option A: 1-Click Batch Runner
Double-click:
```text
start.bat
```

### Option B: Command Line (PowerShell)
```powershell
cd "D:\RBMI\Mini Project\ScamGraph-Combined"
python run.py
```
The platform will launch and open in your browser at:  
👉 **`http://localhost:8501`**

---

## 🧪 Testing the Upgrade

Run the automated verification suite to test all components:

```powershell
cd "D:\RBMI\Mini Project\ScamGraph-Combined"
python tests/test_scamgraph_upgrade.py
```

Expected output:
```text
======================================================================
      SCAMGRAPH AI - UPGRADE VERIFICATION TEST SUITE
======================================================================
[1/5] Testing Forensic Indicator Extractor...
  [PASSED] Real forensic indicators extracted accurately.
[2/5] Testing Spam Protection Engine & Uncertainty Safety...
  [PASSED] Spam email classified: 99.9% (Threshold: 80%)
  [PASSED] Safe email classified: 97.2% Safe
[3/5] Testing SQLite Database Forensic Persistence...
  [PASSED] Saved and verified email record #1 in SQLite.
[4/5] Testing Threat Relationship Graph Engine...
  [PASSED] Constructed Threat Graph: 4 nodes, 3 edges.
  [PASSED] Zero mock data: graph contains only real extracted evidence.
[5/5] Testing Windows Desktop Toast Notifications (bottom-right)...
  [PASSED] Fired 'ScamGraph AI — Spam Detected' [View] [Network] toast.
  [PASSED] Fired 'You received a new email!' safe toast.
======================================================================
  ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!
======================================================================
```
