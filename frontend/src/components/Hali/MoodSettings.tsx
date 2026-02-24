import React from 'react';
import { motion } from 'framer-motion';
import { useKioniStore } from '../../store/kioniStore';
import { Mood } from '../../store/types';
import axios from 'axios';

const moods: { id: Mood; name: string; description: string; icon: string }[] = [
  { id: 'poa', name: 'Poa', description: 'Chill & relaxed', icon: '☕' },
  { id: 'safi', name: 'Safi', description: 'Good vibes', icon: '✨' },
  { id: 'mzito', name: 'Mzito', description: 'Serious & thoughtful', icon: '🧠' },
  { id: 'mchekeshaji', name: 'Mchekeshaji', description: 'Funny & energetic', icon: '🎉' },
  { id: 'mshauri', name: 'Mshauri', description: 'Supportive advisor', icon: '🤝' },
  { id: 'shughuli', name: 'Shughuli', description: 'Busy mode', icon: '⚡' }
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
    <div className="p-4 space-y-4">
      <h3 className="font-bold text-amber-900 mb-3">Hali ya Kioni (Kioni's Mood)</h3>
      
      {/* Mood Selection */}
      <div className="grid grid-cols-3 gap-2">
        {moods.map((mood) => (
          <motion.button
            key={mood.id}
            onClick={() => handleMoodChange(mood.id)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={`p-3 rounded-lg border-2 text-center transition-colors ${
              currentMood === mood.id
                ? 'border-amber-500 bg-amber-50 text-amber-900'
                : 'border-amber-200 hover:border-amber-300 text-amber-700'
            }`}
          >
            <div className="text-2xl mb-1">{mood.icon}</div>
            <div className="font-medium text-sm">{mood.name}</div>
            <div className="text-xs opacity-70">{mood.description}</div>
          </motion.button>
        ))}
      </div>

      {/* Personality Sliders */}
      <div className="space-y-3 pt-4 border-t border-amber-200">
        <h4 className="font-medium text-amber-800 text-sm">Personality Traits</h4>
        
        {[
          { key: 'urafiki', label: 'Urafiki (Friendliness)', value: urafiki, color: 'bg-pink-500' },
          { key: 'ucheshi', label: 'Ucheshi (Humor)', value: ucheshi, color: 'bg-yellow-500' },
          { key: 'hekima', label: 'Hekima (Wisdom)', value: hekima, color: 'bg-purple-500' },
          { key: 'msaada', label: 'Msaada (Support)', value: msaada, color: 'bg-green-500' }
        ].map((trait) => (
          <div key={trait.key} className="space-y-1">
            <div className="flex justify-between text-xs text-amber-700">
              <span>{trait.label}</span>
              <span>{trait.value}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={trait.value}
              onChange={(e) => handleSliderChange(trait.key, parseInt(e.target.value))}
              className="w-full h-2 bg-amber-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default MoodSettings;