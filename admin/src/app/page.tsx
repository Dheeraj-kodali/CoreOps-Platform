'use client';

import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import DashboardView from '../components/DashboardView';
import VisitorsView from '../components/VisitorsView';
import AnalyticsView from '../components/AnalyticsView';
import ReportsView from '../components/ReportsView';
import UsersView from '../components/UsersView';
import NotificationsView from '../components/NotificationsView';
import SettingsView from '../components/SettingsView';
import LoginModal from '../components/LoginModal';
import { getMe, UserProfile } from '../api/auth';

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(true);
  const [showLoginModal, setShowLoginModal] = useState<boolean>(false);

  const checkAuth = async () => {
    try {
      const me = await getMe();
      setUser(me);
      setIsAuthenticated(true);
      setShowLoginModal(false);
    } catch (_) {
      setIsAuthenticated(false);
      setShowLoginModal(true);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <div className="flex min-h-screen bg-[#FAF8F5]">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header user={user} onLogout={() => checkAuth()} />

        <main className="flex-1 overflow-y-auto">
          {activeTab === 'dashboard' && <DashboardView />}
          {activeTab === 'visitors' && <VisitorsView />}
          {activeTab === 'analytics' && <AnalyticsView />}
          {activeTab === 'reports' && <ReportsView />}
          {activeTab === 'users' && <UsersView />}
          {activeTab === 'notifications' && <NotificationsView />}
          {activeTab === 'audit' && <VisitorsView />}
          {activeTab === 'settings' && <SettingsView />}
        </main>
      </div>

      {/* Admin Login Modal when token missing/expired */}
      <LoginModal isOpen={showLoginModal} onSuccess={checkAuth} />
    </div>
  );
}
