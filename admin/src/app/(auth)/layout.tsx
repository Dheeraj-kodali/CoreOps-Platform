import React from 'react';
import { PublicGuard } from '../../components/shared/public-guard';

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <PublicGuard>
      <div className="min-h-screen bg-[#1C1410] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#2C1A11] via-[#1C1410] to-[#0E0907] flex items-center justify-center p-6 text-[#FAFAFA] relative overflow-hidden">
        {/* Background Sacred Geometric Glow Effect */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-[#D4AF37]/10 blur-3xl pointer-events-none"></div>

        <div className="w-full max-w-md relative z-10">{children}</div>
      </div>
    </PublicGuard>
  );
}
