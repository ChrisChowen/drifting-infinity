import { useState, useEffect, useCallback } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Menu } from "lucide-react";
import { Sidebar } from "./Sidebar";
import { SettingsDrawer } from "./SettingsDrawer";
import { ParticleCanvas } from "@/components/effects/ParticleCanvas";

function useIsMobile() {
  const [mobile, setMobile] = useState(() =>
    typeof window !== "undefined" ? window.innerWidth < 768 : false,
  );
  useEffect(() => {
    const mq = window.matchMedia("(max-width: 767px)");
    const handler = (e: MediaQueryListEvent) => setMobile(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);
  return mobile;
}

export function HubLayout() {
  const location = useLocation();
  const isMobile = useIsMobile();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    try {
      return localStorage.getItem("sidebar-collapsed") === "true";
    } catch {
      return false;
    }
  });

  // Close mobile drawer on route change
  useEffect(() => {
    setMobileDrawerOpen(false);
  }, [location.pathname]);

  const handleToggleSidebar = useCallback(() => {
    if (isMobile) {
      setMobileDrawerOpen((prev) => !prev);
    } else {
      setSidebarCollapsed((prev) => {
        const next = !prev;
        try { localStorage.setItem("sidebar-collapsed", String(next)); } catch { /* noop */ }
        return next;
      });
    }
  }, [isMobile]);

  const sidebarMargin = isMobile ? 0 : sidebarCollapsed ? 64 : 240;

  return (
    <div className="min-h-screen bg-surface-0 text-gray-100 flex flex-col md:flex-row">
      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-2 focus:left-2 focus:px-4 focus:py-2 focus:bg-accent focus:text-white focus:rounded-lg">
        Skip to content
      </a>
      {/* Subtle background texture */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,rgba(99,102,241,0.04)_0%,transparent_50%)] pointer-events-none" />
      <ParticleCanvas preset="arcane_dust" />

      {/* Mobile header bar */}
      {isMobile && (
        <header className="sticky top-0 z-40 bg-surface-1 border-b border-surface-3/50 px-4 py-2.5 flex items-center gap-3">
          <button
            onClick={() => setMobileDrawerOpen(true)}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-surface-2 transition-colors"
            aria-label="Open navigation menu"
          >
            <Menu size={20} />
          </button>
          <h1 className="text-sm font-display font-bold text-gradient-gold">Drifting Infinity</h1>
        </header>
      )}

      {/* Sidebar — overlay on mobile, fixed on desktop */}
      {isMobile ? (
        <AnimatePresence>
          {mobileDrawerOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/60 z-40"
                onClick={() => setMobileDrawerOpen(false)}
              />
              <motion.div
                initial={{ x: -260 }}
                animate={{ x: 0 }}
                exit={{ x: -260 }}
                transition={{ type: "spring", damping: 25, stiffness: 300 }}
                className="fixed left-0 top-0 bottom-0 z-50 w-60"
              >
                <Sidebar
                  collapsed={false}
                  onToggle={() => setMobileDrawerOpen(false)}
                  onOpenSettings={() => { setMobileDrawerOpen(false); setSettingsOpen(true); }}
                />
              </motion.div>
            </>
          )}
        </AnimatePresence>
      ) : (
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={handleToggleSidebar}
          onOpenSettings={() => setSettingsOpen(true)}
        />
      )}

      {/* Main Content */}
      <main
        id="main-content"
        className="flex-1 relative z-10 min-h-screen transition-all duration-300"
        style={{ marginLeft: sidebarMargin }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="p-4 md:p-6 max-w-5xl mx-auto w-full"
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>

      <SettingsDrawer open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}
