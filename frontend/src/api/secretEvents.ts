import { api } from "./client";

export interface SecretEvent {
  id: string;
  name: string;
  description: string;
  dm_instructions: string;
  trigger_type: string;
  content_type: string;
  rewards: Record<string, string | number | boolean>;
  lore_fragment_id: string | null;
  is_floor_event: boolean;
}

export const secretEventsApi = {
  check: (runId: string, floorNumber: number, triggerType = "floor_transition", arenaNumber = 1) =>
    api.post<SecretEvent | null>(`/runs/${runId}/secret-events/check`, {
      floor_number: floorNumber,
      arena_number: arenaNumber,
      trigger_type: triggerType,
    }),
  get: (runId: string, eventId: string) =>
    api.get<SecretEvent>(`/runs/${runId}/secret-events/${eventId}`),
};
