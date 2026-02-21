import { forwardRef, type InputHTMLAttributes } from "react";
import { clsx } from "clsx";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  description?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, description, error, className, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");
    return (
      <div className="space-y-1">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-gray-300">
            {label}
          </label>
        )}
        {description && (
          <p className="text-xs text-gray-500">{description}</p>
        )}
        <input
          ref={ref}
          id={inputId}
          className={clsx(
            "w-full bg-surface-2 text-white px-3 py-2.5 rounded-lg border transition-colors",
            "placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent/50",
            error ? "border-red-500/50" : "border-surface-3",
            className,
          )}
          {...props}
        />
        {error && (
          <p className="text-xs text-red-400">{error}</p>
        )}
      </div>
    );
  },
);

Input.displayName = "Input";
