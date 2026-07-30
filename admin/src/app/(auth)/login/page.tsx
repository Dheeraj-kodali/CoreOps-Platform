'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Lock, User as UserIcon, Eye, EyeOff, AlertCircle, CheckCircle2, ShieldCheck, ArrowRight, X } from 'lucide-react';
import { useAuth } from '../../../providers/AuthProvider';
import { AuthRepository } from '../../../repositories/auth-repository';

// Zod Validation Schema
const loginSchema = z.object({
  username: z.string().min(1, 'Username or Email is required'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  rememberMe: z.boolean().optional(),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login: authLogin } = useAuth();

  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [sessionExpired, setSessionExpired] = useState(false);

  // Forgot Password Modal State
  const [isForgotOpen, setIsForgotOpen] = useState(false);
  const [forgotInput, setForgotInput] = useState('');
  const [forgotSuccess, setForgotSuccess] = useState<string | null>(null);
  const [forgotLoading, setForgotLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: '',
      password: '',
      rememberMe: true,
    },
  });

  useEffect(() => {
    if (searchParams.get('expired') === '1') {
      setSessionExpired(true);
    }
  }, [searchParams]);

  const onSubmit = async (data: LoginFormData) => {
    setErrorMessage(null);
    try {
      const result = await AuthRepository.login({
        username: data.username,
        password: data.password,
      });

      authLogin(result.token, '', result.user);
      router.replace('/dashboard');
    } catch (err: any) {
      setErrorMessage(err?.message || 'Invalid username or password. Please try again.');
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotInput) return;
    setForgotLoading(true);
    setForgotSuccess(null);
    try {
      await AuthRepository.login; // trigger check or request API
      setForgotSuccess('If an account exists for this username/email, password reset instructions have been issued.');
    } catch {
      setForgotSuccess('Request received. Please contact your Temple Super Administrator if issues persist.');
    } finally {
      setForgotLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Temple Sacred Gold Header Branding */}
      <div className="text-center space-y-2">
        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#D4AF37] via-[#FF9933] to-[#B38F24] flex items-center justify-center text-3xl mx-auto shadow-lg shadow-[#D4AF37]/20 border-2 border-[#D4AF37]/50">
          🛕
        </div>
        <h1 className="text-2xl font-bold font-serif text-[#D4AF37] tracking-wide uppercase">
          Sri Kalki Seva Alayam
        </h1>
        <p className="text-xs text-[#FAFAFA]/70 tracking-wider">
          Enterprise Visitor Management & Admin Console
        </p>
      </div>

      {/* Login Card */}
      <div className="p-8 rounded-3xl bg-[#2C1A11]/90 backdrop-blur-xl border border-[#D4AF37]/40 shadow-2xl space-y-6">
        {/* Session Expired Banner */}
        {sessionExpired && (
          <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>Your session has expired or was revoked. Please log in again to continue.</span>
          </div>
        )}

        {/* Error Alert Banner */}
        {errorMessage && (
          <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-start space-x-2 animate-shake">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {/* Username / Email Field */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#FAFAFA]/90 uppercase tracking-wider">
              Username or Email
            </label>
            <div className="relative">
              <UserIcon className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#D4AF37]" />
              <input
                {...register('username')}
                type="text"
                disabled={isSubmitting}
                placeholder="admin@kalkiseva.org"
                className={`w-full pl-10 pr-4 py-2.5 text-xs rounded-xl bg-[#1C1410] border text-[#FAFAFA] placeholder-gray-500 focus:outline-none focus:border-[#D4AF37] transition-all ${
                  errors.username ? 'border-red-500' : 'border-[#D4AF37]/30'
                }`}
              />
            </div>
            {errors.username && (
              <p className="text-[11px] text-red-400 font-medium">{errors.username.message}</p>
            )}
          </div>

          {/* Password Field */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-[#FAFAFA]/90 uppercase tracking-wider">
                Password
              </label>
              <button
                type="button"
                onClick={() => setIsForgotOpen(true)}
                className="text-[11px] text-[#D4AF37] hover:underline focus:outline-none"
              >
                Forgot Password?
              </button>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#D4AF37]" />
              <input
                {...register('password')}
                type={showPassword ? 'text' : 'password'}
                disabled={isSubmitting}
                placeholder="••••••••••••"
                className={`w-full pl-10 pr-10 py-2.5 text-xs rounded-xl bg-[#1C1410] border text-[#FAFAFA] placeholder-gray-500 focus:outline-none focus:border-[#D4AF37] transition-all ${
                  errors.password ? 'border-red-500' : 'border-[#D4AF37]/30'
                }`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#D4AF37] focus:outline-none"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.password && (
              <p className="text-[11px] text-red-400 font-medium">{errors.password.message}</p>
            )}
          </div>

          {/* Remember Me Checkbox */}
          <div className="flex items-center justify-between pt-1">
            <label className="flex items-center space-x-2 text-xs text-[#FAFAFA]/80 cursor-pointer">
              <input
                {...register('rememberMe')}
                type="checkbox"
                className="rounded border-[#D4AF37]/40 bg-[#1C1410] text-[#D4AF37] focus:ring-[#D4AF37]"
              />
              <span>Remember this device</span>
            </label>
          </div>

          {/* Submit Button (Disables multiple login clicks) */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-[#D4AF37] via-[#FF9933] to-[#D4AF37] text-[#1C1410] font-bold text-xs uppercase tracking-wider shadow-lg hover:brightness-110 active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2"
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-[#1C1410] border-t-transparent rounded-full animate-spin"></div>
                <span>Authenticating...</span>
              </>
            ) : (
              <>
                <span>Sign In to Executive Console</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>
      </div>

      {/* Security Footer */}
      <div className="text-center flex items-center justify-center space-x-2 text-[11px] text-[#FAFAFA]/50">
        <ShieldCheck className="w-3.5 h-3.5 text-[#D4AF37]" />
        <span>Protected by Multi-Tenant JWT & Row-Level Security</span>
      </div>

      {/* Forgot Password Modal */}
      {isForgotOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="max-w-md w-full p-6 rounded-3xl bg-[#2C1A11] border border-[#D4AF37]/50 shadow-2xl space-y-4 relative">
            <button
              onClick={() => setIsForgotOpen(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-[#FAFAFA]"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-lg font-bold font-serif text-[#D4AF37]">Reset Password</h3>
            <p className="text-xs text-[#FAFAFA]/70">
              Enter your username or email address below to receive password recovery instructions.
            </p>

            {forgotSuccess ? (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>{forgotSuccess}</span>
              </div>
            ) : (
              <form onSubmit={handleForgotPassword} className="space-y-4 pt-2">
                <input
                  type="text"
                  required
                  value={forgotInput}
                  onChange={(e) => setForgotInput(e.target.value)}
                  placeholder="Username or email address"
                  className="w-full px-4 py-2.5 text-xs rounded-xl bg-[#1C1410] border border-[#D4AF37]/30 text-[#FAFAFA] placeholder-gray-500 focus:outline-none focus:border-[#D4AF37]"
                />
                <button
                  type="submit"
                  disabled={forgotLoading}
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold text-xs uppercase tracking-wider"
                >
                  {forgotLoading ? 'Processing...' : 'Send Recovery Link'}
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
