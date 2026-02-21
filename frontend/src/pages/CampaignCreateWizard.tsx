import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { WizardShell, type WizardStepConfig } from "@/components/wizard";
import { Card, Input } from "@/components/ui";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { campaignsApi } from "@/api/campaigns";
import { DEFAULT_SETTINGS, PRESETS, SETTING_META, type CampaignSettings } from "@/constants/campaignSettings";
import { clsx } from "clsx";
import { Sword, Shield, Heart, Skull, Check } from "lucide-react";

const PRESET_ICONS = [Heart, Shield, Sword, Skull];

export function CampaignCreateWizard() {
  const navigate = useNavigate();
  const { setActiveCampaign, fetchCampaigns } = useCampaignStore();
  const [loading, setLoading] = useState(false);

  const steps: WizardStepConfig[] = [
    {
      id: "name",
      title: "Name Your Campaign",
      subtitle: "This is the name your players will know this arena by",
      validate: (data) => !!((data.name as string)?.trim()),
      content: ({ data, onUpdate }) => (
        <div className="max-w-md mx-auto">
          <Input
            placeholder="e.g., The Shattered Armillary"
            value={(data.name as string) || ""}
            onChange={(e) => onUpdate({ name: e.target.value })}
            autoFocus
            className="text-center text-lg"
          />
        </div>
      ),
    },
    {
      id: "playstyle",
      title: "Choose a Playstyle",
      subtitle: "Pick a preset or customize your settings. You can always change these later.",
      skippable: true,
      content: ({ data, onUpdate }) => {
        const selectedPreset = (data.preset as string) ?? "standard";
        const showCustom = (data.showCustom as boolean) ?? false;
        const settings = { ...DEFAULT_SETTINGS, ...(data.settings as Partial<CampaignSettings> || {}) };

        return (
          <div className="space-y-6">
            {/* Preset Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {PRESETS.map((preset, i) => {
                const Icon = PRESET_ICONS[i]!;
                const isSelected = selectedPreset === preset.preset && !showCustom;
                return (
                  <Card
                    key={preset.name}
                    hover
                    selected={isSelected}
                    padding="md"
                    onClick={() => {
                      onUpdate({
                        preset: preset.preset,
                        presetName: preset.name,
                        settings: { ...DEFAULT_SETTINGS, ...preset.settings },
                        showCustom: false,
                      });
                    }}
                  >
                    <div className="text-center space-y-2">
                      <Icon size={24} className={clsx("mx-auto", isSelected ? "text-accent" : "text-gray-400")} />
                      <div className="font-display font-semibold text-white text-sm">{preset.name}</div>
                      <p className="text-xs text-gray-500">{preset.description}</p>
                    </div>
                  </Card>
                );
              })}
            </div>

            {/* Customize toggle */}
            <button
              className="text-sm text-accent hover:text-accent-bright transition-colors mx-auto block cursor-pointer"
              onClick={() => onUpdate({ showCustom: !showCustom })}
            >
              {showCustom ? "Hide Custom Settings" : "Customize Settings"}
            </button>

            {/* Custom sliders */}
            {showCustom && (
              <div className="space-y-5 bg-surface-1 rounded-xl p-5 border border-surface-3/50">
                {SETTING_META.map((meta) => {
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
                        onChange={(e) =>
                          onUpdate({ settings: { ...settings, [meta.key]: parseFloat(e.target.value) } })
                        }
                        className="w-full accent-[var(--color-accent)]"
                      />
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        );
      },
    },
    {
      id: "review",
      title: "Review Your Campaign",
      subtitle: "Everything look good? You can change settings anytime from the campaign menu.",
      content: ({ data }) => {
        const name = (data.name as string) || "Unnamed Campaign";
        const preset = (data.presetName as string) || "Standard";
        return (
          <Card padding="lg" glow className="max-w-sm mx-auto text-center space-y-4">
            <h3 className="text-xl font-display font-bold text-gradient-gold">{name}</h3>
            <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
              <Check size={16} className="text-emerald-400" />
              <span>{preset} difficulty preset</span>
            </div>
            <p className="text-xs text-gray-500">
              After creation, you will add your party members.
            </p>
          </Card>
        );
      },
    },
  ];

  const handleComplete = async (data: Record<string, unknown>) => {
    setLoading(true);
    try {
      const name = (data.name as string).trim();
      const settings = (data.settings as CampaignSettings) || DEFAULT_SETTINGS;

      const campaign = await campaignsApi.create(name);
      await campaignsApi.update(campaign.id, { settings });
      await fetchCampaigns();
      await setActiveCampaign(campaign.id);
      navigate("/party");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-8">
      <WizardShell
        steps={steps}
        onComplete={handleComplete}
        completionLabel="Create Campaign"
        completionLoading={loading}
      />
    </div>
  );
}
