import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Camera, CameraOff, Eye } from 'lucide-react';
import { useKioniStore } from '../../store/kioniStore';
import axios from 'axios';

const CameraFeed: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { sessionId, addMessage } = useKioniStore();

  useEffect(() => {
    let stream: MediaStream | null = null;
    let interval: ReturnType<typeof setInterval>;

    const startCamera = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: 640, 
            height: 480,
            facingMode: "user"
          } 
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setIsActive(true);
          
          // Send frame every 5 seconds for context
          interval = setInterval(captureAndSend, 5000);
        }
      } catch (err) {
        setError('Camera inapatikana (Camera not available)');
        console.error('Camera error:', err);
      }
    };

    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      if (interval) {
        clearInterval(interval);
      }
    };
  }, []);

  const captureAndSend = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (!context) return;

    // Draw video frame to canvas
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);

    // Convert to base64
    const imageBase64 = canvas.toDataURL('image/jpeg', 0.7).split(',')[1];

    try {
      const response = await axios.post('http://localhost:8000/api/vision/camera-frame', {
        frame_base64: imageBase64,
        session_id: sessionId
      });

      if (response.data.suggested_comment) {
        addMessage({
          id: `vision_${Date.now()}`,
          role: 'kioni',
          content: response.data.suggested_comment,
          type: 'text',
          language: 'mixed',
          timestamp: new Date()
        });
      }
    } catch (err) {
      console.error('Vision API error:', err);
    }
  };

  if (error) {
    return (
      <div className="p-8 bg-slate-900 border border-red-500/20 text-red-400 text-center rounded-2xl">
        <CameraOff className="mx-auto mb-3" size={32} />
        <p className="text-sm font-mono uppercase tracking-widest">{error}</p>
      </div>
    );
  }

  return (
    <div className="relative bg-black rounded-2xl overflow-hidden border border-white/5 shadow-2xl">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-48 md:h-64 object-cover opacity-80"
      />
      <canvas ref={canvasRef} className="hidden" />
      
      {/* Scanning effect overlay */}
      <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-cyan-500/10 via-transparent to-transparent bg-[length:100%_4px] animate-scan" />

      {isActive && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="absolute top-4 left-4 flex items-center gap-2 bg-black/60 backdrop-blur-md text-cyan-400 border border-cyan-500/30 px-3 py-1.5 rounded-lg text-[10px] font-mono uppercase tracking-widest"
        >
          <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.8)]" />
          <span>Live Vision Feed</span>
        </motion.div>
      )}

      <div className="absolute bottom-4 right-4 text-cyan-500/50 text-[10px] font-mono flex items-center gap-2">
        <Eye size={12} />
        Analyzing environment...
      </div>
    </div>
  );
};

export default CameraFeed;
