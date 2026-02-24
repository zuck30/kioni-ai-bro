import { useState, useRef, useCallback } from 'react';
import { useKioniStore } from '../store/kioniStore';

interface UseVoiceReturn {
  isRecording: boolean;
  audioLevel: number;
  error: string | null;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<string | null>; // Returns base64 audio
  cancelRecording: () => void;
}

export const useVoice = (): UseVoiceReturn => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  
  const { setListening } = useKioniStore();

  const startRecording = useCallback(async () => {
    try {
      setError(null);
      audioChunks.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      });

      // Set up audio analysis for visualization
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const microphone = audioContext.createMediaStreamSource(stream);
      microphone.connect(analyser);
      analyser.fftSize = 256;
      analyserRef.current = analyser;

      // Start recording
      const recorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') 
          ? 'audio/webm' 
          : 'audio/mp4'
      });

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
        }
      };

      recorder.start(100); // Collect data every 100ms
      mediaRecorder.current = recorder;
      
      setIsRecording(true);
      setListening(true);

      // Start audio level monitoring
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      
      const updateLevel = () => {
        if (!isRecording) return;
        
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        setAudioLevel(average);
        
        animationFrameRef.current = requestAnimationFrame(updateLevel);
      };
      updateLevel();

    } catch (err) {
      console.error('Recording error:', err);
      setError('Microphone inapatikana (Microphone not available)');
      setIsRecording(false);
      setListening(false);
    }
  }, [isRecording, setListening]);

  const stopRecording = useCallback(async (): Promise<string | null> => {
    return new Promise((resolve) => {
      if (!mediaRecorder.current || !isRecording) {
        resolve(null);
        return;
      }

      // Stop animation frame
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }

      mediaRecorder.current.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { 
          type: mediaRecorder.current?.mimeType || 'audio/webm' 
        });
        
        // Convert to base64
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64 = (reader.result as string).split(',')[1];
          resolve(base64);
        };
        reader.readAsDataURL(audioBlob);

        // Stop all tracks
        const stream = mediaRecorder.current?.stream;
        stream?.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.current.stop();
      setIsRecording(false);
      setListening(false);
      setAudioLevel(0);
    });
  }, [isRecording, setListening]);

  const cancelRecording = useCallback(() => {
    if (mediaRecorder.current && isRecording) {
      const stream = mediaRecorder.current.stream;
      stream?.getTracks().forEach(track => track.stop());
      mediaRecorder.current.stop();
    }
    
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    
    setIsRecording(false);
    setListening(false);
    setAudioLevel(0);
    audioChunks.current = [];
  }, [isRecording, setListening]);

  return {
    isRecording,
    audioLevel,
    error,
    startRecording,
    stopRecording,
    cancelRecording
  };
};