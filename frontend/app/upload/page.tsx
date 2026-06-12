import DropZone from "@/components/upload/DropZone";
import Link from "next/link";

export default function UploadPage() {
  return (
    <div className="flex flex-col items-center pt-12">
      <div className="text-center mb-10">
        <Link href="/dashboard" className="text-sm text-gray-400 hover:text-indigo-600 transition-colors">
          ← Back to Dashboard
        </Link>
        <h1 className="mt-4 text-3xl font-bold text-gray-900">Upload Manuscript</h1>
        <p className="mt-2 text-gray-500 max-w-md mx-auto">
          Upload a DOCX, PDF, or TXT file. Claude AI will analyze it and generate
          publishing metadata and marketing content.
        </p>
      </div>
      <DropZone />
    </div>
  );
}
