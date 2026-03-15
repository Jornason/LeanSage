"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Cpu,
  AlertTriangle,
  ArrowRightLeft,
  Github,
  ArrowRight,
  CheckCircle,
  BookOpen,
  Zap,
  Star,
  ChevronRight,
} from "lucide-react";
import { useTranslation } from "@/lib/i18n/useTranslation";

const DEMO_LEAN_CODE = `import Mathlib.Topology.Algebra.Group.Basic

-- Prove that the sum of continuous functions is continuous
theorem sum_continuous {α β : Type*}
    [TopologicalSpace α] [TopologicalSpace β]
    [Add β] [ContinuousAdd β]
    {f g : α → β}
    (hf : Continuous f) (hg : Continuous g) :
    Continuous (fun x => f x + g x) := by
  exact Continuous.add hf hg`;

export default function LandingPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const { t } = useTranslation();

  const FEATURES = [
    {
      icon: Search,
      title: t.landing.feature_search_title,
      description: t.landing.feature_search_desc,
      color: "text-blue-400",
      bg: "bg-blue-500/10",
      border: "border-blue-500/20",
      href: "/search",
    },
    {
      icon: Cpu,
      title: t.landing.feature_ai_title,
      description: t.landing.feature_ai_desc,
      color: "text-violet-400",
      bg: "bg-violet-500/10",
      border: "border-violet-500/20",
      href: "/workspace",
    },
    {
      icon: AlertTriangle,
      title: t.landing.feature_diagnosis_title,
      description: t.landing.feature_diagnosis_desc,
      color: "text-amber-400",
      bg: "bg-amber-500/10",
      border: "border-amber-500/20",
      href: "/diagnose",
    },
    {
      icon: ArrowRightLeft,
      title: t.landing.feature_converter_title,
      description: t.landing.feature_converter_desc,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
      href: "/convert",
    },
  ];

  const TESTIMONIALS = [
    {
      name: t.landing.testimonial_1_name,
      role: t.landing.testimonial_1_role,
      avatar: "SC",
      text: t.landing.testimonial_1_text,
      rating: 5,
    },
    {
      name: t.landing.testimonial_2_name,
      role: t.landing.testimonial_2_role,
      avatar: "MW",
      text: t.landing.testimonial_2_text,
      rating: 5,
    },
    {
      name: t.landing.testimonial_3_name,
      role: t.landing.testimonial_3_role,
      avatar: "YT",
      text: t.landing.testimonial_3_text,
      rating: 5,
    },
  ];

  const PRICING = [
    {
      name: t.landing.plan_free,
      price: "$0",
      period: t.landing.per_month,
      description: t.landing.plan_free_desc,
      features: t.landing.plan_free_features,
      cta: t.landing.cta_start_free,
      highlighted: false,
    },
    {
      name: t.landing.plan_researcher,
      price: "$19",
      period: t.landing.per_month,
      description: t.landing.plan_researcher_desc,
      features: t.landing.plan_researcher_features,
      cta: t.landing.cta_start_trial,
      highlighted: true,
    },
    {
      name: t.landing.plan_lab,
      price: "$99",
      period: t.landing.per_month,
      description: t.landing.plan_lab_desc,
      features: t.landing.plan_lab_features,
      cta: t.landing.cta_contact_sales,
      highlighted: false,
    },
  ];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <div className="min-h-screen bg-bg-dark">
      {/* Navigation */}
      <nav className="border-b border-border/50 backdrop-blur-md sticky top-0 z-50 bg-bg-dark/90">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <span className="text-white text-xs font-bold">LP</span>
            </div>
            <span className="font-semibold text-text-primary">{t.common.app_name}</span>
          </div>
          <div className="hidden md:flex items-center gap-6 text-sm text-text-secondary">
            <Link href="/search" className="hover:text-text-primary transition-colors">{t.common.search}</Link>
            <Link href="/workspace" className="hover:text-text-primary transition-colors">{t.common.workspace}</Link>
            <Link href="/convert" className="hover:text-text-primary transition-colors">{t.common.converter}</Link>
            <Link href="/#pricing" className="hover:text-text-primary transition-colors">{t.common.pricing}</Link>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/demo"
              className="text-sm text-emerald-400 hover:text-emerald-300 font-medium transition-colors border border-emerald-400/30 rounded-lg px-3 py-1.5"
            >
              {t.common.try_demo}
            </Link>
            <Link
              href="/login"
              className="text-sm text-text-secondary hover:text-text-primary transition-colors"
            >
              {t.common.sign_in}
            </Link>
            <Link
              href="/login"
              className="btn-primary text-sm py-1.5 px-4"
            >
              {t.common.get_started}
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background decorations */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl" />
          <div className="absolute top-40 right-1/4 w-64 h-64 bg-secondary/10 rounded-full blur-3xl" />
          {/* Math symbols decoration */}
          <div className="absolute top-16 left-16 text-primary/10 text-6xl font-mono select-none">∀</div>
          <div className="absolute top-32 right-24 text-secondary/10 text-5xl font-mono select-none">∃</div>
          <div className="absolute bottom-16 left-32 text-primary/10 text-4xl font-mono select-none">λ</div>
          <div className="absolute bottom-32 right-16 text-secondary/10 text-5xl font-mono select-none">∑</div>
          <div className="absolute top-48 left-1/2 text-primary/5 text-8xl font-mono select-none">⊢</div>
        </div>

        <div className="relative max-w-5xl mx-auto px-6 pt-20 pb-24 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-medium mb-8">
            <Zap className="w-3 h-3" />
            {t.landing.badge}
          </div>

          <h1 className="text-5xl md:text-6xl font-bold text-text-primary leading-tight mb-6">
            {t.landing.hero_title_1}{" "}
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              {t.landing.hero_title_2}
            </span>{" "}
            {t.landing.hero_title_4}{" "}
            <span className="bg-gradient-to-r from-secondary to-blue-400 bg-clip-text text-transparent">
              {t.landing.hero_title_3}
            </span>
          </h1>

          <p className="text-lg text-text-secondary max-w-2xl mx-auto mb-10 leading-relaxed">
            {t.landing.hero_description}
          </p>

          {/* Search bar */}
          <form onSubmit={handleSearch} className="relative max-w-2xl mx-auto mb-8">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-secondary/20 rounded-xl blur-sm group-hover:blur-md transition-all" />
              <div className="relative flex items-center bg-bg-surface border border-border rounded-xl overflow-hidden">
                <Search className="w-5 h-5 text-text-muted ml-4 flex-shrink-0" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t.landing.search_placeholder}
                  className="flex-1 bg-transparent px-4 py-4 text-text-primary placeholder-text-muted outline-none text-sm"
                />
                <button
                  type="submit"
                  className="m-2 bg-primary hover:bg-primary-dark text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                >
                  {t.landing.search_btn}
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </form>

          <div className="flex items-center justify-center gap-6 text-sm text-text-muted">
            <div className="flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-success" />
              {t.landing.stat_theorems}
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-success" />
              {t.landing.stat_no_credit_card}
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-success" />
              {t.landing.stat_free_tier}
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-text-primary mb-4">
              {t.landing.features_heading}
            </h2>
            <p className="text-text-secondary max-w-xl mx-auto">
              {t.landing.features_subheading}
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {FEATURES.map((feature) => (
              <Link
                key={feature.title}
                href={feature.href}
                className={`group relative card border ${feature.border} hover:border-opacity-60 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg`}
              >
                <div className={`w-10 h-10 ${feature.bg} rounded-lg flex items-center justify-center mb-4`}>
                  <feature.icon className={`w-5 h-5 ${feature.color}`} />
                </div>
                <h3 className="font-semibold text-text-primary mb-2">{feature.title}</h3>
                <p className="text-sm text-text-secondary leading-relaxed">{feature.description}</p>
                <div className={`mt-4 flex items-center gap-1 text-xs ${feature.color} font-medium opacity-0 group-hover:opacity-100 transition-opacity`}>
                  {t.common.try_it_now} <ChevronRight className="w-3 h-3" />
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section className="py-20 px-6 bg-bg-surface/30">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-text-primary mb-4">{t.landing.demo_heading}</h2>
            <p className="text-text-secondary">{t.landing.demo_subheading}</p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Natural language input */}
            <div className="card border-border">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-2 h-2 rounded-full bg-error" />
                <div className="w-2 h-2 rounded-full bg-warning" />
                <div className="w-2 h-2 rounded-full bg-success" />
                <span className="ml-2 text-xs text-text-muted font-mono">{t.landing.demo_natural_language}</span>
              </div>
              <div className="bg-bg-dark rounded-lg p-4 text-sm text-text-secondary leading-relaxed">
                <p className="text-text-primary font-medium mb-2">{t.landing.demo_theorem_desc_label}</p>
                <p className="italic">
                  &ldquo;{t.landing.demo_theorem_desc}&rdquo;
                </p>
              </div>
            </div>

            {/* Generated Lean code */}
            <div className="card border-border">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-2 h-2 rounded-full bg-error" />
                <div className="w-2 h-2 rounded-full bg-warning" />
                <div className="w-2 h-2 rounded-full bg-success" />
                <span className="ml-2 text-xs text-text-muted font-mono">{t.landing.demo_generated_lean}</span>
                <span className="ml-auto text-xs text-success flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" /> {t.landing.demo_compiled}
                </span>
              </div>
              <pre className="bg-bg-dark rounded-lg p-4 overflow-x-auto">
                <code className="text-xs font-mono leading-relaxed">
                  <span className="text-blue-400">import</span>
                  <span className="text-text-primary"> Mathlib.Topology.Algebra.Group.Basic{"\n\n"}</span>
                  <span className="text-violet-400">theorem</span>
                  <span className="text-yellow-400"> sum_continuous</span>
                  <span className="text-text-primary"> {"{α β : Type*}"}{"\n"}</span>
                  <span className="text-text-secondary">    [TopologicalSpace α] [TopologicalSpace β]{"\n"}</span>
                  <span className="text-text-secondary">    [Add β] [ContinuousAdd β]{"\n"}</span>
                  <span className="text-text-secondary">    {"{f g : α → β}"}{"\n"}</span>
                  <span className="text-text-secondary">    (hf : Continuous f) (hg : Continuous g) :{"\n"}</span>
                  <span className="text-text-primary">    Continuous (</span>
                  <span className="text-blue-400">fun</span>
                  <span className="text-text-primary"> x ={">"} f x + g x) := </span>
                  <span className="text-violet-400">by{"\n"}</span>
                  <span className="text-text-primary">  exact Continuous.add hf hg</span>
                </code>
              </pre>
            </div>
          </div>

          <div className="text-center mt-8">
            <Link href="/workspace" className="btn-primary inline-flex">
              {t.landing.demo_try_workspace}
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-text-primary mb-4">
              {t.landing.testimonials_heading}
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {TESTIMONIALS.map((item) => (
              <div key={item.name} className="card border-border">
                <div className="flex items-center gap-1 mb-3">
                  {Array.from({ length: item.rating }).map((_, i) => (
                    <Star key={i} className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                  ))}
                </div>
                <p className="text-sm text-text-secondary leading-relaxed mb-4 italic">
                  &ldquo;{item.text}&rdquo;
                </p>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xs font-bold">
                    {item.avatar}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-text-primary">{item.name}</p>
                    <p className="text-xs text-text-muted">{item.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 px-6 bg-bg-surface/30">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-text-primary mb-4">{t.landing.pricing_heading}</h2>
            <p className="text-text-secondary">{t.landing.pricing_subheading}</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {PRICING.map((plan) => (
              <div
                key={plan.name}
                className={`relative card flex flex-col ${
                  plan.highlighted
                    ? "border-primary shadow-glow-primary ring-1 ring-primary/30"
                    : "border-border"
                }`}
              >
                {plan.highlighted && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-white text-xs px-3 py-1 rounded-full font-medium">
                    {t.landing.plan_most_popular}
                  </div>
                )}
                <div className="mb-6">
                  <h3 className="font-semibold text-text-primary mb-1">{plan.name}</h3>
                  <p className="text-text-muted text-sm mb-3">{plan.description}</p>
                  <div className="flex items-baseline gap-1">
                    <span className="text-3xl font-bold text-text-primary">{plan.price}</span>
                    <span className="text-text-muted text-sm">{plan.period}</span>
                  </div>
                </div>
                <ul className="space-y-2 mb-6 flex-1">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-text-secondary">
                      <CheckCircle className="w-4 h-4 text-success flex-shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/login"
                  className={`w-full text-center py-2.5 px-4 rounded-lg font-medium text-sm transition-colors ${
                    plan.highlighted
                      ? "bg-primary hover:bg-primary-dark text-white"
                      : "bg-bg-elevated hover:bg-border text-text-primary"
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-md bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <span className="text-white text-xs font-bold">LP</span>
              </div>
              <span className="font-semibold text-text-primary">{t.common.app_name}</span>
              <span className="text-text-muted text-sm ml-2">{t.common.copyright}</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-text-secondary">
              <Link href="/search" className="hover:text-text-primary transition-colors">{t.common.search}</Link>
              <Link href="/workspace" className="hover:text-text-primary transition-colors">{t.common.workspace}</Link>
              <Link href="/convert" className="hover:text-text-primary transition-colors">{t.common.converter}</Link>
              <a
                href="https://github.com"
                className="hover:text-text-primary transition-colors flex items-center gap-1"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Github className="w-4 h-4" />
                {t.common.github}
              </a>
              <a
                href="https://leanprover-community.github.io/mathlib4_docs/"
                className="hover:text-text-primary transition-colors flex items-center gap-1"
                target="_blank"
                rel="noopener noreferrer"
              >
                <BookOpen className="w-4 h-4" />
                {t.common.mathlib_docs}
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
