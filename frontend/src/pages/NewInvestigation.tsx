import React, { useState } from "react";
import {
  ShieldAlert,
  Send,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Fingerprint,
  ExternalLink,
  Terminal,
  ArrowRight,
  RotateCcw,
} from "lucide-react";
import { apiClient } from "../api/client";
import { InvestigationDetail } from "../types";

interface NewInvestigationProps {
  onInvestigationComplete: (inv: InvestigationDetail) => void;
  onNavigateToGraph: () => void;
}

export const NewInvestigation: React.FC<NewInvestigationProps> = ({
  onInvestigationComplete,
  onNavigateToGraph,
}) => {
  const [formData, setFormData] = useState({
    title: "",
    raw_text: "",
    website_url: "",
    recruiter_name: "",
    email: "",
    phone: "",
    payment_id: "",
    notes: "",
  });

  const [loading, setLoading] = useState(false);
  const [currentStage, setCurrentStage] = useState<string | null>(null);
  const [stageLogs, setStageLogs] = useState<string[]>([]);
  const [result, setResult] = useState<InvestigationDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  const sampleCases = [
    {
      label: "Tata Consultancy Services Security Deposit Scam",
      data: {
        title: "TCS Software Engineer Onboarding Scam",
        raw_text:
          "Dear Candidate, You are directly shortlisted for System Engineer at TCS. CTC: 8.5 LPA. No interview needed. Transfer Rs 4,999 refundable documentation security fee within 24 hours to UPI ID: hr.recruit@axisbank to confirm onboarding. Connect on Telegram: @tcs_hr_onboarding. Non-payment leads to legal blacklisting.",
        website_url: "https://tcs-careers-portal.online",
        recruiter_name: "Rohan Verma (TCS HR)",
        email: "tcs.careers.helpdesk@gmail.com",
        phone: "+91 98765 43210",
        payment_id: "hr.recruit@axisbank",
        notes: "Received via unsolicited SMS. Correlates with Syndicate Alpha.",
      },
    },
    {
      label: "Infosys Remote Internship Laptop Courier Scam",
      data: {
        title: "Infosys Virtual Web Dev Internship Courier Fraud",
        raw_text:
          "Infosys Virtual Internship Program: Selected for 3-month summer cohort. Free Dell laptop and kit dispatched upon payment of Rs 3,500 courier transit fee. Send immediate payment to UPI: hr.recruit@axisbank or WhatsApp +919876543210.",
        website_url: "https://infosys-internship-portal.live",
        recruiter_name: "Sneha Patel",
        email: "infosys.internship.onboard@outlook.com",
        phone: "+91 98765 43210",
        payment_id: "hr.recruit@axisbank",
        notes: "Matches the exact same payment recipient and phone as TCS case!",
      },
    },
    {
      label: "YouTube Video Rating Task Ponzi Scam",
      data: {
        title: "Global Media YouTube Rating Task Scheme",
        raw_text:
          "Earn Rs 3000 to Rs 8000 daily from home by liking YouTube videos and rating hotels. Complete 3 trial tasks on https://work-task-earn.xyz. Deposit Rs 2000 activation fee via UPI: taskmaster@ybl to unlock VIP commission withdrawals.",
        website_url: "https://work-task-earn.xyz",
        recruiter_name: "Sarah (Global Media)",
        email: "support@work-task-earn.xyz",
        phone: "+91 88776 65544",
        payment_id: "taskmaster@ybl",
        notes: "Task scam operating through high-risk .xyz domain.",
      },
    },
  ];

  const loadSample = (sample: (typeof sampleCases)[0]) => {
    setFormData(sample.data);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    // Verify at least one field is provided
    if (
      !formData.raw_text &&
      !formData.website_url &&
      !formData.email &&
      !formData.phone &&
      !formData.payment_id
    ) {
      setError("Please provide at least one field (offer text, website URL, email, phone, or payment ID).");
      return;
    }

    setLoading(true);
    setStageLogs([
      "Stage 1: Validating submitted indicators & enforcing SSRF safety checks...",
      "Stage 2: Initializing case record dossier...",
      "Stage 3: Running multi-layer behavioral scam engine across 8 threat vectors...",
      "Stage 4: Normalizing digital entities (domains, RFC emails, E.164 phones, UPI handles)...",
      "Stage 5: Querying external intelligence & TinyFish recon adapter...",
      "Stage 6: Scanning database for cross-investigation indicator matches...",
      "Stage 7: Calculating topological relationship linkages & confidence scoring...",
      "Stage 8: Generating structured intelligence report and risk explanation...",
      "Stage 9: Formulating victim safety defense checklist...",
      "Stage 10: Committing graph edges and finalizing case dossier.",
    ]);

    try {
      const inv = await apiClient.createInvestigation(formData);
      setResult(inv);
      setLoading(false);
      onInvestigationComplete(inv);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Investigation analysis failed. Please verify input.");
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      title: "",
      raw_text: "",
      website_url: "",
      recruiter_name: "",
      email: "",
      phone: "",
      payment_id: "",
      notes: "",
    });
    setResult(null);
    setError(null);
  };

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-slate-100 font-mono tracking-tight flex items-center space-x-2">
            <ShieldAlert className="w-6 h-6 text-cyan-400" />
            <span>NEW THREAT INVESTIGATION</span>
          </h1>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Ingest suspicious messages, fake recruitment websites, unsolicited job offers, and payment identifiers.
          </p>
        </div>

        <button
          onClick={resetForm}
          className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-400 hover:text-slate-200 flex items-center space-x-1.5 cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Form</span>
        </button>
      </div>

      {/* Quick Test Demo Samples */}
      <div className="p-4 rounded-xl glass-panel space-y-2">
        <div className="text-xs font-mono text-cyan-400 font-bold uppercase tracking-wider flex items-center space-x-1.5">
          <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
          <span>Pre-Configured Threat Templates (One-Click Testing)</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {sampleCases.map((s, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => loadSample(s)}
              className="px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 hover:border-cyan-500/50 text-xs font-mono text-slate-300 hover:text-cyan-300 transition cursor-pointer"
            >
              &rarr; {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Intake Form */}
      <form onSubmit={handleSubmit} className="p-6 rounded-xl glass-panel space-y-5">
        {error && (
          <div className="p-3.5 rounded-lg bg-rose-950/60 border border-rose-500/50 text-rose-300 text-xs font-mono flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider block mb-1">
              Investigation Title / Subject
            </label>
            <input
              type="text"
              placeholder="e.g. Unsolicited TCS HR Message via WhatsApp"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div className="md:col-span-2">
            <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider block mb-1">
              Suspicious Offer Message / Email Body / Transcript
            </label>
            <textarea
              rows={4}
              placeholder="Paste the full SMS, WhatsApp message, email offer letter, or job description text..."
              value={formData.raw_text}
              onChange={(e) => setFormData({ ...formData, raw_text: e.target.value })}
              className="w-full px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-400 leading-relaxed"
            />
          </div>

          <div>
            <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider block mb-1">
              Suspect Recruitment Website / URL
            </label>
            <input
              type="text"
              placeholder="https://tcs-careers-portal.online"
              value={formData.website_url}
              onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
              className="w-full px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider block mb-1">
              Claimed Recruiter or Company Name
            </label>
            <input
              type="text"
              placeholder="e.g. Rohan Verma (Tata Consultancy Services)"
              value={formData.recruiter_name}
              onChange={(e) => setFormData({ ...formData, recruiter_name: e.target.value })}
              className="w-full px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider block mb-1">
              Sender Email Address
            </label>
            <input
              type="email"
              placeholder="tcs.careers.helpdesk@gmail.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider block mb-1">
              Contact Phone / WhatsApp Number
            </label>
            <input
              type="text"
              placeholder="+91 98765 43210"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="w-full px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider block mb-1">
              Requested Payment / UPI ID / Wallet
            </label>
            <input
              type="text"
              placeholder="hr.recruit@axisbank or taskmaster@ybl"
              value={formData.payment_id}
              onChange={(e) => setFormData({ ...formData, payment_id: e.target.value })}
              className="w-full px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider block mb-1">
              Additional Evidence Notes
            </label>
            <input
              type="text"
              placeholder="Notes on communication channels, requested payment methods..."
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-400"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 text-slate-950 font-black text-sm font-mono tracking-wider flex items-center justify-center space-x-2 shadow-lg shadow-cyan-500/20 transition cursor-pointer"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              <span>RUNNING SCAMGRAPH INVESTIGATION ENGINE...</span>
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span>EXECUTE THREAT INVESTIGATION PIPELINE</span>
            </>
          )}
        </button>
      </form>

      {/* Real-time Multi-Stage Progress Terminal */}
      {loading && (
        <div className="p-5 rounded-xl bg-slate-950 border border-cyan-500/40 space-y-3 font-mono">
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase">
            <Terminal className="w-4 h-4" />
            <span>Autonomous Intelligence Pipeline In-Flight</span>
          </div>

          <div className="space-y-1.5 text-xs">
            {stageLogs.map((log, idx) => (
              <div key={idx} className="flex items-center space-x-2 text-slate-300">
                <span className="text-cyan-400">&gt;</span>
                <span>{log}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Investigation Dossier Output Card */}
      {result && !loading && (
        <div className="p-6 rounded-2xl glass-panel border border-cyan-500/40 space-y-6 animate-in fade-in duration-300">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs px-2.5 py-0.5 rounded font-mono font-bold bg-cyan-950 text-cyan-400 border border-cyan-500/40">
                  {result.case_number}
                </span>
                <span
                  className={`text-xs px-2.5 py-0.5 rounded font-mono font-bold uppercase ${
                    result.status === "CONFIRMED_SCAM"
                      ? "bg-rose-950 text-rose-300 border border-rose-500/40"
                      : result.status === "SUSPICIOUS"
                      ? "bg-amber-950 text-amber-300 border border-amber-500/40"
                      : "bg-emerald-950 text-emerald-300 border border-emerald-500/40"
                  }`}
                >
                  {result.status}
                </span>
              </div>
              <h2 className="text-lg font-bold text-slate-100 font-mono mt-1">
                {result.title}
              </h2>
            </div>

            <div className="flex items-center space-x-3">
              <div className="text-right">
                <div className="text-[10px] text-slate-400 font-mono uppercase">Overall Risk</div>
                <div className="text-2xl font-black text-rose-400 font-mono">
                  {result.overall_risk_score}/100
                </div>
              </div>
              <button
                onClick={onNavigateToGraph}
                className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs font-mono flex items-center space-x-1.5 transition cursor-pointer"
              >
                <span>View on 3D Globe</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Executive Summary */}
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-xs font-mono text-slate-300 leading-relaxed">
            <span className="font-bold text-cyan-400 block mb-1 uppercase tracking-wider">
              Executive Threat Assessment:
            </span>
            {result.summary}
          </div>

          {/* Extracted Indicators */}
          <div className="space-y-3">
            <h4 className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>Detected Red-Flag Indicators ({result.indicators.length})</span>
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {result.indicators.map((ind, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1.5"
                >
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="font-bold text-slate-200">{ind.title}</span>
                    <span
                      className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${
                        ind.severity === "CRITICAL"
                          ? "bg-rose-950 text-rose-400 border border-rose-500/40"
                          : "bg-amber-950 text-amber-400 border border-amber-500/40"
                      }`}
                    >
                      {ind.severity}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 font-mono">{ind.explanation}</p>
                  {ind.matched_snippet && (
                    <div className="text-[10px] text-cyan-300 font-mono bg-slate-950 p-1.5 rounded border border-slate-800/80">
                      &ldquo;{ind.matched_snippet}&rdquo;
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Normalized Digital Entities Linked to Graph */}
          <div className="space-y-2">
            <h4 className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
              <Fingerprint className="w-4 h-4 text-cyan-400" />
              <span>Resolved Digital Entities ({result.entities.length})</span>
            </h4>
            <div className="flex flex-wrap gap-2">
              {result.entities.map((e) => (
                <div
                  key={e.id}
                  className="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 flex items-center space-x-2"
                >
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-300 font-bold uppercase">
                    {e.entity_type}
                  </span>
                  <span className="font-semibold">{e.display_label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Verification Steps */}
          {result.analysis_results?.recommended_verification_steps && (
            <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 space-y-2">
              <span className="text-xs font-mono font-bold text-cyan-300 uppercase tracking-wider block">
                Recommended Verification Steps:
              </span>
              <ul className="space-y-1.5 text-xs font-mono text-slate-300">
                {result.analysis_results.recommended_verification_steps.map((st, i) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-cyan-400 font-bold">&bull;</span>
                    <span>{st}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
