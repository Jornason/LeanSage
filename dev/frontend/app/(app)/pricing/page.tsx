"use client";

import { useState } from "react";
import Link from "next/link";
import {
  CheckCircle,
  Zap,
  Users,
  Building2,
  ArrowRight,
  HelpCircle,
} from "lucide-react";
import { useTranslation } from "@/lib/i18n/useTranslation";

export default function PricingPage() {
  const { t } = useTranslation();
  const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">("monthly");
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  const PRICING_PLANS = [
    {
      name: t.pricing.plan_free,
      price: "$0",
      period: t.pricing.per_month,
      description: t.pricing.plan_free_desc,
      icon: Zap,
      color: "text-text-secondary",
      borderColor: "border-border",
      features: t.pricing.plan_free_features,
      limitations: t.pricing.plan_free_limitations,
      cta: t.pricing.cta_current_plan,
      ctaStyle: "bg-bg-elevated text-text-secondary cursor-default",
      highlighted: false,
    },
    {
      name: t.pricing.plan_researcher,
      price: "$19",
      period: t.pricing.per_month,
      description: t.pricing.plan_researcher_desc,
      icon: Users,
      color: "text-primary",
      borderColor: "border-primary",
      features: t.pricing.plan_researcher_features,
      limitations: [] as readonly string[],
      cta: t.pricing.cta_start_trial,
      ctaStyle: "bg-primary hover:bg-primary-dark text-white",
      highlighted: true,
    },
    {
      name: t.pricing.plan_lab,
      price: "$99",
      period: t.pricing.per_month,
      description: t.pricing.plan_lab_desc,
      icon: Building2,
      color: "text-secondary",
      borderColor: "border-secondary/50",
      features: t.pricing.plan_lab_features,
      limitations: [] as readonly string[],
      cta: t.pricing.cta_contact_sales,
      ctaStyle: "bg-secondary/20 hover:bg-secondary/30 border border-secondary/30 text-secondary",
      highlighted: false,
    },
  ];

  const FAQ = [
    { q: t.pricing.faq_1_q, a: t.pricing.faq_1_a },
    { q: t.pricing.faq_2_q, a: t.pricing.faq_2_a },
    { q: t.pricing.faq_3_q, a: t.pricing.faq_3_a },
    { q: t.pricing.faq_4_q, a: t.pricing.faq_4_a },
    { q: t.pricing.faq_5_q, a: t.pricing.faq_5_a },
  ];

  return (
    <div className="h-[calc(100vh-56px)] overflow-y-auto">
      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-text-primary mb-3">
            {t.pricing.page_title}
          </h1>
          <p className="text-text-secondary max-w-lg mx-auto">
            {t.pricing.page_description}
          </p>

          {/* Billing toggle */}
          <div className="flex items-center justify-center gap-3 mt-6">
            <button
              onClick={() => setBillingCycle("monthly")}
              className={`text-sm px-4 py-1.5 rounded-lg transition-all ${
                billingCycle === "monthly"
                  ? "bg-primary text-white"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              {t.pricing.monthly}
            </button>
            <button
              onClick={() => setBillingCycle("annual")}
              className={`text-sm px-4 py-1.5 rounded-lg transition-all ${
                billingCycle === "annual"
                  ? "bg-primary text-white"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              {t.pricing.annual}
              <span className="ml-1.5 text-xs text-success">{t.pricing.save_percent}</span>
            </button>
          </div>
        </div>

        {/* Pricing cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          {PRICING_PLANS.map((plan) => {
            const displayPrice =
              billingCycle === "annual" && plan.price !== "$0"
                ? `$${Math.round(parseInt(plan.price.slice(1)) * 0.8)}`
                : plan.price;

            return (
              <div
                key={plan.name}
                className={`relative card flex flex-col ${
                  plan.highlighted
                    ? "border-primary shadow-glow-primary ring-1 ring-primary/30"
                    : plan.borderColor
                }`}
              >
                {plan.highlighted && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-white text-xs px-3 py-1 rounded-full font-medium">
                    {t.pricing.most_popular}
                  </div>
                )}

                <div className="flex items-center gap-3 mb-4">
                  <div
                    className={`w-9 h-9 rounded-lg flex items-center justify-center ${
                      plan.highlighted
                        ? "bg-primary/20"
                        : "bg-bg-elevated"
                    }`}
                  >
                    <plan.icon className={`w-4.5 h-4.5 ${plan.color}`} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-text-primary">{plan.name}</h3>
                    <p className="text-xs text-text-muted">{plan.description}</p>
                  </div>
                </div>

                <div className="flex items-baseline gap-1 mb-6">
                  <span className="text-3xl font-bold text-text-primary">
                    {displayPrice}
                  </span>
                  <span className="text-text-muted text-sm">
                    {plan.period}
                    {billingCycle === "annual" && plan.price !== "$0" && (
                      <span className="ml-1 text-text-muted line-through text-xs">
                        {plan.price}
                      </span>
                    )}
                  </span>
                </div>

                <ul className="space-y-2.5 mb-6 flex-1">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-text-secondary">
                      <CheckCircle className="w-4 h-4 text-success flex-shrink-0 mt-0.5" />
                      {f}
                    </li>
                  ))}
                  {plan.limitations.map((l) => (
                    <li key={l} className="flex items-start gap-2 text-sm text-text-muted">
                      <span className="w-4 h-4 flex items-center justify-center flex-shrink-0 mt-0.5 text-text-muted">
                        &mdash;
                      </span>
                      {l}
                    </li>
                  ))}
                </ul>

                <Link
                  href={plan.name === t.pricing.plan_lab ? "#" : "/login"}
                  className={`w-full text-center py-2.5 px-4 rounded-lg font-medium text-sm transition-all flex items-center justify-center gap-2 ${plan.ctaStyle}`}
                >
                  {plan.cta}
                  {plan.name !== t.pricing.plan_free && <ArrowRight className="w-3.5 h-3.5" />}
                </Link>
              </div>
            );
          })}
        </div>

        {/* FAQ */}
        <div className="max-w-2xl mx-auto">
          <h2 className="text-xl font-bold text-text-primary text-center mb-8">
            {t.pricing.faq_title}
          </h2>
          <div className="space-y-3">
            {FAQ.map((item, i) => (
              <div key={i} className="card border-border">
                <button
                  onClick={() => setExpandedFaq(expandedFaq === i ? null : i)}
                  className="w-full flex items-center justify-between text-left"
                >
                  <span className="text-sm font-medium text-text-primary">{item.q}</span>
                  <HelpCircle
                    className={`w-4 h-4 text-text-muted flex-shrink-0 ml-3 transition-transform ${
                      expandedFaq === i ? "rotate-45" : ""
                    }`}
                  />
                </button>
                {expandedFaq === i && (
                  <p className="text-sm text-text-secondary mt-3 leading-relaxed animate-fade-in">
                    {item.a}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
