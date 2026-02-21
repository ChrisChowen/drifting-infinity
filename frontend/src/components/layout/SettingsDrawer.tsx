import { useEffect, useState } from "react";
import { useCampaignStore } from "@/stores/useCampaignStore";
import { campaignsApi } from "@/api/campaigns";
import { Button } from "@/components/ui";
import { DEFAULT_SETTINGS, SETTING_META, type CampaignSettings } from "@/constants/campaignSettings";
import { X, Save } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface SettingsDrawerProps {
  open: boolean;
  onClose: () => void;
}

export function SettingsDrawer({ open, onClose }: SettingsDrawerProps) {
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

  const handleChange = (key: keyof CampaignSettings, value: number) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  };

  const handleSave = async () => {
    if (!activeCampaignId) return;
    setSaving(true);
    try {
      await campaignsApi.update(activeCampaignId, { settings });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally {
      setSaving(false);
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40"
            onClick={onClose}
          />

          {/* Drawer */}
          <motion.aside
            role="dialog"
            aria-modal="true"
            aria-label="Campaign Settings"
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 250 }}
            className="fixed right-0 top-0 bottom-0 w-80 bg-surface-1 border-l border-surface-3 z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-surface-3">
              <h2 className="font-display font-semibold text-white text-sm">Campaign Settings</h2>
              <button
                className="p-1.5 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-surface-2 transition-colors"
                onClick={onClose}
                aria-label="Close settings"
              >
                <X size={18} />
              </button>
            </div>

            {/* Sliders */}
            <div className="flex-1 overflow-y-auto p-4 space-y-5">
              {!activeCampaignId ? (
                <p className="text-sm text-gray-500">No active campaign.</p>
              ) : (
                SETTING_META.map((meta) => {
                  const value = settings[meta.key] as number;
                  return (
                    <div key={meta.key}>
                      <div className="flex justify-between items-center mb-1">
                        <label htmlFor={`setting-${meta.key}`} className="text-xs font-medium text-gray-300">{meta.label}</label>
                        <span className="text-xs font-mono text-accent">{meta.format(value)}</span>
                      </div>
                      <input
                        id={`setting-${meta.key}`}
                        type="range"
                        min={meta.min}
                        max={meta.max}
                        step={meta.step}
                        value={value}
                        onChange={(e) => handleChange(meta.key, parseFloat(e.target.value))}
                        className="w-full accent-[var(--color-accent)]"
                        aria-label={meta.label}
                      />
                      <div className="flex justify-between text-[10px] text-gray-600 mt-0.5">
                        <span>{meta.format(meta.min)}</span>
                        <span>{meta.format(meta.max)}</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Save button */}
            {activeCampaignId && (
              <div className="px-4 py-3 border-t border-surface-3">
                <Button
                  variant="primary"
                  size="sm"
                  icon={<Save size={14} />}
                  onClick={handleSave}
                  loading={saving}
                  className="w-full"
                >
                  {saved ? "Saved" : "Save Settings"}
                </Button>
              </div>
            )}
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
