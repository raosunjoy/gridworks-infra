'use client';

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { MousePosition } from '@/types/portal';

interface RealityDistortionProps {
  intensity: number;
  mousePosition: MousePosition;
}

export function RealityDistortion({ intensity, mousePosition }: RealityDistortionProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  // Custom shader for reality distortion effect
  const shaderMaterial = useMemo(() => {
    return new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uMouse: { value: new THREE.Vector2(0, 0) },
        uIntensity: { value: intensity },
        uResolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
        uVoidColor: { value: new THREE.Color('#FFD700') },
        uDistortionStrength: { value: 0.1 }
      },
      vertexShader: `
        varying vec2 vUv;
        varying vec3 vPosition;
        
        void main() {
          vUv = uv;
          vPosition = position;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform float uTime;
        uniform vec2 uMouse;
        uniform float uIntensity;
        uniform vec2 uResolution;
        uniform vec3 uVoidColor;
        uniform float uDistortionStrength;
        
        varying vec2 vUv;
        varying vec3 vPosition;
        
        // Noise function for reality distortion
        float noise(vec2 st) {
          return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
        }
        
        // Smooth noise
        float smoothNoise(vec2 st) {
          vec2 i = floor(st);
          vec2 f = fract(st);
          
          float a = noise(i);
          float b = noise(i + vec2(1.0, 0.0));
          float c = noise(i + vec2(0.0, 1.0));
          float d = noise(i + vec2(1.0, 1.0));
          
          vec2 u = f * f * (3.0 - 2.0 * f);
          
          return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
        }
        
        // Fractal noise
        float fractalNoise(vec2 st) {
          float value = 0.0;
          float amplitude = 0.5;
          float frequency = 0.0;
          
          for (int i = 0; i < 4; i++) {
            value += amplitude * smoothNoise(st);
            st *= 2.0;
            amplitude *= 0.5;
          }
          return value;
        }
        
        // Reality warp function
        vec2 warpReality(vec2 uv, float time, vec2 mouse) {
          // Distance from mouse
          float mouseDistance = distance(uv, mouse * 0.5 + 0.5);
          
          // Create warping effect near mouse
          float warpStrength = uDistortionStrength * (1.0 - smoothstep(0.0, 0.3, mouseDistance));
          
          // Time-based reality breathing
          float breathe = sin(time * 0.5) * 0.01;
          
          // Fractal distortion
          vec2 distortion = vec2(
            fractalNoise(uv * 3.0 + time * 0.1),
            fractalNoise(uv * 3.0 + time * 0.1 + 100.0)
          ) * 2.0 - 1.0;
          
          // Apply distortions
          uv += distortion * warpStrength;
          uv += breathe;
          
          return uv;
        }
        
        // Void energy visualization
        float voidEnergy(vec2 uv, float time) {
          vec2 center = vec2(0.5, 0.5);
          float distance = length(uv - center);
          
          // Pulsing void core
          float pulse = sin(time * 2.0) * 0.5 + 0.5;
          float core = 1.0 - smoothstep(0.0, 0.3 * pulse, distance);
          
          // Energy rings
          float rings = 0.0;
          for (float i = 1.0; i <= 3.0; i++) {
            float ringDistance = 0.1 * i + sin(time + i) * 0.05;
            float ring = abs(distance - ringDistance);
            rings += 1.0 - smoothstep(0.0, 0.02, ring);
          }
          
          return core + rings * 0.3;
        }
        
        void main() {
          vec2 uv = vUv;
          
          // Apply reality distortion
          vec2 distortedUv = warpReality(uv, uTime, uMouse);
          
          // Calculate void energy
          float energy = voidEnergy(distortedUv, uTime);
          
          // Mouse interaction glow
          float mouseGlow = 1.0 - smoothstep(0.0, 0.5, distance(uv, uMouse * 0.5 + 0.5));
          mouseGlow = pow(mouseGlow, 3.0);
          
          // Combine effects
          vec3 color = uVoidColor * energy * uIntensity;
          color += uVoidColor * mouseGlow * 0.5;
          
          // Add some shimmer
          float shimmer = fractalNoise(distortedUv * 10.0 + uTime * 0.5) * 0.1;
          color += shimmer;
          
          // Calculate alpha for transparency
          float alpha = (energy + mouseGlow) * uIntensity * 0.3;
          
          gl_FragColor = vec4(color, alpha);
        }
      `,
      transparent: true,
      blending: THREE.AdditiveBlending,
      side: THREE.DoubleSide
    });
  }, [intensity]);

  // Update uniforms
  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = state.clock.elapsedTime;
      materialRef.current.uniforms.uMouse.value.set(mousePosition.x, mousePosition.y);
      materialRef.current.uniforms.uIntensity.value = intensity;
    }
  });

  return (
    <>
      {/* Primary distortion plane */}
      <mesh ref={meshRef} position={[0, 0, -1]}>
        <planeGeometry args={[6, 6, 64, 64]} />
        <shaderMaterial
          ref={materialRef}
          attach="material"
          args={[shaderMaterial]}
        />
      </mesh>
      
      {/* Secondary reality layers for depth */}
      <mesh position={[0, 0, -1.5]} rotation={[0, 0, Math.PI / 4]}>
        <planeGeometry args={[4, 4, 32, 32]} />
        <shaderMaterial
          uniforms={{
            ...shaderMaterial.uniforms,
            uIntensity: { value: intensity * 0.5 },
            uDistortionStrength: { value: 0.05 }
          }}
          vertexShader={shaderMaterial.vertexShader}
          fragmentShader={shaderMaterial.fragmentShader}
          transparent={true}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
      
      {/* Floating void orbs */}
      {[...Array(5)].map((_, i) => (
        <mesh
          key={i}
          position={[
            Math.sin(i * 1.2) * 2,
            Math.cos(i * 0.8) * 1.5,
            -0.5 - i * 0.2
          ]}
        >
          <sphereGeometry args={[0.05 + i * 0.01, 16, 16]} />
          <meshBasicMaterial
            color="#FFD700"
            transparent
            opacity={0.6}
            blending={THREE.AdditiveBlending}
          />
        </mesh>
      ))}
    </>
  );
}