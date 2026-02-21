import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui";
import { Compass, ChevronRight, ChevronLeft } from "lucide-react";
import { ARMILLARY_IDENTITY, ARBITER_QUOTES } from "@/constants/lore";

const LORE_STEPS = [
  {
    heading: ARMILLARY_IDENTITY.name,
    body: ARMILLARY_IDENTITY.description[0],
  },
  {
    heading: "It Watches. It Learns.",
    body: ARMILLARY_IDENTITY.description[1],
  },
  {
    heading: "You Are the Arbiter",
    body: ARMILLARY_IDENTITY.description[2],
  },
  {
    heading: "The Edge of Survival",
    body: ARMILLARY_IDENTITY.description[3],
  },
];

export function WelcomePage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);

  const isLast = step === LORE_STEPS.length - 1;
  const isFirst = step === 0;

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center text-center px-4">
      {/* Arcane glow backdrop */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[500px] h-[500px] rounded-full bg-arcane/5 blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative z-10 space-y-8 max-w-lg"
      >
        {/* Icon */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="mx-auto w-20 h-20 rounded-full bg-surface-1 border border-accent/30 flex items-center justify-center animate-float"
        >
          <Compass size={36} className="text-accent" />
        </motion.div>

        {/* Title */}
        <div>
          <h1 className="text-4xl font-display font-bold text-gradient-gold mb-3">
            Drifting Infinity
          </h1>
          <p className="text-sm text-gray-500 italic">
            {ARMILLARY_IDENTITY.tagline}
          </p>
        </div>

        {/* Lore Steps */}
        <div className="min-h-[180px] flex flex-col justify-center">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-3"
            >
              <h2 className="text-lg font-display font-semibold text-accent">
                {LORE_STEPS[step]!.heading}
              </h2>
              <p className="text-sm text-gray-400 leading-relaxed">
                {LORE_STEPS[step]!.body}
              </p>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Step indicators */}
        <div className="flex items-center justify-center gap-2">
          {LORE_STEPS.map((_, i) => (
            <button
              key={i}
              onClick={() => setStep(i)}
              className={`w-2 h-2 rounded-full transition-all duration-300 cursor-pointer ${
                i === step
                  ? "bg-accent w-6"
                  : "bg-surface-3 hover:bg-gray-500"
              }`}
            />
          ))}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-center gap-3">
          {!isFirst && (
            <Button
              variant="ghost"
              size="sm"
              icon={<ChevronLeft size={16} />}
              onClick={() => setStep((s) => s - 1)}
            >
              Back
            </Button>
          )}

          {isLast ? (
            <Button
              size="xl"
              glow
              onClick={() => navigate("/campaign/new")}
              icon={<Compass size={20} />}
            >
              Begin Your Campaign
            </Button>
          ) : (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setStep((s) => s + 1)}
            >
              Continue
              <ChevronRight size={16} className="ml-1" />
            </Button>
          )}
        </div>

        {/* Arbiter whisper */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.0, duration: 1.0 }}
          className="text-xs text-gray-600 italic"
        >
          "{ARBITER_QUOTES.welcome![0]}"
        </motion.p>
      </motion.div>
    </div>
  );
}
