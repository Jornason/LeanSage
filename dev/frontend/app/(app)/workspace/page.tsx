"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import {
  Play,
  CheckCircle,
  XCircle,
  Loader2,
  Plus,
  FileCode,
  ChevronRight,
  Cpu,
  AlertTriangle,
  BookOpen,
  Copy,
  Download,
  Send,
  Wand2,
  Info,
} from "lucide-react";
import { LeanEditor } from "@/components/editor/LeanEditor";
import toast from "react-hot-toast";

const DEFAULT_CODE = `import Mathlib.Tactic

-- Welcome to LeanProve AI Workspace
-- Start writing your Lean 4 proof here

theorem add_comm_example (a b : ℕ) : a + b = b + a := by
  ring

-- Try generating a proof using the AI panel on the right!
`;

const MOCK_FILES = [
  { name: "main.lean", active: true },
  { name: "helpers.lean", active: false },
  { name: "examples.lean", active: false },
];

type CompileStatus = "idle" | "compiling" | "success" | "error";

interface CompilationError {
  line: number;
  column: number;
  message: string;
  severity: "error" | "warning";
}

type AITab = "generate" | "diagnose" | "explain";

export default function WorkspacePage() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [compileStatus, setCompileStatus] = useState<CompileStatus>("idle");
  const [errors, setErrors] = useState<CompilationError[]>([]);
  const [activeAITab, setActiveAITab] = useState<AITab>("generate");
  const [generateInput, setGenerateInput] = useState("");
  const [generatedCode, setGeneratedCode] = useState("");
  const [generating, setGenerating] = useState(false);
  const [diagnosing, setDiagnosing] = useState(false);
  const [diagnosisResult, setDiagnosisResult] = useState<any>(null);
  const [files, setFiles] = useState(MOCK_FILES);
  const [goalText, setGoalText] = useState("⊢ a + b = b + a");

  const handleCompile = async () => {
    setCompileStatus("compiling");
    setErrors([]);
    try {
      await new Promise((r) => setTimeout(r, 2000));
      // Simulate success or error based on code content
      if (code.includes("omega_bad") || code.includes("sorry_bad")) {
        setCompileStatus("error");
        setErrors([
          {
            line: 5,
            column: 2,
            message: "unknown tactic 'omega_bad'",
            severity: "error",
          },
        ]);
      } else {
        setCompileStatus("success");
        setErrors([]);
        toast.success("Compiled successfully!");
      }
    } catch (err) {
      setCompileStatus("error");
      toast.error("Compilation failed");
    }
  };

  const handleGenerate = async () => {
    if (!generateInput.trim()) return;
    setGenerating(true);
    try {
      await new Promise((r) => setTimeout(r, 2500));
      const generated = `import Mathlib.Tactic

theorem generated_proof (n : ℕ) : n + 0 = n := by
  simp`;
      setGeneratedCode(generated);
    } catch {
      toast.error("Generation failed");
    } finally {
      setGenerating(false);
    }
  };

  const insertGeneratedCode = () => {
    setCode(generatedCode);
    toast.success("Code inserted into editor");
  };

  const handleDiagnose = async () => {
    setDiagnosing(true);
    setDiagnosisResult(null);
    try {
      await new Promise((r) => setTimeout(r, 1800));
      setDiagnosisResult({
        diagnostics: [
          {
            line: 5,
            severity: "info",
            explanation: "Your proof looks correct. The `ring` tactic successfully closes the goal.",
            suggestions: [],
          },
        ],
      });
    } catch {
      toast.error("Diagnosis failed");
    } finally {
      setDiagnosing(false);
    }
  };

  const statusConfig = {
    idle: { icon: null, text: "Ready", color: "text-text-muted" },
    compiling: {
      icon: <Loader2 className="w-3.5 h-3.5 animate-spin" />,
      text: "Compiling...",
      color: "text-warning",
    },
    success: {
      icon: <CheckCircle className="w-3.5 h-3.5" />,
      text: "Compiled OK",
      color: "text-success",
    },
    error: {
      icon: <XCircle className="w-3.5 h-3.5" />,
      text: `${errors.length} error${errors.length !== 1 ? "s" : ""}`,
      color: "text-error",
    },
  };

  const status = statusConfig[compileStatus];

  return (
    <div className="ide-container h-[calc(100vh-56px)]">
      {/* Left panel - File tree */}
      <aside className="border-r border-border bg-bg-surface/50 ide-file-tree flex flex-col">
        <div className="px-3 py-2.5 border-b border-border flex items-center justify-between">
          <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
            Files
          </span>
          <button
            className="p-0.5 text-text-muted hover:text-text-primary transition-colors"
            title="New file"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-1.5">
          {files.map((file) => (
            <button
              key={file.name}
              onClick={() =>
                setFiles((prev) =>
                  prev.map((f) => ({ ...f, active: f.name === file.name }))
                )
              }
              className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs transition-all ${
                file.active
                  ? "bg-primary/20 text-primary"
                  : "text-text-secondary hover:bg-bg-elevated hover:text-text-primary"
              }`}
            >
              <FileCode className="w-3.5 h-3.5 flex-shrink-0" />
              <span className="truncate">{file.name}</span>
            </button>
          ))}
        </div>

        {/* Goal view */}
        <div className="border-t border-border p-3">
          <div className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Info className="w-3 h-3" />
            Proof Goal
          </div>
          <div className="bg-bg-dark rounded-lg p-2.5 proof-goal text-xs">
            {goalText}
          </div>
        </div>
      </aside>

      {/* Center panel - Editor */}
      <div className="flex flex-col overflow-hidden border-r border-border">
        {/* Editor toolbar */}
        <div className="h-9 border-b border-border flex items-center px-3 gap-3 bg-bg-surface/30">
          <div className="flex items-center gap-1.5 text-xs text-text-muted font-mono flex-1 min-w-0">
            <FileCode className="w-3.5 h-3.5 text-primary flex-shrink-0" />
            <span className="truncate">
              {files.find((f) => f.active)?.name ?? "main.lean"}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                navigator.clipboard.writeText(code);
                toast.success("Copied to clipboard");
              }}
              className="p-1.5 text-text-muted hover:text-text-primary hover:bg-bg-elevated rounded-md transition-all"
              title="Copy code"
            >
              <Copy className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={handleCompile}
              disabled={compileStatus === "compiling"}
              className="flex items-center gap-1.5 bg-success/20 hover:bg-success/30 border border-success/30 text-success px-3 py-1 rounded-lg text-xs font-medium transition-all disabled:opacity-50"
            >
              {compileStatus === "compiling" ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Play className="w-3.5 h-3.5" />
              )}
              Compile
            </button>
          </div>
        </div>

        {/* Code editor */}
        <div className="flex-1 overflow-hidden">
          <LeanEditor
            value={code}
            onChange={setCode}
            errors={errors}
          />
        </div>

        {/* Status bar */}
        <div className="h-7 border-t border-border flex items-center px-3 gap-4 text-xs bg-bg-surface/50">
          <div className={`flex items-center gap-1.5 ${status.color}`}>
            {status.icon}
            <span>{status.text}</span>
          </div>
          {errors.length > 0 && (
            <div className="flex items-center gap-1.5 text-error">
              <XCircle className="w-3 h-3" />
              {errors.map((e) => (
                <span key={`${e.line}-${e.column}`}>
                  Line {e.line}: {e.message}
                </span>
              ))}
            </div>
          )}
          <div className="ml-auto flex items-center gap-3 text-text-muted">
            <span>Lean 4.8.0</span>
            <span>Mathlib 2026-03</span>
            <span>Ln {code.split("\n").length}</span>
          </div>
        </div>
      </div>

      {/* Right panel - AI */}
      <aside className="flex flex-col overflow-hidden bg-bg-surface/30">
        {/* AI Panel tabs */}
        <div className="border-b border-border">
          <div className="flex">
            {(["generate", "diagnose", "explain"] as AITab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveAITab(tab)}
                className={`flex-1 py-2.5 text-xs font-medium capitalize transition-all border-b-2 ${
                  activeAITab === tab
                    ? "text-primary border-primary bg-primary/5"
                    : "text-text-muted border-transparent hover:text-text-secondary"
                }`}
              >
                {tab === "generate" && <Wand2 className="w-3.5 h-3.5 inline mr-1.5" />}
                {tab === "diagnose" && <AlertTriangle className="w-3.5 h-3.5 inline mr-1.5" />}
                {tab === "explain" && <BookOpen className="w-3.5 h-3.5 inline mr-1.5" />}
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* AI Panel content */}
        <div className="flex-1 overflow-y-auto p-4">
          {activeAITab === "generate" && (
            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-text-secondary mb-2 block">
                  Describe your theorem
                </label>
                <textarea
                  value={generateInput}
                  onChange={(e) => setGenerateInput(e.target.value)}
                  placeholder="e.g. Prove that for all natural numbers n, n + 0 = n"
                  rows={4}
                  className="w-full bg-bg-dark border border-border rounded-xl px-3 py-2.5 text-sm text-text-primary placeholder-text-muted outline-none focus:border-primary transition-colors resize-none"
                />
              </div>
              <button
                onClick={handleGenerate}
                disabled={generating || !generateInput.trim()}
                className="w-full flex items-center justify-center gap-2 bg-primary hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed text-white py-2.5 rounded-xl text-sm font-medium transition-all"
              >
                {generating ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Wand2 className="w-4 h-4" />
                )}
                {generating ? "Generating..." : "Generate Proof"}
              </button>

              {generatedCode && (
                <div className="space-y-3 animate-fade-in">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-success flex items-center gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5" />
                      Generated
                    </span>
                  </div>
                  <pre className="bg-bg-dark rounded-xl p-3 overflow-x-auto">
                    <code className="text-xs font-mono text-text-secondary leading-relaxed">
                      {generatedCode}
                    </code>
                  </pre>
                  <button
                    onClick={insertGeneratedCode}
                    className="w-full flex items-center justify-center gap-2 bg-success/20 hover:bg-success/30 border border-success/30 text-success py-2 rounded-xl text-sm font-medium transition-all"
                  >
                    <ChevronRight className="w-4 h-4" />
                    Insert into Editor
                  </button>
                </div>
              )}
            </div>
          )}

          {activeAITab === "diagnose" && (
            <div className="space-y-4">
              <p className="text-xs text-text-secondary leading-relaxed">
                Click below to diagnose errors in the current editor code. AI will explain
                errors and suggest fixes.
              </p>
              <button
                onClick={handleDiagnose}
                disabled={diagnosing}
                className="w-full flex items-center justify-center gap-2 bg-warning/20 hover:bg-warning/30 border border-warning/30 text-warning py-2.5 rounded-xl text-sm font-medium transition-all disabled:opacity-50"
              >
                {diagnosing ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <AlertTriangle className="w-4 h-4" />
                )}
                {diagnosing ? "Analyzing..." : "Diagnose Current Code"}
              </button>

              {diagnosisResult && (
                <div className="space-y-3 animate-fade-in">
                  {diagnosisResult.diagnostics.map((d: any, i: number) => (
                    <div key={i} className="bg-bg-dark rounded-xl p-3 border border-border">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs text-text-muted font-mono">Line {d.line}</span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${
                            d.severity === "error"
                              ? "bg-error/10 text-error border border-error/20"
                              : d.severity === "warning"
                              ? "bg-warning/10 text-warning border border-warning/20"
                              : "bg-success/10 text-success border border-success/20"
                          }`}
                        >
                          {d.severity}
                        </span>
                      </div>
                      <p className="text-xs text-text-secondary leading-relaxed">
                        {d.explanation}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeAITab === "explain" && (
            <div className="space-y-4">
              <p className="text-xs text-text-secondary leading-relaxed">
                Select a tactic in the editor to get a plain-language explanation of what it does.
              </p>
              <div className="bg-bg-dark rounded-xl p-4 border border-border/50">
                <div className="text-xs text-text-muted mb-2 font-mono">ring</div>
                <p className="text-xs text-text-secondary leading-relaxed">
                  The <code className="font-mono text-primary">ring</code> tactic proves goals that follow
                  from the axioms of a commutative (semi)ring. It closes goals like{" "}
                  <code className="font-mono text-primary">a + b = b + a</code> automatically.
                </p>
              </div>
              <div className="bg-bg-dark rounded-xl p-4 border border-border/50">
                <div className="text-xs text-text-muted mb-2 font-mono">simp</div>
                <p className="text-xs text-text-secondary leading-relaxed">
                  The <code className="font-mono text-primary">simp</code> tactic simplifies the goal
                  using a collection of lemmas marked with the <code className="font-mono text-primary">@[simp]</code>{" "}
                  attribute. It can close many routine goals automatically.
                </p>
              </div>
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}
