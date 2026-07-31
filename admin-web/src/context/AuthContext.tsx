"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { apiClient } from "@/lib/api";

interface User {
  username: string;
  role: string;
  email?: string;
  fullName?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const storedToken = localStorage.getItem("admin_access_token");
    const storedUser = localStorage.getItem("admin_user");

    if (storedToken) {
      setToken(storedToken);
      if (storedUser) {
        try {
          setUser(JSON.parse(storedUser));
        } catch {
          setUser({ username: "admin", role: "Administrator", fullName: "Temple Administrator" });
        }
      } else {
        setUser({ username: "admin", role: "Administrator", fullName: "Temple Administrator" });
      }
    }
    setIsLoading(false);
  }, []);

  // Protected route enforcement
  useEffect(() => {
    if (!isLoading) {
      const isPublicRoute = pathname === "/login" || pathname === "/";
      if (!token && pathname.startsWith("/dashboard")) {
        router.replace("/login");
      } else if (token && isPublicRoute) {
        router.replace("/dashboard");
      }
    }
  }, [token, isLoading, pathname, router]);

  const login = async (usernameInput: string, passwordInput: string) => {
    const trimmedUsername = usernameInput.trim();
    const trimmedPassword = passwordInput.trim();

    try {
      // Authenticate with live backend POST /api/v1/auth/login
      const response = await apiClient.post("/auth/login", {
        username: trimmedUsername,
        password: trimmedPassword,
      });

      const { access_token, refresh_token } = response.data;

      const userObj: User = {
        username: trimmedUsername,
        role: trimmedUsername.toLowerCase() === "admin" ? "Administrator" : "Staff User",
        email: `${trimmedUsername}@kalkiseva.org`,
        fullName: trimmedUsername === "admin" ? "Temple Administrator" : trimmedUsername,
      };

      localStorage.setItem("admin_access_token", access_token);
      if (refresh_token) {
        localStorage.setItem("admin_refresh_token", refresh_token);
      }
      localStorage.setItem("admin_user", JSON.stringify(userObj));

      setToken(access_token);
      setUser(userObj);

      router.push("/dashboard");
      return { success: true };
    } catch (err: any) {
      console.warn("Backend authentication failed:", err?.response?.data || err?.message);
      const errorMessage = err?.response?.data?.detail || "Invalid username or password";
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    localStorage.removeItem("admin_access_token");
    localStorage.removeItem("admin_refresh_token");
    localStorage.removeItem("admin_user");
    setToken(null);
    setUser(null);
    router.replace("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
