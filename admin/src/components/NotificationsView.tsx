"use client";

import React, { useState } from "react";
import { MessageSquare, RefreshCw, CheckCircle, AlertTriangle, Send } from "lucide-react";

interface NotificationsViewProps {
  language: "en" | "te";
}

export default function NotificationsView() {
  const language: string = "en";
  const [activeSubTab, setActiveSubTab] = useState<"logs" | "templates">("logs");

  const templates = [
    { code: "WELCOME_GREETING_SMS", channel: "SMS", name: "Welcome SMS", contentEn: "Sri Kalki Seva Alayam: Welcome {{name}}. Your registration is confirmed for {{purpose}}.", contentTe: "శ్రీ కల్కి సేవా ఆలయం: స్వాగతం {{name}}. మీ {{purpose}} నమోదు స్థిరీకరించబడింది." },
    { code: "ANNADANAM_RECEIPT_WA", channel: "WHATSAPP", name: "Annadanam WhatsApp Receipt", contentEn: "Namaste {{name}}, Thank you for your Annadanam contribution at Sri Kalki Seva Alayam.", contentTe: "నమస్తే {{name}}, శ్రీ కల్కి సేవా ఆలయంలో మీ అన్నదాన సేవకు ధన్యవాదములు." },
  ];

  const logs = [
    { id: 101, visitor: "Ramesh Kumar", phone: "+91 98765 43210", channel: "WHATSAPP", template: "WELCOME_GREETING_SMS", status: "DELIVERED", time: "10:30 AM", retries: 0 },
    { id: 102, visitor: "Saraswathi Amma", phone: "+91 94401 12345", channel: "SMS", template: "WELCOME_GREETING_SMS", status: "DELIVERED", time: "09:45 AM", retries: 0 },
    { id: 103, visitor: "Venkatadri M", phone: "+91 98480 99887", channel: "SMS", template: "WELCOME_GREETING_SMS", status: "FAILED", time: "09:12 AM", retries: 2 },
  ];

  return (
    <div className="space-y-6">
      {/* Subtab navigation */}
      <div className="flex items-center justify-between temple-card p-4">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveSubTab("logs")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              activeSubTab === "logs" ? "bg-[#2C1A11] text-[#D4AF37]" : "bg-amber-50 text-amber-900 hover:bg-amber-100"
            }`}
          >
            Delivery Logs & Retry Queue
          </button>
          <button
            onClick={() => setActiveSubTab("templates")}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              activeSubTab === "templates" ? "bg-[#2C1A11] text-[#D4AF37]" : "bg-amber-50 text-amber-900 hover:bg-amber-100"
            }`}
          >
            Message Templates (SMS & WhatsApp)
          </button>
        </div>
      </div>

      {activeSubTab === "logs" ? (
        <div className="temple-card overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-[#2C1A11] text-[#D4AF37] text-xs uppercase font-semibold">
              <tr>
                <th className="py-3.5 px-4">Visitor</th>
                <th className="py-3.5 px-4">Phone</th>
                <th className="py-3.5 px-4">Channel</th>
                <th className="py-3.5 px-4">Template</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">Retries</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-amber-100">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-amber-50/50 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-[#2C1A11]">{log.visitor}</td>
                  <td className="py-3.5 px-4 text-gray-600 font-mono text-xs">{log.phone}</td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold ${
                      log.channel === "WHATSAPP" ? "bg-green-100 text-green-800" : "bg-blue-100 text-blue-800"
                    }`}>
                      {log.channel}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-xs text-gray-600">{log.template}</td>
                  <td className="py-3.5 px-4">
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                      log.status === "DELIVERED" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                    }`}>
                      {log.status === "DELIVERED" ? <CheckCircle className="w-3 h-3 text-green-600" /> : <AlertTriangle className="w-3 h-3 text-red-600" />}
                      {log.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-xs font-bold">{log.retries}</td>
                  <td className="py-3.5 px-4 text-right">
                    {log.status === "FAILED" && (
                      <button className="flex items-center gap-1 text-xs font-bold text-[#2C1A11] bg-amber-200 hover:bg-[#D4AF37] px-2.5 py-1 rounded ml-auto">
                        <RefreshCw className="w-3 h-3" /> Retry Send
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {templates.map((tpl, idx) => (
            <div key={idx} className="temple-card p-6 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase text-amber-900 bg-amber-100 px-2 py-0.5 rounded border border-[#D4AF37]/30">
                  {tpl.channel}
                </span>
                <span className="font-mono text-xs text-gray-400">{tpl.code}</span>
              </div>
              <h4 className="heading-temple text-base font-bold text-[#2C1A11]">{tpl.name}</h4>
              <div className="space-y-2 text-xs">
                <div>
                  <p className="font-bold text-amber-900">English Template:</p>
                  <p className="p-2 bg-amber-50 rounded border text-gray-700">{tpl.contentEn}</p>
                </div>
                <div>
                  <p className="font-bold text-amber-900">Telugu Template:</p>
                  <p className="p-2 bg-amber-50 rounded border text-gray-700">{tpl.contentTe}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
