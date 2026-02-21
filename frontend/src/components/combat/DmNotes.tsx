import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { StickyNote, ChevronDown, ChevronUp } from "lucide-react";

interface DmNotesProps {
  arenaId: string | null;
}

const STORAGE_PREFIX = "dm-notes-";

export function DmNotes({ arenaId }: DmNotesProps) {
  const [collapsed, setCollapsed] = useState(true);
  const [notes, setNotes] = useState("");

  const storageKey = arenaId ? `${STORAGE_PREFIX}${arenaId}` : null;

  // Load notes from localStorage
  useEffect(() => {
    if (!storageKey) return;
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) setNotes(saved);
      else setNotes("");
    } catch {
      setNotes("");
    }
  }, [storageKey]);

  // Save notes to localStorage
  const handleChange = useCallback(
    (value: string) => {
      setNotes(value);
      if (storageKey) {
        try {
          localStorage.setItem(storageKey, value);
        } catch {
          // Storage full, ignore
        }
      }
    },
    [storageKey],
  );

  return (
    <div className="bg-surface-1 rounded-lg border border-surface-3">
      <button
        className="w-full flex items-center justify-between px-3 py-2 text-sm"
        onClick={() => setCollapsed(!collapsed)}
      >
        <div className="flex items-center gap-2 text-gray-400">
          <StickyNote size={14} />
          <span className="font-medium">DM Notes</span>
          {notes.length > 0 && (
            <span className="text-[10px] text-gray-500">({notes.length} chars)</span>
          )}
        </div>
        {collapsed ? <ChevronDown size={14} className="text-gray-500" /> : <ChevronUp size={14} className="text-gray-500" />}
      </button>

      {!collapsed && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          className="border-t border-surface-3 overflow-hidden"
        >
          <textarea
            value={notes}
            onChange={(e) => handleChange(e.target.value)}
            placeholder="Jot down notes for this encounter..."
            className="w-full bg-transparent text-sm text-gray-300 p-3 resize-none h-32 focus:outline-none placeholder-gray-600"
          />
        </motion.div>
      )}
    </div>
  );
}
