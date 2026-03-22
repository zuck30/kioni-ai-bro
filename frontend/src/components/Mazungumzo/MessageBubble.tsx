import React from 'react';
import { motion } from 'framer-motion';
import { Message } from '../../store/types';
import { User, Bot } from 'lucide-react';

interface Props {
  message: Message;
}

const MessageBubble: React.FC<Props> = ({ message }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  if (isSystem) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex justify-center my-6"
      >
        <span className="px-5 py-1.5 bg-white/40 backdrop-blur-md border border-slate-200 text-slate-500 text-[10px] font-mono uppercase tracking-[0.2em] rounded-full">
          {message.content}
        </span>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} w-full mb-4`}
    >
      <div className={`flex items-start gap-3 max-w-[85%] sm:max-w-[75%] ${isUser ? 'flex-row-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm ${
          isUser
            ? 'bg-gradient-to-br from-cyan-600 to-blue-700 text-white'
            : 'bg-white border border-slate-200 text-cyan-600'
        }`}>
          {isUser ? <User size={18} /> : <Bot size={18} />}
        </div>

        {/* Content */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-4 py-3 rounded-2xl shadow-sm backdrop-blur-sm ${
            isUser
              ? 'bg-white/80 text-slate-900 rounded-tr-none border border-cyan-100'
              : 'bg-white/90 border border-slate-100 text-slate-800 rounded-tl-none'
          }`}>
            <p className="text-[15px] leading-relaxed font-medium">{message.content}</p>
          </div>
          
          {/* Metadata */}
          <div className={`flex items-center gap-2 mt-1.5 px-1 text-[10px] font-mono uppercase tracking-tighter ${
            isUser ? 'text-cyan-600/70' : 'text-slate-400'
          }`}>
            <span>{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            {message.language !== 'en' && (
              <span className={`px-1.5 py-0.5 rounded-md border ${
                isUser ? 'bg-cyan-100/50 border-cyan-200/50' : 'bg-slate-50 border-slate-200'
              }`}>
                {message.language === 'sw' ? 'SWA' : message.language === 'sheng' ? 'SHG' : 'MIX'}
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble;