"use client";

import { useState } from "react";
import Link from "next/link";
import { Github, Mail, Eye, EyeOff, ArrowRight } from "lucide-react";
import { useTranslation } from "@/lib/i18n/useTranslation";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8005/v1";

export default function LoginPage() {
  const { t } = useTranslation();
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const endpoint = isLogin ? "/auth/login" : "/auth/register";
      const body = isLogin
        ? { email, password }
        : { email, password, display_name: name };
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const json = await res.json();
      if (!json.success) throw new Error(json.error ?? "Authentication failed");
      localStorage.setItem("access_token", json.data.access_token);
      window.location.href = "/search";
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleGithubLogin = () => {
    window.location.href = "/api/auth/github";
  };

  return (
    <div className="min-h-screen bg-bg-dark flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 bg-gradient-to-br from-bg-dark via-bg-surface to-bg-dark p-12 border-r border-border relative overflow-hidden">
        {/* Background math symbols */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-20 left-12 text-primary/5 text-9xl font-mono">∀</div>
          <div className="absolute top-48 right-16 text-secondary/5 text-8xl font-mono">∃</div>
          <div className="absolute bottom-32 left-20 text-primary/5 text-7xl font-mono">⊢</div>
          <div className="absolute bottom-16 right-12 text-secondary/5 text-8xl font-mono">λ</div>
        </div>

        <div className="relative">
          <div className="flex items-center gap-3 mb-16">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-glow-primary">
              <span className="text-white text-sm font-bold">LP</span>
            </div>
            <span className="font-bold text-xl text-text-primary">{t.common.app_name}</span>
          </div>

          <h1 className="text-4xl font-bold text-text-primary leading-tight mb-6">
            {t.login.branding_title_1}<br />
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              {t.login.branding_title_2}
            </span>{" "}
            {t.login.branding_title_3}
          </h1>
          <p className="text-text-secondary text-lg leading-relaxed max-w-md">
            {t.login.branding_description}
          </p>
        </div>

        <div className="relative space-y-4">
          {[
            { icon: "🔍", text: t.login.branding_stat_1 },
            { icon: "⚡", text: t.login.branding_stat_2 },
            { icon: "🎯", text: t.login.branding_stat_3 },
          ].map((item) => (
            <div key={item.text} className="flex items-center gap-3 text-text-secondary text-sm">
              <span className="text-lg">{item.icon}</span>
              {item.text}
            </div>
          ))}
        </div>
      </div>

      {/* Right side - Auth form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <span className="text-white text-xs font-bold">LP</span>
            </div>
            <span className="font-bold text-text-primary">{t.common.app_name}</span>
          </div>

          <h2 className="text-2xl font-bold text-text-primary mb-2">
            {isLogin ? t.login.welcome_back : t.login.create_account}
          </h2>
          <p className="text-text-secondary text-sm mb-8">
            {isLogin ? t.login.sign_in_subtitle : t.login.sign_up_subtitle}
          </p>

          {/* GitHub OAuth */}
          <button
            onClick={handleGithubLogin}
            className="w-full flex items-center justify-center gap-3 bg-bg-surface hover:bg-bg-elevated border border-border text-text-primary py-3 px-4 rounded-xl text-sm font-medium transition-all duration-150 mb-6"
          >
            <Github className="w-5 h-5" />
            {t.login.continue_github}
          </button>

          <div className="flex items-center gap-3 mb-6">
            <div className="flex-1 h-px bg-border" />
            <span className="text-text-muted text-xs">{t.login.or_continue_email}</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          {error && (
            <div className="bg-error/10 border border-error/30 text-error text-sm rounded-xl px-4 py-3 mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1.5">
                  {t.login.full_name}
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={t.login.full_name_placeholder}
                  required={!isLogin}
                  className="w-full bg-bg-surface border border-border rounded-xl px-4 py-3 text-text-primary placeholder-text-muted text-sm outline-none focus:border-primary transition-colors"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1.5">
                {t.login.email_address}
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t.login.email_placeholder}
                  required
                  className="w-full bg-bg-surface border border-border rounded-xl pl-10 pr-4 py-3 text-text-primary placeholder-text-muted text-sm outline-none focus:border-primary transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1.5">
                {t.login.password}
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={t.login.password_placeholder}
                  required
                  minLength={8}
                  className="w-full bg-bg-surface border border-border rounded-xl px-4 py-3 pr-11 text-text-primary placeholder-text-muted text-sm outline-none focus:border-primary transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {isLogin && (
              <div className="text-right">
                <Link href="#" className="text-xs text-primary hover:text-primary-light transition-colors">
                  {t.login.forgot_password}
                </Link>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary hover:bg-primary-dark disabled:opacity-60 disabled:cursor-not-allowed text-white py-3 px-4 rounded-xl font-medium text-sm transition-all duration-150 flex items-center justify-center gap-2"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  {isLogin ? t.login.sign_in_btn : t.login.create_account_btn}
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-text-muted mt-6">
            {isLogin ? t.login.no_account : t.login.have_account}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-primary hover:text-primary-light transition-colors font-medium"
            >
              {isLogin ? t.login.sign_up_free : t.common.sign_in}
            </button>
          </p>

          <p className="text-center text-xs text-text-muted mt-4">
            {t.login.terms_prefix}
            <Link href="#" className="text-primary hover:underline">{t.login.terms}</Link>
            {t.login.and}
            <Link href="#" className="text-primary hover:underline">{t.login.privacy_policy}</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
