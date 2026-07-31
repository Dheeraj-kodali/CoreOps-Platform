"use client";

import React, { useState } from "react";
import { Shield, Lock, User, Eye, EyeOff, AlertCircle, Server } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setErrorMsg("Please enter both Username/Email and Password.");
      return;
    }

    setErrorMsg(null);
    setIsSubmitting(true);

    try {
      const result = await login(username, password);
      if (!result.success) {
        setErrorMsg(result.error || "Authentication failed. Please check credentials.");
      }
    } catch (err: any) {
      setErrorMsg("An unexpected connection error occurred.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const backendUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://coreops-platform.onrender.com/api/v1";

  return (
    <main className="min-h-screen relative flex items-center justify-center bg-slate-950 px-4 py-12 overflow-hidden">
      {/* Background Lighting Effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-tr from-amber-500/20 via-orange-600/10 to-transparent rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-10 right-10 w-[350px] h-[350px] bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b15_1px,transparent_1px),linear-gradient(to_bottom,#1e293b15_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] pointer-events-none" />

      <div className="relative z-10 w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl backdrop-blur-xl transition-all sm:p-10">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-400">
            <Shield className="h-3.5 w-3.5" />
            <span>Admin Portal</span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-emerald-400 font-mono bg-emerald-950/60 border border-emerald-800/40 px-2.5 py-0.5 rounded-full">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Live Backend
          </div>
        </div>

        <h1 className="text-2xl font-bold tracking-tight text-white mb-1">
          Sign in to Admin Portal
        </h1>
        <p className="text-xs text-slate-400 mb-6">
          Temple Management Platform Operational Console
        </p>

        {/* Backend Target Alert */}
        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3 mb-6 flex items-center justify-between text-xs text-slate-400">
          <span className="flex items-center gap-1.5 text-slate-300 font-medium">
            <Server className="h-3.5 w-3.5 text-amber-400" />
            Target API:
          </span>
          <span className="font-mono text-[11px] text-amber-300/80 truncate max-w-[200px]" title={backendUrl}>
            {backendUrl}
          </span>
        </div>

        {/* Error Alert */}
        {errorMsg && (
          <div className="mb-6 rounded-lg border border-rose-800/50 bg-rose-950/40 p-3.5 text-xs text-rose-300 flex items-start gap-2.5 animate-fadeIn">
            <AlertCircle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
              Username / Email
            </label>
            <div className="relative">
              <User className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                id="username-input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="admin or user@kalkiseva.org"
                required
                className="w-full rounded-xl border border-slate-800 bg-slate-950/80 pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                id="password-input"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full rounded-xl border border-slate-800 bg-slate-950/80 pl-10 pr-10 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 transition-colors"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          <button
            id="login-submit-btn"
            type="submit"
            disabled={isSubmitting}
            className="w-full relative group overflow-hidden rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-bold px-6 py-3 shadow-lg shadow-amber-500/25 transition-all duration-200 active:scale-[0.99] disabled:opacity-50 disabled:pointer-events-none mt-2 flex items-center justify-center gap-2"
          >
            {isSubmitting ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-950 border-t-transparent" />
                <span>Authenticating...</span>
              </>
            ) : (
              <span>Sign In</span>
            )}
          </button>
        </form>

        {/* Demo Credentials Tip */}
        <div className="mt-6 pt-4 border-t border-slate-800/80 text-center text-xs text-slate-500">
          Demo Admin: <code className="text-amber-400 font-mono">admin</code> / <code className="text-amber-400 font-mono">admin123</code>
        </div>
      </div>
    </main>
  );
}
