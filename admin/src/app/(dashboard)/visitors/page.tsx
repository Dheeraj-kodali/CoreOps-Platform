'use client';

import React, { useState, useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-[#D4AF37]';
import { Search, Download, Eye, Calendar, RefreshCw, LogOut, MapPin, Edit, CheckCircle2, Lock, PieChart } from 'lucide-react';
import { TableSkeleton } from '../../../components/shared/loading-skeleton';
import { VisitorDetailsDrawer } from '../../../features/visitors/visitor-details-drawer';
import { apiClient } from '../../../api/client';

export default function VisitorManagementPage() {
  const queryClient = useQueryClient();

  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState('TODAY');
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [volunteerFilter, setVolunteerFilter] = useState<string>('ALL');

  const [selectedVisitor, setSelectedVisitor] = useState<any | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [editProfileRecord, setEditProfileRecord] = useState<any | null>(null);
  const [editFormData, setEditFormData] = useState({
    name: '',
    phone_number: '',
    village_name_custom: '',
    gender: 'MALE',
    age: 30,
  });

  const apiDates = useMemo(() => {
    const todayStr = new Date().toISOString().split('T')[0];
    if (dateFilter === 'TODAY') {
      return { date_from: todayStr, date_to: todayStr };
    } else if (dateFilter === 'YESTERDAY') {
      const yest = new Date();
      yest.setDate(yest.getDate() - 1);
      const yestStr = yest.toISOString().split('T')[0];
      return { date_from: yestStr, date_to: yestStr };
    } else if (dateFilter === '7DAYS') {
      const d7 = new Date();
      d7.setDate(d7.getDate() - 7);
      return { date_from: d7.toISOString().split('T')[0] };
    } else if (dateFilter === 'MONTH') {
      const d30 = new Date();
      d30.setDate(d30.getDate() - 30);
      return { date_from: d30.toISOString().split('T')[0] };
    } else if (dateFilter === 'CUSTOM' && customStartDate) {
      return { date_from: customStartDate, date_to: customEndDate || undefined };
    }
    return {};
  }, [dateFilter, customStartDate, customEndDate]);

  // Query Daily Ledgers API
  const { data: ledgerData, isLoading, isError, refetch } = useQuery({
    queryKey: ['daily-ledgers', searchTerm, apiDates, statusFilter],
    queryFn: async () => {
      let url = `/visitors/ledgers?limit=50`;
      if (apiDates.date_from) url += `&date_from=${apiDates.date_from}`;
      if (apiDates.date_to) url += `&date_to=${apiDates.date_to}`;
      if (statusFilter !== 'ALL') url += `&status=${statusFilter}`;
      if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;

      const res = await apiClient.get(url);
      return res.data;
    },
  });

  const ledgers = ledgerData?.items || [];

  const handleCheckout = async (id: string) => {
    if (confirm('Checkout visitor session?')) {
      try {
        await apiClient.post(`/visitors/${id}/checkout`, {});
        refetch();
      } catch (err) {
        alert('Failed to checkout.');
      }
    }
  };

  const handleSaveProfileEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editProfileRecord) return;
    try {
      const profileId = editProfileRecord.visitor_profile_id || editProfileRecord.id;
      await apiClient.put(`/visitors/profiles/${profileId}`, editFormData).catch(async () => {
        return await apiClient.put(`/visitors/${editProfileRecord.id}`, editFormData);
      });
      setEditProfileRecord(null);
      refetch();
    } catch (err) {
      alert('Failed to update profile.');
    }
  };

  const exportCSV = () => {
    const headers = 'Ledger Date,Session ID,Visitor Name,Phone,Persons Count,Purpose,Check-In,Check-Out,Duration,Status,Volunteer,Sync State,GPS,Read-Only\n';
    const rows: string[][] = [];

    ledgers.forEach((l: any) => {
      l.sessions.forEach((s: any) => {
        rows.push([
          l.date,
          s.id || s.visitor_uuid,
          s.name,
          s.phone_number || s.phone || '',
          (s.persons_count || 1).toString(),
          s.purpose?.name_en || s.purpose_name || 'General Darshan',
          s.check_in_time || s.visitor_time || '',
          s.check_out_time || (s.status === 'AUTO_CLOSED' ? '23:59:59 (Auto)' : 'N/A'),
          s.duration || 'Completed',
          s.status || 'INSIDE',
          s.volunteer_id || 'admin',
          s.sync_status || 'SYNCED',
          s.latitude ? 'YES' : 'NO',
          l.summary?.is_read_only ? 'YES' : 'NO',
        ]);
      });
    });

    const blob = new Blob([headers + rows.map((r) => r.map((cell) => `"${cell}"`).join(',')).join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `daily_visit_ledgers_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-serif text-gray-900 dark:text-[#D4AF37]">
            Daily Visit Ledgers
          </h1>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70">
            Immutable Operational Ledgers. Every calendar day represents one operational ledger.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => refetch()}
            className="p-2 rounded-xl bg-gray-100 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-700 dark:text-[#FAFAFA]"
          >
            <RefreshCw className="w-4 h-4 text-[#D4AF37]" />
          </button>
          <button
            onClick={exportCSV}
            className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] text-xs font-bold shadow-md hover:brightness-110 flex items-center space-x-1.5"
          >
            <Download className="w-4 h-4" />
            <span>Export Ledgers CSV</span>
          </button>
        </div>
      </div>

      {/* Filter Controls */}
      <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search name, phone, session ID..."
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA]"
            />
          </div>

          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] font-bold"
          >
            <option value="TODAY">Ledger: TODAY (Default)</option>
            <option value="YESTERDAY">Ledger: Yesterday</option>
            <option value="7DAYS">Ledger: Last 7 Days</option>
            <option value="MONTH">Ledger: This Month</option>
            <option value="CUSTOM">Ledger: Custom Date Range</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA]"
          >
            <option value="ALL">All Session Statuses</option>
            <option value="INSIDE">INSIDE Premise</option>
            <option value="CHECKED_OUT">CHECKED_OUT</option>
            <option value="AUTO_CLOSED">AUTO_CLOSED</option>
          </select>

          <input
            type="text"
            value={volunteerFilter === 'ALL' ? '' : volunteerFilter}
            onChange={(e) => setVolunteerFilter(e.target.value || 'ALL')}
            placeholder="Filter by Volunteer..."
            className="px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA]"
          />
        </div>
      </div>

      {/* Daily Ledgers Listing */}
      {isLoading ? (
        <div className="p-8">
          <TableSkeleton rows={6} />
        </div>
      ) : ledgers.length === 0 ? (
        <div className="p-12 text-center text-gray-500 dark:text-gray-400 text-xs space-y-2 bg-white dark:bg-[#1C1410] rounded-2xl border border-[#D4AF37]/20">
          <Calendar className="w-8 h-8 text-[#D4AF37] mx-auto opacity-50" />
          <p className="font-semibold text-sm text-gray-700 dark:text-[#FAFAFA]">No Daily Ledgers Found</p>
          <p>Try adjusting your filter selection.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {ledgers.map((l: any) => {
            const sum = l.summary || {};

            return (
              <div key={l.date} className="rounded-2xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm overflow-hidden p-4 space-y-4">
                
                {/* LEDGER HEADER & SUMMARY */}
                <div className="p-4 bg-gray-50 dark:bg-[#2C1A11] rounded-xl border border-gray-200 dark:border-[#D4AF37]/20 space-y-3">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 rounded-xl bg-[#D4AF37]/20 text-[#D4AF37]">
                        <Calendar className="w-5 h-5" />
                      </div>
                      <div>
                        <h2 className="text-base font-bold text-gray-900 dark:text-[#FAFAFA]">
                          Daily Visit Ledger: {sum.display_date || l.date} <span className="text-xs font-mono font-normal text-gray-400">({l.date})</span>
                        </h2>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{l.sessions?.length || 0} Sessions Recorded in Ledger</p>
                      </div>
                    </div>

                    <div>
                      {sum.is_read_only ? (
                        <span className="px-3 py-1 rounded-xl bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 font-bold text-xs flex items-center space-x-1">
                          <Lock className="w-3.5 h-3.5" />
                          <span>READ-ONLY LEDGER</span>
                        </span>
                      ) : (
                        <span className="px-3 py-1 rounded-xl bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 font-bold text-xs flex items-center space-x-1">
                          <span>ACTIVE TODAY'S LEDGER</span>
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 text-xs font-semibold">
                    <span className="px-3 py-1 rounded-xl bg-gray-100 dark:bg-[#1C1410] text-gray-800 dark:text-[#FAFAFA]">
                      Visitors: <strong className="text-[#D4AF37] font-mono">{sum.total_visitors}</strong>
                    </span>
                    <span className="px-3 py-1 rounded-xl bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300">
                      Inside: <strong className="font-mono">{sum.people_inside}</strong>
                    </span>
                    <span className="px-3 py-1 rounded-xl bg-gray-100 dark:bg-[#1C1410] text-gray-700 dark:text-gray-300">
                      Checked Out: <strong className="font-mono">{sum.checked_out}</strong>
                    </span>
                    <span className="px-3 py-1 rounded-xl bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300">
                      Auto Closed: <strong className="font-mono">{sum.auto_closed}</strong>
                    </span>
                  </div>
                </div>

                {/* SESSIONS TABLE */}
                <div className="overflow-x-auto border border-gray-100 dark:border-[#D4AF37]/10 rounded-xl">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-gray-50/50 dark:bg-[#2C1A11]/50 border-b border-gray-100 dark:border-[#D4AF37]/10 text-gray-500 dark:text-[#D4AF37] uppercase font-semibold">
                        <th className="py-3 px-4">Visitor Name</th>
                        <th className="py-3 px-4">Phone</th>
                        <th className="py-3 px-4 text-center">Persons Count</th>
                        <th className="py-3 px-4">Purpose</th>
                        <th className="py-3 px-4">Check-In</th>
                        <th className="py-3 px-4">Check-Out</th>
                        <th className="py-3 px-4">Duration</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4">Volunteer</th>
                        <th className="py-3 px-4">Sync State</th>
                        <th className="py-3 px-4 text-center">GPS</th>
                        <th className="py-3 px-4 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 dark:divide-[#D4AF37]/10">
                      {l.sessions.map((s: any) => {
                        const status = s.status || 'INSIDE';
                        const sync = s.sync_status || 'SYNCED';
                        const hasGps = s.latitude != null && s.longitude != null;

                        return (
                          <tr key={s.id || s.visitor_uuid} className="hover:bg-gray-50/50 dark:hover:bg-[#2C1A11]/40 transition-colors">
                            <td className="py-3 px-4 font-semibold text-gray-900 dark:text-[#FAFAFA]">{s.name}</td>
                            <td className="py-3 px-4 text-gray-600 dark:text-gray-300 font-mono">{s.phone_number || s.phone || '—'}</td>
                            <td className="py-3 px-4 text-center font-bold text-[#D4AF37]">{s.persons_count || 1}</td>
                            <td className="py-3 px-4 text-gray-700 dark:text-gray-300">{s.purpose?.name_en || s.purpose_name || 'General Darshan'}</td>
                            <td className="py-3 px-4 text-gray-600 dark:text-gray-300 font-mono">{s.check_in_time || s.visitor_time || '09:30 AM'}</td>
                            <td className="py-3 px-4 text-gray-500 font-mono">{s.check_out_time || (status === 'AUTO_CLOSED' ? '23:59:59 (Auto)' : 'N/A')}</td>
                            <td className="py-3 px-4 font-semibold text-emerald-600 dark:text-emerald-400 font-mono">{s.duration || 'Completed'}</td>
                            <td className="py-3 px-4">
                              {status === 'INSIDE' ? (
                                <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 font-bold text-[10px]">INSIDE</span>
                              ) : status === 'AUTO_CLOSED' || s.is_auto_closed ? (
                                <span className="px-2.5 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 font-bold text-[10px]">AUTO_CLOSED</span>
                              ) : (
                                <span className="px-2.5 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 font-bold text-[10px]">CHECKED_OUT</span>
                              )}
                            </td>
                            <td className="py-3 px-4 text-gray-600 dark:text-gray-400 font-mono">{s.volunteer_name || s.volunteer_id || 'admin'}</td>
                            <td className="py-3 px-4">
                              <span className="px-2 py-0.5 rounded-full bg-sky-100 dark:bg-sky-950/60 text-sky-800 dark:text-sky-300 font-semibold text-[10px]">{sync}</span>
                            </td>
                            <td className="py-3 px-4 text-center">
                              {hasGps ? <span className="text-emerald-500 font-bold text-[10px]">YES</span> : <span className="text-gray-400 text-[10px]">NO</span>}
                            </td>
                            <td className="py-3 px-4 text-right">
                              <div className="flex items-center justify-end space-x-1.5">
                                <button
                                  onClick={() => {
                                    setSelectedVisitor(s);
                                    setIsDrawerOpen(true);
                                  }}
                                  className="p-1 text-[#D4AF37] hover:bg-gray-100 dark:hover:bg-[#2C1A11] rounded"
                                  title="View Details"
                                >
                                  <Eye className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => {
                                    setEditProfileRecord(s);
                                    setEditFormData({
                                      name: s.name,
                                      phone_number: s.phone_number || s.phone || '',
                                      village_name_custom: s.village_name_custom || '',
                                      gender: s.gender || 'MALE',
                                      age: s.age || 30,
                                    });
                                  }}
                                  className="p-1 text-amber-500 hover:bg-gray-100 dark:hover:bg-[#2C1A11] rounded"
                                  title="Edit Visitor Profile"
                                >
                                  <Edit className="w-4 h-4" />
                                </button>
                                {status === 'INSIDE' && !sum.is_read_only && (
                                  <button
                                    onClick={() => handleCheckout(s.id || s.visitor_uuid)}
                                    className="p-1 text-emerald-600 hover:bg-emerald-50 rounded"
                                    title="Checkout Session"
                                  >
                                    <LogOut className="w-4 h-4" />
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

              </div>
            );
          })}
        </div>
      )}

      {/* Edit Visitor Profile Popup */}
      {editProfileRecord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-md bg-white dark:bg-[#1C1410] border border-[#D4AF37]/30 rounded-2xl p-6 shadow-2xl space-y-4 text-xs">
            <div className="border-b border-gray-200 dark:border-[#D4AF37]/20 pb-3 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-gray-900 dark:text-[#FAFAFA] text-sm">Edit Visitor Profile</h3>
                <p className="text-[10px] text-[#D4AF37]">Modifies permanent Visitor Profile only. Visit Sessions remain immutable.</p>
              </div>
              <button onClick={() => setEditProfileRecord(null)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>

            <form onSubmit={handleSaveProfileEdit} className="space-y-3">
              <div>
                <label className="block font-semibold mb-1 text-gray-700 dark:text-gray-300">Full Name</label>
                <input
                  type="text"
                  value={editFormData.name}
                  onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                  className="w-full p-2.5 rounded-xl border border-gray-200 dark:border-[#D4AF37]/30 bg-gray-50 dark:bg-[#2C1A11] text-gray-800 dark:text-[#FAFAFA]"
                  required
                />
              </div>

              <div>
                <label className="block font-semibold mb-1 text-gray-700 dark:text-gray-300">Phone Number</label>
                <input
                  type="text"
                  value={editFormData.phone_number}
                  onChange={(e) => setEditFormData({ ...editFormData, phone_number: e.target.value })}
                  className="w-full p-2.5 rounded-xl border border-gray-200 dark:border-[#D4AF37]/30 bg-gray-50 dark:bg-[#2C1A11] text-gray-800 dark:text-[#FAFAFA]"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold mb-1 text-gray-700 dark:text-gray-300">Gender</label>
                  <select
                    value={editFormData.gender}
                    onChange={(e) => setEditFormData({ ...editFormData, gender: e.target.value })}
                    className="w-full p-2.5 rounded-xl border border-gray-200 dark:border-[#D4AF37]/30 bg-gray-50 dark:bg-[#2C1A11] text-gray-800 dark:text-[#FAFAFA]"
                  >
                    <option value="MALE">Male</option>
                    <option value="FEMALE">Female</option>
                    <option value="OTHER">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold mb-1 text-gray-700 dark:text-gray-300">Age</label>
                  <input
                    type="number"
                    value={editFormData.age}
                    onChange={(e) => setEditFormData({ ...editFormData, age: parseInt(e.target.value) || 30 })}
                    className="w-full p-2.5 rounded-xl border border-gray-200 dark:border-[#D4AF37]/30 bg-gray-50 dark:bg-[#2C1A11] text-gray-800 dark:text-[#FAFAFA]"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold mb-1 text-gray-700 dark:text-gray-300">Village / City</label>
                <input
                  type="text"
                  value={editFormData.village_name_custom}
                  onChange={(e) => setEditFormData({ ...editFormData, village_name_custom: e.target.value })}
                  className="w-full p-2.5 rounded-xl border border-gray-200 dark:border-[#D4AF37]/30 bg-gray-50 dark:bg-[#2C1A11] text-gray-800 dark:text-[#FAFAFA]"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-gray-200 dark:border-[#D4AF37]/20">
                <button
                  type="button"
                  onClick={() => setEditProfileRecord(null)}
                  className="px-4 py-2 rounded-xl bg-gray-100 dark:bg-[#2C1A11] text-gray-700 dark:text-gray-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-[#D4AF37] text-black font-bold hover:brightness-110"
                >
                  Update Profile
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Drawer */}
      <VisitorDetailsDrawer visitor={selectedVisitor} isOpen={isDrawerOpen} onClose={() => setIsDrawerOpen(false)} />
    </div>
  );
}
