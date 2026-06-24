export interface Insight {
  category: string;
  icon: string;
  color: string;
  change: string;
  why: string;
}

export interface OptimizeResult {
  optimized: string;
  insights: Insight[];
  mode: "ai" | "rule";
  model?: string;
  elapsed: number;
}

export interface ArchitectResult {
  analysis: string;
  prompt: string;
  enhancements: string;
  qualityScore: string;
  scores: Record<string, number>;
  total: number;
}

export interface Tip {
  id: string;
  type: string;
  icon: string;
  title: string;
  body: string;
  platform?: string;
  trigger: string;
}

export interface LearnItem {
  title: string;
  icon: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  readTime: string;
  summary: string;
  keyPoints: string[];
}
