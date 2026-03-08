"use client";

import { useState } from "react";
import {
  ArrowRightLeft,
  ArrowRight,
  ArrowLeft,
  Loader2,
  Copy,
  CheckCircle,
  RefreshCw,
  Clock,
  ChevronRight,
} from "lucide-react";
import { MathFormula } from "@/components/math/MathFormula";
import toast from "react-hot-toast";

type Direction = "latex-to-lean" | "lean-to-latex";

interface ConversionHistory {
  id: string;
  direction: Direction;
  input: string;
  output: string;
  timestamp: Date;
}

const EXAMPLES = {
  "latex-to-lean": [
    {
      label: "Sequence limit",
      latex: "\\forall \\epsilon > 0, \\exists N \\in \\mathbb{N}, \\forall n \\geq N, |a_n - L| < \\epsilon",
      lean: "∀ ε > 0, ∃ N : ℕ, ∀ n ≥ N, |a n - L| < ε",
    },
    {
      label: "Sum of series",
      latex: "\\sum_{n=0}^{\\infty} a_n = L",
      lean: "∑' n, a n = L",
    },
    {
      label: "Continuity",
      latex: "\\forall x_0, \\lim_{x \\to x_0} f(x) = f(x_0)",
      lean: "∀ x₀, Filter.Tendsto f (nhds x₀) (nhds (f x₀))",
    },
  ],
  "lean-to-latex": [
    {
      label: "Addition commutativity",
      lean: "∀ (a b : ℕ), a + b = b + a",
      latex: "\\forall a, b \\in \\mathbb{N},\\ a + b = b + a",
    },
    {
      label: "Continuous composition",
      lean: "Continuous f ∧ Continuous g → Continuous (f ∘ g)",
      latex: "\\text{Continuous}(f) \\wedge \\text{Continuous}(g) \\Rightarrow \\text{Continuous}(f \\circ g)",
    },
  ],
};

const MOCK_CONVERSIONS: Record<string, string> = {
  "latex-to-lean:default": "∀ ε > 0, ∃ N : ℕ, ∀ n ≥ N, |a n - L| < ε",
  "lean-to-latex:default": "\\forall \\epsilon > 0,\\ \\exists N \\in \\mathbb{N},\\ \\forall n \\geq N,\\ |a_n - L| < \\epsilon",
};

export default function ConverterPage() {
  const [direction, setDirection] = useState<Direction>("latex-to-lean");
  const [inputText, setInputText] = useState(
    "\\forall \\epsilon > 0, \\exists N \\in \\mathbb{N}, \\forall n \\geq N, |a_n - L| < \\epsilon"
  );
  const [outputText, setOutputText] = useState("");
  const [converting, setConverting] = useState(false);
  const [copied, setCopied] = useState(false);
  const [history, setHistory] = useState<ConversionHistory[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  const handleConvert = async () => {
    if (!inputText.trim()) {
      toast.error("Please enter some text to convert");
      return;
    }
    setConverting(true);
    try {
      await new Promise((r) => setTimeout(r, 1200));
      const result =
        direction === "latex-to-lean"
          ? "∀ ε > 0, ∃ N : ℕ, ∀ n ≥ N, |a n - L| < ε"
          : "\\forall \\epsilon > 0,\\ \\exists N \\in \\mathbb{N},\\ \\forall n \\geq N,\\ |a_n - L| < \\epsilon";
      setOutputText(result);
      setHistory((prev) => [
        {
          id: Date.now().toString(),
          direction,
          input: inputText,
          output: result,
          timestamp: new Date(),
        },
        ...prev.slice(0, 9),
      ]);
    } catch {
      toast.error("Conversion failed");
    } finally {
      setConverting(false);
    }
  };

  const swapDirection = () => {
    setDirection((prev) =>
      prev === "latex-to-lean" ? "lean-to-latex" : "latex-to-lean"
    );
    setInputText(outputText);
    setOutputText(inputText);
  };

  const copyOutput = () => {
    if (!outputText) return;
    navigator.clipboard.writeText(outputText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const loadExample = (example: { latex?: string; lean?: string; label: string }) => {
    if (direction === "latex-to-lean") {
      setInputText(example.latex || "");
    } else {
      setInputText(example.lean || "");
    }
    setOutputText("");
  };

  const leftLabel = direction === "latex-to-lean" ? "LaTeX" : "Lean 4";
  const rightLabel = direction === "latex-to-lean" ? "Lean 4" : "LaTeX";

  return (
    <div className="h-[calc(100vh-56px)] flex flex-col">
      {/* Page header */}
      <div className="border-b border-border px-6 py-3 flex items-center justify-between bg-bg-surface/30">
        <div>
          <h1 className="text-base font-semibold text-text-primary flex items-center gap-2">
            <ArrowRightLeft className="w-4 h-4 text-emerald-400" />
            LaTeX ↔ Lean 4 Converter
          </h1>
          <p className="text-xs text-text-secondary mt-0.5">
            Bidirectional conversion between LaTeX math and Lean 4 types
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Direction toggle */}
          <div className="flex items-center bg-bg-surface border border-border rounded-xl overflow-hidden">
            <button
              onClick={() => setDirection("latex-to-lean")}
              className={`px-3 py-2 text-xs font-medium transition-all ${
                direction === "latex-to-lean"
                  ? "bg-primary text-white"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              LaTeX → Lean
            </button>
            <button
              onClick={() => setDirection("lean-to-latex")}
              className={`px-3 py-2 text-xs font-medium transition-all ${
                direction === "lean-to-latex"
                  ? "bg-primary text-white"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              Lean → LaTeX
            </button>
          </div>

          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-1.5 text-xs text-text-secondary hover:text-text-primary px-3 py-2 bg-bg-surface border border-border rounded-xl transition-all"
          >
            <Clock className="w-3.5 h-3.5" />
            History ({history.length})
          </button>
        </div>
      </div>

      {/* Examples bar */}
      <div className="border-b border-border px-6 py-2 bg-bg-surface/20 flex items-center gap-3 overflow-x-auto">
        <span className="text-xs text-text-muted flex-shrink-0">Examples:</span>
        {EXAMPLES[direction].map((ex) => (
          <button
            key={ex.label}
            onClick={() => loadExample(ex)}
            className="text-xs px-3 py-1 bg-bg-surface hover:bg-bg-elevated border border-border hover:border-primary/30 rounded-lg text-text-secondary hover:text-text-primary transition-all whitespace-nowrap"
          >
            {ex.label}
          </button>
        ))}
      </div>

      {/* Main conversion area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left editor */}
        <div className="flex-1 flex flex-col border-r border-border">
          <div className="px-4 py-2.5 border-b border-border bg-bg-surface/20 flex items-center justify-between flex-shrink-0">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
              {leftLabel} Input
            </span>
            <button
              onClick={() => {
                setInputText("");
                setOutputText("");
              }}
              className="text-xs text-text-muted hover:text-text-secondary transition-colors"
            >
              Clear
            </button>
          </div>

          <div className="flex-1 flex flex-col overflow-hidden">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={
                direction === "latex-to-lean"
                  ? "Enter LaTeX math expression...\ne.g. \\forall x > 0, \\exists n \\in \\mathbb{N}, n > x"
                  : "Enter Lean 4 expression...\ne.g. ∀ x : ℝ, x > 0 → ∃ n : ℕ, (n : ℝ) > x"
              }
              className="flex-1 bg-bg-dark font-mono text-sm text-text-primary placeholder-text-muted p-4 outline-none resize-none"
              onKeyDown={(e) => {
                if (e.key === "Enter" && e.ctrlKey) {
                  e.preventDefault();
                  handleConvert();
                }
              }}
            />

            {/* KaTeX preview for LaTeX input */}
            {direction === "latex-to-lean" && inputText.trim() && (
              <div className="border-t border-border p-4 bg-bg-surface/20">
                <p className="text-xs text-text-muted mb-2 uppercase tracking-wider font-semibold">
                  KaTeX Preview
                </p>
                <div className="bg-bg-dark rounded-lg p-3 overflow-x-auto min-h-[40px]">
                  <MathFormula formula={inputText} display={true} />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Center - Convert button */}
        <div className="flex flex-col items-center justify-center px-3 gap-4 border-r border-border bg-bg-surface/10">
          <button
            onClick={handleConvert}
            disabled={converting || !inputText.trim()}
            className="flex flex-col items-center gap-2 w-14 h-14 rounded-full bg-primary hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed text-white transition-all shadow-glow-primary group"
            title="Convert (Ctrl+Enter)"
          >
            {converting ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <ArrowRight className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
            )}
          </button>
          <button
            onClick={swapDirection}
            className="p-2 text-text-muted hover:text-text-primary hover:bg-bg-elevated rounded-lg transition-all"
            title="Swap direction"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {/* Right - Output */}
        <div className="flex-1 flex flex-col">
          <div className="px-4 py-2.5 border-b border-border bg-bg-surface/20 flex items-center justify-between flex-shrink-0">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
              {rightLabel} Output
            </span>
            {outputText && (
              <button
                onClick={copyOutput}
                className="flex items-center gap-1.5 text-xs text-text-secondary hover:text-text-primary transition-colors"
              >
                {copied ? (
                  <CheckCircle className="w-3.5 h-3.5 text-success" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
                {copied ? "Copied!" : "Copy"}
              </button>
            )}
          </div>

          <div className="flex-1 flex flex-col overflow-hidden">
            {!outputText ? (
              <div className="flex-1 flex items-center justify-center text-center p-8">
                <div>
                  <ArrowRight className="w-8 h-8 text-text-muted mx-auto mb-3 opacity-30" />
                  <p className="text-sm text-text-muted">
                    {converting ? "Converting..." : "Output will appear here"}
                  </p>
                  <p className="text-xs text-text-muted mt-1">
                    Press Ctrl+Enter or click the arrow button
                  </p>
                </div>
              </div>
            ) : (
              <>
                <div className="flex-1 bg-bg-dark font-mono text-sm text-text-primary p-4 overflow-auto">
                  {outputText}
                </div>

                {/* KaTeX preview for LaTeX output */}
                {direction === "lean-to-latex" && outputText && (
                  <div className="border-t border-border p-4 bg-bg-surface/20">
                    <p className="text-xs text-text-muted mb-2 uppercase tracking-wider font-semibold">
                      KaTeX Preview
                    </p>
                    <div className="bg-bg-dark rounded-lg p-3 overflow-x-auto min-h-[40px]">
                      <MathFormula formula={outputText} display={true} />
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* History panel */}
        {showHistory && (
          <div className="w-64 border-l border-border bg-bg-surface/50 flex flex-col overflow-hidden animate-slide-up">
            <div className="px-4 py-3 border-b border-border flex items-center justify-between">
              <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
                History
              </span>
              <button
                onClick={() => setHistory([])}
                className="text-xs text-text-muted hover:text-text-secondary transition-colors"
              >
                Clear
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-2 space-y-2">
              {history.length === 0 ? (
                <p className="text-xs text-text-muted text-center py-6">
                  No conversions yet
                </p>
              ) : (
                history.map((h) => (
                  <button
                    key={h.id}
                    onClick={() => {
                      setInputText(h.input);
                      setOutputText(h.output);
                      setDirection(h.direction);
                    }}
                    className="w-full text-left p-2.5 bg-bg-dark hover:bg-bg-elevated rounded-lg transition-all group"
                  >
                    <div className="flex items-center gap-1.5 mb-1">
                      <span className="text-xs text-primary font-medium">
                        {h.direction === "latex-to-lean" ? "LaTeX→Lean" : "Lean→LaTeX"}
                      </span>
                      <ChevronRight className="w-3 h-3 text-text-muted group-hover:text-text-secondary" />
                    </div>
                    <p className="text-xs text-text-muted font-mono truncate">{h.input}</p>
                    <p className="text-xs text-text-secondary/60 mt-0.5">
                      {h.timestamp.toLocaleTimeString()}
                    </p>
                  </button>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
