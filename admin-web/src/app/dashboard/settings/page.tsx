import React from "react";
import { Settings } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Settings className="h-6 w-6 text-amber-400" />
          System Settings
        </h1>
        <p className="text-xs text-slate-400 mt-1">Configure global application parameters & API keys</p>
      </div>
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-8 text-center text-slate-400">
        System Settings Module Foundation Ready.
      </div>
    </div>
  );
}
