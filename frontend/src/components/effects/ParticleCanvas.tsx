import { useRef, useEffect, useCallback } from "react";
import { PARTICLE_PRESETS, type ParticlePreset, type ParticlePresetKey } from "./particlePresets";

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  color: string;
  opacity: number;
  maxOpacity: number;
  lifetime: number;
  age: number;
}

interface ParticleCanvasProps {
  preset: ParticlePresetKey | ParticlePreset;
  /** CSS class for positioning (defaults to fixed fullscreen) */
  className?: string;
}

function rand(min: number, max: number) {
  return min + Math.random() * (max - min);
}

function pickRandom<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]!;
}

function createParticle(preset: ParticlePreset, w: number, h: number): Particle {
  const maxOpacity = rand(preset.opacityRange[0], preset.opacityRange[1]);
  return {
    x: rand(0, w),
    y: rand(0, h),
    vx: rand(preset.speedXRange[0], preset.speedXRange[1]),
    vy: rand(preset.speedYRange[0], preset.speedYRange[1]),
    size: rand(preset.sizeRange[0], preset.sizeRange[1]),
    color: pickRandom(preset.colors),
    opacity: 0,
    maxOpacity,
    lifetime: rand(preset.lifetimeRange[0], preset.lifetimeRange[1]),
    age: 0,
  };
}

/**
 * Lightweight canvas-based ambient particle system.
 * Renders as a fixed fullscreen layer with pointer-events: none.
 */
export function ParticleCanvas({ preset, className }: ParticleCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const rafRef = useRef<number>(0);
  const lastTimeRef = useRef<number>(0);
  const spawnAccRef = useRef<number>(0);

  const config = typeof preset === "string" ? PARTICLE_PRESETS[preset] : preset;

  const animate = useCallback(
    (time: number) => {
      if (!config) return;
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      const dt = lastTimeRef.current ? (time - lastTimeRef.current) / 1000 : 0.016;
      lastTimeRef.current = time;

      const w = canvas.width;
      const h = canvas.height;

      // Spawn new particles
      spawnAccRef.current += config.spawnRate * dt;
      while (spawnAccRef.current >= 1 && particlesRef.current.length < config.count) {
        const p = createParticle(config, w, h);
        // For new spawns, start at edges
        if (config.speedYRange[1] < 0) {
          // Moving up → spawn at bottom
          p.y = h + p.size;
        } else if (config.speedYRange[0] > 0) {
          // Moving down → spawn at top
          p.y = -p.size;
        }
        particlesRef.current.push(p);
        spawnAccRef.current -= 1;
      }

      // Clear
      ctx.clearRect(0, 0, w, h);

      // Update & draw
      const alive: Particle[] = [];
      for (const p of particlesRef.current) {
        p.age += dt;
        if (p.age >= p.lifetime) continue;

        p.x += p.vx * dt;
        p.y += p.vy * dt;

        // Fade in first 20%, fade out last 20%
        const t = p.age / p.lifetime;
        if (t < 0.2) {
          p.opacity = p.maxOpacity * (t / 0.2);
        } else if (t > 0.8) {
          p.opacity = p.maxOpacity * ((1 - t) / 0.2);
        } else {
          p.opacity = p.maxOpacity;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.opacity;
        ctx.fill();

        alive.push(p);
      }

      ctx.globalAlpha = 1;
      particlesRef.current = alive;

      rafRef.current = requestAnimationFrame(animate);
    },
    [config],
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    // Seed some initial particles so it doesn't start empty
    if (config) {
      particlesRef.current = Array.from({ length: Math.floor(config.count * 0.6) }, () =>
        createParticle(config, canvas.width, canvas.height),
      );
      // Give initial particles random ages so they're spread across lifecycle
      for (const p of particlesRef.current) {
        p.age = rand(0, p.lifetime * 0.7);
      }
    }

    rafRef.current = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(rafRef.current);
    };
  }, [config, animate]);

  return (
    <canvas
      ref={canvasRef}
      className={className ?? "fixed inset-0 pointer-events-none z-0"}
      aria-hidden
    />
  );
}
