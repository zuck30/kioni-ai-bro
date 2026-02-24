import { useEffect, useRef, useState, useCallback } from 'react';
import { useKioniStore } from '../store/kioniStore';

interface WebSocketMessage {
  type: 'chat' | 'typing' | 'vision' | 'voice' | 'system' | 'error';
  payload: any;
  timestamp: string;
}

export const useWebSocket = () => {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const { sessionId, addMessage, setTyping } = useKioniStore();

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return;

    const wsUrl = `ws://localhost:8000/ws/chat/${sessionId}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('Kioni WebSocket connected');
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        setLastMessage(data);
        handleMessage(data);
      } catch (err) {
        console.error('WebSocket message parse error:', err);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    ws.current.onclose = () => {
      console.log('Kioni WebSocket disconnected');
      setIsConnected(false);
      // Attempt reconnect after 3 seconds
      setTimeout(connect, 3000);
    };
  }, [sessionId]);

  const handleMessage = (data: WebSocketMessage) => {
    switch (data.type) {
      case 'chat':
        addMessage({
          id: Date.now().toString(),
          role: data.payload.role,
          content: data.payload.message,
          type: 'text',
          language: data.payload.language || 'mixed',
          timestamp: new Date()
        });
        setTyping(false);
        break;
      
      case 'typing':
        setTyping(data.payload.status === 'start');
        break;
      
      case 'system':
        addMessage({
          id: Date.now().toString(),
          role: 'system',
          content: data.payload.message,
          type: 'text',
          language: 'mixed',
          timestamp: new Date()
        });
        break;
      
      case 'error':
        console.error('Kioni error:', data.payload);
        break;
    }
  };

  const sendMessage = useCallback((type: string, payload: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type, payload }));
    } else {
      console.warn('WebSocket not connected');
    }
  }, []);

  const sendChat = useCallback((message: string) => {
    sendMessage('chat', {
      message,
      session_id: sessionId
    });
    setTyping(true);
  }, [sendMessage, sessionId, setTyping]);

  const sendVoice = useCallback((audioBase64: string) => {
    sendMessage('voice', {
      audio: audioBase64,
      session_id: sessionId
    });
  }, [sendMessage, sessionId]);

  const sendVision = useCallback((imageBase64: string) => {
    sendMessage('vision', {
      image: imageBase64,
      session_id: sessionId
    });
  }, [sendMessage, sessionId]);

  useEffect(() => {
    connect();
    
    return () => {
      ws.current?.close();
    };
  }, [connect]);

  return {
    isConnected,
    lastMessage,
    sendChat,
    sendVoice,
    sendVision,
    connect
  };
};