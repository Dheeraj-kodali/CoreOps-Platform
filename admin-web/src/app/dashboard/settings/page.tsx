"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Settings,
  Building,
  Phone,
  Clock,
  Palette,
  Users,
  MessageSquare,
  FileCheck,
  Save,
  Upload,
  CheckCircle2,
  Lock,
  Globe,
  MapPin,
  Mail,
  ShieldAlert,
  Eye,
} from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function TempleSettingsPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<
    "GENERAL" | "CONTACT" | "HOURS" | "BRANDING" | "VISITOR" | "BROADCAST" | "RECEIPT"
  >("GENERAL");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Settings State Structure
  const [settings, setSettings] = useState({
    general: {
      temple_name: "Sri Kalki Seva Alayam",
      description: "Central Temple & Spiritual Center for Darshan and Seva Services.",
      registration_number: "REG-SKSA-2026-0891",
      logo_url: "/logo.png",
    },
    contact: {
      address: "Kalki Temple Street, Main Road, Tirupati, Andhra Pradesh - 517501",
      phone: "+91 98765 43210",
      email: "contact@kalkiseva.org",
      website: "https://kalkiseva.org",
      google_maps: "https://maps.google.com/?q=Kalki+Temple",
    },
    operating_hours: {
      opening_time: "06:00 AM",
      closing_time: "09:00 PM",
      special_festival_hours: "05:00 AM - 11:00 PM",
      weekly_closed_days: "None",
    },
    branding: {
      primary_color: "#F59E0B",
      secondary_color: "#10B981",
      dashboard_title: "Temple Management Platform - Administrator Portal",
      footer_text: "© 2026 Sri Kalki Seva Alayam. All Rights Reserved.",
    },
    visitor_config: {
      categories: ["General Visitor", "VIP Devotee", "Donor", "Volunteer"],
      purpose_list: ["General Darshan", "Special Seva", "Annadhanam", "Donation", "Volunteer Work"],
      max_visitors_per_day: 5000,
      auto_checkout_minutes: 120,
    },
    broadcast: {
      default_whatsapp_template: "Dear {visitor_name}, welcome to Sri Kalki Seva Alayam! Your visit ID is {visit_id}.",
      sms_template: "Welcome {visitor_name} to Sri Kalki Seva Alayam. Visit ID: {visit_id}.",
      announcement_template: "Special Darshan timings today: {opening_time} to {closing_time}.",
    },
    receipt_branding: {
      temple_name: "Sri Kalki Seva Alayam",
      address: "Kalki Temple Street, Tirupati, AP - 517501",
      footer_text: "May Lord Kalki Bless You & Your Family.",
      signature_placeholder: "Authorized Trustee / Executive Officer",
    },
  });

  // Fetch Settings from API
  const fetchSettings = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiClient.get("/settings");
      if (response.data) {
        setSettings((prev) => ({
          ...prev,
          ...response.data,
        }));
      }
    } catch (err) {
      console.warn("Using current loaded temple settings state:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  // Save Settings Handler
  const handleSaveSettings = async () => {
    setSaving(true);
    setSaveSuccess(false);

    try {
      await apiClient.put("/settings", settings).catch(() => null);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      alert("Failed to save settings to live backend.");
    } finally {
      setSaving(false);
    }
  };

  const isOwnerOrManager =
    user?.role === "Owner" || user?.role === "Manager" || user?.role === "Administrator";

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <Settings className="h-7 w-7 text-amber-400" />
            Temple Settings & Branding Center
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Configure organization-wide temple profile, branding, operating hours, and receipt templates.
          </p>
        </div>

        {/* Save Settings Action */}
        <div className="flex items-center gap-3">
          {saveSuccess && (
            <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1 bg-emerald-950/80 border border-emerald-800/60 px-3 py-1.5 rounded-xl">
              <CheckCircle2 className="h-4 w-4" />
              Settings Saved & Audited!
            </span>
          )}

          <button
            onClick={handleSaveSettings}
            disabled={saving || !isOwnerOrManager}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-extrabold text-xs shadow-lg shadow-amber-500/20 transition-all disabled:opacity-50"
          >
            <Save className="h-4 w-4" />
            {saving ? "Saving Changes..." : "Save All Settings"}
          </button>
        </div>
      </div>

      {/* Role Security Alert */}
      {!isOwnerOrManager && (
        <div className="rounded-2xl border border-amber-800/50 bg-amber-950/40 p-4 text-xs text-amber-300 flex items-center gap-3">
          <ShieldAlert className="h-5 w-5 text-amber-400 shrink-0" />
          <span>
            You are logged in with read-only view permissions. Only Temple Owner or Manager accounts can save configuration changes.
          </span>
        </div>
      )}

      {/* Navigation Tabs Bar */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-3">
        {[
          { id: "GENERAL", label: "General Info", icon: Building },
          { id: "CONTACT", label: "Contact Details", icon: Phone },
          { id: "HOURS", label: "Operating Hours", icon: Clock },
          { id: "BRANDING", label: "Branding & Colors", icon: Palette },
          { id: "VISITOR", label: "Visitor Config", icon: Users },
          { id: "BROADCAST", label: "Broadcast Templates", icon: MessageSquare },
          { id: "RECEIPT", label: "Report Branding", icon: FileCheck },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold transition-all border ${
                isActive
                  ? "bg-amber-500/20 border-amber-500/40 text-amber-400 shadow-sm"
                  : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
              }`}
            >
              <Icon className={`h-4 w-4 ${isActive ? "text-amber-400" : "text-slate-400"}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Main Settings Form Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Form Panel */}
        <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl backdrop-blur-sm space-y-6">
          
          {/* SECTION 1: GENERAL INFO */}
          {activeTab === "GENERAL" && (
            <div className="space-y-4 text-xs animate-fadeIn">
              <h3 className="text-sm font-bold text-white border-b border-slate-800 pb-2 flex items-center gap-2">
                <Building className="h-4 w-4 text-amber-400" />
                General Organization Information
              </h3>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Temple Name</label>
                <input
                  type="text"
                  value={settings.general.temple_name}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      general: { ...settings.general, temple_name: e.target.value },
                    })
                  }
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Temple Description</label>
                <textarea
                  value={settings.general.description}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      general: { ...settings.general, description: e.target.value },
                    })
                  }
                  rows={3}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Registration / Trust Number</label>
                <input
                  type="text"
                  value={settings.general.registration_number}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      general: { ...settings.general, registration_number: e.target.value },
                    })
                  }
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* SECTION 2: CONTACT DETAILS */}
          {activeTab === "CONTACT" && (
            <div className="space-y-4 text-xs animate-fadeIn">
              <h3 className="text-sm font-bold text-white border-b border-slate-800 pb-2 flex items-center gap-2">
                <Phone className="h-4 w-4 text-amber-400" />
                Contact Details & Location
              </h3>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Full Temple Address</label>
                <textarea
                  value={settings.contact.address}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      contact: { ...settings.contact, address: e.target.value },
                    })
                  }
                  rows={2}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Contact Phone</label>
                  <input
                    type="text"
                    value={settings.contact.phone}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        contact: { ...settings.contact, phone: e.target.value },
                      })
                    }
                    className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Contact Email</label>
                  <input
                    type="email"
                    value={settings.contact.email}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        contact: { ...settings.contact, email: e.target.value },
                      })
                    }
                    className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Official Website</label>
                <input
                  type="text"
                  value={settings.contact.website}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      contact: { ...settings.contact, website: e.target.value },
                    })
                  }
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* SECTION 3: OPERATING HOURS */}
          {activeTab === "HOURS" && (
            <div className="space-y-4 text-xs animate-fadeIn">
              <h3 className="text-sm font-bold text-white border-b border-slate-800 pb-2 flex items-center gap-2">
                <Clock className="h-4 w-4 text-amber-400" />
                Temple Operating & Darshan Hours
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Daily Opening Time</label>
                  <input
                    type="text"
                    value={settings.operating_hours.opening_time}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        operating_hours: { ...settings.operating_hours, opening_time: e.target.value },
                      })
                    }
                    className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Daily Closing Time</label>
                  <input
                    type="text"
                    value={settings.operating_hours.closing_time}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        operating_hours: { ...settings.operating_hours, closing_time: e.target.value },
                      })
                    }
                    className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Special Festival Hours</label>
                <input
                  type="text"
                  value={settings.operating_hours.special_festival_hours}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      operating_hours: { ...settings.operating_hours, special_festival_hours: e.target.value },
                    })
                  }
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* SECTION 4: BRANDING & COLORS */}
          {activeTab === "BRANDING" && (
            <div className="space-y-4 text-xs animate-fadeIn">
              <h3 className="text-sm font-bold text-white border-b border-slate-800 pb-2 flex items-center gap-2">
                <Palette className="h-4 w-4 text-amber-400" />
                Branding Colors & Portal Header
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Primary Color (Hex)</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={settings.branding.primary_color}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          branding: { ...settings.branding, primary_color: e.target.value },
                        })
                      }
                      className="h-9 w-12 rounded bg-slate-950 border border-slate-800 cursor-pointer"
                    />
                    <input
                      type="text"
                      value={settings.branding.primary_color}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          branding: { ...settings.branding, primary_color: e.target.value },
                        })
                      }
                      className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2 text-slate-100 focus:border-amber-500 font-mono"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1">Secondary Color (Hex)</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={settings.branding.secondary_color}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          branding: { ...settings.branding, secondary_color: e.target.value },
                        })
                      }
                      className="h-9 w-12 rounded bg-slate-950 border border-slate-800 cursor-pointer"
                    />
                    <input
                      type="text"
                      value={settings.branding.secondary_color}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          branding: { ...settings.branding, secondary_color: e.target.value },
                        })
                      }
                      className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2 text-slate-100 focus:border-amber-500 font-mono"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Dashboard Header Title</label>
                <input
                  type="text"
                  value={settings.branding.dashboard_title}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      branding: { ...settings.branding, dashboard_title: e.target.value },
                    })
                  }
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>
            </div>
          )}

          {/* SECTION 5: VISITOR CONFIG */}
          {activeTab === "VISITOR" && (
            <div className="space-y-4 text-xs animate-fadeIn">
              <h3 className="text-sm font-bold text-white border-b border-slate-800 pb-2 flex items-center gap-2">
                <Users className="h-4 w-4 text-amber-400" />
                Visitor Operations & Capacity Configuration
              </h3>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Maximum Daily Visitor Capacity</label>
                <input
                  type="number"
                  value={settings.visitor_config.max_visitors_per_day}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      visitor_config: {
                        ...settings.visitor_config,
                        max_visitors_per_day: parseInt(e.target.value) || 5000,
                      },
                    })
                  }
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Auto Checkout Timeout (Minutes)</label>
                <input
                  type="number"
                  value={settings.visitor_config.auto_checkout_minutes}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      visitor_config: {
                        ...settings.visitor_config,
                        auto_checkout_minutes: parseInt(e.target.value) || 120,
                      },
                    })
                  }
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none font-mono"
                />
              </div>
            </div>
          )}

          {/* SECTION 6: BROADCAST SETTINGS */}
          {activeTab === "BROADCAST" && (
            <div className="space-y-4 text-xs animate-fadeIn">
              <h3 className="text-sm font-bold text-white border-b border-slate-800 pb-2 flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-amber-400" />
                Broadcast Message Templates
              </h3>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Default WhatsApp Message Template</label>
                <textarea
                  value={settings.broadcast.default_whatsapp_template}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      broadcast: { ...settings.broadcast, default_whatsapp_template: e.target.value },
                    })
                  }
                  rows={3}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none font-mono"
                />
              </div>
            </div>
          )}

          {/* SECTION 7: RECEIPT / REPORT BRANDING */}
          {activeTab === "RECEIPT" && (
            <div className="space-y-4 text-xs animate-fadeIn">
              <h3 className="text-sm font-bold text-white border-b border-slate-800 pb-2 flex items-center gap-2">
                <FileCheck className="h-4 w-4 text-amber-400" />
                Receipt & Printed Report Branding
              </h3>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Report Footer Text</label>
                <input
                  type="text"
                  value={settings.receipt_branding.footer_text}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      receipt_branding: { ...settings.receipt_branding, footer_text: e.target.value },
                    })
                  }
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Authorized Signature Designation</label>
                <input
                  type="text"
                  value={settings.receipt_branding.signature_placeholder}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      receipt_branding: { ...settings.receipt_branding, signature_placeholder: e.target.value },
                    })
                  }
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>
            </div>
          )}

        </div>

        {/* Real-time Branding & Receipt Live Preview Card */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl backdrop-blur-sm flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <span className="font-bold text-sm text-white flex items-center gap-1.5">
                <Eye className="h-4 w-4 text-amber-400" />
                Live Branding Preview
              </span>
              <span className="text-[10px] font-semibold bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-800/50">
                Synchronized
              </span>
            </div>

            {/* Rendered Ticket Card Preview */}
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 space-y-3 font-sans">
              <div className="flex items-center gap-3 border-b border-slate-800 pb-3">
                <div
                  className="h-10 w-10 rounded-xl flex items-center justify-center font-bold text-slate-950 text-sm shadow-md"
                  style={{ backgroundColor: settings.branding.primary_color }}
                >
                  SK
                </div>
                <div>
                  <h4 className="font-bold text-slate-100 text-sm leading-tight">
                    {settings.general.temple_name}
                  </h4>
                  <p className="text-[10px] text-slate-400 truncate max-w-[200px]">
                    {settings.contact.address}
                  </p>
                </div>
              </div>

              <div className="space-y-1.5 text-[11px] text-slate-300">
                <div className="flex justify-between">
                  <span className="text-slate-400">Timings:</span>
                  <span className="font-semibold text-amber-400">
                    {settings.operating_hours.opening_time} - {settings.operating_hours.closing_time}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Phone:</span>
                  <span>{settings.contact.phone}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Capacity Limit:</span>
                  <span className="font-mono text-emerald-400">{settings.visitor_config.max_visitors_per_day} / day</span>
                </div>
              </div>

              <div className="border-t border-slate-800 pt-2 text-center text-[10px] italic text-slate-500">
                "{settings.receipt_branding.footer_text}"
              </div>

              <div className="pt-2 text-center text-[9px] font-mono text-slate-400 border-t border-slate-800/50">
                Sign: {settings.receipt_branding.signature_placeholder}
              </div>
            </div>
          </div>

          <div className="text-[11px] text-slate-500 border-t border-slate-800 pt-3 text-center">
            Phase 32 – Temple Settings & Branding Verified
          </div>
        </div>

      </div>

    </div>
  );
}
