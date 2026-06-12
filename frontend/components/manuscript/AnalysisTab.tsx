"use client";

import { useState } from "react";
import { runAnalysis } from "@/lib/api";
import type { AnalysisResult } from "@/lib/types";

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
      <p className="text-sm text-gray-800 leading-relaxed">{value}</p>
    </div>
  );
}

function Tags({ label, items }: { label: string; items: string[] | null | undefined }) {
  if (!items?.length) return null;
  return (
    <div className="mb-4">
      <span className="text-xs font-semibold uppercase tracking-wide text-gray-500 block mb-2">{label}</span>
      <div className="flex flex-wrap gap-2">
        {items.map((item, i) => (
          <span key={i} className="rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs text-indigo-700">{item}</span>
        ))}
      </div>
    </div>
  );
}

function BulletList({ label, items, color }: { label: string; items: string[] | null | undefined; color: string }) {
  if (!items?.length) return null;
  return (
    <div className="mb-4">
      <span className="text-xs font-semibold uppercase tracking-wide text-gray-500 block mb-2">{label}</span>
      <ul className="space-y-1">
        {items.map((item, i) => (
          <li key={i} className={`flex items-start gap-2 text-sm text-gray-800`}>
            <span className={`mt-1 h-1.5 w-1.5 rounded-full shrink-0 ${color}`} />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function AnalysisTab({
  manuscriptId,
  initial,
}: {
  manuscriptId: number;
  initial: AnalysisResult | null;
}) {
  const [result, setResult] = useState<AnalysisResult | null>(initial);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setLoading(true);
    setError(null);
    try {
      const data = await runAnalysis(manuscriptId);
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
        <p className="text-gray-500 mb-4">No analysis yet. Generate one using Claude AI.</p>
        {error && <p className="text-sm text-red-600 mb-3">{error}</p>}
        <button
          onClick={generate}
          disabled={loading}
          className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          {loading ? "Analyzing with Claude…" : "Generate Analysis"}
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
      <Field label="Genre" value={result.genre} />
      <Field label="Writing Style" value={result.writing_style} />
      <Field label="Target Audience" value={result.target_audience} />
      <Field label="Readability Score" value={result.readability_score} />
      <Tags label="Themes" items={result.themes} />
      <BulletList label="Strengths" items={result.strengths} color="bg-green-500" />
      <BulletList label="Areas for Improvement" items={result.weaknesses} color="bg-amber-500" />
    </div>
  );
}
