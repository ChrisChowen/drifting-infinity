import { Outlet } from "react-router-dom";

export function FullscreenLayout() {
  return (
    <div className="min-h-screen bg-surface-0 text-gray-100">
      {/* Subtle background texture */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,rgba(99,102,241,0.04)_0%,transparent_50%)] pointer-events-none" />
      <div className="relative z-10">
        <Outlet />
      </div>
    </div>
  );
}
