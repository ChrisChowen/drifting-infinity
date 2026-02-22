# Drifting Infinity

A DM companion tool for D&D 5e (2024 rules) roguelike combat arenas. Runs as a "second screen" alongside your VTT, handling procedural encounter generation, adaptive difficulty, economy tracking, reward distribution, meta-progression, and live combat management.

## The Game

A party enters the **Armillary** — a shifting extradimensional arena. Each run consists of escalating floors (up to 20) of combat encounters, punctuated by reward choices, shops, social encounters, and rest decisions. Between runs, players spend currency on permanent upgrades and pull from gacha-style banners. Death is a setback, not the end.

## Features

### Encounter Generation
- Multi-step procedural pipeline: XP budget, environment selection, template matching, candidate scoring, creature selection, constraint validation
- ~1,850 monsters from Open5e (SRD + Kobold Press)
- Themed encounters, floor biomes, and stackable floor affixes
- Arena objectives (extermination, survival, tactical)

### Adaptive Difficulty
- L4D AI Director-inspired intensity curve (buildup/peak/resolution)
- Party Power Coefficient (PPC) historical tracking
- Scales for 1-6+ players, levels 1-20

### Combat Systems
- Weakness exploit chains ("One More" system)
- Momentum recovery between arenas
- Final Stand death mechanics
- Armillary dynamic event system (per-round combat modifiers)

### Progression
- **Economy:** Gold (triangular scaling), Astral Shards, shop system
- **Gacha:** Three banners (Mirror of Selves, Armillary Armoury, Echoes of Fate) with pity counters
- **Meta-progression:** Essence currency, talent tree (3 branches, 5 tiers each), achievement tracking
- **Story:** 5-act narrative across 20 floors featuring Aethon, The Architect

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy (async), SQLite, Pydantic
**Frontend:** React 19, TypeScript, Vite, React Router v7, Tailwind CSS
**Data:** Open5e API integration (~1,850 monsters, SRD spells & magic items)

## Getting Started

### Backend

```bash
cd backend
pip install -e ".[dev]"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

On first run, the backend auto-creates DB tables and ingests monster data from Open5e.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server (port 5173) proxies `/api` requests to the backend.

## Architecture

```
backend/app/
├── routers/        # 18 FastAPI routers (campaigns, combat, gacha, etc.)
├── services/       # 11 business logic orchestrators
├── engine/
│   ├── encounter/  # 14-file encounter generation pipeline
│   ├── difficulty/ # Adaptive difficulty director
│   ├── combat/     # Weakness chains, momentum, Final Stand
│   ├── armillary/  # Dynamic per-round combat events
│   ├── gacha/      # Banner system with pity counters
│   ├── economy/    # Gold, shards, shop system
│   └── meta/       # Talent tree, achievements, lives
├── models/         # 13 SQLAlchemy ORM models
├── schemas/        # Pydantic request/response schemas
└── data/           # Game data definitions + Open5e ingestion

frontend/src/
├── pages/          # 20 page components (welcome, hub, run flow)
├── components/     # 50+ reusable components
├── hooks/          # Custom React hooks
└── lib/            # API client, utilities
```

## Status

Phase 3 complete. Phase 4 (LLM integration for narrative generation) is next.
