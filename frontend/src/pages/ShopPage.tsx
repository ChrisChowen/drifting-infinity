import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useRunStore } from "@/stores/useRunStore";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { useEconomyStore } from "@/stores/useEconomyStore";
import { rewardsApi } from "@/api/economy";
import { Card, Badge, Button, PageHeader, LoadingState } from "@/components/ui";
import { useToastStore } from "@/stores/useToastStore";
import { ShoppingBag, Coins, Check, ArrowRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { clsx } from "clsx";
import { getRarityConfig } from "@/lib/rarity";
import { TypewriterText } from "@/components/transitions/TypewriterText";

interface ShopItem {
  id: string;
  name: string;
  type: string;
  rarity: string;
  description: string;
  price: number;
  effect: Record<string, string | number | boolean>;
}

const MERCHANT_GREETINGS = [
  "Ah, adventurers! I've wares that might interest you...",
  "Step closer, friends. These relics won't sell themselves.",
  "The Armillary led me here, and it seems it led you too.",
  "Rare goods, fair prices. Well... mostly fair.",
  "You look like you've seen battle. Perhaps these will help?",
];

const MERCHANT_BROWSE = [
  "Take your time. I'm not going anywhere... yet.",
  "That one's a fine choice, if I do say so myself.",
  "Hmm, studying the wares closely. A discerning eye!",
  "Everything here was found in the depths. Still warm, some of it.",
];

const MERCHANT_PURCHASE = [
  "Excellent taste! That one's served many a champion well.",
  "A wise investment. May it bring you fortune below.",
  "Pleasure doing business with you, friend.",
  "Another item finds a worthy owner.",
];

const MERCHANT_POOR = [
  "Ah... perhaps after your next arena, you'll have the coin.",
  "I might lower the price. Might. Come back later.",
  "Gold is earned in the depths, friend. Go earn some more.",
];

function pickRandom(arr: string[]): string {
  return arr[Math.floor(Math.random() * arr.length)]!;
}

const CATEGORY_BADGE: Record<string, string> = {
  consumable: "emerald",
  equipment: "gold",
  buff: "blue",
  favour: "purple",
  spell: "indigo",
  prestige: "gold",
  enhancement: "blue",
};

export function ShopPage() {
  const navigate = useNavigate();
  const { floor, completeFloor, startArena, setPhase } = useRunStore();
  const { activeCampaignId } = useCampaignStore();
  const { goldBalance, fetchBalance } = useEconomyStore();

  const [items, setItems] = useState<ShopItem[]>([]);
  const [purchased, setPurchased] = useState<Set<string>>(new Set());
  const [buying, setBuying] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [merchantLine, setMerchantLine] = useState("");

  const greeting = useMemo(() => pickRandom(MERCHANT_GREETINGS), []);

  useEffect(() => {
    async function loadShop() {
      if (!floor) return;
      try {
        const result = await rewardsApi.checkShop(floor.id, floor.floor_number);
        if (result.shop_available && result.inventory) {
          setItems(result.inventory as ShopItem[]);
        }
      } catch {
        // API error — show empty shop
      } finally {
        setLoading(false);
      }
    }
    loadShop();
  }, [floor]);

  useEffect(() => {
    if (activeCampaignId) {
      fetchBalance(activeCampaignId);
    }
  }, [activeCampaignId, fetchBalance]);

  const handleBuy = async (item: ShopItem) => {
    if (!floor || goldBalance < item.price || purchased.has(item.id)) return;
    setBuying(item.id);

    try {
      await rewardsApi.purchaseItem(floor.id, {
        item_id: item.id,
        item_name: item.name,
        item_rarity: item.rarity,
        item_type: item.type,
        price: item.price,
      });
      setPurchased((prev) => new Set(prev).add(item.id));
      setMerchantLine(pickRandom(MERCHANT_PURCHASE));
    } catch {
      useToastStore.getState().addToast("Purchase failed. Try again.", "error");
    }
    setBuying(null);

    if (activeCampaignId) {
      await fetchBalance(activeCampaignId);
    }
  };

  const handleLeaveShop = async () => {
    if (!floor) return;

    const completed = floor.arenas_completed + 1;
    if (completed >= floor.arena_count) {
      await completeFloor();
      navigate("/run/floor-transition");
    } else {
      await startArena();
      setPhase("encounter-brief");
      navigate("/run/encounter");
    }
  };

  if (!floor) {
    return <div className="py-8 text-center text-gray-400">No active floor data.</div>;
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <PageHeader
        title="Wandering Merchant"
        subtitle={`Floor ${floor.floor_number} — Browse wares`}
        action={
          <Card padding="sm" className="flex items-center gap-2">
            <Coins size={16} className="text-gold" />
            <span className="text-lg font-bold text-gold">{goldBalance}</span>
          </Card>
        }
      />

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <Card padding="md" className="text-center">
          <ShoppingBag size={24} className="mx-auto text-accent mb-2" />
          <TypewriterText
            text={`"${greeting}"`}
            speed={30}
            delay={200}
            className="text-sm text-gray-400 italic font-display"
            cursorColor="bg-accent"
          />
          <p className="text-[11px] text-accent mt-2">— The Merchant</p>
        </Card>
      </motion.div>

      {/* Merchant reaction to browsing/buying */}
      <AnimatePresence>
        {merchantLine && (
          <motion.div
            key={merchantLine}
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="text-center"
          >
            <p className="text-xs text-gray-500 italic font-display">"{merchantLine}"</p>
          </motion.div>
        )}
      </AnimatePresence>

      {loading ? (
        <LoadingState message="The merchant unpacks their wares..." />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {items.map((item, i) => {
              const config = getRarityConfig(item.rarity);
              const isBought = purchased.has(item.id);
              const canAfford = goldBalance >= item.price;
              const isBuying = buying === item.id;

              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.08 }}
                  onHoverStart={() => {
                    if (!isBought && !canAfford) {
                      setMerchantLine(pickRandom(MERCHANT_POOR));
                    } else if (!isBought) {
                      setMerchantLine(pickRandom(MERCHANT_BROWSE));
                    }
                  }}
                >
                  <Card
                    padding="none"
                    className={clsx(
                      "border-t-2 overflow-hidden",
                      config.border,
                      isBought ? "opacity-50" : ""
                    )}
                  >
                    <div className="p-5 space-y-3">
                      <div className="flex items-center justify-between">
                        <Badge color={(CATEGORY_BADGE[item.type] || "gray") as "emerald" | "gold" | "blue" | "purple" | "indigo" | "gray"}>
                          {item.type}
                        </Badge>
                        <span className={clsx("text-xs font-medium", config.text)}>
                          {config.label}
                        </span>
                      </div>

                      <div>
                        <h3 className="text-base font-display font-semibold text-white">{item.name}</h3>
                        <p className="text-sm text-gray-400 mt-1 leading-relaxed">{item.description}</p>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-surface-3">
                        <div className="flex items-center gap-1.5">
                          <Coins size={14} className="text-gold" />
                          <span className="text-lg font-bold text-gold">{item.price}</span>
                        </div>
                        <Button
                          variant={isBought ? "ghost" : canAfford ? "primary" : "ghost"}
                          size="sm"
                          icon={isBought ? <Check size={14} /> : undefined}
                          onClick={() => handleBuy(item)}
                          loading={isBuying}
                          disabled={isBought || !canAfford || isBuying}
                        >
                          {isBought ? "Purchased" : !canAfford ? "Can't Afford" : "Buy"}
                        </Button>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              );
            })}
          </div>

          <Button
            variant="secondary"
            size="lg"
            icon={<ArrowRight size={16} />}
            onClick={handleLeaveShop}
            className="w-full"
          >
            Leave Shop
          </Button>
        </>
      )}
    </div>
  );
}
