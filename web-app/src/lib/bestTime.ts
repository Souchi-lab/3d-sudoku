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

// ---------------------------------------------------------------------------
// Play statistics
// ---------------------------------------------------------------------------

export interface PlayStats {
  plays: number;
  clears: number;
  bestTime: number | null;
}

const statsKey = (N: number, level: number) => `sochiblocks-stats-${N}-${level}`;

/** Record one play session. */
export function recordPlay(N: number, level: number, cleared: boolean): void {
  if (typeof window === "undefined") return;
  const raw = localStorage.getItem(statsKey(N, level));
  const data: { plays: number; clears: number } = raw
    ? JSON.parse(raw)
    : { plays: 0, clears: 0 };
  data.plays++;
  if (cleared) data.clears++;
  localStorage.setItem(statsKey(N, level), JSON.stringify(data));
}

/** Returns cumulative stats for a given N + level. */
export function getStats(N: number, level: number): PlayStats {
  if (typeof window === "undefined") return { plays: 0, clears: 0, bestTime: null };
  const raw = localStorage.getItem(statsKey(N, level));
  const data: { plays: number; clears: number } = raw
    ? JSON.parse(raw)
    : { plays: 0, clears: 0 };
  return { ...data, bestTime: getBestTime(N, level) };
}

// ---------------------------------------------------------------------------
// Daily streak
// ---------------------------------------------------------------------------

const STREAK_KEY = "sochiblocks-streak";

interface StreakData {
  lastDate: string;
  count: number;
}

function todayStr(): string {
  return new Date().toISOString().slice(0, 10);
}

function yesterdayStr(): string {
  return new Date(Date.now() - 86_400_000).toISOString().slice(0, 10);
}

/** Returns the current consecutive-day streak (0 if expired). */
export function getDailyStreak(): number {
  if (typeof window === "undefined") return 0;
  const raw = localStorage.getItem(STREAK_KEY);
  if (!raw) return 0;
  const data: StreakData = JSON.parse(raw);
  const today = todayStr();
  const yesterday = yesterdayStr();
  if (data.lastDate === today || data.lastDate === yesterday) return data.count;
  return 0;
}

/** Call once per day when a game is completed (idempotent within a day). */
export function updateDailyStreak(): void {
  if (typeof window === "undefined") return;
  const today = todayStr();
  const yesterday = yesterdayStr();
  const raw = localStorage.getItem(STREAK_KEY);
  let data: StreakData = raw ? JSON.parse(raw) : { lastDate: "", count: 0 };

  if (data.lastDate === today) return; // already updated today
  if (data.lastDate === yesterday) {
    data = { lastDate: today, count: data.count + 1 };
  } else {
    data = { lastDate: today, count: 1 };
  }
  localStorage.setItem(STREAK_KEY, JSON.stringify(data));
}
