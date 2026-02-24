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
    <div className="relative">
      <motion.button
        onClick={isRecording ? stopRecording : startRecording}
        whileTap={{ scale: 0.95 }}
        className={`p-3 rounded-full transition-colors ${
          isRecording 
            ? 'bg-red-500 text-white animate-pulse' 
            : 'bg-amber-100 text-amber-700 hover:bg-amber-200'
        }`}
      >
        {isRecording ? <Square size={20} /> : <Mic size={20} />}
      </motion.button>

      {/* Audio Level Indicator */}
      <AnimatePresence>
        {isRecording && (
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0 }}
            className="absolute -top-1 -right-1 -left-1 -bottom-1 rounded-full border-2 border-red-400"
            style={{
              transform: `scale(${1 + audioLevel / 200})`
            }}
          />
        )}
      </AnimatePresence>

      {isRecording && (
        <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs text-red-500 whitespace-nowrap">
          Rekodi... (Recording)
        </span>
      )}
    </div>
  );
};

export default VoiceControl;