import React, { useEffect, useState } from "react";
import {
  Settings as SettingsIcon,
  Globe2,
  Cpu,
  Save,
  CheckCircle2,
  AlertTriangle,
  Activity,
  Key,
} from "lucide-react";
import { apiClient } from "../api/client";
import { SettingsData } from "../types";

export const Settings: React.FC = () => {
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Form fields
  const [tinyfishKey, setTinyfishKey] = useState("");
  const [tinyfishBaseUrl, setTinyfishBaseUrl] = useState("https://api.tinyfish.io/v1");
  const [tinyfishEnabled, setTinyfishEnabled] = useState(false);
  const [aiModelName, setAiModelName] = useState("rule-engine-v2");

  // Test connection feedback
  const [testStatus, setTestStatus] = useState<any>(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    apiClient
      .getSettings()
      .then((data) => {
        setSettings(data);
        setTinyfishEnabled(data.tinyfish_enabled);
        setTinyfishBaseUrl(data.tinyfish_base_url || "https://api.tinyfish.io/v1");
        setAiModelName(data.ai_model_name || "rule-engine-v2");
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);

    try {
      const payload: any = {
        tinyfish_base_url: tinyfishBaseUrl,
        tinyfish_enabled: tinyfishEnabled,
        ai_model_name: aiModelName,
      };
      if (tinyfishKey) {
        payload.tinyfish_api_key = tinyfishKey;
      }

      await apiClient.updateSettings(payload);
      setSaving(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      alert("Failed to save settings.");
      setSaving(false);
    }
  };

  const handleTestTinyFish = async () => {
    setTesting(true);
    setTestStatus(null);
    try {
      const res = await apiClient.testTinyFish();
      setTestStatus(res);
      setTesting(false);
    } catch (err: any) {
      setTestStatus({
        enabled: false,
        message: "Endpoint connection failed or timed out.",
      });
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center font-mono text-cyan-400 space-x-2">
        <Activity className="w-5 h-5 animate-spin" />
        <span>Loading Configuration...</span>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-slate-100 font-mono tracking-tight flex items-center space-x-2">
          <SettingsIcon className="w-6 h-6 text-cyan-400" />
          <span>SYSTEM & API CONFIGURATION</span>
        </h1>
        <p className="text-xs text-slate-400 font-mono mt-1">
          Configure TinyFish Public Web Intelligence, external recon endpoints, and optional AI explanation engines.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* TinyFish API Configuration */}
        <div className="p-6 rounded-2xl glass-panel space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center space-x-2.5">
              <Globe2 className="w-5 h-5 text-cyan-400" />
              <div>
                <h3 className="text-sm font-bold text-slate-100 font-mono">
                  TinyFish Web Research Integration
                </h3>
                <span className="text-[11px] text-slate-400 font-mono">
                  Autonomous website extraction and corporate career verification
                </span>
              </div>
            </div>

            {/* Enable Toggle */}
            <label className="flex items-center space-x-2 cursor-pointer font-mono text-xs">
              <span className="text-slate-300">Enabled</span>
              <input
                type="checkbox"
                checked={tinyfishEnabled}
                onChange={(e) => setTinyfishEnabled(e.target.checked)}
                className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-0 cursor-pointer"
              />
            </label>
          </div>

          <div className="space-y-3">
            <div>
              <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider block mb-1">
                TinyFish API Endpoint Base URL
              </label>
              <input
                type="text"
                value={tinyfishBaseUrl}
                onChange={(e) => setTinyfishBaseUrl(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider block mb-1">
                TinyFish API Secret Key
              </label>
              <div className="relative">
                <input
                  type="password"
                  placeholder={
                    settings?.tinyfish_configured
                      ? "•••••••••••••••• (API Key Configured)"
                      : "Paste TINYFISH_API_KEY..."
                  }
                  value={tinyfishKey}
                  onChange={(e) => setTinyfishKey(e.target.value)}
                  className="w-full px-3.5 py-2 pl-9 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-400"
                />
                <Key className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              </div>
              <span className="text-[10px] text-slate-400 font-mono mt-1 block">
                Never shared with frontend clients. Read securely by the FastAPI backend server.
              </span>
            </div>

            {/* Test Connection Button */}
            <div className="pt-2 flex items-center space-x-3">
              <button
                type="button"
                onClick={handleTestTinyFish}
                disabled={testing}
                className="px-3.5 py-1.5 rounded bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-mono text-slate-300 hover:text-cyan-300 transition cursor-pointer"
              >
                {testing ? "Testing Endpoint..." : "Test TinyFish Connection"}
              </button>

              {testStatus && (
                <div
                  className={`text-xs font-mono flex items-center space-x-1.5 ${
                    testStatus.enabled ? "text-emerald-400" : "text-amber-400"
                  }`}
                >
                  {testStatus.enabled ? (
                    <CheckCircle2 className="w-4 h-4" />
                  ) : (
                    <AlertTriangle className="w-4 h-4" />
                  )}
                  <span>{testStatus.message}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* AI & Heuristic Intelligence Provider */}
        <div className="p-6 rounded-2xl glass-panel space-y-4">
          <div className="flex items-center space-x-2.5 pb-3 border-b border-slate-800">
            <Cpu className="w-5 h-5 text-purple-400" />
            <div>
              <h3 className="text-sm font-bold text-slate-100 font-mono">
                Scam Analysis & Explanation Engine
              </h3>
              <span className="text-[11px] text-slate-400 font-mono">
                Multilayer explainable heuristics + optional LLM reasoning
              </span>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <label className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider block mb-1">
                Active Analysis Engine
              </label>
              <select
                value={aiModelName}
                onChange={(e) => setAiModelName(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-100"
              >
                <option value="rule-engine-v2">Rule Engine v2 (Offline Deterministic Heuristics - Active)</option>
                <option value="gpt-4o-mini">OpenAI GPT-4o Mini (Optional External)</option>
                <option value="gemini-1.5-flash">Google Gemini 1.5 Flash (Optional External)</option>
                <option value="claude-3-haiku">Anthropic Claude 3 Haiku (Optional External)</option>
              </select>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs font-mono text-slate-300 leading-relaxed">
              <span className="font-bold text-cyan-300 block mb-0.5">
                EXPLAINABLE FALLBACK GUARANTEE:
              </span>
              When no external LLM API keys are provided, ScamGraph AI operates seamlessly with high-precision offline regex, linguistic threat vector pattern matching, and exact graph correlation.
            </div>
          </div>
        </div>

        {/* Save Bar */}
        <div className="flex items-center justify-between pt-2">
          {saveSuccess && (
            <div className="flex items-center space-x-2 text-xs font-mono text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <span>Settings updated successfully!</span>
            </div>
          )}
          {!saveSuccess && <div />}

          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs font-mono flex items-center space-x-2 transition cursor-pointer"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? "Saving..." : "Save Configuration"}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
