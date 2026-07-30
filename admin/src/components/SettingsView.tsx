"use client";

import React from "react";
import { Save, Globe, Smartphone, Lock, Building } from "lucide-react";

interface SettingsViewProps {
  language: "en" | "te";
}

export default function SettingsView() {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Temple Information */}
      <div className="temple-card p-6 space-y-4">
        <div className="flex items-center gap-2 border-b border-amber-200 pb-3">
          <Building className="w-5 h-5 text-[#D4AF37]" />
          <h3 className="heading-temple text-lg font-bold text-[#2C1A11]">Temple Profile & Contact</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-semibold text-amber-900">
          <div>
            <label className="block mb-1">Official Temple Name</label>
            <input type="text" className="w-full p-2.5 border rounded-lg bg-white" defaultValue="Sri Kalki Seva Alayam" />
          </div>
          <div>
            <label className="block mb-1">Primary Contact Phone</label>
            <input type="text" className="w-full p-2.5 border rounded-lg bg-white" defaultValue="+91 98765 43210" />
          </div>
          <div className="md:col-span-2">
            <label className="block mb-1">Temple Address</label>
            <textarea className="w-full p-2.5 border rounded-lg bg-white" rows={2} defaultValue="Sri Kalki Seva Alayam Temple Complex, Chittoor Highway, Andhra Pradesh, India" />
          </div>
        </div>
      </div>

      {/* Gateway API Credentials */}
      <div className="temple-card p-6 space-y-4">
        <div className="flex items-center gap-2 border-b border-amber-200 pb-3">
          <Lock className="w-5 h-5 text-[#D4AF37]" />
          <h3 className="heading-temple text-lg font-bold text-[#2C1A11]">Messaging API Credentials</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-semibold text-amber-900">
          <div>
            <label className="block mb-1">SMS Gateway API Key</label>
            <input type="password" className="w-full p-2.5 border rounded-lg bg-white" defaultValue="sk_live_sms_998877665544332211" />
          </div>
          <div>
            <label className="block mb-1">WhatsApp Business Token</label>
            <input type="password" className="w-full p-2.5 border rounded-lg bg-white" defaultValue="EAAGm0PX4Z070BA..." />
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button className="flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-[#D4AF37] to-[#997A15] text-[#2C1A11] font-bold text-sm rounded-lg shadow-lg hover:opacity-95 transition-all">
          <Save className="w-4 h-4" /> Save System Settings
        </button>
      </div>
    </div>
  );
};
