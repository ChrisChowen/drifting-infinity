import { useEffect, useState, useCallback } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { useEconomyStore } from "@/stores/useEconomyStore";
import { gachaApi } from "@/api/economy";
import { Card, CardHeader, CardTitle, Badge, Button, PageHeader, EmptyState, LoadingState } from "@/components/ui";
import { useToastStore } from "@/stores/useToastStore";
import { Gem, Star, Sparkles, Clock, ArrowLeft } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { clsx } from "clsx";
import { getRarityConfig } from "@/lib/rarity";
import { PullSequence } from "@/components/gacha/PullSequence";

/* ---------- Local types ---------- */

interface PullResult {
  id: string;
  banner: string;
  rarity: string;
  pull_number: number;
  result_type: string;
  result_id: string;
  was_pity: boolean;
  was_duplicate: boolean;
  item_name?: string;
  item_description?: string;
}

interface PityState {
  total_pulls: number;
  pulls_since_rare: number;
  pulls_since_very_rare: number;
  pulls_since_legendary: number;
}

interface BannerInfo {
  key: string;
  name: string;
  description: string;
  item_type: string;
}

/* ---------- Constants ---------- */

const PULL_COST = 5;
const PULL_10_COST = 50;

const BANNER_THEMES: Record<string, { accent: string; bg: string; border: string }> = {
  weapon: { accent: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/40" },
  variant: { accent: "text-purple-400", bg: "bg-purple-500/10", border: "border-purple-500/40" },
  identity: { accent: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/40" },
};

const DEFAULT_BANNER_THEME = { accent: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/40" };

function getBannerTheme(itemType: string) {
  return BANNER_THEMES[itemType] ?? DEFAULT_BANNER_THEME;
}

/* ---------- Component ---------- */

export function GachaPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const returnTo = searchParams.get("returnTo");

  const { activeCampaignId } = useCampaignStore();
  const { astralShardBalance, fetchBalance } = useEconomyStore();

  const [banners, setBanners] = useState<BannerInfo[]>([]);
  const [selectedBanner, setSelectedBanner] = useState<BannerInfo | null>(null);
  const [pity, setPity] = useState<PityState | null>(null);
  const [pullResults, setPullResults] = useState<PullResult[]>([]);
  const [history, setHistory] = useState<PullResult[]>([]);
  const [collection, setCollection] = useState<Record<string, number>>({});
  const [pulling, setPulling] = useState(false);
  const [showingCeremony, setShowingCeremony] = useState(false);
  const [loadingBanners, setLoadingBanners] = useState(false);

  useEffect(() => {
    if (!activeCampaignId) return;
    setLoadingBanners(true);
    gachaApi
      .getBanners(activeCampaignId)
      .then((data) => {
        setBanners(data);
        if (data.length > 0 && !selectedBanner && data[0]) {
          setSelectedBanner(data[0]);
        }
      })
      .catch(() => setBanners([]))
      .finally(() => setLoadingBanners(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeCampaignId]);

  useEffect(() => {
    if (activeCampaignId) fetchBalance(activeCampaignId);
  }, [activeCampaignId, fetchBalance]);

  const loadBannerData = useCallback(async () => {
    if (!activeCampaignId || !selectedBanner) return;

    const [pityData, historyData, collectionData] = await Promise.all([
      gachaApi.getPityState(activeCampaignId, selectedBanner.key).catch(() => null),
      gachaApi.getHistory(activeCampaignId, 20).catch(() => []),
      gachaApi.getCollection(activeCampaignId).catch(() => ({})),
    ]);

    if (pityData) setPity(pityData as PityState);
    setHistory(historyData as PullResult[]);

    if (collectionData && typeof collectionData === "object") {
      setCollection(collectionData as Record<string, number>);
    }
  }, [activeCampaignId, selectedBanner]);

  useEffect(() => {
    loadBannerData();
  }, [loadBannerData]);

  const handlePull = async (count: 1 | 10) => {
    if (!activeCampaignId || !selectedBanner) return;
    setPulling(true);
    setShowingCeremony(false);

    try {
      const results: PullResult[] = [];
      for (let i = 0; i < count; i++) {
        const result = await gachaApi.pull(activeCampaignId, selectedBanner.key);
        results.push(result as PullResult);
      }

      setPullResults(results);
      setShowingCeremony(true);
      await Promise.all([
        fetchBalance(activeCampaignId),
        loadBannerData(),
      ]);
    } catch {
      useToastStore.getState().addToast("Pull failed. Not enough Astral Shards.", "error");
    } finally {
      setPulling(false);
    }
  };

  const handleCeremonyComplete = useCallback(() => {
    setShowingCeremony(false);
  }, []);

  const canPull1 = astralShardBalance >= PULL_COST;
  const canPull10 = astralShardBalance >= PULL_10_COST;

  return (
    <div className="space-y-6">
      <PageHeader
        title="The Vault"
        subtitle="The Armillary yields relics from previous challengers. Spend Astral Shards to recover them."
        action={
          <div className="flex items-center gap-2 bg-surface-2 rounded-lg px-3 py-1.5">
            <Gem size={16} className="text-shard" />
            <span className="text-lg font-bold text-shard font-display">{astralShardBalance.toLocaleString()}</span>
          </div>
        }
      />

      {returnTo && (
        <Button
          variant="secondary"
          size="md"
          icon={<ArrowLeft size={16} />}
          onClick={() => navigate(returnTo)}
        >
          Return to Expedition
        </Button>
      )}

      {/* Banner Selection */}
      {loadingBanners ? (
        <LoadingState message="Summoning banners..." />
      ) : banners.length === 0 ? (
        <EmptyState
          icon={<Star size={40} />}
          title="No Banners Available"
          description="Complete more runs to unlock gacha banners."
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {banners.map((banner) => {
            const theme = getBannerTheme(banner.item_type);
            const isSelected = selectedBanner?.key === banner.key;

            return (
              <Card
                key={banner.key}
                hover
                selected={isSelected}
                padding="md"
                className={clsx(theme.bg, isSelected && theme.border)}
                onClick={() => {
                  setSelectedBanner(banner);
                  setPullResults([]);
                  setShowingCeremony(false);
                }}
              >
                <h3 className={`text-lg font-bold font-display ${theme.accent}`}>
                  {banner.name}
                </h3>
                <p className="text-gray-400 text-sm mt-1">
                  {banner.description}
                </p>
                <div className="text-xs text-gray-500 mt-2 uppercase tracking-wide">
                  {banner.item_type.replace(/_/g, " ")}
                </div>
                {collection[banner.key] !== undefined && (
                  <div className="text-xs text-gray-400 mt-1">
                    {collection[banner.key]} unique collected
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      )}

      {/* Selected Banner Details */}
      {selectedBanner && (
        <Card padding="lg">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-5">
            <div>
              <h2 className="text-xl font-semibold text-white font-display">
                {selectedBanner.name}
              </h2>
              <p className="text-sm text-gray-400 mt-1">
                Cost: <span className="text-shard font-medium">{PULL_COST} Astral Shards</span> per pull
              </p>
            </div>

            {/* Pull Buttons */}
            <div className="flex gap-3">
              <Button
                variant="primary"
                size="md"
                icon={<Sparkles size={16} />}
                disabled={!canPull1}
                loading={pulling}
                onClick={() => handlePull(1)}
              >
                Pull x1
              </Button>
              <Button
                variant="secondary"
                size="md"
                disabled={!canPull10}
                loading={pulling}
                onClick={() => handlePull(10)}
              >
                Pull x10
              </Button>
            </div>
          </div>

          {/* Pity Counters */}
          {pity && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: "Total Pulls", value: pity.total_pulls, color: "text-white" },
                { label: "Since Rare", value: pity.pulls_since_rare, color: "text-blue-300" },
                { label: "Since Very Rare", value: pity.pulls_since_very_rare, color: "text-purple-300" },
                { label: "Since Legendary", value: pity.pulls_since_legendary, color: "text-amber-300" },
              ].map((stat) => (
                <div key={stat.label} className="bg-surface-2 rounded-lg p-3">
                  <div className="text-xs text-gray-400">{stat.label}</div>
                  <div className={`text-lg font-bold ${stat.color}`}>{stat.value}</div>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}

      {/* Pull Ceremony */}
      <AnimatePresence>
        {showingCeremony && pullResults.length > 0 && (
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <PullSequence
              results={pullResults}
              onComplete={handleCeremonyComplete}
            />
          </motion.section>
        )}
      </AnimatePresence>

      {/* Static Results (shown after ceremony completes) */}
      <AnimatePresence>
        {!showingCeremony && pullResults.length > 0 && (
          <motion.section
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <h2 className="text-lg font-semibold text-white font-display">Pull Results</h2>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {pullResults.map((result) => {
                const config = getRarityConfig(result.rarity);

                return (
                  <div
                    key={result.id}
                    className={clsx(
                      "bg-surface-1 rounded-xl border-2 p-4 text-center",
                      config.border,
                      config.glow,
                    )}
                  >
                    <div className={`text-sm font-bold ${config.text}`}>
                      {result.item_name ?? result.result_type}
                    </div>
                    <div className={`text-xs mt-1 ${config.text}`}>
                      {config.label}
                    </div>
                    {result.item_description && (
                      <p className="text-xs text-gray-400 mt-2 line-clamp-2">
                        {result.item_description}
                      </p>
                    )}
                    <div className="flex items-center justify-center gap-2 mt-2">
                      {result.was_pity && <Badge color="gold">PITY</Badge>}
                      {result.was_duplicate && <Badge color="gray">DUP</Badge>}
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* Pull History */}
      {history.length > 0 && (
        <Card padding="lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock size={18} className="text-gray-400" />
              Recent Pull History
            </CardTitle>
          </CardHeader>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {history.map((entry) => {
              const config = getRarityConfig(entry.rarity);
              return (
                <div
                  key={entry.id}
                  className="flex items-center justify-between bg-surface-2 rounded-lg px-4 py-2"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-500 w-8 text-right">
                      #{entry.pull_number}
                    </span>
                    <span className="text-sm text-white">
                      {entry.item_name ?? entry.result_type}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {entry.was_pity && <Badge color="gold">PITY</Badge>}
                    {entry.was_duplicate && <Badge color="gray">DUP</Badge>}
                    <span className={`text-xs font-medium ${config.text}`}>
                      {config.label}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Collection Tracker */}
      {Object.keys(collection).length > 0 && (
        <Card padding="lg">
          <CardHeader>
            <CardTitle>Collection Tracker</CardTitle>
          </CardHeader>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {banners.map((banner) => {
              const theme = getBannerTheme(banner.item_type);
              const count = collection[banner.key] ?? 0;
              return (
                <div
                  key={banner.key}
                  className="bg-surface-2 rounded-lg p-4 flex items-center justify-between"
                >
                  <span className={`font-medium ${theme.accent}`}>
                    {banner.name}
                  </span>
                  <span className="text-white font-bold">
                    {count} <span className="text-gray-400 font-normal text-sm">unique</span>
                  </span>
                </div>
              );
            })}
          </div>
        </Card>
      )}
    </div>
  );
}
