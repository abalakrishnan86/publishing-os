import type { AnalysisResult, Manuscript, MarketingResult, MetadataResult } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export async function uploadManuscript(file: File): Promise<Manuscript> {
  const form = new FormData();
  form.append("file", file);
  return req<Manuscript>("/manuscripts/upload", { method: "POST", body: form });
}

export async function listManuscripts(): Promise<Manuscript[]> {
  return req<Manuscript[]>("/manuscripts");
}

export async function getManuscript(id: number): Promise<Manuscript> {
  return req<Manuscript>(`/manuscripts/${id}`);
}

export async function deleteManuscript(id: number): Promise<void> {
  await req(`/manuscripts/${id}`, { method: "DELETE" });
}

export async function runAnalysis(id: number): Promise<AnalysisResult> {
  return req<AnalysisResult>(`/manuscripts/${id}/analysis`, { method: "POST" });
}

export async function getAnalysis(id: number): Promise<AnalysisResult> {
  return req<AnalysisResult>(`/manuscripts/${id}/analysis`);
}

export async function runMetadata(id: number): Promise<MetadataResult> {
  return req<MetadataResult>(`/manuscripts/${id}/metadata`, { method: "POST" });
}

export async function getMetadata(id: number): Promise<MetadataResult> {
  return req<MetadataResult>(`/manuscripts/${id}/metadata`);
}

export async function runMarketing(id: number): Promise<MarketingResult> {
  return req<MarketingResult>(`/manuscripts/${id}/marketing`, { method: "POST" });
}

export async function getMarketing(id: number): Promise<MarketingResult> {
  return req<MarketingResult>(`/manuscripts/${id}/marketing`);
}

export function exportJsonUrl(id: number): string {
  return `${BASE}/manuscripts/${id}/export/json`;
}

export function exportPdfUrl(id: number): string {
  return `${BASE}/manuscripts/${id}/export/pdf`;
}
