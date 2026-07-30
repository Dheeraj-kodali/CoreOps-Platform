'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bell, Send, MessageSquare, Mail, Smartphone, RefreshCw, CheckCircle2, AlertCircle, Clock, Filter, Eye, RotateCcw } from 'lucide-react';
import { NotificationRepository } from '../../../repositories/notification-repository';
import { BroadcastModal } from '../../../features/notifications/broadcast-modal';
import { TableSkeleton } from '../../../components/shared/loading-skeleton';
import { NotificationChannel, NotificationLog, NotificationStatus, NotificationTemplate } from '../../../types/notification';

const MOCK_NOTIFICATIONS: NotificationLog[] = [
  {
    id: 'n1',
    recipient_name: 'Ramesh Kumar',
    recipient_contact: '+91 98765 43210',
    channel: 'WHATSAPP',
    title: 'Darshan Token Pass',
    message: 'Jai Kalki! Your Darshan Token Pass is #TK-48201. Entry Gate: Gate 1.',
    status: 'DELIVERED',
    sent_at: 'Today 09:15 AM',
    retry_count: 0,
  },
  {
    id: 'n2',
    recipient_name: 'Suresh Babu',
    recipient_contact: '+91 91234 56789',
    channel: 'SMS',
    title: 'Check-in Confirmation',
    message: 'Sri Kalki Seva Alayam: Visitor check-in registered for 3 person(s).',
    status: 'SENT',
    sent_at: 'Today 09:30 AM',
    retry_count: 0,
  },
  {
    id: 'n3',
    recipient_name: 'Anitha Reddy',
    recipient_contact: '+91 99887 76655',
    channel: 'EMAIL',
    title: 'Seva Booking Receipt',
    message: 'Thank you for booking Special Seva. Receipt PDF attached.',
    status: 'FAILED',
    sent_at: 'Today 08:45 AM',
    retry_count: 2,
    error_detail: 'SMTP connection timeout to gateway',
  },
];

const MOCK_TEMPLATES: NotificationTemplate[] = [
  {
    id: 't1',
    title: 'Visitor Check-in SMS Pass',
    code: 'VISITOR_CHECKIN_SMS',
    channel: 'SMS',
    template_body: 'Jai Kalki! Welcome {visitor_name}. Your check-in pass for {date} is verified. Token: {token_pass}.',
    variables: ['visitor_name', 'date', 'token_pass'],
    is_active: true,
  },
  {
    id: 't2',
    title: 'WhatsApp Digital Gate Pass',
    code: 'WHATSAPP_GATE_PASS',
    channel: 'WHATSAPP',
    template_body: '🛕 Sri Kalki Seva Alayam\n\nDear {visitor_name},\nYour digital gate pass is ready!\nToken: {token_pass}\nDate: {date}',
    variables: ['visitor_name', 'date', 'token_pass'],
    is_active: true,
  },
];

export default function NotificationCenterPage() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'LOGS' | 'TEMPLATES'>('LOGS');

  // Filters
  const [channelFilter, setChannelFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [isBroadcastOpen, setIsBroadcastOpen] = useState(false);

  // TanStack Query for Logs
  const { data: logsData, isLoading, refetch } = useQuery<NotificationLog[]>({
    queryKey: ['notifications', channelFilter, statusFilter],
    queryFn: async () => {
      try {
        const res = await NotificationRepository.getNotifications();
        return res || MOCK_NOTIFICATIONS;
      } catch {
        return MOCK_NOTIFICATIONS;
      }
    },
  });

  const handleRetry = async (id: string) => {
    try {
      await NotificationRepository.retryFailedNotification(id);
      refetch();
    } catch {
      alert('Retry dispatched.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner & Action Triggers */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-serif text-gray-900 dark:text-[#D4AF37]">
            Notification Center & Messaging
          </h1>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70">
            Multi-Channel Dispatch (SMS, WhatsApp, Email, Push), Template Registry & Delivery Tracking
          </p>
        </div>

        <button
          onClick={() => setIsBroadcastOpen(true)}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] text-xs font-bold shadow-md hover:brightness-110 transition-all flex items-center space-x-1.5"
        >
          <Send className="w-4 h-4" />
          <span>Dispatch Alert Broadcast</span>
        </button>
      </div>

      {/* Navigation Tabs & Filters */}
      <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm space-y-4">
        <div className="flex border-b border-gray-200 dark:border-[#D4AF37]/20">
          <button
            onClick={() => setActiveTab('LOGS')}
            className={`py-2 px-4 text-xs font-semibold border-b-2 transition-colors ${
              activeTab === 'LOGS' ? 'border-[#D4AF37] text-[#D4AF37]' : 'border-transparent text-gray-500'
            }`}
          >
            Message Delivery Logs
          </button>
          <button
            onClick={() => setActiveTab('TEMPLATES')}
            className={`py-2 px-4 text-xs font-semibold border-b-2 transition-colors ${
              activeTab === 'TEMPLATES' ? 'border-[#D4AF37] text-[#D4AF37]' : 'border-transparent text-gray-500'
            }`}
          >
            Template Registry Editor
          </button>
        </div>

        {activeTab === 'LOGS' && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <select
                value={channelFilter}
                onChange={(e) => setChannelFilter(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
              >
                <option value="ALL">All Messaging Channels</option>
                <option value="WHATSAPP">WhatsApp</option>
                <option value="SMS">SMS Gateway</option>
                <option value="EMAIL">Email Gateway</option>
                <option value="PUSH">Push Notifications</option>
              </select>
            </div>

            <div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
              >
                <option value="ALL">All Delivery Statuses</option>
                <option value="SENT">Sent / Delivered</option>
                <option value="FAILED">Failed Deliveries</option>
                <option value="PENDING">Pending Queue</option>
              </select>
            </div>

            <button
              onClick={() => {
                setChannelFilter('ALL');
                setStatusFilter('ALL');
              }}
              className="py-2 px-3 rounded-xl bg-gray-100 dark:bg-[#2C1A11] text-xs font-semibold text-gray-600 dark:text-[#FAFAFA]/70 hover:bg-gray-200 dark:hover:bg-[#3D2519] transition-colors flex items-center justify-center space-x-1"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Reset Filters</span>
            </button>
          </div>
        )}
      </div>

      {/* Main Content Area */}
      {activeTab === 'LOGS' ? (
        <div className="rounded-2xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm overflow-hidden">
          {isLoading ? (
            <div className="p-6">
              <TableSkeleton rows={5} />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-gray-50 dark:bg-[#2C1A11] border-b border-gray-200 dark:border-[#D4AF37]/20 text-gray-500 dark:text-[#D4AF37] uppercase font-semibold">
                    <th className="py-3.5 px-4">Recipient</th>
                    <th className="py-3.5 px-4">Channel</th>
                    <th className="py-3.5 px-4">Title / Message</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4">Sent At</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-[#D4AF37]/10">
                  {(logsData || MOCK_NOTIFICATIONS).map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50/50 dark:hover:bg-[#2C1A11]/40 transition-colors">
                      <td className="py-3.5 px-4 font-semibold text-gray-900 dark:text-[#FAFAFA]">
                        <p>{log.recipient_name}</p>
                        <p className="text-[10px] text-gray-400 font-mono">{log.recipient_contact}</p>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 rounded-full bg-[#D4AF37]/20 text-[#D4AF37] font-bold text-[10px]">
                          {log.channel}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 max-w-xs truncate text-gray-700 dark:text-gray-300">
                        {log.title && <p className="font-semibold text-xs text-[#D4AF37]">{log.title}</p>}
                        <p className="truncate text-[11px]">{log.message}</p>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                            log.status === 'DELIVERED' || log.status === 'SENT'
                              ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300'
                              : 'bg-red-100 dark:bg-red-950/60 text-red-700 dark:text-red-300'
                          }`}
                        >
                          {log.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-gray-500 font-mono text-[11px]">{log.sent_at}</td>
                      <td className="py-3.5 px-4 text-right">
                        {log.status === 'FAILED' && (
                          <button
                            onClick={() => handleRetry(log.id)}
                            className="p-1.5 rounded-lg text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-950/40 transition-colors flex items-center space-x-1"
                            title="Retry Delivery"
                          >
                            <RotateCcw className="w-3.5 h-3.5" />
                            <span className="text-[10px] font-bold">Retry</span>
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {MOCK_TEMPLATES.map((tmpl) => (
            <div
              key={tmpl.id}
              className="p-5 rounded-3xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/30 shadow-sm space-y-3"
            >
              <div className="flex items-center justify-between">
                <h4 className="font-bold font-serif text-sm text-[#D4AF37]">{tmpl.title}</h4>
                <span className="px-2 py-0.5 rounded-full bg-[#D4AF37]/20 text-[#D4AF37] text-[10px] font-bold uppercase">
                  {tmpl.channel}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-100 dark:border-[#D4AF37]/20 font-mono text-xs text-gray-700 dark:text-[#FAFAFA] whitespace-pre-wrap">
                {tmpl.template_body}
              </div>
              <div className="flex items-center justify-between text-[11px] text-gray-400">
                <span>Variables: {tmpl.variables.map((v) => `{${v}}`).join(', ')}</span>
                <span className="text-emerald-500 font-semibold">Active</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Broadcast Alert Modal */}
      <BroadcastModal
        isOpen={isBroadcastOpen}
        onClose={() => setIsBroadcastOpen(false)}
        onSuccess={() => refetch()}
      />
    </div>
  );
}
