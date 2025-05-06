import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import GestureRecognition from './gesturerecognition';
import './App.css';

function App() {
  const [gestureResult, setGestureResult] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [detecting, setDetecting] = useState(false);
  const [progress, setProgress] = useState(0);

  const gesturePromptMap = {
    "Thumb_Up": "a peaceful forest landscape at sunrise, digital art",
    "Victory": "a futuristic cyberpunk city skyline at night, neon lights",
    "Open_Palm": "a surreal cosmic landscape with colorful nebulae and planets",
    "Closed_Fist": "a mighty dragon breathing fire on a mountain peak, fantasy art",
    "Pointing_Up": "a majestic castle floating in the clouds, dreamlike atmosphere"
  };

  const recognizeGesture = async (gestureName) => {
    if (isGenerating || !detecting) return;

    setDetecting(false);
    setIsGenerating(true);
    setGestureResult(`Detected: ${gestureName}`);
    setImageUrl('');
    setStatusMessage('Preparing prompt...');
    setProgress(0);

    const prompt = gesturePromptMap[gestureName];
    if (!prompt) {
      setGestureResult(`No prompt defined for ${gestureName}`);
      setIsGenerating(false);
      return;
    }

    try {
      setStatusMessage('Initializing connection...');
      
      // Create URL with query parameters
      const url = new URL('http://localhost:8000/api/generate-stream');
      url.searchParams.append('prompt', prompt);
      
      const eventSource = new EventSource(url.toString());

      eventSource.onopen = () => {
        setStatusMessage('Connected to server, starting generation...');
      };

      eventSource.onmessage = (event) => {
        try {
          if (!event.data) return;
          
          const data = JSON.parse(event.data);
          
          switch (data.event) {
            case 'status':
              setStatusMessage(data.data);
              break;
            case 'progress':
              setStatusMessage(`${data.data} (${Math.round(data.progress)}%)`);
              setProgress(data.progress);
              break;
            case 'complete':
              setImageUrl(data.image);
              setGestureResult(`Successfully generated: ${prompt}`);
              setStatusMessage('Generation complete!');
              setProgress(100);
              eventSource.close();
              setIsGenerating(false);
              break;
            case 'error':
              setGestureResult(`Generation error: ${data.data}`);
              setStatusMessage('Failed to generate image');
              setProgress(0);
              eventSource.close();
              setIsGenerating(false);
              break;
            default:
              console.warn('Unknown event type:', data.event);
          }
        } catch (e) {
          console.error('Error parsing event data:', e);
          setStatusMessage('Error processing server response');
        }
      };

      eventSource.onerror = (error) => {
        console.error('EventSource error:', error);
        if (eventSource.readyState === EventSource.CLOSED) {
          setStatusMessage('Connection closed');
        } else {
          setGestureResult('Connection to server failed');
          setStatusMessage('Network error - try again');
          setProgress(0);
          setIsGenerating(false);
        }
        eventSource.close();
      };

      // Cleanup function
      return () => {
        if (eventSource.readyState !== EventSource.CLOSED) {
          eventSource.close();
        }
      };

    } catch (error) {
      console.error('Initialization error:', error);
      setGestureResult(`Initialization failed: ${error.message}`);
      setStatusMessage('Failed to start generation');
      setProgress(0);
      setIsGenerating(false);
    }
  };

  const handleStartDetection = () => {
    if (isGenerating) return;
    setDetecting(true);
    setGestureResult('');
    setStatusMessage('Gesture detection started...');
    setProgress(0);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1 className="app-title">Gesture to Image Generator</h1>

        <div className="gesture-container">
          <GestureRecognition
            onGestureDetected={recognizeGesture}
            isDetecting={detecting}
            onDetectionStart={handleStartDetection}
          />
        </div>

        <button
          onClick={handleStartDetection}
          className="start-detection-button"
          disabled={detecting || isGenerating}
        >
          {detecting ? 'Detecting...' : 'Start Gesture Detection'}
        </button>

        {isGenerating && (
          <div className="loading-indicator">
            <div className="progress-container">
              <div 
                className="progress-bar" 
                style={{ width: `${progress}%` }}
              >
                {progress}%
              </div>
            </div>
            <p>{statusMessage}</p>
          </div>
        )}

        {gestureResult && (
          <div className={`result-display ${gestureResult.includes('Error') ? 'error' : 'success'}`}>
            <p>{gestureResult}</p>
          </div>
        )}

        {imageUrl && (
          <div className="image-result">
            <img
              src={imageUrl}
              alt="Generated from gesture"
              className="generated-image"
            />
          </div>
        )}

        <footer className="app-footer">
          Gesture Recognition System © {new Date().getFullYear()}
        </footer>
      </header>
    </div>
  );
}

export default App;