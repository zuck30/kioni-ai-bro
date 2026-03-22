import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useKioniStore } from '../../store/kioniStore';
import { Send, Mic, Settings } from 'lucide-react';
import MessageBubble from './MessageBubble';
import InputArea from './InputArea';
import KioniSVG from '../KioniCharacter/KioniSVG';
import VoiceControl from '../Sauti/VoiceControl';
import MoodSettings from '../Hali/MoodSettings';

const ChatInterface: React.FC = () => {
  const { messages, isTyping, addMessage, sessionId, currentGreeting } = useKioniStore();
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
          timestamp: new Date(),
          audioUrl: data.payload.audio ? `data:audio/wav;base64,${data.payload.audio}` : undefined
        });

        if (data.payload.audio) {
          const audio = new Audio(`data:audio/wav;base64,${data.payload.audio}`);
          audio.play().catch(e => console.error("Audio playback failed:", e));
        }

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
    <div className="flex h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      {/* Left Panel - Kioni Character (Hidden on mobile) */}
      <div className="hidden lg:flex lg:w-1/3 xl:w-1/4 flex-col items-center justify-center p-8 border-r border-slate-800 bg-slate-900/50 backdrop-blur-xl">
        <div className="w-full h-2/3 relative">
          <KioniSVG />
        </div>
        <div className="mt-8 text-center">
          <h2 className="text-3xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">KIONI</h2>
          <p className="text-slate-400 font-medium tracking-widest uppercase text-xs mt-2">Personal Bro Engine</p>
        </div>
      </div>

      {/* Right Panel - Chat */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-950">
        {/* Header */}
        <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 p-4 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <div className="lg:hidden w-10 h-10 bg-slate-800 border border-cyan-500/30 rounded-full flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.2)]">
              <span className="text-cyan-400 font-bold">K</span>
            </div>
            <div className="min-w-0">
              <h1 className="font-bold text-slate-100 truncate">Kioni Chat</h1>
              <p className="text-[10px] text-cyan-500/70 font-mono uppercase tracking-wider">
                {currentGreeting}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={`p-2 rounded-full transition-all duration-300 ${
                showSettings
                  ? 'bg-cyan-500 text-slate-950 shadow-[0_0_15px_rgba(6,182,212,0.5)]'
                  : 'bg-slate-800 text-slate-300 hover:text-cyan-400'
              }`}
            >
              <Settings size={20} />
            </button>
          </div>
        </header>

        {/* Settings Panel */}
        <AnimatePresence>
          {showSettings && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md overflow-hidden"
            >
              <MoodSettings />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-3 text-cyan-500/80 font-mono text-xs ml-2"
            >
              <div className="flex gap-1.5">
                <motion.div
                  className="w-1.5 h-1.5 bg-cyan-500 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.8)]"
                  animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 0.8, repeat: Infinity, delay: 0 }}
                />
                <motion.div
                  className="w-1.5 h-1.5 bg-cyan-500 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.8)]"
                  animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 0.8, repeat: Infinity, delay: 0.2 }}
                />
                <motion.div
                  className="w-1.5 h-1.5 bg-cyan-500 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.8)]"
                  animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 0.8, repeat: Infinity, delay: 0.4 }}
                />
              </div>
              <span className="tracking-widest uppercase">Kioni anawaza...</span>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-slate-800 bg-slate-900/50 backdrop-blur-xl p-4 sm:p-6">
          <div className="flex items-end gap-3 max-w-5xl mx-auto relative">
            <div className="flex-shrink-0 mb-1">
              <VoiceControl />
            </div>
            <InputArea
              value={inputValue}
              onChange={setInputValue}
              onSend={sendMessage}
              placeholder="Sema na Kioni... (Type message)"
            />
            <button
              onClick={sendMessage}
              disabled={!inputValue.trim()}
              className="flex-shrink-0 p-3.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 rounded-xl disabled:opacity-30 disabled:hover:bg-cyan-600 transition-all duration-300 shadow-[0_0_20px_rgba(6,182,212,0.2)] hover:shadow-[0_0_25px_rgba(6,182,212,0.4)] mb-1"
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