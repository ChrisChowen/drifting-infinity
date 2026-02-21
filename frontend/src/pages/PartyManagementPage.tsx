import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { campaignsApi } from "@/api/campaigns";
import { Button, Card, Badge, ProgressBar, PageHeader, EmptyState, ConfirmModal } from "@/components/ui";
import { useConfirm } from "@/hooks/useConfirm";
import { UserPlus, Trash2, ArrowUp, Users } from "lucide-react";

export function PartyManagementPage() {
  const navigate = useNavigate();
  const { activeCampaignId, characters, fetchCharacters, removeCharacter } = useCampaignStore();
  const [levelUpCharId, setLevelUpCharId] = useState<string | null>(null);
  const [levelUpForm, setLevelUpForm] = useState({ new_max_hp: 0, new_ac: 0 });
  const [levelUpLoading, setLevelUpLoading] = useState(false);
  const { confirm, modalProps } = useConfirm();

  useEffect(() => {
    if (activeCampaignId) fetchCharacters();
  }, [activeCampaignId, fetchCharacters]);

  const handleStartLevelUp = (charId: string, currentHp: number, currentAc: number) => {
    setLevelUpCharId(charId);
    setLevelUpForm({ new_max_hp: currentHp, new_ac: currentAc });
  };

  const handleLevelUp = async () => {
    if (!activeCampaignId || !levelUpCharId) return;
    setLevelUpLoading(true);
    try {
      await campaignsApi.levelUp(activeCampaignId, levelUpCharId, levelUpForm);
      await fetchCharacters();
      setLevelUpCharId(null);
    } catch (e) {
      console.error("Level up failed:", e);
    } finally {
      setLevelUpLoading(false);
    }
  };

  if (!activeCampaignId) {
    return (
      <EmptyState
        icon={<Users size={48} />}
        title="No Campaign Selected"
        description="Select or create a campaign from the Lobby first."
        action={<Button onClick={() => navigate("/")}>Go to Lobby</Button>}
      />
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="Your Party"
        subtitle={`${characters.length} adventurer${characters.length !== 1 ? "s" : ""} ready for battle`}
        action={
          <Button
            variant="primary"
            icon={<UserPlus size={16} />}
            onClick={() => navigate("/party/add")}
          >
            Add Character
          </Button>
        }
      />

      {/* Character List */}
      {characters.length === 0 ? (
        <EmptyState
          icon={<Users size={48} />}
          title="Your Party Awaits"
          description="Add your first character to begin forging a legend in the Armillary."
          action={
            <Button icon={<UserPlus size={16} />} onClick={() => navigate("/party/add")}>
              Add Character
            </Button>
          }
        />
      ) : (
        <section className="space-y-3">
          {characters.map((c) => {
            const xpPercent = c.xp_to_next_level > 0
              ? Math.min(100, Math.round((c.xp_total / c.xp_to_next_level) * 100))
              : 100;
            const canLevelUp = c.xp_total >= c.xp_to_next_level && c.level < 20;

            return (
              <Card key={c.id} padding="md">
                <div className="space-y-3">
                  {/* Header Row */}
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-display font-semibold text-white">{c.name}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge color="gold">Lv {c.level}</Badge>
                        <span className="text-sm text-gray-400">
                          {c.character_class}{c.subclass ? ` (${c.subclass})` : ""}
                        </span>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={<Trash2 size={14} />}
                      className="text-gray-500 hover:text-red-400"
                      onClick={async () => {
                        const ok = await confirm({
                          title: `Remove ${c.name}?`,
                          description: `This will permanently remove ${c.name} from your party. This cannot be undone.`,
                          confirmLabel: "Remove",
                          variant: "danger",
                        });
                        if (ok) removeCharacter(c.id);
                      }}
                    />
                  </div>

                  {/* Stats Row */}
                  <div className="flex gap-4 text-sm">
                    <div className="text-center">
                      <div className="font-bold text-white">{c.ac}</div>
                      <div className="text-xs text-gray-500">AC</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-hp-full">{c.max_hp}</div>
                      <div className="text-xs text-gray-500">HP</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-white">{c.speed}ft</div>
                      <div className="text-xs text-gray-500">Speed</div>
                    </div>
                    {(c.damage_types || []).length > 0 && (
                      <div className="flex items-center gap-1 flex-wrap ml-2">
                        {(c.damage_types || []).map((dt) => (
                          <span key={dt} className="text-xs bg-surface-2 text-gray-400 px-1.5 py-0.5 rounded capitalize">{dt}</span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* XP Progress */}
                  <ProgressBar
                    value={c.xp_total}
                    max={c.xp_to_next_level}
                    label={`XP: ${c.xp_total} / ${c.xp_to_next_level}`}
                    sublabel={`${xpPercent}%`}
                    color="green"
                    size="sm"
                  />

                  {/* Level Up */}
                  {canLevelUp && levelUpCharId !== c.id && (
                    <Button
                      variant="success"
                      size="sm"
                      icon={<ArrowUp size={14} />}
                      onClick={() => handleStartLevelUp(c.id, c.max_hp, c.ac)}
                    >
                      Level Up to {c.level + 1}
                    </Button>
                  )}

                  {/* Inline Level Up Form */}
                  {levelUpCharId === c.id && (
                    <Card padding="sm" className="bg-surface-2 border-surface-3">
                      <div className="space-y-3">
                        <h4 className="text-sm font-display font-semibold text-accent">Level Up to {c.level + 1}</h4>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="block text-xs text-gray-400 mb-1">New Max HP</label>
                            <input
                              type="number" min={1}
                              className="w-full bg-surface-1 text-white px-3 py-2 rounded-lg border border-surface-3 focus:outline-none focus:ring-2 focus:ring-accent/40"
                              value={levelUpForm.new_max_hp}
                              onChange={(e) => setLevelUpForm({ ...levelUpForm, new_max_hp: +e.target.value })}
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-400 mb-1">New AC</label>
                            <input
                              type="number" min={1} max={30}
                              className="w-full bg-surface-1 text-white px-3 py-2 rounded-lg border border-surface-3 focus:outline-none focus:ring-2 focus:ring-accent/40"
                              value={levelUpForm.new_ac}
                              onChange={(e) => setLevelUpForm({ ...levelUpForm, new_ac: +e.target.value })}
                            />
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant="success"
                            size="sm"
                            onClick={handleLevelUp}
                            loading={levelUpLoading}
                          >
                            Confirm Level Up
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setLevelUpCharId(null)}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    </Card>
                  )}
                </div>
              </Card>
            );
          })}
        </section>
      )}
      <ConfirmModal {...modalProps} />
    </div>
  );
}
