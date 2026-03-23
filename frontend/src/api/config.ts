/**
 * Kioni Frontend API Configuration
 *
 * In development, these point to localhost:8000.
 * In production (Netlify), these should be set as environment variables.
 */

const getApiUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  return 'http://localhost:8000';
};

const getWsUrl = () => {
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL;
  }
  // If API URL is provided but not WS, try to derive it
  const apiUrl = getApiUrl();
  if (apiUrl.startsWith('https://')) {
    return apiUrl.replace('https://', 'wss://') + '/ws/chat';
  } else if (apiUrl.startsWith('http://')) {
    return apiUrl.replace('http://', 'ws://') + '/ws/chat';
  }
  return 'ws://localhost:8000/ws/chat';
};

export const API_URL = getApiUrl();
export const WS_URL = getWsUrl();
