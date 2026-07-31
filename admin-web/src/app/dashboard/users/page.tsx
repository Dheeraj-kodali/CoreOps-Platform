import React from "react";
import { UserCheck } from "lucide-react";

export default function UsersPage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <UserCheck className="h-6 w-6 text-amber-400" />
          User & Staff Management
        </h1>
        <p className="text-xs text-slate-400 mt-1">Manage staff accounts, roles, and authorization</p>
      </div>
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-8 text-center text-slate-400">
        User Management Module Foundation Ready.
      </div>
    </div>
  );
}
