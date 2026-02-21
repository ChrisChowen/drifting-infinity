import { clsx } from "clsx";
import type { WizardStepConfig } from "./WizardShell";

interface StepIndicatorProps {
  steps: WizardStepConfig[];
  currentStep: number;
}

export function StepIndicator({ steps, currentStep }: StepIndicatorProps) {
  return (
    <div className="flex items-center justify-center gap-2">
      {steps.map((step, i) => (
        <div key={step.id} className="flex items-center gap-2">
          <div
            className={clsx(
              "w-2.5 h-2.5 rounded-full transition-all duration-300",
              i === currentStep
                ? "bg-accent scale-125"
                : i < currentStep
                  ? "bg-accent/40"
                  : "bg-surface-3",
            )}
          />
          {i < steps.length - 1 && (
            <div
              className={clsx(
                "w-8 h-0.5 rounded-full transition-colors duration-300",
                i < currentStep ? "bg-accent/40" : "bg-surface-3",
              )}
            />
          )}
        </div>
      ))}
    </div>
  );
}
