"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listManuscripts } from "@/lib/api";
import type { Manuscript } from "@/lib/types";
import ManuscriptCard from "@/components/dashboard/ManuscriptCard";

const POLL_INTERVAL_MS = 10_000;

function isProcessing(m: Manuscript) {
  return m.status === "uploaded" || m.status === "extracting";
}

export default function DashboardPage() {
  const [manuscripts, setManuscripts] = useState<Manuscript[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function fetchManuscripts() {
    try {
      const data = await listManuscripts();
      setManuscripts(data);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load manuscripts");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchManuscripts();
  }, []);

  useEffect(() => {
    if (manuscripts.some(isProcessing)) {
      const id = setInterval(fetchManuscripts, POLL_INTERVAL_MS);
      return () => clearInterval(id);
    }
  }, [manuscripts]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Your Manuscripts</h1>
        <Link
          href="/upload"
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 transition-colors"
        >
          + Upload New
        </Link>
      </div>

      {loading && (
        <div className="text-center py-16 text-gray-400">Loading…</div>
      )}

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {!loading && manuscripts.length === 0 && !error && (
        <div className="flex flex-col items-center py-20 text-center">
          <div className="text-5xl mb-4">📚</div>
          <p className="text-lg font-semibold text-gray-700">No manuscripts yet</p>
          <p className="text-sm text-gray-400 mt-1 mb-6">Upload your first manuscript to get started.</p>
          <Link
            href="/upload"
            className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 transition-colors"
          >
            Upload Manuscript
          </Link>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {manuscripts.map((m) => (
          <ManuscriptCard key={m.id} manuscript={m} />
        ))}
      </div>
    </div>
  );
}
