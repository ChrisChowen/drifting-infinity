import { type ReactNode } from "react";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { clsx } from "clsx";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  backTo?: string;
  backLabel?: string;
  action?: ReactNode;
  className?: string;
}

export function PageHeader({ title, subtitle, backTo, backLabel, action, className }: PageHeaderProps) {
  const navigate = useNavigate();

  return (
    <div className={clsx("space-y-1", className)}>
      {backTo && (
        <button
          className="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-accent transition-colors mb-2 cursor-pointer"
          onClick={() => navigate(backTo)}
        >
          <ArrowLeft size={16} />
          {backLabel ?? "Back"}
        </button>
      )}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white font-display">{title}</h1>
          {subtitle && <p className="text-sm text-gray-400 mt-1 font-body">{subtitle}</p>}
        </div>
        {action}
      </div>
    </div>
  );
}
