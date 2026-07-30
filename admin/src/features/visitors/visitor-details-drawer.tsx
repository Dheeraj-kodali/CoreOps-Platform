'use client';

import React, { useState } from 'react';
import { X, User, Phone, Calendar, Clock, MapPin, HeartHandshake, ShieldCheck, QrCode, Printer, Activity, History, Star, FileText } from 'lucide-react';
import { Visitor, VisitorStatus } from '../../types/visitor';

interface VisitorDetailsDrawerProps {
  visitor: Visitor | null;
  isOpen: boolean;
  onClose: () => void;
}

const LIFECYCLE_STEPS: VisitorStatus[] = ['REGISTERED', 'CHECKED_IN', 'WAITING', 'INSIDE_TEMPLE', 'COMPLETED'];

export function VisitorDetailsDrawer({ visitor, isOpen, onClose }: VisitorDetailsDrawerProps) {
  const [showQR, setShowQR] = useState(false);
  const [activeTab, setActiveTab] = useState<'DETAILS' | 'TIMELINE' | 'AUDIT'>('DETAILS');

  if (!isOpen || !visitor) return null;

  const currentStatus = visitor.status || 'CHECKED_IN';
  const currentStepIdx = LIFECYCLE_STEPS.indexOf(currentStatus);

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end animate-fadeIn">
      <div className="w-full max-w-lg bg-white dark:bg-[#1C1410] text-[#1C1410] dark:text-[#FAFAFA] h-full shadow-2xl border-l border-[#D4AF37]/30 flex flex-col justify-between overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-[#D4AF37]/20 bg-gray-50 dark:bg-[#2C1A11]">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#D4AF37] to-[#FF9933] flex items-center justify-center font-bold text-xl text-[#1C1410] shadow-md">
                {visitor.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-lg font-bold font-serif text-[#D4AF37]">{visitor.name}</h2>
                  {(visitor.is_repeat_visitor || (visitor.total_visits_count && visitor.total_visits_count > 1)) && (
                    <span className="px-2 py-0.5 rounded-full bg-[#D4AF37]/20 border border-[#D4AF37]/40 text-[#D4AF37] font-bold text-[9px] uppercase tracking-wider flex items-center">
                      <Star className="w-2.5 h-2.5 mr-0.5 fill-current" />
                      Repeat ({visitor.total_visits_count || 2}x)
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70">UUID: {visitor.visitor_uuid}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-gray-400 hover:text-gray-700 dark:hover:text-[#FAFAFA] hover:bg-gray-200 dark:hover:bg-[#3D2519] transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Lifecycle Status Progress Stepper */}
          <div className="mt-5 pt-3 border-t border-gray-200 dark:border-[#D4AF37]/20">
            <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Lifecycle Status Stepper</span>
            <div className="flex items-center justify-between mt-2">
              {LIFECYCLE_STEPS.map((step, idx) => {
                const isPassed = currentStepIdx >= idx;
                const isCurrent = currentStepIdx === idx;
                return (
                  <div key={step} className="flex flex-col items-center flex-1">
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold transition-all ${
                        isCurrent
                          ? 'bg-[#FF9933] text-[#1C1410] ring-4 ring-[#FF9933]/20 shadow-md'
                          : isPassed
                          ? 'bg-[#D4AF37] text-[#1C1410]'
                          : 'bg-gray-200 dark:bg-[#3D2519] text-gray-400'
                      }`}
                    >
                      {idx + 1}
                    </div>
                    <span className={`text-[9px] mt-1 tracking-tight text-center ${isCurrent ? 'text-[#D4AF37] font-bold' : 'text-gray-400'}`}>
                      {step.replace('_', ' ')}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex border-b border-gray-200 dark:border-[#D4AF37]/20 mt-4">
            <button
              onClick={() => setActiveTab('DETAILS')}
              className={`py-2 px-4 text-xs font-semibold border-b-2 transition-colors ${
                activeTab === 'DETAILS' ? 'border-[#D4AF37] text-[#D4AF37]' : 'border-transparent text-gray-500'
              }`}
            >
              Details
            </button>
            <button
              onClick={() => setActiveTab('TIMELINE')}
              className={`py-2 px-4 text-xs font-semibold border-b-2 transition-colors ${
                activeTab === 'TIMELINE' ? 'border-[#D4AF37] text-[#D4AF37]' : 'border-transparent text-gray-500'
              }`}
            >
              Timeline
            </button>
            <button
              onClick={() => setActiveTab('AUDIT')}
              className={`py-2 px-4 text-xs font-semibold border-b-2 transition-colors ${
                activeTab === 'AUDIT' ? 'border-[#D4AF37] text-[#D4AF37]' : 'border-transparent text-gray-500'
              }`}
            >
              Audit Log
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-6 space-y-6 flex-1">
          {activeTab === 'DETAILS' && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3.5 rounded-2xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-100 dark:border-[#D4AF37]/20">
                  <span className="text-[10px] uppercase font-semibold text-gray-500 dark:text-[#FAFAFA]/60">Phone Number</span>
                  <p className="text-xs font-bold mt-1 flex items-center text-gray-800 dark:text-[#FAFAFA]">
                    <Phone className="w-3.5 h-3.5 mr-1.5 text-[#D4AF37]" />
                    {visitor.phone_number}
                  </p>
                </div>

                <div className="p-3.5 rounded-2xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-100 dark:border-[#D4AF37]/20">
                  <span className="text-[10px] uppercase font-semibold text-gray-500 dark:text-[#FAFAFA]/60">Group Size</span>
                  <p className="text-xs font-bold mt-1 flex items-center text-gray-800 dark:text-[#FAFAFA]">
                    <User className="w-3.5 h-3.5 mr-1.5 text-[#D4AF37]" />
                    {visitor.persons_count} Person(s) ({visitor.gender}, {visitor.age} yrs)
                  </p>
                </div>

                <div className="p-3.5 rounded-2xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-100 dark:border-[#D4AF37]/20">
                  <span className="text-[10px] uppercase font-semibold text-gray-500 dark:text-[#FAFAFA]/60">Visit Date & Time</span>
                  <p className="text-xs font-bold mt-1 flex items-center text-gray-800 dark:text-[#FAFAFA]">
                    <Calendar className="w-3.5 h-3.5 mr-1.5 text-[#D4AF37]" />
                    {visitor.visitor_date} at {visitor.visitor_time}
                  </p>
                </div>

                <div className="p-3.5 rounded-2xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-100 dark:border-[#D4AF37]/20">
                  <span className="text-[10px] uppercase font-semibold text-gray-500 dark:text-[#FAFAFA]/60">Lifecycle Status</span>
                  <p className="text-xs font-bold mt-1 flex items-center text-emerald-600 dark:text-emerald-400">
                    <ShieldCheck className="w-3.5 h-3.5 mr-1.5 text-emerald-500" />
                    {visitor.status || 'CHECKED_IN'}
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                <div className="p-4 rounded-2xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-100 dark:border-[#D4AF37]/20 space-y-2">
                  <div className="flex items-center space-x-2 text-xs font-bold text-[#D4AF37]">
                    <HeartHandshake className="w-4 h-4" />
                    <span>Visit Purpose</span>
                  </div>
                  <p className="text-xs text-gray-700 dark:text-[#FAFAFA]/90">
                    {visitor.purpose?.name_en || 'General Darshan'} ({visitor.purpose?.name_te || 'సాధారణ దర్శనం'})
                  </p>
                  {visitor.temple_service && (
                    <p className="text-[11px] text-gray-500 dark:text-[#FAFAFA]/70">Special Seva: {visitor.temple_service}</p>
                  )}
                </div>

                <div className="p-4 rounded-2xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-100 dark:border-[#D4AF37]/20 space-y-2">
                  <div className="flex items-center space-x-2 text-xs font-bold text-[#D4AF37]">
                    <MapPin className="w-4 h-4" />
                    <span>Origin Village / City</span>
                  </div>
                  <p className="text-xs text-gray-700 dark:text-[#FAFAFA]/90">
                    {visitor.village?.name_en || visitor.village_name_custom || 'Local Region'}
                  </p>
                </div>
              </div>

              {/* QR Code Pass Display */}
              {showQR && (
                <div className="p-6 rounded-3xl bg-white dark:bg-[#2C1A11] border border-[#D4AF37] text-center space-y-4 shadow-xl animate-fadeIn">
                  <div className="w-40 h-40 bg-gray-900 text-white rounded-2xl mx-auto flex items-center justify-center p-3 font-mono text-[10px] shadow-inner">
                    <div className="border-4 border-white p-2 w-full h-full flex items-center justify-center text-center">
                      [ QR PASS ]
                      <br />
                      {visitor.visitor_uuid.substring(0, 8)}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-[#D4AF37]">Token Pass: {visitor.visitor_uuid.substring(0, 8)}</h4>
                    <p className="text-[11px] text-gray-500 dark:text-[#FAFAFA]/70">Gate Fast-Track Entry QR Token</p>
                  </div>
                </div>
              )}
            </>
          )}

          {activeTab === 'TIMELINE' && (
            <div className="space-y-4">
              <h4 className="text-xs font-bold text-[#D4AF37] uppercase tracking-wider">Chronological Event Timeline</h4>
              <div className="space-y-3 relative pl-4 border-l-2 border-[#D4AF37]/30">
                <div className="relative">
                  <div className="w-3 h-3 rounded-full bg-[#D4AF37] absolute -left-[23px] top-1"></div>
                  <p className="text-xs font-bold text-gray-800 dark:text-[#FAFAFA]">Registered & Token Generated</p>
                  <p className="text-[10px] text-gray-400">{visitor.visitor_date} at {visitor.visitor_time} • Volunteer</p>
                </div>
                <div className="relative">
                  <div className="w-3 h-3 rounded-full bg-[#FF9933] absolute -left-[23px] top-1"></div>
                  <p className="text-xs font-bold text-gray-800 dark:text-[#FAFAFA]">Gate Check-In Verified</p>
                  <p className="text-[10px] text-gray-400">{visitor.visitor_date} • Gate 1 Scanner</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'AUDIT' && (
            <div className="space-y-4">
              <h4 className="text-xs font-bold text-[#D4AF37] uppercase tracking-wider">Immutable Audit Trail</h4>
              <div className="p-3.5 rounded-2xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-100 dark:border-[#D4AF37]/20 space-y-1 text-xs">
                <div className="flex items-center justify-between font-mono text-[11px] text-gray-500">
                  <span>ACTION: CREATE_VISITOR</span>
                  <span>{visitor.visitor_date}</span>
                </div>
                <p className="text-gray-700 dark:text-[#FAFAFA]">User: admin@kalkiseva.org (IP: 127.0.0.1)</p>
                <div className="p-2 rounded-lg bg-gray-100 dark:bg-[#1C1410] font-mono text-[10px] text-emerald-600 dark:text-emerald-400 overflow-x-auto">
                  + status: "REGISTERED" $\rightarrow$ "SYNCED"
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-6 border-t border-gray-200 dark:border-[#D4AF37]/20 bg-gray-50 dark:bg-[#2C1A11] flex items-center space-x-3">
          <button
            onClick={() => setShowQR(!showQR)}
            className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold text-xs shadow-md hover:brightness-110 transition-all flex items-center justify-center space-x-1.5"
          >
            <QrCode className="w-4 h-4" />
            <span>{showQR ? 'Hide Pass' : 'Show Digital Pass'}</span>
          </button>
          <button
            onClick={() => window.print()}
            className="px-4 py-2.5 rounded-xl bg-gray-200 dark:bg-[#3D2519] text-gray-800 dark:text-[#FAFAFA] font-semibold text-xs hover:bg-gray-300 dark:hover:bg-[#4D3223] transition-colors flex items-center space-x-1.5"
          >
            <Printer className="w-4 h-4 text-[#D4AF37]" />
            <span>Print Pass</span>
          </button>
        </div>
      </div>
    </div>
  );
}
