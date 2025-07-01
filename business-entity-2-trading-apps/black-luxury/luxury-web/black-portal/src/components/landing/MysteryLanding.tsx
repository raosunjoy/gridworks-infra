'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { MousePosition } from '@/types/portal';

interface MysteryLandingProps {
  onInvitationPrompt: () => void;
  mousePosition: MousePosition;
}

export function MysteryLanding({ onInvitationPrompt, mousePosition }: MysteryLandingProps) {
  const [showHints, setShowHints] = useState(false);
  const [discoveries, setDiscoveries] = useState(0);
  const [mysteryPhase, setMysteryPhase] = useState<'silent' | 'whispers' | 'revelation'>('silent');
  const containerRef = useRef<HTMLDivElement>(null);
  
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 300], [0, -50]);
  const y2 = useTransform(scrollY, [0, 300], [0, -100]);
  const opacity = useTransform(scrollY, [0, 100, 200], [1, 0.8, 0.6]);

  // Hidden discovery zones for mystery interaction
  const discoveryZones = [
    { x: 10, y: 15, hint: "The void sees all" },
    { x: 85, y: 25, hint: "Gold flows through obsidian" },
    { x: 50, y: 80, hint: "17 members. ₹8,000 Cr. Absolute privacy." },
    { x: 25, y: 60, hint: "For those who trade beyond charts" },
    { x: 75, y: 70, hint: "Your invitation awaits..." }
  ];

  // Progress mystery phases based on interactions
  useEffect(() => {
    if (discoveries === 0) setMysteryPhase('silent');
    else if (discoveries < 3) setMysteryPhase('whispers');
    else setMysteryPhase('revelation');
  }, [discoveries]);

  // Handle mysterious mouse interactions
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    
    // Check if mouse is near discovery zones
    discoveryZones.forEach((zone, index) => {
      const distance = Math.sqrt(Math.pow(x - zone.x, 2) + Math.pow(y - zone.y, 2));
      if (distance < 5 && discoveries <= index) {
        setDiscoveries(prev => Math.max(prev, index + 1));
        setShowHints(true);
        setTimeout(() => setShowHints(false), 3000);
      }
    });
  };

  // Cryptic messages that appear based on phase
  const getCrypticMessage = () => {
    switch (mysteryPhase) {
      case 'silent':
        return '';
      case 'whispers':
        return 'Something watches from the shadows...';
      case 'revelation':
        return 'The void recognizes you.';
      default:
        return '';
    }
  };

  return (
    <motion.div
      ref={containerRef}
      className="relative min-h-screen overflow-hidden bg-void-black"
      style={{ opacity }}
      onMouseMove={handleMouseMove}
    >
      {/* Luxury Background Layers */}
      <div className="absolute inset-0">
        {/* Base Reality Layer */}
        <motion.div 
          className="absolute inset-0 opacity-20"
          style={{ y: y1 }}
        >
          <div className="absolute inset-0 bg-gradient-radial from-void-gold/5 via-transparent to-transparent" />
        </motion.div>
        
        {/* Floating Luxury Orbs */}
        <motion.div 
          className="absolute inset-0"
          style={{ y: y2 }}
        >
          {[...Array(7)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 bg-void-gold rounded-full opacity-30"
              style={{
                left: `${15 + i * 12}%`,
                top: `${20 + (i % 3) * 25}%`,
              }}
              animate={{
                y: [0, -20, 0],
                opacity: [0.1, 0.4, 0.1],
                scale: [0.5, 1, 0.5]
              }}
              transition={{
                duration: 4 + i,
                repeat: Infinity,
                ease: "easeInOut",
                delay: i * 0.5
              }}
            />
          ))}
        </motion.div>
      </div>

      {/* Main Mystery Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-8">
        
        {/* Central Cryptic Symbol */}
        <motion.div
          className="mb-12"
          initial={{ scale: 0, rotateY: -180 }}
          animate={{ scale: 1, rotateY: 0 }}
          transition={{ duration: 2, ease: "easeOut", delay: 0.5 }}
        >
          <div className="relative w-32 h-32">
            {/* Outer Ring */}
            <motion.div
              className="absolute inset-0 border-2 border-void-gold/30 rounded-full"
              animate={{ rotate: 360 }}
              transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
            />
            
            {/* Inner Symbol */}
            <motion.div
              className="absolute inset-4 border border-void-gold/60 rounded-full flex items-center justify-center"
              animate={{ rotateY: [0, 180, 360] }}
              transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
            >
              <div className="w-8 h-8 bg-void-gold/20 transform rotate-45" />
            </motion.div>
            
            {/* Center Void */}
            <motion.div
              className="absolute inset-12 bg-void-black rounded-full border border-void-gold/80"
              animate={{ 
                boxShadow: [
                  "0 0 20px rgba(255,215,0,0.2)",
                  "0 0 40px rgba(255,215,0,0.4)",
                  "0 0 20px rgba(255,215,0,0.2)"
                ]
              }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            />
          </div>
        </motion.div>

        {/* Cryptic Main Message */}
        <motion.div
          className="text-center max-w-2xl mb-8"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.5, delay: 1 }}
        >
          <motion.h1
            className="text-4xl md:text-6xl font-luxury-serif text-void-gold mb-6 tracking-wider"
            animate={{
              textShadow: [
                "0 0 10px rgba(255,215,0,0.3)",
                "0 0 20px rgba(255,215,0,0.6)",
                "0 0 10px rgba(255,215,0,0.3)"
              ]
            }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          >
            FOR THOSE WHO
          </motion.h1>
          
          <motion.h2
            className="text-2xl md:text-4xl font-luxury-serif text-white mb-8 tracking-wide"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2, duration: 1 }}
          >
            TRADE BEYOND CHARTS
          </motion.h2>
        </motion.div>

        {/* Cryptic Stats - Only show in revelation phase */}
        {mysteryPhase === 'revelation' && (
          <motion.div
            className="grid grid-cols-3 gap-8 mb-12 text-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, ease: "easeOut" }}
          >
            <div className="glass-morphism p-4 rounded-lg">
              <div className="text-3xl font-luxury-serif text-void-gold">17</div>
              <div className="text-sm text-gray-400 uppercase tracking-widest">Members</div>
            </div>
            <div className="glass-morphism p-4 rounded-lg">
              <div className="text-3xl font-luxury-serif text-void-gold">₹8,000 Cr</div>
              <div className="text-sm text-gray-400 uppercase tracking-widest">Secured</div>
            </div>
            <div className="glass-morphism p-4 rounded-lg">
              <div className="text-3xl font-luxury-serif text-void-gold">ABSOLUTE</div>
              <div className="text-sm text-gray-400 uppercase tracking-widest">Privacy</div>
            </div>
          </motion.div>
        )}

        {/* Progressive Call-to-Action */}
        {mysteryPhase !== 'silent' && (
          <motion.div
            className="text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.5 }}
          >
            {mysteryPhase === 'whispers' && (
              <motion.p
                className="text-gray-400 mb-6 font-luxury-sans tracking-wider"
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                Continue exploring to reveal more...
              </motion.p>
            )}
            
            {mysteryPhase === 'revelation' && (
              <>
                <motion.p
                  className="text-void-gold mb-8 text-lg font-luxury-sans tracking-wide"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1, duration: 1 }}
                >
                  Your invitation awaits verification.
                </motion.p>
                
                <motion.button
                  className="btn-void px-12 py-4 text-lg font-luxury-sans tracking-widest luxury-shadow-lg"
                  onClick={onInvitationPrompt}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1.5, duration: 0.8, ease: "easeOut" }}
                  whileHover={{ 
                    scale: 1.05,
                    boxShadow: "0 0 30px rgba(255,215,0,0.4)"
                  }}
                  whileTap={{ scale: 0.95 }}
                >
                  ENTER THE VOID
                </motion.button>
              </>
            )}
          </motion.div>
        )}

        {/* Hidden Discovery Hints */}
        {showHints && (
          <motion.div
            className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
          >
            <div className="glass-morphism px-6 py-3 rounded-full">
              <p className="text-void-gold text-sm font-luxury-sans tracking-wide">
                {getCrypticMessage()}
              </p>
            </div>
          </motion.div>
        )}
      </div>

      {/* Invisible Discovery Zones */}
      {discoveryZones.map((zone, index) => (
        <div
          key={index}
          className="absolute w-16 h-16 opacity-0 hover:opacity-5 transition-opacity duration-300"
          style={{
            left: `${zone.x}%`,
            top: `${zone.y}%`,
            background: index < discoveries ? 'rgba(255,215,0,0.1)' : 'transparent'
          }}
          title={index < discoveries ? zone.hint : ''}
        />
      ))}

      {/* Parallax Mouse-Following Effect */}
      <motion.div
        className="fixed pointer-events-none w-64 h-64 opacity-5"
        style={{
          background: 'radial-gradient(circle, rgba(255,215,0,0.3) 0%, transparent 70%)',
          left: `${50 + mousePosition.x * 10}%`,
          top: `${50 + mousePosition.y * 10}%`,
          transform: 'translate(-50%, -50%)'
        }}
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 180, 360]
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear"
        }}
      />

      {/* Subtle Breathing Effect on Container */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        animate={{
          background: [
            'radial-gradient(circle at 50% 50%, rgba(0,0,0,0) 0%, rgba(255,215,0,0.01) 100%)',
            'radial-gradient(circle at 50% 50%, rgba(0,0,0,0) 0%, rgba(255,215,0,0.03) 100%)',
            'radial-gradient(circle at 50% 50%, rgba(0,0,0,0) 0%, rgba(255,215,0,0.01) 100%)'
          ]
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
    </motion.div>
  );
}