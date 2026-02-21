/**
 * D&D-style stat block renderer for Open5e monster JSON.
 * Interactive: clickable ability scores, color-coded damage pills, collapsible sections.
 */

import { useState } from "react";
import { clsx } from "clsx";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { DAMAGE_TYPE_COLORS, type DamageType } from "@/constants/damageTypes";

import type { MonsterStatblock } from "@/types/creature";

interface StatBlockProps {
  statblock: MonsterStatblock;
  className?: string;
}

const ABILITY_KEYS = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"] as const;
const ABILITY_ABBR: Record<string, string> = {
  strength: "STR",
  dexterity: "DEX",
  constitution: "CON",
  intelligence: "INT",
  wisdom: "WIS",
  charisma: "CHA",
};

function abilityMod(score: number): number {
  return Math.floor((score - 10) / 2);
}

function formatMod(mod: number): string {
  return mod >= 0 ? `+${mod}` : `${mod}`;
}

function formatSpeed(speed: Record<string, string> | string | undefined): string {
  if (typeof speed === "string") return speed;
  if (typeof speed === "object" && speed !== null) {
    const entries = Object.entries(speed);
    return entries
      .map(([k, v]) => (k === "walk" ? `${v} ft.` : `${k} ${v} ft.`))
      .join(", ");
  }
  return "30 ft.";
}

function formatAC(ac: number | unknown): string {
  if (typeof ac === "number") return String(ac);
  if (typeof ac === "object" && ac !== null) {
    if (Array.isArray(ac)) {
      const first = ac[0] as { value?: number } | undefined;
      if (first && typeof first === "object" && "value" in first) {
        return String(first.value);
      }
      return String(first ?? "?");
    }
  }
  return String(ac ?? "?");
}

interface ActionEntry {
  name?: string;
  desc?: string;
  attack_bonus?: number;
  damage_dice?: string;
}

/** Collapsible action section with animated expand/collapse. */
function CollapsibleActionBlock({ title, actions }: { title: string; actions: ActionEntry[] }) {
  const [open, setOpen] = useState(true);

  if (!actions || actions.length === 0) return null;
  return (
    <div>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full text-xs font-bold uppercase tracking-wider text-red-400 border-b border-red-400/30 pb-1 mb-2 cursor-pointer hover:text-red-300 transition-colors"
      >
        {title} ({actions.length})
        <motion.span animate={{ rotate: open ? 0 : -90 }} transition={{ duration: 0.15 }}>
          <ChevronDown size={12} />
        </motion.span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden space-y-2"
          >
            {actions.map((a, i) => (
              <div key={i} className="text-xs leading-relaxed">
                <span className="font-semibold text-white italic">{a.name || "Unknown"}.</span>{" "}
                <span className="text-gray-300">{a.desc || ""}</span>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function InfoLine({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value) return null;
  return (
    <div className="text-xs">
      <span className="font-semibold text-gray-300">{label}</span>{" "}
      <span className="text-gray-400">{value}</span>
    </div>
  );
}

/** Color-coded damage type pills for vulnerabilities/resistances/immunities. */
function DamageTypePills({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value) return null;

  // Parse comma-separated damage types, handling compound entries like
  // "bludgeoning, piercing, and slashing from nonmagical attacks"
  const types = value
    .toLowerCase()
    .split(/[,;]/)
    .map((t) => t.trim().replace(/^and\s+/, ""))
    .filter(Boolean);

  return (
    <div className="text-xs">
      <span className="font-semibold text-gray-300 block mb-1">{label}</span>
      <div className="flex flex-wrap gap-1">
        {types.map((t, i) => {
          // Try to match a known damage type for coloring
          const knownType = Object.keys(DAMAGE_TYPE_COLORS).find((dt) =>
            t.startsWith(dt),
          ) as DamageType | undefined;

          const colorClass = knownType
            ? DAMAGE_TYPE_COLORS[knownType]
            : "text-gray-400";
          const bgClass = knownType
            ? colorClass.replace("text-", "bg-").replace("400", "400/15")
            : "bg-gray-400/15";

          return (
            <span
              key={i}
              className={clsx(
                "inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium",
                colorClass,
                bgClass,
              )}
            >
              {t}
            </span>
          );
        })}
      </div>
    </div>
  );
}

/** Clickable ability score that toggles between showing score and modifier prominently. */
function AbilityScore({ abbr, score }: { abbr: string; score: number }) {
  const [showMod, setShowMod] = useState(false);
  const mod = abilityMod(score);

  return (
    <button
      onClick={() => setShowMod(!showMod)}
      className="cursor-pointer hover:bg-surface-2 rounded p-1 transition-colors"
      title={`Click to toggle score/modifier`}
    >
      <div className="text-[10px] font-bold text-red-400 uppercase">{abbr}</div>
      <AnimatePresence mode="wait">
        {showMod ? (
          <motion.div
            key="mod"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ duration: 0.12 }}
          >
            <div className={clsx("text-lg font-bold", mod >= 0 ? "text-emerald-400" : "text-red-400")}>
              {formatMod(mod)}
            </div>
            <div className="text-[10px] text-gray-500">{score}</div>
          </motion.div>
        ) : (
          <motion.div
            key="score"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ duration: 0.12 }}
          >
            <div className="text-sm font-bold text-white">{score}</div>
            <div className="text-[10px] text-gray-500">({formatMod(mod)})</div>
          </motion.div>
        )}
      </AnimatePresence>
    </button>
  );
}

export function StatBlockPanel({ statblock, className }: StatBlockProps) {
  if (!statblock || Object.keys(statblock).length === 0) {
    return (
      <div className={clsx("text-xs text-gray-500 italic py-2", className)}>
        No stat block available.
      </div>
    );
  }

  const s = statblock;
  const name = s.name || "Unknown";
  const size = s.size || "";
  const type = s.type || "";
  const alignment = s.alignment || "";
  const subtitle = [size, type, alignment].filter(Boolean).join(", ");

  const hp = s.hit_points;
  const hitDice = s.hit_dice;
  const ac = s.armor_class;
  const speed = s.speed;

  // Saves
  const saveMap = {
    strength: s.strength_save,
    dexterity: s.dexterity_save,
    constitution: s.constitution_save,
    intelligence: s.intelligence_save,
    wisdom: s.wisdom_save,
    charisma: s.charisma_save,
  } as const;
  const saves = ABILITY_KEYS
    .map((k) => {
      const val = saveMap[k];
      return val != null ? `${ABILITY_ABBR[k]} +${val}` : null;
    })
    .filter(Boolean);

  // Skills
  const skills = s.skills;
  const skillStr = skills
    ? Object.entries(skills)
        .map(([k, v]) => `${k} +${v}`)
        .join(", ")
    : null;

  const actions = s.actions || [];
  const bonusActions = s.bonus_actions || [];
  const reactions = s.reactions || [];
  const legendaryActions = s.legendary_actions || [];
  const legendaryDesc = s.legendary_desc;
  const specialAbilities = s.special_abilities || [];

  return (
    <div className={clsx("bg-[var(--surface-1)] border border-[var(--surface-3)] rounded-lg p-4 space-y-3", className)}>
      {/* Header */}
      <div className="border-b border-red-400/30 pb-2">
        <h3 className="font-display font-bold text-lg text-red-400">{name}</h3>
        {subtitle && <p className="text-xs text-gray-500 italic">{subtitle}</p>}
      </div>

      {/* Core Stats */}
      <div className="space-y-1 text-xs border-b border-[var(--surface-3)] pb-3">
        <div>
          <span className="font-semibold text-gray-300">Armor Class</span>{" "}
          <span className="text-white">{formatAC(ac)}</span>
        </div>
        <div>
          <span className="font-semibold text-gray-300">Hit Points</span>{" "}
          <span className="text-white">{String(hp ?? "?")}</span>
          {hitDice && <span className="text-gray-500"> ({hitDice})</span>}
        </div>
        <div>
          <span className="font-semibold text-gray-300">Speed</span>{" "}
          <span className="text-white">{formatSpeed(speed)}</span>
        </div>
      </div>

      {/* Ability Scores — clickable to toggle score/modifier */}
      <div className="grid grid-cols-6 gap-1 text-center border-b border-[var(--surface-3)] pb-3">
        {ABILITY_KEYS.map((key) => {
          const score = s[key] ?? 10;
          return (
            <AbilityScore key={key} abbr={ABILITY_ABBR[key]!} score={score} />
          );
        })}
      </div>

      {/* Key Info */}
      <div className="space-y-1 border-b border-[var(--surface-3)] pb-3">
        {saves.length > 0 && <InfoLine label="Saving Throws" value={saves.join(", ")} />}
        {skillStr && <InfoLine label="Skills" value={skillStr} />}
        <DamageTypePills label="Damage Vulnerabilities" value={s.damage_vulnerabilities} />
        <DamageTypePills label="Damage Resistances" value={s.damage_resistances} />
        <DamageTypePills label="Damage Immunities" value={s.damage_immunities} />
        <InfoLine label="Condition Immunities" value={s.condition_immunities} />
        <InfoLine label="Senses" value={s.senses} />
        <InfoLine label="Languages" value={s.languages} />
        <InfoLine label="Challenge" value={s.challenge_rating != null ? String(s.challenge_rating) : undefined} />
      </div>

      {/* Special Abilities */}
      <CollapsibleActionBlock title="Traits" actions={specialAbilities} />

      {/* Actions */}
      <CollapsibleActionBlock title="Actions" actions={actions} />

      {/* Bonus Actions */}
      <CollapsibleActionBlock title="Bonus Actions" actions={bonusActions} />

      {/* Reactions */}
      <CollapsibleActionBlock title="Reactions" actions={reactions} />

      {/* Legendary Actions */}
      {(legendaryActions.length > 0 || legendaryDesc) && (
        <CollapsibleLegendaryBlock actions={legendaryActions} desc={legendaryDesc} />
      )}
    </div>
  );
}

function CollapsibleLegendaryBlock({ actions, desc }: { actions: ActionEntry[]; desc?: string }) {
  const [open, setOpen] = useState(true);

  return (
    <div>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full text-xs font-bold uppercase tracking-wider text-red-400 border-b border-red-400/30 pb-1 mb-2 cursor-pointer hover:text-red-300 transition-colors"
      >
        Legendary Actions
        <motion.span animate={{ rotate: open ? 0 : -90 }} transition={{ duration: 0.15 }}>
          <ChevronDown size={12} />
        </motion.span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            {desc && (
              <p className="text-xs text-gray-400 italic mb-2">{desc}</p>
            )}
            <div className="space-y-2">
              {actions.map((a, i) => (
                <div key={i} className="text-xs leading-relaxed">
                  <span className="font-semibold text-white italic">{a.name || "Unknown"}.</span>{" "}
                  <span className="text-gray-300">{a.desc || ""}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
