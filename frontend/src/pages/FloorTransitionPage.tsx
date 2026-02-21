import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useRunStore } from "@/stores/useRunStore";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { useEconomyStore } from "@/stores/useEconomyStore";
import { useMetaStore } from "@/stores/useMetaStore";
import { Card, Badge, Button, ProgressBar } from "@/components/ui";
import { Coins, Sparkles, ArrowDown, Trophy, XCircle, ScrollText, Quote, Hammer, Gem, GitBranch } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { FloorDescent } from "@/components/transitions/FloorDescent";
import { TypewriterText } from "@/components/transitions/TypewriterText";
import { IntensityCurve } from "@/components/charts/IntensityCurve";
import { SecretEventBanner } from "@/components/encounter/SecretEventBanner";
import { secretEventsApi, type SecretEvent } from "@/api/secretEvents";

export function FloorTransitionPage() {
  const navigate = useNavigate();
  const { run, floor, startFloor, startArena, endRun, setPhase } = useRunStore();
  const { activeCampaignId } = useCampaignStore();
  const { goldBalance, astralShardBalance, fetchBalance } = useEconomyStore();
  const { loreBeats, fetchLoreBeats } = useMetaStore();

  const [transitioning, setTransitioning] = useState(false);
  const [showDescent, setShowDescent] = useState(false);
  const [descentComplete, setDescentComplete] = useState(false);
  const [secretEvent, setSecretEvent] = useState<SecretEvent | null>(null);
  const [secretEventChecked, setSecretEventChecked] = useState(false);

  useEffect(() => {
    if (activeCampaignId) {
      fetchBalance(activeCampaignId);
    }
  }, [activeCampaignId, fetchBalance]);

  // Check for secret events at floor transition
  useEffect(() => {
    if (run && !secretEventChecked) {
      setSecretEventChecked(true);
      const floorNum = run.floors_completed;
      if (floorNum > 0) {
        secretEventsApi
          .check(run.id, floorNum, "floor_transition")
          .then((event) => {
            if (event) setSecretEvent(event);
          })
          .catch(() => {});
      }
    }
  }, [run, secretEventChecked]);

  const floorNumber = floor?.floor_number ?? (run ? run.floors_completed : 0);
  const totalFloors = run?.floor_count ?? 4;
  const floorsCompleted = run?.floors_completed ?? 0;
  const isAllFloorsComplete = floorsCompleted >= totalFloors;

  // Fetch lore beats for the completed floor
  useEffect(() => {
    if (activeCampaignId && floorNumber > 0) {
      fetchLoreBeats(activeCampaignId, floorNumber, "floor_end");
    }
  }, [activeCampaignId, floorNumber, fetchLoreBeats]);

  // Auto-navigate to run complete if all floors done
  useEffect(() => {
    if (isAllFloorsComplete) {
      const timer = setTimeout(() => {
        setPhase("run-complete");
        navigate("/run/complete");
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isAllFloorsComplete, setPhase, navigate]);

  const handleNextFloor = useCallback(async () => {
    setTransitioning(true);
    setShowDescent(true);
  }, []);

  const handleDescentComplete = useCallback(async () => {
    setDescentComplete(true);
    try {
      await startFloor();
      await startArena();
      navigate("/run/encounter");
    } catch (err) {
      console.error("[FloorTransition] Failed to start next floor:", err);
      setTransitioning(false);
      setShowDescent(false);
      setDescentComplete(false);
    }
  }, [startFloor, startArena, navigate]);

  const handleEndRun = async () => {
    if (!activeCampaignId) return;
    setTransitioning(true);
    try {
      await endRun(activeCampaignId, "completed");
      navigate("/run/complete");
    } catch (err) {
      console.error("[FloorTransition] Failed to end run:", err);
      setTransitioning(false);
    }
  };

  if (!run) {
    return <div className="py-8 text-center text-gray-400">No active run data.</div>;
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-2 pt-6"
      >
        {isAllFloorsComplete ? (
          <>
            <Trophy size={40} className="mx-auto text-gold animate-float" />
            <h1 className="text-3xl font-display font-bold text-gradient-gold">
              Final Floor Complete!
            </h1>
            <p className="text-gray-400">All {totalFloors} floors conquered. Preparing your summary...</p>
          </>
        ) : (
          <>
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
            >
              <ArrowDown size={32} className="mx-auto text-accent" />
            </motion.div>
            <h1 className="text-2xl font-display font-bold text-white">
              Floor {floorNumber} Complete
            </h1>
            <p className="text-sm text-gray-400">
              {floorsCompleted} of {totalFloors} floors cleared
            </p>
          </>
        )}
      </motion.div>

      {/* Floor Descent Overlay */}
      <AnimatePresence>
        {showDescent && !descentComplete && (
          <FloorDescent
            fromFloor={floorNumber}
            toFloor={floorNumber + 1}
            onComplete={handleDescentComplete}
          />
        )}
      </AnimatePresence>

      {/* Lore Beats — Narrative Spine */}
      <AnimatePresence>
        {loreBeats.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="space-y-3"
          >
            {loreBeats.map((beat, i) => (
              <motion.div
                key={beat.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + i * 0.15 }}
              >
                <Card padding="lg" className="border border-accent/20 bg-surface-0/80">
                  {/* Arbiter Quote — typewriter for drama */}
                  {beat.arbiter_text && (
                    <div className="mb-3">
                      <div className="flex items-start gap-2">
                        <Quote size={14} className="text-accent flex-shrink-0 mt-1" />
                        <div>
                          <TypewriterText
                            text={beat.arbiter_text}
                            speed={30}
                            delay={400 + i * 600}
                            className="text-sm text-gray-200 italic font-display leading-relaxed"
                            cursorColor="bg-accent"
                          />
                          <p className="text-[11px] text-accent mt-1">— The Arbiter</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Aethon Quote — typewriter */}
                  {beat.aethon_text && (
                    <div className="mb-3">
                      <div className="flex items-start gap-2">
                        <Quote size={14} className="text-red-400 flex-shrink-0 mt-1" />
                        <div>
                          <TypewriterText
                            text={beat.aethon_text}
                            speed={25}
                            delay={800 + i * 600}
                            className="text-sm text-gray-200 italic font-display leading-relaxed"
                            cursorColor="bg-red-400"
                          />
                          <p className="text-[11px] text-red-400 mt-1">— Aethon</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* DM Stage Direction */}
                  {beat.dm_stage_direction && (
                    <p className="text-xs text-gray-500 italic border-t border-surface-3 pt-2 mt-2">
                      {beat.dm_stage_direction}
                    </p>
                  )}

                  {/* Lore Fragment Badge */}
                  {beat.lore_fragment_id && (
                    <div className="mt-2 flex items-center gap-1.5">
                      <ScrollText size={12} className="text-blue-400" />
                      <Badge color="blue" className="text-[10px]">
                        Lore Fragment Discovered
                      </Badge>
                    </div>
                  )}
                </Card>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Secret Event */}
      <AnimatePresence>
        {secretEvent && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ delay: 0.3 }}
          >
            <SecretEventBanner
              event={secretEvent}
              onDismiss={() => setSecretEvent(null)}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floor progress bar */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <ProgressBar
          value={floorsCompleted}
          max={totalFloors}
          label={`Floor Progress: ${floorsCompleted} / ${totalFloors}`}
          color={isAllFloorsComplete ? "gold" : "green"}
          size="md"
        />
      </motion.div>

      {/* Stats summary — cascading stagger */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={{
          hidden: {},
          visible: { transition: { staggerChildren: 0.12, delayChildren: 0.4 } },
        }}
        className="grid grid-cols-2 gap-3"
      >
        {[
          { icon: <Coins size={20} className="mx-auto text-gold mb-1" />, value: run.total_gold_earned, label: "Gold Earned", color: "text-gold" },
          { icon: <Sparkles size={20} className="mx-auto text-shard mb-1" />, value: run.total_shards_earned, label: "Shards Earned", color: "text-shard" },
        ].map((stat) => (
          <motion.div
            key={stat.label}
            variants={{
              hidden: { opacity: 0, y: 16, scale: 0.95 },
              visible: { opacity: 1, y: 0, scale: 1 },
            }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          >
            <Card padding="md" className="text-center">
              {stat.icon}
              <div className={`text-2xl font-bold font-display ${stat.color}`}>{stat.value}</div>
              <div className="text-xs text-gray-500">{stat.label}</div>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {/* Balance */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
      >
        <Card padding="sm">
          <div className="flex justify-between text-sm">
            <div className="flex items-center gap-2">
              <Coins size={14} className="text-gold" />
              <span className="text-gray-400">Balance:</span>
              <span className="font-bold text-gold">{goldBalance}</span>
            </div>
            <div className="flex items-center gap-2">
              <Sparkles size={14} className="text-shard" />
              <span className="text-gray-400">Shards:</span>
              <span className="font-bold text-shard">{astralShardBalance}</span>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Intensity Curve */}
      {run?.id && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.55 }}
        >
          <Card padding="md">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
              Difficulty Director
            </h3>
            <IntensityCurve runId={run.id} />
          </Card>
        </motion.div>
      )}

      {/* Armillary Services */}
      {!isAllFloorsComplete && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.65 }}
          className="space-y-2"
        >
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider text-center">
            The Armillary's Services
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <Card
              hover
              padding="md"
              className="cursor-pointer border-gold/20"
              onClick={() => navigate("/forge?returnTo=/run/floor-transition")}
            >
              <div className="text-center space-y-1">
                <Hammer size={20} className="mx-auto text-gold" />
                <div className="text-sm font-display font-semibold text-gold">Enhancement Forge</div>
                <div className="text-[10px] text-gray-500">
                  <Coins size={10} className="inline mr-0.5" />{goldBalance} gold
                </div>
              </div>
            </Card>
            <Card
              hover
              padding="md"
              className="cursor-pointer border-shard/20"
              onClick={() => navigate("/gacha?returnTo=/run/floor-transition")}
            >
              <div className="text-center space-y-1">
                <Gem size={20} className="mx-auto text-shard" />
                <div className="text-sm font-display font-semibold text-shard">Pull Banners</div>
                <div className="text-[10px] text-gray-500">
                  <Sparkles size={10} className="inline mr-0.5" />{astralShardBalance} shards
                </div>
              </div>
            </Card>
            <Card
              hover
              padding="md"
              className="cursor-pointer border-purple-400/20"
              onClick={() => navigate("/attunement?returnTo=/run/floor-transition")}
            >
              <div className="text-center space-y-1">
                <GitBranch size={20} className="mx-auto text-purple-400" />
                <div className="text-sm font-display font-semibold text-purple-400">Attunement</div>
                <div className="text-[10px] text-gray-500">Spend essence on talents</div>
              </div>
            </Card>
          </div>
        </motion.div>
      )}

      {/* Actions */}
      {!isAllFloorsComplete && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="flex gap-3"
        >
          <Button
            variant="primary"
            size="lg"
            glow
            icon={<ArrowDown size={18} />}
            onClick={handleNextFloor}
            loading={transitioning}
            className="flex-1"
          >
            Descend to Floor {floorNumber + 1}
          </Button>
          <Button
            variant="danger"
            size="lg"
            icon={<XCircle size={16} />}
            onClick={handleEndRun}
            disabled={transitioning}
          >
            End Run
          </Button>
        </motion.div>
      )}
    </div>
  );
}
