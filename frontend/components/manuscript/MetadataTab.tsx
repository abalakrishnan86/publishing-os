"use client";

import { useState } from "react";
import { runMetadata } from "@/lib/api";
import type { MetadataResult } from "@/lib/types";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
      className="text-xs text-gray-400 hover:text-indigo-600 transition-colors"
    >
      {copied ? "Copied!" : "Copy"}
    </button>
  );
}

function Field({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value) return null;
  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-semibold uppercase tracking-wide text-gray-500">{label}</span>
        <CopyButton text={value} />
      </div>
      <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">{value}</p>
    </div>
  );
}

export default function MetadataTab({
  manuscriptId,
  initial,
}: {
  manuscriptId: number;
  initial: MetadataResult | null;
}) {
  const [result, setResult] = useState<MetadataResult | null>(initial);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const data = await runMetadata(manuscriptId);
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
        <p className="text-gray-500 mb-4">No metadata yet. Generate publishing metadata with Claude AI.</p>
        {error && <p className="text-sm text-red-600 mb-3">{error}</p>}
        <button
          onClick={generate}
          disabled={loading}
          className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {loading ? "Generating with Claude…" : "Generate Metadata"}
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

      {result.title_suggestions && result.title_suggestions.length > 0 && (
        <div className="mb-4">
          <span className="text-xs font-semibold uppercase tracking-wide text-gray-500 block mb-2">Title Suggestions</span>
          <ol className="space-y-1">
            {result.title_suggestions.map((t, i) => (
              <li key={i} className="flex items-center justify-between rounded-lg border border-gray-100 bg-gray-50 px-3 py-2 text-sm text-gray-800">
                <span>{t}</span>
                <CopyButton text={t} />
              </li>
            ))}
          </ol>
        </div>
      )}

      <Field label="Subtitle" value={result.subtitle} />
      <Field label="Description" value={result.description} />

      {result.keywords && result.keywords.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold uppercase tracking-wide text-gray-500">Keywords</span>
            <CopyButton text={result.keywords.join(", ")} />
          </div>
          <div className="flex flex-wrap gap-2">
            {result.keywords.map((k, i) => (
              <span key={i} className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs text-indigo-700">{k}</span>
            ))}
          </div>
        </div>
      )}

      {result.bisac_categories && result.bisac_categories.length > 0 && (
        <div className="mb-4">
          <span className="text-xs font-semibold uppercase tracking-wide text-gray-500 block mb-2">BISAC Categories</span>
          <ul className="space-y-1">
            {result.bisac_categories.map((cat, i) => (
              <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-indigo-400 shrink-0" />
                {cat}
              </li>
            ))}
          </ul>
        </div>
      )}

      <Field label="Author Bio Prompt" value={result.author_bio_prompt} />
    </div>
  );
}
