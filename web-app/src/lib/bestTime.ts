const storageKey = (N: number, level: number) =>
  `sochiblocks-best-${N}-${level}`;

/** Returns the stored best time in seconds, or null if none. */
export function getBestTime(N: number, level: number): number | null {
  if (typeof window === "undefined") return null;
  const v = localStorage.getItem(storageKey(N, level));
  return v !== null ? parseInt(v, 10) : null;
}

/**
 * Saves `seconds` as the best time if it's better than the stored record.
 * Returns true when a new record is set.
 */
export function trySetBestTime(N: number, level: number, seconds: number): boolean {
  if (typeof window === "undefined") return false;
  const current = getBestTime(N, level);
  if (current === null || seconds < current) {
    localStorage.setItem(storageKey(N, level), String(seconds));
    return true;
  }
  return false;
}

/** Formats seconds as "M:SS". */
export function fmtTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}
