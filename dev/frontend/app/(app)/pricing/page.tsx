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

const PRICING_PLANS = [
  {
    name: "Free",
    price: "$0",
    period: "/month",
    description: "Get started with Lean 4",
    icon: Zap,
    color: "text-text-secondary",
    borderColor: "border-border",
    features: [
      "10 searches/month",
      "5 proof generations/month",
      "10 AI diagnoses/month",
      "Basic LaTeX converter",
      "Community support",
    ],
    limitations: [
      "No real-time compilation",
      "No proof collaboration",
    ],
    cta: "Current Plan",
    ctaStyle: "bg-bg-elevated text-text-secondary cursor-default",
    highlighted: false,
  },
  {
    name: "Researcher",
    price: "$19",
    period: "/month",
    description: "For active researchers",
    icon: Users,
    color: "text-primary",
    borderColor: "border-primary",
    features: [
      "Unlimited searches",
      "50 proof generations/month",
      "Unlimited diagnostics",
      "Real-time Lean compiler",
      "Priority support",
      "Search history export",
      "Advanced LaTeX converter",
    ],
    limitations: [],
    cta: "Start Free Trial",
    ctaStyle: "bg-primary hover:bg-primary-dark text-white",
    highlighted: true,
  },
  {
    name: "Lab",
    price: "$99",
    period: "/month",
    description: "For research groups",
    icon: Building2,
    color: "text-secondary",
    borderColor: "border-secondary/50",
    features: [
      "Everything in Researcher",
      "10 team seats included",
      "Proof collaboration",
      "Usage analytics dashboard",
      "SSO integration",
      "Dedicated support",
      "Custom Mathlib indexing",
    ],
    limitations: [],
    cta: "Contact Sales",
    ctaStyle: "bg-secondary/20 hover:bg-secondary/30 border border-secondary/30 text-secondary",
    highlighted: false,
  },
];

const FAQ = [
  {
    q: "Can I switch plans at any time?",
    a: "Yes, you can upgrade or downgrade at any time. Changes take effect at the start of your next billing cycle.",
  },
  {
    q: "Do you offer academic discounts?",
    a: "Yes! We offer 50% off the Researcher plan for verified students and academics. Contact us with your .edu email.",
  },
  {
    q: "What happens when I exceed my usage limit?",
    a: "On the Free plan, you'll be prompted to upgrade. We never charge overage fees without your consent.",
  },
  {
    q: "Can I try the Researcher plan before committing?",
    a: "Absolutely. We offer a 14-day free trial of the Researcher plan with no credit card required.",
  },
  {
    q: "How does the Lab plan team seating work?",
    a: "The Lab plan includes 10 seats. Additional seats can be added at $9/seat/month. Each member gets full Researcher-level access.",
  },
];

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">("monthly");
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  return (
    <div className="h-[calc(100vh-56px)] overflow-y-auto">
      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-text-primary mb-3">
            Simple, transparent pricing
          </h1>
          <p className="text-text-secondary max-w-lg mx-auto">
            Start free, scale as your research grows. All plans include access
            to Mathlib semantic search and AI-powered proof tools.
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
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle("annual")}
              className={`text-sm px-4 py-1.5 rounded-lg transition-all ${
                billingCycle === "annual"
                  ? "bg-primary text-white"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              Annual
              <span className="ml-1.5 text-xs text-success">Save 20%</span>
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
                    Most Popular
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
                  href={plan.name === "Lab" ? "#" : "/login"}
                  className={`w-full text-center py-2.5 px-4 rounded-lg font-medium text-sm transition-all flex items-center justify-center gap-2 ${plan.ctaStyle}`}
                >
                  {plan.cta}
                  {plan.name !== "Free" && <ArrowRight className="w-3.5 h-3.5" />}
                </Link>
              </div>
            );
          })}
        </div>

        {/* FAQ */}
        <div className="max-w-2xl mx-auto">
          <h2 className="text-xl font-bold text-text-primary text-center mb-8">
            Frequently Asked Questions
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
