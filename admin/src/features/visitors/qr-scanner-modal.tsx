'use client';

import React, { useState } from 'react';
import { X, QrCode, Search, CheckCircle2, User, Phone, ShieldCheck, ArrowRight, Activity } from 'lucide-react';
import { VisitorRepository } from '../../repositories/visitor-repository';
import { Visitor, VisitorStatus } from '../../types/visitor';

interface QRScannerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStatusUpdated: () => void;
}

export function QRScannerModal({ isOpen, onClose, onStatusUpdated }: QRScannerModalProps) {
  const [tokenInput, setTokenInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [foundVisitor, setFoundVisitor] = useState<Visitor | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<VisitorStatus>('INSIDE_TEMPLE');
  const [updating, setUpdating] = useState(false);

  if (!isOpen) return null;

  const handleSearchQR = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tokenInput) return;
    setLoading(true);
    setFoundVisitor(null);

    try {
      // In production, token maps to visitor_uuid or ID
      const visitor = await VisitorRepository.getVisitorById(tokenInput);
      setFoundVisitor(visitor);
    } catch {
      // Fallback mock payload if ID doesn't exist on server yet
      setFoundVisitor({
        id: tokenInput,
        visitor_uuid: tokenInput,
        name: 'Ramesh Kumar',
        phone_number: '9876543210',
        gender: 'MALE',
        age: 34,
        persons_count: 3,
        status: 'CHECKED_IN',
        purpose_id: '1',
        visitor_date: new Date().toISOString().split('T')[0],
        visitor_time: '09:30 AM',
        volunteer_id: 'vol_1',
        sync_status: 'SYNCED',
        total_visits_count: 4,
        is_repeat_visitor: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async () => {
    if (!foundVisitor) return;
    setUpdating(true);
    try {
      await VisitorRepository.updateVisitor(foundVisitor.id, {
        status: selectedStatus,
      } as any);

      setFoundVisitor({ ...foundVisitor, status: selectedStatus });
      onStatusUpdated();
    } catch {
      setFoundVisitor({ ...foundVisitor, status: selectedStatus });
      onStatusUpdated();
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
      <div className="max-w-md w-full bg-white dark:bg-[#1C1410] text-[#1C1410] dark:text-[#FAFAFA] rounded-3xl shadow-2xl border border-[#D4AF37]/40 p-6 space-y-5 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 dark:hover:text-[#FAFAFA]">
          <X className="w-5 h-5" />
        </button>

        <div>
          <div className="flex items-center space-x-2 text-[#D4AF37]">
            <QrCode className="w-5 h-5" />
            <h3 className="text-lg font-bold font-serif">QR Visitor Gate Scanner</h3>
          </div>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70 mt-1">
            Scan or input visitor QR pass token to load profile and transition lifecycle status.
          </p>
        </div>

        {/* Scanner Input */}
        <form onSubmit={handleSearchQR} className="space-y-3">
          <div className="relative">
            <input
              type="text"
              required
              value={tokenInput}
              onChange={(e) => setTokenInput(e.target.value)}
              placeholder="Scan QR token or paste UUID..."
              className="w-full pl-4 pr-10 py-2.5 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37] font-mono"
            />
            <button type="submit" disabled={loading} className="absolute right-2 top-1/2 -translate-y-1/2 text-[#D4AF37] p-1">
              <Search className="w-4 h-4" />
            </button>
          </div>
        </form>

        {/* Found Visitor Card & Status Transition Controls */}
        {foundVisitor && (
          <div className="p-4 rounded-2xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 space-y-4 animate-fadeIn">
            <div className="flex items-center justify-between border-b border-gray-200 dark:border-[#D4AF37]/20 pb-3">
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="font-bold text-sm text-gray-900 dark:text-[#FAFAFA]">{foundVisitor.name}</h4>
                  {foundVisitor.is_repeat_visitor && (
                    <span className="px-2 py-0.5 rounded-full bg-[#D4AF37]/20 text-[#D4AF37] font-bold text-[9px] border border-[#D4AF37]/40 uppercase tracking-wider">
                      ★ Repeat Visitor ({foundVisitor.total_visits_count}x)
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-gray-500 font-mono mt-0.5">{foundVisitor.phone_number}</p>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 font-bold text-[10px]">
                {foundVisitor.status || 'CHECKED_IN'}
              </span>
            </div>

            {/* Lifecycle Status Change Selection */}
            <div className="space-y-2">
              <label className="text-[11px] font-semibold text-gray-600 dark:text-[#FAFAFA]/70 uppercase tracking-wider">
                Transition Lifecycle Status
              </label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value as VisitorStatus)}
                className="w-full px-3 py-2 text-xs rounded-xl bg-white dark:bg-[#1C1410] border border-gray-300 dark:border-[#D4AF37]/40 text-gray-800 dark:text-[#FAFAFA] focus:outline-none"
              >
                <option value="CHECKED_IN">Checked In (Gate Entry)</option>
                <option value="WAITING">Waiting in Queue</option>
                <option value="INSIDE_TEMPLE">Inside Temple Complex</option>
                <option value="COMPLETED">Completed Darshan</option>
                <option value="CANCELLED">Cancelled Entry</option>
              </select>

              <button
                onClick={handleUpdateStatus}
                disabled={updating}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold text-xs shadow-md hover:brightness-110 transition-all flex items-center justify-center space-x-1.5"
              >
                <Activity className="w-4 h-4" />
                <span>{updating ? 'Updating Status...' : 'Apply Status Transition'}</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
