"""HTTP client for Open5e API with retry and pagination."""

import asyncio
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class Open5eClient:
    """Client for fetching monster data from the Open5e API."""

    def __init__(self):
        self.base_url = settings.open5e_base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        await self.client.aclose()

    async def _get_with_retry(self, url: str, max_retries: int = 3) -> dict:
        """Fetch a URL with exponential backoff retry."""
        for attempt in range(max_retries):
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPStatusError, httpx.ConnectError) as e:
                if attempt == max_retries - 1:
                    raise
                wait = 2 ** attempt
                logger.warning(f"Open5e request failed (attempt {attempt + 1}): {e}. Retrying in {wait}s")
                await asyncio.sleep(wait)
        raise RuntimeError("Unreachable")

    # Document slugs to fetch monsters from (in priority order)
    MONSTER_DOCUMENT_SLUGS: list[str] = [
        "wotc-srd",  # Core SRD (~322 monsters)
        "o5e",       # Open5e community content
        "tob",       # Tome of Beasts
        "cc",        # Creature Codex
        "tob2",      # Tome of Beasts 2
        "tob3",      # Tome of Beasts 3
        "a5e",       # Level Up: Advanced 5th Edition
        "menagerie", # Monster Menagerie
    ]

    # Curated high-quality sources: SRD + Kobold Press books
    CURATED_DOCUMENT_SLUGS: list[str] = [
        "wotc-srd",  # Core SRD (~322 monsters)
        "tob",       # Tome of Beasts (~391 monsters)
        "cc",        # Creature Codex (~356 monsters)
        "tob2",      # Tome of Beasts 2 (~383 monsters)
        "tob3",      # Tome of Beasts 3 (~397 monsters)
    ]

    async def fetch_srd_monsters(self) -> list[dict]:
        """Fetch all SRD 5.2 monsters from Open5e API."""
        all_monsters: list[dict] = []
        url = f"{self.base_url}/monsters/?document__slug=wotc-srd&limit=50"

        while url:
            logger.info(f"Fetching monsters: {url}")
            data = await self._get_with_retry(url)
            results = data.get("results", [])
            all_monsters.extend(results)
            url = data.get("next")
            logger.info(f"  Got {len(results)} monsters (total: {len(all_monsters)})")

        logger.info(f"Fetched {len(all_monsters)} SRD monsters total")
        return all_monsters

    async def fetch_curated_monsters(self) -> list[dict]:
        """Fetch monsters from curated high-quality sources (SRD + Kobold Press).

        Same dedup pattern as fetch_all_available_monsters but restricted
        to CURATED_DOCUMENT_SLUGS for quality control.
        """
        all_monsters: list[dict] = []
        seen_slugs: set[str] = set()

        for doc_slug in self.CURATED_DOCUMENT_SLUGS:
            try:
                monsters = await self._fetch_monsters_by_slug(doc_slug)
                new_count = 0
                for m in monsters:
                    m_slug = m.get("slug", "")
                    if m_slug and m_slug not in seen_slugs:
                        seen_slugs.add(m_slug)
                        m["_source_document"] = doc_slug
                        all_monsters.append(m)
                        new_count += 1
                logger.info(
                    f"Fetched {new_count} new monsters from '{doc_slug}' "
                    f"(total: {len(all_monsters)})"
                )
            except Exception as e:
                logger.warning(f"Could not fetch from '{doc_slug}': {e}")
                continue

        logger.info(
            f"Fetched {len(all_monsters)} curated monsters from "
            f"{len(self.CURATED_DOCUMENT_SLUGS)} sources"
        )
        return all_monsters

    async def fetch_all_available_monsters(self) -> list[dict]:
        """Fetch monsters from all available document sources.

        Tries each document slug and skips any that return errors
        (indicating the source isn't available on this API instance).
        """
        all_monsters: list[dict] = []
        seen_slugs: set[str] = set()

        for doc_slug in self.MONSTER_DOCUMENT_SLUGS:
            try:
                monsters = await self._fetch_monsters_by_slug(doc_slug)
                # Deduplicate by monster slug
                new_count = 0
                for m in monsters:
                    m_slug = m.get("slug", "")
                    if m_slug and m_slug not in seen_slugs:
                        seen_slugs.add(m_slug)
                        m["_source_document"] = doc_slug
                        all_monsters.append(m)
                        new_count += 1
                logger.info(f"Fetched {new_count} new monsters from '{doc_slug}' (total: {len(all_monsters)})")
            except Exception as e:
                logger.warning(f"Could not fetch monsters from '{doc_slug}': {e}")
                continue

        logger.info(f"Fetched {len(all_monsters)} total monsters from all sources")
        return all_monsters

    async def _fetch_monsters_by_slug(self, doc_slug: str) -> list[dict]:
        """Fetch all monsters for a specific document slug."""
        monsters: list[dict] = []
        url = f"{self.base_url}/monsters/?document__slug={doc_slug}&limit=50"

        while url:
            data = await self._get_with_retry(url)
            results = data.get("results", [])
            monsters.extend(results)
            url = data.get("next")

        return monsters

    async def fetch_available_document_slugs(self) -> list[str]:
        """Discover which document slugs are available on the API."""
        available: list[str] = []
        for doc_slug in self.MONSTER_DOCUMENT_SLUGS:
            try:
                url = f"{self.base_url}/monsters/?document__slug={doc_slug}&limit=1"
                data = await self._get_with_retry(url)
                if data.get("count", 0) > 0:
                    available.append(doc_slug)
            except Exception:
                continue
        return available

    async def fetch_srd_magic_items(self) -> list[dict]:
        """Fetch all SRD 5.2 magic items from Open5e API."""
        all_items: list[dict] = []
        url = f"{self.base_url}/magicitems/?document__slug=wotc-srd&limit=50"

        while url:
            logger.info(f"Fetching magic items: {url}")
            data = await self._get_with_retry(url)
            results = data.get("results", [])
            all_items.extend(results)
            url = data.get("next")
            logger.info(f"  Got {len(results)} magic items (total: {len(all_items)})")

        logger.info(f"Fetched {len(all_items)} SRD magic items total")
        return all_items

    async def fetch_srd_spells(self) -> list[dict]:
        """Fetch all SRD 5.2 spells from Open5e API."""
        all_spells: list[dict] = []
        url = f"{self.base_url}/spells/?document__slug=wotc-srd&limit=50"

        while url:
            logger.info(f"Fetching spells: {url}")
            data = await self._get_with_retry(url)
            results = data.get("results", [])
            all_spells.extend(results)
            url = data.get("next")
            logger.info(f"  Got {len(results)} spells (total: {len(all_spells)})")

        logger.info(f"Fetched {len(all_spells)} SRD spells total")
        return all_spells

    async def fetch_monster_by_slug(self, slug: str) -> dict:
        """Fetch a single monster by slug."""
        url = f"{self.base_url}/monsters/{slug}/"
        return await self._get_with_retry(url)
