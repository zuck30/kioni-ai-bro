import React from 'react';
import { motion } from 'framer-motion';
import { Message } from '../../store/types';
import { User, Cpu, Globe } from 'lucide-react';

interface Props {
  message: Message;
}

const MessageBubble: React.FC<Props> = ({ message }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  if (isSystem) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex justify-center my-6"
      >
        <div className="px-6 py-1.5 border border-white/5 bg-white/5 text-slate-500 text-[10px] uppercase tracking-[0.2em] rounded-full font-mono">
          {message.content}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 group`}
    >
      <div className={`flex items-start gap-4 max-w-[85%] md:max-w-[70%] ${isUser ? 'flex-row-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 border transition-all duration-300 ${
          isUser
            ? 'bg-slate-900 border-slate-700 text-slate-400 group-hover:border-cyan-500/50'
            : 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.2)]'
        }`}>
          {isUser ? <User size={18} /> : <Cpu size={18} className="animate-pulse" />}
        </div>

        {/* Content */}
        <div className={`relative flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-5 py-3.5 rounded-2xl relative overflow-hidden transition-all duration-300 ${
            isUser
              ? 'bg-slate-900 border border-slate-700 text-slate-100 rounded-tr-none'
              : 'bg-slate-800/50 border border-white/10 text-cyan-50 backdrop-blur-md rounded-tl-none group-hover:bg-slate-800/80'
          }`}>
            {!isUser && (
              <div className="absolute top-0 left-0 w-1 h-full bg-cyan-500/50" />
            )}
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

            {/* Metadata */}
            <div className={`flex items-center gap-3 mt-3 text-[10px] font-mono tracking-wider ${
              isUser ? 'text-slate-500' : 'text-cyan-500/60'
            }`}>
              <span className="flex items-center gap-1">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              {message.language !== 'en' && (
                <span className="flex items-center gap-1 uppercase bg-black/30 px-1.5 py-0.5 rounded border border-white/5">
                  <Globe size={10} />
                  {message.language === 'sw' ? 'SWA' : message.language === 'sheng' ? 'SHG' : 'MIX'}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble;
