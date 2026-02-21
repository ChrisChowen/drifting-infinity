"""Integration tests for campaign and character CRUD endpoints."""

import pytest
import pytest_asyncio


@pytest.mark.asyncio
class TestCampaignCRUD:
    async def test_create_campaign(self, client):
        resp = await client.post("/api/campaigns", json={"name": "Test Campaign"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Test Campaign"
        assert data["id"]
        assert data["party_power_coefficient"] == 1.0
        assert data["gold_balance"] == 0

    async def test_list_campaigns(self, client):
        await client.post("/api/campaigns", json={"name": "Camp A"})
        await client.post("/api/campaigns", json={"name": "Camp B"})
        resp = await client.get("/api/campaigns")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    async def test_get_campaign(self, client):
        create = await client.post("/api/campaigns", json={"name": "My Campaign"})
        cid = create.json()["id"]
        resp = await client.get(f"/api/campaigns/{cid}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "My Campaign"

    async def test_get_campaign_404(self, client):
        resp = await client.get("/api/campaigns/nonexistent")
        assert resp.status_code == 404

    async def test_update_campaign_name(self, client):
        create = await client.post("/api/campaigns", json={"name": "Old Name"})
        cid = create.json()["id"]
        resp = await client.patch(
            f"/api/campaigns/{cid}", json={"name": "New Name"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"

    async def test_update_campaign_settings(self, client):
        create = await client.post("/api/campaigns", json={"name": "Settings Test"})
        cid = create.json()["id"]
        resp = await client.patch(
            f"/api/campaigns/{cid}",
            json={"settings": {"leveling_speed": 1.5, "gold_multiplier": 2.0}},
        )
        assert resp.status_code == 200
        settings = resp.json()["settings"]
        assert settings["leveling_speed"] == 1.5
        assert settings["gold_multiplier"] == 2.0

    async def test_update_campaign_invalid_settings(self, client):
        create = await client.post("/api/campaigns", json={"name": "Bad Settings"})
        cid = create.json()["id"]
        resp = await client.patch(
            f"/api/campaigns/{cid}",
            json={"settings": {"leveling_speed": 100.0}},  # Out of range
        )
        assert resp.status_code == 422

    async def test_delete_campaign(self, client):
        create = await client.post("/api/campaigns", json={"name": "To Delete"})
        cid = create.json()["id"]
        resp = await client.delete(f"/api/campaigns/{cid}")
        assert resp.status_code == 200
        # Verify deleted
        resp = await client.get(f"/api/campaigns/{cid}")
        assert resp.status_code == 404

    async def test_delete_campaign_404(self, client):
        resp = await client.delete("/api/campaigns/nonexistent")
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestCharacterCRUD:
    async def _create_campaign(self, client):
        resp = await client.post("/api/campaigns", json={"name": "Test"})
        return resp.json()["id"]

    async def test_create_character(self, client):
        cid = await self._create_campaign(client)
        resp = await client.post(f"/api/campaigns/{cid}/characters", json={
            "name": "Thorn",
            "character_class": "fighter",
            "level": 3,
            "ac": 18,
            "max_hp": 28,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Thorn"
        assert data["character_class"] == "fighter"
        assert data["level"] == 3
        assert data["campaign_id"] == cid

    async def test_list_characters(self, client):
        cid = await self._create_campaign(client)
        await client.post(f"/api/campaigns/{cid}/characters", json={
            "name": "A", "character_class": "fighter", "level": 1, "ac": 16, "max_hp": 12,
        })
        await client.post(f"/api/campaigns/{cid}/characters", json={
            "name": "B", "character_class": "wizard", "level": 1, "ac": 12, "max_hp": 8,
        })
        resp = await client.get(f"/api/campaigns/{cid}/characters")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_get_character(self, client):
        cid = await self._create_campaign(client)
        create = await client.post(f"/api/campaigns/{cid}/characters", json={
            "name": "Solo", "character_class": "rogue", "level": 5, "ac": 15, "max_hp": 30,
        })
        char_id = create.json()["id"]
        resp = await client.get(f"/api/campaigns/{cid}/characters/{char_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Solo"

    async def test_update_character(self, client):
        cid = await self._create_campaign(client)
        create = await client.post(f"/api/campaigns/{cid}/characters", json={
            "name": "Old", "character_class": "fighter", "level": 1, "ac": 16, "max_hp": 10,
        })
        char_id = create.json()["id"]
        resp = await client.patch(
            f"/api/campaigns/{cid}/characters/{char_id}",
            json={"name": "New", "level": 5, "max_hp": 40},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "New"
        assert data["level"] == 5
        assert data["max_hp"] == 40

    async def test_delete_character(self, client):
        cid = await self._create_campaign(client)
        create = await client.post(f"/api/campaigns/{cid}/characters", json={
            "name": "Temp", "character_class": "wizard", "level": 1, "ac": 12, "max_hp": 6,
        })
        char_id = create.json()["id"]
        resp = await client.delete(f"/api/campaigns/{cid}/characters/{char_id}")
        assert resp.status_code == 200
        # Verify deleted
        resp = await client.get(f"/api/campaigns/{cid}/characters/{char_id}")
        assert resp.status_code == 404

    async def test_award_xp(self, client):
        cid = await self._create_campaign(client)
        create = await client.post(f"/api/campaigns/{cid}/characters", json={
            "name": "XP Test", "character_class": "fighter", "level": 1, "ac": 16, "max_hp": 10,
        })
        char_id = create.json()["id"]
        resp = await client.post(
            f"/api/campaigns/{cid}/characters/{char_id}/award-xp",
            params={"amount": 200},
        )
        assert resp.status_code == 200
        assert resp.json()["xp_total"] == 200

    async def test_award_xp_rejects_negative(self, client):
        cid = await self._create_campaign(client)
        create = await client.post(f"/api/campaigns/{cid}/characters", json={
            "name": "XP Test", "character_class": "fighter", "level": 1, "ac": 16, "max_hp": 10,
        })
        char_id = create.json()["id"]
        resp = await client.post(
            f"/api/campaigns/{cid}/characters/{char_id}/award-xp",
            params={"amount": -50},
        )
        assert resp.status_code == 400
