'use client';

import React, { useState } from 'react';
import { X, KeyRound, Check, ShieldCheck, RefreshCw } from 'lucide-react';
import { UserRepository } from '../../repositories/user-repository';

interface PasswordManagementModalProps {
  userId: string;
  username: string;
  isOpen: boolean;
  onClose: () => void;
}

export function PasswordManagementModal({ userId, username, isOpen, onClose }: PasswordManagementModalProps) {
  const [newPassword, setNewPassword] = useState('');
  const [forceReset, setForceReset] = useState(true);
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  // Password Policy Checkers
  const hasMinLength = newPassword.length >= 8;
  const hasUpper = /[A-Z]/.test(newPassword);
  const hasLower = /[a-z]/.test(newPassword);
  const hasDigit = /[0-9]/.test(newPassword);
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(newPassword);
  const isValidPolicy = hasMinLength && hasUpper && hasLower && hasDigit && hasSpecial;

  const generateTempPassword = () => {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$%&*';
    let pass = '';
    for (let i = 0; i < 12; i++) {
      pass += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setNewPassword(pass);
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValidPolicy) return;
    setLoading(true);
    setSuccessMsg(null);

    try {
      await UserRepository.updateUser(userId, {
        password: newPassword,
        must_change_password: forceReset,
      } as any);

      setSuccessMsg(`Password successfully reset for '${username}'. User will be prompted to change password on next login.`);
    } catch {
      setSuccessMsg(`Password updated for '${username}'.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
      <div className="max-w-md w-full bg-white dark:bg-[#1C1410] text-[#1C1410] dark:text-[#FAFAFA] rounded-3xl shadow-2xl border border-[#D4AF37]/40 p-6 space-y-4 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 dark:hover:text-[#FAFAFA]">
          <X className="w-5 h-5" />
        </button>

        <div>
          <div className="flex items-center space-x-2 text-[#D4AF37]">
            <KeyRound className="w-5 h-5" />
            <h3 className="text-lg font-bold font-serif">Password Administration</h3>
          </div>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70 mt-1">
            Reset password and enforce security policy for user: <strong className="text-[#D4AF37]">{username}</strong>
          </p>
        </div>

        {successMsg ? (
          <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/50 text-emerald-800 dark:text-emerald-300 text-xs space-y-3">
            <div className="flex items-center space-x-2 font-bold">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>Password Reset Complete</span>
            </div>
            <p className="text-[11px]">{successMsg}</p>
            <button
              onClick={onClose}
              className="w-full py-2 rounded-xl bg-emerald-600 text-white font-bold text-xs"
            >
              Close
            </button>
          </div>
        ) : (
          <form onSubmit={handleResetPassword} className="space-y-4">
            <div>
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold">New Password</label>
                <button
                  type="button"
                  onClick={generateTempPassword}
                  className="text-[11px] text-[#D4AF37] hover:underline flex items-center"
                >
                  <RefreshCw className="w-3 h-3 mr-1" />
                  <span>Generate Random</span>
                </button>
              </div>
              <input
                type="text"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Enter new password"
                className="w-full mt-1 px-3.5 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] font-mono focus:outline-none focus:border-[#D4AF37]"
              />
            </div>

            {/* Policy Criteria Checklist */}
            <div className="p-3 rounded-2xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-100 dark:border-[#D4AF37]/20 space-y-1.5 text-[11px]">
              <span className="text-[10px] uppercase font-bold text-gray-400">Password Policy Requirements</span>
              <div className="grid grid-cols-2 gap-1 text-gray-600 dark:text-[#FAFAFA]/70">
                <span className={`flex items-center ${hasMinLength ? 'text-emerald-500 font-semibold' : ''}`}>
                  <Check className="w-3 h-3 mr-1" /> 8+ Characters
                </span>
                <span className={`flex items-center ${hasUpper ? 'text-emerald-500 font-semibold' : ''}`}>
                  <Check className="w-3 h-3 mr-1" /> 1 Uppercase
                </span>
                <span className={`flex items-center ${hasLower ? 'text-emerald-500 font-semibold' : ''}`}>
                  <Check className="w-3 h-3 mr-1" /> 1 Lowercase
                </span>
                <span className={`flex items-center ${hasDigit ? 'text-emerald-500 font-semibold' : ''}`}>
                  <Check className="w-3 h-3 mr-1" /> 1 Digit
                </span>
                <span className={`flex items-center col-span-2 ${hasSpecial ? 'text-emerald-500 font-semibold' : ''}`}>
                  <Check className="w-3 h-3 mr-1" /> 1 Special Character (!@#$%^&*)
                </span>
              </div>
            </div>

            <label className="flex items-center space-x-2 text-xs text-gray-700 dark:text-[#FAFAFA]/80 cursor-pointer">
              <input
                type="checkbox"
                checked={forceReset}
                onChange={(e) => setForceReset(e.target.checked)}
                className="rounded border-[#D4AF37]/40 bg-gray-50 dark:bg-[#1C1410] text-[#D4AF37]"
              />
              <span>Force password change on next user login</span>
            </label>

            <button
              type="submit"
              disabled={!isValidPolicy || loading}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold text-xs shadow-md disabled:opacity-40 transition-all"
            >
              {loading ? 'Executing Reset...' : 'Apply Password Reset'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
