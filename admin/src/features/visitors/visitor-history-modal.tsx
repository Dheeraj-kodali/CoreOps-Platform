'use client';

import React, { useState } from 'react';
import { X, Search, History, Calendar, Star, Clock, User } from 'lucide-react';
import { VisitorRepository } from '../../repositories/visitor-repository';
import { Visitor } from '../../types/visitor';

interface VisitorHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function VisitorHistoryModal({ isOpen, onClose }: VisitorHistoryModalProps) {
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [historyList, setHistoryList] = useState<Visitor[] | null>(null);

  if (!isOpen) return null;

  const handleSearchHistory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phone) return;
    setLoading(true);
    try {
      const res = await VisitorRepository.getVisitors({ search: phone });
      setHistoryList(res.items || []);
    } catch {
      setHistoryList([]);
    } finally {
      setLoading(false);
    }
  };

  const totalVisits = historyList?.length || 0;
  const isRepeat = totalVisits > 1;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
      <div className="max-w-lg w-full bg-white dark:bg-[#1C1410] text-[#1C1410] dark:text-[#FAFAFA] rounded-3xl shadow-2xl border border-[#D4AF37]/40 p-6 space-y-5 relative max-h-[85vh] flex flex-col">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 dark:hover:text-[#FAFAFA]">
          <X className="w-5 h-5" />
        </button>

        <div>
          <div className="flex items-center space-x-2 text-[#D4AF37]">
            <History className="w-5 h-5" />
            <h3 className="text-lg font-bold font-serif">Visitor Check-in History</h3>
          </div>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70 mt-1">
            Search by phone number to display historical visit frequency, repeat badges, and audit timelines.
          </p>
        </div>

        {/* Search Input */}
        <form onSubmit={handleSearchHistory} className="space-y-3">
          <div className="relative">
            <input
              type="text"
              required
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="Enter phone number (e.g. 9876543210)..."
              className="w-full pl-4 pr-10 py-2.5 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
            <button type="submit" disabled={loading} className="absolute right-2 top-1/2 -translate-y-1/2 text-[#D4AF37] p-1">
              <Search className="w-4 h-4" />
            </button>
          </div>
        </form>

        {/* History Results List */}
        {historyList && (
          <div className="flex-1 overflow-y-auto space-y-3 pr-1">
            {/* Header Badge */}
            <div className="p-3.5 rounded-2xl bg-[#D4AF37]/10 border border-[#D4AF37]/30 flex items-center justify-between">
              <div>
                <span className="text-[10px] uppercase font-bold text-gray-500 dark:text-[#FAFAFA]/60">Total Historical Visits</span>
                <p className="text-lg font-bold text-[#D4AF37] font-serif">{totalVisits} Visit(s)</p>
              </div>
              {isRepeat && (
                <div className="flex items-center space-x-1 px-3 py-1 rounded-full bg-[#FF9933]/20 border border-[#FF9933]/40 text-[#FF9933] font-bold text-xs">
                  <Star className="w-3.5 h-3.5 fill-current" />
                  <span>Repeat Visitor</span>
                </div>
              )}
            </div>

            {historyList.length === 0 ? (
              <p className="text-xs text-center py-6 text-gray-500">No visit history found for this phone number.</p>
            ) : (
              historyList.map((item, idx) => (
                <div key={item.id || idx} className="p-3.5 rounded-2xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-100 dark:border-[#D4AF37]/20 space-y-1 text-xs">
                  <div className="flex items-center justify-between font-semibold">
                    <span className="flex items-center text-gray-800 dark:text-[#FAFAFA]">
                      <Calendar className="w-3.5 h-3.5 mr-1.5 text-[#D4AF37]" />
                      {item.visitor_date} at {item.visitor_time}
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 text-[10px]">
                      {item.status || 'SYNCED'}
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-500 dark:text-[#FAFAFA]/70">
                    Purpose: {item.purpose?.name_en || 'General Darshan'} | Group: {item.persons_count} Person(s)
                  </p>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
