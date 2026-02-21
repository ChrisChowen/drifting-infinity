import { api } from "./client";

export const armillaryApi = {
  list: (arenaId: string) =>
    api.get<unknown[]>(`/arenas/${arenaId}/armillary`),
  roll: (arenaId: string, roundNumber: number) =>
    api.post<unknown>(`/arenas/${arenaId}/armillary/roll?round_number=${roundNumber}`),
  reroll: (arenaId: string, effectId: string) =>
    api.post<unknown>(`/arenas/${arenaId}/armillary/reroll?effect_id=${effectId}`),
  forecast: (arenaId: string) =>
    api.get<unknown>(`/arenas/${arenaId}/armillary/forecast`),
};
