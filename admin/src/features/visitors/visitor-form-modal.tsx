'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { X, User, Phone, MapPin, HeartHandshake } from 'lucide-react';
import { VisitorRepository } from '../../repositories/visitor-repository';

const visitorSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  phone_number: z.string().min(10, 'Phone number must be at least 10 digits'),
  gender: z.enum(['MALE', 'FEMALE', 'OTHER']),
  age: z.number().min(1, 'Age must be valid').max(120),
  persons_count: z.number().min(1, 'Count must be at least 1'),
  village_name_custom: z.string().optional(),
  temple_service: z.string().optional(),
  notes: z.string().optional(),
});

type VisitorFormData = z.infer<typeof visitorSchema>;

interface VisitorFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function VisitorFormModal({ isOpen, onClose, onSuccess }: VisitorFormModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<VisitorFormData>({
    resolver: zodResolver(visitorSchema),
    defaultValues: {
      gender: 'MALE',
      age: 30,
      persons_count: 1,
    },
  });

  if (!isOpen) return null;

  const onSubmit = async (data: VisitorFormData) => {
    try {
      const visitor_uuid = crypto.randomUUID();
      const today = new Date().toISOString().split('T')[0];
      const time = new Date().toTimeString().split(' ')[0];

      await VisitorRepository.registerVisitor({
        ...data,
        visitor_uuid,
        visitor_date: today,
        visitor_time: time,
        purpose_id: 'd9b3e100-0000-0000-0000-000000000001', // Default Darshan Purpose ID
      });

      reset();
      onSuccess();
      onClose();
    } catch (err: any) {
      alert(err?.message || 'Failed to register visitor.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
      <div className="max-w-lg w-full bg-white dark:bg-[#1C1410] text-[#1C1410] dark:text-[#FAFAFA] rounded-3xl shadow-2xl border border-[#D4AF37]/40 p-6 space-y-4 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 dark:hover:text-[#FAFAFA]">
          <X className="w-5 h-5" />
        </button>

        <div>
          <h3 className="text-lg font-bold font-serif text-[#D4AF37]">Register New Visitor</h3>
          <p className="text-xs text-gray-500 dark:text-[#FAFAFA]/70 mt-1">Manual visitor check-in form for executive staff.</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <div>
            <label className="text-xs font-semibold">Full Name *</label>
            <input
              {...register('name')}
              placeholder="e.g. Ramesh Kumar"
              className="w-full mt-1 px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
            {errors.name && <p className="text-[11px] text-red-500">{errors.name.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold">Phone Number *</label>
              <input
                {...register('phone_number')}
                placeholder="9876543210"
                className="w-full mt-1 px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
              />
              {errors.phone_number && <p className="text-[11px] text-red-500">{errors.phone_number.message}</p>}
            </div>

            <div>
              <label className="text-xs font-semibold">Gender</label>
              <select
                {...register('gender')}
                className="w-full mt-1 px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
              >
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold">Age</label>
              <input
                type="number"
                {...register('age', { valueAsNumber: true })}
                className="w-full mt-1 px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
              />
            </div>

            <div>
              <label className="text-xs font-semibold">Group / Family Count</label>
              <input
                type="number"
                {...register('persons_count', { valueAsNumber: true })}
                className="w-full mt-1 px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold">Origin Village / City</label>
            <input
              {...register('village_name_custom')}
              placeholder="e.g. Tirupati Rural"
              className="w-full mt-1 px-3 py-2 text-xs rounded-xl bg-gray-50 dark:bg-[#2C1A11] border border-gray-200 dark:border-[#D4AF37]/30 text-gray-800 dark:text-[#FAFAFA] focus:outline-none focus:border-[#D4AF37]"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-2.5 mt-2 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#FF9933] text-[#1C1410] font-bold text-xs shadow-md hover:brightness-110 transition-all"
          >
            {isSubmitting ? 'Registering...' : 'Complete Visitor Registration'}
          </button>
        </form>
      </div>
    </div>
  );
}
