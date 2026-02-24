import { useCallback } from 'react';
import { useKioniStore } from '../store/kioniStore';
import { Mood } from '../store/types';
import axios from 'axios';

export const useKioniPersonality = () => {
  const { 
    currentMood, 
    urafiki, 
    ucheshi, 
    hekima, 
    msaada,
    updatePersonality 
  } = useKioniStore();

  const setMood = useCallback(async (mood: Mood) => {
    updatePersonality({ currentMood: mood });
    
    try {
      await axios.post('http://localhost:8000/api/hali/update', {
        mode: mood
      });
    } catch (err) {
      console.error('Failed to update mood:', err);
    }
  }, [updatePersonality]);

  const updateTrait = useCallback(async (trait: 'urafiki' | 'ucheshi' | 'hekima' | 'msaada', value: number) => {
    updatePersonality({ [trait]: value });
    
    try {
      await axios.post('http://localhost:8000/api/hali/update', {
        [trait]: value
      });
    } catch (err) {
      console.error('Failed to update trait:', err);
    }
  }, [updatePersonality]);

  const getMoodDescription = useCallback((mood: Mood): string => {
    const descriptions: Record<Mood, string> = {
      poa: 'Chill and relaxed - Kioni is your laid-back bro',
      safi: 'Good vibes only - Positive and upbeat',
      mzito: 'Serious and thoughtful - Deep conversations mode',
      mchekeshaji: 'Funny and energetic - Celebration mode',
      mshauri: 'Supportive advisor - Here to help with problems',
      shughuli: 'Busy but available - Quick and efficient'
    };
    return descriptions[mood];
  }, []);

  const getCurrentGreeting = useCallback((): string => {
    const hour = new Date().getHours();
    
    if (hour < 10) return 'Habari za asubuhi';
    if (hour < 16) return 'Habari za mchana';
    if (hour < 19) return 'Habari za jioni';
    return 'Habari za usiku';
  }, []);

  return {
    currentMood,
    urafiki,
    ucheshi,
    hekima,
    msaada,
    setMood,
    updateTrait,
    getMoodDescription,
    getCurrentGreeting,
    personality: {
      currentMood,
      urafiki,
      ucheshi,
      hekima,
      msaada
    }
  };
};