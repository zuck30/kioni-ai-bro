import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/kitenge-theme.css';

// Polyfill for regenerator-runtime (needed for async/await in some browsers)
import 'regenerator-runtime/runtime';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);