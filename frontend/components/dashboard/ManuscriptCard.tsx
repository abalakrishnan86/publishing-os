import Link from "next/link";
import type { Manuscript } from "@/lib/types";
import StatusBadge from "@/components/StatusBadge";

const FILE_TYPE_STYLES: Record<string, string> = {
  docx: "bg-blue-50 text-blue-700",
  pdf: "bg-red-50 text-red-700",
  txt: "bg-gray-50 text-gray-700",
};

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function ManuscriptCard({ manuscript }: { manuscript: Manuscript }) {
  const ftStyle = FILE_TYPE_STYLES[manuscript.file_type] ?? "bg-gray-50 text-gray-700";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate font-semibold text-gray-900">{manuscript.title}</h3>
          <div className="mt-1.5 flex flex-wrap items-center gap-2">
            <span className={`rounded px-1.5 py-0.5 text-xs font-medium uppercase ${ftStyle}`}>
              {manuscript.file_type}
            </span>
            <StatusBadge status={manuscript.status} />
            {manuscript.word_count != null && (
              <span className="text-xs text-gray-400">{manuscript.word_count.toLocaleString()} words</span>
            )}
          </div>
        </div>
        <span className="shrink-0 text-xs text-gray-400">{timeAgo(manuscript.created_at)}</span>
      </div>

      <div className="mt-4">
        <Link
          href={`/manuscript/${manuscript.id}`}
          className="inline-block rounded-lg bg-indigo-600 px-4 py-1.5 text-xs font-semibold text-white
            hover:bg-indigo-700 transition-colors"
        >
          View Results →
        </Link>
      </div>
    </div>
  );
}
