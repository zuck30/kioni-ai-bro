import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useKioniStore } from '../../store/kioniStore';
import { kioniColors } from './kitenge-patterns/colors';

const KioniSVG: React.FC = () => {
  const { currentMood, isTyping, isSpeaking, isListening, isOnline } = useKioniStore();
  const svgRef = useRef<SVGSVGElement>(null);

  // Dynamic colors based on mood
  const getMoodColors = () => {
    switch (currentMood) {
      case 'poa': return { primary: kioniColors.earth.red, accent: kioniColors.kitenge.blue };
      case 'mzito': return { primary: kioniColors.earth.brown, accent: kioniColors.kitenge.purple };
      case 'mchekeshaji': return { primary: kioniColors.kitenge.orange, accent: kioniColors.kitenge.yellow };
      case 'mshauri': return { primary: kioniColors.earth.brown, accent: kioniColors.kitenge.green };
      default: return { primary: kioniColors.earth.red, accent: kioniColors.kitenge.blue };
    }
  };

  const colors = getMoodColors();

  // Animation variants
  const swayVariants = {
    idle: {
      rotate: [0, 2, -2, 0],
      transition: { duration: 4, repeat: Infinity, ease: "easeInOut" }
    },
    talking: {
      scale: [1, 1.02, 1],
      transition: { duration: 0.5, repeat: Infinity }
    },
    listening: {
      rotate: [0, -5, 5, 0],
      transition: { duration: 2, repeat: Infinity }
    }
  };

  const patternVariants = {
    idle: {
      opacity: [0.8, 1, 0.8],
      transition: { duration: 3, repeat: Infinity }
    },
    active: {
      opacity: 1,
      scale: [1, 1.05, 1],
      transition: { duration: 0.5, repeat: Infinity }
    }
  };

  const currentVariant = isSpeaking ? 'talking' : isListening ? 'listening' : 'idle';

  return (
    <div className="relative w-full h-full flex items-center justify-center">
      <motion.svg
        ref={svgRef}
        viewBox="0 0 400 500"
        className="w-full h-full max-w-md"
        initial="idle"
        animate={currentVariant}
        variants={swayVariants}
      >
        <defs>
          {/* Kitenge Pattern 1: Geometric */}
          <pattern id="kitenge1" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
            <rect width="40" height="40" fill={colors.primary} />
            <circle cx="20" cy="20" r="10" fill={colors.accent} opacity="0.6" />
            <path d="M0,0 L40,40 M40,0 L0,40" stroke={kioniColors.gold} strokeWidth="2" opacity="0.3" />
          </pattern>

          {/* Kitenge Pattern 2: Waves */}
          <pattern id="kitenge2" x="0" y="0" width="60" height="20" patternUnits="userSpaceOnUse">
            <rect width="60" height="20" fill={colors.accent} />
            <path d="M0,10 Q15,0 30,10 T60,10" fill="none" stroke={colors.primary} strokeWidth="3" />
          </pattern>

          {/* Gradient for depth */}
          <radialGradient id="glow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={colors.accent} stopOpacity="0.3" />
            <stop offset="100%" stopColor="transparent" stopOpacity="0" />
          </radialGradient>

          {/* Filter for fabric texture */}
          <filter id="fabric">
            <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" result="noise" />
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="2" />
          </filter>
        </defs>

        {/* Background Aura */}
        <motion.circle
          cx="200"
          cy="250"
          r="180"
          fill="url(#glow)"
          variants={patternVariants}
          animate={isSpeaking ? 'active' : 'idle'}
        />

        {/* Main Body - Abstract Kanga shape */}
        <motion.path
          d="M100,150 Q200,100 300,150 Q320,250 300,350 Q200,400 100,350 Q80,250 100,150"
          fill="url(#kitenge1)"
          stroke={colors.primary}
          strokeWidth="3"
          filter="url(#fabric)"
        />

        {/* Secondary Pattern Layer */}
        <motion.path
          d="M120,180 Q200,140 280,180 Q290,250 280,320 Q200,360 120,320 Q110,250 120,180"
          fill="url(#kitenge2)"
          opacity="0.7"
        />

        {/* Face Area - Abstract but expressive */}
        <g transform="translate(200, 220)">
          {/* Eyes */}
          <motion.g
            animate={isListening ? { scaleY: [1, 0.3, 1] } : {}}
            transition={{ duration: 0.2, repeat: isListening ? Infinity : 0, repeatDelay: 3 }}
          >
            <ellipse cx="-40" cy="0" rx="20" ry="25" fill={kioniColors.earth.brown} />
            <ellipse cx="40" cy="0" rx="20" ry="25" fill={kioniColors.earth.brown} />
            
            {/* Pupils - follow interaction */}
            <motion.circle 
              cx="-40" 
              cy="0" 
              r="8" 
              fill={kioniColors.gold}
              animate={isTyping ? { x: [-5, 5, -5] } : {}}
              transition={{ duration: 1, repeat: Infinity }}
            />
            <motion.circle 
              cx="40" 
              cy="0" 
              r="8" 
              fill={kioniColors.gold}
              animate={isTyping ? { x: [-5, 5, -5] } : {}}
              transition={{ duration: 1, repeat: Infinity }}
            />
          </motion.g>

          {/* Expression lines - change with mood */}
          {currentMood === 'mchekeshaji' && (
            <motion.path
              d="M-60,40 Q0,80 60,40"
              fill="none"
              stroke={kioniColors.earth.brown}
              strokeWidth="4"
              strokeLinecap="round"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
            />
          )}
          
          {currentMood === 'mzito' && (
            <motion.path
              d="M-40,60 Q0,40 40,60"
              fill="none"
              stroke={kioniColors.earth.brown}
              strokeWidth="3"
              strokeLinecap="round"
            />
          )}

          {/* Decorative elements - Maasai bead inspired */}
          <motion.circle
            cx="0"
            cy="-60"
            r="15"
            fill={kioniColors.kitenge.red}
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          >
            <animateTransform
              attributeName="transform"
              type="rotate"
              from="0 0 -60"
              to="360 0 -60"
              dur="20s"
              repeatCount="indefinite"
            />
          </motion.circle>
        </g>

        {/* Kanga Border - bottom */}
        <rect x="80" y="380" width="240" height="40" fill={colors.primary} opacity="0.8" />
        <text
          x="200"
          y="405"
          textAnchor="middle"
          fill={kioniColors.gold}
          fontSize="14"
          fontFamily="serif"
          fontStyle="italic"
        >
          "Kutoa ni moyo"
        </text>

        {/* Acacia silhouette - subtle background */}
        <path
          d="M50,400 Q100,350 150,380 T250,370 T350,400"
          fill="none"
          stroke={colors.primary}
          strokeWidth="2"
          opacity="0.2"
        />
      </motion.svg>

      {/* Status Indicator */}
      <div className="absolute bottom-4 right-4 flex items-center gap-2">
        <motion.div
          className={`w-3 h-3 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}`}
          animate={isTyping ? { scale: [1, 1.2, 1] } : {}}
          transition={{ duration: 0.5, repeat: Infinity }}
        />
        <span className="text-xs text-amber-800 font-medium">
          {isTyping ? 'Anawaza...' : isListening ? 'Anaskiliza...' : 'Bro, Nipo Online'}
        </span>
      </div>
    </div>
  );
};

export default KioniSVG;