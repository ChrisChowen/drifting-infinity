import { api } from "./client";

export interface CharacterSnapshotPayload {
  character_id: string;
  name: string;
  hp_percentage: number;
  is_on_final_stand: boolean;
  is_dead: boolean;
  resources_depleted: number;
}

export interface SnapshotCreatePayload {
  dm_assessment: string;
  dm_combat_perception: string;
  any_on_final_stand: boolean;
  character_snapshots: CharacterSnapshotPayload[];
}

export interface SnapshotResponse {
  id: string;
  floor_id: string;
  after_arena_number: number;
  dm_assessment: string;
  dm_combat_perception: string | null;
  any_on_final_stand: boolean;
  character_snapshots: CharacterSnapshotPayload[];
  average_hp_percentage: number;
  lowest_hp_percentage: number;
  any_dead: boolean;
  estimated_resource_depletion: number;
  cumulative_stress: number;
}

export const snapshotsApi = {
  submit: (floorId: string, data: SnapshotCreatePayload) =>
    api.post<SnapshotResponse>(`/floors/${floorId}/snapshots`, data),

  list: (floorId: string) =>
    api.get<SnapshotResponse[]>(`/floors/${floorId}/snapshots`),
};
