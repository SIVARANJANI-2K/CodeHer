import React, { useRef, useState } from 'react';
import { Tldraw } from '@tldraw/tldraw';
import '@tldraw/tldraw/tldraw.css';
import ModelViewer from './ModelViewer'; // adjust the path as needed


function DrawingCanvas() {
  const editorRef = useRef(null); // store editor instance
  const [generatedImage, setGeneratedImage] = useState(null);
  const [modelUrl, setModelUrl] = useState('https://img.theapi.app/temp/c486b91f-8381-4c4d-9c58-39ce27d18fa4.glb');
  const [uploadedFilename, setUploadedFilename] = useState(null);

  const handleImproveDrawing = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
  
    input.onchange = async (event) => {
      const file = event.target.files[0];
      if (!file) {
        alert("Please select an image.");
        return;
      }
  
      try {
        const formData = new FormData();
        formData.append('file', file); // Key should match what server expects
        formData.append('prompt', "Analyze and generate a clean, flat 2D color illustration. Identify the pose and individual elements such as body parts, objects, or clothing. Assign appropriate, realistic colors to each component (e.g., skin tone, hair, clothing, objects), while preserving the proportions and structure. The background must be plain white. Avoid adding shadows, lighting effects, gradients, or depth. Focus on clean outlines, solid fill colors, and a flat, illustrative art style similar to digital cartoons or 2D vector drawings."); // Make sure key matches server expectation
  
        // Debug: Log FormData contents
        for (let [key, value] of formData.entries()) {
          console.log(key, value);
        }
  
        const response = await fetch('https://537f-35-230-109-251.ngrok-free.app/upload', {
          method: 'POST',
          body: formData,
          headers: {
            'Accept': 'application/json',
          }
        });
  
        if (!response.ok) {
          const errorData = await response.json().catch(() => null);
          throw new Error(errorData?.message || `HTTP error! status: ${response.status}`);
        }
  
        const responseData = await response.json(); // Assuming the server responds with JSON containing an image URL
        console.log("Backend Response Data:", responseData);
        const base64Image = responseData.image_base64; // Get the base64 image data from the response
        const imageUrl = `data:image/png;base64,${base64Image}`; // Create a full image source URL from the base64 string
        setGeneratedImage(imageUrl);  
        setUploadedFilename(base64Image); // <-- store filename

      } catch (err) {
        console.error('Error generating image:', err);
        alert(`Failed to generate image: ${err.message}`);
      }
    };
  
    input.click();
  };

  const handleMake3D = async() => {
    if (!uploadedFilename) {
      alert("No filename found. Please generate the image first.");
      return;
    }
    try {
      const res=await fetch("https://537f-35-230-109-251.ngrok-free.app/send-local-image", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ filename: uploadedFilename }),
      });
      const data = await res.json()
      console.log("URL:",data.model_url)
      if (data.model_url) {
        alert("3D model ready!")
        setModelUrl(data.model_url)
      } else {
        alert("Model generation failed.")
        console.error(data)
      }
      alert("Local image sent from Python successfully!");

    } 
    
    
    catch (error) {
      console.error("Error sending image:", error);
      alert("Failed to send image.");
    }
  };

  return (
  <div style={{ display: 'flex', flexDirection: 'column', height: '150vh' }}>
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

  {/* Top 50% - Canvas */}
  <div style={{ height: '50%' }}>
    <Tldraw
      onMount={(editor) => {
        editorRef.current = editor;
      }}
    />
  </div>

  {/* Bottom 50% - 3D Model + Image */}
  {(modelUrl || generatedImage) && (
    <div style={{  height: '50%', display: 'flex', justifyContent: 'space-between', padding: '20px' }}>
      {modelUrl && (
        <div style={{ flex: 1, marginRight: '10px' }}>
          <ModelViewer modelUrl={modelUrl} />
        </div>
      )}
      {generatedImage && (
        <div style={{ flex: 1, marginLeft: '10px', textAlign: 'center' }}>
          <h3>Generated Image</h3>
          <img
            src={generatedImage}
            alt="Generated"
            style={{ width: '100%', maxHeight: '100%', objectFit: 'contain' }}
          />
        </div>
      )}
    </div>
  )}
</div>

  );
}

export default DrawingCanvas;
