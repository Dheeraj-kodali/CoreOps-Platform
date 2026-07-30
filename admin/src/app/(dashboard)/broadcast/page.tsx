'use client';

import React, { useState } from 'react';

interface Campaign {
  id: string;
  title: string;
  message: string;
  filterType: string;
  status: 'Draft' | 'Validated' | 'Approved' | 'Queued' | 'Sending' | 'Completed' | 'Cancelled';
  totalRecipients: number;
  deliveredCount: number;
  failedCount: number;
  createdAt: string;
}

export default function BroadcastPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([
    {
      id: 'camp-101',
      title: 'Sri Kalki Annual Brahmotsavam Invitation',
      message: '🙏 Namaste Devotee, Sri Kalki Seva Alayam invites you to the Grand Annual Brahmotsavam.',
      filterType: 'ALL_DEVOTEES',
      status: 'Completed',
      totalRecipients: 320,
      deliveredCount: 315,
      failedCount: 5,
      createdAt: '2026-07-29 10:00 AM',
    },
    {
      id: 'camp-102',
      title: 'Special Annadanam Seva Notice',
      message: '🙏 Mahaprasadam Annadanam Seva will be served today at Sri Kalki Seva Alayam.',
      filterType: 'VILLAGE',
      status: 'Sending',
      totalRecipients: 150,
      deliveredCount: 98,
      failedCount: 2,
      createdAt: '2026-07-30 08:30 AM',
    },
  ]);

  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [filterType, setFilterType] = useState('ALL_DEVOTEES');
  const [confirmed, setConfirmed] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCreateCampaign = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !message.trim()) {
      alert('Please enter a campaign title and message.');
      return;
    }
    if (!confirmed) {
      alert('Explicit safety confirmation is required before creating a campaign.');
      return;
    }

    setIsSubmitting(true);
    setTimeout(() => {
      const newCamp: Campaign = {
        id: `camp-${Date.now()}`,
        title: title.trim(),
        message: message.trim(),
        filterType,
        status: 'Queued',
        totalRecipients: filterType === 'ALL_DEVOTEES' ? 320 : 85,
        deliveredCount: 0,
        failedCount: 0,
        createdAt: new Date().toLocaleString(),
      };
      setCampaigns([newCamp, ...campaigns]);
      setTitle('');
      setMessage('');
      setConfirmed(false);
      setIsSubmitting(false);
      alert('Broadcast Campaign created and queued successfully!');
    }, 400);
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px', color: '#111827' }}>
        Enterprise Broadcast Messaging System
      </h1>
      <p style={{ color: '#6b7280', marginBottom: '24px' }}>
        Meta WhatsApp Cloud API multi-channel broadcast campaign creation, audience filtering, and progress tracking.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
        {/* Campaign Creation Form */}
        <div style={{ background: '#ffffff', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: '#1f2937' }}>
            New Broadcast Campaign
          </h2>
          <form onSubmit={handleCreateCampaign}>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '6px', color: '#374151' }}>
                Campaign Title
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Temple Festival Announcement"
                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px' }}
              />
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '6px', color: '#374151' }}>
                Target Audience Filter
              </label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px' }}
              >
                <option value="ALL_DEVOTEES">All Devotees (320 recipients)</option>
                <option value="VILLAGE">Filter by Village (Tenali / Guntur)</option>
                <option value="REPEAT_VISITORS">Repeat Visitors (2+ visits)</option>
                <option value="LAST_30_DAYS">Visitors in Last 30 Days</option>
              </select>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '6px', color: '#374151' }}>
                Message Body (Meta WhatsApp Format)
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={4}
                placeholder="Enter Meta WhatsApp message text..."
                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px' }}
              />
            </div>

            <div style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="checkbox"
                id="confirm"
                checked={confirmed}
                onChange={(e) => setConfirmed(e.target.checked)}
              />
              <label htmlFor="confirm" style={{ fontSize: '13px', color: '#4b5563' }}>
                Require explicit user confirmation (Safety Enforcement Rule)
              </label>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              style={{
                background: '#2563eb',
                color: '#ffffff',
                padding: '12px 20px',
                borderRadius: '6px',
                border: 'none',
                fontWeight: '600',
                cursor: 'pointer',
                width: '100%',
              }}
            >
              {isSubmitting ? 'Processing...' : 'Create & Queue Campaign'}
            </button>
          </form>
        </div>

        {/* Analytics Summary */}
        <div style={{ background: '#ffffff', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: '#1f2937' }}>
            Broadcast Metrics & Overview
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px', border: '1px solid #f3f4f6' }}>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Total Messages Sent</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827' }}>413</div>
            </div>
            <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px', border: '1px solid #f3f4f6' }}>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Delivery Success Rate</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#059669' }}>98.3%</div>
            </div>
            <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px', border: '1px solid #f3f4f6' }}>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Average Latency</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2563eb' }}>0.05s</div>
            </div>
            <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '8px', border: '1px solid #f3f4f6' }}>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Meta API Version</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#7c3aed' }}>v23.0</div>
            </div>
          </div>
        </div>
      </div>

      {/* Campaign List */}
      <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px', color: '#1f2937' }}>
        Broadcast Campaign History
      </h2>
      <div style={{ background: '#ffffff', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        {campaigns.map((c) => {
          const pct = c.totalRecipients > 0 ? Math.round((c.deliveredCount / c.totalRecipients) * 100) : 0;
          return (
            <div key={c.id} style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: '600', margin: 0, color: '#111827' }}>{c.title}</h3>
                <span
                  style={{
                    padding: '4px 10px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '600',
                    background: c.status === 'Completed' ? '#d1fae5' : '#fef3c7',
                    color: c.status === 'Completed' ? '#065f46' : '#92400e',
                  }}
                >
                  {c.status}
                </span>
              </div>
              <p style={{ fontSize: '14px', color: '#4b5563', margin: '0 0 12px 0' }}>{c.message}</p>
              <div style={{ background: '#e5e7eb', height: '8px', borderRadius: '4px', overflow: 'hidden', marginBottom: '8px' }}>
                <div style={{ width: `${pct}%`, background: '#2563eb', height: '100%' }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#6b7280' }}>
                <span>Delivered: {c.deliveredCount} / {c.totalRecipients} ({pct}%)</span>
                <span>Created: {c.createdAt}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
