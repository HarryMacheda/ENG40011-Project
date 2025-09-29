"use client"
import { useEffect, useRef, useState, useCallback } from "react";
import { ApiClient } from "../utility/api-client";

interface UseWebSocketOptions<T> {
  onMessage?: (data: T) => void;
  onOpen?: (ws: WebSocket) => void;
  onClose?: () => void;
  onError?: (err: Event) => void;
}

export function useWebSocket<T = any>(
  client: ApiClient,
  path: string,
  options: UseWebSocketOptions<T> = {}
) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<T | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = client.connectWebSocket(path);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      options.onOpen?.(ws);
    };

    ws.onmessage = (event: MessageEvent) => {
      try {
        const data: T = JSON.parse(event.data);
        setLastMessage(data);
        options.onMessage?.(data);
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      options.onClose?.();
    };

    ws.onerror = (event: Event) => {
      options.onError?.(event);
    };

    return () => {
      ws.close();
    };
  }, [client, path]);

  const sendMessage = useCallback((message: unknown) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn("WebSocket not connected. Message not sent.");
    }
  }, []);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    socket: wsRef.current,
  };
}