import { useState } from "react";
import { motion } from "framer-motion";
import { BookOpen, Copy, Check, Pencil } from "lucide-react";
import { Card } from "@/components/ui";

interface ReadAloudBlockProps {
  text: string;
  editable?: boolean;
  onEdit?: (newText: string) => void;
}

export function ReadAloudBlock({ text, editable = false, onEdit }: ReadAloudBlockProps) {
  const [copied, setCopied] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editText, setEditText] = useState(text);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSave = () => {
    onEdit?.(editText);
    setEditing(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card padding="lg" className="border-amber-500/20 bg-amber-950/10 relative">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2 text-amber-400">
            <BookOpen size={16} />
            <span className="text-xs font-semibold uppercase tracking-wider">Read Aloud</span>
          </div>
          <div className="flex items-center gap-1">
            {editable && !editing && (
              <button
                onClick={() => setEditing(true)}
                className="p-1.5 rounded text-gray-500 hover:text-amber-400 transition-colors"
                title="Edit"
              >
                <Pencil size={14} />
              </button>
            )}
            <button
              onClick={handleCopy}
              className="p-1.5 rounded text-gray-500 hover:text-amber-400 transition-colors"
              title="Copy to clipboard"
            >
              {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
            </button>
          </div>
        </div>

        {editing ? (
          <div className="space-y-2">
            <textarea
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              className="w-full bg-surface-2 text-gray-200 rounded-lg p-3 text-base leading-relaxed resize-none min-h-[120px] focus:outline-none focus:ring-1 focus:ring-amber-500/40 font-serif italic"
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setEditing(false)}
                className="text-xs text-gray-500 hover:text-gray-300 px-3 py-1"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="text-xs bg-amber-600/20 text-amber-400 hover:bg-amber-600/30 px-3 py-1 rounded"
              >
                Save
              </button>
            </div>
          </div>
        ) : (
          <div className="font-serif text-lg text-gray-200 leading-relaxed italic whitespace-pre-line">
            {text}
          </div>
        )}
      </Card>
    </motion.div>
  );
}
