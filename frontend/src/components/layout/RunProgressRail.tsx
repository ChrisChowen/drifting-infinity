import { useNavigate } from "react-router-dom";
import { useRunStore } from "@/stores/useRunStore";
import { Home } from "lucide-react";
import { clsx } from "clsx";
import { motion } from "framer-motion";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { useConfirm } from "@/hooks/useConfirm";

export function RunProgressRail() {
  const navigate = useNavigate();
  const { run, floor } = useRunStore();
  const { modalProps, confirm } = useConfirm();

  const floorCount = run?.floor_count ?? 4;
  const floorsCompleted = run?.floors_completed ?? 0;
  const currentFloorNumber = floorsCompleted + 1;
  const arenaCount = floor?.arena_count ?? 4;
  const arenasCompleted = floor?.arenas_completed ?? 0;
  const currentArenaNumber = arenasCompleted + 1;

  const handleReturnToHub = async () => {
    const ok = await confirm({
      title: "Leave Expedition?",
      description: "Return to the Nexus? Your run will be preserved and you can resume later.",
      confirmLabel: "Leave",
      cancelLabel: "Stay",
      variant: "warning",
    });
    if (ok) navigate("/");
  };

  return (
    <>
    <ConfirmModal {...modalProps} />

    {/* Desktop: vertical rail on left */}
    <div className="hidden md:flex fixed left-0 top-0 bottom-0 w-16 bg-surface-1 border-r border-surface-3/50 flex-col items-center py-3 z-20">
      {/* Home button */}
      <button
        onClick={handleReturnToHub}
        className="p-2.5 rounded-lg text-gray-400 hover:text-accent hover:bg-surface-2 transition-colors mb-4"
        title="Return to Nexus"
        aria-label="Return to Nexus"
      >
        <Home size={18} />
      </button>

      <div className="w-8 border-t border-surface-3 mb-4" />

      {/* Floor markers */}
      <div className="flex-1 flex flex-col items-center gap-1 overflow-y-auto">
        {Array.from({ length: floorCount }, (_, fi) => {
          const floorNum = fi + 1;
          const isCompleted = floorNum < currentFloorNumber;
          const isCurrent = floorNum === currentFloorNumber;
          const isFuture = floorNum > currentFloorNumber;

          return (
            <div key={`floor-${floorNum}`} className="flex flex-col items-center">
              <motion.div
                initial={false}
                animate={{ scale: isCurrent ? 1.1 : 1 }}
                className={clsx(
                  "w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold font-display transition-colors",
                  isCompleted && "bg-accent text-surface-0",
                  isCurrent && "ring-2 ring-accent bg-accent/20 text-accent",
                  isFuture && "bg-surface-2 text-gray-600 ring-1 ring-surface-3",
                )}
              >
                F{floorNum}
              </motion.div>

              {isCurrent && (
                <div className="flex flex-col items-center gap-1 my-1.5">
                  <div className="h-2 w-px bg-surface-3" />
                  {Array.from({ length: arenaCount }, (_, ai) => {
                    const arenaNum = ai + 1;
                    const arenaCompleted = arenaNum <= arenasCompleted;
                    const arenaCurrent = arenaNum === currentArenaNumber;

                    return (
                      <motion.div
                        key={`arena-${arenaNum}`}
                        initial={false}
                        animate={{ scale: arenaCurrent ? 1.2 : 1 }}
                        className={clsx(
                          "w-3 h-3 rounded-full transition-colors",
                          arenaCompleted && "bg-accent",
                          arenaCurrent && "ring-2 ring-accent bg-accent/30",
                          !arenaCompleted && !arenaCurrent && "bg-surface-3",
                        )}
                        title={`Arena ${arenaNum}`}
                      />
                    );
                  })}
                  <div className="h-2 w-px bg-surface-3" />
                </div>
              )}

              {fi < floorCount - 1 && !isCurrent && (
                <div className={clsx(
                  "h-3 w-px",
                  isCompleted ? "bg-accent/50" : "bg-surface-3",
                )} />
              )}
            </div>
          );
        })}
      </div>
    </div>

    {/* Mobile: horizontal compact bar at top */}
    <div className="md:hidden sticky top-0 z-20 bg-surface-1 border-b border-surface-3/50 px-3 py-2 flex items-center gap-2">
      <button
        onClick={handleReturnToHub}
        className="p-1.5 rounded-lg text-gray-400 hover:text-accent hover:bg-surface-2 transition-colors flex-shrink-0"
        title="Return to Nexus"
        aria-label="Return to Nexus"
      >
        <Home size={16} />
      </button>

      <div className="h-5 w-px bg-surface-3 flex-shrink-0" />

      {/* Floor dots */}
      <div className="flex items-center gap-1.5 overflow-x-auto flex-1">
        {Array.from({ length: floorCount }, (_, fi) => {
          const floorNum = fi + 1;
          const isCompleted = floorNum < currentFloorNumber;
          const isCurrent = floorNum === currentFloorNumber;
          const isFuture = floorNum > currentFloorNumber;

          return (
            <div key={`m-floor-${floorNum}`} className="flex items-center gap-1 flex-shrink-0">
              <motion.div
                initial={false}
                animate={{ scale: isCurrent ? 1.15 : 1 }}
                className={clsx(
                  "w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold font-display transition-colors",
                  isCompleted && "bg-accent text-surface-0",
                  isCurrent && "ring-2 ring-accent bg-accent/20 text-accent",
                  isFuture && "bg-surface-2 text-gray-600 ring-1 ring-surface-3",
                )}
              >
                {floorNum}
              </motion.div>

              {isCurrent && (
                <div className="flex items-center gap-0.5">
                  {Array.from({ length: arenaCount }, (_, ai) => {
                    const arenaNum = ai + 1;
                    const arenaCompleted = arenaNum <= arenasCompleted;
                    const arenaCurrent = arenaNum === currentArenaNumber;

                    return (
                      <motion.div
                        key={`m-arena-${arenaNum}`}
                        initial={false}
                        animate={{ scale: arenaCurrent ? 1.3 : 1 }}
                        className={clsx(
                          "w-2 h-2 rounded-full transition-colors",
                          arenaCompleted && "bg-accent",
                          arenaCurrent && "ring-1 ring-accent bg-accent/30",
                          !arenaCompleted && !arenaCurrent && "bg-surface-3",
                        )}
                      />
                    );
                  })}
                </div>
              )}

              {fi < floorCount - 1 && (
                <div className={clsx(
                  "w-2 h-px",
                  isCompleted ? "bg-accent/50" : "bg-surface-3",
                )} />
              )}
            </div>
          );
        })}
      </div>
    </div>
    </>
  );
}
