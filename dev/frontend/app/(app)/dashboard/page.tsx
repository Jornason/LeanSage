"use client";

import { useState } from "react";
import {
  Search,
  Code2,
  AlertTriangle,
  ArrowRightLeft,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  LayoutDashboard,
  Plus,
  ChevronRight,
  Zap,
  ArrowUpRight,
} from "lucide-react";
import Link from "next/link";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useTranslation } from "@/lib/i18n/useTranslation";

const USAGE_DATA = [
  { day: "Mon", searches: 8, generations: 2, diagnoses: 1 },
  { day: "Tue", searches: 12, generations: 3, diagnoses: 2 },
  { day: "Wed", searches: 5, generations: 1, diagnoses: 0 },
  { day: "Thu", searches: 9, generations: 2, diagnoses: 3 },
  { day: "Fri", searches: 7, generations: 2, diagnoses: 1 },
  { day: "Sat", searches: 3, generations: 1, diagnoses: 0 },
  { day: "Sun", searches: 3, generations: 1, diagnoses: 1 },
];

const PROOF_SESSIONS = [
  {
    id: "1",
    title: "Continuity of Sum",
    status: "success",
    lastEdited: "2 hours ago",
    description: "Prove sum of continuous functions is continuous",
  },
  {
    id: "2",
    title: "Cauchy Sequences",
    status: "error",
    lastEdited: "1 day ago",
    description: "Cauchy sequence convergence in complete metric spaces",
  },
  {
    id: "3",
    title: "IVT Proof",
    status: "success",
    lastEdited: "2 days ago",
    description: "Intermediate Value Theorem formalization",
  },
  {
    id: "4",
    title: "Group Homomorphisms",
    status: "pending",
    lastEdited: "3 days ago",
    description: "Properties of group homomorphisms",
  },
  {
    id: "5",
    title: "Zorn's Lemma",
    status: "success",
    lastEdited: "5 days ago",
    description: "Zorn's lemma and its applications",
  },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-bg-surface border border-border rounded-lg px-3 py-2 text-xs">
        <p className="font-medium text-text-primary mb-1">{label}</p>
        {payload.map((p: any) => (
          <p key={p.name} style={{ color: p.color }}>
            {p.name}: {p.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function DashboardPage() {
  const { t } = useTranslation();
  const [sessionFilter, setSessionFilter] = useState("");

  const STATS = [
    {
      label: t.dashboard.searches,
      value: 47,
      limit: t.common.unlimited,
      icon: Search,
      color: "text-blue-400",
      bg: "bg-blue-500/10",
      border: "border-blue-500/20",
      trend: "+12 " + t.dashboard.this_week,
      trendUp: true,
    },
    {
      label: t.dashboard.generations,
      value: 12,
      limit: t.common.unlimited,
      icon: Code2,
      color: "text-violet-400",
      bg: "bg-violet-500/10",
      border: "border-violet-500/20",
      trend: "+5 " + t.dashboard.this_week,
      trendUp: true,
    },
    {
      label: t.dashboard.diagnoses,
      value: 8,
      limit: t.common.unlimited,
      icon: AlertTriangle,
      color: "text-amber-400",
      bg: "bg-amber-500/10",
      border: "border-amber-500/20",
      trend: "+2 " + t.dashboard.this_week,
      trendUp: true,
    },
    {
      label: t.dashboard.compilations,
      value: 23,
      limit: t.common.unlimited,
      icon: Code2,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
      trend: "+8 " + t.dashboard.this_week,
      trendUp: true,
    },
  ];

  const STATUS_CONFIG = {
    success: {
      icon: <CheckCircle className="w-3.5 h-3.5" />,
      label: t.dashboard.compiled,
      class: "text-success bg-success/10 border-success/20",
    },
    error: {
      icon: <XCircle className="w-3.5 h-3.5" />,
      label: t.dashboard.error_status,
      class: "text-error bg-error/10 border-error/20",
    },
    pending: {
      icon: <Clock className="w-3.5 h-3.5" />,
      label: t.dashboard.pending,
      class: "text-text-muted bg-bg-elevated border-border",
    },
  };

  const filteredSessions = PROOF_SESSIONS.filter(
    (s) =>
      s.title.toLowerCase().includes(sessionFilter.toLowerCase()) ||
      s.description.toLowerCase().includes(sessionFilter.toLowerCase())
  );

  return (
    <div className="h-[calc(100vh-56px)] overflow-y-auto">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-text-primary flex items-center gap-2">
              <LayoutDashboard className="w-5 h-5 text-primary" />
              {t.dashboard.page_title}
            </h1>
            <p className="text-sm text-text-secondary mt-0.5">
              {t.dashboard.welcome}
            </p>
          </div>
          <Link
            href="/workspace"
            className="btn-primary text-sm"
          >
            <Plus className="w-4 h-4" />
            {t.dashboard.new_proof_session}
          </Link>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {STATS.map((stat) => (
            <div key={stat.label} className={`card border ${stat.border}`}>
              <div className="flex items-start justify-between mb-3">
                <div className={`w-9 h-9 ${stat.bg} rounded-lg flex items-center justify-center`}>
                  <stat.icon className={`w-4.5 h-4.5 ${stat.color}`} />
                </div>
                <div className={`flex items-center gap-1 text-xs ${stat.trendUp ? "text-success" : "text-error"}`}>
                  <ArrowUpRight className="w-3 h-3" />
                  {stat.trend}
                </div>
              </div>
              <div className="text-2xl font-bold text-text-primary mb-0.5">{stat.value}</div>
              <div className="text-xs text-text-muted">{stat.label} {t.dashboard.this_month}</div>
              <div className="text-xs text-primary mt-1">{t.dashboard.limit}: {stat.limit}</div>
            </div>
          ))}
        </div>

        {/* Main content grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Proof sessions */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-text-primary">{t.dashboard.proof_sessions}</h2>
              <input
                type="text"
                value={sessionFilter}
                onChange={(e) => setSessionFilter(e.target.value)}
                placeholder={t.dashboard.filter_sessions}
                className="bg-bg-surface border border-border rounded-lg px-3 py-1.5 text-xs text-text-primary placeholder-text-muted outline-none focus:border-primary transition-colors w-48"
              />
            </div>

            <div className="space-y-2">
              {filteredSessions.map((session) => {
                const statusCfg = STATUS_CONFIG[session.status as keyof typeof STATUS_CONFIG];
                return (
                  <Link
                    key={session.id}
                    href={`/workspace?session=${session.id}`}
                    className="flex items-center gap-4 card border-border hover:border-border/60 transition-all group"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-text-primary group-hover:text-primary transition-colors truncate">
                          {session.title}
                        </span>
                        <span
                          className={`flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border flex-shrink-0 ${statusCfg.class}`}
                        >
                          {statusCfg.icon}
                          {statusCfg.label}
                        </span>
                      </div>
                      <p className="text-xs text-text-muted truncate">{session.description}</p>
                    </div>
                    <div className="text-xs text-text-muted flex-shrink-0">
                      {session.lastEdited}
                    </div>
                    <ChevronRight className="w-4 h-4 text-text-muted group-hover:text-primary transition-colors flex-shrink-0" />
                  </Link>
                );
              })}
            </div>

            {filteredSessions.length === 0 && (
              <div className="text-center py-8 text-text-muted text-sm">
                {t.dashboard.no_sessions_match}
              </div>
            )}
          </div>

          {/* Right sidebar */}
          <div className="space-y-4">
            {/* Plan card */}
            <div className="card border-primary/30 bg-gradient-card">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-xs text-text-muted mb-0.5">{t.dashboard.current_plan}</p>
                  <h3 className="text-base font-bold text-text-primary">{t.pricing.plan_researcher}</h3>
                </div>
                <div className="flex items-center gap-1 text-xs text-primary font-medium bg-primary/10 px-2.5 py-1 rounded-full border border-primary/20">
                  <Zap className="w-3 h-3" />
                  {t.dashboard.active}
                </div>
              </div>
              <div className="text-2xl font-bold text-text-primary mb-1">$19</div>
              <div className="text-xs text-text-muted mb-4">{t.dashboard.per_month} • {t.dashboard.renews} Apr 1, 2026</div>
              <Link
                href="/#pricing"
                className="block w-full text-center py-2 bg-primary/20 hover:bg-primary/30 border border-primary/30 text-primary text-xs font-medium rounded-lg transition-all"
              >
                {t.dashboard.upgrade_to_lab}
              </Link>
            </div>

            {/* Usage chart */}
            <div className="card border-border">
              <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-4 flex items-center gap-2">
                <TrendingUp className="w-3.5 h-3.5" />
                {t.dashboard.weekly_usage}
              </h3>
              <div className="h-40">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={USAGE_DATA}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                      dataKey="day"
                      tick={{ fontSize: 10, fill: "#94A3B8" }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 10, fill: "#94A3B8" }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Line
                      type="monotone"
                      dataKey="searches"
                      stroke="#6366F1"
                      strokeWidth={2}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="generations"
                      stroke="#8B5CF6"
                      strokeWidth={2}
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="diagnoses"
                      stroke="#F59E0B"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="flex gap-3 mt-2">
                {[
                  { color: "#6366F1", label: t.dashboard.search_legend },
                  { color: "#8B5CF6", label: t.dashboard.generate_legend },
                  { color: "#F59E0B", label: t.dashboard.diagnose_legend },
                ].map((l) => (
                  <div key={l.label} className="flex items-center gap-1.5">
                    <div
                      className="w-2.5 h-2.5 rounded-full"
                      style={{ background: l.color }}
                    />
                    <span className="text-xs text-text-muted">{l.label}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick actions */}
            <div className="card border-border">
              <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">
                {t.dashboard.quick_actions}
              </h3>
              <div className="space-y-2">
                {[
                  { href: "/search", label: t.dashboard.search_mathlib, icon: Search },
                  { href: "/workspace", label: t.dashboard.new_proof, icon: Code2 },
                  { href: "/diagnose", label: t.dashboard.diagnose_code, icon: AlertTriangle },
                  { href: "/convert", label: t.dashboard.convert_latex, icon: ArrowRightLeft },
                ].map((action) => (
                  <Link
                    key={action.href}
                    href={action.href}
                    className="flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-bg-elevated text-text-secondary hover:text-text-primary transition-all group text-sm"
                  >
                    <action.icon className="w-3.5 h-3.5 text-text-muted group-hover:text-primary transition-colors" />
                    {action.label}
                    <ChevronRight className="w-3.5 h-3.5 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
