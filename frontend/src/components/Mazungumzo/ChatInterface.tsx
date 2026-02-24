import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useKioniStore } from '../../store/kioniStore';
import { Send, Mic, Camera, Settings } from 'lucide-react';
import MessageBubble from './MessageBubble';
import InputArea from './InputArea';
import KioniSVG from '../KioniCharacter/KioniSVG';
import CameraFeed from '../Kamera/CameraFeed';
import VoiceControl from '../Sauti/VoiceControl';
import MoodSettings from '../Hali/MoodSettings';

const ChatInterface: React.FC = () => {
  const { messages, isTyping, addMessage, sessionId, cameraEnabled } = useKioniStore();
  const [inputValue, setInputValue] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const ws = useRef<WebSocket | null>(null);

  // WebSocket connection
  useEffect(() => {
    const wsUrl = `ws://localhost:8000/ws/chat/${sessionId}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('Connected to Kioni');
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.current?.close();
    };
  }, [sessionId]);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'chat':
        addMessage({
          id: Date.now().toString(),
          role: 'kioni',
          content: data.payload.message,
          type: 'text',
          language: data.payload.language,
          timestamp: new Date()
        });
        useKioniStore.getState().setTyping(false);
        break;
      case 'typing':
        useKioniStore.getState().setTyping(data.payload.status === 'start');
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
    }
  };

  const sendMessage = () => {
    if (!inputValue.trim() || !ws.current) return;

    const message = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: inputValue,
      type: 'text' as const,
      language: 'mixed' as const,
      timestamp: new Date()
    };

    addMessage(message);
    
    ws.current.send(JSON.stringify({
      type: 'chat',
      payload: {
        message: inputValue,
        session_id: sessionId
      }
    }));

    setInputValue('');
    useKioniStore.getState().setTyping(true);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50">
      {/* Left Panel - Kioni Character */}
      <div className="hidden lg:flex lg:w-1/3 flex-col items-center justify-center p-8 border-r border-amber-200 bg-white/50 backdrop-blur-sm">
        <div className="w-full h-2/3 relative">
          <KioniSVG />
        </div>
        <div className="mt-4 text-center">
          <h2 className="text-2xl font-bold text-amber-900">KIONI</h2>
          <p className="text-amber-700 italic">"Rafiki yako wa AI"</p>
        </div>
      </div>

      {/* Right Panel - Chat */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-md border-b border-amber-200 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="lg:hidden w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
              <span className="text-amber-800 font-bold">K</span>
            </div>
            <div>
              <h1 className="font-bold text-amber-900">Mazungumzo</h1>
              <p className="text-xs text-amber-600">
                {useKioniStore.getState().currentGreeting}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => useKioniStore.getState().toggleCamera()}
              className={`p-2 rounded-full transition-colors ${
                cameraEnabled ? 'bg-amber-500 text-white' : 'bg-amber-100 text-amber-700'
              }`}
            >
              <Camera size={20} />
            </button>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 rounded-full bg-amber-100 text-amber-700 hover:bg-amber-200"
            >
              <Settings size={20} />
            </button>
          </div>
        </header>

        {/* Camera Feed (if enabled) */}
        <AnimatePresence>
          {cameraEnabled && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="border-b border-amber-200"
            >
              <CameraFeed />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Settings Panel */}
        <AnimatePresence>
          {showSettings && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="border-b border-amber-200 bg-white/90"
            >
              <MoodSettings />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 text-amber-600"
            >
              <div className="flex gap-1">
                <motion.div
                  className="w-2 h-2 bg-amber-400 rounded-full"
                  animate={{ y: [0, -5, 0] }}
                  transition={{ duration: 0.5, repeat: Infinity, delay: 0 }}
                />
                <motion.div
                  className="w-2 h-2 bg-amber-400 rounded-full"
                  animate={{ y: [0, -5, 0] }}
                  transition={{ duration: 0.5, repeat: Infinity, delay: 0.1 }}
                />
                <motion.div
                  className="w-2 h-2 bg-amber-400 rounded-full"
                  animate={{ y: [0, -5, 0] }}
                  transition={{ duration: 0.5, repeat: Infinity, delay: 0.2 }}
                />
              </div>
              <span className="text-sm">Kioni anawaza...</span>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-amber-200 bg-white/80 backdrop-blur-md p-4">
          <div className="flex items-center gap-2 max-w-4xl mx-auto">
            <VoiceControl />
            <InputArea
              value={inputValue}
              onChange={setInputValue}
              onSend={sendMessage}
              placeholder="Andika ujumbe... (Type message)"
            />
            <button
              onClick={sendMessage}
              disabled={!inputValue.trim()}
              className="p-3 bg-amber-600 text-white rounded-full hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;