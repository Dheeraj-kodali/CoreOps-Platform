'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchVisitors, deleteVisitor, Visitor } from '../api/visitors';
import { Search, Download, Trash2, Eye, RefreshCw, X } from 'lucide-react';

export default function VisitorsView() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [selectedVisitor, setSelectedVisitor] = useState<Visitor | null>(null);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['visitorsList', search, page],
    queryFn: () => fetchVisitors({ search, page, limit: 10 }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteVisitor,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['visitorsList'] });
    },
  });

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to soft-delete this visitor entry?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleExportCSV = () => {
    if (!data?.items) return;
    const headers = 'Name,Phone,Gender,Age,Persons,Date,Time,Status\n';
    const rows = data.items
      .map(
        (v) =>
          `"${v.name}","${v.phone_number}","${v.gender}",${v.age},${v.persons_count},"${v.visitor_date}","${v.visitor_time}","${v.sync_status}"`
      )
      .join('\n');
    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `visitors_export_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="font-serif text-2xl font-bold text-[#2C1A11]">Visitor Master Registry</h2>
          <p className="text-xs text-gray-500 mt-1">Comprehensive records of all registered temple visitors</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleExportCSV}
            className="flex items-center space-x-2 bg-[#D4AF37] text-[#2C1A11] px-4 py-2 rounded-lg text-xs font-bold hover:bg-[#b8972e] transition-colors shadow-sm"
          >
            <Download className="w-4 h-4" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={() => refetch()}
            className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="bg-white p-4 rounded-xl border border-[#D4AF37]/30 shadow-sm flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search visitor name, phone, village..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full pl-9 pr-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:border-[#D4AF37]"
          />
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-white rounded-xl border border-[#D4AF37]/30 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#FAF8F5] border-b border-[#D4AF37]/20 text-[11px] font-bold text-[#2C1A11] uppercase">
                <th className="py-3 px-4">Visitor Name</th>
                <th className="py-3 px-4">Phone Number</th>
                <th className="py-3 px-4">Gender / Age</th>
                <th className="py-3 px-4">Persons</th>
                <th className="py-3 px-4">Service / Purpose</th>
                <th className="py-3 px-4">Date & Time</th>
                <th className="py-3 px-4">Sync Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-xs">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-gray-500">
                    Loading visitor records...
                  </td>
                </tr>
              ) : data?.items && data.items.length > 0 ? (
                data.items.map((v) => (
                  <tr key={v.id} className="hover:bg-gray-50/80">
                    <td className="py-3.5 px-4 font-bold text-[#2C1A11]">{v.name}</td>
                    <td className="py-3.5 px-4 text-gray-600">{v.phone_number}</td>
                    <td className="py-3.5 px-4 text-gray-600">{v.gender} / {v.age} Yrs</td>
                    <td className="py-3.5 px-4 text-gray-600">{v.persons_count}</td>
                    <td className="py-3.5 px-4 text-gray-600">{v.temple_service || v.purpose?.name_en || 'General Darshan'}</td>
                    <td className="py-3.5 px-4 text-gray-500">{v.visitor_date} {v.visitor_time}</td>
                    <td className="py-3.5 px-4">
                      <span className="bg-green-100 text-green-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                        {v.sync_status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right space-x-2">
                      <button
                        onClick={() => setSelectedVisitor(v)}
                        className="p-1 text-gray-500 hover:text-[#2C1A11]"
                        title="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(v.id)}
                        className="p-1 text-gray-400 hover:text-red-600"
                        title="Delete Entry"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-gray-400">
                    No visitor records matching your query.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        {data && data.pages > 1 && (
          <div className="p-4 border-t border-gray-100 flex items-center justify-between text-xs">
            <span className="text-gray-500">
              Page {data.page} of {data.pages} ({data.total} records)
            </span>
            <div className="flex space-x-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
                className="px-3 py-1 bg-gray-100 rounded disabled:opacity-50 text-gray-700"
              >
                Previous
              </button>
              <button
                disabled={page >= data.pages}
                onClick={() => setPage((p) => p + 1)}
                className="px-3 py-1 bg-gray-100 rounded disabled:opacity-50 text-gray-700"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Visitor Detail Modal */}
      {selectedVisitor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-lg shadow-xl overflow-hidden border border-[#D4AF37]/40">
            <div className="bg-[#2C1A11] p-4 text-white flex items-center justify-between">
              <h3 className="font-serif text-base font-bold text-[#D4AF37]">Visitor Record Detail</h3>
              <button onClick={() => setSelectedVisitor(null)} className="text-gray-300 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-3 text-xs">
              <div className="flex justify-between border-b pb-2">
                <span className="font-bold text-gray-600">Visitor UUID:</span>
                <span className="text-gray-800 font-mono">{selectedVisitor.visitor_uuid}</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="font-bold text-gray-600">Name:</span>
                <span className="text-gray-800 font-bold">{selectedVisitor.name}</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="font-bold text-gray-600">Phone:</span>
                <span className="text-gray-800">{selectedVisitor.phone_number}</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="font-bold text-gray-600">Gender / Age:</span>
                <span className="text-gray-800">{selectedVisitor.gender} / {selectedVisitor.age} Yrs</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="font-bold text-gray-600">Persons Count:</span>
                <span className="text-gray-800">{selectedVisitor.persons_count}</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="font-bold text-gray-600">Village / Town:</span>
                <span className="text-gray-800">{selectedVisitor.village_name_custom || 'N/A'}</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="font-bold text-gray-600">Service:</span>
                <span className="text-gray-800">{selectedVisitor.temple_service || 'General Darshan'}</span>
              </div>
              <div className="flex justify-between border-b pb-2">
                <span className="font-bold text-gray-600">Registration Date/Time:</span>
                <span className="text-gray-800">{selectedVisitor.visitor_date} {selectedVisitor.visitor_time}</span>
              </div>
            </div>
            <div className="p-4 bg-gray-50 text-right">
              <button
                onClick={() => setSelectedVisitor(null)}
                className="px-4 py-2 bg-[#D4AF37] text-[#2C1A11] font-bold text-xs rounded-lg"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
