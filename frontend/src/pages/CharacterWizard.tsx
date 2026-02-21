import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { WizardShell, type WizardStepConfig } from "@/components/wizard";
import { Card, Input, NumberStepper } from "@/components/ui";
import { useCampaignStore } from "@/stores/useCampaignStore";
import type { CharacterCreatePayload } from "@/api/campaigns";
import {
  D5E_CLASSES, computeDefaults, ALL_DAMAGE_TYPES,
  type D5eClass,
} from "@/constants/classDefaults";
import { clsx } from "clsx";
import {
  Axe, Music, Shield, Leaf, Sword, Wind, Sun, Target, Eye, Flame, Moon, Wand2, UserPlus,
} from "lucide-react";

const CLASS_ICONS: Record<D5eClass, typeof Sword> = {
  Barbarian: Axe, Bard: Music, Cleric: Shield, Druid: Leaf,
  Fighter: Sword, Monk: Wind, Paladin: Sun, Ranger: Target,
  Rogue: Eye, Sorcerer: Flame, Warlock: Moon, Wizard: Wand2,
};

const ABILITIES = ["str", "dex", "con", "int", "wis", "cha"] as const;

export function CharacterWizard() {
  const navigate = useNavigate();
  const { addCharacter } = useCampaignStore();
  const [loading, setLoading] = useState(false);

  const makeSteps = useCallback((): WizardStepConfig[] => [
    {
      id: "identity",
      title: "Who Are They?",
      subtitle: "Name your character and choose their class",
      validate: (data) => !!((data.name as string)?.trim()) && !!(data.character_class as string),
      content: ({ data, onUpdate }) => (
        <div className="space-y-6">
          <Input
            label="Character Name"
            placeholder="e.g., Aelindra Thornweave"
            value={(data.name as string) || ""}
            onChange={(e) => onUpdate({ name: e.target.value })}
            autoFocus
          />

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">Class</label>
            <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
              {D5E_CLASSES.map((cls) => {
                const Icon = CLASS_ICONS[cls];
                const isSelected = data.character_class === cls;
                return (
                  <Card
                    key={cls}
                    hover
                    selected={isSelected}
                    padding="sm"
                    onClick={() => {
                      const defaults = computeDefaults(cls, (data.level as number) || 1);
                      onUpdate({ character_class: cls, ...defaults });
                    }}
                  >
                    <div className="text-center py-1">
                      <Icon size={20} className={clsx("mx-auto mb-1", isSelected ? "text-accent" : "text-gray-400")} />
                      <div className="text-xs font-medium text-gray-200">{cls}</div>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>

          <Input
            label="Subclass (optional)"
            placeholder="e.g., Champion, Divination"
            value={(data.subclass as string) || ""}
            onChange={(e) => onUpdate({ subclass: e.target.value })}
          />
        </div>
      ),
    },
    {
      id: "stats",
      title: "How Tough Are They?",
      subtitle: "Smart defaults are pre-filled from their class. Adjust as needed.",
      content: ({ data, onUpdate }) => {
        const level = (data.level as number) || 1;
        const cls = (data.character_class as D5eClass) || "Fighter";

        const updateLevel = (newLevel: number) => {
          const defaults = computeDefaults(cls, newLevel);
          onUpdate({ level: newLevel, ...defaults });
        };

        return (
          <div className="space-y-6">
            <div className="flex justify-center">
              <NumberStepper
                label="Level"
                value={level}
                onChange={updateLevel}
                min={1}
                max={20}
                size="lg"
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">AC</label>
                <input
                  type="number" min={1} max={30}
                  className="w-full bg-surface-2 text-white text-center text-lg font-bold px-3 py-2.5 rounded-lg border border-surface-3 focus:outline-none focus:ring-2 focus:ring-accent/40"
                  value={(data.ac as number) || 10}
                  onChange={(e) => onUpdate({ ac: +e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Max HP</label>
                <input
                  type="number" min={1}
                  className="w-full bg-surface-2 text-white text-center text-lg font-bold px-3 py-2.5 rounded-lg border border-surface-3 focus:outline-none focus:ring-2 focus:ring-accent/40"
                  value={(data.max_hp as number) || 10}
                  onChange={(e) => onUpdate({ max_hp: +e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Speed</label>
                <input
                  type="number" min={0} step={5}
                  className="w-full bg-surface-2 text-white text-center text-lg font-bold px-3 py-2.5 rounded-lg border border-surface-3 focus:outline-none focus:ring-2 focus:ring-accent/40"
                  value={(data.speed as number) || 30}
                  onChange={(e) => onUpdate({ speed: +e.target.value })}
                />
              </div>
            </div>
          </div>
        );
      },
    },
    {
      id: "saves",
      title: "Saving Throws",
      subtitle: "Pre-filled from class proficiencies. Estimates are fine — these help generate fair encounters.",
      skippable: true,
      content: ({ data, onUpdate }) => {
        const saves = (data.saves as Record<string, number>) || {};
        return (
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
            {ABILITIES.map((ab) => (
              <div key={ab} className="text-center">
                <label className="block text-xs text-gray-400 uppercase font-medium mb-1">{ab}</label>
                <input
                  type="number"
                  className="w-full bg-surface-2 text-white text-center font-bold px-2 py-2.5 rounded-lg border border-surface-3 focus:outline-none focus:ring-2 focus:ring-accent/40"
                  value={saves[ab] ?? 0}
                  onChange={(e) => onUpdate({ saves: { ...saves, [ab]: +e.target.value } })}
                />
              </div>
            ))}
          </div>
        );
      },
    },
    {
      id: "damage",
      title: "Damage Types",
      subtitle: "What damage types can this character deal? Tap to toggle.",
      skippable: true,
      content: ({ data, onUpdate }) => {
        const types = (data.damage_types as string[]) || [];
        const toggle = (dt: string) => {
          const next = types.includes(dt) ? types.filter((t) => t !== dt) : [...types, dt];
          onUpdate({ damage_types: next });
        };

        return (
          <div className="flex flex-wrap gap-2 justify-center">
            {ALL_DAMAGE_TYPES.map((dt) => {
              const isActive = types.includes(dt);
              return (
                <button
                  key={dt}
                  type="button"
                  className={clsx(
                    "px-4 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer capitalize",
                    isActive
                      ? "bg-accent/20 text-accent border border-accent/40"
                      : "bg-surface-2 text-gray-400 border border-surface-3 hover:border-gray-500",
                  )}
                  onClick={() => toggle(dt)}
                >
                  {dt}
                </button>
              );
            })}
          </div>
        );
      },
    },
    {
      id: "review",
      title: "Character Summary",
      subtitle: "Review your character before adding them to the party",
      content: ({ data }) => {
        const name = (data.name as string) || "Unnamed";
        const cls = (data.character_class as string) || "Fighter";
        const sub = (data.subclass as string) || "";
        const level = (data.level as number) || 1;
        const ac = (data.ac as number) || 10;
        const hp = (data.max_hp as number) || 10;
        const types = (data.damage_types as string[]) || [];

        return (
          <Card padding="lg" glow className="max-w-sm mx-auto text-center space-y-3">
            <h3 className="text-xl font-display font-bold text-gradient-gold">{name}</h3>
            <p className="text-sm text-gray-400">
              Level {level} {cls}{sub ? ` (${sub})` : ""}
            </p>
            <div className="flex justify-center gap-6 text-sm">
              <div>
                <div className="text-lg font-bold text-white">{ac}</div>
                <div className="text-xs text-gray-500">AC</div>
              </div>
              <div>
                <div className="text-lg font-bold text-hp-full">{hp}</div>
                <div className="text-xs text-gray-500">HP</div>
              </div>
            </div>
            {types.length > 0 && (
              <div className="flex flex-wrap justify-center gap-1">
                {types.map((t) => (
                  <span key={t} className="text-xs bg-surface-2 text-gray-400 px-2 py-0.5 rounded capitalize">{t}</span>
                ))}
              </div>
            )}
          </Card>
        );
      },
    },
  ], []);

  const handleComplete = async (data: Record<string, unknown>) => {
    setLoading(true);
    try {
      // Coerce all numeric fields to numbers and enforce Pydantic minimums (ge=1)
      const payload: CharacterCreatePayload = {
        name: ((data.name as string) || "").trim(),
        character_class: (data.character_class as string) || "Fighter",
        subclass: (data.subclass as string) || null,
        level: Math.max(1, Math.min(20, Number(data.level) || 1)),
        ac: Math.max(1, Math.min(30, Number(data.ac) || 10)),
        max_hp: Math.max(1, Number(data.max_hp) || 10),
        speed: Math.max(0, Number(data.speed) || 30),
        saves: (data.saves as Record<string, number>) || {},
        damage_types: (data.damage_types as string[]) || [],
        capabilities: {},
      };

      // Coerce save values to numbers
      if (payload.saves) {
        for (const key of Object.keys(payload.saves)) {
          payload.saves[key] = Number(payload.saves[key]) || 0;
        }
      }

      await addCharacter(payload);
      navigate("/party");
    } catch (err) {
      console.error("[CharacterWizard] Failed to create character:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-8">
      <div className="text-center mb-2">
        <UserPlus size={24} className="mx-auto text-accent mb-2" />
      </div>
      <WizardShell
        steps={makeSteps()}
        onComplete={handleComplete}
        completionLabel="Add to Party"
        completionLoading={loading}
        initialData={{ level: 1, character_class: "Fighter", ...computeDefaults("Fighter", 1) }}
      />
    </div>
  );
}
