import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useKioniStore } from '../../store/kioniStore';
import { Send, Camera, Settings, Cpu, ChevronDown, ChevronUp } from 'lucide-react';
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
  const [showKioniOnMobile, setShowKioniOnMobile] = useState(true);
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
    <div className="flex h-screen bg-[#050505] text-slate-200 overflow-hidden">
      {/* Left Panel - Kioni Character (Visible on LG screens) */}
      <div className="hidden lg:flex lg:w-1/3 flex-col items-center justify-center p-8 border-r border-cyan-500/10 bg-slate-950/50 backdrop-blur-xl relative">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(6,182,212,0.05)_0%,transparent_70%)]" />
        <div className="w-full h-2/3 relative z-10">
          <KioniSVG />
        </div>
        <div className="mt-8 text-center z-10">
          <h2 className="text-4xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
            KIONI
          </h2>
          <p className="text-cyan-500/60 font-mono text-sm mt-2 uppercase tracking-[0.3em]">AI OS v2.0</p>
        </div>
      </div>

      {/* Right Panel - Chat */}
      <div className="flex-1 flex flex-col relative h-full">
        {/* Header */}
        <header className="glass-header z-20 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="lg:hidden flex items-center justify-center w-10 h-10 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400">
              <Cpu size={20} className="animate-pulse" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-tight">System Terminal</h1>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
                <p className="text-[10px] text-slate-400 uppercase tracking-widest font-mono">
                  {useKioniStore.getState().currentGreeting}
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowKioniOnMobile(!showKioniOnMobile)}
              className="lg:hidden p-2 rounded-lg border border-slate-800 text-slate-400 hover:text-cyan-400"
              aria-label="Toggle Kioni"
            >
              {showKioniOnMobile ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </button>
            <button
              onClick={() => useKioniStore.getState().toggleCamera()}
              className={`p-2 rounded-lg transition-all duration-300 border ${
                cameraEnabled ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.3)]' : 'border-slate-800 text-slate-400'
              }`}
              aria-label="Toggle Camera"
            >
              <Camera size={20} />
            </button>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={`p-2 rounded-lg border transition-all duration-300 ${
                showSettings ? 'bg-blue-500/20 border-blue-500 text-blue-400' : 'border-slate-800 text-slate-400'
              }`}
              aria-label="Settings"
            >
              <Settings size={20} />
            </button>
          </div>
        </header>

        {/* Mobile Kioni Character */}
        <AnimatePresence>
          {showKioniOnMobile && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="lg:hidden border-b border-cyan-500/10 bg-slate-950/30 overflow-hidden"
            >
              <div className="h-48 w-full">
                <KioniSVG />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Camera Feed (if enabled) */}
        <AnimatePresence>
          {cameraEnabled && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="border-b border-cyan-500/20"
            >
              <CameraFeed />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Settings Panel */}
        <AnimatePresence>
          {showSettings && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="absolute top-20 right-4 left-4 z-30 glass-panel rounded-2xl shadow-2xl overflow-hidden max-h-[80vh] overflow-y-auto"
            >
              <MoodSettings />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center p-8">
              <div className="w-16 h-16 rounded-full border border-cyan-500/20 flex items-center justify-center mb-4 text-cyan-500/40">
                <Cpu size={32} />
              </div>
              <h3 className="text-xl font-bold text-slate-400">System Ready</h3>
              <p className="text-slate-500 max-w-xs mt-2 text-sm font-mono">
                Initiate communication with Kioni. Language protocols: Swahili, Sheng, English.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          {isTyping && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-3 text-cyan-500/60 font-mono text-xs"
            >
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-1.5 h-1.5 bg-cyan-500 rounded-full"
                    animate={{ opacity: [0.2, 1, 0.2] }}
                    transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                  />
                ))}
              </div>
              <span className="tracking-widest uppercase">Kioni anachakata...</span>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-gradient-to-t from-black via-black/80 to-transparent">
          <div className="max-w-4xl mx-auto flex items-end gap-2 bg-slate-900/50 border border-slate-800 p-2 rounded-2xl backdrop-blur-xl focus-within:border-cyan-500/50 transition-all">
            <VoiceControl />
            <InputArea
              value={inputValue}
              onChange={setInputValue}
              onSend={sendMessage}
              placeholder="Andika ujumbe hapa..."
            />
            <button
              onClick={sendMessage}
              disabled={!inputValue.trim()}
              className="p-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl disabled:opacity-30 disabled:grayscale transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
            >
              <Send size={20} />
            </button>
          </div>
          <p className="text-center text-[8px] text-slate-600 mt-2 uppercase tracking-[0.2em] font-mono">
            Secure Connection established // End-to-End Encryption
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
