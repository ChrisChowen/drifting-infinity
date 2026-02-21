import { useState, useMemo } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { RunProgressRail } from "./RunProgressRail";
import { RunStatusBar } from "./RunStatusBar";
import { SettingsDrawer } from "./SettingsDrawer";
import { ParticleCanvas } from "@/components/effects/ParticleCanvas";
import { useRunStore } from "@/stores/useRunStore";
import { getEnvironmentTheme } from "@/lib/environmentThemes";

export function RunLayout() {
  const location = useLocation();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const encounter = useRunStore((s) => s.encounter);

  const theme = useMemo(
    () => getEnvironmentTheme(encounter?.environment ?? null),
    [encounter?.environment],
  );

  return (
    <div className="min-h-screen bg-surface-0 text-gray-100 flex flex-col md:flex-row">
      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-2 focus:left-2 focus:px-4 focus:py-2 focus:bg-accent focus:text-white focus:rounded-lg">
        Skip to content
      </a>
      {/* Environment-reactive background */}
      <div
        className="fixed inset-0 pointer-events-none transition-all duration-1000"
        style={{ background: theme.gradient }}
      />
      <ParticleCanvas key={theme.particles} preset={theme.particles} />

      {/* Progress Rail */}
      <RunProgressRail />

      {/* Main Content Area */}
      <div className="flex-1 md:ml-16 flex flex-col min-h-screen relative z-10">
        {/* Status Bar */}
        <RunStatusBar onOpenSettings={() => setSettingsOpen(true)} />

        {/* Page Content */}
        <main id="main-content" className="flex-1">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="p-3 md:p-6 max-w-5xl mx-auto w-full"
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>

      <SettingsDrawer open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}
