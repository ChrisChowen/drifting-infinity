import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useRunStore } from "@/stores/useRunStore";
import { rewardsApi } from "@/api/economy";
import { Badge, Button, PageHeader, LoadingState } from "@/components/ui";
import { Gift, SkipForward, Users, User } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { clsx } from "clsx";
import { getRarityConfig } from "@/lib/rarity";

interface RewardChoice {
  id: string;
  name: string;
  category: string;
  rarity: string;
  description: string;
  effect: Record<string, string | number | boolean>;
  scope: "party" | "character";
}

const CATEGORY_BADGE: Record<string, string> = {
  consumable: "emerald",
  buff: "blue",
  favour: "purple",
  equipment: "gold",
  spell: "indigo",
};

export function RewardSelectionPage() {
  const navigate = useNavigate();
  const { arena, floor, completeFloor, setPhase, startArena } = useRunStore();

  const [rewards, setRewards] = useState<RewardChoice[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [cardsRevealed, setCardsRevealed] = useState(false);
  const [claiming, setClaiming] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadRewards() {
      if (!arena || !floor) return;
      try {
        const data = await rewardsApi.getChoices(arena.id, floor.floor_number);
        if (!cancelled && data && data.length > 0) {
          setRewards(data as RewardChoice[]);
        }
      } catch {
        // API error — leave rewards empty
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadRewards();
    return () => { cancelled = true; };
  }, [arena, floor]);

  // Reveal cards after a brief pause (face-down → face-up)
  useEffect(() => {
    if (rewards.length === 0) return;
    const t = setTimeout(() => setCardsRevealed(true), 800);
    return () => clearTimeout(t);
  }, [rewards]);

  const handleSelect = useCallback((id: string) => {
    if (claiming) return;
    setSelectedId(id);
  }, [claiming]);

  const handleClaimReward = async () => {
    if (!selectedId || !arena || !floor) return;
    setClaiming(true);

    const selected = rewards.find((r) => r.id === selectedId);
    if (selected) {
      try {
        await rewardsApi.claimReward(arena.id, {
          reward_id: selected.id,
          reward_name: selected.name,
          reward_rarity: selected.rarity,
          reward_category: selected.category,
        });
      } catch {
        // Continue even if claim fails
      }
    }

    await handleFloorTransition();
  };

  const handleSkip = async () => {
    setClaiming(true);
    await handleFloorTransition();
  };

  const handleFloorTransition = async () => {
    if (!floor || !arena) return;

    try {
      const shopResult = await rewardsApi.checkShop(floor.id, floor.floor_number);
      if (shopResult.shop_available) {
        setPhase("shop");
        navigate("/run/shop");
        return;
      }
    } catch {
      // No shop
    }

    const completed = floor.arenas_completed + 1;
    if (completed >= floor.arena_count) {
      await completeFloor();
      navigate("/run/floor-transition");
    } else {
      await startArena();
      navigate("/run/encounter");
    }
  };

  if (!arena || !floor) {
    return <div className="py-8 text-center text-gray-400">No active arena data.</div>;
  }

  const selectedReward = rewards.find((r) => r.id === selectedId);
  const selectedConfig = selectedReward ? getRarityConfig(selectedReward.rarity) : null;

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <PageHeader
        title="Choose Your Reward"
        subtitle={`Arena ${arena.arena_number} — Select one`}
      />

      {loading ? (
        <LoadingState message="The Armillary presents its offerings..." />
      ) : (
        <>
          {/* Reward Cards — start face-down, then reveal */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4" style={{ perspective: 1000 }}>
            {rewards.map((reward, i) => {
              const isSelected = selectedId === reward.id;
              const isNotSelected = selectedId !== null && !isSelected;
              const config = getRarityConfig(reward.rarity);

              return (
                <motion.div
                  key={reward.id}
                  initial={{ opacity: 0, y: 40 }}
                  animate={{
                    opacity: isNotSelected ? 0.5 : 1,
                    y: isSelected ? -8 : isNotSelected ? 8 : 0,
                    scale: isSelected ? 1.04 : isNotSelected ? 0.96 : 1,
                  }}
                  transition={{
                    delay: i * 0.12,
                    duration: 0.5,
                    ease: [0.22, 1, 0.36, 1],
                  }}
                  style={{ transformStyle: "preserve-3d" }}
                >
                  <motion.button
                    className={clsx(
                      "w-full text-left rounded-xl border-2 p-5 transition-colors cursor-pointer",
                      isSelected
                        ? `${config.border} ${config.glow} bg-surface-1`
                        : "border-surface-3 bg-surface-1 hover:border-gray-500",
                      claiming && "pointer-events-none"
                    )}
                    animate={{
                      rotateY: cardsRevealed ? 0 : 180,
                    }}
                    transition={{
                      delay: cardsRevealed ? i * 0.15 : 0,
                      duration: 0.6,
                      ease: [0.22, 1, 0.36, 1],
                    }}
                    style={{ transformStyle: "preserve-3d" }}
                    onClick={() => handleSelect(reward.id)}
                  >
                    {/* Face-down back */}
                    {!cardsRevealed && (
                      <div className="py-8 flex flex-col items-center gap-3" style={{ backfaceVisibility: "hidden" }}>
                        <div className="w-12 h-12 rounded-full border-2 border-purple-500/30 flex items-center justify-center">
                          <span className="text-purple-400 text-2xl">?</span>
                        </div>
                        <span className="text-xs text-purple-400/60 uppercase tracking-widest">Unknown</span>
                      </div>
                    )}

                    {/* Face-up content */}
                    {cardsRevealed && (
                      <div style={{ backfaceVisibility: "hidden" }}>
                        <div className="flex items-center gap-2 flex-wrap">
                          <Badge color={(CATEGORY_BADGE[reward.category] || "gray") as "emerald" | "gold" | "blue" | "purple" | "indigo" | "gray"}>
                            {reward.category}
                          </Badge>
                          <span className={clsx(
                            "inline-flex items-center gap-1 text-[10px] font-medium px-2 py-0.5 rounded-full border",
                            reward.scope === "party"
                              ? "text-blue-300 border-blue-500/30 bg-blue-900/20"
                              : "text-amber-300 border-amber-500/30 bg-amber-900/20"
                          )}>
                            {reward.scope === "party"
                              ? <><Users size={10} /> Party</>
                              : <><User size={10} /> Character</>
                            }
                          </span>
                        </div>

                        <h3 className="text-lg font-display font-semibold text-white mt-3">
                          {reward.name}
                        </h3>

                        <p className={clsx("text-sm font-medium mt-1", config.text)}>
                          {config.label}
                        </p>

                        <p className="text-sm text-gray-400 mt-3 leading-relaxed">
                          {reward.description}
                        </p>

                        <AnimatePresence>
                          {isSelected && (
                            <motion.div
                              initial={{ opacity: 0, scale: 0.8, y: 4 }}
                              animate={{ opacity: 1, scale: 1, y: 0 }}
                              exit={{ opacity: 0, scale: 0.8 }}
                              className={clsx("mt-4 text-center text-sm font-semibold", config.text)}
                            >
                              Selected
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    )}
                  </motion.button>
                </motion.div>
              );
            })}
          </div>

          {/* Actions */}
          <motion.div
            className="flex gap-3"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: cardsRevealed ? 1 : 0, y: cardsRevealed ? 0 : 12 }}
            transition={{ delay: 0.6, duration: 0.4 }}
          >
            <Button
              variant="primary"
              size="lg"
              glow
              icon={<Gift size={18} />}
              onClick={handleClaimReward}
              loading={claiming}
              disabled={!selectedId}
              className={clsx(
                "flex-1 transition-all",
                selectedConfig && `shadow-[0_0_20px] ${selectedConfig.glow}`
              )}
            >
              Claim Reward
            </Button>
            <Button
              variant="secondary"
              size="lg"
              icon={<SkipForward size={16} />}
              onClick={handleSkip}
              disabled={claiming}
            >
              Skip
            </Button>
          </motion.div>
        </>
      )}
    </div>
  );
}
