export interface Manuscript {
  id: number;
  title: string;
  filename: string;
  file_type: "docx" | "pdf" | "txt";
  status: "uploaded" | "extracting" | "completed" | "failed";
  word_count: number | null;
  created_at: string;
  updated_at: string;
}

export interface AnalysisResult {
  id: number;
  manuscript_id: number;
  genre: string | null;
  themes: string[] | null;
  writing_style: string | null;
  target_audience: string | null;
  readability_score: string | null;
  strengths: string[] | null;
  weaknesses: string[] | null;
  created_at: string;
}

export interface MetadataResult {
  id: number;
  manuscript_id: number;
  title_suggestions: string[] | null;
  subtitle: string | null;
  description: string | null;
  keywords: string[] | null;
  bisac_categories: string[] | null;
  author_bio_prompt: string | null;
  created_at: string;
}

export interface MarketingResult {
  id: number;
  manuscript_id: number;
  back_cover_blurb: string | null;
  amazon_description: string | null;
  twitter_post: string | null;
  linkedin_post: string | null;
  instagram_post: string | null;
  press_release_excerpt: string | null;
  elevator_pitch: string | null;
  created_at: string;
}
