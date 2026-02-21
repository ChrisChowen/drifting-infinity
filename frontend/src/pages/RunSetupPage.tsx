import { useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { useRunStore } from "@/stores/useRunStore";
import { useMetaStore } from "@/stores/useMetaStore";
import { WizardShell, type WizardStepConfig } from "@/components/wizard";
import { Card, Badge, Button, PageHeader, EmptyState } from "@/components/ui";
import { Play, Users, Layers, Grid3X3, Swords, GitBranch, Heart, Mountain } from "lucide-react";
import { clsx } from "clsx";
import { motion } from "framer-motion";

const FLOOR_OPTIONS = [
  { value: 10, label: "10 Floors", desc: "Half Descent", icon: Swords },
  { value: 20, label: "20 Floors", desc: "Full Descent", icon: Mountain },
];

export function RunSetupPage() {
  const navigate = useNavigate();
  const { activeCampaignId, characters, fetchCharacters } = useCampaignStore();
  const { startRun, startFloor, startArena, run, floor } = useRunStore();
  const { meta, talents, fetchMeta, fetchTalents } = useMetaStore();

  useEffect(() => {
    if (activeCampaignId) {
      fetchCharacters();
      fetchMeta(activeCampaignId);
      fetchTalents(activeCampaignId);
    }
  }, [activeCampaignId, fetchCharacters, fetchMeta, fetchTalents]);

  const derivedLevel = characters.length > 0
    ? Math.max(1, Math.floor(characters.reduce((s, c) => s + c.level, 0) / characters.length))
    : 1;

  // If we have a run with a floor and the floor isn't complete, go straight to encounter
  useEffect(() => {
    if (run && floor && !floor.is_complete) {
      // Floor already started — skip setup
    }
  }, [run, floor]);

  // Handle resuming an existing run that needs a floor or arena started
  const handleResumeRun = async () => {
    if (run && !floor) {
      // Need to start a floor
      await startFloor();
    }
    if (run && floor) {
      await startArena();
      navigate("/run/encounter");
    }
  };

  const makeSteps = useCallback((): WizardStepConfig[] => {
    const steps: WizardStepConfig[] = [];

    // Only show new run steps if no active run
    if (!run) {
      steps.push(
        {
          id: "party",
          title: "Your Party Awaits",
          subtitle: `${characters.length} adventurer${characters.length !== 1 ? "s" : ""} ready for battle`,
          validate: () => characters.length > 0,
          content: () => (
            <div className="space-y-4">
              {characters.length === 0 ? (
                <EmptyState
                  icon={<Users size={40} />}
                  title="No Party Members"
                  description="Add at least one character before entering the Armillary."
                  action={
                    <Button icon={<Users size={16} />} onClick={() => navigate("/party/add")}>
                      Add Character
                    </Button>
                  }
                />
              ) : (
                <div className="space-y-2">
                  {characters.map((c, i) => (
                    <motion.div
                      key={c.id}
                      initial={{ opacity: 0, x: -12 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.06 }}
                    >
                      <Card padding="sm">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div>
                              <div className="font-display font-semibold text-white text-sm">{c.name}</div>
                              <div className="text-xs text-gray-500">
                                {c.character_class}{c.subclass ? ` (${c.subclass})` : ""}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-3 text-xs">
                            <Badge color="gold">Lv {c.level}</Badge>
                            <span className="text-gray-500">AC {c.ac}</span>
                            <span className="text-gray-500">HP {c.max_hp}</span>
                          </div>
                        </div>
                      </Card>
                    </motion.div>
                  ))}
                  <div className="text-center pt-2">
                    <Badge color="emerald">Party Level {derivedLevel}</Badge>
                  </div>
                </div>
              )}
            </div>
          ),
        },
        {
          id: "floors",
          title: "How Deep?",
          subtitle: "Choose how many floors to descend into the Armillary",
          content: ({ data, onUpdate }) => {
            const selected = (data.floors as number) || 20;
            return (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-md mx-auto">
                {FLOOR_OPTIONS.map((opt) => {
                  const Icon = opt.icon;
                  const isSelected = selected === opt.value;
                  return (
                    <Card
                      key={opt.value}
                      hover
                      selected={isSelected}
                      padding="md"
                      onClick={() => onUpdate({ floors: opt.value })}
                    >
                      <div className="text-center space-y-2 py-2">
                        <Icon
                          size={28}
                          className={clsx("mx-auto", isSelected ? "text-accent" : "text-gray-500")}
                        />
                        <div className="font-display font-semibold text-white">{opt.label}</div>
                        <div className="text-xs text-gray-500">{opt.desc}</div>
                      </div>
                    </Card>
                  );
                })}
              </div>
            );
          },
        },
        {
          id: "loadout",
          title: "Run Loadout",
          subtitle: "Active meta-talents that will shape this expedition",
          content: () => {
            const unlockedTalents = talents.filter((t) => t.is_unlocked);
            const hasExtraLife = meta?.unlocked_talents?.includes("resilience_1");
            const runNumber = (meta?.total_runs_completed ?? 0) + 1;
            return (
              <div className="space-y-4">
                {/* Lives + Run Number */}
                <div className="flex justify-center gap-6">
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1 mb-1">
                      {Array.from({ length: hasExtraLife ? 4 : 3 }, (_, i) => (
                        <Heart key={i} size={16} className="text-red-400 fill-red-400" />
                      ))}
                    </div>
                    <div className="text-xs text-gray-500">{hasExtraLife ? 4 : 3} Lives</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-accent font-display">#{runNumber}</div>
                    <div className="text-xs text-gray-500">Run Number</div>
                  </div>
                </div>

                {/* Active Talents */}
                {unlockedTalents.length > 0 ? (
                  <div className="space-y-2">
                    <h4 className="text-xs text-gray-500 uppercase tracking-wider text-center">Active Talents</h4>
                    {unlockedTalents.map((t) => (
                      <Card key={t.id} padding="sm">
                        <div className="flex items-center gap-2">
                          <GitBranch size={14} className="text-accent" />
                          <span className="text-sm font-semibold text-white">{t.name}</span>
                          <Badge color="gray" className="text-[10px] ml-auto">{t.branch} T{t.tier}</Badge>
                        </div>
                        <p className="text-xs text-gray-500 mt-1 ml-6">{t.description}</p>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <GitBranch size={24} className="mx-auto text-gray-600 mb-2" />
                    <p className="text-sm text-gray-500">No talents unlocked yet</p>
                    <p className="text-xs text-gray-600 mt-1">Complete runs to earn essence for the Attunement</p>
                  </div>
                )}
              </div>
            );
          },
        },
        {
          id: "confirm",
          title: "Enter the Armillary",
          subtitle: "Review your expedition before descending",
          content: ({ data }) => {
            const floors = (data.floors as number) || 20;
            return (
              <Card glow padding="lg" className="max-w-sm mx-auto text-center space-y-4">
                <Layers size={32} className="mx-auto text-accent" />
                <div>
                  <h3 className="text-lg font-display font-bold text-gradient-gold">Expedition Summary</h3>
                  <p className="text-sm text-gray-400 mt-1">
                    {characters.length} adventurer{characters.length !== 1 ? "s" : ""} at Level {derivedLevel}
                  </p>
                </div>
                <div className="flex justify-center gap-8 text-sm">
                  <div>
                    <div className="text-xl font-bold text-white">{floors}</div>
                    <div className="text-xs text-gray-500">Floors</div>
                  </div>
                  <div>
                    <div className="text-xl font-bold text-white">{floors === 20 ? "Full" : "Half"}</div>
                    <div className="text-xs text-gray-500">Descent</div>
                  </div>
                </div>
                <p className="text-xs text-gray-600">
                  Arenas per floor scale with your tier. Longer runs can be paused between floors.
                </p>
              </Card>
            );
          },
        },
      );
    }

    return steps;
  }, [run, characters, derivedLevel, navigate, meta, talents]);

  if (!activeCampaignId) {
    return (
      <EmptyState
        icon={<Layers size={48} />}
        title="No Campaign Selected"
        description="Select or create a campaign from the Lobby first."
        action={<Button onClick={() => navigate("/")}>Go to Lobby</Button>}
      />
    );
  }

  if (characters.length === 0) {
    return (
      <EmptyState
        icon={<Users size={48} />}
        title="Your Party Is Empty"
        description="Add at least one character before entering the Armillary."
        action={
          <Button icon={<Users size={16} />} onClick={() => navigate("/party/add")}>
            Add Character
          </Button>
        }
      />
    );
  }

  // If run exists but needs floor/arena, show a resume state
  if (run && !floor) {
    return (
      <div className="py-8 max-w-2xl mx-auto space-y-6">
        <PageHeader
          title="Continue Run"
          subtitle={`Floor ${run.floors_completed + 1} of ${run.floor_count}`}
        />
        <Card glow padding="lg" className="text-center space-y-4">
          <Play size={32} className="mx-auto text-accent" />
          <h3 className="text-lg font-display font-semibold text-white">Ready for Floor {run.floors_completed + 1}</h3>
          <p className="text-sm text-gray-400">
            {run.floors_completed} of {run.floor_count} floors complete
          </p>
          <Button variant="primary" size="lg" glow icon={<Play size={18} />} onClick={handleResumeRun}>
            Descend to Floor {run.floors_completed + 1}
          </Button>
        </Card>
      </div>
    );
  }

  // If run and floor exist, go to encounter
  if (run && floor) {
    return (
      <div className="py-8 max-w-2xl mx-auto space-y-6">
        <PageHeader
          title="Run In Progress"
          subtitle={`Floor ${floor.floor_number} — Arena ${floor.arenas_completed + 1} of ${floor.arena_count}`}
        />
        <Card glow padding="lg" className="text-center space-y-4">
          <Grid3X3 size={32} className="mx-auto text-accent" />
          <h3 className="text-lg font-display font-semibold text-white">
            Arena {floor.arenas_completed + 1} Awaits
          </h3>
          <Button
            variant="primary"
            size="lg"
            glow
            icon={<Swords size={18} />}
            onClick={async () => {
              await startArena();
              navigate("/run/encounter");
            }}
          >
            Enter Arena
          </Button>
        </Card>
      </div>
    );
  }

  // New run wizard
  const handleComplete = async (data: Record<string, unknown>) => {
    const floors = (data.floors as number) || 20;
    await startRun(activeCampaignId, undefined, floors);
    await startFloor();
    await startArena();
    navigate("/run/encounter");
  };

  return (
    <div className="py-8">
      <div className="text-center mb-2">
        <Layers size={24} className="mx-auto text-accent mb-2" />
      </div>
      <WizardShell
        steps={makeSteps()}
        onComplete={handleComplete}
        completionLabel="Enter the Armillary"
        initialData={{ floors: 20 }}
      />
    </div>
  );
}
