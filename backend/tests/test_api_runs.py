"""Integration tests for run lifecycle endpoints (runs, floors, arenas)."""

import pytest


@pytest.mark.asyncio
class TestRunLifecycle:
    """Test a complete run lifecycle: campaign → characters → run → floor → arena → complete."""

    async def _setup_campaign_with_party(self, client):
        """Helper: create a campaign with 4 characters."""
        resp = await client.post("/api/campaigns", json={"name": "Run Test"})
        cid = resp.json()["id"]
        chars = [
            {"name": "Fighter", "character_class": "fighter", "level": 3, "ac": 18, "max_hp": 28},
            {"name": "Wizard", "character_class": "wizard", "level": 3, "ac": 13, "max_hp": 16},
            {"name": "Cleric", "character_class": "cleric", "level": 3, "ac": 18, "max_hp": 24},
            {"name": "Rogue", "character_class": "rogue", "level": 3, "ac": 15, "max_hp": 21},
        ]
        for c in chars:
            await client.post(f"/api/campaigns/{cid}/characters", json=c)
        return cid

    async def test_start_run(self, client):
        cid = await self._setup_campaign_with_party(client)
        resp = await client.post(
            f"/api/campaigns/{cid}/runs",
            json={"floor_count": 5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["campaign_id"] == cid
        assert data["floor_count"] == 5
        assert data["starting_level"] == 3
        assert data["outcome"] is None

    async def test_start_run_auto_level(self, client):
        cid = await self._setup_campaign_with_party(client)
        resp = await client.post(f"/api/campaigns/{cid}/runs", json={})
        assert resp.status_code == 200
        assert resp.json()["starting_level"] == 3  # Average of 4 level-3 chars

    async def test_start_run_no_characters_400(self, client):
        resp = await client.post("/api/campaigns", json={"name": "Empty"})
        cid = resp.json()["id"]
        resp = await client.post(f"/api/campaigns/{cid}/runs", json={})
        assert resp.status_code == 400
        assert "No characters" in resp.json()["detail"]

    async def test_start_run_campaign_404(self, client):
        resp = await client.post("/api/campaigns/nonexistent/runs", json={})
        assert resp.status_code == 404

    async def test_list_runs(self, client):
        cid = await self._setup_campaign_with_party(client)
        await client.post(f"/api/campaigns/{cid}/runs", json={"floor_count": 5})
        resp = await client.get(f"/api/campaigns/{cid}/runs")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_get_active_run(self, client):
        cid = await self._setup_campaign_with_party(client)
        create = await client.post(
            f"/api/campaigns/{cid}/runs", json={"floor_count": 5},
        )
        run_id = create.json()["id"]
        resp = await client.get(f"/api/campaigns/{cid}/runs/active")
        assert resp.status_code == 200
        assert resp.json()["id"] == run_id

    async def test_end_run(self, client):
        cid = await self._setup_campaign_with_party(client)
        create = await client.post(
            f"/api/campaigns/{cid}/runs", json={"floor_count": 5},
        )
        run_id = create.json()["id"]
        resp = await client.post(
            f"/api/campaigns/{cid}/runs/{run_id}/end",
            params={"outcome": "completed"},
        )
        assert resp.status_code == 200
        # Verify run is now ended
        get_resp = await client.get(f"/api/campaigns/{cid}/runs/{run_id}")
        assert get_resp.json()["outcome"] == "completed"

    async def test_end_run_already_ended(self, client):
        cid = await self._setup_campaign_with_party(client)
        create = await client.post(
            f"/api/campaigns/{cid}/runs", json={"floor_count": 5},
        )
        run_id = create.json()["id"]
        await client.post(
            f"/api/campaigns/{cid}/runs/{run_id}/end",
            params={"outcome": "completed"},
        )
        resp = await client.post(
            f"/api/campaigns/{cid}/runs/{run_id}/end",
            params={"outcome": "failed"},
        )
        assert resp.status_code == 400

    async def test_end_run_increments_campaign_total(self, client):
        cid = await self._setup_campaign_with_party(client)
        create = await client.post(
            f"/api/campaigns/{cid}/runs", json={"floor_count": 5},
        )
        run_id = create.json()["id"]
        await client.post(
            f"/api/campaigns/{cid}/runs/{run_id}/end",
            params={"outcome": "completed"},
        )
        campaign = await client.get(f"/api/campaigns/{cid}")
        assert campaign.json()["total_runs"] == 1


@pytest.mark.asyncio
class TestFloorLifecycle:
    async def _setup_run(self, client):
        resp = await client.post("/api/campaigns", json={"name": "Floor Test"})
        cid = resp.json()["id"]
        await client.post(f"/api/campaigns/{cid}/characters", json={
            "name": "Hero", "character_class": "fighter", "level": 1, "ac": 16, "max_hp": 12,
        })
        run_resp = await client.post(
            f"/api/campaigns/{cid}/runs", json={"floor_count": 5},
        )
        return cid, run_resp.json()["id"]

    async def test_start_floor(self, client):
        cid, run_id = await self._setup_run(client)
        resp = await client.post(
            f"/api/runs/{run_id}/floors",
            json={"arena_count": 4},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["floor_number"] == 1
        assert data["arena_count"] == 4
        assert data["is_complete"] is False

    async def test_list_floors(self, client):
        cid, run_id = await self._setup_run(client)
        await client.post(f"/api/runs/{run_id}/floors", json={"arena_count": 3})
        resp = await client.get(f"/api/runs/{run_id}/floors")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_get_active_floor(self, client):
        cid, run_id = await self._setup_run(client)
        create = await client.post(
            f"/api/runs/{run_id}/floors", json={"arena_count": 3},
        )
        floor_id = create.json()["id"]
        resp = await client.get(f"/api/runs/{run_id}/floors/active")
        assert resp.status_code == 200
        assert resp.json()["id"] == floor_id

    async def test_complete_floor(self, client):
        cid, run_id = await self._setup_run(client)
        create = await client.post(
            f"/api/runs/{run_id}/floors", json={"arena_count": 3},
        )
        floor_id = create.json()["id"]
        resp = await client.post(f"/api/runs/{run_id}/floors/{floor_id}/complete")
        assert resp.status_code == 200

    async def test_complete_floor_already_complete(self, client):
        cid, run_id = await self._setup_run(client)
        create = await client.post(
            f"/api/runs/{run_id}/floors", json={"arena_count": 3},
        )
        floor_id = create.json()["id"]
        await client.post(f"/api/runs/{run_id}/floors/{floor_id}/complete")
        resp = await client.post(f"/api/runs/{run_id}/floors/{floor_id}/complete")
        assert resp.status_code == 400

    async def test_floor_number_auto_increments(self, client):
        cid, run_id = await self._setup_run(client)
        r1 = await client.post(f"/api/runs/{run_id}/floors", json={"arena_count": 3})
        r2 = await client.post(f"/api/runs/{run_id}/floors", json={"arena_count": 3})
        assert r1.json()["floor_number"] == 1
        assert r2.json()["floor_number"] == 2

    async def test_cannot_exceed_floor_count(self, client):
        resp = await client.post("/api/campaigns", json={"name": "Small"})
        cid = resp.json()["id"]
        await client.post(f"/api/campaigns/{cid}/characters", json={
            "name": "Hero", "character_class": "fighter", "level": 1, "ac": 16, "max_hp": 12,
        })
        run_resp = await client.post(
            f"/api/campaigns/{cid}/runs", json={"floor_count": 2},
        )
        run_id = run_resp.json()["id"]
        await client.post(f"/api/runs/{run_id}/floors", json={"arena_count": 3})
        await client.post(f"/api/runs/{run_id}/floors", json={"arena_count": 3})
        resp = await client.post(f"/api/runs/{run_id}/floors", json={"arena_count": 3})
        assert resp.status_code == 400
        assert "All floors already created" in resp.json()["detail"]


@pytest.mark.asyncio
class TestArenaLifecycle:
    async def _setup_floor(self, client):
        resp = await client.post("/api/campaigns", json={"name": "Arena Test"})
        cid = resp.json()["id"]
        await client.post(f"/api/campaigns/{cid}/characters", json={
            "name": "Hero", "character_class": "fighter", "level": 1, "ac": 16, "max_hp": 12,
        })
        run_resp = await client.post(
            f"/api/campaigns/{cid}/runs", json={"floor_count": 5},
        )
        run_id = run_resp.json()["id"]
        floor_resp = await client.post(
            f"/api/runs/{run_id}/floors", json={"arena_count": 3},
        )
        return cid, run_id, floor_resp.json()["id"]

    async def test_start_arena(self, client):
        cid, run_id, floor_id = await self._setup_floor(client)
        resp = await client.post(f"/api/floors/{floor_id}/arenas")
        assert resp.status_code == 200
        data = resp.json()
        assert data["arena_number"] == 1
        assert data["is_active"] is True
        assert data["is_complete"] is False

    async def test_list_arenas(self, client):
        cid, run_id, floor_id = await self._setup_floor(client)
        await client.post(f"/api/floors/{floor_id}/arenas")
        resp = await client.get(f"/api/floors/{floor_id}/arenas")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_get_active_arena(self, client):
        cid, run_id, floor_id = await self._setup_floor(client)
        create = await client.post(f"/api/floors/{floor_id}/arenas")
        arena_id = create.json()["id"]
        resp = await client.get(f"/api/floors/{floor_id}/arenas/active")
        assert resp.status_code == 200
        assert resp.json()["id"] == arena_id

    async def test_complete_arena(self, client):
        cid, run_id, floor_id = await self._setup_floor(client)
        create = await client.post(f"/api/floors/{floor_id}/arenas")
        arena_id = create.json()["id"]
        resp = await client.post(f"/api/floors/{floor_id}/arenas/{arena_id}/complete")
        assert resp.status_code == 200
        data = resp.json()
        assert "completed" in data["message"]
        assert "gold_per_player" in data
        assert "xp_award" in data

    async def test_complete_arena_already_complete(self, client):
        cid, run_id, floor_id = await self._setup_floor(client)
        create = await client.post(f"/api/floors/{floor_id}/arenas")
        arena_id = create.json()["id"]
        await client.post(f"/api/floors/{floor_id}/arenas/{arena_id}/complete")
        resp = await client.post(f"/api/floors/{floor_id}/arenas/{arena_id}/complete")
        assert resp.status_code == 400

    async def test_arena_number_auto_increments(self, client):
        cid, run_id, floor_id = await self._setup_floor(client)
        a1 = await client.post(f"/api/floors/{floor_id}/arenas")
        a2 = await client.post(f"/api/floors/{floor_id}/arenas")
        assert a1.json()["arena_number"] == 1
        assert a2.json()["arena_number"] == 2

    async def test_cannot_exceed_arena_count(self, client):
        cid, run_id, floor_id = await self._setup_floor(client)
        # Floor has arena_count=3
        await client.post(f"/api/floors/{floor_id}/arenas")
        await client.post(f"/api/floors/{floor_id}/arenas")
        await client.post(f"/api/floors/{floor_id}/arenas")
        resp = await client.post(f"/api/floors/{floor_id}/arenas")
        assert resp.status_code == 400
        assert "All arenas already created" in resp.json()["detail"]

    async def test_cannot_add_arena_to_complete_floor(self, client):
        cid, run_id, floor_id = await self._setup_floor(client)
        # Complete the floor first
        await client.post(f"/api/runs/{run_id}/floors/{floor_id}/complete")
        resp = await client.post(f"/api/floors/{floor_id}/arenas")
        assert resp.status_code == 400


@pytest.mark.asyncio
class TestFullRunFlow:
    """End-to-end test: campaign → party → run → floor → arenas → complete."""

    async def test_complete_flow(self, client):
        # 1. Create campaign
        camp = await client.post("/api/campaigns", json={"name": "E2E Test"})
        cid = camp.json()["id"]

        # 2. Add characters
        for char in [
            {"name": "Fighter", "character_class": "fighter", "level": 1, "ac": 16, "max_hp": 12},
            {"name": "Wizard", "character_class": "wizard", "level": 1, "ac": 12, "max_hp": 8},
        ]:
            resp = await client.post(f"/api/campaigns/{cid}/characters", json=char)
            assert resp.status_code == 200

        # 3. Start run
        run = await client.post(
            f"/api/campaigns/{cid}/runs", json={"floor_count": 2},
        )
        assert run.status_code == 200
        run_id = run.json()["id"]
        assert run.json()["starting_level"] == 1

        # 4. Start floor 1
        floor = await client.post(
            f"/api/runs/{run_id}/floors", json={"arena_count": 2},
        )
        assert floor.status_code == 200
        floor_id = floor.json()["id"]
        assert floor.json()["floor_number"] == 1

        # 5. Start and complete arena 1
        arena1 = await client.post(f"/api/floors/{floor_id}/arenas")
        assert arena1.status_code == 200
        a1_id = arena1.json()["id"]
        complete1 = await client.post(
            f"/api/floors/{floor_id}/arenas/{a1_id}/complete",
        )
        assert complete1.status_code == 200

        # 6. Start and complete arena 2
        arena2 = await client.post(f"/api/floors/{floor_id}/arenas")
        a2_id = arena2.json()["id"]
        await client.post(f"/api/floors/{floor_id}/arenas/{a2_id}/complete")

        # 7. Complete floor 1
        await client.post(f"/api/runs/{run_id}/floors/{floor_id}/complete")

        # 8. Start floor 2
        floor2 = await client.post(
            f"/api/runs/{run_id}/floors", json={"arena_count": 2},
        )
        assert floor2.json()["floor_number"] == 2

        # 9. End run
        end = await client.post(
            f"/api/campaigns/{cid}/runs/{run_id}/end",
            params={"outcome": "completed"},
        )
        assert end.status_code == 200

        # 10. Verify final state
        final_run = await client.get(f"/api/campaigns/{cid}/runs/{run_id}")
        assert final_run.json()["outcome"] == "completed"
        campaign = await client.get(f"/api/campaigns/{cid}")
        assert campaign.json()["total_runs"] == 1
