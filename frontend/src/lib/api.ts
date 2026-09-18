import { Roadmap, UserPreferences } from '../types';

/**
 * API base resolution, in order of precedence:
 *   1. NEXT_PUBLIC_API_URL when explicitly set (deploy the API elsewhere).
 *   2. The dev server (:3000) talks to FastAPI on :8000.
 *   3. Otherwise same-origin ("" => relative /api), which is what the
 *      static-export demo uses when FastAPI serves frontend/out.
 */
function resolveApiBase(): string {
  const fromEnv = process.env.NEXT_PUBLIC_API_URL;
  if (fromEnv) return fromEnv;
  if (typeof window !== 'undefined' && window.location.port === '3000') {
    return 'http://localhost:8000';
  }
  return '';
}

export const API_BASE = resolveApiBase();

async function readError(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (body && typeof body.detail === 'string') return body.detail;
  } catch {
    /* not json */
  }
  return `Request failed with status ${res.status}`;
}

export async function generateRoadmap(
  preferences: UserPreferences,
): Promise<Roadmap> {
  const res = await fetch(`${API_BASE}/api/roadmap`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(preferences),
  });
  if (!res.ok) throw new Error(await readError(res));
  return (await res.json()) as Roadmap;
}

export function exportUrl(
  roadmapId: string,
  format: 'markdown' | 'ics',
): string {
  return `${API_BASE}/api/export/${encodeURIComponent(roadmapId)}?format=${format}`;
}
