'use client';

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';
import { MousePosition } from '@/types/portal';

interface LuxuryParticlesProps {
  count: number;
  tier: 'mystery' | 'onyx' | 'obsidian' | 'void';
  mousePosition: MousePosition;
}

export function LuxuryParticles({ count, tier, mousePosition }: LuxuryParticlesProps) {
  const pointsRef = useRef<THREE.Points>(null);
  
  // Tier-specific configurations
  const tierConfig = useMemo(() => {
    switch (tier) {
      case 'void':
        return {
          color: '#FFD700',
          size: 0.008,
          opacity: 0.8,
          speed: 0.0008,
          attraction: 0.02
        };
      case 'obsidian':
        return {
          color: '#E5E4E2',
          size: 0.006,
          opacity: 0.6,
          speed: 0.0006,
          attraction: 0.015
        };
      case 'onyx':
        return {
          color: '#C0C0C0',
          size: 0.004,
          opacity: 0.4,
          speed: 0.0004,
          attraction: 0.01
        };
      case 'mystery':
      default:
        return {
          color: '#FFD700',
          size: 0.003,
          opacity: 0.3,
          speed: 0.0003,
          attraction: 0.008
        };
    }
  }, [tier]);

  // Generate particle positions and properties
  const [positions, velocities, originalPositions] = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);
    const originalPositions = new Float32Array(count * 3);
    
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      
      // Create luxury formation patterns
      let x, y, z;
      
      if (tier === 'void') {
        // Void: Sacred geometry formation
        const angle = (i / count) * Math.PI * 2 * 3; // Triple spiral
        const radius = 1 + Math.sin(i / count * Math.PI * 8) * 0.5;
        x = Math.cos(angle) * radius;
        y = Math.sin(angle) * radius;
        z = (Math.random() - 0.5) * 2;
      } else if (tier === 'obsidian') {
        // Obsidian: Crystalline formation
        const layer = Math.floor(i / (count / 5));
        const angleOffset = layer * 0.2;
        const angle = (i / count) * Math.PI * 2 + angleOffset;
        const radius = 0.8 + layer * 0.2;
        x = Math.cos(angle) * radius;
        y = Math.sin(angle) * radius * 0.6; // Compressed Y for crystal effect
        z = (layer - 2) * 0.3 + (Math.random() - 0.5) * 0.2;
      } else if (tier === 'onyx') {
        // Onyx: Flowing river formation
        const flow = i / count;
        x = (Math.random() - 0.5) * 3 + Math.sin(flow * Math.PI * 4) * 0.5;
        y = (flow - 0.5) * 2 + Math.cos(flow * Math.PI * 6) * 0.3;
        z = (Math.random() - 0.5) * 1.5;
      } else {
        // Mystery: Random ethereal cloud
        const angle = Math.random() * Math.PI * 2;
        const radius = Math.random() * 1.5 + 0.5;
        x = Math.cos(angle) * radius + (Math.random() - 0.5) * 0.5;
        y = Math.sin(angle) * radius + (Math.random() - 0.5) * 0.5;
        z = (Math.random() - 0.5) * 2;
      }
      
      positions[i3] = x;
      positions[i3 + 1] = y;
      positions[i3 + 2] = z;
      
      // Store original positions for attraction
      originalPositions[i3] = x;
      originalPositions[i3 + 1] = y;
      originalPositions[i3 + 2] = z;
      
      // Random velocities
      velocities[i3] = (Math.random() - 0.5) * tierConfig.speed;
      velocities[i3 + 1] = (Math.random() - 0.5) * tierConfig.speed;
      velocities[i3 + 2] = (Math.random() - 0.5) * tierConfig.speed;
    }
    
    return [positions, velocities, originalPositions];
  }, [count, tier, tierConfig.speed]);

  // Animation loop
  useFrame((state) => {
    if (!pointsRef.current) return;
    
    const positions = pointsRef.current.geometry.attributes.position.array as Float32Array;
    const time = state.clock.elapsedTime;
    
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      
      // Get current position
      let x = positions[i3];
      let y = positions[i3 + 1];
      let z = positions[i3 + 2];
      
      // Mouse attraction
      const mouseX = mousePosition.x * 2; // Convert to 3D space
      const mouseY = mousePosition.y * -2;
      const mouseZ = 0;
      
      const dx = mouseX - x;
      const dy = mouseY - y;
      const dz = mouseZ - z;
      const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
      
      if (distance < 2) {
        const force = tierConfig.attraction / (distance + 0.1);
        velocities[i3] += dx * force;
        velocities[i3 + 1] += dy * force;
        velocities[i3 + 2] += dz * force;
      }
      
      // Attraction back to original position
      const originX = originalPositions[i3];
      const originY = originalPositions[i3 + 1];
      const originZ = originalPositions[i3 + 2];
      
      const returnForce = 0.002;
      velocities[i3] += (originX - x) * returnForce;
      velocities[i3 + 1] += (originY - y) * returnForce;
      velocities[i3 + 2] += (originZ - z) * returnForce;
      
      // Apply tier-specific motion
      if (tier === 'void') {
        // Void: Orbital motion with sacred geometry
        const orbital = time * 0.1 + (i / count) * Math.PI * 2;
        velocities[i3] += Math.cos(orbital) * 0.001;
        velocities[i3 + 1] += Math.sin(orbital) * 0.001;
        velocities[i3 + 2] += Math.sin(time * 0.5 + i * 0.1) * 0.0005;
      } else if (tier === 'obsidian') {
        // Obsidian: Crystalline vibration
        const vibration = Math.sin(time * 2 + i * 0.5) * 0.0003;
        velocities[i3] += vibration;
        velocities[i3 + 1] += vibration * 0.7;
        velocities[i3 + 2] += Math.cos(time * 1.5 + i * 0.3) * 0.0002;
      } else if (tier === 'onyx') {
        // Onyx: Flowing motion
        const flow = time * 0.3 + (i / count) * Math.PI * 4;
        velocities[i3] += Math.sin(flow) * 0.0004;
        velocities[i3 + 1] += Math.cos(flow * 1.5) * 0.0003;
      } else {
        // Mystery: Ethereal floating
        const float = time * 0.2 + i * 0.1;
        velocities[i3] += Math.sin(float) * 0.0002;
        velocities[i3 + 1] += Math.cos(float * 1.3) * 0.0002;
        velocities[i3 + 2] += Math.sin(float * 0.7) * 0.0001;
      }
      
      // Apply damping
      velocities[i3] *= 0.99;
      velocities[i3 + 1] *= 0.99;
      velocities[i3 + 2] *= 0.99;
      
      // Update positions
      positions[i3] += velocities[i3];
      positions[i3 + 1] += velocities[i3 + 1];
      positions[i3 + 2] += velocities[i3 + 2];
      
      // Boundary checking - keep particles in view
      const boundary = 3;
      if (Math.abs(positions[i3]) > boundary) {
        positions[i3] = Math.sign(positions[i3]) * boundary;
        velocities[i3] *= -0.5;
      }
      if (Math.abs(positions[i3 + 1]) > boundary) {
        positions[i3 + 1] = Math.sign(positions[i3 + 1]) * boundary;
        velocities[i3 + 1] *= -0.5;
      }
      if (Math.abs(positions[i3 + 2]) > boundary) {
        positions[i3 + 2] = Math.sign(positions[i3 + 2]) * boundary;
        velocities[i3 + 2] *= -0.5;
      }
    }
    
    pointsRef.current.geometry.attributes.position.needsUpdate = true;
  });

  return (
    <Points ref={pointsRef} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color={tierConfig.color}
        size={tierConfig.size}
        sizeAttenuation={true}
        depthWrite={false}
        opacity={tierConfig.opacity}
        blending={THREE.AdditiveBlending}
      />
    </Points>
  );
}