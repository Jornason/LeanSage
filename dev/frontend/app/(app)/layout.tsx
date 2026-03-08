"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Search,
  Code2,
  AlertTriangle,
  ArrowRightLeft,
  LayoutDashboard,
  Settings,
  CreditCard,
  LogOut,
  ChevronDown,
  Bell,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/search", label: "Semantic Search", icon: Search },
  { href: "/workspace", label: "Proof Workspace", icon: Code2 },
  { href: "/diagnose", label: "Error Diagnosis", icon: AlertTriangle },
  { href: "/convert", label: "LaTeX Converter", icon: ArrowRightLeft },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/pricing", label: "Pricing", icon: CreditCard },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-bg-dark flex flex-col">
      {/* Top navigation */}
      <header className="h-14 border-b border-border bg-bg-surface/80 backdrop-blur-md sticky top-0 z-50 flex items-center px-4 gap-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 flex-shrink-0">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <span className="text-white text-xs font-bold">LP</span>
          </div>
          <span className="font-semibold text-text-primary text-sm hidden md:block">
            LeanProve AI
          </span>
        </Link>

        {/* Nav items */}
        <nav className="flex items-center gap-1 flex-1 overflow-x-auto">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-150 ${
                  active
                    ? "bg-primary/20 text-primary border border-primary/30"
                    : "text-text-secondary hover:text-text-primary hover:bg-bg-elevated"
                }`}
              >
                <item.icon className="w-3.5 h-3.5" />
                <span className="hidden lg:block">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Right side */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Usage indicator */}
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-bg-dark rounded-lg border border-border text-xs text-text-secondary">
            <div className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
            <span>47 searches</span>
          </div>

          {/* Notification */}
          <button className="p-2 text-text-secondary hover:text-text-primary hover:bg-bg-elevated rounded-lg transition-colors">
            <Bell className="w-4 h-4" />
          </button>

          {/* User menu */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-bg-elevated hover:bg-border rounded-lg cursor-pointer transition-colors group">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xs font-bold">
              R
            </div>
            <span className="text-xs text-text-secondary hidden md:block group-hover:text-text-primary transition-colors">
              Researcher
            </span>
            <ChevronDown className="w-3 h-3 text-text-muted hidden md:block" />
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 overflow-hidden">{children}</main>
    </div>
  );
}
