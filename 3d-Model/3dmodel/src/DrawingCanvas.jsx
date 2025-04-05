import React, { useRef,useState } from 'react';
import { Tldraw} from '@tldraw/tldraw';
import '@tldraw/tldraw/tldraw.css';
import axios from 'axios';
import ModelViewer from './ModelViewer';

function DrawingCanvas() {
  const editorRef = useRef(null); // store editor instance
  const [modelUrl, setModelUrl] = useState('https://img.theapi.app/temp/c486b91f-8381-4c4d-9c58-39ce27d18fa4.glb')
  const handleImproveDrawing = async () => {
    const editor = editorRef.current;
    if (!editor) {
      console.error("Editor not available yet.");
      return;
    }

    try {
      // Get the PNG blob
      const blob = await editor.exportImage('png', {
        background: true, // or false if you want transparent background
        maxWidth: 1024, // optional size control
      });
      

      // Convert to base64
      const reader = new FileReader();
      reader.readAsDataURL(blob);

      reader.onloadend = async () => {
        const base64data = reader.result.split(',')[1]; // Remove header

        console.log("Sending Base64 data to Gemini AI...");

        const API_KEY = "AIzaSyAbkhcGkTunotds5crYdxNpkOIj_32nSrg"; // Replace with your API key
        const URL = `https://generativelanguage.googleapis.com/v1/models/gemini-1.5:generateContent?key=${API_KEY}`;

        try {
          const response = await axios.post(URL, {
            contents: [{
              parts: [
                { text: "Enhance this 2D sketch to look more refined and detailed." },
                { inline_data: { mime_type: "image/png", data: base64data } }
              ]
            }]
          });

          const enhancedImage = response.data.candidates[0].content.parts[0].inline_data.data;
          console.log("Enhanced image received!");

          // Convert back to displayable format
          const imgSrc = `data:image/png;base64,${enhancedImage}`;
          const img = new Image();
          img.src = imgSrc;
          document.body.appendChild(img); // Append enhanced image to document

        } catch (err) {
          console.error("Error sending image to Gemini:", err);
          alert("Enhancement failed!");
        }
      };
    } catch (error) {
      console.error("Export error:", error);
      alert("Failed to export drawing");
    }
  };

  const handleMake3D = async () => {
    try {
      const res=await fetch("http://127.0.0.1:5000/send-local-image", {
        method: "POST",
      });
      const data = await res.json()
      if (data.modelUrl) {
        alert("3D model ready!")
        setModelUrl(data.modelUrl)
      } else {
        alert("Model generation failed.")
        console.error(data)
      }
      alert("Local image sent from Python successfully!");
    } catch (error) {
      console.error("Error sending image:", error);
      alert("Failed to send image.");
    }
  };
  
  
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <div style={{ padding: '10px', display: 'flex', gap: '10px', background: '#f0f0f0' }}>
        <button 
          onClick={handleImproveDrawing}
          style={{ padding: '8px 16px', background: '#4c68d7', color: 'white', border: 'none', borderRadius: '4px' }}
        >
          Improve Drawing
        </button>
        <button 
          onClick={handleMake3D}
          style={{ padding: '8px 16px', background: '#4c68d7', color: 'white', border: 'none', borderRadius: '4px' }}
        >
          Make 3D
        </button>
      </div>
      <div style={{ flex: 1 }}>
        <Tldraw
          onMount={(editor) => {
            editorRef.current = editor; // store editor instance in ref
          }}
        />
      </div>
      {modelUrl && (
        <div style={{ flex: 1 }}>
          <ModelViewer modelUrl={modelUrl} />
        </div>
      )}
    </div>
  );
}

export default DrawingCanvas;
