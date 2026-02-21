import { api } from "./client";

export const economyApi = {
  getBalance: (campaignId: string) =>
    api.get<{ gold_balance: number; astral_shard_balance: number }>(`/campaigns/${campaignId}/economy/balance`),
  getGoldLedger: (campaignId: string, limit?: number) =>
    api.get<unknown[]>(`/campaigns/${campaignId}/economy/gold?limit=${limit || 50}`),
  getShardLedger: (campaignId: string, limit?: number) =>
    api.get<unknown[]>(`/campaigns/${campaignId}/economy/shards?limit=${limit || 50}`),
};

export const enhancementsApi = {
  getCatalog: (campaignId: string, tier?: number) =>
    api.get<unknown[]>(`/campaigns/${campaignId}/enhancements/catalog${tier ? `?tier=${tier}` : ""}`),
  getCharacterEnhancements: (campaignId: string, characterId: string) =>
    api.get<unknown[]>(`/campaigns/${campaignId}/enhancements/character/${characterId}`),
  purchase: (campaignId: string, characterId: string, enhancementId: string) =>
    api.post(`/campaigns/${campaignId}/enhancements/purchase`, { character_id: characterId, enhancement_id: enhancementId }),
};

export const gachaApi = {
  getBanners: (campaignId: string) =>
    api.get<{ key: string; name: string; description: string; item_type: string }[]>(`/campaigns/${campaignId}/gacha/banners`),
  pull: (campaignId: string, banner: string) =>
    api.post(`/campaigns/${campaignId}/gacha/pull?banner=${banner}`),
  getHistory: (campaignId: string, limit?: number) =>
    api.get<unknown[]>(`/campaigns/${campaignId}/gacha/history?limit=${limit || 50}`),
  getPityState: (campaignId: string, banner: string) =>
    api.get<unknown>(`/campaigns/${campaignId}/gacha/pity?banner=${banner}`),
  getCollection: (campaignId: string) =>
    api.get<unknown>(`/campaigns/${campaignId}/gacha/collection`),
};

export const rewardsApi = {
  getChoices: (arenaId: string, floorNumber: number) =>
    api.get<unknown[]>(`/arenas/${arenaId}/rewards?floor_number=${floorNumber}`),
  claimReward: (arenaId: string, data: { reward_id: string; reward_name: string; reward_rarity: string; reward_category: string }) =>
    api.post(`/arenas/${arenaId}/rewards/claim`, data),
  checkShop: (floorId: string, floorNumber: number) =>
    api.get<{ shop_available: boolean; inventory: unknown[] }>(`/floors/${floorId}/shop?floor_number=${floorNumber}`),
  purchaseItem: (floorId: string, data: { item_id: string; item_name: string; item_rarity: string; item_type: string; price: number }) =>
    api.post<{ message: string; inventory_id: string; gold_remaining: number }>(`/floors/${floorId}/shop/purchase`, data),
};

export const archiveApi = {
  getStats: (campaignId: string) =>
    api.get<unknown>(`/campaigns/${campaignId}/archive/stats`),
  getRunHistory: (campaignId: string, limit?: number) =>
    api.get<unknown[]>(`/campaigns/${campaignId}/archive/runs?limit=${limit || 20}`),
  getDifficultyCurves: (campaignId: string, lastN?: number) =>
    api.get<unknown[]>(`/campaigns/${campaignId}/archive/difficulty-curves?last_n=${lastN || 5}`),
};
