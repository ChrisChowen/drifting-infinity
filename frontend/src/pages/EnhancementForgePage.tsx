import { useEffect, useState, useCallback } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { useEconomyStore } from "@/stores/useEconomyStore";
import { enhancementsApi } from "@/api/economy";
import { Card, Badge, Button, PageHeader, EmptyState, LoadingState, Select } from "@/components/ui";
import { Hammer, Coins, Check, Sparkles, BookOpen, ArrowLeft } from "lucide-react";
import { motion } from "framer-motion";
import { clsx } from "clsx";

interface EnhancementItem {
  id: string;
  name: string;
  tier: number;
  base_cost: number;
  effect: Record<string, string | number | boolean>;
  power_rating: number;
  description: string;
  d20_source?: string;
  stacking_rules: { max_per_character: number; stacks_with: string[] };
}

const ARTIFICER_QUOTES = [
  "The Armillary's essence can be bound to mortal frames... for a price.",
  "Each enhancement echoes a legend from beyond the arena.",
  "Choose wisely. The arena does not forgive the unprepared.",
  "These materials were forged from the residue of fallen challengers.",
];

const TIER_CONFIG = {
  1: { label: "Common Materials", badge: "emerald" as const, accent: "bg-emerald-600 hover:bg-emerald-700" },
  2: { label: "Rare Alloys", badge: "blue" as const, accent: "bg-blue-600 hover:bg-blue-700" },
  3: { label: "Legendary Essences", badge: "purple" as const, accent: "bg-purple-600 hover:bg-purple-700" },
} satisfies Record<number, { label: string; badge: "emerald" | "blue" | "purple"; accent: string }>;

export function EnhancementForgePage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const returnTo = searchParams.get("returnTo");

  const { characters, activeCampaignId } = useCampaignStore();
  const { goldBalance, fetchBalance } = useEconomyStore();

  const [activeTier, setActiveTier] = useState<1 | 2 | 3>(1);
  const [selectedCharacterId, setSelectedCharacterId] = useState<string>("");
  const [catalog, setCatalog] = useState<EnhancementItem[]>([]);
  const [ownedIds, setOwnedIds] = useState<Set<string>>(new Set());
  const [loadingCatalog, setLoadingCatalog] = useState(false);
  const [purchasing, setPurchasing] = useState<string | null>(null);

  useEffect(() => {
    if (characters.length > 0 && !selectedCharacterId && characters[0]) {
      setSelectedCharacterId(characters[0].id);
    }
  }, [characters, selectedCharacterId]);

  const fetchCatalog = useCallback(async () => {
    if (!activeCampaignId) return;
    setLoadingCatalog(true);
    try {
      const items = await enhancementsApi.getCatalog(activeCampaignId, activeTier);
      setCatalog(items as EnhancementItem[]);
    } catch {
      setCatalog([]);
    } finally {
      setLoadingCatalog(false);
    }
  }, [activeCampaignId, activeTier]);

  useEffect(() => {
    fetchCatalog();
  }, [fetchCatalog]);

  useEffect(() => {
    if (!activeCampaignId || !selectedCharacterId) return;
    enhancementsApi
      .getCharacterEnhancements(activeCampaignId, selectedCharacterId)
      .then((owned) => {
        const ids = new Set((owned as { enhancement_id: string }[]).map((e) => e.enhancement_id));
        setOwnedIds(ids);
      })
      .catch(() => setOwnedIds(new Set()));
  }, [activeCampaignId, selectedCharacterId]);

  useEffect(() => {
    if (activeCampaignId) fetchBalance(activeCampaignId);
  }, [activeCampaignId, fetchBalance]);

  const handlePurchase = async (enhancement: EnhancementItem) => {
    if (!activeCampaignId || !selectedCharacterId) return;
    setPurchasing(enhancement.id);
    try {
      await enhancementsApi.purchase(activeCampaignId, selectedCharacterId, enhancement.id);
      setOwnedIds((prev) => new Set([...prev, enhancement.id]));
      await fetchBalance(activeCampaignId);
    } catch {
      // Purchase failed
    } finally {
      setPurchasing(null);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="The Artificer's Workshop"
        subtitle="Korvath the Artificer offers to bind the Armillary's essence to your champions."
        action={
          <div className="flex items-center gap-2 bg-surface-2 rounded-lg px-3 py-1.5">
            <Coins size={16} className="text-gold" />
            <span className="text-lg font-bold text-gold font-display">{goldBalance.toLocaleString()}</span>
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

      {/* Artificer Quote */}
      <Card padding="sm" className="border-accent/20">
        <p className="text-sm text-gray-400 italic text-center">
          "{ARTIFICER_QUOTES[Math.floor(Date.now() / 60000) % ARTIFICER_QUOTES.length]}"
          <span className="block text-xs text-gray-600 mt-1">— Korvath the Artificer</span>
        </p>
      </Card>

      {/* Character Selector */}
      <Card padding="sm">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
          <Hammer size={20} className="text-accent shrink-0" />
          <Select
            label="Enhance Character"
            value={selectedCharacterId}
            onChange={(e) => setSelectedCharacterId(e.target.value)}
            className="flex-1"
          >
            {characters.length === 0 && (
              <option value="">No characters available</option>
            )}
            {characters.map((char) => (
              <option key={char.id} value={char.id}>
                {char.name} — Lv.{char.level} {char.character_class}
              </option>
            ))}
          </Select>
        </div>
      </Card>

      {/* Tier Tabs */}
      <div className="flex gap-2">
        {([1, 2, 3] as const).map((tier) => {
          const config = TIER_CONFIG[tier];
          const isActive = activeTier === tier;
          return (
            <button
              key={tier}
              className={clsx(
                "px-5 py-2 rounded-lg font-medium transition-colors cursor-pointer",
                isActive
                  ? `${config.accent} text-white`
                  : "bg-surface-2 text-gray-400 hover:bg-surface-3 hover:text-white"
              )}
              onClick={() => setActiveTier(tier)}
            >
              {config.label}
            </button>
          );
        })}
      </div>

      {/* Enhancement Catalog Grid */}
      {loadingCatalog ? (
        <LoadingState message="Heating the forge..." />
      ) : catalog.length === 0 ? (
        <EmptyState
          icon={<Sparkles size={40} />}
          title="No Enhancements Available"
          description={`No enhancements available for ${TIER_CONFIG[activeTier].label}.`}
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {catalog.map((enhancement, i) => {
            const tierKey = (enhancement.tier as 1 | 2 | 3) in TIER_CONFIG ? (enhancement.tier as 1 | 2 | 3) : 1;
            const config = TIER_CONFIG[tierKey];
            const isOwned = ownedIds.has(enhancement.id);
            const canAfford = goldBalance >= enhancement.base_cost;
            const isPurchasing = purchasing === enhancement.id;

            return (
              <motion.div
                key={enhancement.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
              >
                <Card
                  padding="md"
                  className={clsx(
                    isOwned && "border-emerald-500/40"
                  )}
                >
                  {/* Card Header */}
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <h3 className="text-white font-semibold truncate">{enhancement.name}</h3>
                    <Badge color={config.badge}>T{enhancement.tier}</Badge>
                  </div>

                  {/* Description */}
                  <p className="text-gray-400 text-sm leading-relaxed mb-2">
                    {enhancement.description}
                  </p>
                  {enhancement.d20_source && (
                    <p className="flex items-center gap-1 text-xs text-gray-600 mb-3">
                      <BookOpen size={10} />
                      Based on: <span className="text-gray-500">{enhancement.d20_source}</span>
                    </p>
                  )}

                  {/* Stats Row */}
                  <div className="flex items-center justify-between text-sm mb-3">
                    <span className="text-gold font-medium">
                      {enhancement.base_cost.toLocaleString()} gold
                    </span>
                    <span className="text-gray-400">
                      Power: <span className="text-white font-medium">{enhancement.power_rating}</span>
                    </span>
                  </div>

                  {/* Purchase / Owned */}
                  {isOwned ? (
                    <div className="flex items-center gap-2 text-emerald-400 text-sm font-medium">
                      <Check size={16} />
                      Owned
                    </div>
                  ) : (
                    <Button
                      variant={canAfford ? "primary" : "secondary"}
                      size="sm"
                      className="w-full"
                      disabled={!canAfford || isPurchasing || !selectedCharacterId}
                      loading={isPurchasing}
                      onClick={() => handlePurchase(enhancement)}
                    >
                      {canAfford ? "Purchase" : "Not Enough Gold"}
                    </Button>
                  )}
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
