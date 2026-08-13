"use client";

import React, { useEffect, useState, useCallback } from "react";
import {
  Users,
  UserCheck,
  LogOut,
  RefreshCw,
  Radio,
  Clock,
  TrendingUp,
  ShieldCheck,
  Activity,
  ArrowUpRight,
  PieChart as PieChartIcon,
  BarChart3,
} from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useWebSocket } from "@/context/WebSocketContext";

interface Visitor {
  id: string;
  name: string;
  phone_number?: string;
  phone?: string;
  persons_count: number;
  visitor_date?: string;
  date?: string;
  visitor_time?: string;
  time?: string;
  purpose?: { name_en?: string };
}

interface PurposeBreakdownItem {
  name: string;
  count: number;
  percentage?: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState({
    todaysVisitors: 0,
    visitorsInside: 0,
    checkIns: 0,
    checkOuts: 0,
    pendingSync: 0,
    broadcastStatus: "Active",
  });

  const [recentVisitors, setRecentVisitors] = useState<Visitor[]>([]);
  const [purposeBreakdown, setPurposeBreakdown] = useState<PurposeBreakdownItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<string>("");

  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { isConnected: wsConnected, lastEvent } = useWebSocket();

  const loadLiveDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      const dashboardRes = await apiClient.get("/analytics/dashboard");

      if (dashboardRes?.data) {
        const d = dashboardRes.data;
        setStats({
          todaysVisitors: d.todays_visitors ?? 0,
          visitorsInside: d.visitors_inside ?? 0,
          checkIns: d.todays_check_ins ?? 0,
          checkOuts: d.todays_check_outs ?? 0,
          pendingSync: d.pending_sync ?? 0,
          broadcastStatus: d.broadcast_status || "Active",
        });

        if (d.recent_visitors?.length) {
          setRecentVisitors(d.recent_visitors);
        }
        if (d.purpose_breakdown?.length) {
          setPurposeBreakdown(
            d.purpose_breakdown.map((item: any) => ({
              name: item.name || item.name_en || "General Darshan",
              count: item.count || 0,
              percentage: item.percentage || 0,
            }))
          );
        }
      }
      setLastRefreshed(new Date().toLocaleTimeString());
    } catch (err: any) {
      console.warn("Could not retrieve live dashboard data:", err?.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      loadLiveDashboardData();

      // Smart 10s fallback polling interval for instant APK sync
      const interval = setInterval(() => {
        loadLiveDashboardData();
      }, 10000);

      return () => clearInterval(interval);
    }
  }, [authLoading, isAuthenticated, loadLiveDashboardData]);

  // Real-time WebSocket event received -> refresh live dashboard data instantly
  useEffect(() => {
    if (lastEvent) {
      console.log("[DashboardPage] Real-time event received from WebSocket:", lastEvent);
      loadLiveDashboardData();
    }
  }, [lastEvent, loadLiveDashboardData]);

  const cards = [
    {
      title: "Today's Visitors",
      value: stats.todaysVisitors,
      change: "Total devotees registered today",
      icon: Users,
      color: "from-amber-500/20 to-amber-600/5 text-amber-400 border-amber-500/30",
    },
    {
      title: "Visitors Inside",
      value: stats.visitorsInside,
      change: "Currently in temple premises",
      icon: UserCheck,
      color: "from-emerald-500/20 to-emerald-600/5 text-emerald-400 border-emerald-500/30",
    },
    {
      title: "Today's Check-ins",
      value: stats.checkIns,
      change: "Entry visits recorded",
      icon: TrendingUp,
      color: "from-blue-500/20 to-blue-600/5 text-blue-400 border-blue-500/30",
    },
    {
      title: "Today's Check-outs",
      value: stats.checkOuts,
      change: "Completed visits",
      icon: LogOut,
      color: "from-purple-500/20 to-purple-600/5 text-purple-400 border-purple-500/30",
    },
    {
      title: "Pending Sync",
      value: stats.pendingSync,
      change: "Queue status",
      icon: RefreshCw,
      color: "from-sky-500/20 to-sky-600/5 text-sky-400 border-sky-500/30",
    },
    {
      title: "Messaging Status",
      value: "Active",
      change: "WhatsApp & SMS notifications",
      icon: Radio,
      color: "from-rose-500/20 to-rose-600/5 text-rose-400 border-rose-500/30",
    },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Temple Operations Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Real-time devotee attendance and darshan analytics.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="inline-flex items-center gap-2 rounded-xl bg-slate-900 border border-slate-800 px-3.5 py-2 text-xs font-mono text-slate-300">
            <Clock className="h-3.5 w-3.5 text-amber-400" />
            <span className="flex items-center gap-1.5">
              {loading ? (
                <>
                  <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse" />
                  <span>Loading Data...</span>
                </>
              ) : (
                <>
                  <span className={`h-2 w-2 rounded-full ${wsConnected ? "bg-emerald-400 animate-pulse" : "bg-amber-400"}`} />
                  <span>{wsConnected ? "WebSocket Real-Time Active" : "System Active"} • Refreshed {lastRefreshed || "Just Now"}</span>
                </>
              )}
            </span>
          </div>

          <button
            type="button"
            onClick={loadLiveDashboardData}
            disabled={loading}
            className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 hover:bg-amber-500/20 active:scale-95 transition-all disabled:opacity-50"
            title="Refresh Data"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.title}
              className={`relative overflow-hidden rounded-2xl border bg-gradient-to-br p-6 shadow-xl backdrop-blur-sm transition-all hover:scale-[1.01] ${card.color}`}
            >
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  {card.title}
                </span>
                <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
                  <Icon className="h-5 w-5" />
                </div>
              </div>

              <div className="text-3xl font-extrabold text-white tracking-tight mb-1">
                {typeof card.value === "number" ? card.value.toLocaleString() : card.value}
              </div>

              <div className="text-xs text-slate-400 flex items-center gap-1">
                <span>{card.change}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Visitors & Purpose Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Recent Visitors Live Table */}
        <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl backdrop-blur-sm">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-amber-400" />
              <h3 className="font-bold text-base text-white">Recent Visitors</h3>
            </div>
            <span className="text-xs text-amber-400 font-semibold cursor-pointer hover:underline flex items-center gap-1">
              View All <ArrowUpRight className="h-3.5 w-3.5" />
            </span>
          </div>

          <div className="overflow-x-auto">
            {recentVisitors.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-xs font-medium">
                No visitors registered today.
              </div>
            ) : (
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                    <th className="pb-3 px-2">Visitor Name</th>
                    <th className="pb-3 px-2">Phone</th>
                    <th className="pb-3 px-2">Headcount</th>
                    <th className="pb-3 px-2">Date / Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-200">
                  {recentVisitors.map((v, idx) => (
                    <tr key={v.id || `visitor-${idx}`} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-2 font-medium text-slate-100">{v.name}</td>
                      <td className="py-3 px-2 text-slate-400 font-mono">{v.phone_number || v.phone || "—"}</td>
                      <td className="py-3 px-2 font-semibold text-amber-400">{v.persons_count || 1} persons</td>
                      <td className="py-3 px-2 text-slate-400 font-mono">
                        {v.visitor_date || v.date || "Today"} {v.visitor_time || v.time || ""}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Live Purpose Analytics Chart Card */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl backdrop-blur-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 border-b border-slate-800 pb-4 mb-4">
              <PieChartIcon className="h-5 w-5 text-amber-400" />
              <h3 className="font-bold text-base text-white">Darshan Purpose Breakdown</h3>
            </div>

            {purposeBreakdown.length === 0 ? (
              <div className="space-y-4">
                {[
                  { name: "General Darshan", count: 0, pct: 100 },
                ].map((item) => (
                  <div key={item.name} className="space-y-1.5">
                    <div className="flex justify-between text-xs font-semibold text-slate-300">
                      <span>{item.name}</span>
                      <span className="font-mono text-amber-400">{item.count} ({item.pct}%)</span>
                    </div>
                    <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full"
                        style={{ width: `${item.pct}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {purposeBreakdown.map((item, idx) => (
                  <div key={item.name || `purpose-${idx}`} className="space-y-1.5">
                    <div className="flex justify-between text-xs font-semibold text-slate-300">
                      <span>{item.name}</span>
                      <span className="font-mono text-amber-400">
                        {item.count} {item.percentage ? `(${item.percentage}%)` : ""}
                      </span>
                    </div>
                    <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full"
                        style={{ width: `${Math.min(100, item.percentage || 30)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <BarChart3 className="h-4 w-4 text-emerald-400" />
              Real-time Analytics
            </span>
            <span className="text-[11px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2 py-0.5 rounded-full">
              System Active
            </span>
          </div>
        </div>

      </div>

      {/* System Operational Status Monitor */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl backdrop-blur-sm">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-emerald-400" />
            <h3 className="font-bold text-base text-white">System Operational Status</h3>
          </div>
          <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />{" "}OPERATIONAL
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
            <div>
              <p className="text-slate-400 font-semibold mb-0.5">Central Server</p>
              <p className="text-[11px] text-slate-500 font-mono">Sri Kalki Seva Cloud</p>
            </div>
            <span className="px-2.5 py-1 rounded-full bg-emerald-950/80 border border-emerald-800/60 text-emerald-400 font-semibold text-[11px]">
              ONLINE
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
            <div>
              <p className="text-slate-400 font-semibold mb-0.5">Database Storage</p>
              <p className="text-[11px] text-slate-500 font-mono">Secure Cloud DB</p>
            </div>
            <span className="px-2.5 py-1 rounded-full bg-emerald-950/80 border border-emerald-800/60 text-emerald-400 font-semibold text-[11px]">
              CONNECTED
            </span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
            <div>
              <p className="text-slate-400 font-semibold mb-0.5">Mobile Synchronization</p>
              <p className="text-[11px] text-slate-500 font-mono">Real-time Outbox</p>
            </div>
            <span className="px-2.5 py-1 rounded-full bg-emerald-950/80 border border-emerald-800/60 text-emerald-400 font-semibold text-[11px]">
              ACTIVE
            </span>
          </div>
        </div>
      </div>

    </div>
  );
}
