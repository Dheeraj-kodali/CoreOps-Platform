'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronRight, Home } from 'lucide-react';

export function Breadcrumbs() {
  const pathname = usePathname();
  const segments = pathname.split('/').filter(Boolean);

  if (segments.length === 0) return null;

  return (
    <nav className="flex items-center text-xs font-medium text-gray-500 dark:text-gray-400 py-1">
      <Link href="/dashboard" className="hover:text-[#D4AF37] transition-colors flex items-center">
        <Home className="w-3.5 h-3.5 mr-1" />
        <span>Home</span>
      </Link>

      {segments.map((segment, index) => {
        const href = `/${segments.slice(0, index + 1).join('/')}`;
        const isLast = index === segments.length - 1;
        const title = segment.charAt(0).toUpperCase() + segment.slice(1);

        return (
          <React.Fragment key={href}>
            <ChevronRight className="w-3.5 h-3.5 mx-1.5 text-gray-400 flex-shrink-0" />
            {isLast ? (
              <span className="text-[#D4AF37] font-semibold">{title}</span>
            ) : (
              <Link href={href} className="hover:text-[#D4AF37] transition-colors">
                {title}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
}
