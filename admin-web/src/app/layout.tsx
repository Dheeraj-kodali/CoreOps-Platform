import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Temple Management Platform - Administrator Portal",
  description: "Production Admin Web Portal for CoreOps Temple Management Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased dark">
      <body className={`${inter.className} min-h-full bg-slate-950 text-slate-50 flex flex-col selection:bg-amber-500 selection:text-slate-950`}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
