import React, { useState, useRef, useEffect } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { OrbitControls, Text, Float, Sphere, Box } from '@react-three/drei';
import { motion, AnimatePresence } from 'framer-motion';
import * as THREE from 'three';
import axios from 'axios';
import './App.css';

// Floating 3D Elements Component
function FloatingElements() {
  const meshRef = useRef();
  const sphereRef = useRef();
  const boxRef = useRef();

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.3) * 0.1;
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.2) * 0.2;
    }
    if (sphereRef.current) {
      sphereRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.4) * 0.3;
      sphereRef.current.rotation.x = state.clock.elapsedTime * 0.5;
    }
    if (boxRef.current) {
      boxRef.current.position.x = Math.sin(state.clock.elapsedTime * 0.3) * 0.2;
      boxRef.current.rotation.z = state.clock.elapsedTime * 0.3;
    }
  });

  return (
    <>
      <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
        <Box ref={boxRef} args={[0.5, 0.5, 0.5]} position={[-2, 1, 0]}>
          <meshStandardMaterial color="#D76C82" />
        </Box>
      </Float>
      
      <Float speed={1.5} rotationIntensity={0.3} floatIntensity={0.3}>
        <Sphere ref={sphereRef} args={[0.3]} position={[2, -1, 0]}>
          <meshStandardMaterial color="#EBE8DB" />
        </Sphere>
      </Float>

      <Float speed={1} rotationIntensity={0.2} floatIntensity={0.7}>
        <mesh ref={meshRef} position={[0, 0, -2]}>
          <torusGeometry args={[0.4, 0.15, 16, 100]} />
          <meshStandardMaterial color="#B03052" />
        </mesh>
      </Float>

      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#D76C82" />
    </>
  );
}

// Download Modal Component
function DownloadModal({ isOpen, onClose, onDownload }) {
  const [name, setName] = useState('');
  const [projectName, setProjectName] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await onDownload({ name, projectName });
      onClose();
    } catch (error) {
      console.error('Download failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 modal-backdrop flex items-center justify-center z-50"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            className="bg-opacity-95 p-8 rounded-lg border-2 max-w-md w-full mx-4 vintage-border paper-texture scan-lines"
            style={{ backgroundColor: 'rgba(61, 3, 1, 0.95)' }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-2xl font-bold mb-6 text-center heading-text vintage-pink" style={{ color: 'var(--pink)' }}>
              Download ImageCombiner
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium mb-2 accent-text" style={{ color: 'var(--cream)' }}>
                  Your Name (Optional)
                </label>
                <input
                  type="text"
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 rounded-md focus:outline-none focus:ring-2"
                  placeholder="Enter your name"
                  style={{ backgroundColor: 'rgba(61, 3, 1, 0.8)', color: 'var(--cream)', borderColor: 'var(--pink)' }}
                />
              </div>
              
              <div>
                <label htmlFor="projectName" className="block text-sm font-medium mb-2 accent-text" style={{ color: 'var(--cream)' }}>
                  Project Name (Optional)
                </label>
                <input
                  type="text"
                  id="projectName"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="w-full px-3 py-2 rounded-md focus:outline-none focus:ring-2"
                  placeholder="Your Creative Project"
                  style={{ backgroundColor: 'rgba(61, 3, 1, 0.8)', color: 'var(--cream)', borderColor: 'var(--pink)' }}
                />
              </div>
              
              <div className="flex gap-4 mt-6">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 px-4 py-2 rounded-md hover:opacity-80 transition-colors body-text"
                  style={{ backgroundColor: 'rgba(235, 232, 219, 0.2)', color: 'var(--cream)' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1 px-4 py-2 rounded-md transition-colors disabled:opacity-50 download-button"
                >
                  {isLoading ? 'Creating...' : 'Download'}
                </button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Main App Component
function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [notification, setNotification] = useState('');

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleDownload = async ({ name, projectName }) => {
    try {
      // Create download package
      const response = await axios.post(`${backendUrl}/api/download`, {
        name,
        project_name: projectName
      });

      const downloadId = response.data.download_id;
      
      // Trigger download
      const downloadUrl = `${backendUrl}/api/download/${downloadId}`;
      window.open(downloadUrl, '_blank');
      
      setNotification('Download Started! Your ImagePack is ready.');
      setTimeout(() => setNotification(''), 4000);
      
      // Refresh stats
      fetchStats();
      
    } catch (error) {
      console.error('Download failed:', error);
      setNotification('Download failed. Please try again.');
      setTimeout(() => setNotification(''), 4000);
    }
  };

  return (
    <div className="min-h-screen text-white overflow-hidden vintage-texture film-grain">
      {/* 3D Background */}
      <div className="fixed inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
          <FloatingElements />
          <OrbitControls enableZoom={false} enablePan={false} />
        </Canvas>
      </div>

      {/* Notification */}
      <AnimatePresence>
        {notification && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg notification"
          >
            {notification}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <header className="p-6">
          <nav className="flex justify-between items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-2xl font-bold heading-text"
              style={{ color: 'var(--pink)' }}
            >
              ImageCombiner
            </motion.div>
            
            {stats && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="vintage-badge stats-counter"
              >
                {stats.completed_downloads} downloads
              </motion.div>
            )}
          </nav>
        </header>

        {/* Hero Section */}
        <main className="flex-1 flex items-center justify-center px-6">
          <div className="text-center max-w-4xl">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mb-6"
            >
              <div className="vintage-ornament mb-4">✦ ✧ ✦</div>
              <h1 className="vintage-title leading-tight mb-4">
                IMAGECOMBINER
              </h1>
              <div className="vintage-ornament">✧ ✦ ✧</div>
            </motion.div>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-xl md:text-2xl mb-8 max-w-2xl mx-auto body-text"
              style={{ color: 'var(--cream)' }}
            >
              Transform multiple images into a single, beautifully organized frame. 
              <span className="accent-text" style={{ color: 'var(--pink)' }}> Crafted for creative professionals.</span>
            </motion.p>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="space-y-4"
            >
              <button
                onClick={() => setIsModalOpen(true)}
                className="download-button px-12 py-4 rounded-lg text-xl font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                Download ImageCombiner
              </button>
              
              <p className="text-sm body-text" style={{ color: 'rgba(235, 232, 219, 0.7)' }}>
                Free • Open Source • No Registration Required
              </p>
            </motion.div>
          </div>
        </main>

        {/* Features Section */}
        <section className="py-20 px-6">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="text-center mb-12"
            >
              <div className="vintage-ornament mb-4">✦ ✧ ✦</div>
              <h2 className="text-4xl font-bold heading-text vintage-cream" style={{ color: 'var(--cream)' }}>
                Why Choose ImageCombiner?
              </h2>
            </motion.div>
            
            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: "🎨",
                  title: "Smart Layout",
                  description: "Automatically organizes your images in the perfect grid"
                },
                {
                  icon: "⚡",
                  title: "Lightning Fast",
                  description: "Process hundreds of images in seconds"
                },
                {
                  icon: "📐",
                  title: "Aspect Ratio",
                  description: "Preserves original proportions for professional results"
                }
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1 + index * 0.2 }}
                  className="text-center p-6 feature-card rounded-lg transition-all duration-300 hover-lift"
                >
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <h3 className="text-xl font-semibold mb-2 accent-text" style={{ color: 'var(--pink)' }}>
                    {feature.title}
                  </h3>
                  <p className="body-text" style={{ color: 'var(--cream)' }}>
                    {feature.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="p-6 border-t" style={{ borderColor: 'rgba(215, 108, 130, 0.3)' }}>
          <div className="text-center body-text" style={{ color: 'rgba(235, 232, 219, 0.7)' }}>
            <div className="vintage-ornament mb-2">✧</div>
            <p>© 2025 ImageCombiner. Crafted for creative professionals.</p>
          </div>
        </footer>
      </div>

      {/* Download Modal */}
      <DownloadModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onDownload={handleDownload}
      />
    </div>
  );
}

export default App;