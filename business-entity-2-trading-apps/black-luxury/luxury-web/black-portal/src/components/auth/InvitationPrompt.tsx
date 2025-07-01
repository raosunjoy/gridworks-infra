'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface InvitationPromptProps {
  onSubmit: (code: string) => void;
  onBack: () => void;
}

export function InvitationPrompt({ onSubmit, onBack }: InvitationPromptProps) {
  const [invitationCode, setInvitationCode] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState('');
  const [attempts, setAttempts] = useState(0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!invitationCode.trim()) {
      setError('Invitation code required');
      return;
    }

    setIsValidating(true);
    setError('');
    
    // Simulate validation delay for luxury feel
    setTimeout(() => {
      setAttempts(prev => prev + 1);
      
      // Mock validation - in production, this would hit your API
      const validCodes = ['VOID2024001', 'OBSIDIAN2024001', 'ONYX2024001', 'DEMO', 'TEST'];
      
      if (validCodes.includes(invitationCode.toUpperCase())) {
        onSubmit(invitationCode.toUpperCase());
      } else {
        setError('Invalid invitation code');
        if (attempts >= 2) {
          setError('Too many attempts. Access denied.');
          setTimeout(() => onBack(), 3000);
        }
      }
      
      setIsValidating(false);
    }, 2000);
  };

  const formatCode = (value: string) => {
    // Auto-format as user types (XXXX2024XXX)
    const cleaned = value.replace(/[^A-Z0-9]/gi, '').toUpperCase();
    return cleaned.slice(0, 11); // Max length for codes
  };

  return (
    <motion.div
      className="min-h-screen flex items-center justify-center bg-void-black px-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 1 }}
    >
      {/* Background Reality Distortion */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0 bg-gradient-radial from-void-gold/10 via-transparent to-transparent animate-pulse" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        
        {/* Back Button */}
        <motion.button
          onClick={onBack}
          className="absolute top-0 left-0 text-void-gold hover:text-white transition-colors duration-300"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </motion.button>

        {/* Main Content */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.3 }}
        >
          <motion.div
            className="w-16 h-16 mx-auto mb-8 relative"
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          >
            <div className="absolute inset-0 border-2 border-void-gold/30 rounded-full" />
            <div className="absolute inset-2 border border-void-gold/60 rounded-full" />
            <div className="absolute inset-4 bg-void-gold/20 rounded-full" />
          </motion.div>

          <h1 className="text-3xl md:text-4xl font-luxury-serif text-void-gold mb-4 tracking-wider">
            INVITATION REQUIRED
          </h1>
          
          <p className="text-gray-400 font-luxury-sans tracking-wide mb-8">
            Access to the void is by invitation only.<br />
            Enter your exclusive code to proceed.
          </p>
        </motion.div>

        {/* Invitation Form */}
        <motion.form
          onSubmit={handleSubmit}
          className="space-y-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.6 }}
        >
          <div className="relative">
            <motion.input
              type="text"
              value={invitationCode}
              onChange={(e) => setInvitationCode(formatCode(e.target.value))}
              placeholder="ENTER INVITATION CODE"
              className="w-full bg-transparent border-2 border-void-gold/30 rounded-lg px-6 py-4 text-center text-xl font-luxury-mono tracking-widest text-void-gold placeholder-void-gold/50 focus:border-void-gold focus:outline-none transition-all duration-300"
              disabled={isValidating}
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.3 }}
              whileFocus={{ 
                scale: 1.02,
                boxShadow: "0 0 20px rgba(255,215,0,0.3)"
              }}
            />
            
            {/* Loading indicator */}
            {isValidating && (
              <motion.div
                className="absolute right-4 top-1/2 transform -translate-y-1/2"
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0 }}
              >
                <div className="w-6 h-6 border-2 border-void-gold border-t-transparent rounded-full animate-spin" />
              </motion.div>
            )}
          </div>

          {/* Error Message */}
          <AnimatePresence>
            {error && (
              <motion.div
                className="text-center"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <p className="text-red-400 font-luxury-sans tracking-wide">
                  {error}
                </p>
                {attempts >= 2 && (
                  <p className="text-red-600 text-sm mt-2">
                    Redirecting to landing...
                  </p>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Submit Button */}
          <motion.button
            type="submit"
            disabled={isValidating || attempts >= 3}
            className="w-full btn-void py-4 text-lg font-luxury-sans tracking-widest disabled:opacity-50 disabled:cursor-not-allowed"
            whileHover={!isValidating ? { 
              scale: 1.02,
              boxShadow: "0 0 30px rgba(255,215,0,0.4)"
            } : {}}
            whileTap={!isValidating ? { scale: 0.98 } : {}}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9 }}
          >
            {isValidating ? (
              <motion.span
                className="flex items-center justify-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <motion.div
                  className="w-5 h-5 border-2 border-void-black border-t-transparent rounded-full mr-3"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                />
                VALIDATING ACCESS
              </motion.span>
            ) : (
              'VERIFY INVITATION'
            )}
          </motion.button>
        </motion.form>

        {/* Hint for Demo */}
        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
        >
          <p className="text-gray-600 text-sm font-luxury-sans tracking-wide">
            For demonstration: Use code <span className="text-void-gold/70">DEMO</span>
          </p>
        </motion.div>

        {/* Luxury Decorative Elements */}
        <div className="absolute -top-20 -left-20 w-40 h-40 opacity-10">
          <motion.div
            className="w-full h-full border border-void-gold/20 rounded-full"
            animate={{ rotate: 360, scale: [1, 1.1, 1] }}
            transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
          />
        </div>
        
        <div className="absolute -bottom-20 -right-20 w-32 h-32 opacity-10">
          <motion.div
            className="w-full h-full border border-void-gold/20 rounded-full"
            animate={{ rotate: -360, scale: [1, 0.9, 1] }}
            transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
          />
        </div>

        {/* Attempt Counter (Hidden) */}
        {attempts > 0 && (
          <div className="absolute top-4 right-4 text-xs text-gray-600">
            Attempts: {attempts}/3
          </div>
        )}
      </div>

      {/* Ambient Particles */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-void-gold rounded-full opacity-20"
            style={{
              left: `${10 + i * 12}%`,
              top: `${15 + (i % 4) * 20}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.2, 0.6, 0.2],
              scale: [0.5, 1, 0.5]
            }}
            transition={{
              duration: 3 + i * 0.5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.3
            }}
          />
        ))}
      </div>
    </motion.div>
  );
}