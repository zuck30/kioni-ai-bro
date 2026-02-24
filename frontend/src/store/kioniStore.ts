import { create } from 'zustand';
import { KioniState, Message, Mood } from './types';

interface KioniStore extends KioniState {
  messages: Message[];
  sessionId: string;
  
  // Actions
  setMood: (mood: Mood) => void;
  setTyping: (typing: boolean) => void;
  setListening: (listening: boolean) => void;
  setSpeaking: (speaking: boolean) => void;
  toggleCamera: () => void;
  addMessage: (message: Message) => void;
  updatePersonality: (traits: Partial<Omit<KioniState, 'messages' | 'sessionId'>>) => void;
  clearMessages: () => void;
}

const generateSessionId = () => `kioni_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

export const useKioniStore = create<KioniStore>((set, get) => ({
  // Initial state
  currentMood: 'poa',
  urafiki: 80,
  ucheshi: 60,
  hekima: 70,
  msaada: 90,
  isOnline: true,
  isTyping: false,
  isListening: false,
  isSpeaking: false,
  cameraEnabled: false,
  currentGreeting: 'Habari!',
  timeOfDay: 'mchana',
  messages: [],
  sessionId: generateSessionId(),

  // Actions
  setMood: (mood) => set({ currentMood: mood }),
  
  setTyping: (typing) => set({ isTyping: typing }),
  
  setListening: (listening) => set({ isListening: listening }),
  
  setSpeaking: (speaking) => set({ isSpeaking: speaking }),
  
  toggleCamera: () => set((state) => ({ cameraEnabled: !state.cameraEnabled })),
  
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  
  updatePersonality: (traits) => set((state) => ({ ...state, ...traits })),
  
  clearMessages: () => set({ messages: [] }),
}));