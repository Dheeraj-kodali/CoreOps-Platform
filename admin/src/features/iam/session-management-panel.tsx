'use client';

import React from 'react';
import { Laptop, Smartphone, Globe, ShieldAlert, LogOut } from 'lucide-react';
import { UserSession } from '../../types/user';

interface SessionManagementPanelProps {
  sessions: UserSession[];
  onRevokeSession: (tokenJti: string) => void;
  onRevokeAllSessions: () => void;
}

export function SessionManagementPanel({ sessions, onRevokeSession, onRevokeAllSessions }: SessionManagementPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-sm font-bold font-serif text-[#D4AF37]">Active Security Sessions</h4>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70 mt-0.5">
            Devices and browser sessions currently authenticated with JWT tokens.
          </p>
        </div>

        {sessions.length > 0 && (
          <button
            onClick={onRevokeAllSessions}
            className="px-3.5 py-1.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 font-bold text-xs hover:bg-red-500/20 transition-all flex items-center space-x-1.5"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Revoke All Devices</span>
          </button>
        )}
      </div>

      <div className="space-y-2.5">
        {sessions.length === 0 ? (
          <p className="text-xs text-center py-6 text-gray-500">No active sessions found.</p>
        ) : (
          sessions.map((sess) => {
            const isMobile = sess.user_agent.toLowerCase().includes('mobile');
            return (
              <div
                key={sess.id || sess.token_jti}
                className="p-3.5 rounded-2xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-100 dark:border-[#D4AF37]/20 flex items-center justify-between text-xs"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-[#D4AF37]/20 text-[#D4AF37] flex items-center justify-center">
                    {isMobile ? <Smartphone className="w-5 h-5" /> : <Laptop className="w-5 h-5" />}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <p className="font-bold text-gray-800 dark:text-[#FAFAFA]">{sess.user_agent}</p>
                      {sess.is_current && (
                        <span className="px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 text-[9px] font-bold">
                          Current Device
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-gray-400 mt-0.5 flex items-center space-x-2">
                      <span className="flex items-center">
                        <Globe className="w-3 h-3 mr-1 text-[#D4AF37]" />
                        IP: {sess.ip_address}
                      </span>
                      <span>• Login: {sess.login_time}</span>
                    </p>
                  </div>
                </div>

                {!sess.is_current && (
                  <button
                    onClick={() => onRevokeSession(sess.token_jti)}
                    className="p-2 rounded-xl text-red-500 hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors"
                    title="Revoke Session Token"
                  >
                    <LogOut className="w-4 h-4" />
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
