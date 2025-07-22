export interface Step {
  number: number;
  raw: string;
}
export interface StepIssue {
  step_number: number;
  description: string;
  suggestion: string;
}
export interface AnalyzeResponse {
  steps: Step[];
  issues: StepIssue[];
}

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

export async function analyzeMarkdown(markdown: string): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ markdown })
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}`);
  }
  return res.json();
}


export interface FixResponse {
  fixed_markdown: string;
  applied_fixes: StepIssue[];
}

export async function fixMarkdown(markdown: string): Promise<FixResponse> {
  const res = await fetch(`${API_URL}/fix`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ markdown })
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
