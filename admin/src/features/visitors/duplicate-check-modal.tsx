'use client';

import React, { useState } from 'react';
import { X, Search, AlertCircle, CheckCircle2 } from 'lucide-react';
import { VisitorRepository } from '../../repositories/visitor-repository';
import { Visitor } from '../../types/visitor';

interface DuplicateCheckModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function DuplicateCheckModal({ isOpen, onClose }: DuplicateCheckModalProps) {
  const [name, setName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [visitorDate, setVisitorDate] = useState(new Date().toISOString().split('T')[0]);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ checked: boolean; is_duplicate: boolean; existing_record?: Visitor } | null>(null);

  if (!isOpen) return null;

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !phoneNumber || !visitorDate) return;

    setLoading(true);
    setResult(null);
    try {
      const res = await VisitorRepository.checkDuplicate(name, phoneNumber, visitorDate);
      setResult({ checked: true, is_duplicate: res.is_duplicate, existing_record: res.existing_record });
    } catch {
      setResult({ checked: true, is_duplicate: false });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
      <div className="max-w-md w-full bg-white dark:bg-[#1C1410] text-[#1C1410] dark:text-[#FAFAFA] rounded-3xl shadow-2xl border border-[#D4AF37]/40 p-6 space-y-5 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 dark:hover:text-[#FAFAFA]"
        >
          <X className="w-5 h-5" />
        </button>

        <div>
          <h3 className="text-lg font-bold font-serif text-[#D4AF37]">Visitor Duplicate Check</h3>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70 mt-1">
            Verify if a visitor has already checked in on the selected date to prevent double counting.
          </p>
        </div>

        <form onSubmit={handleCheck} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-gray-700 dark:text-[#FAFAFA]/90">Visitor Name</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Ramesh Kumar"
              className="w-full mt-1 px-3.5 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-gray-700 dark:text-[#FAFAFA]/90">Phone Number</label>
            <input
              type="text"
              required
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="e.g. 9876543210"
              className="w-full mt-1 px-3.5 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-gray-700 dark:text-[#FAFAFA]/90">Visitor Date</label>
            <input
              type="date"
              required
              value={visitorDate}
              onChange={(e) => setVisitorDate(e.target.value)}
              className="w-full mt-1 px-3.5 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold text-xs shadow-md hover:brightness-110 transition-all flex items-center justify-center space-x-1.5"
          >
            <Search className="w-4 h-4" />
            <span>{loading ? 'Searching Database...' : 'Execute Duplicate Check'}</span>
          </button>
        </form>

        {/* Results Presentation */}
        {result?.checked && (
          <div className="pt-2">
            {result.is_duplicate ? (
              <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/50 text-amber-800 dark:text-amber-300 text-xs space-y-1">
                <div className="flex items-center font-bold space-x-1.5">
                  <AlertCircle className="w-4 h-4 text-amber-600" />
                  <span>Matching Duplicate Record Found!</span>
                </div>
                <p className="text-[11px] mt-1">
                  Visitor <span className="font-semibold">{result.existing_record?.name || name}</span> checked in on {visitorDate}.
                </p>
              </div>
            ) : (
              <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/50 text-emerald-800 dark:text-emerald-300 text-xs space-y-1">
                <div className="flex items-center font-bold space-x-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span>No Duplicate Found</span>
                </div>
                <p className="text-[11px] mt-1">This visitor has not checked in on {visitorDate}. Safe to register.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
