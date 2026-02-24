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
        className="flex justify-center my-4"
      >
        <span className="px-4 py-2 bg-amber-100/50 text-amber-700 text-sm rounded-full italic">
          {message.content}
        </span>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: isUser ? 20 : -20 }}
      animate={{ opacity: 1, x: 0 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`flex items-start gap-2 max-w-[80%] ${isUser ? 'flex-row-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-amber-600 text-white' : 'bg-amber-200 text-amber-800'
        }`}>
          {isUser ? <User size={16} /> : <Bot size={16} />}
        </div>

        {/* Content */}
        <div className={`px-4 py-3 rounded-2xl ${
          isUser 
            ? 'bg-amber-600 text-white rounded-br-none' 
            : 'bg-white border border-amber-200 text-amber-900 rounded-bl-none shadow-sm'
        }`}>
          <p className="text-sm leading-relaxed">{message.content}</p>
          
          {/* Metadata */}
          <div className={`flex items-center gap-2 mt-2 text-xs ${
            isUser ? 'text-amber-100' : 'text-amber-500'
          }`}>
            <span>{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
            {message.language !== 'en' && (
              <span className="px-1.5 py-0.5 bg-black/10 rounded">
                {message.language === 'sw' ? 'SW' : message.language === 'sheng' ? 'SH' : 'Mix'}
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble;