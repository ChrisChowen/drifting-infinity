# Drifting Infinity

## Game Design Document v0.2

**February 2026 | Comprehensive Merged Specification**

---

## Executive Summary

Drifting Infinity is a standalone web application that transforms D&D 5e (2024) into a roguelike combat arena experience. It is a DM's companion tool: a second screen that handles procedural encounter generation, dynamic difficulty scaling, economy tracking, reward distribution, session-persistent progression, and live combat management. The DM still runs the table, narrates the action, rolls for monsters, and adjudicates edge cases. Players continue to use their preferred VTT for maps, tokens, and character sheets. Drifting Infinity runs the roguelike layer on top.

The core experience: a party of adventurers enters a shifting extradimensional arena called the Armillary. Each run consists of escalating floors of combat encounters, punctuated by reward choices, shops, and rest decisions. Between runs, players spend earned currency on permanent upgrades and pull from gacha-style banners that grant new character variants, weapons, and identities. Death is not the end but a setback. Every run, whether a triumph or a wipe, advances the team's meta-progression.

**Target audience:** DMs who want to run fast, replayable, combat-focused sessions for parties of 1-6+ players using 5e 2024 rules, without spending hours on prep.

**Design principles:**

- RAW 5e 2024 combat as the foundation, with a clean custom rules layer on top
- Optimized for 3-5 players, with scaling support from solo to 6+
- Standalone experience (no campaign required, though campaign content can be imported)
- Supports starting at any player level (1-20) with scaling through the full range
- Every run should feel distinct, every death should teach something, every session should advance something permanent
- The DM is the narrator and adjudicator; the app is the encounter architect and bookkeeper
- Tier 0 integration only: the app is a DM screen, not a VTT. Players use their existing VTT for maps and rolling

---

## Part 1: Game Structure

### 1.1 The Run

A run is a single expedition into the Armillary. It is the primary unit of play, designed to fill a 2-4 hour session depending on party size and pace. A run consists of 3-4 Floors, each containing 3-5 Arenas (individual combat encounters). Between floors, the party returns to the Lobby for rest, shopping, and reward selection.

A run ends when either: the party clears all floors (a successful run), or the entire party is eliminated within a floor (a failed run). Both outcomes return players to the Lobby with whatever currency and progression they have earned.

### 1.2 The Lobby

The Lobby is the persistent hub between runs. It is where players spend gold on enhancements, pull from gacha banners, review their build, and configure their next run. Mechanically, the Lobby represents a long rest: all HP, spell slots, and abilities are restored.

The Lobby offers:

- **The Enhancement Forge:** Purchase permanent stat upgrades with gold
- **The Banners:** Gacha pulls for character variants, weapons, and identities
- **The Armillary Console:** Configure the next run (select difficulty tier, view available modifiers, set starting level parameters)
- **The Archive:** Review run history, statistics, difficulty curves from previous runs, and unlocked content
- **Party Management:** Swap between base characters and gacha-pulled variants

### 1.3 Floors

Each floor is a sequence of 3-5 Arenas connected by brief transitions. The party does not take full rests between arenas within a floor. Instead, a partial recovery system called the **Momentum System** (see Part 2.5) provides limited resource recovery that equalizes class types while preserving attrition tension.

Between arenas within a floor, the party receives a **Reward Selection** (choose 1 of 3 options, following the Slay the Spire model) and may encounter a **Shop** (random chance, weighted higher on later arenas).

At the end of each floor (after the final arena), dead characters are resurrected and the party receives a **short rest**. This maintains pressure across floors while preventing total resource depletion from making later floors impossible.

Floor structure scales with configuration:

- **Floor 1:** 3 arenas. Base difficulty. Tutorial pace for the run.
- **Floor 2:** 4 arenas. Difficulty increases. CR minimum +1.
- **Floor 3:** 4 arenas. Difficulty increases again. CR minimum +2. Elite enemy pool unlocked.
- **Floor 4 (if present):** 5 arenas. Maximum difficulty. CR minimum +3. Boss encounter guaranteed on final arena.

The DM configures floor count during run setup. A 3-floor run suits a 2-hour session; a 4-floor run fills 3-4 hours.

### 1.4 Arenas

An arena is a single combat encounter on a single map. The app selects:

1. **Map** from the available pool (21+ maps, tagged with terrain type, size, and hazards)
2. **Enemy composition** via the encounter generation algorithm (Part 3)
3. **Environmental modifiers** (optional terrain effects, lighting, weather)
4. **Armillary Effects** (per-turn random events during combat)

Arena pacing targets 15-25 minutes of real-time play per arena for a party of 4. This means encounters should be challenging enough to require tactical thinking but not so brutal that they become 45-minute slogs. The encounter generator aims for 3-5 rounds of combat as the sweet spot.

### 1.5 Level Scaling Across the Full Range

Drifting Infinity supports starting at any player level from 1 to 20. The entire system scales with the party's level, and the difficulty curve must account for the fundamental power shifts across D&D's four tiers of play:

**Tier 1 (Levels 1-4): Fragile and Swingy.** Characters have very low HP pools. A single critical hit can drop a character. Encounter generation at this tier must be extremely conservative: no save-or-die effects, no permanent drain, strict single-monster CR caps (never exceeding average party level). The Armillary's hostile effects are tuned down. Floor count defaults to 3 with 3 arenas per floor.

**Tier 2 (Levels 5-10): The Sweet Spot.** Extra Attack, 3rd-level spells, Fireball, and subclass features create a significant power spike at level 5. CR is most accurate in this range. This is the tier the system is primarily optimized for. Full 4-floor runs with 4-5 arenas per floor are appropriate.

**Tier 3 (Levels 11-16): Caster Dominance Emerges.** 6th+ level spells, multiple attacks, and powerful class features mean parties punch well above what CR predicts. The encounter generator must scale harder: more creatures, higher CR minimums, more frequent Elite and Boss templates. The Armillary becomes more aggressive. Enhancement scaling must not stack with natural class power to create triviality.

**Tier 4 (Levels 17-20): Rocket Tag.** 9th-level spells, rapid Legendary Resistance consumption, and near-immunity to many threats create a fundamentally different game. Encounters at this tier require Legendary creatures as the baseline, environmental puzzles that can't be solved with raw power, and Armillary effects that specifically challenge high-level capabilities (antimagic fields, planar instability, etc.). Enhancement caps become critical to prevent total trivialization.

The encounter generation algorithm (Part 3) uses tier-specific parameters for every decision it makes.

---

## Part 2: Combat Rules Layer

The following rules modify standard 5e 2024 combat. They are designed to accelerate play, reward teamwork, and create the moment-to-moment excitement that makes roguelike combat compelling. Players use their standard character sheets and abilities; these rules layer on top.

### 2.1 The Weakness Exploit System

This is Drifting Infinity's signature mechanic, inspired by the Shin Megami Tensei/Persona "One More" system. It transforms D&D combat from individual turn optimization into a team coordination puzzle.

**Core rule:** When a player deals damage using a type to which the target is Vulnerable, or hits a target with a spell requiring a saving throw that the target fails using an ability score in which it has a negative modifier, this triggers a **Weakness Exploit**.

**On a Weakness Exploit:**

- The attacking player may immediately grant one ally a Reaction they can use before the start of the next creature's turn. This Reaction can be used to make a single weapon attack, cast a cantrip, move up to half their speed, or use the Help action.
- This bonus Reaction can itself trigger a Weakness Exploit if it hits another weakness, chaining the effect. A chain can continue until a Weakness Exploit fails to occur or every ally has already received a bonus Reaction this round.
- Each ally can only receive one bonus Reaction per round from Weakness Exploits.

**Why this works:** It creates a combo system where players actively plan turns around enemy weaknesses rather than defaulting to their highest-damage option. It rewards knowledge of the monster manual, encourages diverse damage types in party composition, and generates exciting chain sequences. The per-round cap prevents infinite loops while still allowing dramatic moments.

**Soft constraint for encounter generation:** Every encounter must include at least one creature with an exploitable vulnerability or notably weak save. If the generator produces an encounter where the Weakness Exploit system cannot activate, it must swap at least one creature for an alternative that enables it. Without this, the signature mechanic goes dormant and combat feels like generic 5e.

**DM tool support:** The app displays each enemy's vulnerabilities and weak save abilities prominently in the DM view, and flags when a Weakness Exploit triggers. The DM confirms each trigger with a single tap.

### 2.2 Modified Opportunity Attacks

**Rule:** Opportunity attacks are removed from standard play. A creature can only make an opportunity attack if it used the Ready action on its previous turn to prepare one.

**Why this works:** In standard 5e, opportunity attacks create a "sticky" battlefield where creatures rarely move once engaged. This is fine for narrative combat but kills the tactical dynamism that makes roguelike combat exciting. Removing default OAs means flanking, repositioning, and kiting become viable tactics. Requiring a Ready action to set up an OA creates a meaningful choice: do you attack now, or do you lock down an area?

### 2.3 The Fate Spinning Armillary

The Armillary is a persistent entity in every combat encounter. It sits at initiative count 0 (always last in the round). At the end of every round, the Armillary activates a random effect from a weighted table.

**Effect categories and base weights:**

- **Hostile (40%):** Adds a reinforcement enemy, imposes a condition on a random ally, triggers an environmental hazard, or shifts the arena terrain
- **Neutral (30%):** Teleports creatures, changes lighting, activates terrain features, reverses initiative order
- **Beneficial (20%):** Heals a random ally, grants temporary hit points, removes a condition, grants advantage
- **Chaos (10%):** Wild Magic-style effects affecting both sides

**Armillary Budget Cap:** Each arena has an Armillary Budget equal to 20% of the encounter's base XP budget. Hostile Armillary effects that add creatures or deal damage draw from this budget. Once the budget is spent, further hostile effects downgrade to the next-least-harmful hostile option (typically a condition rather than a reinforcement or damage spike). This preserves excitement while preventing runaway difficulty.

**Context-Sensitive Weight Adjustment:** Rather than static weights, the Armillary dynamically adjusts based on party state:

```
function adjustArmillaryWeights(baseWeights, partyState) {
  let modifier = 0

  // Party health assessment
  if (partyState.averageHpPercentage < 0.3) modifier -= 15
  else if (partyState.averageHpPercentage < 0.5) modifier -= 5

  // Death pressure
  if (partyState.anyoneOnFinalStand) modifier -= 10
  if (partyState.anyoneDead) modifier -= 15

  // Resource depletion
  if (partyState.averageSpellSlotsRemaining < 0.25) modifier -= 5

  // Encounter going too easily
  if (partyState.enemyHpPercentage < 0.3
      && partyState.roundNumber <= 2) modifier += 10

  return {
    hostile: clamp(baseWeights.hostile + modifier, 15, 60),
    neutral: baseWeights.neutral,
    beneficial: clamp(baseWeights.beneficial - modifier, 10, 40),
    chaos: baseWeights.chaos
  }
}
```

The weight shift is invisible to players, preserving the feeling of randomness while preventing feel-bad moments. The DM can always override.

**Floor Scaling:** As floor number increases, base hostile weight shifts upward (Floor 1: 40%; Floor 4: 55%) and Chaos effects become more dramatic.

**Armillary's Favour:** After clearing a floor, the party earns 1 Armillary's Favour (shared resource). Favour can be spent to force a reroll on any single Armillary-generated value: the difficulty roll, an enemy selection, a map choice, or an Armillary effect. This is the party's primary tool for managing bad luck.

### 2.4 Death and Recovery

Death handling balances roguelike tension with D&D's investment in characters.

**Within an arena:**

- First time a character drops to 0 HP: standard death saving throws apply. Allies can heal them as normal.
- Once a character has been brought back up (whether by succeeding on death saves or being healed), they gain the **Final Stand** condition for the remainder of that arena. Final Stand: the next time this character drops to 0 HP, they die immediately. No death saves.
- **Special rule:** Will-o'-Wisps and similar creatures that exploit dying characters (Consume Life, etc.) cannot trigger their life-consumption abilities against characters on Final Stand. This prevents an unavoidable death spiral.

**Within a floor:**

- Dead characters remain dead until the floor is cleared (all arenas completed by surviving party members).
- At the end of a floor, dead characters are resurrected with 1 HP and the party takes a short rest.
- If all characters die within a floor, the run ends (failed run). The party returns to the Lobby with whatever gold they earned before the wipe.

**Between floors:**

- Short rest (not long rest). Hit dice can be spent. Short rest abilities recharge.
- Dead characters return at 1 HP.

**Between runs:**

- Long rest. Full restoration.

### 2.5 The Momentum System (Partial Recovery Between Arenas)

**The Problem:** 5e classes are wildly unequal in how they handle resource attrition. A Warlock with short-rest slots thrives across multiple encounters. A Wizard burning 3rd-level slots across 5 arenas without a rest feels punished. No rests between arenas preserves attrition tension but creates a severe class imbalance. Full short rests between every arena would eliminate attrition entirely for short-rest classes. The Momentum System sits in the middle.

**Core Mechanic:** After each arena, each character may recover **ONE** of the following (player's choice):

- One expended spell slot of 3rd level or lower
- One use of a class feature that recharges on a short rest
- Hit points equal to one roll of their hit die (without expending the hit die)
- Remove one condition carried over from the previous arena

**Momentum Bonus:** If the party cleared the arena without any character dropping to 0 HP, each character may recover **TWO** of the above instead of one. Additionally, the Momentum Bonus unlocks a fifth option:

- One use of a class feature that recharges on a long rest (Bardic Inspiration, Wild Shape, Channel Divinity, etc.)

This rewards clean play while providing a path for long-rest-dependent classes to stay competitive without opening the floodgates.

**Why Momentum Instead of Short Rests:** A full short rest restores ALL short-rest features and allows spending ALL hit dice. That eliminates attrition for short-rest classes while leaving long-rest casters relatively depleted. The Momentum system equalizes recovery across class types through player choice. A Fighter recovers HP. A Wizard recovers a spell slot. A Monk recovers Ki. This creates between-arena decision-making that adds strategic depth to the roguelike loop.

**Class Archetype Analysis:**

*Favoured by attrition (monitor for dominance):*

- Warlock: Eldritch Blast is a strong at-will option. Between-floor short rests give full slot recovery.
- Fighter: Action Surge is single-use between rests. Second Wind provides self-sustain.
- Rogue: Sneak Attack is fully at-will, no resource expenditure.

*Neutral:*

- Monk: Ki is short-rest dependent. Momentum lets them recover some, but extended combat still burns through Ki.
- Ranger: Mix of at-will weapon attacks and limited spellcasting.
- Paladin: Divine Smite burns slots fast but baseline weapon attacks are strong.

*Penalised by attrition (needs Momentum most):*

- Wizard: Limited slots, many concentration spells, fragile.
- Sorcerer: Sorcery Points and spell slots both deplete fast.
- Bard: Heavily dependent on Bardic Inspiration uses and spell slots.
- Druid: Wild Shape uses are limited; spell slots critical for Moon Druid survival.

**Tuning Knob:** If playtesting reveals that long-rest casters are still significantly disadvantaged even with the Momentum Bonus option, the spell slot recovery cap can be raised to 4th level instead of 3rd. This is adjustable without changing the core system.

### 2.6 Mana Drain Redesign

The "Mana Drain" Armillary effect is redesigned from permanent slot loss to temporary suppression:

> "One random ally with remaining spell slots must succeed on a DC 13 Constitution saving throw or have their lowest available spell slot **suppressed** until the end of their next turn (the slot is not expended, just temporarily unavailable)."

This creates tactical pressure without permanent resource destruction that compounds across arenas.

### 2.7 Speed of Play Rules (Optional, DM-Toggled)

- **Shot Clock:** Each player has 60 seconds to declare their action. If the timer expires, their character takes the Dodge action. Configurable timer length.
- **Simultaneous Initiative:** All players act simultaneously, then all enemies act. Removes individual initiative tracking. Faster but less tactical.
- **Minion Rules:** Creatures below CR 1 become Minions: 1 HP, deal fixed damage (no rolling), defeated on any hit. Enables large mob encounters without tracking dozens of HP pools.

---

## Part 3: The Arena Director (Encounter Generation and Dynamic Balancing)

### 3.1 Design Philosophy: The Left 4 Dead Model Applied to D&D

Static encounter balancing is a solved problem with unsatisfying solutions. CR is a rough heuristic that degrades at Tier 1 (too swingy), works passably at Tier 2 (the sweet spot), and collapses at Tier 3-4 (CR increasingly underestimates party power). Every existing tool, from the DMG encounter builder to Sly Flourish's Lazy Benchmark, ultimately reduces to "guess and adjust." That is fine for a human DM improvising a campaign, but a procedural roguelike needs to do better.

Drifting Infinity's approach borrows from Left 4 Dead's AI Director: a feedback-driven state machine that monitors player state in real time and adjusts the experience to maintain a target intensity curve. The key insight from L4D is that balancing isn't about making every encounter equally hard. It's about pacing: build-up, peak, and release. Some arenas should be tense. Some should be cathartic stomps. Some should be genuinely terrifying. The Director manages this arc across a floor, not per-encounter.

**The Three Balancing Layers:**

1. **Pre-Generation (Static):** XP budgets, CR constraints, mechanical signature checks, and combo interaction rules. This produces a "theoretically balanced" encounter before any player data is considered.
2. **Adaptive Generation (Between-Arena):** The DM enters brief health/resource snapshots between arenas. The Director uses this data to adjust the next encounter's difficulty target, shifting the intensity curve up or down. This is where Drifting Infinity diverges from pure algorithmic balancing.
3. **Live Adjustment (Mid-Combat):** The DM has one-tap access to HP sliders, reinforcement spawning, retreat triggers, and Armillary overrides. The system suggests adjustments based on how combat is progressing but never acts autonomously; the DM always decides.

### 3.2 DM Health Snapshot: The Feedback Loop

Between each arena, the DM enters a brief snapshot of party state. This takes 30-60 seconds and is the critical data feed that makes adaptive difficulty possible.

**Required inputs (per character):**

- Current HP (numeric or a quick slider: Full / Above Half / Below Half / Critical / Down)
- Any conditions carried over (dropdown or toggle)
- Any Final Stand status (toggle)

**Optional inputs (party-wide, improves accuracy):**

- Approximate spell slots remaining (Full / Most / Half / Few / Empty)
- Key feature availability (e.g., "Action Surge used," "Bardic Inspiration: 2 remaining")
- DM difficulty assessment of the previous arena (Too Easy / Just Right / Too Hard / Near TPK)

The DM's subjective assessment is the most valuable single data point. It captures everything the algorithm cannot: player skill level, tactical coordination quality, how lucky or unlucky the dice were, and whether the table is having fun. This is explicitly modelled after the Resident Evil 4 difficulty rank system, where the game's internal difficulty counter adjusts based on player deaths, damage taken, and completion time, but wrapped in a D&D-appropriate interface.

**From this snapshot, the Director computes:**

```
PartyState {
  averageHpPercentage: float,
  lowestHpPercentage: float,
  anyOnFinalStand: boolean,
  anyDead: boolean,
  estimatedResourceDepletion: float,    // 0.0 = fresh, 1.0 = empty
  dmAssessment: "too_easy" | "just_right" | "too_hard" | "near_tpk",
  cumulativeStress: float,             // running total across the floor
  arenasCleared: int,
  arenasRemaining: int
}
```

### 3.3 The Intensity Curve: Pacing Across a Floor

Borrowing from L4D's Director state machine, each floor follows an intensity arc:

**Build-Up (Arena 1-2):** Moderate difficulty. The party learns what threats this floor contains. Encounter composition favours familiar tactical roles (Brutes, Soldiers) before introducing complex ones (Controllers, Lurkers). The Director is in "warming up" mode.

**Peak (Arena 3, or Arena 4 on longer floors):** Hard difficulty. The most complex encounters with the most dangerous creature combinations. This is where the encounter generator is allowed to use its full threat flag budget. The Armillary is at its most aggressive.

**Resolution (Final Arena):** The difficulty depends on party state. If the party is healthy and well-resourced, the final arena is the hardest encounter on the floor (Boss template or equivalent). If the party is depleted and struggling, the final arena is still challenging but avoids stacking threats, the idea being that the party should feel like they *earned* the floor clear rather than stumbling over the finish line through luck.

The Director achieves this by mapping the DM's health snapshots to a **Difficulty Target** for the next arena:

```
function computeDifficultyTarget(partyState, floorPosition) {
  // Base curve: follows the intensity arc
  let baseDifficulty = INTENSITY_CURVES[floorPosition]
  // baseDifficulty values:
  // Arena 1: 0.4 (Low-Moderate)
  // Arena 2: 0.6 (Moderate)
  // Arena 3: 0.85 (Hard)
  // Arena 4: 0.7 (Moderate-Hard, resolution)
  // Arena 5 (if present): 0.9 (Hard, Boss)

  // Adaptive adjustment based on party state
  let adjustment = 0

  // DM assessment is the strongest signal
  switch (partyState.dmAssessment) {
    case "too_easy":   adjustment += 0.15; break
    case "just_right": adjustment += 0.0;  break
    case "too_hard":   adjustment -= 0.10; break
    case "near_tpk":   adjustment -= 0.20; break
  }

  // Health-based adjustment
  if (partyState.averageHpPercentage < 0.3) adjustment -= 0.15
  else if (partyState.averageHpPercentage < 0.5) adjustment -= 0.05

  // Resource depletion
  if (partyState.estimatedResourceDepletion > 0.7) adjustment -= 0.10

  // Death pressure
  if (partyState.anyOnFinalStand) adjustment -= 0.05
  if (partyState.anyDead) adjustment -= 0.10

  // Cumulative stress (don't pile on if the floor has been brutal)
  if (partyState.cumulativeStress > 0.7) adjustment -= 0.10

  // Ensure the final arena is never trivial
  if (floorPosition === FINAL_ARENA) {
    adjustment = Math.max(adjustment, -0.15)
  }

  return clamp(baseDifficulty + adjustment, 0.2, 1.0)
}
```

The Difficulty Target (0.0-1.0) maps to encounter XP budget thresholds:

| Difficulty Target | Budget Level | Feel |
|---|---|---|
| 0.0-0.3 | Low (below Easy threshold) | Warm-up, resource recovery |
| 0.3-0.5 | Moderate (Easy to Medium) | Comfortable, strategic |
| 0.5-0.7 | Challenging (Medium to Hard) | Requires coordination |
| 0.7-0.85 | Hard (Hard to Deadly) | Dangerous, resources burn |
| 0.85-1.0 | Extreme (Deadly+) | Potential deaths, boss fights |

### 3.4 XP Budget Calculation (The Static Foundation)

The XP budget is calculated using a hybrid of 2024 DMG thresholds and 2014 encounter multipliers, with tier-specific adjustments.

**Step 1: Base XP Budget**

Use the 2024 DMG's three difficulty tiers (Low, Moderate, High) as starting ranges, interpolated by the Difficulty Target computed above.

**Step 2: Apply Encounter Multiplier (from 2014 DMG)**

The 2024 DMG dropped encounter multipliers, which was a significant regression. Multiple creatures are disproportionately more dangerous than their raw XP sum suggests due to action economy. The 2014 multipliers are essential:

| Creature Count | Multiplier |
|---|---|
| 1 | x1 |
| 2 | x1.5 |
| 3-6 | x2 |
| 7-10 | x2.5 |
| 11-14 | x3 |
| 15+ | x4 |

Party size adjusts: fewer than 3 PCs shifts the multiplier up one step; 6+ PCs shifts it down one step.

**Step 3: Tier-Specific CR Bounds**

| Tier | Min CR per Creature | Max Single CR | Notes |
|---|---|---|---|
| Tier 1 (1-4) | 1/8 | Party level + 1 | No creature above party level on Floor 1 |
| Tier 2 (5-10) | 1/2 | Party level + 3 | Most accurate CR range |
| Tier 3 (11-16) | 2 | Party level + 4 | Budget inflated 20% to challenge empowered parties |
| Tier 4 (17-20) | 5 | Party level + 5 | Budget inflated 40%, Legendary creatures baseline |

**Step 4: Floor Scaling**

Each floor increases the CR minimum by +1 and shifts the difficulty distribution:

- Floor 1: 50% Moderate, 30% Hard, 20% Low
- Floor 2: 30% Moderate, 50% Hard, 20% Extreme
- Floor 3: 20% Moderate, 40% Hard, 40% Extreme
- Floor 4: 10% Moderate, 30% Hard, 60% Extreme

### 3.5 Encounter Composition: The Ten-Step Pipeline

**Step 1: Select Encounter Template**

Choose a template based on the Difficulty Target and tactical variety (avoid repeating the same template within a floor):

- **Hold and Flank** (requires 1+ Soldier/Brute AND 1+ Lurker/Skirmisher)
- **Focus Fire** (requires 2+ Artillery or 1 Artillery + 1 Commander)
- **Attrition** (horde template, 6+ creatures, minion rules recommended)
- **Area Denial** (requires 1+ Controller)
- **Ambush** (requires 2+ Lurkers, dim/dark map)
- **Boss** (single powerful creature + support, only on final arenas or designated boss arenas)

**Step 2: Filter Candidate Pool**

From the monster database, select creatures matching:
- CR within the tier-appropriate range
- Tactical role matching the template's requirements
- Environment tags compatible with the selected map

**Step 3: Apply Hard Constraints (Section 3.6)**

Remove banned creatures for this tier/floor/difficulty.

**Step 4: Score Candidates**

Weight remaining candidates using:
- Weakness Exploit compatibility (boost creatures with vulnerabilities or weak saves matching party damage types)
- Party composition fit (reduce weight for creatures trivialized by party capabilities, increase for meaningfully challenging ones)
- Damage type diversity (boost candidates adding a new damage type to the encounter)
- Threat flag budget (track flags already in the encounter, reduce weight for candidates that would stack)
- Novelty (reduce weight for creatures the party has already fought this run)

**Step 5: Select Creatures**

From the weighted candidate pool, fill template slots to meet the XP budget.

**Step 6: Check Combo Interactions (Section 3.7)**

If the danger_multiplier from synergistic creatures pushes adjusted XP over budget, swap the cheaper creature for a non-synergistic alternative.

**Step 7: Validate Against Party Capabilities (Section 3.8)**

Check each creature's `party_warnings.dangerous_if_no` against actual party capabilities. REJECT mechanically impossible encounters; WARN on dangerous-but-survivable ones.

**Step 8: Run Sanity Checks**

- Sly Flourish Lazy Benchmark: total CR vs. character level sum
- Action economy check: total enemy actions per round should not exceed 2x party actions (3x for Extreme encounters)
- No more than 2 save-or-suck effects per encounter
- Single-monster CR cap: no single creature more than party level + tier-appropriate ceiling

**Step 9: Generate Tactical Brief**

Compose the unified tactical plan from behaviour profiles and encounter template (see Part 5).

**Step 10: Present to DM**

Display the encounter with any WARN flags highlighted. The DM approves, rerolls individual elements (spending Armillary's Favour if desired), or manually adjusts. The DM always has final approval.

### 3.6 Hard Constraints (Encounter Rejected if Violated)

**No save-or-die below Hard difficulty.** If any creature has `save_or_die: true`, the encounter must be rated Hard or above.

**No permanent drain on Floor 1.** Creatures with `permanent_drain: true` (Shadow, Specter, Wraith, Succubus) are excluded from Floor 1 entirely.

**No double-stacking incapacitation sources.** If one creature has `save_or_incapacitate: true`, the encounter may not include a second creature with the same flag unless it is a Boss template.

**Action denial cap.** Total per-round action denial effects may not exceed half the party size. A party of 4 should never face 3+ creatures that can each deny a turn.

**Party composition validation:**

```
function validateAgainstParty(encounter, party) {
  for (creature of encounter.creatures) {
    for (requirement of creature.party_warnings.dangerous_if_no) {
      if (!party.capabilities.includes(requirement)) {
        if (creature.threat_flags.flight_only
            && !party.has("ranged_damage")) {
          return REJECT  // party literally cannot damage this
        }
        if (creature.threat_flags.save_or_incapacitate
            && requirement === "high_wis_saves"
            && party.averageWisSave < 3) {
          return WARN  // flag for DM review
        }
      }
    }
  }
  return ACCEPT
}
```

The distinction between REJECT and WARN is critical. REJECT means the encounter is mechanically unfair with no counterplay. WARN means it is dangerous but options exist.

### 3.7 Combo Interaction Rules

Certain creature pairings are dramatically more dangerous than their individual CRs suggest. These are modelled as combo multipliers applied to the effective XP cost:

| Source Tag | Partner Tag | Multiplier | Reason |
|---|---|---|---|
| `imposes_restrained` | `high_single_hit_damage` | 1.4 | Restrained grants advantage, amplifying spike damage |
| `imposes_frightened` | `melee_brute` | 1.3 | Frightened prevents approach, negating melee PCs while brutes close in |
| `creates_darkness` | `has_blindsight_or_devilsight` | 1.5 | One side can see, the other cannot |
| `pack_tactics` | `pack_tactics` | 1.3/creature | Advantage on all attacks when allies are adjacent; stacks |
| `grapple_capable` | `environmental_hazard_map` | 1.4 | Grapple-drag into lava/pits/cliffs |
| `aoe_control_zone` | `forced_movement` | 1.3 | Push/pull targets into control zones |
| `summon_or_split` | `aoe_control_zone` | 1.5 | Controller protects summoner while action economy expands |
| `summon_or_split` | `any` | 1.2 | Action economy shifts mid-fight |
| `charm_or_dominate` | `high_single_hit_damage` | 1.5 | Dominated PC becomes the threat |

When the encounter generator selects creatures with matching combo tags, it multiplies the effective XP cost by the danger_multiplier before checking against the budget. This naturally limits how many synergistic threats appear together.

### 3.8 LLM-Assisted Threat Assessment (The Second Opinion)

Automated tagging of the SRD's 317 creatures will catch obvious threats through keyword parsing, but emergent dangers (ability chains, conditional lethality against specific party compositions, non-obvious synergies) require contextual reasoning that rule-based systems struggle with.

**The Hybrid Approach:**

1. **Automated Pipeline (First Pass):** Parse statblock JSON from 5e-database/Open5e. Extract damage output, effective HP, save profiles, and threat flags using keyword detection (see Part 4). This handles roughly 65-70% of creatures accurately.

2. **LLM Review (Second Pass):** For every creature flagged with any threat flag, and for every creature where automated tagging produced low-confidence results, submit the full statblock to a Claude API call with a structured prompt:

```
Given this D&D 5e creature statblock:
[statblock JSON]

And this party composition:
[party capabilities summary]

Rate the following for each of Tiers 1-4:
1. Danger rating (trivial/standard/dangerous/lethal/banned)
2. Any mechanical interactions not captured by: [list of automated flags]
3. Specific party compositions this creature hard-counters
4. Specific party compositions that trivialize this creature
5. Dangerous pairings with other creatures

Respond in JSON format matching MechanicalSignature schema.
```

3. **Manual Review (Third Pass):** For the approximately 40-50 highest-threat creatures (anything with save_or_die, save_or_incapacitate, permanent_drain, or charm_or_dominate), a human reviewer validates the combined automated + LLM assessment.

**Cost:** At roughly $0.003-0.01 per creature assessment using Claude Haiku with prompt caching, the full SRD can be assessed for under $3. This is a one-time data enrichment cost, not a per-session expense.

**Why not rely entirely on the LLM?** Because LLMs can hallucinate mechanical interactions that don't exist in the rules, and because deterministic constraint checking is more reliable than probabilistic reasoning for hard safety constraints (like "never put this creature against a party without ranged damage"). The LLM enriches the data; the constraint system enforces it.

### 3.9 Difficulty Curve Visualization

After each arena, the app updates a visual difficulty curve showing:

- **Planned difficulty** (what the Director intended for each arena)
- **Actual difficulty** (derived from the DM health snapshots and subjective assessment)
- **Party resource trajectory** (HP and estimated resources across the floor)
- **Cumulative stress** (running total of difficulty pressure)

This visualization serves two purposes:

1. **For the DM during the session:** A quick glance shows whether the floor is tracking harder or easier than intended, informing whether to accept the Director's next suggestion or manually adjust.

2. **For post-session review in the Archive:** Over multiple runs, the DM can see patterns. "Floor 3 is consistently too hard for this party." "The Ambush template always produces near-TPKs." This historical data, stored per-party, enables the system to learn that party's actual power level relative to what CR math predicts, creating a **Party Power Coefficient** that silently adjusts future XP budgets.

### 3.10 The Party Power Coefficient

Over time, the system accumulates data: what encounters the DM rated "just right," which were "too easy" or "too hard," how often characters drop, how many floors the party clears. From this, the Director computes a multiplicative adjustment:

```
PartyPowerCoefficient = runningAverage(
  encounterBudget / actualDifficultyRating
)
```

A coefficient of 1.0 means the party performs exactly as CR math predicts. Above 1.0 means the party is stronger than expected (well-optimized characters, experienced players, strong coordination). Below 1.0 means weaker (new players, unoptimized builds, small party).

The coefficient applies as a multiplier to all XP budgets for that party. A party with a coefficient of 1.3 gets encounters that are 30% harder than the base calculation. This happens silently, the DM never sees the number, but they do see that the encounters feel consistently "just right" even as the party grows more experienced.

The coefficient is visible in the Archive for DMs who want to understand it, and can be manually overridden.

### 3.11 Scaling Across the Full Level Range (1-20)

The encounter generation system must handle the full D&D level range, where power curves are non-linear and class capabilities introduce qualitative shifts at specific breakpoints.

**Level 1-2: Survival Mode**

Characters have 6-14 HP. A single goblin crit (2d6+2 = max 14) can kill outright. The system must:
- Cap creature damage output: no creature in the pool should have a single-hit damage potential exceeding the lowest party member's max HP
- Use smaller encounter groups (2-4 creatures maximum)
- Reduce Armillary hostile weight to 25% (from base 40%)
- Disable reinforcement Armillary effects entirely
- Default to 3 arenas per floor, 3 floors per run

**Level 3-4: Foundation**

Extra Attack is not yet online. Spellcasters have 1st and 2nd level slots only. The system can begin using standard encounter rules but still constrains:
- No save-or-die at any difficulty
- No permanent drain effects
- CR cap: party level + 1

**Level 5-10: Core Play**

The system is optimized for this range. Extra Attack, 3rd-level spells (Fireball, Counterspell), and subclass features create a significant power spike at level 5. Standard encounter rules apply. 4-floor runs with 4-5 arenas per floor are appropriate.

**Level 11-16: Caster Supremacy**

Wall of Force, Forcecage, simulacra, and 7th-level spells create qualitative shifts. The encounter generator must:
- Inflate XP budgets by 20-30% over standard calculations
- Require at least one creature with Magic Resistance or Counterspell per encounter at Hard+ difficulty
- Include environmental features that limit line-of-sight and prevent "I cast Wall of Force and win"
- Use Legendary creatures as encounter anchors more frequently
- The Armillary introduces Tier 3-specific effects: antimagic zones, planar instability, concentration checks

**Level 17-20: Rocket Tag**

Wish, True Polymorph, Shapechange, and 9th-level slots mean a single character can potentially end any encounter in one action. The system must:
- Inflate XP budgets by 40-50%
- Require multiple Legendary creatures or Mythic encounters as the baseline
- Enforce environmental constraints that prevent trivial solutions (dimensional anchors, anti-teleportation fields)
- Enhancement caps become critical (see Part 7) to prevent total trivialization
- Floor length may decrease (fewer arenas, each significantly harder) to maintain tension without grinding
- The Armillary becomes a strategic threat rather than a random one: effects at this tier should challenge high-level play specifically

**Enhancement Scaling Across Tiers:**

Player power at higher levels comes not just from class features but from accumulated Enhancements and Gacha items from previous runs. The system must account for this compounding:

```
function adjustBudgetForEnhancements(baseBudget, partyEnhancements) {
  let enhancementPower = sum(partyEnhancements.map(e => e.powerRating))
  let scalingFactor = 1.0 + (enhancementPower * 0.05)
  // Cap at 1.5x to prevent runaway inflation
  return baseBudget * Math.min(scalingFactor, 1.5)
}
```

This ensures that as players accumulate permanent upgrades across runs, the encounters scale to match, maintaining challenge without invalidating the progression system.

---

## Part 4: Monster Database and Mechanical Signatures

### 4.1 Data Sources

**Primary (Licensing Foundation):** SRD 5.2, released under CC-BY-4.0 by Wizards of the Coast. Approximately 317 creatures with full statblocks. This is the only source that can be distributed freely.

**Structured Data:** The 5e-database GitHub repository and Open5e API provide the SRD data in machine-readable JSON format, including parsed action blocks, ability scores, and traits. This is the intake pipeline.

**Extended Pool (Optional, User-Provided):** The Open5e API aggregates approximately 3,200+ creatures from third-party OGL/CC content. These can be imported but require the same tagging pipeline. For non-SRD WotC content (2024 Monster Manual's 500+ creatures), users would need to manually enter or import data; the system provides a statblock entry form but cannot distribute copyrighted content.

### 4.2 Tactical Role Classification

Every creature in the database is assigned a primary tactical role. This drives encounter composition template selection and tactical brief generation.

| Role | Colour Badge | Characteristics | Examples |
|---|---|---|---|
| **Brute** | Red | High HP, high damage, low AC, charges forward | Ogre, Minotaur, Hill Giant |
| **Soldier** | Gold | Moderate HP, moderate AC, holds position, protects allies | Hobgoblin Captain, Knight, Shield Guardian |
| **Artillery** | Blue | Low HP, ranged attacks, stays at distance | Flameskull, Mage, Spectator |
| **Controller** | Purple | Area denial, conditions, terrain manipulation | Beholder, Black Pudding, Gibbering Mouther |
| **Skirmisher** | Green | High mobility, hit-and-run, targets weak points | Goblin Boss, Phase Spider, Displacer Beast |
| **Lurker** | Grey | Stealth, ambush, high burst damage from hiding | Assassin, Shadow, Invisible Stalker |

**Assignment Algorithm:** Role is inferred from statblock analysis:

```
function assignRole(creature) {
  let scores = { brute: 0, soldier: 0, artillery: 0,
                 controller: 0, skirmisher: 0, lurker: 0 }

  // HP above CR-average suggests tankiness
  if (creature.hp > crAverageHp(creature.cr) * 1.2) scores.brute += 2
  if (creature.hp > crAverageHp(creature.cr) * 1.5) scores.brute += 2

  // High AC suggests defensive role
  if (creature.ac >= crAverageAc(creature.cr) + 2) scores.soldier += 3

  // Ranged attacks as primary action
  if (creature.primaryAttack.range > 30) scores.artillery += 3

  // AoE or condition-imposing abilities
  if (creature.hasAoE || creature.imposesConditions) scores.controller += 3

  // High speed + disengage/cunning action
  if (creature.speed >= 40 || creature.hasCunningAction) scores.skirmisher += 3

  // Stealth proficiency or invisibility
  if (creature.stealthBonus >= 6 || creature.hasInvisibility) scores.lurker += 3

  // Leadership or buff abilities
  if (creature.hasLeadershipAbility) scores.soldier += 2

  return roleWithHighestScore(scores)
}
```

Creatures can have a secondary role noted for encounters where they are cast against type. A Hobgoblin Captain is primarily a Soldier but functions as a Skirmisher in ambush encounters.

### 4.3 The Mechanical Signature Schema

Beyond tactical role, each creature receives a Mechanical Signature capturing the specific ways it threatens the party beyond raw HP damage.

```
MechanicalSignature {
  // Damage profile
  damage_output: {
    per_round_average: float,       // expected DPR at 65% hit rate
    per_round_max: float,           // DPR if everything hits/crits
    spike_potential: float,         // single highest possible damage
    damage_types: string[],
    requires_recharge: boolean
  }

  // Defensive profile
  effective_hp: float,              // HP adjusted for resistances/regen
  save_difficulty: {
    strong_saves: string[],
    weak_saves: string[],
    condition_immunities: string[],
    magic_resistance: boolean
  }

  // Threat mechanics
  threat_flags: {
    save_or_die: boolean,
    save_or_incapacitate: boolean,
    permanent_drain: boolean,
    action_denial: boolean,
    healing_prevention: boolean,
    forced_movement: boolean,
    summon_or_split: boolean,
    aoe_damage: boolean,
    aoe_control: boolean,
    stealth_ambush: boolean,
    flight_only: boolean,
    counterspell_or_dispel: boolean,
    charm_or_dominate: boolean,
    swarm_scaling: boolean,
    equipment_destruction: boolean
  }

  // Contextual danger by tier
  danger_by_tier: {
    tier1: "trivial"|"standard"|"dangerous"|"lethal"|"banned",
    tier2: "trivial"|"standard"|"dangerous"|"lethal"|"banned",
    tier3: "trivial"|"standard"|"dangerous"|"lethal",
    tier4: "trivial"|"standard"|"dangerous"|"lethal"
  }

  // Party composition interactions
  party_warnings: {
    dangerous_if_no: string[],
    trivialised_by: string[],
    hard_counters: string[]
  }

  // Weakness Exploit data
  exploit_profile: {
    vulnerabilities: string[],
    weak_saves: { ability: string, modifier: int }[],
    resistance_gaps: string[]
  }
}
```

### 4.4 Automated Tagging Pipeline

**Phase 1: Structural Parsing (Deterministic)**

Damage output, effective HP, save difficulty, and basic threat flags are extracted programmatically from statblock JSON:

| Field | Method |
|---|---|
| `per_round_average` | Parse actions, compute hit probability at 65%, sum multiattack |
| `spike_potential` | Maximum possible single-action damage including crits |
| `effective_hp` | Base HP x resistance multiplier (1.5 at T1, 1.25 at T2+ for common resistances) + regen amortized over 4 rounds |
| `strong_saves`/`weak_saves` | Directly from ability scores |
| `save_or_die` | Text search for "drops to 0" or "dies" with saving throw context |
| `aoe_damage` | Text search for "each creature in" or "each creature within" |
| `equipment_destruction` | Text search for "corrodes," "dissolves," "destroys" with equipment keywords |
| `flight_only` | Has fly speed, no land speed or primary attacks are ranged + fly |
| `summon_or_split` | Text search for "summon," "conjure," or split mechanics |

Estimated accuracy: 65-70% of all flags correctly assigned.

**Phase 2: LLM Enrichment (Contextual)**

For every creature with any threat flag, and for every creature where Phase 1 produced ambiguous results, submit the statblock to Claude API for contextual assessment (see Part 3, Section 3.8). This catches emergent threats like the Intellect Devourer's two-step kill combo and the Shadow's conditional lethality against low-Strength characters.

Estimated accuracy after Phase 2: 85-90%.

**Phase 3: Manual Review (Priority-Ordered)**

- **Priority 1:** Every creature with `save_or_die`, `save_or_incapacitate`, `permanent_drain`, or `charm_or_dominate`. Approximately 40-50 creatures.
- **Priority 2:** Every creature with `summon_or_split`, `healing_prevention`, or `flight_only`. Approximately 30-40 creatures.
- **Priority 3:** Everything else. Automated + LLM tagging is sufficient for creatures whose danger is adequately captured by CR.

For the extended Open5e pool (3,200+ creatures), run Phases 1-2 and flag anything with threat flags for community validation via a review interface.

### 4.5 Behaviour Profile Schema

Each tactical role has a default behaviour profile that drives the tactical brief generator:

```
BehaviourProfile {
  role: TacticalRole,
  positioning: "frontline" | "backline" | "flanking" | "mobile" | "hidden",
  target_priority: "nearest" | "lowest_ac" | "lowest_hp" |
                   "highest_threat" | "caster" | "random",
  retreat_threshold: float,
  ability_priority: string[],      // ordered action preferences
  group_tactics: string | null
}
```

**Default Profiles:**

- **Brute:** frontline, nearest, retreat at 0.25, prioritize multiattack, no group tactics
- **Soldier:** frontline, highest-threat, retreat at 0.3, prioritize defensive then attack, "shield wall" with other Soldiers
- **Artillery:** backline, caster or lowest-AC, retreat at 0.5, prioritize ranged/spell, "focus fire"
- **Controller:** backline, highest-threat cluster (AoE targeting), retreat at 0.4, prioritize area denial then debuffs
- **Skirmisher:** mobile, lowest-HP or opportunity, retreat at 0.5, prioritize hit-and-run, "harass"
- **Lurker:** hidden start, highest-value single target, retreat at 0.3 (via stealth), prioritize ambush then reposition, "pincer" with other Lurkers

**Intelligence Tier Modifiers:**

- **Mindless:** target_priority forced to "nearest," retreat_threshold 0.0, no group tactics
- **Instinctual:** target_priority limited to "nearest" or "lowest_hp," retreat active, no group tactics
- **Cunning:** full profile, group tactics active
- **Mastermind:** full profile plus adaptive targeting (switches targets based on party behaviour), "tactical withdrawal" instead of retreat

### 4.6 Notable SRD Creatures: Threat Analysis

The following creatures require special handling in the encounter generator.

**CR Liars (Far More Dangerous Than CR Suggests):**

- **Shadow (CR 1/2):** Strength drain on hit, no save. Target dies if Strength reaches 0. Against a Wizard with 8 Strength, two Shadows can kill in one round. Flags: `permanent_drain`. Constraint: never pair multiple Shadows against a party with any member below Strength 12 unless Hard+.
- **Intellect Devourer (CR 2):** Devour Intellect + Body Thief is a two-step kill combo. Flags: `save_or_die`. Banned on Floor 1 at all tiers; DM warning at all tiers.
- **Banshee (CR 4):** Wail drops to 0 HP on failed Con 13 save, 30ft radius. Flags: `save_or_die`, `aoe_damage`. Solo only, Hard+ encounters only.
- **Rust Monster (CR 1/2):** Destroys nonmagical metal equipment permanently. In a roguelike with equipment progression, potentially devastating. Flags: `equipment_destruction`. Only appears if party has magical weapon alternatives.
- **Will-o'-Wisp (CR 2):** Consume Life auto-fails one death save. Custom rule: cannot trigger against characters on Final Stand.
- **Specter (CR 1):** Life Drain reduces max HP. Constraint: cap number per encounter at party size.

**Encounter Warpers:**

- **Swallow creatures (Giant Toad CR 1, Behir CR 11, Purple Worm CR 15):** Remove characters from combat entirely. Constraint: max one Swallow creature per encounter, never against solo players.
- **Black Pudding (CR 4):** Splits on slashing damage. Flags: `summon_or_split`, `equipment_destruction`. Generator must account for potential creature count doubling.
- **Gibbering Mouther (CR 2):** AoE confusion + difficult terrain. Not dangerous in HP terms but extremely frustrating when paired with other threats.

**Tier Gatekeepers:**

- **Poison multiattack creatures (Giant Spider CR 1, Phase Spider CR 3):** Spike damage well above CR expectations. Flag: high `spike_potential` relative to tier.
- **Flameskull (CR 4):** Fireball (8d6 avg 28) can down multiple party members at Tier 1. Rejuvenation requires specific counter. Pair with Intel reward on preceding arena.
- **Mind Flayer (CR 7):** Mind Blast + Extract Brain is a two-round kill combo. Tier 1 and low Tier 2: banned. High Tier 2+: Boss template only.

---

## Part 5: Party Capabilities Model and DM Interface

### 5.1 Party Capabilities Schema

For the constraint system and adaptive difficulty to work, the app needs a structured representation of what the party can do. This is entered at run start and updated between arenas.

```
PartyCapabilities {
  // Defensive
  lowest_ac: int,
  lowest_hp: int,
  average_save_bonus: { str, dex, con, int, wis, cha },
  weakest_save_per_member: { characterId, save, bonus }[],
  condition_removal_available: boolean,
  death_ward_available: boolean,
  revivify_available: boolean,

  // Offensive
  damage_types_available: string[],
  magical_weapons: boolean,
  ranged_damage: boolean,
  aoe_available: boolean,

  // Tactical
  flight_available: boolean,
  teleportation_available: boolean,
  darkvision_count: int,
  stealth_capable: boolean,

  // Dynamic state (updated between arenas via DM snapshot)
  average_hp_percentage: float,
  average_spell_slots_remaining: float,
  any_on_final_stand: boolean,
  any_dead: boolean
}
```

**Data Entry:** At run start, the DM enters each character via a streamlined form: name, class, level, AC, HP, primary damage types, notable features (checkboxes for common capabilities like "has ranged attacks," "has flight," "has condition removal"). For repeat parties, this is saved and loaded automatically. The dynamic state updates between arenas via the DM Health Snapshot (Part 3, Section 3.2).

### 5.2 The DM Combat Interface

The DM interface is the product. Everything else is backend. If the interface is bad, nothing else matters. The core tension is information density versus cognitive load: the DM needs enough to run tactically interesting monsters without reading a wall of text mid-combat.

**Design Principle:** Layered information architecture. Essential info always visible. Tactical guidance one click away. Full statblock available but never forced.

### 5.3 The Encounter Brief (Pre-Combat Screen)

Before the DM starts an arena, they see a single-screen summary answering three questions: what am I running, how should these creatures behave, and what's the Armillary doing?

**Encounter Composition Panel:** Each creature type displayed as a card showing:
- Name, CR, HP (with adjustable slider range), AC
- Tactical role as a colour-coded badge
- Creature count as a multiplier
- Total adjusted XP and difficulty tier at the top

**Tactical Brief:** A 2-3 sentence encounter plan synthesized per-encounter, not per-creature. Rather than six individual monster descriptions, the system composes a unified tactical picture:

> "The Hobgoblin Captain (Soldier) holds the chokepoint at the bridge while two Hobgoblin Iron Shadows (Lurkers) use Shadow Jaunt to flank the backline. The Goblin Boss (Skirmisher) kites at range with Redirect Attack, using goblins (Minions) as ablative shields. Focus fire priority: lowest-AC target for the Lurkers, highest-threat caster for the Captain."

This brief is generated from template grammar driven by tactical tags, not by the LLM (keeping it deterministic and fast). The templates are the encounter composition templates from Part 3.5:

- **Hold and Flank:** "[Frontliner] holds [terrain feature] while [Flanker] uses [mobility ability] to reach [target priority]."
- **Focus Fire:** "[Artillery units] focus [target priority]. [Support creature] uses [buff/control ability] to enable."
- **Attrition:** "[Minions] engage nearest targets in groups of 2-3. [Commander] uses [leadership ability] and stays at medium range."
- **Area Denial:** "[Controller] uses [AoE/zone ability] to deny [area]. Other creatures herd targets toward controlled zones."
- **Ambush:** "All enemies begin hidden. [Lurkers] attack from [cover positions] targeting [priority]. After initial strike, [behaviour based on remaining composition]."

**Armillary Forecast:** Pre-rolled effects for rounds 1-5, displayed either fully revealed or as category indicators (Hostile/Neutral/Beneficial/Chaos) depending on DM preference toggle.

**Map Placement Zones:** Suggested creature starting positions described as zones rather than exact squares. "The Lurkers start in the shadowed alcoves. The Soldier holds the bridge chokepoint. The Skirmisher and Minions start in the open area south of the party's entry point."

### 5.4 The Live Combat Panel

During combat, the DM's screen shows three primary elements:

**Initiative Tracker with Embedded Status:** Each creature shows name, current HP as a visual bar (not a number), AC, and active conditions as icon badges. Clicking a creature expands its action panel. Current turn highlighted. The Armillary sits at initiative count 0 with its upcoming effect visible.

**Active Creature Action Panel:** When it is a monster's turn, the panel shows only what that creature will plausibly do, ordered by the tactical brief's priority:

- **Primary action:** "Multiattack: Longsword (+5, 1d8+3 slashing) x2" with a one-tap damage roller
- **Tactical action** (if situationally relevant): "Redirect Attack: swap places with adjacent goblin when targeted"
- **Movement note:** "Shadow Jaunt (recharge 5-6): Teleport 30ft to dim light or darkness"
- **Behavioural hint:** "Targets lowest-AC party member. Retreats via Shadow Jaunt if below 15 HP."

The full statblock is available via expansion but never shown by default. The DM should not need to read a full statblock during combat.

**One-Tap Damage Rolling:** Since this is a DM screen (Tier 0), the app rolls monster damage with a single tap. Results display the total, the breakdown, and the damage type. Players still roll their own dice in whatever VTT or physical setup they use.

**Weakness Exploit Tracker:** Persistent UI element showing:
- Which enemies have which vulnerabilities
- Which enemies have weak saves (and in what)
- A log of Weakness Exploits triggered this combat
- Whose bonus Reaction is available
- Visual indicator when a Weakness Exploit triggers (not just a log entry)
- DM confirms each trigger with a single tap

**Armillary Effect Bar:** Along the bottom. Shows current round's effect, countdown to activation (end of round), and DM override buttons (force beneficial, force hostile, spend Favour to reroll). When the Armillary activates, the effect description pops up with mechanical resolution instructions.

**Dynamic Adjustment Tools:** Accessible but not prominent (the DM should not feel pressured to use them):
- HP slider per creature (adjust mid-combat if the encounter is too easy or too hard)
- "Add Reinforcements" button (spawns an additional creature appropriate to the encounter)
- "Retreat Trigger" button (causes a creature to flee, reducing enemy count)
- Armillary override (force a specific effect category)

### 5.5 Post-Arena Summary

After combat ends, a brief summary screen shows:
- Gold earned
- Casualties and Final Stand status
- DM Health Snapshot input (the feedback loop from Part 3.2)
- Difficulty curve visualization update
- Transition to Reward Selection interface (pick 1 of 3)

The DM should never have to manually calculate anything post-combat.

### 5.6 The DM Health Snapshot Interface

This is the critical data entry point between arenas. Design for speed (30-60 seconds maximum):

**Quick Mode (Minimum Viable Input):**
- Per-character HP slider: Full / Above Half / Below Half / Critical / Down
- Party-wide DM assessment: Too Easy / Just Right / Too Hard / Near TPK
- One toggle: "Any character on Final Stand?"

**Detailed Mode (Optional, Improves Accuracy):**
- Per-character: exact HP, conditions, Final Stand toggle
- Per-character: spell slot estimate (Full / Most / Half / Few / Empty)
- Per-character: key feature availability (checkboxes for class-specific resources)
- Notes field for anything the DM wants to flag

The system works with Quick Mode alone. Detailed Mode refines the Director's adaptive calculations but is never required.

---

## Part 6: Economy and Progression

### 6.1 Dual Currency System

Two currencies prevent tension between in-run upgrades and meta-progression:

- **Gold (gp):** Earned in-run. Spent on Enhancements and Shop items. Persists between runs.
- **Astral Shards:** Earned from floor clears, run completions, and achievements. Spent on Gacha pulls. Not purchasable.

### 6.2 Gold Economy

**Per-Arena Payout:** The base payout follows a triangular progression: Arena N within a floor yields 5N gp per player. This means later arenas within a floor are worth more, rewarding the party for pushing deeper.

| Arena | Gold per Player (base) |
|---|---|
| 1 | 5 gp |
| 2 | 10 gp |
| 3 | 15 gp |
| 4 | 20 gp |
| 5 | 25 gp |

For a 4-player party across a full 4-floor run (3+4+4+5 = 16 arenas), total base gold earned = sum of 5+10+15+...+80 = 680 gp per player.

**Milestone Gold Bonuses:**

| Milestone | Bonus per Player |
|---|---|
| Clear Floor 1 | +50 gp |
| Clear Floor 2 | +100 gp |
| Clear Floor 3 | +200 gp |
| Clear Floor 4 | +400 gp |
| Full run completion | +150 gp |

A full 4-floor clear yields: 680 (base) + 750 (milestones) + 150 (completion) = **1,580 gp** per player.

A Floor 2 wipe (7 arenas cleared + Floor 1 milestone) yields: 140 (base) + 50 (Floor 1) = **190 gp** per player.

**Participation Floor:** To ensure failed runs feel like progress rather than waste, a flat **50 gp per arena cleared** is guaranteed regardless of milestone status. A Floor 2 wipe after 7 arenas thus guarantees at least 350 gp base. This compresses the full-clear-to-early-wipe ratio from 8:1 to approximately 4.5:1, which still strongly rewards full clears but softens early failure.

**Level Scaling:** Gold payouts scale with party level to maintain purchasing power as enhancement prices increase:

| Party Level | Gold Multiplier |
|---|---|
| 1-4 | x1 |
| 5-10 | x2 |
| 11-16 | x4 |
| 17-20 | x8 |

### 6.3 Enhancements

Enhancements are permanent upgrades purchased with gold in the Lobby. They persist across runs and represent the core meta-progression loop.

**Tier 1 Enhancements (75-100 gp, level-scaled):** Incremental stat buffs. Capped to prevent stacking beyond balance.
- +1 to a saving throw (max +2 total from enhancements)
- +5 max HP (max +15 total)
- +1 to a skill proficiency
- Additional cantrip known

**Tier 2 Enhancements (200-300 gp, level-scaled):** Tactical capabilities that change how a character plays.
- Bonus action Dash once per arena
- Resistance to one damage type (chosen at purchase)
- Extra 1st-level spell slot
- Advantage on initiative rolls

**Tier 3 Enhancements (500-800 gp, level-scaled):** Build-defining upgrades that create synergies with the Weakness Exploit system and class features.
- When you trigger a Weakness Exploit, you also gain temporary HP equal to your proficiency bonus
- Once per floor, reroll a failed saving throw
- Your first attack each arena deals an additional 1d6 damage of a type you choose
- When you are targeted by the Armillary, you may redirect the effect to a different ally or enemy within 30 feet

**Enhancement Caps:** Total enhancement power per character is capped by tier:

| Tier of Play | Max Enhancement Slots |
|---|---|
| Tier 1 (1-4) | 3 |
| Tier 2 (5-10) | 5 |
| Tier 3 (11-16) | 7 |
| Tier 4 (17-20) | 9 |

This prevents high-level characters with dozens of runs under their belt from becoming invincible. Slot count increases with tier, but the cap ensures encounters can still challenge them.

### 6.4 Between-Arena Rewards

After each arena (before the shop check), the party chooses 1 of 3 randomly generated rewards:

**Reward pool categories:**
- **Consumables:** Healing potions, spell scrolls, single-use items
- **Buffs:** Temporary bonuses lasting until the next short rest (e.g., +2 AC for next arena, resistance to fire)
- **Equipment:** Mundane or minor magical items
- **Favour:** +1 Armillary's Favour
- **Gold:** Bonus gold payout
- **Intel:** Preview of the next arena's encounter composition (see the Tactical Brief before committing)

Reward rarity scales with floor depth: Floor 1 rewards are mostly Common/Uncommon. Floor 4 rewards include Rare and Very Rare options.

### 6.5 Shops

Shops have a 30% chance of appearing between arenas (not after the final arena on a floor, since the floor transition handles rest and rewards). A shop offers 4-6 items for purchase with gold.

Shop inventory is generated from the reward pool with higher rarity items available. Prices follow the standard 5e magic item pricing guidelines, adjusted for the economy's scale.

---

## Part 7: The Gacha System

### 7.1 Design Philosophy

This is a non-monetized gacha. There is no real-money purchase path. The psychological hooks of gacha (anticipation, surprise, collection) are used to create excitement around meta-progression, not to extract money. Every pull must be meaningful: no dead pulls, no vendor trash.

### 7.2 Astral Shards (Gacha Currency)

| Source | Shards Earned |
|---|---|
| Clear a floor | 3 |
| Complete a full run | 10 bonus |
| Achievement (first time only) | 5 |
| Daily login (if applicable) | 1 |

**Cost per pull:** 5 Astral Shards. A full 4-floor run yields 12 (floors) + 10 (completion) = 22 Shards = 4 pulls with 2 leftover. Over 3 runs: ~13 pulls.

### 7.3 Three Banners

**Mirror of Selves (Character Banner):** Pulls grant alternate versions of existing party members. Each variant has:
- A new Origin (background/race combination)
- A modified class build (same class, different subclass or feature selection)
- A unique inherent item (bound to this variant)
- 1-2 pre-applied Enhancements

Variants are sidegrades, not upgrades. A variant Wizard might have Evocation features instead of Divination, with a staff that grants bonus fire damage. The player chooses which variant to bring into a run.

**Armillary Armoury (Weapon Banner):** Pulls grant weapons with randomized properties:
- Base weapon type (longsword, shortbow, staff, etc.)
- 1-3 magical properties (damage bonus, elemental damage type, on-hit effect)
- Rarity determines property count and strength

**Echoes of Fate (Identity Banner):** Pulls grant Identities: meta-level character modifications that combine:
- A passive ability (e.g., "Whenever you roll a natural 20, the Armillary's next effect is Beneficial")
- An activated ability (once per floor, e.g., "Force one enemy to reroll a successful saving throw")
- An epithet (cosmetic title, e.g., "the Unyielding," "Starforged")

### 7.4 Rarity and Pity

| Rarity | Pull Rate | Power Level |
|---|---|---|
| Common | 40% | Minor variant, +1 weapon, simple identity |
| Uncommon | 30% | Notable variant, +1 weapon with rider, useful identity |
| Rare | 20% | Significant variant with unique item, +2 weapon, strong identity |
| Very Rare | 8% | Powerful variant with build-enabling item, +2 weapon with major rider |
| Legendary | 2% | Transformative variant, +3 weapon, game-changing identity |

**Pity System:**
- Guaranteed Rare or better every 5 pulls
- Guaranteed Very Rare or better every 15 pulls
- Guaranteed Legendary every 40 pulls
- Soft pity starts at pull 30: Legendary rate increases by +2% per pull until triggered

**Duplicate Protection:** Pulling a duplicate converts it to Enhancement Materials (crafting components for Tier 2-3 Enhancements) or refunds partial Shards.

**Collection Bonuses:** At pull milestones (10, 25, 50, 100 total pulls), the player receives bonus rewards: guaranteed rarity upgrades, unique cosmetic epithets, or exclusive Enhancement recipes.

---

## Part 8: Party Scaling

### 8.1 Solo Play (1 Player)

Solo play requires significant adjustments to prevent the roguelike's attrition model from being instantly lethal:

- **NPC Companion:** The system generates an NPC companion using the same statblock template system as Echo generation (Part 9). The DM controls this companion. It has simplified decision-making (follows the behaviour profile system).
- **Rally Mechanic:** Replaces Final Stand. Once per arena, when the solo character drops to 0 HP, they can Rally: immediately regain HP equal to their level + Constitution modifier and take one action. If they drop again, standard death rules apply.
- **Armillary adjustment:** Beneficial weight increased to 30%, Hostile reduced to 30%.
- **Floor structure:** 3 arenas per floor maximum. 3 floors per run.
- **Encounter scaling:** Standard encounter multipliers apply (solo = multiplier shifts up one step), but the XP budget is further reduced by 20% to account for the NPC companion's lower effectiveness compared to a full player.

### 8.2 Small Party (2-3 Players)

- Encounter multipliers shifted up one step (a 2-creature encounter uses the 3-6 creature multiplier)
- Beneficial Armillary weight: 25%
- Floor structure: 3-4 arenas per floor
- Momentum System: recovery options increased to TWO per arena (THREE with Momentum Bonus)

### 8.3 Standard Party (3-5 Players)

Full rules as written. The system is optimized for this range.

### 8.4 Large Party (6+ Players)

- Encounter multipliers shifted down one step
- CR minimum increased by +1 across the board
- Minion rules recommended for encounters with 8+ creatures
- Hostile Armillary weight: 45%
- Floor structure: 4-5 arenas per floor, 4 floors per run
- Encounters gain additional creatures to maintain action economy pressure (a party of 6 fighting 3 monsters is not a challenge regardless of CR)

---

## Part 9: LLM Integration

### 9.1 Design Philosophy: Templates First, LLM Second

Pure LLM generation is unreliable for mechanical balance. An LLM asked to create a monster statblock will produce something that reads well but may be wildly over- or under-powered. The proven approach is a hybrid: deterministic templates for stats and mechanical balance, LLM for creativity, flavour, and contextual reasoning.

All LLM features degrade gracefully. If no API key is configured, the system falls back to template-only generation with generic flavour text. The core experience works without an LLM; the LLM makes it better.

### 9.2 Use Cases

**Echo Statblock Generation:** When the gacha's Mirror of Selves banner produces a character variant, the LLM customizes an NPC statblock template:
- Input: PC class, level, selected subclass variant, inherent item properties
- Template: NPC statblock with appropriate HP, AC, attack bonuses, and save DCs derived deterministically from level
- LLM contribution: 2-3 unique flavour abilities, a backstory paragraph, personality traits, and a visual description
- Validation: Rules engine checks that generated abilities do not exceed the power budget for the variant's rarity

**Magic Item Creation:** For the Armillary Armoury weapon banner:
- Input: Base weapon type, rarity, intended damage type
- Template: Stat bonuses and basic properties determined by rarity tier
- LLM contribution: Flavour name, lore description, and one creative rider effect constrained to the rarity's power budget
- Validation: Rider effect checked against a whitelist of acceptable mechanical effects per rarity

**Tactical Brief Enhancement:** The template-driven tactical brief (Part 5.3) produces functional but formulaic prose. The LLM can optionally rewrite it into more engaging DM-facing text while preserving the mechanical content.

**Armillary Narration:** The Armillary's effects are mechanically determined by the weighted table. The LLM provides dramatic narration: "The Armillary shudders and a crack of violet light splits the arena. A frost elemental claws its way through the rift, ice forming on the ground around it."

**Arena Descriptions:** Brief, evocative descriptions of the arena environment for the DM to read or paraphrase to players.

**Identity Banner Content:** Passive abilities, activated abilities, and epithets for the Echoes of Fate banner.

### 9.3 Pre-Generation Model

LLM calls are not made during live play. All LLM-generated content is pre-cached:

- At run start: generate arena descriptions, Armillary narration, and tactical brief enhancements for all arenas in the run
- On gacha pull: generate the variant/weapon/identity immediately, cache the result
- During downtime: the system can batch-generate content for future runs

This ensures zero latency during play and prevents API failures from disrupting a session.

### 9.4 Cost Estimate

Using Claude Haiku for most generation tasks and Sonnet for complex statblock validation:

| Task | Model | Calls/Session | Cost/Call | Total |
|---|---|---|---|---|
| Arena descriptions (16) | Haiku | 16 | $0.003 | $0.05 |
| Tactical brief rewrites (16) | Haiku | 16 | $0.003 | $0.05 |
| Armillary narration (80 rounds) | Haiku | 16 (batched) | $0.005 | $0.08 |
| Gacha content (4 pulls) | Sonnet | 4 | $0.027 | $0.11 |
| Echo statblock (if pulled) | Sonnet | 1 | $0.027 | $0.03 |
| Threat assessment (one-time) | Haiku | 317 | $0.005 | $1.59 |

**Per-session cost (excluding one-time setup): approximately $0.30-$0.50.** With prompt caching enabled, repeat patterns reduce this further.

### 9.5 Structured Output and Validation

All LLM outputs use structured JSON schemas with validation:

```
// Example: Magic Item Generation
{
  "name": string,           // max 40 chars
  "description": string,    // max 200 chars
  "base_weapon": enum,      // from valid weapon list
  "rarity": enum,           // must match requested rarity
  "bonus": int,             // constrained by rarity (+1/+2/+3)
  "damage_type": enum,      // from valid damage types
  "rider_effect": {
    "trigger": string,      // max 50 chars
    "effect": string,       // max 100 chars
    "uses_per": enum        // "hit" | "turn" | "rest" | "arena"
  }
}
```

A rules validation layer checks every generated item against mechanical constraints before it enters the game. If validation fails, the system retries with a tighter prompt or falls back to a template-only result.

---

## Part 10: Technical Architecture

### 10.1 Stack

- **Frontend:** React + Tailwind CSS. Single-page application optimized for tablet-sized screens (the DM's second screen). Responsive down to phone but primary target is 10"+ tablets and laptops.
- **Backend:** Node.js (Express) or Python (FastAPI). Handles encounter generation, economy calculations, gacha logic, and LLM orchestration.
- **Database:** SQLite for self-hosted single-DM deployments. PostgreSQL (via Supabase or similar) for hosted multi-user deployments.
- **LLM Integration:** Claude API (Haiku for bulk generation, Sonnet for complex tasks). Optional; system functions fully without it.
- **Monster Data:** Open5e API for initial data load, cached locally after first fetch.

### 10.2 Data Model (Core Entities)

```
Campaign {
  id, name, created_at,
  party_power_coefficient: float,
  total_runs: int,
  settings: JSON
}

Character {
  id, campaign_id, name, class, subclass, level,
  ac, max_hp, saves: JSON, damage_types: JSON,
  capabilities: JSON,
  enhancement_slots: Enhancement[],
  variant_id: nullable,
  identity_id: nullable,
  weapon_id: nullable
}

Run {
  id, campaign_id, started_at, ended_at,
  starting_level: int, floors_completed: int,
  total_gold_earned: int, total_shards_earned: int,
  difficulty_curve: JSON,
  outcome: "completed" | "failed" | "abandoned"
}

Floor {
  id, run_id, floor_number: int,
  arenas_completed: int,
  party_snapshots: JSON[]     // DM health snapshots per arena
}

Arena {
  id, floor_id, arena_number: int,
  encounter_composition: JSON,
  difficulty_target: float,
  actual_difficulty: string,   // DM assessment
  gold_earned: int,
  armillary_effects: JSON[],
  tactical_brief: text,
  map_id: string
}

Monster {
  id, name, source: string,
  cr: float, hp: int, ac: int,
  tactical_role: enum,
  mechanical_signature: JSON,
  behaviour_profile: JSON,
  statblock: JSON
}

Enhancement {
  id, name, tier: int, cost: int,
  effect: JSON,
  power_rating: float
}

GachaPull {
  id, campaign_id, character_id,
  banner: enum, rarity: enum,
  result: JSON,
  pull_number: int,        // for pity tracking
  timestamp
}
```

### 10.3 Deployment Options

**Self-Hosted (Recommended for Privacy):**
- Docker container with SQLite
- Single command: `docker run -p 3000:3000 drifting-infinity`
- No external dependencies except optional Claude API key
- All data stays on the DM's machine

**Hosted (Convenience):**
- Vercel (frontend) + Railway or Fly.io (backend) + Supabase (database)
- User accounts with campaign data sync
- LLM features handled server-side with shared API key (cost managed via rate limiting)

**Hybrid (Best of Both):**
- Frontend served from CDN
- Backend runs locally via Electron or Tauri wrapper
- Data stored locally, LLM calls proxied through a cloud endpoint

### 10.4 Offline Capability

The core experience (encounter generation, combat management, economy, dice rolling) works entirely offline. LLM features require connectivity but are pre-cached at run start. If connectivity drops mid-session, the system falls back to template-only content with no interruption to play.

---

## Part 11: Development Roadmap

### Phase 1: MVP (Core Engine)

**Goal:** A usable DM second screen for running roguelike D&D combat sessions.

**Deliverables:**
- Character entry form (manual input, save/load)
- Encounter generation algorithm (XP budget + CR constraints + basic role assignment)
- Basic Armillary (weighted random effects, no budget cap yet)
- Initiative tracker with HP bars
- Active creature action panel (abbreviated statblock view)
- One-tap damage rolling
- Gold economy (per-arena payout + milestone bonuses)
- Death and Final Stand tracking
- Momentum System (between-arena recovery)
- DM Health Snapshot (Quick Mode only)
- Basic difficulty curve visualization
- 5-10 pre-built encounter maps (descriptions only, no visual maps)

**Not included in MVP:** Gacha, LLM integration, tactical briefs, Weakness Exploit tracker, shops, enhancements, adaptive difficulty, Party Power Coefficient.

### Phase 2: The Director

**Goal:** Adaptive difficulty and encounter intelligence.

**Deliverables:**
- Full DM Health Snapshot (Quick + Detailed modes)
- Adaptive difficulty target computation
- Intensity curve pacing (build-up/peak/resolution)
- Party Power Coefficient (historical data tracking)
- Mechanical Signature tagging for SRD creatures (automated pipeline)
- Hard constraints and combo interaction checking
- Tactical brief generation (template-based)
- Encounter composition templates (Hold and Flank, Focus Fire, etc.)
- Weakness Exploit tracker UI
- Armillary Budget Cap
- Context-sensitive Armillary weight adjustment

### Phase 3: Progression

**Goal:** Between-run meta-progression that makes every session matter.

**Deliverables:**
- Enhancement system (Tiers 1-3, purchase with gold)
- Gacha system (all three banners, pity tracking, duplicate protection)
- Astral Shard economy
- Shop system (between-arena, gold-based)
- Between-arena reward selection (pick 1 of 3)
- Collection bonuses
- Run statistics and Archive
- Difficulty curve comparison across runs

### Phase 4: LLM Integration

**Goal:** AI-enhanced content that makes every run feel unique.

**Deliverables:**
- Claude API integration (Haiku + Sonnet)
- Echo statblock generation (character variants)
- Magic item generation (weapon banner)
- Identity generation (identity banner)
- Tactical brief enhancement (LLM rewrite of template briefs)
- Armillary narration
- Arena descriptions
- Pre-generation caching system
- LLM threat assessment pipeline (Phase 2 of creature tagging)
- Structured output validation layer

### Phase 5: Polish and Community

**Goal:** Production quality and community content.

**Deliverables:**
- Extended monster database (Open5e 3,200+ creatures, community-tagged)
- Community encounter template sharing
- Custom monster entry form with automated tagging
- Map library (community-contributed encounter maps with tagged terrain)
- Mobile-responsive interface optimization
- Campaign import/export
- Seasonal reset options (fresh meta-progression for groups wanting a new start)
- Accessibility features (screen reader support, colour-blind mode, font scaling)
- Localization framework

---

## Part 12: Open Questions for Playtesting

1. Does the Momentum System adequately equalise attrition across class types, or do long-rest casters still feel significantly disadvantaged by Floor 3?

2. Is the Armillary Budget Cap (20% of encounter XP) the right threshold, or does it feel too restrictive or too permissive?

3. Do the combo interaction multipliers produce the right "feels harder but fair" experience, or do they over-correct?

4. Is the milestone gold bonus structure motivating? Does the 4.5:1 ratio between full clears and early wipes feel fair for failed runs?

5. How often does the DM need to override the encounter generator's selections? If overrides are frequent, the constraint system needs tightening. If rare, the system is working.

6. Does the Weakness Exploit system remain engaging across a full 4-floor run, or does it become routine? If routine, consider introducing Exploit-immune creatures on later floors.

7. Are the tactical briefs useful in practice, or does the DM ignore them? Both answers are acceptable; the latter just means the brief is a nice-to-have.

8. How accurate is the DM's subjective difficulty assessment as a signal for adaptive difficulty? Does Quick Mode provide enough data, or is Detailed Mode necessary for good pacing?

9. Does the Party Power Coefficient converge to a useful value within 3-5 runs, or does it need more data?

10. At Tier 3-4, does the enhancement cap system prevent trivialization, or do high-level characters still steamroll encounters regardless?

11. For solo play, is the Rally mechanic engaging, or does it feel like a safety net that removes tension?

12. Does the pre-generation caching model for LLM content feel seamless, or do players notice when content was pre-generated versus live?

13. How long does the DM Health Snapshot actually take in practice? If it consistently exceeds 60 seconds, the Quick Mode interface needs simplification.

14. Does the Mana Drain redesign (temporary suppression) still create meaningful tactical pressure, or has it been defanged too much?

---

## Appendix A: Glossary

| Term | Definition |
|---|---|
| Arena | A single combat encounter on a single map |
| Armillary | The Fate Spinning Armillary; a persistent entity that generates random effects each combat round |
| Armillary's Favour | Reroll currency earned per floor cleared |
| Astral Shards | Meta-progression currency for gacha pulls |
| Director | The adaptive difficulty system that manages encounter pacing across a floor |
| Echo | A character variant generated via the Mirror of Selves gacha banner |
| Enhancement | A permanent stat upgrade purchased with gold |
| Final Stand | Condition applied after a character is revived in an arena; next drop to 0 HP is instant death |
| Floor | A sequence of 3-5 arenas with no full rests between them |
| Identity | A meta-level character modification from the Echoes of Fate gacha banner |
| Lobby | The persistent hub between runs |
| Mechanical Signature | A structured threat assessment of a creature beyond its CR |
| Momentum Bonus | Enhanced recovery granted when the party clears an arena without anyone dropping to 0 HP |
| Momentum System | Partial recovery between arenas within a floor |
| Party Power Coefficient | A multiplicative adjustment learned from historical DM assessments |
| Run | A single expedition through 3-4 floors |
| Tactical Brief | A 2-3 sentence encounter plan generated from creature behaviour profiles |
| Weakness Exploit | The signature mechanic: hitting a weakness grants an ally a bonus Reaction |

## Appendix B: Reference Implementations

**Monte Carlo Combat Simulators (for validation):**
- github.com/andrei-gorbatch/monte_carlo (Python, D&D 5e, web app)
- github.com/DanielK314/DnDSimulator (Python, includes DM mode)
- github.com/matteoferla/DnD-battler (Python, statistical analysis)
- github.com/lemonade512/combatsim (Python, grid-based tactics)

These simulators can be used during development to validate that the encounter generation algorithm produces encounters with appropriate win rates (target: 85-95% party victory rate for Moderate, 70-85% for Hard, 50-70% for Extreme).

**Dynamic Difficulty Precedents:**
- Left 4 Dead AI Director: build-up/peak/relax state machine, intensity tracking, dynamic spawning
- Resident Evil 4 difficulty rank: internal counter adjusted by player performance metrics
- Slay the Spire: act-based difficulty scaling with elite/boss gates

**Encounter Balancing References:**
- Sly Flourish Lazy Encounter Benchmark (CC-BY-4.0): total CR vs. character level sum as quick deadliness gauge
- 2014 DMG encounter multipliers: action economy adjustment for multiple creatures
- 2024 DMG three-tier difficulty: Low/Moderate/High XP thresholds per character level

**Monster Data Sources:**
- SRD 5.2 (CC-BY-4.0): 317 creatures, full statblocks
- 5e-database (github.com/5e-bits/5e-database): structured JSON
- Open5e API (open5e.com): 3,200+ creatures from OGL/CC sources

---

*Drifting Infinity GDD v0.2 | February 2026 | This document merges and supersedes GDD v0.1 and the Design Companion Document.*
