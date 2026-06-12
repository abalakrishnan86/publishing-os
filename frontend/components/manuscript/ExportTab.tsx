import { exportJsonUrl, exportPdfUrl } from "@/lib/api";
import type { AnalysisResult, MarketingResult, MetadataResult } from "@/lib/types";

export default function ExportTab({
  manuscriptId,
  analysis,
  metadata,
  marketing,
}: {
  manuscriptId: number;
  analysis: AnalysisResult | null;
  metadata: MetadataResult | null;
  marketing: MarketingResult | null;
}) {
  const allGenerated = analysis && metadata && marketing;
  const missing = [
    !analysis && "Analysis",
    !metadata && "Metadata",
    !marketing && "Marketing",
  ].filter(Boolean);

  return (
    <div className="max-w-md mx-auto py-6">
      {!allGenerated && (
        <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          Generate the following sections first to include them in the report:{" "}
          <strong>{missing.join(", ")}</strong>.
        </div>
      )}

      <div className="space-y-4">
        <a
          href={exportJsonUrl(manuscriptId)}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-4 rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-gray-100 text-2xl">
            📋
          </div>
          <div>
            <p className="font-semibold text-gray-900">Download JSON Report</p>
            <p className="text-xs text-gray-500">All results in a structured JSON file</p>
          </div>
        </a>

        <a
          href={exportPdfUrl(manuscriptId)}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-4 rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-red-50 text-2xl">
            📄
          </div>
          <div>
            <p className="font-semibold text-gray-900">Download PDF Report</p>
            <p className="text-xs text-gray-500">Formatted report ready to share</p>
          </div>
        </a>
      </div>
    </div>
  );
}
