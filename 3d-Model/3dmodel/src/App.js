import React from 'react';
import DrawingCanvas from './DrawingCanvas';
import './App.css';

function App() {
  const modelUrl = "https://img.theapi.app/temp/c486b91f-8381-4c4d-9c58-39ce27d18fa4.glb"
  return (
    <div className="App">
      <DrawingCanvas />
      
    </div>
  );
}

export default App;