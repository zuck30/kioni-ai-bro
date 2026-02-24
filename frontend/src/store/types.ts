export type Language = 'sw' | 'en' | 'sheng' | 'mixed';
export type Mood = 'poa' | 'safi' | 'mzito' | 'mchekeshaji' | 'mshauri' | 'shughuli';

export interface KioniState {
  currentMood: Mood;
  urafiki: number;
  ucheshi: number;
  hekima: number;
  msaada: number;
  isOnline: boolean;
  isTyping: boolean;
  isListening: boolean;
  isSpeaking: boolean;
  cameraEnabled: boolean;
  currentGreeting: string;
  timeOfDay: string;
}

export interface Message {
  id: string;
  role: 'user' | 'kioni' | 'system';
  content: string;
  type: 'text' | 'voice' | 'image';
  language: Language;
  timestamp: Date;
  audioUrl?: string;
}

export interface VisionData {
  description: string;
  swahiliContext: string;
  objects: Array<{
    object: string;
    meaning: string;
    culturalSignificance: string;
  }>;
  moodSuggestion: Mood;
}