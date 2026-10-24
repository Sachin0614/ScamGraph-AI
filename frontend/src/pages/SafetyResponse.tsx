import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  PhoneCall,
  ExternalLink,
  AlertOctagon,
  CheckCircle2,
  Lock,
  CreditCard,
  Key,
  FileText,
  AlertTriangle,
} from "lucide-react";
import { apiClient } from "../api/client";
import { SafetyResponseData, OfficialPortal } from "../types";

export const SafetyResponse: React.FC = () => {
  const [hasPaid, setHasPaid] = useState<boolean>(false);
  const [sharedOtp, setSharedOtp] = useState<boolean>(false);
  const [sharedId, setSharedId] = useState<boolean>(false);
  const [clickedLink, setClickedLink] = useState<boolean>(false);
  const [amountLost, setAmountLost] = useState<string>("");
  const [paymentRef, setPaymentRef] = useState<string>("");

  const [assessment, setAssessment] = useState<SafetyResponseData | null>(null);
  const [portals, setPortals] = useState<OfficialPortal[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch verified portals on load
  useEffect(() => {
    apiClient.getOfficialPortals().then((res: { portals: OfficialPortal[] }) => {
      setPortals(res.portals);
    });
    // Initial evaluation
    evaluatePlan(false, false, false, false);
  }, []);

  const evaluatePlan = (
    paid: boolean,
    otp: boolean,
    id: boolean,
    link: boolean,
    amt?: string,
    ref?: string
  ) => {
    setLoading(true);
    apiClient
      .assessSafety({
        has_paid: paid,
        shared_otp: otp,
        shared_id: id,
        clicked_link: link,
        amount_lost: amt ? parseFloat(amt) : undefined,
        payment_reference: ref || undefined,
      })
      .then((data) => {
        setAssessment(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleCheckboxChange = (field: "paid" | "otp" | "id" | "link", val: boolean) => {
    let p = hasPaid,
      o = sharedOtp,
      i = sharedId,
      l = clickedLink;
    if (field === "paid") {
      setHasPaid(val);
      p = val;
    } else if (field === "otp") {
      setSharedOtp(val);
      o = val;
    } else if (field === "id") {
      setSharedId(val);
      i = val;
    } else if (field === "link") {
      setClickedLink(val);
      l = val;
    }
    evaluatePlan(p, o, i, l, amountLost, paymentRef);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-slate-100 font-mono tracking-tight flex items-center space-x-2">
          <ShieldCheck className="w-6 h-6 text-emerald-400" />
          <span>INCIDENT SAFETY & RESPONSE ASSISTANT</span>
        </h1>
        <p className="text-xs text-slate-400 font-mono mt-1">
          Tailored emergency mitigation steps and verified Indian cybercrime reporting authorities.
        </p>
      </div>

      {/* Emergency Hotline Banner for Indian Users */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-rose-950/80 via-slate-900 to-amber-950/50 border border-rose-500/40 space-y-3">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-400 flex items-center justify-center text-rose-400 shrink-0">
              <PhoneCall className="w-5 h-5 animate-bounce" />
            </div>
            <div>
              <div className="text-xs font-mono font-bold text-rose-300 uppercase tracking-wider">
                NATIONAL CYBER FINANCIAL FRAUD HELPLINE
              </div>
              <div className="text-2xl font-black font-mono text-slate-100">
                DIAL: <span className="text-rose-400 underline">1930</span>
              </div>
            </div>
          </div>

          <div className="text-xs font-mono text-slate-300 max-w-md bg-slate-950/60 p-3 rounded-lg border border-slate-800">
            <span className="text-amber-400 font-bold block mb-0.5">GOLDEN HOUR NOTICE:</span>
            Reporting fraudulent transfers within 2 to 4 hours enables the Citizen Financial Cyber Fraud Reporting System to freeze funds before ATM withdrawal.
          </div>
        </div>
      </div>

      {/* Interactive Situation Questionnaire */}
      <div className="p-5 rounded-xl glass-panel space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-mono font-bold text-cyan-300 uppercase tracking-wider">
            Step 1: Check All Scenarios That Apply to Your Situation
          </h3>
          <span className="text-[11px] font-mono text-slate-400">Real-time dynamic playbook</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {/* Question 1: Paid money */}
          <label
            className={`p-3.5 rounded-lg border flex items-start space-x-3 cursor-pointer transition ${
              hasPaid
                ? "bg-rose-950/40 border-rose-500/50 text-rose-200"
                : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700"
            }`}
          >
            <input
              type="checkbox"
              checked={hasPaid}
              onChange={(e) => handleCheckboxChange("paid", e.target.checked)}
              className="mt-0.5 rounded border-slate-700 bg-slate-900 text-rose-500 focus:ring-0"
            />
            <div className="space-y-1">
              <span className="text-xs font-bold font-mono block">
                I transferred money or paid a registration fee
              </span>
              <span className="text-[11px] text-slate-400 block font-mono">
                Sent funds via UPI, NetBanking, debit card, or crypto wallet.
              </span>
            </div>
          </label>

          {/* Question 2: Shared OTP */}
          <label
            className={`p-3.5 rounded-lg border flex items-start space-x-3 cursor-pointer transition ${
              sharedOtp
                ? "bg-rose-950/40 border-rose-500/50 text-rose-200"
                : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700"
            }`}
          >
            <input
              type="checkbox"
              checked={sharedOtp}
              onChange={(e) => handleCheckboxChange("otp", e.target.checked)}
              className="mt-0.5 rounded border-slate-700 bg-slate-900 text-rose-500 focus:ring-0"
            />
            <div className="space-y-1">
              <span className="text-xs font-bold font-mono block">
                I shared an OTP, password, or PIN
              </span>
              <span className="text-[11px] text-slate-400 block font-mono">
                Gave an SMS code, banking password, or remote access to my device.
              </span>
            </div>
          </label>

          {/* Question 3: Shared ID */}
          <label
            className={`p-3.5 rounded-lg border flex items-start space-x-3 cursor-pointer transition ${
              sharedId
                ? "bg-amber-950/40 border-amber-500/50 text-amber-200"
                : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700"
            }`}
          >
            <input
              type="checkbox"
              checked={sharedId}
              onChange={(e) => handleCheckboxChange("id", e.target.checked)}
              className="mt-0.5 rounded border-slate-700 bg-slate-900 text-amber-500 focus:ring-0"
            />
            <div className="space-y-1">
              <span className="text-xs font-bold font-mono block">
                I submitted identity documents (Aadhaar, PAN, Passport)
              </span>
              <span className="text-[11px] text-slate-400 block font-mono">
                Provided photos or scans of official government IDs.
              </span>
            </div>
          </label>

          {/* Question 4: Clicked Link */}
          <label
            className={`p-3.5 rounded-lg border flex items-start space-x-3 cursor-pointer transition ${
              clickedLink
                ? "bg-blue-950/40 border-blue-500/50 text-blue-200"
                : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700"
            }`}
          >
            <input
              type="checkbox"
              checked={clickedLink}
              onChange={(e) => handleCheckboxChange("link", e.target.checked)}
              className="mt-0.5 rounded border-slate-700 bg-slate-900 text-blue-500 focus:ring-0"
            />
            <div className="space-y-1">
              <span className="text-xs font-bold font-mono block">
                I clicked a suspicious link or downloaded a file/app
              </span>
              <span className="text-[11px] text-slate-400 block font-mono">
                Visited an unfamiliar URL or installed an APK or file on my phone/PC.
              </span>
            </div>
          </label>
        </div>

        {/* Optional payment details if paid */}
        {hasPaid && (
          <div className="p-4 rounded-lg bg-rose-950/20 border border-rose-500/30 grid grid-cols-1 sm:grid-cols-2 gap-3 animate-in fade-in">
            <div>
              <label className="text-[11px] font-mono text-rose-300 block mb-1">
                Amount Transferred (INR ₹):
              </label>
              <input
                type="number"
                placeholder="e.g. 4999"
                value={amountLost}
                onChange={(e) => {
                  setAmountLost(e.target.value);
                  evaluatePlan(hasPaid, sharedOtp, sharedId, clickedLink, e.target.value, paymentRef);
                }}
                className="w-full px-3 py-1.5 rounded bg-slate-900 border border-rose-500/40 text-xs font-mono text-slate-100"
              />
            </div>
            <div>
              <label className="text-[11px] font-mono text-rose-300 block mb-1">
                Transaction Reference / UTR Number:
              </label>
              <input
                type="text"
                placeholder="e.g. 402847291048"
                value={paymentRef}
                onChange={(e) => {
                  setPaymentRef(e.target.value);
                  evaluatePlan(hasPaid, sharedOtp, sharedId, clickedLink, amountLost, e.target.value);
                }}
                className="w-full px-3 py-1.5 rounded bg-slate-900 border border-rose-500/40 text-xs font-mono text-slate-100"
              />
            </div>
          </div>
        )}
      </div>

      {/* Prioritized Action Plan */}
      <div className="p-5 rounded-xl glass-panel space-y-4">
        <h3 className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Step 2: Prioritized Emergency Incident Response Actions</span>
        </h3>

        <div className="space-y-3">
          {assessment?.actions.map((act, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
                act.priority === "CRITICAL_URGENT"
                  ? "bg-rose-950/30 border-rose-500/40"
                  : act.priority === "HIGH"
                  ? "bg-amber-950/20 border-amber-500/40"
                  : "bg-slate-900/60 border-slate-800"
              }`}
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span
                    className={`text-[9px] px-2 py-0.5 rounded font-mono font-bold ${
                      act.priority === "CRITICAL_URGENT"
                        ? "bg-rose-500 text-slate-950"
                        : "bg-amber-500 text-slate-950"
                    }`}
                  >
                    {act.priority.replace(/_/g, " ")}
                  </span>
                  <span className="text-sm font-bold text-slate-100 font-mono">
                    {act.title}
                  </span>
                </div>
                <p className="text-xs text-slate-300 font-mono leading-relaxed">
                  {act.description}
                </p>
              </div>

              {act.portal_url && (
                <a
                  href={act.portal_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs font-mono flex items-center space-x-1.5 shrink-0 transition"
                >
                  <span>Open {act.portal_name || "Portal"}</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Official Indian Reporting Resources Directory */}
      <div className="p-5 rounded-xl glass-panel space-y-4">
        <h3 className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider">
          Official Government & Regulatory Reporting Portals (India)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {portals.map((portal, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="font-bold text-cyan-300">{portal.name}</span>
                  {portal.helpline && (
                    <span className="text-rose-400 font-bold bg-rose-950/60 px-2 py-0.5 rounded border border-rose-500/30">
                      Helpline: {portal.helpline}
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-400 font-mono mt-1 leading-relaxed">
                  {portal.description}
                </p>
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                <span className="text-[10px] text-slate-500 font-mono">
                  {portal.jurisdiction}
                </span>
                <a
                  href={portal.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cyan-400 hover:underline flex items-center space-x-1 text-xs font-mono"
                >
                  <span>Visit Portal</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Disclaimer */}
      <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-400 leading-relaxed">
        {assessment?.disclaimer ||
          "ScamGraph AI provides defensive intelligence guidance for educational and safety purposes. ScamGraph AI does not guarantee the recovery of stolen funds."}
      </div>
    </div>
  );
};
