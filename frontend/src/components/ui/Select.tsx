import { forwardRef, type SelectHTMLAttributes } from "react";
import { clsx } from "clsx";

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  description?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, description, className, id, children, ...props }, ref) => {
    const selectId = id || label?.toLowerCase().replace(/\s+/g, "-");
    return (
      <div className="space-y-1">
        {label && (
          <label htmlFor={selectId} className="block text-sm font-medium text-gray-300">
            {label}
          </label>
        )}
        {description && (
          <p className="text-xs text-gray-500">{description}</p>
        )}
        <select
          ref={ref}
          id={selectId}
          className={clsx(
            "w-full bg-surface-2 text-white px-3 py-2.5 rounded-lg border border-surface-3 transition-colors",
            "focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent/50",
            className,
          )}
          {...props}
        >
          {children}
        </select>
      </div>
    );
  },
);

Select.displayName = "Select";
