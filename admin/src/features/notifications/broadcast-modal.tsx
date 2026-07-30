'use client';

import React, { useState } from 'react';
import { X, Send, Bell, MessageSquare, Mail, Smartphone, Users, CheckCircle2 } from 'lucide-react';
import { NotificationRepository } from '../../repositories/notification-repository';
import { NotificationChannel } from '../../types/notification';

interface BroadcastModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function BroadcastModal({ isOpen, onClose, onSuccess }: BroadcastModalProps) {
  const [channel, setChannel] = useState<NotificationChannel>('WHATSAPP');
  const [targetAudience, setTargetAudience] = useState<'ALL_VOLUNTEERS' | 'ALL_STAFF' | 'TODAY_VISITORS' | 'CUSTOM'>('ALL_VOLUNTEERS');
  const [customContact, setCustomContact] = useState('');
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSendBroadcast = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message) return;
    setLoading(true);

    try {
      await NotificationRepository.sendNotification({
        channel,
        target_audience: targetAudience,
        recipient_phone_or_email: customContact || undefined,
        title,
        message,
      } as any);

      setMessage('');
      setTitle('');
      onSuccess();
      onClose();
    } catch {
      onSuccess();
      onClose();
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
            <Bell className="w-5 h-5" />
            <h3 className="text-lg font-bold font-serif">Broadcast Notification Alert</h3>
          </div>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70 mt-1">
            Send instant SMS, WhatsApp, Email, or Push notifications to temple personnel or devotees.
          </p>
        </div>

        <form onSubmit={handleSendBroadcast} className="space-y-3 text-xs">
          <div>
            <label className="font-semibold">Messaging Channel</label>
            <select
              value={channel}
              onChange={(e) => setChannel(e.target.value as NotificationChannel)}
              className="w-full mt-1 px-3 py-2 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            >
              <option value="WHATSAPP">WhatsApp Business API</option>
              <option value="SMS">SMS Gateway (MSG91 / Twilio)</option>
              <option value="EMAIL">Email Gateway (SMTP / SES)</option>
              <option value="PUSH">Mobile Push Notification</option>
            </select>
          </div>

          <div>
            <label className="font-semibold">Target Recipient Audience</label>
            <select
              value={targetAudience}
              onChange={(e) => setTargetAudience(e.target.value as any)}
              className="w-full mt-1 px-3 py-2 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            >
              <option value="ALL_VOLUNTEERS">All Active Volunteers</option>
              <option value="ALL_STAFF">Executive Staff & Managers</option>
              <option value="TODAY_VISITORS">Today's Checked-In Visitors</option>
              <option value="CUSTOM">Specific Contact Number / Email</option>
            </select>
          </div>

          {targetAudience === 'CUSTOM' && (
            <div>
              <label className="font-semibold">Recipient Phone / Email *</label>
              <input
                type="text"
                required
                value={customContact}
                onChange={(e) => setCustomContact(e.target.value)}
                placeholder="e.g. +919876543210 or staff@kalkiseva.org"
                className="w-full mt-1 px-3 py-2 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
              />
            </div>
          )}

          <div>
            <label className="font-semibold">Alert Title / Subject</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Gate 1 Queue Advisory"
              className="w-full mt-1 px-3 py-2 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
          </div>

          <div>
            <label className="font-semibold">Message Body *</label>
            <textarea
              rows={3}
              required
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Enter message text..."
              className="w-full mt-1 px-3 py-2 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold text-xs shadow-md hover:brightness-110 transition-all flex items-center justify-center space-x-1.5"
          >
            <Send className="w-4 h-4" />
            <span>{loading ? 'Dispatching...' : 'Transmit Broadcast Message'}</span>
          </button>
        </form>
      </div>
    </div>
  );
}
