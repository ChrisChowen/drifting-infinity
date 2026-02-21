import { useState, type ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { StepIndicator } from "./StepIndicator";
import { Button } from "@/components/ui";
import { ArrowLeft, ArrowRight, SkipForward } from "lucide-react";

export interface WizardStepConfig {
  id: string;
  title: string;
  subtitle?: string;
  skippable?: boolean;
  content: (props: { data: Record<string, unknown>; onUpdate: (patch: Record<string, unknown>) => void }) => ReactNode;
  validate?: (data: Record<string, unknown>) => boolean;
}

interface WizardShellProps {
  steps: WizardStepConfig[];
  onComplete: (data: Record<string, unknown>) => void | Promise<void>;
  initialData?: Record<string, unknown>;
  completionLabel?: string;
  completionLoading?: boolean;
}

export function WizardShell({
  steps, onComplete, initialData = {}, completionLabel = "Complete", completionLoading,
}: WizardShellProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [direction, setDirection] = useState(1);
  const [data, setData] = useState<Record<string, unknown>>(initialData);

  const step = steps[currentStep]!;
  const isFirst = currentStep === 0;
  const isLast = currentStep === steps.length - 1;
  const isValid = step.validate ? step.validate(data) : true;

  const handleUpdate = (patch: Record<string, unknown>) => {
    setData((prev) => ({ ...prev, ...patch }));
  };

  const goForward = () => {
    if (isLast) {
      onComplete(data);
    } else {
      setDirection(1);
      setCurrentStep((s) => s + 1);
    }
  };

  const goBack = () => {
    if (!isFirst) {
      setDirection(-1);
      setCurrentStep((s) => s - 1);
    }
  };

  const skip = () => {
    if (!isLast) {
      setDirection(1);
      setCurrentStep((s) => s + 1);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Step Indicator */}
      <StepIndicator steps={steps} currentStep={currentStep} />

      {/* Step Content */}
      <AnimatePresence mode="wait" custom={direction}>
        <motion.div
          key={step.id}
          custom={direction}
          initial={{ opacity: 0, x: direction * 60 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: direction * -60 }}
          transition={{ duration: 0.25, ease: "easeOut" }}
          className="space-y-2"
        >
          <div className="text-center mb-8">
            <h2 className="text-2xl font-display font-bold text-white">{step.title}</h2>
            {step.subtitle && (
              <p className="text-sm text-gray-400 mt-2">{step.subtitle}</p>
            )}
          </div>

          {step.content({ data, onUpdate: handleUpdate })}
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-4">
        <div>
          {!isFirst && (
            <Button variant="ghost" size="md" icon={<ArrowLeft size={16} />} onClick={goBack}>
              Back
            </Button>
          )}
        </div>

        <div className="flex items-center gap-2">
          {step.skippable && !isLast && (
            <Button variant="ghost" size="md" iconRight={<SkipForward size={16} />} onClick={skip}>
              Skip
            </Button>
          )}
          <Button
            variant="primary"
            size="lg"
            iconRight={!isLast ? <ArrowRight size={16} /> : undefined}
            onClick={goForward}
            disabled={!isValid}
            loading={isLast && completionLoading}
            glow={isLast}
          >
            {isLast ? completionLabel : "Continue"}
          </Button>
        </div>
      </div>
    </div>
  );
}
