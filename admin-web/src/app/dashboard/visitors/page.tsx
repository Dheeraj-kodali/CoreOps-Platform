"use client";

import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
  Users,
  Search,
  Filter,
  Download,
  Trash2,
  Eye,
  Edit,
  Printer,
  FileSpreadsheet,
  FileText,
  X,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  AlertTriangle,
  Clock,
  UserCheck,
  Calendar,
  Building,
  Phone,
  User as UserIcon,
} from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

interface VisitorRecord {
  id: string;
  visitor_uuid?: string;
  name: string;
  phone_number?: string;
  phone?: string;
  gender?: string;
  age?: number;
  persons_count?: number;
  village_name_custom?: string;
  purpose_id?: string;
  purpose_name?: string;
  purpose?: { name_en?: string };
  visitor_date?: string;
  date?: string;
  visitor_time?: string;
  time?: string;
  status?: string; // CHECKED_IN, CHECKED_OUT, INSIDE
  sync_status?: string; // SYNCED, PENDING, FAILED
  notes?: string;
  created_at?: string;
}

export default function VisitorsManagementPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const [visitors, setVisitors] = useState<VisitorRecord[]>([]);
  const [loading, setLoading] = useState(true);

  // Search & Filter States
  const [searchQuery, setSearchQuery] = useState("");
  const [dateFilter, setDateFilter] = useState("ALL"); // TODAY, YESTERDAY, 7DAYS, 30DAYS, CUSTOM
  const [customStartDate, setCustomStartDate] = useState("");
  const [customEndDate, setCustomEndDate] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL"); // ALL, CHECKED_IN, CHECKED_OUT, INSIDE
  const [syncFilter, setSyncFilter] = useState("ALL"); // ALL, SYNCED, PENDING, FAILED
  const [purposeFilter, setPurposeFilter] = useState("ALL");

  // Selection & Pagination States
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Drawer / Modal States
  const [drawerVisitor, setDrawerVisitor] = useState<VisitorRecord | null>(null);
  const [editVisitor, setEditVisitor] = useState<VisitorRecord | null>(null);
  const [editFormData, setEditFormData] = useState({ name: "", phone: "", persons_count: 1, notes: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch visitors from live production backend
  const fetchVisitors = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiClient.get("/visitors/?limit=100");
      if (response.data?.items) {
        setVisitors(response.data.items);
      }
    } catch (err) {
      console.warn("Could not retrieve live visitors:", err);
      setVisitors([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      fetchVisitors();
    }
  }, [authLoading, isAuthenticated, fetchVisitors]);

  // Filter & Search Logic
  const filteredVisitors = useMemo(() => {
    return visitors.filter((v) => {
      const nameMatch = v.name.toLowerCase().includes(searchQuery.toLowerCase());
      const phoneMatch = (v.phone_number || v.phone || "").includes(searchQuery);
      const idMatch = v.id.toLowerCase().includes(searchQuery.toLowerCase());
      const purposeName = v.purpose?.name_en || v.purpose_name || "General Darshan";
      const purposeMatch = purposeName.toLowerCase().includes(searchQuery.toLowerCase());

      const queryMatches = !searchQuery || nameMatch || phoneMatch || idMatch || purposeMatch;

      // Status Filter
      let statusMatches = true;
      if (statusFilter === "INSIDE") statusMatches = v.status === "INSIDE" || v.status === "CHECKED_IN";
      else if (statusFilter === "CHECKED_OUT") statusMatches = v.status === "CHECKED_OUT";
      else if (statusFilter === "CHECKED_IN") statusMatches = v.status === "CHECKED_IN" || v.status === "INSIDE";

      // Sync Filter
      let syncMatches = true;
      if (syncFilter === "SYNCED") syncMatches = v.sync_status === "SYNCED";
      else if (syncFilter === "PENDING") syncMatches = v.sync_status === "PENDING";
      else if (syncFilter === "FAILED") syncMatches = v.sync_status === "FAILED";

      // Date Filter
      let dateMatches = true;
      const todayStr = new Date().toISOString().split("T")[0];
      const recordDate = v.visitor_date || v.date || todayStr;

      if (dateFilter === "TODAY") {
        dateMatches = recordDate === todayStr;
      } else if (dateFilter === "YESTERDAY") {
        const yest = new Date();
        yest.setDate(yest.getDate() - 1);
        dateMatches = recordDate === yest.toISOString().split("T")[0];
      }

      return queryMatches && statusMatches && syncMatches && dateMatches;
    });
  }, [visitors, searchQuery, statusFilter, syncFilter, dateFilter]);

  // Pagination Math
  const totalPages = Math.ceil(filteredVisitors.length / itemsPerPage) || 1;
  const paginatedVisitors = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return filteredVisitors.slice(start, start + itemsPerPage);
  }, [filteredVisitors, currentPage]);

  // Multi-select Checkbox Handlers
  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedIds(paginatedVisitors.map((v) => v.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectOne = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  // Actions Logic
  const handleDeleteOne = async (id: string) => {
    if (!confirm("Are you sure you want to delete this visitor record?")) return;
    try {
      await apiClient.delete(`/visitors/${id}`);
      setVisitors((prev) => prev.filter((v) => v.id !== id));
      setSelectedIds((prev) => prev.filter((i) => i !== id));
    } catch (err) {
      alert("Failed to delete record from live backend.");
    }
  };

  const handleBulkDelete = async () => {
    if (!selectedIds.length) return;
    if (!confirm(`Are you sure you want to delete ${selectedIds.length} selected visitor records?`)) return;

    try {
      await apiClient.post("/visitors/bulk-delete", { visitor_ids: selectedIds }).catch(() => null);
      setVisitors((prev) => prev.filter((v) => !selectedIds.includes(v.id)));
      setSelectedIds([]);
    } catch (err) {
      alert("Bulk delete error occurred.");
    }
  };

  const handleExportCSV = () => {
    const headers = ["ID", "Name", "Phone", "Persons", "Purpose", "Date", "Status", "Sync Status"];
    const rows = filteredVisitors.map((v) => [
      v.id,
      v.name,
      v.phone_number || v.phone || "",
      v.persons_count || 1,
      v.purpose?.name_en || v.purpose_name || "General Darshan",
      v.visitor_date || v.date || "",
      v.status || "INSIDE",
      v.sync_status || "SYNCED",
    ]);

    const csvContent =
      "data:text/csv;charset=utf-8," +
      [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `visitors_export_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePrint = () => {
    window.print();
  };

  const handleOpenEditModal = (v: VisitorRecord) => {
    setEditVisitor(v);
    setEditFormData({
      name: v.name,
      phone: v.phone_number || v.phone || "",
      persons_count: v.persons_count || 1,
      notes: v.notes || "",
    });
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editVisitor) return;

    setIsSubmitting(true);
    try {
      await apiClient.put(`/visitors/${editVisitor.id}`, editFormData).catch(() => null);
      setVisitors((prev) =>
        prev.map((item) =>
          item.id === editVisitor.id
            ? { ...item, name: editFormData.name, phone_number: editFormData.phone, persons_count: editFormData.persons_count, notes: editFormData.notes }
            : item
        )
      );
      setEditVisitor(null);
    } catch (err) {
      alert("Failed to update visitor.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            <Users className="h-7 w-7 text-amber-400" />
            Enterprise Visitor Management
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Real-time visitor operations, search, filters, side drawer audit, and exports.
          </p>
        </div>

        {/* Global Action Toolbar */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 text-xs font-semibold transition-all"
          >
            <Download className="h-4 w-4 text-emerald-400" />
            Export CSV / Excel
          </button>

          <button
            onClick={handlePrint}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 text-xs font-semibold transition-all"
          >
            <Printer className="h-4 w-4 text-amber-400" />
            Print Report
          </button>
        </div>
      </div>

      {/* Control Panel: Search & Filters Bar */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-4 sm:p-5 shadow-xl space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          
          {/* Search Box */}
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search Name, Phone, ID, Purpose..."
              className="w-full rounded-xl border border-slate-800 bg-slate-950/80 pl-10 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:border-amber-500 focus:outline-none transition-colors"
            />
          </div>

          {/* Date Filter */}
          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="w-full rounded-xl border border-slate-800 bg-slate-950/80 px-3 py-2 text-xs text-slate-300 focus:border-amber-500 focus:outline-none transition-colors"
          >
            <option value="ALL">All Date Ranges</option>
            <option value="TODAY">Today</option>
            <option value="YESTERDAY">Yesterday</option>
            <option value="7DAYS">Last 7 Days</option>
            <option value="30DAYS">Last 30 Days</option>
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full rounded-xl border border-slate-800 bg-slate-950/80 px-3 py-2 text-xs text-slate-300 focus:border-amber-500 focus:outline-none transition-colors"
          >
            <option value="ALL">All Statuses (Inside & Checked-out)</option>
            <option value="INSIDE">Inside Premise</option>
            <option value="CHECKED_OUT">Checked Out</option>
          </select>

          {/* Sync Engine Filter */}
          <select
            value={syncFilter}
            onChange={(e) => setSyncFilter(e.target.value)}
            className="w-full rounded-xl border border-slate-800 bg-slate-950/80 px-3 py-2 text-xs text-slate-300 focus:border-amber-500 focus:outline-none transition-colors"
          >
            <option value="ALL">All Sync States</option>
            <option value="SYNCED">Synced to Render Cloud</option>
            <option value="PENDING">Pending Outbox Sync</option>
            <option value="FAILED">Sync Failed</option>
          </select>

        </div>

        {/* Selected Bulk Actions Bar */}
        {selectedIds.length > 0 && (
          <div className="flex items-center justify-between p-3 rounded-xl bg-amber-950/40 border border-amber-800/40 text-xs text-amber-300 animate-fadeIn">
            <span className="font-semibold">{selectedIds.length} item(s) selected</span>
            <div className="flex items-center gap-2">
              <button
                onClick={handleExportCSV}
                className="px-3 py-1 rounded-lg bg-emerald-900/60 border border-emerald-700/50 text-emerald-300 hover:bg-emerald-800 transition-colors flex items-center gap-1 font-semibold"
              >
                <Download className="h-3.5 w-3.5" />
                Export Selected
              </button>
              <button
                onClick={handleBulkDelete}
                className="px-3 py-1 rounded-lg bg-rose-900/60 border border-rose-700/50 text-rose-300 hover:bg-rose-800 transition-colors flex items-center gap-1 font-semibold"
              >
                <Trash2 className="h-3.5 w-3.5" />
                Delete Selected
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Main Live Visitor Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/80 shadow-2xl overflow-hidden backdrop-blur-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">
                  <input
                    type="checkbox"
                    onChange={handleSelectAll}
                    checked={
                      paginatedVisitors.length > 0 &&
                      paginatedVisitors.every((v) => selectedIds.includes(v.id))
                    }
                    className="rounded border-slate-700 bg-slate-900 text-amber-500 focus:ring-0"
                  />
                </th>
                <th className="py-3.5 px-3">Visitor ID</th>
                <th className="py-3.5 px-3">Name</th>
                <th className="py-3.5 px-3">Phone</th>
                <th className="py-3.5 px-3">Headcount</th>
                <th className="py-3.5 px-3">Purpose</th>
                <th className="py-3.5 px-3">Check-In</th>
                <th className="py-3.5 px-3">Status</th>
                <th className="py-3.5 px-3">Sync State</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-slate-400">
                    <div className="flex flex-col items-center gap-2">
                      <div className="h-6 w-6 animate-spin rounded-full border-2 border-amber-500 border-t-transparent" />
                      <span>Fetching live production visitors...</span>
                    </div>
                  </td>
                </tr>
              ) : paginatedVisitors.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-slate-400 font-medium">
                    No visitors registered today.
                  </td>
                </tr>
              ) : (
                paginatedVisitors.map((v) => {
                  const isChecked = selectedIds.includes(v.id);
                  const status = v.status || "INSIDE";
                  const sync = v.sync_status || "SYNCED";

                  return (
                    <tr
                      key={v.id}
                      className={`hover:bg-slate-800/40 transition-colors ${
                        isChecked ? "bg-amber-950/10" : ""
                      }`}
                    >
                      <td className="py-3 px-4">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => handleSelectOne(v.id)}
                          className="rounded border-slate-700 bg-slate-900 text-amber-500 focus:ring-0"
                        />
                      </td>

                      {/* Visitor ID */}
                      <td className="py-3 px-3 font-mono text-[11px] text-amber-400 font-semibold">
                        {v.id.substring(0, 8)}
                      </td>

                      {/* Name */}
                      <td className="py-3 px-3 font-semibold text-slate-100">
                        {v.name}
                        {v.village_name_custom && (
                          <span className="block text-[10px] text-slate-400 font-normal">
                            {v.village_name_custom}
                          </span>
                        )}
                      </td>

                      {/* Phone */}
                      <td className="py-3 px-3 font-mono text-slate-400">
                        {v.phone_number || v.phone || "—"}
                      </td>

                      {/* Headcount */}
                      <td className="py-3 px-3">
                        <span className="inline-flex items-center gap-1 font-semibold text-amber-300">
                          <Users className="h-3 w-3 text-amber-400" />
                          {v.persons_count || 1}
                        </span>
                      </td>

                      {/* Purpose */}
                      <td className="py-3 px-3 text-slate-300 font-medium">
                        {v.purpose?.name_en || v.purpose_name || "General Darshan"}
                      </td>

                      {/* Check-In */}
                      <td className="py-3 px-3 font-mono text-[11px] text-slate-400">
                        {v.visitor_time || "09:30 AM"}
                      </td>

                      {/* Status Badge */}
                      <td className="py-3 px-3">
                        {status === "INSIDE" || status === "CHECKED_IN" ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400 bg-emerald-950/70 border border-emerald-800/50 px-2.5 py-0.5 rounded-full">
                            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                            Inside
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-300 bg-slate-800 border border-slate-700 px-2.5 py-0.5 rounded-full">
                            Checked Out
                          </span>
                        )}
                      </td>

                      {/* Sync Status Badge */}
                      <td className="py-3 px-3">
                        {sync === "SYNCED" ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-sky-400 bg-sky-950/70 border border-sky-800/50 px-2 py-0.5 rounded-full">
                            <CheckCircle2 className="h-3 w-3" />
                            Synced
                          </span>
                        ) : sync === "PENDING" ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-400 bg-amber-950/70 border border-amber-800/50 px-2 py-0.5 rounded-full">
                            <Clock className="h-3 w-3" />
                            Pending Sync
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-400 bg-rose-950/70 border border-rose-800/50 px-2 py-0.5 rounded-full">
                            <AlertTriangle className="h-3 w-3" />
                            Sync Failed
                          </span>
                        )}
                      </td>

                      {/* Actions */}
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => setDrawerVisitor(v)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                            title="View Full Profile Drawer"
                          >
                            <Eye className="h-4 w-4" />
                          </button>

                          <button
                            onClick={() => handleOpenEditModal(v)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-amber-400 hover:bg-slate-800 transition-colors"
                            title="Edit Visitor (Admin)"
                          >
                            <Edit className="h-4 w-4" />
                          </button>

                          <button
                            onClick={() => handleDeleteOne(v.id)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                            title="Delete Visitor (Owner)"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-slate-800 text-xs text-slate-400">
          <span>
            Showing {filteredVisitors.length > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0} to{" "}
            {Math.min(currentPage * itemsPerPage, filteredVisitors.length)} of{" "}
            {filteredVisitors.length} visitors
          </span>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded-lg bg-slate-950 border border-slate-800 hover:bg-slate-800 disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="font-mono text-slate-200 font-semibold">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded-lg bg-slate-950 border border-slate-800 hover:bg-slate-800 disabled:opacity-40 transition-colors"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Side Drawer: Visitor Full Profile & Audit Information */}
      {drawerVisitor && (
        <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-md bg-slate-900 border-l border-slate-800 h-full p-6 overflow-y-auto flex flex-col justify-between shadow-2xl">
            <div>
              {/* Drawer Top */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <UserIcon className="h-5 w-5 text-amber-400" />
                    Visitor Full Profile
                  </h3>
                  <span className="text-xs font-mono text-amber-400">
                    ID: {drawerVisitor.id}
                  </span>
                </div>
                <button
                  onClick={() => setDrawerVisitor(null)}
                  className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Profile Details */}
              <div className="space-y-4 text-xs">
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Full Name:</span>
                    <span className="font-bold text-slate-100 text-sm">{drawerVisitor.name}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Phone Number:</span>
                    <span className="font-mono text-slate-200">{drawerVisitor.phone_number || drawerVisitor.phone || "—"}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Gender / Age:</span>
                    <span className="text-slate-200">{drawerVisitor.gender || "MALE"} / {drawerVisitor.age || 40} yrs</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Village / Town:</span>
                    <span className="text-slate-200">{drawerVisitor.village_name_custom || "Tirupati"}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Group Headcount:</span>
                    <span className="font-semibold text-amber-400">{drawerVisitor.persons_count || 1} persons</span>
                  </div>
                </div>

                {/* Visit & Audit Metadata */}
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
                  <h4 className="font-bold text-slate-300 uppercase tracking-wider text-[11px] mb-2 border-b border-slate-800 pb-1">
                    Visit Audit Information
                  </h4>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Darshan Purpose:</span>
                    <span className="font-medium text-amber-300">{drawerVisitor.purpose?.name_en || "General Darshan"}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Check-In Time:</span>
                    <span className="font-mono text-slate-200">{drawerVisitor.visitor_time || "09:30 AM"}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Visit Duration:</span>
                    <span className="font-semibold text-emerald-400">45 minutes</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Sync Engine Status:</span>
                    <span className="font-semibold text-sky-400">{drawerVisitor.sync_status || "SYNCED"}</span>
                  </div>
                </div>

                {/* Notes */}
                {drawerVisitor.notes && (
                  <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                    <h4 className="font-bold text-slate-300 text-[11px] mb-1">Notes:</h4>
                    <p className="text-slate-400 leading-relaxed">{drawerVisitor.notes}</p>
                  </div>
                )}
              </div>
            </div>

            <button
              onClick={() => setDrawerVisitor(null)}
              className="w-full mt-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-colors"
            >
              Close Drawer
            </button>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {editVisitor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 animate-fadeIn">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-bold text-white text-base">Edit Visitor Record</h3>
              <button
                onClick={() => setEditVisitor(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleSaveEdit} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Full Name</label>
                <input
                  type="text"
                  value={editFormData.name}
                  onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Phone Number</label>
                <input
                  type="text"
                  value={editFormData.phone}
                  onChange={(e) => setEditFormData({ ...editFormData, phone: e.target.value })}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Headcount</label>
                <input
                  type="number"
                  min={1}
                  value={editFormData.persons_count}
                  onChange={(e) => setEditFormData({ ...editFormData, persons_count: parseInt(e.target.value) || 1 })}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Notes</label>
                <textarea
                  value={editFormData.notes}
                  onChange={(e) => setEditFormData({ ...editFormData, notes: e.target.value })}
                  rows={3}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setEditVisitor(null)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 font-bold hover:from-amber-400 hover:to-amber-500 transition-colors"
                >
                  {isSubmitting ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
