"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useAuth } from "./AuthContext";

interface WebSocketContextType {
  isConnected: boolean;
  lastEvent: any | null;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

const PROD_WS_URL = "wss://coreops-platform.onrender.com/api/v1/ws";

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<any | null>(null);
  const { isAuthenticated } = useAuth();

  const getWsUrl = useCallback(() => {
    const envUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    if (envUrl && envUrl.trim() !== "") {
      const formatted = envUrl.trim().replace(/\/$/, "");
      return formatted.replace(/^https:\/\//i, "wss://").replace(/^http:\/\//i, "ws://") + "/ws";
    }
    return PROD_WS_URL;
  }, []);

  const connectWebSocket = useCallback(() => {
    if (typeof window === "undefined") return;

    const wsUrl = getWsUrl();
    console.log(`[WebSocketProvider] Attempting production WebSocket connection to: ${wsUrl}`);

    try {
      const socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        console.log(`[WebSocketProvider] Successfully established WebSocket connection (HTTP 101) to ${wsUrl}`);
        setIsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          console.log("[WebSocket Event Received]", parsed);
          setLastEvent(parsed);
        } catch (err) {
          console.warn("[WebSocket] Failed to parse event JSON", err);
        }
      };

      socket.onerror = (error) => {
        console.error("[WebSocket Error]", error);
        setIsConnected(false);
      };

      socket.onclose = (event) => {
        console.warn(`[WebSocket Closed] Code: ${event.code}, Reason: ${event.reason || "Disconnected"}. Reconnecting in 3s...`);
        setIsConnected(false);
      };

      return socket;
    } catch (err) {
      console.error("[WebSocket Exception]", err);
      setIsConnected(false);
      return null;
    }
  }, [getWsUrl]);

  useEffect(() => {
    if (!isAuthenticated) {
      setIsConnected(false);
      return;
    }

    const wsUrl = getWsUrl();
    console.log(`[WebSocketProvider Mount] Initializing WebSocket client connection to ${wsUrl}`);

    let socket: WebSocket | null = null;
    let reconnectTimer: NodeJS.Timeout | null = null;

    const initSocket = () => {
      try {
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
          console.log(`[WebSocket Active] Connected to ${wsUrl} (HTTP 101 Switching Protocols)`);
          setIsConnected(true);
        };

        socket.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data);
            console.log("[WebSocket Broadcast Received]", parsed);
            if (parsed.event && parsed.event !== "CONNECTED") {
              setLastEvent(parsed);
            }
          } catch (e) {
            console.error("[WebSocket Message Parse Error]", e);
          }
        };

        socket.onerror = (err) => {
          console.error("[WebSocket Client Error]", err);
          setIsConnected(false);
        };

        socket.onclose = () => {
          console.warn("[WebSocket Client Disconnected] Retrying in 3000ms...");
          setIsConnected(false);
          reconnectTimer = setTimeout(initSocket, 3000);
        };
      } catch (e) {
        console.error("[WebSocket Initialization Exception]", e);
        reconnectTimer = setTimeout(initSocket, 3000);
      }
    };

    initSocket();

    return () => {
      if (socket) {
        socket.close();
      }
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
    };
  }, [isAuthenticated, getWsUrl]);

  return (
    <WebSocketContext.Provider
      value={{
        isConnected,
        lastEvent,
        connectWebSocket,
        disconnectWebSocket: () => setIsConnected(false),
      }}
    >
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error("useWebSocket must be used within a WebSocketProvider");
  }
  return context;
}
