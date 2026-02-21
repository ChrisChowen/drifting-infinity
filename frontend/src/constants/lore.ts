/**
 * Drifting Infinity — Lore & Flavor System
 *
 * The Armillary is a sentient arcane construct — part arena, part experiment, part trap.
 * It drifts through the planes, drawing in creatures and champions, testing them,
 * learning from them, and adapting. The DM assumes the role of the Arbiter —
 * the Armillary's voice and judge.
 */

// ─── Screen Names ────────────────────────────────────────────────────────────

export const SCREEN_NAMES: Record<string, string> = {
  lobby: "The Nexus",
  party: "The Roster",
  forge: "The Forge",
  gacha: "The Vault",
  archive: "The Chronicle",
  attunement: "Armillary Attunement",
  chronicles: "The Chronicle",
  settings: "Armillary Controls",
  welcome: "The Threshold",
  "run/setup": "Expedition Planning",
  "run/encounter": "Arena Briefing",
  "run/combat": "The Arena",
  "run/summary": "Arena Aftermath",
  "run/rewards": "Spoils of Battle",
  "run/shop": "The Wandering Merchant",
  "run/floor-transition": "Descent",
  "run/complete": "Expedition's End",
};

// ─── Screen Descriptions ─────────────────────────────────────────────────────

export const SCREEN_DESCRIPTIONS: Record<string, string> = {
  lobby: "The central chamber where expeditions are planned and champions await orders.",
  party: "Where the Arbiter assembles the challengers who will face the Armillary's trials.",
  forge: "The Artificer's workshop — enhancements forged from the arena's essence.",
  gacha: "The Armillary's vault of relics — weapons, armor, and boons from past challengers.",
  archive: "The Chronicle of Expeditions — every trial recorded, every outcome measured.",
  attunement: "Channel essence into the Armillary's talent matrix — permanent advantages for future expeditions.",
  chronicles: "A record of discoveries, triumphs, and the Armillary's secrets — lore fragments and achievements.",
  settings: "The Armillary's control mechanisms — adjust the arena's parameters.",
  welcome: "The threshold between worlds — where the Arbiter first awakens the Armillary.",
};

// ─── Loading Messages ────────────────────────────────────────────────────────

export const LOADING_MESSAGES: Record<string, string[]> = {
  default: [
    "The Armillary stirs...",
    "Arcane gears align...",
    "The planes shift...",
    "Consulting ancient mechanisms...",
    "The Armillary processes...",
  ],
  lobby: [
    "The Nexus hums with potential...",
    "Champions await your command, Arbiter...",
    "The Armillary assesses the challengers...",
    "Expedition records materialize...",
    "The central chamber awakens...",
  ],
  party: [
    "The Roster crystallizes...",
    "Champion profiles emerge from the aether...",
    "The Armillary studies its challengers...",
    "Measuring combat potential...",
  ],
  forge: [
    "The Artificer stokes the forge...",
    "Molten essence flows through channels...",
    "Enhancement matrices align...",
    "The forge fires burn bright...",
    "Korvath prepares the crucible...",
  ],
  gacha: [
    "The Vault's mechanisms engage...",
    "Relics stir within their crystalline prisons...",
    "Echoes of past challengers resonate...",
    "The Armillary unlocks its treasures...",
    "Ancient power coalesces...",
  ],
  archive: [
    "The Chronicle unfurls its pages...",
    "Expedition records materialize...",
    "The Armillary recalls past trials...",
    "Battle data reconstructs...",
    "Patterns emerge from the chronicle...",
  ],
  attunement: [
    "The talent matrix resonates...",
    "Essence pathways illuminate...",
    "The Armillary opens its attunement channels...",
    "Ancient power flows through the branches...",
    "The matrix awaits your choice, Arbiter...",
  ],
  chronicles: [
    "The Chronicle compiles its records...",
    "Lore fragments coalesce from memory...",
    "Achievements materialize in golden light...",
    "The Armillary recalls what it has witnessed...",
    "Secrets whisper from the pages...",
  ],
  encounter: [
    "The Armillary selects its champions...",
    "Arena defenses calibrate...",
    "Hostile creatures are summoned...",
    "The arena reshapes itself...",
    "Environmental hazards charge...",
    "The Armillary chooses its weapons...",
  ],
  combat: [
    "Initiative order crystallizes...",
    "Combat matrices engage...",
    "The arena pulses with energy...",
    "The Armillary observes...",
  ],
  rewards: [
    "Spoils of battle manifest...",
    "The arena yields its treasures...",
    "Victory resonance detected...",
    "The Armillary offers tribute...",
  ],
  shop: [
    "A merchant emerges from the shadows...",
    "Wares from distant planes materialize...",
    "The Wandering Merchant arrives...",
    "Exotic goods shimmer into view...",
  ],
  floor: [
    "The arena descends deeper...",
    "New challenges await below...",
    "The Armillary intensifies...",
    "Deeper mechanisms engage...",
    "The descent continues...",
  ],
};

/** Get a random loading message for a given route context */
export function getLoadingMessage(context?: string): string {
  const pool = context && LOADING_MESSAGES[context];
  const messages = pool || LOADING_MESSAGES.default!;
  return messages[Math.floor(Math.random() * messages.length)]!;
}

// ─── Arbiter Quotes ──────────────────────────────────────────────────────────

export const ARBITER_QUOTES: Record<string, string[]> = {
  welcome: [
    "The Armillary has been waiting for you, Arbiter.",
    "Another cycle begins. The arena remembers all who enter.",
    "Welcome back. The Armillary has learned from its last challengers.",
  ],
  lobby: [
    "Choose your champions wisely — the Armillary adapts to weakness.",
    "Every expedition teaches the arena something new.",
    "The Armillary grows restless. It craves a challenge.",
    "Your challengers' fate is in your hands, Arbiter.",
    "The arena remembers those who fell. And those who survived.",
    "Steel, spell, and strategy — the Armillary tests all three.",
  ],
  run_start: [
    "The descent begins. May your champions prove worthy.",
    "The Armillary stirs — it has prepared new trials.",
    "Into the depths. The arena awaits with calculated malice.",
    "Another expedition. The Armillary wagers against you.",
  ],
  floor_transition: [
    "Deeper. The Armillary intensifies its defenses.",
    "The arena shifts. New threats crystallize below.",
    "Your champions descend. The Armillary has learned from the last floor.",
    "The deeper you go, the more the Armillary invests in stopping you.",
    "The gears turn. The next floor will not be as forgiving.",
  ],
  combat_start: [
    "The arena seals. Let the trial begin.",
    "Hostile creatures materialize. The Armillary watches.",
    "Combat initiated. The arena records everything.",
    "The Armillary's creatures have their orders. Do your champions have theirs?",
  ],
  death: [
    "A champion falls. The Armillary adds their essence to its collection.",
    "One less challenger. The arena drinks deep.",
    "Death is not the end — merely a setback. If lives remain.",
    "The Armillary claims another. It grows stronger.",
    "Fallen, but not forgotten. The Chronicle records all.",
  ],
  victory: [
    "The arena yields. For now.",
    "Your champions prevail. The Armillary takes note.",
    "Victory — but the Armillary is already planning its next move.",
    "Well fought. The arena respects strength.",
  ],
  defeat: [
    "The Armillary prevails. As it often does.",
    "Your champions fall. The arena resets, hungry for new challengers.",
    "Defeat is a teacher. Return when you are ready.",
    "The Armillary collects its due. Another expedition ends.",
  ],
  shop: [
    "A figure emerges from between dimensions. Their wares are... unusual.",
    "The Wandering Merchant exists outside the Armillary's control. Mostly.",
    "Gold speaks louder than steel in this place between trials.",
  ],
  forge: [
    "The Artificer awaits. What shall we forge today?",
    "Enhancement essence flows freely after battle.",
    "The forge burns with captured arena energy.",
    "Korvath nods approvingly. Good materials to work with.",
  ],
  vault: [
    "The Vault stirs. Relics from a thousand expeditions lie within.",
    "The Armillary's treasures are won by fate, not force.",
    "Past challengers left their mark. Perhaps their power lingers.",
    "The Vault resonates. Something powerful draws near.",
  ],
  armillary_effect: [
    "The Armillary intervenes!",
    "The arena shifts — the Armillary asserts its will.",
    "An arcane surge ripples through the arena.",
    "The Armillary's influence manifests...",
    "The arena responds to the flow of combat.",
  ],
  reward: [
    "The arena yields its treasures to the victorious.",
    "Choose wisely — every reward shapes the expedition ahead.",
    "The Armillary offers tribute. For now.",
  ],
  talent_unlock: [
    "The Armillary's matrix responds. A new pathway opens.",
    "Essence flows into the attunement channels. Power crystallizes.",
    "The talent matrix hums with newfound energy.",
    "A permanent bond forms between Arbiter and Armillary.",
    "The arena acknowledges your investment. It will test you accordingly.",
  ],
  achievement_earned: [
    "The Chronicle records a new triumph.",
    "An achievement crystallizes — the Armillary takes note.",
    "Your champions' deeds echo through the arena's memory.",
    "Worthy of recognition. The Armillary respects persistence.",
  ],
  lore_discovered: [
    "A fragment of truth surfaces from the Armillary's depths.",
    "The arena reveals one of its secrets. There are many more.",
    "Knowledge is the true treasure of the Armillary.",
    "Another piece of the puzzle. The Chronicle grows.",
  ],
  essence_earned: [
    "Essence flows from the Armillary to the Arbiter.",
    "The arena yields its deeper currency — pure essence.",
    "With enough essence, even the Armillary's secrets can be unlocked.",
    "Essence accumulates. The attunement matrix awaits.",
  ],
};

/** Get a random Arbiter quote for a given event */
export function getArbiterQuote(event: string): string {
  const pool = ARBITER_QUOTES[event];
  const quotes = pool || ARBITER_QUOTES.lobby!;
  return quotes[Math.floor(Math.random() * quotes.length)]!;
}

// ─── Armillary Identity ──────────────────────────────────────────────────────

export const ARMILLARY_IDENTITY = {
  name: "The Armillary",
  tagline: "A sentient arcane arena that learns, adapts, and challenges.",
  description: [
    "The Armillary is an ancient arcane construct that drifts between the planes of existence. Part arena, part experiment, part prison — it draws in creatures from across reality and pits them against those bold enough to enter.",
    "It is not merely a dungeon. It watches. It learns. Every spell cast, every sword swing, every tactical decision is recorded and analyzed. The creatures it summons grow more cunning. Its environmental hazards grow more devious. Its rewards grow more enticing.",
    "You are the Arbiter — the one who guides champions through the Armillary's trials. You interpret its machinations, narrate its horrors, and decide when mercy or cruelty serves the greater challenge.",
    "The Armillary does not want to destroy your champions. It wants to test them. To push them to the very edge of their abilities. A dead challenger teaches nothing. A champion who barely survives — that is data worth collecting.",
  ],
  dm_role: "As the Arbiter, you are the Armillary's voice and judge. The tool handles encounter generation, difficulty scaling, and mechanical tracking — you bring the world to life.",
  lore_hooks: [
    "Who built the Armillary? And why does it continue to operate?",
    "What happens to the essence of those who fall within its walls?",
    "Is the Armillary's growing intelligence a feature... or a malfunction?",
    "The Wandering Merchant seems immune to the Armillary's control. How?",
    "Korvath the Artificer was once a challenger. Now he serves the arena. Why?",
  ],
};

// ─── In-World Navigation Labels ──────────────────────────────────────────────

export const NAV_LABELS = {
  lobby: { name: "The Nexus", icon: "Home", tooltip: "Central hub — plan expeditions and manage your campaign" },
  party: { name: "The Roster", icon: "Users", tooltip: "Assemble and manage the champions who face the Armillary" },
  attunement: { name: "Attunement", icon: "GitBranch", tooltip: "Channel essence into permanent talents for future expeditions" },
  chronicles: { name: "Chronicles", icon: "ScrollText", tooltip: "Lore fragments, achievements, and the Armillary's secrets" },
  forge: { name: "The Forge", icon: "Anvil", tooltip: "Purchase permanent enhancements for your champions" },
  gacha: { name: "The Vault", icon: "Sparkles", tooltip: "Acquire magic items and boons from the Armillary's collection" },
  archive: { name: "The Chronicle", icon: "BookOpen", tooltip: "Review expedition history, statistics, and the Armillary's assessment" },
  settings: { name: "Controls", icon: "Settings", tooltip: "Configure the Armillary's parameters" },
} as const;
