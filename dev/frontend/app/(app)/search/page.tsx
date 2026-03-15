"use client";

import { useState, useEffect, useCallback, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  Search,
  Filter,
  Copy,
  ExternalLink,
  Loader2,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  BookOpen,
  Clock,
  Sliders,
} from "lucide-react";
import { MathFormula } from "@/components/math/MathFormula";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import { useTranslation } from "@/lib/i18n/useTranslation";

const MODULES = [
  "Topology",
  "Algebra",
  "Analysis",
  "NumberTheory",
  "Combinatorics",
  "CategoryTheory",
  "LinearAlgebra",
  "MeasureTheory",
  "Logic",
  "Order",
];

const HOT_SEARCHES = [
  "continuous function sum is continuous",
  "limit uniqueness real sequences",
  "Cauchy sequence convergence",
  "intermediate value theorem",
  "compactness in metric spaces",
];

interface SearchResult {
  rank: number;
  theorem_name: string;
  full_name: string;
  type_signature: string;
  module: string;
  doc_url: string;
  similarity: number;
}

const MOCK_RESULTS: SearchResult[] = [
  {
    rank: 1,
    theorem_name: "Continuous.add",
    full_name: "Mathlib.Topology.ContinuousOn.add",
    type_signature:
      "theorem Continuous.add {f g : α → β} [TopologicalSpace α] [TopologicalSpace β] [Add β] [ContinuousAdd β] (hf : Continuous f) (hg : Continuous g) : Continuous (fun x => f x + g x)",
    module: "Mathlib.Topology.Algebra.Group.Basic",
    doc_url:
      "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Topology/Algebra/Group/Basic.html",
    similarity: 0.934,
  },
  {
    rank: 2,
    theorem_name: "ContinuousOn.add",
    full_name: "Mathlib.Topology.ContinuousOn.add",
    type_signature:
      "theorem ContinuousOn.add {f g : α → β} {s : Set α} (hf : ContinuousOn f s) (hg : ContinuousOn g s) : ContinuousOn (fun x => f x + g x) s",
    module: "Mathlib.Topology.Algebra.Group.Basic",
    doc_url: "https://leanprover-community.github.io/mathlib4_docs/...",
    similarity: 0.891,
  },
  {
    rank: 3,
    theorem_name: "continuous_add",
    full_name: "Mathlib.Topology.Algebra.Group.continuous_add",
    type_signature:
      "theorem continuous_add [TopologicalSpace α] [Add α] [ContinuousAdd α] : Continuous (fun p : α × α => p.1 + p.2)",
    module: "Mathlib.Topology.Algebra.Group.Basic",
    doc_url: "https://leanprover-community.github.io/mathlib4_docs/...",
    similarity: 0.856,
  },
  {
    rank: 4,
    theorem_name: "Continuous.comp",
    full_name: "Mathlib.Topology.Basic.Continuous.comp",
    type_signature:
      "theorem Continuous.comp {f : β → γ} {g : α → β} (hf : Continuous f) (hg : Continuous g) : Continuous (f ∘ g)",
    module: "Mathlib.Topology.Basic",
    doc_url: "https://leanprover-community.github.io/mathlib4_docs/...",
    similarity: 0.812,
  },
  {
    rank: 5,
    theorem_name: "Continuous.mul",
    full_name: "Mathlib.Topology.Algebra.Group.Continuous.mul",
    type_signature:
      "theorem Continuous.mul {f g : α → β} [TopologicalSpace α] [TopologicalSpace β] [Mul β] [ContinuousMul β] (hf : Continuous f) (hg : Continuous g) : Continuous (fun x => f x * g x)",
    module: "Mathlib.Topology.Algebra.Group.Basic",
    doc_url: "https://leanprover-community.github.io/mathlib4_docs/...",
    similarity: 0.789,
  },
];

function getSimilarityColor(score: number) {
  if (score >= 0.9) return "text-success bg-success/10 border-success/30";
  if (score >= 0.8) return "text-primary bg-primary/10 border-primary/30";
  if (score >= 0.7) return "text-warning bg-warning/10 border-warning/30";
  return "text-text-muted bg-bg-elevated border-border";
}

function ResultCard({ result }: { result: SearchResult }) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const copyTheoremName = () => {
    navigator.clipboard.writeText(result.theorem_name);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const copyFullSignature = () => {
    navigator.clipboard.writeText(result.type_signature);
    toast.success(t.common.copied);
  };

  return (
    <div className="card border-border hover:border-border/80 transition-all duration-200 group animate-fade-in">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center gap-3 mb-3 flex-wrap">
            <span className="text-text-muted text-xs font-mono bg-bg-elevated px-2 py-0.5 rounded">
              #{result.rank}
            </span>
            <code className="text-primary font-mono text-sm font-semibold">
              {result.theorem_name}
            </code>
            <span
              className={`text-xs font-mono px-2 py-0.5 rounded-full border ${getSimilarityColor(
                result.similarity
              )}`}
            >
              {(result.similarity * 100).toFixed(1)}% {t.search.match}
            </span>
          </div>

          {/* Module path */}
          <div className="flex items-center gap-1.5 mb-3 text-xs text-text-muted font-mono">
            <BookOpen className="w-3 h-3 flex-shrink-0" />
            <span className="truncate">{result.module}</span>
          </div>

          {/* Type signature */}
          <div className="mb-3">
            <div
              className="bg-bg-dark rounded-lg p-3 overflow-hidden cursor-pointer"
              onClick={() => setExpanded(!expanded)}
            >
              <div className={`font-mono text-xs text-text-secondary leading-relaxed ${!expanded ? "line-clamp-2" : ""}`}>
                {result.type_signature}
              </div>
              {result.type_signature.length > 100 && (
                <button className="mt-1 flex items-center gap-1 text-xs text-primary hover:text-primary-light transition-colors">
                  {expanded ? (
                    <>{t.common.show_less} <ChevronUp className="w-3 h-3" /></>
                  ) : (
                    <>{t.common.show_full} <ChevronDown className="w-3 h-3" /></>
                  )}
                </button>
              )}
            </div>
          </div>

          {/* Math rendering of a simplified version */}
          <div className="bg-bg-surface/50 rounded-lg px-3 py-2 mb-3 overflow-x-auto">
            <MathFormula
              formula={`\\text{${result.theorem_name}} : \\text{Continuous}(f) \\wedge \\text{Continuous}(g) \\Rightarrow \\text{Continuous}(f + g)`}
              display={false}
            />
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border/50">
        <button
          onClick={copyTheoremName}
          className="flex items-center gap-1.5 text-xs text-text-secondary hover:text-text-primary px-3 py-1.5 bg-bg-elevated hover:bg-border rounded-lg transition-all"
        >
          {copied ? (
            <CheckCircle className="w-3.5 h-3.5 text-success" />
          ) : (
            <Copy className="w-3.5 h-3.5" />
          )}
          {copied ? t.common.copied : t.common.copy_name}
        </button>
        <button
          onClick={copyFullSignature}
          className="flex items-center gap-1.5 text-xs text-text-secondary hover:text-text-primary px-3 py-1.5 bg-bg-elevated hover:bg-border rounded-lg transition-all"
        >
          <Copy className="w-3.5 h-3.5" />
          {t.common.copy_signature}
        </button>
        <a
          href={result.doc_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 text-xs text-primary hover:text-primary-light px-3 py-1.5 bg-primary/10 hover:bg-primary/20 border border-primary/20 rounded-lg transition-all ml-auto"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          {t.common.mathlib_docs}
        </a>
      </div>
    </div>
  );
}

function SearchPageContent() {
  const { t } = useTranslation();
  const searchParams = useSearchParams();
  const router = useRouter();
  const initialQuery = searchParams.get("q") || "";

  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [topK, setTopK] = useState(5);
  const [selectedModules, setSelectedModules] = useState<string[]>([]);
  const [filterOpen, setFilterOpen] = useState(false);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);

  const performSearch = useCallback(
    async (q: string) => {
      if (!q.trim()) return;
      setLoading(true);
      setSearched(true);
      try {
        // API call - use mock data for now
        await new Promise((r) => setTimeout(r, 800));
        setResults(MOCK_RESULTS.slice(0, topK));
        setSearchHistory((prev) => [q, ...prev.filter((h) => h !== q)].slice(0, 5));
      } catch (err) {
        toast.error("Search failed. Please try again.");
      } finally {
        setLoading(false);
      }
    },
    [topK]
  );

  useEffect(() => {
    if (initialQuery) {
      performSearch(initialQuery);
    }
  }, [initialQuery, performSearch]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    router.push(`/search?q=${encodeURIComponent(query)}`);
    performSearch(query);
  };

  const toggleModule = (module: string) => {
    setSelectedModules((prev) =>
      prev.includes(module) ? prev.filter((m) => m !== module) : [...prev, module]
    );
  };

  return (
    <div className="flex h-[calc(100vh-56px)]">
      {/* Left sidebar - Filters */}
      <aside
        className={`${
          filterOpen ? "w-56" : "w-0 overflow-hidden"
        } md:w-56 border-r border-border bg-bg-surface/50 flex-shrink-0 transition-all duration-300`}
      >
        <div className="p-4 space-y-5 overflow-y-auto h-full">
          <div>
            <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3 flex items-center gap-2">
              <Filter className="w-3.5 h-3.5" />
              {t.search.modules}
            </h3>
            <div className="space-y-1.5">
              {MODULES.map((module) => (
                <label
                  key={module}
                  className="flex items-center gap-2 cursor-pointer group"
                >
                  <div
                    onClick={() => toggleModule(module)}
                    className={`w-4 h-4 rounded border flex items-center justify-center transition-all flex-shrink-0 ${
                      selectedModules.includes(module)
                        ? "bg-primary border-primary"
                        : "border-border group-hover:border-primary/50"
                    }`}
                  >
                    {selectedModules.includes(module) && (
                      <CheckCircle className="w-2.5 h-2.5 text-white" />
                    )}
                  </div>
                  <span
                    onClick={() => toggleModule(module)}
                    className="text-xs text-text-secondary group-hover:text-text-primary transition-colors"
                  >
                    {module}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3 flex items-center gap-2">
              <Sliders className="w-3.5 h-3.5" />
              {t.search.results_count}
            </h3>
            <div className="space-y-2">
              <input
                type="range"
                min={1}
                max={20}
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full accent-primary"
              />
              <div className="flex justify-between text-xs text-text-muted">
                <span>1</span>
                <span className="text-primary font-medium">Top {topK}</span>
                <span>20</span>
              </div>
            </div>
          </div>

          {searchHistory.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3 flex items-center gap-2">
                <Clock className="w-3.5 h-3.5" />
                {t.search.recent}
              </h3>
              <div className="space-y-1">
                {searchHistory.map((h) => (
                  <button
                    key={h}
                    onClick={() => {
                      setQuery(h);
                      performSearch(h);
                    }}
                    className="w-full text-left text-xs text-text-muted hover:text-text-primary truncate py-1 px-2 hover:bg-bg-elevated rounded transition-colors"
                  >
                    {h}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Search bar */}
        <div className="p-4 border-b border-border bg-bg-surface/30">
          <form onSubmit={handleSearch} className="flex gap-3">
            <button
              type="button"
              onClick={() => setFilterOpen(!filterOpen)}
              className="md:hidden p-2.5 bg-bg-surface border border-border rounded-xl text-text-secondary hover:text-text-primary transition-colors"
            >
              <Filter className="w-4 h-4" />
            </button>
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={t.search.search_placeholder}
                className="w-full bg-bg-surface border border-border hover:border-border/80 focus:border-primary rounded-xl pl-10 pr-4 py-3 text-sm text-text-primary placeholder-text-muted outline-none transition-colors"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="bg-primary hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-3 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              <span className="hidden sm:block">{t.common.search}</span>
            </button>
          </form>
        </div>

        {/* Results area */}
        <div className="flex-1 overflow-y-auto p-4">
          {!searched ? (
            /* Empty state - hot searches */
            <div className="max-w-2xl mx-auto mt-12 text-center">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                {t.search.page_title}
              </h3>
              <p className="text-text-secondary text-sm mb-8">
                {t.search.search_description}
              </p>
              <div className="text-left">
                <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">
                  {t.search.popular_searches}
                </p>
                <div className="flex flex-wrap gap-2">
                  {HOT_SEARCHES.map((s) => (
                    <button
                      key={s}
                      onClick={() => {
                        setQuery(s);
                        performSearch(s);
                      }}
                      className="text-sm px-4 py-2 bg-bg-surface hover:bg-bg-elevated border border-border hover:border-primary/30 rounded-xl text-text-secondary hover:text-text-primary transition-all"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : loading ? (
            /* Skeleton loading */
            <div className="space-y-4 max-w-3xl">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="card border-border animate-pulse">
                  <div className="flex gap-3 mb-3">
                    <div className="skeleton w-6 h-4 rounded" />
                    <div className="skeleton w-40 h-4 rounded" />
                    <div className="skeleton w-20 h-4 rounded" />
                  </div>
                  <div className="skeleton w-3/4 h-3 rounded mb-2" />
                  <div className="skeleton w-full h-16 rounded-lg mb-3" />
                  <div className="skeleton w-full h-8 rounded-lg" />
                </div>
              ))}
            </div>
          ) : results.length === 0 ? (
            /* No results */
            <div className="max-w-2xl mx-auto mt-12 text-center">
              <div className="text-6xl mb-4">🤔</div>
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                {t.search.no_results_title}
              </h3>
              <p className="text-text-secondary text-sm mb-4">
                {t.search.no_results_desc}
              </p>
              <button
                onClick={() => {
                  setSelectedModules([]);
                  setQuery("");
                  setSearched(false);
                }}
                className="btn-secondary text-sm"
              >
                {t.search.clear_filters}
              </button>
            </div>
          ) : (
            /* Results */
            <div className="max-w-3xl space-y-4">
              <div className="flex items-center justify-between text-xs text-text-muted mb-2">
                <span>
                  {t.search.found_results} <span className="text-text-secondary font-medium">{results.length}</span> {t.search.results}
                  {selectedModules.length > 0 && (
                    <span> {t.search.in_modules} {selectedModules.join(", ")}</span>
                  )}
                </span>
                <span>{t.search.sorted_by_relevance}</span>
              </div>
              {results.map((result) => (
                <ResultCard key={result.full_name} result={result} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-full"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>}>
      <SearchPageContent />
    </Suspense>
  );
}
