import { clsx } from "clsx";
import { getLoadingMessage } from "@/constants/lore";
import { ArmillarySpinner } from "./ArmillarySpinner";

interface LoadingStateProps {
  message?: string;
  context?: string;
  className?: string;
}

export function LoadingState({ message, context, className }: LoadingStateProps) {
  const displayMessage = message || getLoadingMessage(context);

  return (
    <div className={clsx("flex flex-col items-center justify-center py-16 gap-4", className)}>
      <ArmillarySpinner size="md" />
      <p className="text-sm text-gray-400 font-display">{displayMessage}</p>
    </div>
  );
}
