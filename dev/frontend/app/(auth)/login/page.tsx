"use client";

import { useState } from "react";
import Link from "next/link";
import { Github, Mail, Eye, EyeOff, ArrowRight } from "lucide-react";

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Simulate API call
    await new Promise((r) => setTimeout(r, 1000));
    setLoading(false);
    // Redirect to dashboard
    window.location.href = "/dashboard";
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
            <span className="font-bold text-xl text-text-primary">LeanProve AI</span>
          </div>

          <h1 className="text-4xl font-bold text-text-primary leading-tight mb-6">
            AI-Powered<br />
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              Lean 4
            </span>{" "}
            Assistant
          </h1>
          <p className="text-text-secondary text-lg leading-relaxed max-w-md">
            Search Mathlib semantically, generate proof drafts, diagnose errors,
            and convert between LaTeX and Lean 4.
          </p>
        </div>

        <div className="relative space-y-4">
          {[
            { icon: "🔍", text: "200k+ Mathlib theorems indexed" },
            { icon: "⚡", text: "AI proof generation in seconds" },
            { icon: "🎯", text: "70%+ error diagnosis accuracy" },
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
            <span className="font-bold text-text-primary">LeanProve AI</span>
          </div>

          <h2 className="text-2xl font-bold text-text-primary mb-2">
            {isLogin ? "Welcome back" : "Create your account"}
          </h2>
          <p className="text-text-secondary text-sm mb-8">
            {isLogin
              ? "Sign in to your LeanProve AI account"
              : "Start your Lean 4 research journey today"}
          </p>

          {/* GitHub OAuth */}
          <button
            onClick={handleGithubLogin}
            className="w-full flex items-center justify-center gap-3 bg-bg-surface hover:bg-bg-elevated border border-border text-text-primary py-3 px-4 rounded-xl text-sm font-medium transition-all duration-150 mb-6"
          >
            <Github className="w-5 h-5" />
            Continue with GitHub
          </button>

          <div className="flex items-center gap-3 mb-6">
            <div className="flex-1 h-px bg-border" />
            <span className="text-text-muted text-xs">or continue with email</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1.5">
                  Full name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Dr. Jane Smith"
                  required={!isLogin}
                  className="w-full bg-bg-surface border border-border rounded-xl px-4 py-3 text-text-primary placeholder-text-muted text-sm outline-none focus:border-primary transition-colors"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1.5">
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="researcher@university.edu"
                  required
                  className="w-full bg-bg-surface border border-border rounded-xl pl-10 pr-4 py-3 text-text-primary placeholder-text-muted text-sm outline-none focus:border-primary transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
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
                  Forgot password?
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
                  {isLogin ? "Sign in" : "Create account"}
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-text-muted mt-6">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-primary hover:text-primary-light transition-colors font-medium"
            >
              {isLogin ? "Sign up free" : "Sign in"}
            </button>
          </p>

          <p className="text-center text-xs text-text-muted mt-4">
            By continuing, you agree to our{" "}
            <Link href="#" className="text-primary hover:underline">Terms</Link>
            {" "}and{" "}
            <Link href="#" className="text-primary hover:underline">Privacy Policy</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
