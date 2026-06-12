"use client";

import { useState } from "react";
import { runMarketing } from "@/lib/api";
import type { MarketingResult } from "@/lib/types";

function CopyField({ label, value }: { label: string; value: string | null | undefined }) {
  const [copied, setCopied] = useState(false);
  if (!value) return null;
  return (
    <div className="mb-5">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-semibold uppercase tracking-wide text-gray-500">{label}</span>
        <button
          onClick={() => { navigator.clipboard.writeText(value); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
          className="text-xs text-gray-400 hover:text-indigo-600 transition-colors"
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-3 text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
        {value}
      </div>
    </div>
  );
}

export default function MarketingTab({
  manuscriptId,
  initial,
}: {
  manuscriptId: number;
  initial: MarketingResult | null;
}) {
  const [result, setResult] = useState<MarketingResult | null>(initial);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const data = await runMarketing(manuscriptId);
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setLoading(false);
    }
  }

  if (!result) {
    return (
      <div className="flex flex-col items-center py-12 text-center">
        <p className="text-gray-500 mb-4">No marketing content yet. Generate it with Claude AI.</p>
        {error && <p className="text-sm text-red-600 mb-3">{error}</p>}
        <button
          onClick={generate}
          disabled={loading}
          className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {loading ? "Generating with Claude…" : "Generate Marketing Content"}
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-end mb-4">
        <button onClick={generate} disabled={loading} className="text-xs text-gray-400 hover:text-indigo-600 transition-colors disabled:opacity-50">
          {loading ? "Regenerating…" : "↺ Regenerate"}
        </button>
      </div>
      <CopyField label="Elevator Pitch" value={result.elevator_pitch} />
      <CopyField label="Back Cover Blurb" value={result.back_cover_blurb} />
      <CopyField label="Amazon Description" value={result.amazon_description} />
      <CopyField label="Twitter Post" value={result.twitter_post} />
      <CopyField label="LinkedIn Post" value={result.linkedin_post} />
      <CopyField label="Instagram Post" value={result.instagram_post} />
      <CopyField label="Press Release Excerpt" value={result.press_release_excerpt} />
    </div>
  );
}
