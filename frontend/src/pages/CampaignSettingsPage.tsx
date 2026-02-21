import { useEffect, useState } from "react";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { campaignsApi } from "@/api/campaigns";
import { Button, Card, PageHeader, Select } from "@/components/ui";
import { DEFAULT_SETTINGS, PRESETS, SETTING_META, ENVIRONMENTS, type CampaignSettings } from "@/constants/campaignSettings";
import { Save, RotateCcw, Heart, Shield, Sword, Skull } from "lucide-react";
import { clsx } from "clsx";

const PRESET_ICONS = [Heart, Shield, Sword, Skull];
const CATEGORY_LABELS: Record<string, string> = {
  balance: "Combat & Difficulty",
  economy: "Progression & Economy",
  other: "Miscellaneous",
};

export function CampaignSettingsPage() {
  const { activeCampaignId, campaigns } = useCampaignStore();
  const campaign = campaigns.find((c) => c.id === activeCampaignId);

  const [settings, setSettings] = useState<CampaignSettings>(DEFAULT_SETTINGS);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (campaign?.settings) {
      setSettings({ ...DEFAULT_SETTINGS, ...(campaign.settings as Partial<CampaignSettings>) });
    }
  }, [campaign]);

  if (!activeCampaignId || !campaign) {
    return <div className="text-gray-400">Select a campaign first.</div>;
  }

  const handleChange = (key: keyof CampaignSettings, value: number | string | null) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  };

  const applyPreset = (presetIndex: number) => {
    const preset = PRESETS[presetIndex];
    if (!preset) return;
    setSettings({ ...DEFAULT_SETTINGS, ...preset.settings });
    setSaved(false);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await campaignsApi.update(activeCampaignId, { settings });
      setSaved(true);
    } finally {
      setSaving(false);
    }
  };

  const categories = ["balance", "economy", "other"] as const;

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <PageHeader
        title="Campaign Settings"
        subtitle={campaign.name}
      />

      {/* Quick preset selection */}
      <Card padding="lg">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">Quick Presets</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {PRESETS.map((preset, i) => {
            const Icon = PRESET_ICONS[i]!;
            const isActive = settings.balance_preset === preset.preset;
            return (
              <button
                key={preset.preset}
                onClick={() => applyPreset(i)}
                className={clsx(
                  "rounded-lg border p-3 text-center transition-all cursor-pointer",
                  isActive
                    ? "border-accent bg-accent/10 text-white"
                    : "border-surface-3 bg-surface-1 text-gray-400 hover:border-surface-4 hover:text-gray-300",
                )}
              >
                <Icon size={20} className={clsx("mx-auto mb-1", isActive && "text-accent")} />
                <div className="text-xs font-semibold">{preset.name}</div>
              </button>
            );
          })}
        </div>
      </Card>

      {/* Settings grouped by category */}
      {categories.map((cat) => {
        const catSettings = SETTING_META.filter((m) => m.category === cat);
        if (catSettings.length === 0) return null;
        return (
          <Card key={cat} padding="lg">
            <h3 className="text-sm font-semibold text-gray-300 mb-4">{CATEGORY_LABELS[cat]}</h3>
            <div className="space-y-6">
              {catSettings.map((meta) => {
                const value = settings[meta.key] as number;
                return (
                  <div key={meta.key}>
                    <div className="flex justify-between items-center mb-1">
                      <label className="text-sm font-medium text-gray-300">{meta.label}</label>
                      <span className="text-sm font-mono text-accent">{meta.format(value)}</span>
                    </div>
                    <p className="text-xs text-gray-500 mb-2">{meta.description}</p>
                    <input
                      type="range"
                      min={meta.min}
                      max={meta.max}
                      step={meta.step}
                      value={value}
                      onChange={(e) => handleChange(meta.key, parseFloat(e.target.value))}
                      className="w-full accent-[var(--color-accent)]"
                    />
                    <div className="flex justify-between text-xs text-gray-600 mt-1">
                      <span>{meta.format(meta.min)}</span>
                      <span>{meta.format(meta.max)}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        );
      })}

      {/* Environment preference */}
      <Card padding="lg">
        <Select
          label="Environment Preference"
          description="Lock encounters to a specific environment, or leave on auto for variety."
          value={settings.environment_preference || ""}
          onChange={(e) => handleChange("environment_preference", e.target.value || null)}
        >
          {ENVIRONMENTS.map((env) => (
            <option key={env.key} value={env.key}>{env.label}</option>
          ))}
        </Select>
      </Card>

      {/* Actions */}
      <div className="flex gap-3">
        <Button
          variant="primary"
          size="lg"
          icon={<Save size={16} />}
          onClick={handleSave}
          loading={saving}
          className="flex-1"
        >
          {saved ? "Saved" : "Save Settings"}
        </Button>
        <Button
          variant="secondary"
          size="lg"
          icon={<RotateCcw size={16} />}
          onClick={() => { setSettings(DEFAULT_SETTINGS); setSaved(false); }}
        >
          Reset
        </Button>
      </div>
    </div>
  );
}
