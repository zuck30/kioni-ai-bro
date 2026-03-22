import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Square } from 'lucide-react';
import { useKioniStore } from '../../store/kioniStore';
import axios from 'axios';

const VoiceControl: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const { setListening, sessionId, addMessage } = useKioniStore();

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
        await sendAudioToServer(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.current.start();
      setIsRecording(true);
      setListening(true);

      // Simulate audio level visualization
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const microphone = audioContext.createMediaStreamSource(stream);
      microphone.connect(analyser);
      analyser.fftSize = 256;
      
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      
      const updateLevel = () => {
        if (!isRecording) return;
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        setAudioLevel(average);
        requestAnimationFrame(updateLevel);
      };
      updateLevel();

    } catch (err) {
      console.error('Recording error:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
      setListening(false);
      setAudioLevel(0);
    }
  };

  const sendAudioToServer = async (audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    formData.append('session_id', sessionId);

    try {
      const response = await axios.post('http://localhost:8000/api/voice/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // Add user transcription
      addMessage({
        id: Date.now().toString(),
        role: 'user',
        content: response.data.transcription,
        type: 'voice',
        language: response.data.detected_language,
        timestamp: new Date()
      });

      // Add Kioni's response
      addMessage({
        id: (Date.now() + 1).toString(),
        role: 'kioni',
        content: response.data.kioni_response,
        type: 'voice',
        language: 'mixed',
        timestamp: new Date(),
        audioUrl: response.data.audio_response ? `data:audio/wav;base64,${response.data.audio_response}` : undefined
      });

      // Play audio response
      if (response.data.audio_response) {
        const audio = new Audio(`data:audio/wav;base64,${response.data.audio_response}`);
        audio.play();
      }

    } catch (err) {
      console.error('Voice processing error:', err);
      setIsRecording(false);
      setListening(false);
      setAudioLevel(0);
      alert("Shida na sauti. Jaribu tena baada ya muda kidogo.");
    }
  };

  return (
    <div className="relative group">
      <motion.button
        onClick={isRecording ? stopRecording : startRecording}
        whileTap={{ scale: 0.95 }}
        className={`p-3.5 rounded-xl transition-all duration-500 shadow-sm ${
          isRecording 
            ? 'bg-red-500 text-white'
            : 'bg-white text-cyan-600 hover:text-cyan-700 border border-slate-200'
        }`}
      >
        {isRecording ? <Square size={20} fill="currentColor" /> : <Mic size={20} />}
      </motion.button>

      {/* Audio Level Indicator */}
      <AnimatePresence>
        {isRecording && (
          <>
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 + audioLevel / 100 }}
              exit={{ opacity: 0, scale: 0.5 }}
              className="absolute -inset-1 rounded-xl border-2 border-red-500/50 pointer-events-none"
            />
          </>
        )}
      </AnimatePresence>

      {isRecording && (
        <span className="absolute -top-10 left-1/2 -translate-x-1/2 text-[10px] font-mono font-bold text-red-500 uppercase tracking-widest whitespace-nowrap bg-white/80 backdrop-blur-md px-2 py-1 rounded border border-red-200 shadow-sm">
          Live Recording
        </span>
      )}
    </div>
  );
};

export default VoiceControl;