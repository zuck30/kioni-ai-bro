import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Camera, CameraOff } from 'lucide-react';
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
      <div className="p-4 bg-red-50 text-red-600 text-center">
        <CameraOff className="mx-auto mb-2" />
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="relative bg-black">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-48 object-cover"
      />
      <canvas ref={canvasRef} className="hidden" />
      
      {isActive && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute top-2 right-2 flex items-center gap-2 bg-black/50 text-white px-3 py-1 rounded-full text-xs"
        >
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
          <span>Anakutazama (Watching)</span>
        </motion.div>
      )}

      <div className="absolute bottom-2 left-2 text-white/70 text-xs">
        <Camera size={14} className="inline mr-1" />
        Frame sent every 5s
      </div>
    </div>
  );
};

export default CameraFeed;