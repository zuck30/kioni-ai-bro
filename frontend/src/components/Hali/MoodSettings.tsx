import React from 'react';
import { motion } from 'framer-motion';
import { useKioniStore } from '../../store/kioniStore';
import { Mood } from '../../store/types';
import axios from 'axios';
import {
  Coffee,
  Sparkles,
  Brain,
  Laugh,
  HeartHandshake,
  Zap,
  Activity,
  Heart,
  Smile,
  ShieldCheck
} from 'lucide-react';

const moods: { id: Mood; name: string; description: string; icon: any; color: string }[] = [
  { id: 'poa', name: 'Poa', description: 'Chill & relaxed', icon: Coffee, color: 'text-cyan-400' },
  { id: 'safi', name: 'Safi', description: 'Good vibes', icon: Sparkles, color: 'text-yellow-400' },
  { id: 'mzito', name: 'Mzito', description: 'Serious & thoughtful', icon: Brain, color: 'text-blue-400' },
  { id: 'mchekeshaji', name: 'Mchekeshaji', description: 'Funny & energetic', icon: Laugh, color: 'text-orange-400' },
  { id: 'mshauri', name: 'Mshauri', description: 'Supportive advisor', icon: HeartHandshake, color: 'text-green-400' },
  { id: 'shughuli', name: 'Shughuli', description: 'Busy mode', icon: Zap, color: 'text-red-400' }
];

const MoodSettings: React.FC = () => {
  const { currentMood, urafiki, ucheshi, hekima, msaada, updatePersonality } = useKioniStore();

  const handleMoodChange = async (mood: Mood) => {
    updatePersonality({ currentMood: mood });
    
    try {
      await axios.post('http://localhost:8000/api/hali/update', {
        mode: mood
      });
    } catch (err) {
      console.error('Failed to update mood:', err);
    }
  };

  const handleSliderChange = (trait: string, value: number) => {
    updatePersonality({ [trait]: value });
  };

  return (
    <div className="p-6 space-y-8 bg-slate-950/80 backdrop-blur-xl border border-white/5 rounded-2xl">
      <div>
        <h3 className="text-xl font-bold text-white mb-1">Hali ya Kioni</h3>
        <p className="text-slate-400 text-xs uppercase tracking-widest font-mono">Current Personality State</p>
      </div>
      
      {/* Mood Selection */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {moods.map((mood) => (
          <motion.button
            key={mood.id}
            onClick={() => handleMoodChange(mood.id)}
            whileHover={{ scale: 1.02, backgroundColor: 'rgba(255,255,255,0.05)' }}
            whileTap={{ scale: 0.98 }}
            className={`p-4 rounded-xl border transition-all duration-300 flex flex-col items-center text-center ${
              currentMood === mood.id
                ? 'border-cyan-500 bg-cyan-500/10 shadow-[0_0_15px_rgba(6,182,212,0.2)]'
                : 'border-white/5 bg-white/5 hover:border-white/20'
            }`}
          >
            <mood.icon className={`mb-3 ${currentMood === mood.id ? mood.color : 'text-slate-400'}`} size={24} />
            <div className={`font-bold text-sm ${currentMood === mood.id ? 'text-white' : 'text-slate-300'}`}>
              {mood.name}
            </div>
            <div className="text-[10px] text-slate-500 mt-1 uppercase tracking-tighter">
              {mood.description}
            </div>
          </motion.button>
        ))}
      </div>

      {/* Personality Sliders */}
      <div className="space-y-6 pt-6 border-t border-white/5">
        <div className="flex items-center gap-2 mb-4">
          <Activity size={16} className="text-cyan-500" />
          <h4 className="font-bold text-white text-sm uppercase tracking-wider">Trait Calibration</h4>
        </div>
        
        {[
          { key: 'urafiki', label: 'Urafiki (Friendliness)', value: urafiki, icon: Heart, color: 'text-pink-500', accent: 'accent-pink-500' },
          { key: 'ucheshi', label: 'Ucheshi (Humor)', value: ucheshi, icon: Smile, color: 'text-yellow-500', accent: 'accent-yellow-500' },
          { key: 'hekima', label: 'Hekima (Wisdom)', value: hekima, icon: Brain, color: 'text-purple-500', accent: 'accent-purple-500' },
          { key: 'msaada', label: 'Msaada (Support)', value: msaada, icon: ShieldCheck, color: 'text-green-500', accent: 'accent-green-500' }
        ].map((trait) => (
          <div key={trait.key} className="space-y-3">
            <div className="flex justify-between items-center text-xs">
              <div className="flex items-center gap-2 text-slate-300">
                <trait.icon size={14} className={trait.color} />
                <span className="font-medium">{trait.label}</span>
              </div>
              <span className="font-mono text-cyan-500 bg-cyan-500/10 px-2 py-0.5 rounded text-[10px]">
                {trait.value}%
              </span>
            </div>
            <div className="relative group">
              <input
                type="range"
                min="0"
                max="100"
                value={trait.value}
                onChange={(e) => handleSliderChange(trait.key, parseInt(e.target.value))}
                className={`w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer ${trait.accent} hover:h-2 transition-all`}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MoodSettings;
