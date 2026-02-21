# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Drifting Infinity is a standalone web application that serves as a **DM companion tool** for D&D 5e (2024 rules) roguelike combat arenas. It runs as a "second screen" alongside a DM's existing VTT, handling procedural encounter generation, adaptive difficulty scaling, economy tracking, reward distribution, meta-progression, and live combat management. The DM still runs the table, narrates, rolls for monsters, and adjudicates; the app is the encounter architect and bookkeeper.

**Core experience:** A party enters the Armillary, a shifting extradimensional arena. Each run consists of escalating floors (up to 20) of combat encounters, punctuated by reward choices, shops, social encounters, and rest decisions. Between runs, players spend currency on permanent upgrades and pull from gacha-style banners. Death is a setback, not the end — every run advances meta-progression.

**Design principles:** RAW 5e 2024 combat with a custom rules layer on top. Tier 0 integration (DM screen, not a VTT). Optimized for 3-5 players, scales from solo to 6+. Supports levels 1-20. The full game design document lives at `drifting-infinity-gdd-v02.md` in the project root.

## Commands

### Backend (Python/FastAPI)

```bash
# Install dependencies (from backend/)
pip install -e ".[dev]"

# Run dev server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Lint & format
ruff check backend/app
ruff format backend/app

# Run tests
pytest
pytest backend/tests/test_specific.py -k "test_name"

# Run encounter generation test suite
python backend/scripts/encounter_test_runner.py

# Run full simulation (single run, 20 floors)
python backend/scripts/full_run_simulation.py

# Run multi-run stress test
python backend/scripts/multi_run_simulation.py
```

### Frontend (React/TypeScript)

```bash
# Install dependencies (from frontend/)
npm install

# Run dev server (port 5173, proxies /api → localhost:8000)
npm run dev

# Type-check and build
npm run build
```

### Running Both

Start the backend first (it auto-creates DB tables and ingests monster data from Open5e on first run), then start the frontend. The Vite dev server proxies `/api` requests to the backend at `localhost:8000`.

## Architecture

### Backend: `backend/app/`

Layered architecture: **Routers → Services → Engine → Models/Data**

- **`routers/`** — 18 FastAPI routers, all mounted under `/api` prefix. Covers campaigns, characters, monsters, runs, floors, arenas, encounters, combat, armillary, economy, enhancements, gacha, rewards, archive, snapshots, magic items, meta-progression, and LLM
- **`services/`** — 11 business logic orchestrators between routers and engine. Key services: `encounter_service`, `combat_service`, `difficulty_service`, `gacha_service`, `armillary_service`, `economy_service`, `reward_service`, `shop_service`, `enhancement_service`, `archive_service`, `llm_service` (Phase 4, stubbed)
- **`engine/`** — Core game logic, the heart of the system:
  - **`encounter/`** (14 files) — Multi-step encounter generation pipeline. `pipeline.py` orchestrates: XP budget → environment selection → template selection → candidate pool building → scoring → greedy creature selection → constraints → combo interaction checks → party validation → sanity checks → tactical brief → objective assignment. Supports encounter themes, floor biomes, affix-modified stats, and danger ratings
  - **`difficulty/`** (7 files) — Adaptive difficulty director (L4D AI Director-inspired). Intensity curve state machine (buildup/peak/resolution), Party Power Coefficient (PPC) historical tracking, party strength assessment, target difficulty computation, floor affix cost adjustments, tier-specific parameters
  - **`combat/`** (7 files) — Weakness exploit chains ("One More" system), momentum recovery between arenas, Final Stand death mechanics, initiative tracking, damage calculation with resistance/vulnerability, respawn logic, rest mechanics
  - **`armillary/`** (4 files) — Dynamic per-round combat event system. Weighted effect roller, context-sensitive weight adjustment (based on party HP/conditions/resources), budget tracking (20% of encounter XP cap), effect scaling by floor
  - **`gacha/`** (5 files) — Three banners (Mirror of Selves, Armillary Armoury, Echoes of Fate), pity counters, duplicate protection, collection bonuses
  - **`economy/`** (3 files) — Gold payouts (per-arena triangular scaling + milestone bonuses + level multipliers), Astral Shard calculations, shop system
  - **`meta/`** (5 files) — Meta-progression: Essence currency, talent tree (Armillary Attunement — resilience/insight/fortune branches, 5 tiers each), achievement tracking, lives/death/scar system (3-5 lives per run, TPK handling, Phoenix Protocol), run reset logic
  - **`dice.py`** — Dice rolling utilities
  - **`leveling.py`** — XP-based character leveling tuned for roguelike pace (~1 level per floor, level 20 by floor 18-20)
  - **`scaling.py`** — Tier classification, party size categories, damage scaling
- **`models/`** — 13 SQLAlchemy async ORM models: Campaign, CampaignMeta, Character, Run, Floor, Arena, Monster, Spell, MagicItem, Inventory, Economy, Gacha, Snapshot. `Base` lives in `database.py`
- **`schemas/`** — Pydantic request/response schemas organized by domain (arena, campaign, character, combat, economy, floor, meta, run, snapshot)
- **`data/`** — Static game data definitions and ingestion scripts:
  - **Ingestion:** `open5e_client.py` (HTTP client with retry/pagination), `monster_ingest.py`, `magic_item_ingest.py`, `spell_ingest.py`. Curated sources: SRD + Kobold Press (Tome of Beasts 1-3, Creature Codex) = ~1,850 monsters
  - **Game data:** `environments.py` (arena environments with biome tags), `encounter_themes.py` (themed creature groupings), `arena_objectives.py` (win/fail condition sets: extermination, survival, tactical objectives), `floor_affixes.py` (stackable floor modifiers: creature buffs, environment hazards, armillary tweaks, economy changes), `enhancement_definitions.py` (Tier 1-3 permanent upgrades), `feat_definitions.py`, `reward_pool.py`, `behaviour_profiles.py` (tactical AI per creature role), `role_classifier.py` (Brute/Soldier/Artillery/Controller/Skirmisher/Lurker assignment), `armillary_effects_data.py`, `signature_builder.py` (mechanical signature construction)
  - **Narrative:** `lore_beats.py` (5-act story across 20 floors featuring Aethon, The Architect), `lore_fragments.py` (collectible lore text), `social_encounters.py` (skill-check-based non-combat arenas), `secret_events.py` (rare events: treasure rooms, ghost replays, bonus bosses), `antagonist.py` (Aethon dialogue pools by context)
  - **Reference tables:** `encounter_multipliers.py`, `cr_averages.py`, `xp_thresholds.py`

**Database:** SQLite via async SQLAlchemy + aiosqlite. Stored at `backend/data/drifting_infinity.db`. Tables are auto-created on startup. On first run, curated monsters (~1,850), SRD spells, and SRD magic items are fetched from the Open5e API and ingested.

**Config:** `app/config.py` uses pydantic-settings. Reads from `.env` file. Key settings: `database_url`, `open5e_base_url`, `anthropic_api_key` (for Phase 4 LLM features), `llm_enabled`, `cors_origins`.

### Frontend: `frontend/src/`

React 19 SPA with React Router v7, three layout modes.

- **`pages/`** — 20 page components across three flows:
  - **Welcome:** `/welcome` (fullscreen, no chrome)
  - **Hub/Lobby:** `/` (dashboard), `/campaign/new`, `/party`, `/party/add`, `/forge` (enhancements), `/gacha`, `/attunement`, `/chronicles` (lore), `/archive` (run history), `/settings`
  - **Run flow:** `/run/setup` → `/run/encounter` (brief) → `/run/combat` → `/run/summary` → `/run/rewards` → `/run/shop` → `/run/floor-transition` → `/run/complete`
- **`components/`** — 50+ reusable components organized by subsystem:
  - `ui/` (15 base primitives: Button, Card, Badge, Input, Select, Toast, Tooltip, Modal, ConfirmModal, ProgressBar, PageHeader, LoadingState, EmptyState, NumberStepper, RarityFrame, InsightTooltip, ArmillarySpinner)
  - `combat/` (11 files: CombatLog, DamageNumber, DmNotes, ArmillaryOrb, ArmillaryTurnBanner, ArmillaryRollAnimation, DeathAnnouncement, FinalStandBanner, HotkeyOverlay)
  - `encounter/` (encounter briefing components)
  - `gacha/` (PullSequence animation)
  - `layout/` (8 files: AppShell, HubLayout, RunLayout, FullscreenLayout, RunProgressRail, RunStatusBar, TopBar, Sidebar, SettingsDrawer)
  - `effects/` (ParticleCanvas, ScreenFlash, particlePresets)
  - `transitions/` (FloorDescent, TypewriterText)
  - `charts/` (IntensityCurve visualization)
  - `ErrorBoundary`, `StatBlockPanel`
- **`stores/`** — 6 Zustand stores:
  - `useCampaignStore` — Campaign/character selection, creation, loading
  - `useCombatStore` — Live combat state (initiative, HP, conditions, damage, healing, undo history)
  - `useRunStore` — Run/floor/arena progression, phase management, encounter generation, lives tracking
  - `useEconomyStore` — Gold/shards/enhancements
  - `useMetaStore` — Meta-progression (talents, essence, achievements, lore, lore beats, run-end meta)
  - `useToastStore` — Toast notifications
- **`api/`** — 8+ REST client modules. `client.ts` provides typed `api.get/post/put/patch/delete` helpers. Modules: campaigns, characters, encounters, combat, economy, meta, runs, snapshots, llm
- **`types/`** — 9 TypeScript definition files (character, combat, creature, armillary, encounter, gacha, economy, run, index)
- **`constants/`** — Game constants (damageTypes, conditions, tacticalRoles, classDefaults, campaignSettings, lore)
- **`lib/`** — Utilities (rarity colors, environment themes, Framer Motion animation helpers, session export)
- **`hooks/`** — Custom hooks (useConfirm, useHotkeys, useLlm)
- **`styles/`** — Global CSS + Tailwind CSS v4 configuration
- **`assets/`** — Icons and images

**State management pattern:** Zustand for client-persistent state (localStorage), TanStack Query for server-synced state.

**Path aliases:** `@/*`, `@components/*`, `@stores/*`, `@hooks/*`, `@lib/*`, `@api/*`, `@constants/*` (configured in both `tsconfig.json` and `vite.config.ts`).

## Key Game Systems

These are the unique mechanics that distinguish Drifting Infinity from standard 5e. Understanding them is critical when working on the codebase.

### Weakness Exploit ("One More" System)
The signature mechanic. When a player hits a creature's vulnerability or forces a failed save on a weak ability, they grant an ally a bonus Reaction (attack, cantrip, move, or Help). Chains can continue until no new exploit triggers or every ally has been granted a reaction this round. Encounter generation enforces that every encounter includes at least one exploitable weakness.

### Armillary (Fate Spinning Armillary)
Activates at initiative count 0 each round with a random effect from a weighted table: Hostile (40% base), Neutral (30%), Beneficial (20%), Chaos (10%). Weights dynamically adjust based on party state (HP, deaths, resources). Budget cap = 20% of encounter XP. Floor depth increases hostile weight.

### Adaptive Difficulty Director
L4D-inspired intensity curve: buildup → peak → resolution across each floor. DM health snapshots between arenas feed the Director's adaptive target computation. Party Power Coefficient (PPC) silently adjusts XP budgets based on historical DM assessments. DM subjective assessment is the strongest signal.

### Lives System
Runs start with 3 lives (up to 5 with meta-talents). Character deaths spend lives and generate narrative scars. Zero lives = permanent death for the run. TPK = run over (unless Phoenix Protocol meta-talent is unlocked). Characters resurrect at floor clear.

### Momentum System
Between-arena partial recovery: each character recovers ONE resource (spell slot ≤3rd, short-rest feature, HP from hit die, or condition removal). Clean arena clear = TWO recoveries + access to long-rest features. Equalizes attrition across class types.

### Meta-Progression
- **Enhancements:** Permanent stat upgrades (3 tiers, purchased with gold, slot-capped by tier of play)
- **Gacha:** Three non-monetized banners (character variants, weapons, identities) using Astral Shards. Pity system: guaranteed Rare every 5 pulls, Very Rare every 15, Legendary every 40
- **Talent Tree:** Armillary Attunement — 3 branches (resilience/insight/fortune) of 5 tiers each, purchased with Essence. Expands options and resilience, never raw combat power
- **Leveling:** XP-based, tuned for ~1 level per floor, reaching level 20 by floor 18-20

### Narrative System
5-act story across 20 floors featuring Aethon, The Architect (a cosmic scientist entity who built the Armillary). Lore beats fire at specific floors/conditions. Social encounters replace combat arenas (~40% chance on early floor arenas). Secret events (treasure rooms, ghost replays, bonus bosses) add surprises. Lore fragments are collectible.

## GDD Development Phases

The GDD outlines 5 development phases. The current implementation covers:

- **Phase 1 (MVP Core Engine):** Fully implemented — character entry, encounter generation pipeline, basic Armillary, initiative tracker with HP bars, one-tap damage rolling, gold economy, death/Final Stand tracking, momentum system, DM health snapshot, difficulty curve visualization
- **Phase 2 (The Director):** Fully implemented — adaptive difficulty, intensity curves, PPC tracking, mechanical signature tagging (automated pipeline), hard constraints, combo interactions, tactical briefs, encounter composition templates, Armillary budget cap, context-sensitive weight adjustment
- **Phase 3 (Progression):** Fully implemented — enhancements (Tiers 1-3), gacha (all three banners with pity/duplicate protection), Astral Shards, shops, between-arena rewards, collection bonuses, archive, lives system, talent tree, leveling
- **Phase 4 (LLM Integration):** Stubbed — router/service/hook exist but `llm_enabled` defaults to false. Anthropic API key configurable. Intended for: tactical brief enhancement, Armillary narration, arena descriptions, gacha content generation, threat assessment
- **Phase 5 (Polish):** Not yet started

**Beyond the GDD:** The implementation has expanded significantly beyond the original GDD spec, adding: floor affixes (stackable modifiers), arena objectives (varied win conditions), social encounters (skill-check alternatives to combat), narrative/lore system (5-act story, lore fragments, antagonist dialogue), secret events, encounter themes, floor biome system, 20-floor extended runs (GDD specifies 3-4), character leveling 1-20, curated monster pool from Kobold Press (~1,850 total vs 317 SRD)

## Key Conventions

- **Backend IDs:** Generated with `python-ulid` (string ULIDs, not UUIDs)
- **Backend line length:** 100 characters (Ruff config)
- **Backend Python version:** 3.12+ (type union syntax `X | Y` used throughout)
- **Frontend TypeScript:** Strict mode with `noUnusedLocals`, `noUnusedParameters`, `noUncheckedIndexedAccess`
- **Frontend build target:** ES2022
- **API pattern:** All backend endpoints prefixed with `/api`. Frontend proxies `/api` to `localhost:8000` in dev
- **DB sessions:** Use `get_db` dependency injection in routers. Auto-commits on success, auto-rollbacks on exception
- **Frontend state:** Zustand stores for persistent client state (localStorage). TanStack Query for server-synced data (5-minute stale time, 1 retry)
- **Layouts:** Three distinct layout modes — FullscreenLayout (welcome), HubLayout (lobby/meta with sidebar), RunLayout (in-run with progress rail + status bar)
- **Error handling:** ErrorBoundary at React root, Toast notifications for user-facing errors
- **Animations:** Framer Motion for transitions, custom ParticleCanvas for effects

## Dependencies

### Backend (Python)
- FastAPI 0.115+, Uvicorn — Web framework and ASGI server
- SQLAlchemy 2.0+ (async), aiosqlite — ORM + SQLite async driver
- Pydantic 2.10+, pydantic-settings — Validation and config
- python-ulid — ID generation
- httpx — Async HTTP client (Open5e API)
- Alembic — Database migrations (configured but not actively used)

### Frontend (Node.js)
- React 19, React Router v7 — UI framework and routing
- TypeScript 5.9 — Type safety
- Zustand 5 — State management
- TanStack React Query 5 — Server state
- Tailwind CSS 4 (@tailwindcss/vite plugin) — Styling
- Framer Motion 12 — Animations
- Recharts 3.7 — Data visualization (intensity curves, stats)
- Lucide React — Icons
- @dnd-kit — Drag-and-drop (party management, initiative ordering)
- Zod 4 — Schema validation
- date-fns — Date formatting
- Vite 7.3 (React SWC plugin) — Build tool

## Simulation & Testing

The `backend/scripts/` directory contains simulation tools and their reports:
- `encounter_test_runner.py` — Tests encounter generation across tiers, party sizes, and difficulty levels
- `full_run_simulation.py` — Simulates a complete 20-floor run with leveling, economy, gacha, and TPK handling
- `multi_run_simulation.py` — Stress-tests multiple consecutive runs
- `seed_demo_data.py` — Seeds the database with demo campaigns and characters
- Reports (`*.md`) document simulation results including floor-by-floor breakdowns, encounter compositions, economy totals, death counts, and PPC tracking
