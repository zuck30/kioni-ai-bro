import React from 'react';
import { motion } from 'framer-motion';
import { useKioniStore } from '../../store/kioniStore';
import { Mood } from '../../store/types';
import axios from 'axios';
import { Coffee, Sparkles, Brain, PartyPopper, Handshake, Zap } from 'lucide-react';
import { API_URL } from '../../api/config';

const moods: { id: Mood; name: string; description: string; icon: React.ReactNode }[] = [
  { id: 'poa', name: 'Poa', description: 'Chill & relaxed', icon: <Coffee size={24} /> },
  { id: 'safi', name: 'Safi', description: 'Good vibes', icon: <Sparkles size={24} /> },
  { id: 'mzito', name: 'Mzito', description: 'Serious & thoughtful', icon: <Brain size={24} /> },
  { id: 'mchekeshaji', name: 'Mchekeshaji', description: 'Funny & energetic', icon: <PartyPopper size={24} /> },
  { id: 'mshauri', name: 'Mshauri', description: 'Supportive advisor', icon: <Handshake size={24} /> },
  { id: 'shughuli', name: 'Shughuli', description: 'Busy mode', icon: <Zap size={24} /> }
];

const MoodSettings: React.FC = () => {
  const { currentMood, urafiki, ucheshi, hekima, msaada, updatePersonality } = useKioniStore();

  const handleMoodChange = async (mood: Mood) => {
    updatePersonality({ currentMood: mood });
    
    try {
      await axios.post(`${API_URL}/api/hali/update`, {
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
    <div className="p-6 space-y-6">
      <h3 className="font-bold text-slate-800 mb-4 font-mono uppercase tracking-widest text-xs opacity-60">Hali ya Kioni (Kioni's Mood)</h3>
      
      {/* Mood Selection */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
        {moods.map((mood) => (
          <motion.button
            key={mood.id}
            onClick={() => handleMoodChange(mood.id)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={`p-3 rounded-xl border transition-all duration-300 flex flex-col items-center text-center ${
              currentMood === mood.id
                ? 'border-cyan-500 bg-cyan-50 text-cyan-600 shadow-sm'
                : 'border-slate-100 hover:border-slate-200 bg-white/40 text-slate-400'
            }`}
          >
            <div className={`mb-2 ${currentMood === mood.id ? 'text-cyan-600' : 'text-slate-400'}`}>{mood.icon}</div>
            <div className="font-bold text-[10px] uppercase tracking-tighter">{mood.name}</div>
          </motion.button>
        ))}
      </div>

      {/* Personality Sliders */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-6 border-t border-slate-100">
        {[
          { key: 'urafiki', label: 'Urafiki (Friendliness)', value: urafiki, color: 'bg-pink-400' },
          { key: 'ucheshi', label: 'Ucheshi (Humor)', value: ucheshi, color: 'bg-yellow-400' },
          { key: 'hekima', label: 'Hekima (Wisdom)', value: hekima, color: 'bg-purple-400' },
          { key: 'msaada', label: 'Msaada (Support)', value: msaada, color: 'bg-emerald-400' }
        ].map((trait) => (
          <div key={trait.key} className="space-y-2">
            <div className="flex justify-between text-[10px] font-mono uppercase tracking-wider text-slate-400">
              <span>{trait.label}</span>
              <span className="text-cyan-600/70">{trait.value}%</span>
            </div>
            <div className="relative h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${trait.value}%` }}
                className={`absolute top-0 left-0 h-full ${trait.color}`}
              />
              <input
                type="range"
                min="0"
                max="100"
                value={trait.value}
                onChange={(e) => handleSliderChange(trait.key, parseInt(e.target.value))}
                className="absolute top-0 left-0 w-full h-full opacity-0 cursor-pointer z-10"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MoodSettings;