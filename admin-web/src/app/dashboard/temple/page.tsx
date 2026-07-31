import React from "react";
import { Landmark } from "lucide-react";

export default function TemplePage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Landmark className="h-6 w-6 text-amber-400" />
          Temple Profile & Details
        </h1>
        <p className="text-xs text-slate-400 mt-1">Configure temple info, address, and social links</p>
      </div>
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-8 text-center text-slate-400">
        Temple Profile Module Foundation Ready.
      </div>
    </div>
  );
}
