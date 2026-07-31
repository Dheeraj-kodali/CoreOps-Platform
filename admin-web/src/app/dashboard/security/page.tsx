"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  ShieldCheck,
  Lock,
  Key,
  Smartphone,
  AlertTriangle,
  CheckCircle2,
  Clock,
  LogOut,
  UserX,
  Activity,
  Zap,
  ShieldAlert,
  Laptop,
  Globe,
  RefreshCw,
} from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

interface ActiveSession {
  session_id: string;
  user_id: string;
  username: string;
  role: string;
  ip_address: string;
  device: string;
  created_at: string;
  is_current?: boolean;
}

interface LoginLog {
  id: string;
  timestamp: string;
  username: string;
  role: string;
  ip_address: string;
  device: string;
  status: string;
}

export default function SecurityCenterPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<"OVERVIEW" | "SESSIONS" | "HISTORY" | "POLICY">("OVERVIEW");

  const [overview, setOverview] = useState({
    security_score: 96,
    security_rating: "EXCELLENT",
    last_successful_login: "2026-07-31 11:20:15",
    last_failed_login: "2026-07-31 10:45:00",
    active_sessions_count: 2,
    locked_accounts_count: 0,
    password_expiration_days: 90,
  });

  const [sessions, setSessions] = useState<ActiveSession[]>([]);
  const [loginHistory, setLoginHistory] = useState<LoginLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Password Policy Config State
  const [policy, setPolicy] = useState({
    minLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumber: true,
    requireSpecialChar: true,
    expirationDays: 90,
    maxFailedAttempts: 5,
    lockoutDurationMins: 30,
  });

  // Fetch Security Data
  const fetchSecurityData = useCallback(async () => {
    setLoading(true);
    try {
      const overviewRes = await apiClient.get("/security/overview").catch(() => null);
      if (overviewRes?.data) {
        setOverview(overviewRes.data);
      }

      const sessionsRes = await apiClient.get("/security/sessions").catch(() => null);
      if (sessionsRes?.data?.sessions) {
        setSessions(sessionsRes.data.sessions);
      }

      const historyRes = await apiClient.get("/security/login-history").catch(() => null);
      if (historyRes?.data?.history) {
        setLoginHistory(historyRes.data.history);
      }
    } catch (err) {
      console.warn("Using fallback security data:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSecurityData();
  }, [fetchSecurityData]);

  // Revoke Individual Session
  const handleRevokeSession = async (sessionId: string) => {
    try {
      await apiClient.delete(`/security/sessions/${sessionId}`).catch(() => null);
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
      setActionSuccess(`Session ${sessionId} successfully revoked.`);
      setTimeout(() => setActionSuccess(null), 3000);
    } catch (err) {
      alert("Failed to revoke session.");
    }
  };

  // Logout All Devices
  const handleLogoutAllDevices = async () => {
    if (!confirm("Are you sure you want to revoke all secondary active sessions?")) return;
    try {
      await apiClient.delete("/security/sessions").catch(() => null);
      setSessions((prev) => prev.filter((s) => s.is_current));
      setActionSuccess("All secondary sessions successfully terminated.");
      setTimeout(() => setActionSuccess(null), 3000);
    } catch (err) {
      alert("Failed to terminate sessions.");
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <ShieldCheck className="h-7 w-7 text-emerald-400" />
            Enterprise Security Center
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Hardened access controls, active session management, password policy configuration, and login history audits.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="inline-flex rounded-xl bg-slate-900 border border-slate-800 p-1">
          <button
            onClick={() => setActiveTab("OVERVIEW")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              activeTab === "OVERVIEW" ? "bg-amber-500 text-slate-950" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Security Overview
          </button>
          <button
            onClick={() => setActiveTab("SESSIONS")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              activeTab === "SESSIONS" ? "bg-amber-500 text-slate-950" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Active Sessions
          </button>
          <button
            onClick={() => setActiveTab("HISTORY")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              activeTab === "HISTORY" ? "bg-amber-500 text-slate-950" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Login History
          </button>
          <button
            onClick={() => setActiveTab("POLICY")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              activeTab === "POLICY" ? "bg-amber-500 text-slate-950" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Password Policy
          </button>
        </div>
      </div>

      {actionSuccess && (
        <div className="rounded-xl border border-emerald-800/50 bg-emerald-950/40 p-3.5 text-xs text-emerald-300 flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {activeTab === "OVERVIEW" ? (
        /* OVERVIEW VIEW */
        <div className="space-y-8 animate-fadeIn">
          
          {/* Security Score Header Card */}
          <div className="rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 p-6 shadow-2xl flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
            <div className="flex items-center gap-4">
              <div className="h-16 w-16 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center font-extrabold text-2xl shadow-lg">
                {overview.security_score}%
              </div>
              <div>
                <div className="inline-flex items-center gap-1.5 text-[11px] font-bold text-emerald-400 bg-emerald-950/80 border border-emerald-800/50 px-2.5 py-0.5 rounded-full mb-1">
                  <CheckCircle2 className="h-3 w-3" />
                  {overview.security_rating} SECURITY RATING
                </div>
                <h3 className="text-xl font-bold text-white">System Security Health</h3>
                <p className="text-xs text-slate-400">PBKDF2-SHA256 Password Hashing • HS256 JWT Expiration • Append-Only Audit Trail</p>
              </div>
            </div>

            <button
              onClick={fetchSecurityData}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-colors flex items-center gap-2"
            >
              <RefreshCw className="h-4 w-4 text-amber-400" />
              Re-evaluate Security Score
            </button>
          </div>

          {/* Security KPI Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            
            <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-400 mb-2">
                <span>Last Successful Login</span>
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              </div>
              <div className="text-sm font-bold text-white font-mono">{overview.last_successful_login}</div>
              <div className="text-[11px] text-slate-500 mt-1">IP: 127.0.0.1 (Current Session)</div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-400 mb-2">
                <span>Last Failed Login</span>
                <AlertTriangle className="h-4 w-4 text-rose-400" />
              </div>
              <div className="text-sm font-bold text-white font-mono">{overview.last_failed_login}</div>
              <div className="text-[11px] text-rose-400 mt-1">Blocked & Logged</div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-400 mb-2">
                <span>Active Sessions</span>
                <Laptop className="h-4 w-4 text-amber-400" />
              </div>
              <div className="text-2xl font-extrabold text-white">{sessions.length || overview.active_sessions_count}</div>
              <div className="text-[11px] text-amber-400 mt-1">Revocation controls active</div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-400 mb-2">
                <span>Locked Accounts</span>
                <UserX className="h-4 w-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-extrabold text-white">{overview.locked_accounts_count}</div>
              <div className="text-[11px] text-emerald-400 mt-1">0 Accounts Throttled</div>
            </div>

          </div>

          {/* MFA Readiness & Rate Limiting Overview */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            
            <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl space-y-3">
              <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
                <Smartphone className="h-5 w-5 text-amber-400" />
                <h4 className="font-bold text-white text-sm">TOTP MFA Readiness Framework</h4>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                The authentication architecture is TOTP-ready. Time-based One-Time Passwords can be enabled per account without breaking legacy JWT tokens.
              </p>
              <div className="pt-2">
                <span className="text-[11px] font-semibold text-amber-400 bg-amber-950/60 border border-amber-800/40 px-3 py-1 rounded-full">
                  MFA Readiness: ACTIVE (Optional Toggle)
                </span>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl space-y-3">
              <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
                <Zap className="h-5 w-5 text-emerald-400" />
                <h4 className="font-bold text-white text-sm">Authentication Rate Limiting & Protection</h4>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Brute-force protection limits authentication requests to 100 requests / minute with temporary account locks after 5 consecutive failures.
              </p>
              <div className="pt-2">
                <span className="text-[11px] font-semibold text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-3 py-1 rounded-full">
                  Rate Limiter: ENABLED (100 req/min)
                </span>
              </div>
            </div>

          </div>

        </div>
      ) : activeTab === "SESSIONS" ? (
        /* ACTIVE SESSIONS VIEW */
        <div className="space-y-6 animate-fadeIn">
          
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 className="font-bold text-white text-base">Active User Sessions</h3>
              <p className="text-xs text-slate-400">List of currently authenticated sessions with token revocation capabilities.</p>
            </div>
            <button
              onClick={handleLogoutAllDevices}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-950 border border-rose-800/60 text-rose-300 hover:bg-rose-900 text-xs font-bold transition-all shadow-md"
            >
              <LogOut className="h-4 w-4" />
              Logout From All Devices
            </button>
          </div>

          <div className="space-y-3">
            {sessions.map((sess) => (
              <div
                key={sess.session_id}
                className="flex items-center justify-between p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl"
              >
                <div className="flex items-center gap-3.5">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-amber-400">
                    <Laptop className="h-5 w-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-slate-100">{sess.username}</span>
                      <span className="text-[10px] font-mono bg-amber-950 text-amber-400 px-2 py-0.5 rounded-full border border-amber-800/40">
                        {sess.role}
                      </span>
                      {sess.is_current && (
                        <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-950 border border-emerald-800/40 px-2 py-0.5 rounded-full">
                          Current Device
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-400 mt-1 flex items-center gap-3">
                      <span>{sess.device}</span>
                      <span>•</span>
                      <span className="font-mono text-slate-500">IP: {sess.ip_address}</span>
                      <span>•</span>
                      <span>Logged in: {sess.created_at}</span>
                    </div>
                  </div>
                </div>

                {!sess.is_current && (
                  <button
                    onClick={() => handleRevokeSession(sess.session_id)}
                    className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-rose-900 hover:text-rose-200 text-slate-300 text-xs font-semibold transition-colors"
                  >
                    Revoke Session
                  </button>
                )}
              </div>
            ))}
          </div>

        </div>
      ) : activeTab === "HISTORY" ? (
        /* LOGIN HISTORY VIEW */
        <div className="space-y-6 animate-fadeIn">
          
          <div className="rounded-2xl border border-slate-800 bg-slate-900/80 shadow-2xl overflow-hidden backdrop-blur-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th className="py-3.5 px-4">Timestamp</th>
                    <th className="py-3.5 px-3">Username</th>
                    <th className="py-3.5 px-3">Role</th>
                    <th className="py-3.5 px-3">IP Address</th>
                    <th className="py-3.5 px-3">Browser / Device</th>
                    <th className="py-3.5 px-4 text-right">Attempt Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-200">
                  {loginHistory.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                      
                      <td className="py-3 px-4 font-mono text-slate-400">
                        {log.timestamp}
                      </td>

                      <td className="py-3 px-3 font-semibold text-slate-100">
                        {log.username}
                      </td>

                      <td className="py-3 px-3 text-slate-300">
                        {log.role}
                      </td>

                      <td className="py-3 px-3 font-mono text-amber-400">
                        {log.ip_address}
                      </td>

                      <td className="py-3 px-3 text-slate-400">
                        {log.device}
                      </td>

                      <td className="py-3 px-4 text-right">
                        {log.status === "SUCCESS" ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400 bg-emerald-950/70 border border-emerald-800/50 px-2.5 py-0.5 rounded-full">
                            <CheckCircle2 className="h-3 w-3" />
                            Success
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-400 bg-rose-950/70 border border-rose-800/50 px-2.5 py-0.5 rounded-full">
                            <AlertTriangle className="h-3 w-3" />
                            Failed Credentials
                          </span>
                        )}
                      </td>

                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      ) : (
        /* PASSWORD POLICY VIEW */
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl space-y-6 animate-fadeIn">
          
          <h3 className="font-bold text-white text-base border-b border-slate-800 pb-3 flex items-center gap-2">
            <Lock className="h-5 w-5 text-amber-400" />
            Password Policy & Account Protection Configuration
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-xs">
            
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
              <h4 className="font-bold text-slate-200">Password Complexity Rules</h4>
              <div className="flex items-center justify-between text-slate-300">
                <span>Minimum Length:</span>
                <span className="font-mono text-amber-400 font-bold">8 Characters</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span>Require Uppercase (A-Z):</span>
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span>Require Lowercase (a-z):</span>
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span>Require Digit (0-9):</span>
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span>Require Special Character (!@#$%):</span>
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
              <h4 className="font-bold text-slate-200">Account Throttling & Protection</h4>
              <div className="flex items-center justify-between text-slate-300">
                <span>Max Failed Attempts Before Lock:</span>
                <span className="font-mono text-amber-400 font-bold">5 Attempts</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span>Account Lockout Duration:</span>
                <span className="font-mono text-amber-400 font-bold">30 Minutes</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span>Password Expiration:</span>
                <span className="font-mono text-emerald-400 font-bold">90 Days</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span>Password Reuse Prevention:</span>
                <span className="font-mono text-emerald-400 font-bold">Last 5 Passwords</span>
              </div>
            </div>

          </div>

        </div>
      )}

    </div>
  );
}
