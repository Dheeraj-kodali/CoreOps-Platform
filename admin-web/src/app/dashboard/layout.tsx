"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  FileText,
  MessageSquare,
  Landmark,
  UserCheck,
  Settings,
  Bell,
  User as UserIcon,
  Key,
  Lock,
  LogOut,
  ChevronDown,
  Menu,
  X,
  Shield,
  ShieldCheck,
  Activity,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard, roles: ["Owner", "Administrator", "Manager", "Reception Staff", "Volunteer", "Security", "Auditor"] },
  { name: "Visitors", href: "/dashboard/visitors", icon: Users, roles: ["Owner", "Administrator", "Manager", "Reception Staff", "Volunteer"] },
  { name: "Reports", href: "/dashboard/reports", icon: FileText, roles: ["Owner", "Administrator", "Manager", "Auditor"] },
  { name: "Communication", href: "/dashboard/communication", icon: MessageSquare, roles: ["Owner", "Administrator", "Manager"] },
  { name: "Users & Roles", href: "/dashboard/users", icon: UserCheck, roles: ["Owner", "Administrator", "Manager"] },
  { name: "Operations Center", href: "/dashboard/operations", icon: Activity, roles: ["Owner", "Administrator", "Manager", "Auditor"] },
  { name: "Security Center", href: "/dashboard/security", icon: ShieldCheck, roles: ["Owner", "Administrator", "Manager", "Auditor"] },
  { name: "Temple Profile", href: "/dashboard/temple", icon: Landmark, roles: ["Owner", "Administrator", "Manager"] },
  { name: "Settings", href: "/dashboard/settings", icon: Settings, roles: ["Owner", "Administrator"] },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  const currentUserRole = user?.role || "Administrator";

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md px-4 sm:px-6 h-16 flex items-center justify-between">
        
        {/* Left Section: Mobile Menu Toggle & App Title */}
        <div className="flex items-center gap-3 sm:gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            aria-label="Toggle Navigation Menu"
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>

          <Link href="/dashboard" className="flex items-center gap-2.5 group">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-500 flex items-center justify-center shadow-lg shadow-amber-500/20 group-hover:scale-105 transition-transform">
              <Shield className="h-5 w-5 text-slate-950 font-bold" />
            </div>
            <div>
              <span className="font-bold text-base sm:text-lg tracking-tight text-white block leading-tight">
                Temple Management Platform
              </span>
              <span className="text-[10px] uppercase font-semibold tracking-wider text-amber-400 block">
                Administrator Portal
              </span>
            </div>
          </Link>
        </div>

        {/* Right Section: Notifications & Profile Avatar Dropdown */}
        <div className="flex items-center gap-2 sm:gap-3">
          
          {/* Notifications Icon */}
          <div className="relative">
            <button
              onClick={() => {
                setNotificationsOpen(!notificationsOpen);
                setProfileDropdownOpen(false);
              }}
              className="relative p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              aria-label="Notifications"
            >
              <Bell className="h-5 w-5" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-amber-400 ring-2 ring-slate-900 animate-pulse" />
            </button>

            {notificationsOpen && (
              <div className="absolute right-0 mt-2 w-80 rounded-2xl border border-slate-800 bg-slate-900 p-4 shadow-2xl z-50 animate-fadeIn">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                    System Event Log
                  </h4>
                  <span className="text-[10px] font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-2 py-0.5 rounded-full">
                    Live Real-Time
                  </span>
                </div>
                <div className="space-y-2.5 text-xs">
                  <div className="p-2 rounded-lg bg-slate-850 border border-slate-800 hover:bg-slate-800 transition-colors">
                    <p className="font-semibold text-slate-200">PostgreSQL Cloud DB Connection</p>
                    <p className="text-slate-400 text-[11px] mt-0.5">Neon PostgreSQL Database active & responding</p>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-850 border border-slate-800 hover:bg-slate-800 transition-colors">
                    <p className="font-semibold text-slate-200">Offline Delta Outbox Sync Engine</p>
                    <p className="text-slate-400 text-[11px] mt-0.5">Mobile outbox queue sync protocol active</p>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-850 border border-slate-800 hover:bg-slate-800 transition-colors">
                    <p className="font-semibold text-slate-200">Background Worker Scheduler</p>
                    <p className="text-slate-400 text-[11px] mt-0.5">Cron scheduler running on Render worker process</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="h-5 w-[1px] bg-slate-800 mx-1 hidden sm:block" />

          {/* Profile Avatar & Dropdown */}
          <div className="relative">
            <button
              onClick={() => {
                setProfileDropdownOpen(!profileDropdownOpen);
                setNotificationsOpen(false);
              }}
              className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-slate-800 border border-transparent hover:border-slate-700 transition-all"
            >
              <div className="h-8 w-8 rounded-lg bg-amber-500/20 border border-amber-500/40 text-amber-400 font-bold text-xs flex items-center justify-center uppercase">
                {user?.username?.substring(0, 2) || "AD"}
              </div>
              <div className="text-left hidden sm:block">
                <span className="text-xs font-semibold text-slate-200 block leading-tight">
                  {user?.fullName || user?.username || "Admin"}
                </span>
                <span className="text-[10px] text-slate-400 block leading-tight">
                  {user?.role || "Administrator"}
                </span>
              </div>
              <ChevronDown className="h-4 w-4 text-slate-400 hidden sm:block" />
            </button>

            {/* Profile Dropdown Menu */}
            {profileDropdownOpen && (
              <div className="absolute right-0 mt-2 w-56 rounded-2xl border border-slate-800 bg-slate-900 p-2 shadow-2xl z-50 animate-fadeIn">
                <div className="px-3 py-2 border-b border-slate-800 mb-1">
                  <p className="text-xs font-bold text-slate-200">{user?.fullName || user?.username}</p>
                  <p className="text-[11px] text-slate-400">{user?.email || "admin@kalkiseva.org"}</p>
                </div>

                <div className="space-y-0.5 text-xs font-medium">
                  <button
                    onClick={() => {
                      setProfileDropdownOpen(false);
                    }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
                  >
                    <UserIcon className="h-4 w-4 text-slate-400" />
                    <span>Profile</span>
                  </button>

                  <button
                    onClick={() => {
                      setProfileDropdownOpen(false);
                    }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
                  >
                    <Key className="h-4 w-4 text-slate-400" />
                    <span>Change Password</span>
                  </button>

                  <button
                    onClick={() => {
                      setProfileDropdownOpen(false);
                    }}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
                  >
                    <Lock className="h-4 w-4 text-slate-400" />
                    <span>Change PIN</span>
                  </button>
                </div>

                <div className="border-t border-slate-800 mt-1 pt-1">
                  <button
                    onClick={logout}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-rose-400 hover:bg-rose-950/40 hover:text-rose-300 transition-colors text-xs font-semibold"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            )}
          </div>

        </div>
      </header>

      {/* Main Body with Responsive Sidebar & Content */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Sidebar */}
        <aside
          className={`fixed inset-y-0 left-0 z-30 w-64 bg-slate-900/95 border-r border-slate-800 pt-20 pb-6 px-4 flex flex-col justify-between transition-transform duration-300 ease-in-out md:static md:translate-x-0 md:pt-6 ${
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <div className="space-y-1">
            <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
              Core Modules
            </div>

            {navItems
              .filter((item) => item.roles.includes(currentUserRole) || currentUserRole === "Administrator" || currentUserRole === "Owner")
              .map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));

                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setSidebarOpen(false)}
                    className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all duration-150 ${
                      isActive
                        ? "bg-amber-500/15 border border-amber-500/30 text-amber-400 shadow-sm"
                        : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/60"
                    }`}
                  >
                    <Icon className={`h-4 w-4 ${isActive ? "text-amber-400" : "text-slate-400"}`} />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
          </div>

          {/* Sidebar Bottom Banner */}
          <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-3.5 text-xs text-slate-400">
            <div className="flex items-center justify-between mb-1">
              <span className="font-semibold text-slate-200">Role Security</span>
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            </div>
            <p className="text-[11px] text-slate-500">
              {currentUserRole} RBAC active
            </p>
          </div>
        </aside>

        {/* Backdrop overlay for mobile sidebar */}
        {sidebarOpen && (
          <div
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 z-20 bg-slate-950/80 backdrop-blur-sm md:hidden"
          />
        )}

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-slate-950">
          {children}
        </main>
      </div>

    </div>
  );
}
