import React, { useEffect, useState } from 'react';
import { encodeWAV } from './audioUtils';

const AudioStreamer = () => {
  const [inferenceResult, setInferenceResult] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  let ws;
  let audioContext;
  let processor;

  useEffect(() => {
    if (isStreaming) {
      // Establish WebSocket connection
      const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/audio';
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('Connected to WebSocket server');
        startAudioStreaming();
      };

      ws.onmessage = (event) => {
        setInferenceResult(event.data);
      };

      ws.onclose = () => {
        console.log('WebSocket connection closed');
        stopAudioProcessing();
      };

      return () => {
        ws.close();
        stopAudioProcessing();
      };
    }
  }, [isStreaming]);

  const startAudioStreaming = () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
        const source = audioContext.createMediaStreamSource(stream);
        processor = audioContext.createScriptProcessor(1024, 1, 1); // Use a constant buffer size of 1024

        processor.onaudioprocess = (e) => {
          if (ws.readyState === WebSocket.OPEN) {
            const inputData = e.inputBuffer.getChannelData(0);
            const audioData = encodeWAV(inputData, audioContext.sampleRate);
            ws.send(audioData);
          }
        };

        source.connect(processor);
        processor.connect(audioContext.destination);
      })
      .catch(err => console.error('Error accessing audio stream:', err));
  };

  const stopAudioProcessing = () => {
    if (processor) {
      processor.disconnect();
    }
    if (audioContext && audioContext.state !== 'closed') {
      audioContext.close();
    }
  };

  return (
    <div>
      <h1>Audio Streaming App</h1>
      <button onClick={() => setIsStreaming(!isStreaming)}>
        {isStreaming ? 'Stop Streaming' : 'Start Streaming'}
      </button>
      <div>
        <h2>Inference Result:</h2>
        <p>{inferenceResult}</p>
      </div>
    </div>
  );
};

export default AudioStreamer; 