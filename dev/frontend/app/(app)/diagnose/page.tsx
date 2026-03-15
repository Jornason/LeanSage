"use client";

import { useState } from "react";
import {
  AlertTriangle,
  Loader2,
  CheckCircle,
  XCircle,
  Copy,
  Wand2,
  GitCompare,
  ChevronDown,
  ChevronUp,
  Play,
} from "lucide-react";
import { LeanEditor } from "@/components/editor/LeanEditor";
import toast from "react-hot-toast";
import { useTranslation } from "@/lib/i18n/useTranslation";

const EXAMPLE_CODE = `theorem bad_proof (n : Nat) : n + 1 > n := by
  omega_bad`;

const EXAMPLE_ERROR = `unknown tactic 'omega_bad'`;

interface Diagnostic {
  line: number;
  column: number;
  severity: "error" | "warning" | "info";
  original_error: string;
  explanation: string;
  suggestions: {
    description: string;
    fixed_code: string;
    confidence: number;
  }[];
}

const MOCK_DIAGNOSIS: Diagnostic[] = [
  {
    line: 2,
    column: 2,
    severity: "error",
    original_error: "unknown tactic 'omega_bad'",
    explanation:
      "Lean 4 does not have a tactic named 'omega_bad'. You likely meant to use the 'omega' tactic, which automatically solves linear arithmetic goals over integers and natural numbers. The goal 'n + 1 > n' is exactly the kind of linear arithmetic goal omega handles.",
    suggestions: [
      {
        description: "Replace 'omega_bad' with 'omega'",
        fixed_code: `theorem bad_proof (n : Nat) : n + 1 > n := by
  omega`,
        confidence: 0.97,
      },
      {
        description: "Use 'linarith' as an alternative",
        fixed_code: `theorem bad_proof (n : Nat) : n + 1 > n := by
  linarith`,
        confidence: 0.82,
      },
    ],
  },
];

function DiagnosticCard({
  diagnostic,
  onApplyFix,
}: {
  diagnostic: Diagnostic;
  onApplyFix: (code: string) => void;
}) {
  const { t } = useTranslation();
  const [showDiff, setShowDiff] = useState(false);

  return (
    <div className="card border-border animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4 flex-wrap">
        <div
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
            diagnostic.severity === "error"
              ? "text-error bg-error/10 border-error/20"
              : diagnostic.severity === "warning"
              ? "text-warning bg-warning/10 border-warning/20"
              : "text-primary bg-primary/10 border-primary/20"
          }`}
        >
          <XCircle className="w-3.5 h-3.5" />
          {diagnostic.severity.toUpperCase()}
        </div>
        <code className="text-xs font-mono text-text-muted bg-bg-elevated px-2 py-0.5 rounded">
          {t.workspace.line} {diagnostic.line}, Col {diagnostic.column}
        </code>
      </div>

      {/* Original error */}
      <div className="mb-4">
        <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
          {t.diagnose.compiler_error}
        </p>
        <div className="bg-error/5 border border-error/20 rounded-lg px-3 py-2.5 font-mono text-xs text-error">
          {diagnostic.original_error}
        </div>
      </div>

      {/* AI Explanation */}
      <div className="mb-4">
        <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <Wand2 className="w-3 h-3 text-primary" />
          {t.diagnose.ai_explanation}
        </p>
        <p className="text-sm text-text-secondary leading-relaxed bg-bg-dark rounded-lg p-3">
          {diagnostic.explanation}
        </p>
      </div>

      {/* Fix suggestions */}
      {diagnostic.suggestions.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">
            {t.diagnose.fix_suggestions}
          </p>
          <div className="space-y-3">
            {diagnostic.suggestions.map((suggestion, i) => (
              <div key={i} className="fix-suggestion p-3">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs font-medium text-success">{suggestion.description}</p>
                  <span className="text-xs text-text-muted font-mono">
                    {(suggestion.confidence * 100).toFixed(0)}% {t.diagnose.confidence}
                  </span>
                </div>
                <pre className="bg-bg-dark rounded-lg p-2.5 overflow-x-auto mb-2.5">
                  <code className="text-xs font-mono text-text-secondary leading-relaxed">
                    {suggestion.fixed_code}
                  </code>
                </pre>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onApplyFix(suggestion.fixed_code)}
                    className="flex items-center gap-1.5 bg-success/20 hover:bg-success/30 border border-success/30 text-success px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
                  >
                    <CheckCircle className="w-3.5 h-3.5" />
                    {t.common.apply_fix}
                  </button>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(suggestion.fixed_code);
                      toast.success(t.common.copied);
                    }}
                    className="flex items-center gap-1.5 text-text-secondary hover:text-text-primary px-3 py-1.5 bg-bg-elevated hover:bg-border rounded-lg text-xs transition-all"
                  >
                    <Copy className="w-3.5 h-3.5" />
                    {t.common.copy}
                  </button>
                  <button
                    onClick={() => setShowDiff(!showDiff)}
                    className="flex items-center gap-1.5 text-text-secondary hover:text-text-primary px-3 py-1.5 bg-bg-elevated hover:bg-border rounded-lg text-xs transition-all ml-auto"
                  >
                    <GitCompare className="w-3.5 h-3.5" />
                    {t.common.diff}
                    {showDiff ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function DiagnosisPage() {
  const { t } = useTranslation();
  const [code, setCode] = useState(EXAMPLE_CODE);
  const [errorInput, setErrorInput] = useState(EXAMPLE_ERROR);
  const [diagnosing, setDiagnosing] = useState(false);
  const [diagnostics, setDiagnostics] = useState<Diagnostic[]>([]);
  const [diagnosed, setDiagnosed] = useState(false);

  const handleDiagnose = async () => {
    if (!code.trim()) {
      toast.error("Please enter some Lean 4 code to diagnose");
      return;
    }
    setDiagnosing(true);
    setDiagnosed(false);
    try {
      await new Promise((r) => setTimeout(r, 1500));
      setDiagnostics(MOCK_DIAGNOSIS);
      setDiagnosed(true);
    } catch {
      toast.error("Diagnosis failed. Please try again.");
    } finally {
      setDiagnosing(false);
    }
  };

  const applyFix = (fixedCode: string) => {
    setCode(fixedCode);
    setDiagnostics([]);
    setDiagnosed(false);
    toast.success(t.common.apply_fix);
  };

  return (
    <div className="h-[calc(100vh-56px)] flex flex-col">
      {/* Page header */}
      <div className="border-b border-border px-6 py-4 flex items-center justify-between bg-bg-surface/30">
        <div>
          <h1 className="text-base font-semibold text-text-primary flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-warning" />
            {t.diagnose.page_title}
          </h1>
          <p className="text-xs text-text-secondary mt-0.5">
            {t.diagnose.page_description}
          </p>
        </div>
        <button
          onClick={handleDiagnose}
          disabled={diagnosing || !code.trim()}
          className="flex items-center gap-2 bg-warning/20 hover:bg-warning/30 disabled:opacity-50 disabled:cursor-not-allowed border border-warning/30 text-warning px-5 py-2.5 rounded-xl text-sm font-medium transition-all"
        >
          {diagnosing ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          {diagnosing ? t.workspace.analyzing : t.common.diagnose}
        </button>
      </div>

      {/* Split content */}
      <div className="flex-1 overflow-hidden flex flex-col lg:flex-row">
        {/* Top/Left - Code input */}
        <div className="flex-1 flex flex-col border-b lg:border-b-0 lg:border-r border-border min-h-0">
          <div className="px-4 py-2.5 border-b border-border bg-bg-surface/20 flex items-center justify-between">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
              {t.diagnose.lean4_code}
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCode(EXAMPLE_CODE)}
                className="text-xs text-primary hover:text-primary-light transition-colors"
              >
                {t.diagnose.load_example}
              </button>
              <button
                onClick={() => {
                  setCode("");
                  setErrorInput("");
                  setDiagnostics([]);
                  setDiagnosed(false);
                }}
                className="text-xs text-text-muted hover:text-text-secondary transition-colors"
              >
                {t.common.clear}
              </button>
            </div>
          </div>
          <div className="flex-1 overflow-hidden">
            <LeanEditor
              value={code}
              onChange={setCode}
              errors={
                diagnosed && diagnostics.length > 0
                  ? diagnostics
                      .filter((d) => d.severity === "error")
                      .map((d) => ({
                        line: d.line,
                        column: d.column,
                        message: d.original_error,
                        severity: d.severity,
                      }))
                  : []
              }
            />
          </div>

          {/* Optional error input */}
          <div className="border-t border-border p-3">
            <label className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2 block">
              {t.diagnose.compiler_error_label}
            </label>
            <textarea
              value={errorInput}
              onChange={(e) => setErrorInput(e.target.value)}
              placeholder={t.diagnose.compiler_error_placeholder}
              rows={3}
              className="w-full bg-bg-dark border border-border rounded-lg px-3 py-2 text-xs font-mono text-error placeholder-text-muted outline-none focus:border-warning/50 transition-colors resize-none"
            />
          </div>
        </div>

        {/* Bottom/Right - Diagnosis results */}
        <div className="flex-1 overflow-y-auto">
          <div className="px-4 py-2.5 border-b border-border bg-bg-surface/20 sticky top-0 z-10">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
              {t.diagnose.diagnosis_results}
            </span>
            {diagnosed && (
              <span className="ml-3 text-xs text-text-muted">
                {diagnostics.length} {diagnostics.length !== 1 ? t.diagnose.issues_found : t.diagnose.issue_found}
              </span>
            )}
          </div>

          <div className="p-4">
            {!diagnosed ? (
              <div className="text-center py-16">
                <div className="text-5xl mb-4">🔬</div>
                <h3 className="text-base font-semibold text-text-primary mb-2">
                  {t.diagnose.ready_title}
                </h3>
                <p className="text-sm text-text-secondary max-w-xs mx-auto">
                  {t.diagnose.ready_description}{" "}
                  <span className="text-warning">{t.common.diagnose}</span>{" "}
                  {t.diagnose.ready_description_2}
                </p>
              </div>
            ) : diagnosing ? (
              <div className="space-y-4">
                {[1, 2].map((i) => (
                  <div key={i} className="card border-border animate-pulse">
                    <div className="skeleton h-4 w-32 rounded mb-3" />
                    <div className="skeleton h-16 rounded-lg mb-3" />
                    <div className="skeleton h-24 rounded-lg" />
                  </div>
                ))}
              </div>
            ) : diagnostics.length === 0 ? (
              <div className="text-center py-16">
                <CheckCircle className="w-12 h-12 text-success mx-auto mb-4" />
                <h3 className="text-base font-semibold text-success mb-2">{t.diagnose.no_errors_title}</h3>
                <p className="text-sm text-text-secondary">
                  {t.diagnose.no_errors_desc}
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {diagnostics.map((d, i) => (
                  <DiagnosticCard key={i} diagnostic={d} onApplyFix={applyFix} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
