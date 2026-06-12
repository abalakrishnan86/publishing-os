"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getAnalysis, getManuscript, getMarketing, getMetadata } from "@/lib/api";
import type { AnalysisResult, Manuscript, MarketingResult, MetadataResult } from "@/lib/types";
import StatusBadge from "@/components/StatusBadge";
import AnalysisTab from "@/components/manuscript/AnalysisTab";
import MetadataTab from "@/components/manuscript/MetadataTab";
import MarketingTab from "@/components/manuscript/MarketingTab";
import ExportTab from "@/components/manuscript/ExportTab";

type Tab = "analysis" | "metadata" | "marketing" | "export";

const TABS: { id: Tab; label: string }[] = [
  { id: "analysis", label: "Analysis" },
  { id: "metadata", label: "Metadata" },
  { id: "marketing", label: "Marketing" },
  { id: "export", label: "Export" },
];

export default function ManuscriptPage() {
  const { id } = useParams<{ id: string }>();
  const manuscriptId = Number(id);

  const [manuscript, setManuscript] = useState<Manuscript | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [metadata, setMetadata] = useState<MetadataResult | null>(null);
  const [marketing, setMarketing] = useState<MarketingResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<Tab>("analysis");

  useEffect(() => {
    async function load() {
      const [m, a, meta, mkt] = await Promise.all([
        getManuscript(manuscriptId),
        getAnalysis(manuscriptId).catch(() => null),
        getMetadata(manuscriptId).catch(() => null),
        getMarketing(manuscriptId).catch(() => null),
      ]);
      setManuscript(m);
      setAnalysis(a);
      setMetadata(meta);
      setMarketing(mkt);
      setLoading(false);
    }
    load();
  }, [manuscriptId]);

  if (loading) {
    return <div className="py-20 text-center text-gray-400">Loading…</div>;
  }

  if (!manuscript) {
    return (
      <div className="py-20 text-center">
        <p className="text-gray-600 mb-4">Manuscript not found.</p>
        <Link href="/dashboard" className="text-indigo-600 hover:underline">← Back to Dashboard</Link>
      </div>
    );
  }

  const isReady = manuscript.status === "completed";

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <Link href="/dashboard" className="text-sm text-gray-400 hover:text-indigo-600 transition-colors">
          ← Dashboard
        </Link>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-bold text-gray-900">{manuscript.title}</h1>
          <StatusBadge status={manuscript.status} />
          <span className="text-xs text-gray-400 uppercase">{manuscript.file_type}</span>
          {manuscript.word_count != null && (
            <span className="text-xs text-gray-400">{manuscript.word_count.toLocaleString()} words</span>
          )}
        </div>
      </div>

      {!isReady && (
        <div className="mb-6 rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
          Manuscript is still being processed. Check back shortly.
        </div>
      )}

      {/* Tab bar */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-1">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              disabled={!isReady && tab.id !== "export"}
              className={`
                px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px
                ${activeTab === tab.id
                  ? "border-indigo-600 text-indigo-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"}
                disabled:opacity-40 disabled:cursor-not-allowed
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab content */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        {activeTab === "analysis" && (
          <AnalysisTab manuscriptId={manuscriptId} initial={analysis} />
        )}
        {activeTab === "metadata" && (
          <MetadataTab manuscriptId={manuscriptId} initial={metadata} />
        )}
        {activeTab === "marketing" && (
          <MarketingTab manuscriptId={manuscriptId} initial={marketing} />
        )}
        {activeTab === "export" && (
          <ExportTab
            manuscriptId={manuscriptId}
            analysis={analysis}
            metadata={metadata}
            marketing={marketing}
          />
        )}
      </div>
    </div>
  );
}
