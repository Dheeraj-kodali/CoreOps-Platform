'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, Plus, UserCheck, Download, Filter, Eye, Trash2, Calendar, Phone, Users, ShieldCheck, RefreshCw, QrCode, History, Star, Activity } from 'lucide-react';
import { VisitorRepository } from '../../../repositories/visitor-repository';
import { useDebounce } from '../../../hooks/use-debounce';
import { VisitorDetailsDrawer } from '../../../features/visitors/visitor-details-drawer';
import { DuplicateCheckModal } from '../../../features/visitors/duplicate-check-modal';
import { VisitorFormModal } from '../../../features/visitors/visitor-form-modal';
import { QRScannerModal } from '../../../features/visitors/qr-scanner-modal';
import { VisitorHistoryModal } from '../../../features/visitors/visitor-history-modal';
import { TableSkeleton } from '../../../components/shared/loading-skeleton';
import { Visitor, VisitorStatus } from '../../../types/visitor';

export default function VisitorManagementPage() {
  const queryClient = useQueryClient();

  // Search & Filter States
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 400);

  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [page, setPage] = useState(1);
  const [limit] = useState(20);

  // Selected Visitor & Modals
  const [selectedVisitor, setSelectedVisitor] = useState<Visitor | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isDuplicateModalOpen, setIsDuplicateModalOpen] = useState(false);
  const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
  const [isQRScannerOpen, setIsQRScannerOpen] = useState(false);
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);

  // TanStack Query for Visitor List
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['visitors', debouncedSearch, dateFrom, dateTo, statusFilter, page, limit],
    queryFn: () =>
      VisitorRepository.getVisitors({
        search: debouncedSearch || undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
        page,
        limit,
      }),
  });

  // Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => VisitorRepository.deleteVisitor(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['visitors'] });
    },
  });

  const handleDelete = async (id: string, name: string) => {
    if (confirm(`Are you sure you want to soft-delete visitor record for '${name}'?`)) {
      deleteMutation.mutate(id);
    }
  };

  const exportCSV = () => {
    if (!data?.items) return;
    const headers = 'ID,Name,Phone,Gender,Age,GroupSize,Status,Date,Time,SyncStatus\n';
    const rows = data.items
      .map(
        (v) =>
          `"${v.visitor_uuid}","${v.name}","${v.phone_number}","${v.gender}",${v.age},${v.persons_count},"${v.status || 'CHECKED_IN'}","${v.visitor_date}","${v.visitor_time}","${v.sync_status}"`
      )
      .join('\n');

    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `visitors_export_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* Top Header Banner & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-serif text-gray-900 dark:text-[#D4AF37]">Visitor Lifecycle Management</h1>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70">
            Real-time Status Transitions, Gate QR Scanner, Phone Visit History & Audit Trail
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setIsQRScannerOpen(true)}
            className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] text-xs font-bold shadow-md hover:brightness-110 transition-all flex items-center space-x-1.5"
          >
            <QrCode className="w-4 h-4" />
            <span>Scan Gate QR</span>
          </button>

          <button
            onClick={() => setIsHistoryModalOpen(true)}
            className="px-3.5 py-2 rounded-xl bg-gray-100 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] text-xs font-semibold hover:bg-gray-200 dark:hover:bg-[#3D2519] transition-all flex items-center space-x-1.5"
          >
            <History className="w-4 h-4 text-[#D4AF37]" />
            <span>Phone History</span>
          </button>

          <button
            onClick={() => setIsDuplicateModalOpen(true)}
            className="px-3.5 py-2 rounded-xl bg-gray-100 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] text-xs font-semibold hover:bg-gray-200 dark:hover:bg-[#3D2519] transition-all flex items-center space-x-1.5"
          >
            <UserCheck className="w-4 h-4 text-[#D4AF37]" />
            <span>Check Duplicate</span>
          </button>

          <button
            onClick={exportCSV}
            className="px-3.5 py-2 rounded-xl bg-gray-100 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] text-xs font-semibold hover:bg-gray-200 dark:hover:bg-[#3D2519] transition-all flex items-center space-x-1.5"
          >
            <Download className="w-4 h-4 text-[#D4AF37]" />
            <span>Export CSV</span>
          </button>

          <button
            onClick={() => setIsRegisterModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-[#2C1A11] text-[#D4AF37] border border-[#D4AF37]/40 text-xs font-bold shadow-md hover:bg-[#3D2519] transition-all flex items-center space-x-1.5"
          >
            <Plus className="w-4 h-4" />
            <span>Register Visitor</span>
          </button>
        </div>
      </div>

      {/* Advanced Search & Multi-Filter Bar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Live Search */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search name, phone, village..."
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
          </div>

          {/* Lifecycle Status Filter */}
          <div className="relative">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            >
              <option value="ALL">All Statuses</option>
              <option value="REGISTERED">Registered</option>
              <option value="CHECKED_IN">Checked In</option>
              <option value="WAITING">Waiting in Queue</option>
              <option value="INSIDE_TEMPLE">Inside Temple</option>
              <option value="COMPLETED">Completed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>

          {/* Date From */}
          <div className="relative">
            <Calendar className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
          </div>

          {/* Date To */}
          <div className="relative">
            <Calendar className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
          </div>

          {/* Reset Filters */}
          <button
            onClick={() => {
              setSearchTerm('');
              setStatusFilter('ALL');
              setDateFrom('');
              setDateTo('');
              setPage(1);
            }}
            className="py-2 px-3 rounded-xl bg-gray-100 dark:bg-[#2C1A11] text-xs font-semibold text-gray-600 dark:text-[#FAFAFA]/70 hover:bg-gray-200 dark:hover:bg-[#3D2519] transition-colors flex items-center justify-center space-x-1"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset Filters</span>
          </button>
        </div>
      </div>

      {/* Visitor Data Table */}
      <div className="rounded-2xl bg-white dark:bg-[#1C1410] border border-[#D4AF37]/25 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-6">
            <TableSkeleton rows={6} />
          </div>
        ) : isError ? (
          <div className="p-8 text-center text-red-500 text-xs">
            Failed to load visitor records. Please ensure FastAPI backend is active.
          </div>
        ) : !data?.items || data.items.length === 0 ? (
          <div className="p-12 text-center text-gray-500 dark:text-gray-400 text-xs space-y-2">
            <Users className="w-8 h-8 text-[#D4AF37] mx-auto opacity-50" />
            <p className="font-semibold text-sm text-gray-700 dark:text-[#FAFAFA]">No Visitor Records Found</p>
            <p>Try adjusting your search query or status filter.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-gray-50 dark:bg-[#2C1A11] border-b border-gray-200 dark:border-[#D4AF37]/20 text-gray-500 dark:text-[#D4AF37] uppercase font-semibold">
                  <th className="py-3.5 px-4">Visitor Name</th>
                  <th className="py-3.5 px-4">Phone Number</th>
                  <th className="py-3.5 px-4">Lifecycle Status</th>
                  <th className="py-3.5 px-4">Group Size</th>
                  <th className="py-3.5 px-4">Visit Date & Time</th>
                  <th className="py-3.5 px-4">Purpose</th>
                  <th className="py-3.5 px-4">Village</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-[#D4AF37]/10">
                {data.items.map((visitor) => (
                  <tr key={visitor.id || visitor.visitor_uuid} className="hover:bg-gray-50/50 dark:hover:bg-[#2C1A11]/40 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-gray-900 dark:text-[#FAFAFA]">
                      <div className="flex items-center space-x-2.5">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold flex items-center justify-center text-xs flex-shrink-0">
                          {visitor.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="flex items-center space-x-1.5">
                            <p>{visitor.name}</p>
                            {(visitor.is_repeat_visitor || (visitor.total_visits_count && visitor.total_visits_count > 1)) && (
                              <span className="px-1.5 py-0.5 rounded bg-[#D4AF37]/20 text-[#D4AF37] text-[9px] font-bold border border-[#D4AF37]/30" title="Repeat Visitor">
                                ★ Repeat
                              </span>
                            )}
                          </div>
                          <p className="text-[10px] text-gray-400 font-mono">{visitor.visitor_uuid.substring(0, 8)}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-gray-600 dark:text-gray-300 font-mono">{visitor.phone_number}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 font-bold text-[10px] flex items-center w-fit space-x-1">
                        <Activity className="w-3 h-3 text-emerald-500" />
                        <span>{visitor.status || 'CHECKED_IN'}</span>
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-gray-700 dark:text-gray-300">
                      <span className="px-2 py-0.5 rounded-full bg-gray-100 dark:bg-[#2C1A11] font-semibold text-[11px]">
                        {visitor.persons_count} Person(s)
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-gray-600 dark:text-gray-300">
                      {visitor.visitor_date} <span className="text-[10px] text-gray-400">({visitor.visitor_time})</span>
                    </td>
                    <td className="py-3.5 px-4 text-gray-700 dark:text-gray-300">
                      {visitor.purpose?.name_en || 'General Darshan'}
                    </td>
                    <td className="py-3.5 px-4 text-gray-600 dark:text-gray-300">
                      {visitor.village?.name_en || visitor.village_name_custom || 'Local Region'}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => {
                            setSelectedVisitor(visitor);
                            setIsDrawerOpen(true);
                          }}
                          className="p-1.5 rounded-lg text-[#D4AF37] hover:bg-gray-100 dark:hover:bg-[#2C1A11] transition-colors"
                          title="View Details, Timeline & Digital Pass"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(visitor.id, visitor.name)}
                          className="p-1.5 rounded-lg text-red-500 hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors"
                          title="Soft Delete Record"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {data && data.pages > 1 && (
          <div className="p-4 border-t border-gray-200 dark:border-[#D4AF37]/20 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>
              Showing Page <strong className="text-gray-800 dark:text-[#FAFAFA]">{data.page}</strong> of{' '}
              <strong className="text-gray-800 dark:text-[#FAFAFA]">{data.pages}</strong> ({data.total} Total Visitors)
            </span>

            <div className="flex items-center space-x-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-[#2C1A11] disabled:opacity-40 text-gray-700 dark:text-[#FAFAFA]"
              >
                Previous
              </button>
              <button
                disabled={page >= data.pages}
                onClick={() => setPage(page + 1)}
                className="px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-[#2C1A11] disabled:opacity-40 text-gray-700 dark:text-[#FAFAFA]"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Slide-over Visitor Details Drawer */}
      <VisitorDetailsDrawer visitor={selectedVisitor} isOpen={isDrawerOpen} onClose={() => setIsDrawerOpen(false)} />

      {/* Gate QR Scanner Modal */}
      <QRScannerModal
        isOpen={isQRScannerOpen}
        onClose={() => setIsQRScannerOpen(false)}
        onStatusUpdated={() => refetch()}
      />

      {/* Visitor Phone History Modal */}
      <VisitorHistoryModal isOpen={isHistoryModalOpen} onClose={() => setIsHistoryModalOpen(false)} />

      {/* Duplicate Check Modal */}
      <DuplicateCheckModal isOpen={isDuplicateModalOpen} onClose={() => setIsDuplicateModalOpen(false)} />

      {/* Visitor Registration Modal */}
      <VisitorFormModal
        isOpen={isRegisterModalOpen}
        onClose={() => setIsRegisterModalOpen(false)}
        onSuccess={() => refetch()}
      />
    </div>
  );
}
