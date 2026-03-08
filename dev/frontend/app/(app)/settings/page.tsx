"use client";

import { useState } from "react";
import {
  Settings,
  User,
  Bell,
  Shield,
  Globe,
  Palette,
  Key,
  LogOut,
  Save,
  CheckCircle,
  CreditCard,
  Loader2,
} from "lucide-react";
import toast from "react-hot-toast";

type SettingsTab = "profile" | "notifications" | "security" | "preferences";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<SettingsTab>("profile");
  const [saving, setSaving] = useState(false);

  // Profile state
  const [displayName, setDisplayName] = useState("Demo Researcher");
  const [email, setEmail] = useState("demo@leanprove.ai");
  const [locale, setLocale] = useState("en");

  // Notification state
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [usageAlerts, setUsageAlerts] = useState(true);
  const [weeklyDigest, setWeeklyDigest] = useState(false);

  // Preferences state
  const [editorFontSize, setEditorFontSize] = useState(14);
  const [autoSave, setAutoSave] = useState(true);
  const [autoCompile, setAutoCompile] = useState(false);
  const [defaultProofStyle, setDefaultProofStyle] = useState<"tactic" | "term">("tactic");

  const handleSave = async () => {
    setSaving(true);
    await new Promise((r) => setTimeout(r, 800));
    setSaving(false);
    toast.success("Settings saved successfully");
  };

  const TABS: { key: SettingsTab; label: string; icon: React.ElementType }[] = [
    { key: "profile", label: "Profile", icon: User },
    { key: "notifications", label: "Notifications", icon: Bell },
    { key: "security", label: "Security", icon: Shield },
    { key: "preferences", label: "Preferences", icon: Palette },
  ];

  return (
    <div className="h-[calc(100vh-56px)] overflow-y-auto">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <Settings className="w-5 h-5 text-primary" />
          <h1 className="text-xl font-bold text-text-primary">Settings</h1>
        </div>

        <div className="flex gap-6">
          {/* Sidebar tabs */}
          <div className="w-48 flex-shrink-0">
            <div className="space-y-1">
              {TABS.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-all ${
                    activeTab === tab.key
                      ? "bg-primary/20 text-primary font-medium"
                      : "text-text-secondary hover:text-text-primary hover:bg-bg-elevated"
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}

              <div className="border-t border-border my-3" />

              <button className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-error hover:bg-error/10 transition-all">
                <LogOut className="w-4 h-4" />
                Sign out
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Profile */}
            {activeTab === "profile" && (
              <div className="space-y-6">
                <div className="card border-border">
                  <h2 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
                    <User className="w-4 h-4 text-primary" />
                    Profile Information
                  </h2>

                  <div className="space-y-4">
                    {/* Avatar */}
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xl font-bold">
                        DR
                      </div>
                      <div>
                        <button className="text-xs text-primary hover:text-primary-light transition-colors">
                          Change avatar
                        </button>
                        <p className="text-xs text-text-muted mt-0.5">JPG, PNG. Max 2MB.</p>
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-text-secondary mb-1.5">
                        Display name
                      </label>
                      <input
                        type="text"
                        value={displayName}
                        onChange={(e) => setDisplayName(e.target.value)}
                        className="w-full bg-bg-dark border border-border rounded-lg px-3 py-2.5 text-sm text-text-primary outline-none focus:border-primary transition-colors"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-text-secondary mb-1.5">
                        Email
                      </label>
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full bg-bg-dark border border-border rounded-lg px-3 py-2.5 text-sm text-text-primary outline-none focus:border-primary transition-colors"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-text-secondary mb-1.5 flex items-center gap-1.5">
                        <Globe className="w-3.5 h-3.5" />
                        Language
                      </label>
                      <select
                        value={locale}
                        onChange={(e) => setLocale(e.target.value)}
                        className="w-full bg-bg-dark border border-border rounded-lg px-3 py-2.5 text-sm text-text-primary outline-none focus:border-primary transition-colors"
                      >
                        <option value="en">English</option>
                        <option value="zh">Chinese</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Subscription */}
                <div className="card border-border">
                  <h2 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
                    <CreditCard className="w-4 h-4 text-primary" />
                    Subscription
                  </h2>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-text-primary">Researcher Plan</p>
                      <p className="text-xs text-text-muted">$19/month - Renews Apr 1, 2026</p>
                    </div>
                    <button className="text-xs text-primary hover:text-primary-light transition-colors px-3 py-1.5 border border-primary/30 rounded-lg">
                      Manage Subscription
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Notifications */}
            {activeTab === "notifications" && (
              <div className="card border-border space-y-5">
                <h2 className="text-sm font-semibold text-text-primary flex items-center gap-2">
                  <Bell className="w-4 h-4 text-primary" />
                  Notification Preferences
                </h2>

                {[
                  {
                    label: "Email notifications",
                    description: "Receive emails about compilation results and proof updates",
                    checked: emailNotifications,
                    onChange: setEmailNotifications,
                  },
                  {
                    label: "Usage alerts",
                    description: "Get notified when approaching plan limits",
                    checked: usageAlerts,
                    onChange: setUsageAlerts,
                  },
                  {
                    label: "Weekly digest",
                    description: "Receive a weekly summary of your proof activity",
                    checked: weeklyDigest,
                    onChange: setWeeklyDigest,
                  },
                ].map((item) => (
                  <div key={item.label} className="flex items-start justify-between py-2">
                    <div>
                      <p className="text-sm text-text-primary font-medium">{item.label}</p>
                      <p className="text-xs text-text-muted mt-0.5">{item.description}</p>
                    </div>
                    <button
                      onClick={() => item.onChange(!item.checked)}
                      className={`relative w-10 h-5 rounded-full transition-colors flex-shrink-0 ${
                        item.checked ? "bg-primary" : "bg-bg-elevated"
                      }`}
                    >
                      <div
                        className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${
                          item.checked ? "left-5.5 translate-x-0" : "left-0.5"
                        }`}
                        style={{ left: item.checked ? "22px" : "2px" }}
                      />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Security */}
            {activeTab === "security" && (
              <div className="space-y-6">
                <div className="card border-border">
                  <h2 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
                    <Key className="w-4 h-4 text-primary" />
                    Change Password
                  </h2>
                  <div className="space-y-4 max-w-md">
                    <div>
                      <label className="block text-xs font-medium text-text-secondary mb-1.5">
                        Current password
                      </label>
                      <input
                        type="password"
                        placeholder="Enter current password"
                        className="w-full bg-bg-dark border border-border rounded-lg px-3 py-2.5 text-sm text-text-primary placeholder-text-muted outline-none focus:border-primary transition-colors"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-text-secondary mb-1.5">
                        New password
                      </label>
                      <input
                        type="password"
                        placeholder="At least 8 characters"
                        className="w-full bg-bg-dark border border-border rounded-lg px-3 py-2.5 text-sm text-text-primary placeholder-text-muted outline-none focus:border-primary transition-colors"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-text-secondary mb-1.5">
                        Confirm new password
                      </label>
                      <input
                        type="password"
                        placeholder="Repeat new password"
                        className="w-full bg-bg-dark border border-border rounded-lg px-3 py-2.5 text-sm text-text-primary placeholder-text-muted outline-none focus:border-primary transition-colors"
                      />
                    </div>
                    <button className="text-sm bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded-lg transition-colors">
                      Update Password
                    </button>
                  </div>
                </div>

                <div className="card border-border">
                  <h2 className="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
                    <Shield className="w-4 h-4 text-primary" />
                    Connected Accounts
                  </h2>
                  <div className="flex items-center justify-between py-2">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-bg-elevated flex items-center justify-center">
                        <svg className="w-4 h-4 text-text-primary" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                        </svg>
                      </div>
                      <div>
                        <p className="text-sm text-text-primary font-medium">GitHub</p>
                        <p className="text-xs text-text-muted">Not connected</p>
                      </div>
                    </div>
                    <button className="text-xs text-primary hover:text-primary-light border border-primary/30 px-3 py-1.5 rounded-lg transition-colors">
                      Connect
                    </button>
                  </div>
                </div>

                <div className="card border-error/20">
                  <h2 className="text-sm font-semibold text-error mb-2">Danger Zone</h2>
                  <p className="text-xs text-text-muted mb-3">
                    Permanently delete your account and all associated data. This action cannot be undone.
                  </p>
                  <button className="text-xs bg-error/10 hover:bg-error/20 border border-error/30 text-error px-3 py-1.5 rounded-lg transition-colors">
                    Delete Account
                  </button>
                </div>
              </div>
            )}

            {/* Preferences */}
            {activeTab === "preferences" && (
              <div className="card border-border space-y-5">
                <h2 className="text-sm font-semibold text-text-primary flex items-center gap-2">
                  <Palette className="w-4 h-4 text-primary" />
                  Editor Preferences
                </h2>

                <div>
                  <label className="block text-xs font-medium text-text-secondary mb-1.5">
                    Font size (px)
                  </label>
                  <div className="flex items-center gap-3">
                    <input
                      type="range"
                      min={10}
                      max={20}
                      value={editorFontSize}
                      onChange={(e) => setEditorFontSize(Number(e.target.value))}
                      className="flex-1 accent-primary"
                    />
                    <span className="text-sm font-mono text-text-primary w-8 text-center">
                      {editorFontSize}
                    </span>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-text-secondary mb-1.5">
                    Default proof style
                  </label>
                  <div className="flex gap-3">
                    {(["tactic", "term"] as const).map((style) => (
                      <button
                        key={style}
                        onClick={() => setDefaultProofStyle(style)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-all ${
                          defaultProofStyle === style
                            ? "bg-primary text-white"
                            : "bg-bg-elevated text-text-secondary hover:text-text-primary"
                        }`}
                      >
                        {style} mode
                      </button>
                    ))}
                  </div>
                </div>

                {[
                  {
                    label: "Auto-save",
                    description: "Automatically save editor content every 3 seconds",
                    checked: autoSave,
                    onChange: setAutoSave,
                  },
                  {
                    label: "Auto-compile",
                    description: "Automatically compile when code changes (uses compilation quota)",
                    checked: autoCompile,
                    onChange: setAutoCompile,
                  },
                ].map((item) => (
                  <div key={item.label} className="flex items-start justify-between py-2">
                    <div>
                      <p className="text-sm text-text-primary font-medium">{item.label}</p>
                      <p className="text-xs text-text-muted mt-0.5">{item.description}</p>
                    </div>
                    <button
                      onClick={() => item.onChange(!item.checked)}
                      className={`relative w-10 h-5 rounded-full transition-colors flex-shrink-0 ${
                        item.checked ? "bg-primary" : "bg-bg-elevated"
                      }`}
                    >
                      <div
                        className="absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform"
                        style={{ left: item.checked ? "22px" : "2px" }}
                      />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Save button */}
            <div className="flex justify-end mt-6">
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex items-center gap-2 bg-primary hover:bg-primary-dark disabled:opacity-50 text-white px-5 py-2.5 rounded-xl text-sm font-medium transition-all"
              >
                {saving ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                {saving ? "Saving..." : "Save Changes"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
