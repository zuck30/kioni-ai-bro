import React from 'react';
import { motion } from 'framer-motion';
import { useKioniStore } from '../../store/kioniStore';

const KioniSVG: React.FC = () => {
  const { currentMood, isTyping, isSpeaking, isListening, isOnline } = useKioniStore();

  // Dynamic colors based on mood - now using Jarvis-like palette
  const getMoodColors = () => {
    switch (currentMood) {
      case 'poa': return { primary: '#06b6d4', secondary: '#0891b2', glow: 'rgba(6, 182, 212, 0.5)' };
      case 'mzito': return { primary: '#3b82f6', secondary: '#1d4ed8', glow: 'rgba(59, 130, 246, 0.5)' };
      case 'mchekeshaji': return { primary: '#f59e0b', secondary: '#d97706', glow: 'rgba(245, 158, 11, 0.5)' };
      case 'mshauri': return { primary: '#10b981', secondary: '#047857', glow: 'rgba(16, 185, 129, 0.5)' };
      case 'shughuli': return { primary: '#ef4444', secondary: '#b91c1c', glow: 'rgba(239, 68, 68, 0.5)' };
      default: return { primary: '#06b6d4', secondary: '#0891b2', glow: 'rgba(6, 182, 212, 0.5)' };
    }
  };

  const colors = getMoodColors();

  return (
    <div className="relative w-full h-full flex items-center justify-center">
      {/* Hologram Base Glow */}
      <motion.div
        className="absolute w-64 h-64 rounded-full"
        style={{ background: `radial-gradient(circle, ${colors.glow} 0%, transparent 70%)` }}
        animate={{
          scale: isSpeaking ? [1, 1.2, 1] : [1, 1.1, 1],
          opacity: isOnline ? [0.3, 0.6, 0.3] : 0.1
        }}
        transition={{ duration: 3, repeat: Infinity }}
      />

      <motion.svg
        viewBox="0 0 400 400"
        className="w-full h-full max-w-sm z-10 filter drop-shadow-[0_0_15px_rgba(6,182,212,0.5)]"
        animate={{
          y: [0, -10, 0],
        }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      >
        <defs>
          <linearGradient id="orbGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={colors.primary} stopOpacity="0.8" />
            <stop offset="100%" stopColor={colors.secondary} stopOpacity="0.2" />
          </linearGradient>

          <filter id="neonGlow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Outer Ring */}
        <motion.circle
          cx="200"
          cy="200"
          r="150"
          fill="none"
          stroke={colors.primary}
          strokeWidth="2"
          strokeDasharray="10 5"
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        />

        {/* Inner Rotating Rings */}
        <motion.circle
          cx="200"
          cy="200"
          r="130"
          fill="none"
          stroke={colors.secondary}
          strokeWidth="1"
          strokeDasharray="5 15"
          animate={{ rotate: -360 }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
        />

        {/* Main AI Orb */}
        <motion.circle
          cx="200"
          cy="200"
          r="100"
          fill="url(#orbGradient)"
          stroke={colors.primary}
          strokeWidth="1"
          animate={isSpeaking ? {
            scale: [1, 1.05, 1],
            strokeWidth: [1, 3, 1]
          } : {}}
          transition={{ duration: 0.5, repeat: Infinity }}
        />

        {/* Abstract Eyes / Visualizer */}
        <g transform="translate(200, 200)">
          {/* Left Eye Segment */}
          <motion.path
            d="M -50 -10 Q -30 -40 -10 -10"
            fill="none"
            stroke={colors.primary}
            strokeWidth="4"
            strokeLinecap="round"
            animate={isListening ? { scaleY: [1, 0.2, 1] } : {}}
            transition={{ duration: 2, repeat: Infinity }}
          />
          {/* Right Eye Segment */}
          <motion.path
            d="M 10 -10 Q 30 -40 50 -10"
            fill="none"
            stroke={colors.primary}
            strokeWidth="4"
            strokeLinecap="round"
            animate={isListening ? { scaleY: [1, 0.2, 1] } : {}}
            transition={{ duration: 2, repeat: Infinity }}
          />

          {/* Core Data Stream (Visualizer) */}
          <g transform="translate(-40, 30)">
            {[0, 1, 2, 3, 4].map((i) => (
              <motion.rect
                key={i}
                x={i * 20}
                y="0"
                width="4"
                height="20"
                fill={colors.primary}
                animate={isSpeaking || isTyping ? {
                  height: [10, 30, 10],
                  y: [-5, -15, -5]
                } : {
                  height: [15, 20, 15],
                }}
                transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.1 }}
              />
            ))}
          </g>
        </g>

        {/* Scanning Line */}
        <motion.line
          x1="100" y1="200" x2="300" y2="200"
          stroke={colors.primary}
          strokeWidth="1"
          opacity="0.5"
          animate={{
            y: [-80, 80, -80]
          }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        />
      </motion.svg>

      {/* Status Indicators */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-4 bg-slate-900/50 backdrop-blur-md px-4 py-2 rounded-full border border-cyan-500/30">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-cyan-500 shadow-[0_0_8px_#06b6d4]' : 'bg-red-500'}`} />
          <span className="text-[10px] uppercase tracking-widest text-cyan-500 font-bold">
            {isTyping ? 'Anachakata...' : isListening ? 'Anasikiliza...' : 'Kioni Active'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default KioniSVG;
