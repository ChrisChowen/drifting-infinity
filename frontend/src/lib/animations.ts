import type { Variants, Transition } from "framer-motion";

/* ── Reusable transitions ──────────────────────────────────── */

export const easeOut: Transition = { duration: 0.4, ease: "easeOut" };
export const spring: Transition = { type: "spring", stiffness: 300, damping: 24 };

/* ── Page & section entrances ──────────────────────────────── */

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: easeOut },
};

export const fadeInDown: Variants = {
  hidden: { opacity: 0, y: -12 },
  visible: { opacity: 1, y: 0, transition: easeOut },
};

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.3 } },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.92 },
  visible: { opacity: 1, scale: 1, transition: easeOut },
};

export const slideInLeft: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0, transition: easeOut },
};

export const slideInRight: Variants = {
  hidden: { opacity: 0, x: 20 },
  visible: { opacity: 1, x: 0, transition: easeOut },
};

/* ── Stagger containers ────────────────────────────────────── */

export const staggerContainer: Variants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.08 },
  },
};

export const staggerContainerSlow: Variants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.15 },
  },
};

export const staggerChild: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: easeOut },
};

/* ── Combat feedback ───────────────────────────────────────── */

export const shakeHit: Variants = {
  idle: { x: 0 },
  shake: {
    x: [0, -4, 4, -3, 3, -1, 0],
    transition: { duration: 0.4, ease: "easeOut" },
  },
};

export const pulseHeal: Variants = {
  idle: { scale: 1, boxShadow: "0 0 0px rgba(34,197,94,0)" },
  pulse: {
    scale: [1, 1.03, 1],
    boxShadow: [
      "0 0 0px rgba(34,197,94,0)",
      "0 0 16px rgba(34,197,94,0.4)",
      "0 0 0px rgba(34,197,94,0)",
    ],
    transition: { duration: 0.6 },
  },
};

export const pulseDamage: Variants = {
  idle: { scale: 1, boxShadow: "0 0 0px rgba(239,68,68,0)" },
  pulse: {
    scale: [1, 1.02, 1],
    boxShadow: [
      "0 0 0px rgba(239,68,68,0)",
      "0 0 12px rgba(239,68,68,0.4)",
      "0 0 0px rgba(239,68,68,0)",
    ],
    transition: { duration: 0.4 },
  },
};

/* ── Dramatic reveals ──────────────────────────────────────── */

export const dramaticReveal: Variants = {
  hidden: { opacity: 0, scale: 0.8, y: 20 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] },
  },
};

export const cardFlip: Variants = {
  faceDown: { rotateY: 180, opacity: 0.8 },
  faceUp: {
    rotateY: 0,
    opacity: 1,
    transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] },
  },
};

/* ── Floating number (damage/heal) ─────────────────────────── */

export const floatUp: Variants = {
  initial: { opacity: 1, y: 0, scale: 1 },
  animate: {
    opacity: 0,
    y: -40,
    scale: 1.2,
    transition: { duration: 1, ease: "easeOut" },
  },
};

export const floatUpLarge: Variants = {
  initial: { opacity: 1, y: 0, scale: 1.2 },
  animate: {
    opacity: 0,
    y: -60,
    scale: 1.5,
    transition: { duration: 1.2, ease: "easeOut" },
  },
};

/* ── Screen effects ────────────────────────────────────────── */

export const screenFlash: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: [0, 0.3, 0],
    transition: { duration: 0.5, times: [0, 0.15, 1] },
  },
};

export const vignetteFlash: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: [0, 0.6, 0],
    transition: { duration: 0.8, times: [0, 0.2, 1] },
  },
};
