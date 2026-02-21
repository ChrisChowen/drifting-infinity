import { useState, useEffect } from "react";
import { motion } from "framer-motion";

interface TypewriterTextProps {
  text: string;
  /** Milliseconds per character */
  speed?: number;
  /** Delay before starting (ms) */
  delay?: number;
  className?: string;
  /** Called when typing completes */
  onComplete?: () => void;
  /** Cursor color class */
  cursorColor?: string;
}

export function TypewriterText({
  text,
  speed = 35,
  delay = 0,
  className = "",
  onComplete,
  cursorColor = "bg-accent",
}: TypewriterTextProps) {
  const [displayedText, setDisplayedText] = useState("");
  const [started, setStarted] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setStarted(true), delay);
    return () => clearTimeout(t);
  }, [delay]);

  useEffect(() => {
    if (!started) return;

    let idx = 0;
    setDisplayedText("");
    setDone(false);

    const interval = setInterval(() => {
      idx++;
      setDisplayedText(text.slice(0, idx));
      if (idx >= text.length) {
        clearInterval(interval);
        setDone(true);
        onComplete?.();
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, speed, started, onComplete]);

  if (!started) return null;

  return (
    <span className={className}>
      {displayedText}
      {!done && (
        <motion.span
          className={`inline-block w-0.5 h-[1em] ml-0.5 align-text-bottom ${cursorColor}`}
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.5, repeat: Infinity }}
        />
      )}
    </span>
  );
}
