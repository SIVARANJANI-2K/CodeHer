// src/ModelViewer.jsx
import React from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Stage } from '@react-three/drei'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { useLoader } from '@react-three/fiber'

function Model({ url }) {
  const gltf = useLoader(GLTFLoader, url)
  return <primitive object={gltf.scene} />
}

export default function ModelViewer({ modelUrl }) {
  return (
    <Canvas style={{ height: '500px', width: '100%' }}>
      <ambientLight />
      <OrbitControls />
      <Stage>
        <Model url={modelUrl} />
      </Stage>
    </Canvas>
  )
}
