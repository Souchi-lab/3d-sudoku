// @vitest-environment jsdom
import { describe, it, expect, beforeEach } from "vitest";
import {
  getBestTime, trySetBestTime, fmtTime,
  recordPlay, getStats,
  getDailyStreak, updateDailyStreak,
} from "../bestTime";

describe("bestTime", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  // ── getBestTime() ─────────────────────────────────────────────────────────

  describe("getBestTime()", () => {
    it("returns null when no record has been stored", () => {
      expect(getBestTime(3, 3)).toBeNull();
    });

    it("returns the stored number of seconds", () => {
      localStorage.setItem("sochiblocks-best-3-3", "150");
      expect(getBestTime(3, 3)).toBe(150);
    });

    it("returns null for an N/level combo with no record even if others exist", () => {
      localStorage.setItem("sochiblocks-best-3-3", "150");
      expect(getBestTime(3, 4)).toBeNull();
      expect(getBestTime(4, 3)).toBeNull();
    });
  });

  // ── trySetBestTime() ──────────────────────────────────────────────────────

  describe("trySetBestTime()", () => {
    it("saves the time and returns true on first record", () => {
      expect(trySetBestTime(3, 3, 150)).toBe(true);
      expect(getBestTime(3, 3)).toBe(150);
    });

    it("overwrites and returns true when new time is better (lower)", () => {
      trySetBestTime(3, 3, 150);
      expect(trySetBestTime(3, 3, 120)).toBe(true);
      expect(getBestTime(3, 3)).toBe(120);
    });

    it("does not overwrite and returns false when new time is worse (higher)", () => {
      trySetBestTime(3, 3, 150);
      expect(trySetBestTime(3, 3, 200)).toBe(false);
      expect(getBestTime(3, 3)).toBe(150);
    });

    it("does not overwrite and returns false for an equal time", () => {
      trySetBestTime(3, 3, 150);
      expect(trySetBestTime(3, 3, 150)).toBe(false);
      expect(getBestTime(3, 3)).toBe(150);
    });

    it("stores records independently for different N/level combos", () => {
      trySetBestTime(3, 3, 150);
      trySetBestTime(3, 4, 200);
      trySetBestTime(4, 3, 300);
      expect(getBestTime(3, 3)).toBe(150);
      expect(getBestTime(3, 4)).toBe(200);
      expect(getBestTime(4, 3)).toBe(300);
    });
  });

  // ── fmtTime() ─────────────────────────────────────────────────────────────

  describe("fmtTime()", () => {
    it("formats 0 seconds as 0:00", () => {
      expect(fmtTime(0)).toBe("0:00");
    });

    it("formats exactly one minute as 1:00", () => {
      expect(fmtTime(60)).toBe("1:00");
    });

    it("pads single-digit seconds with a leading zero", () => {
      expect(fmtTime(65)).toBe("1:05");
    });

    it("formats 90 seconds as 1:30", () => {
      expect(fmtTime(90)).toBe("1:30");
    });

    it("formats 150 seconds as 2:30", () => {
      expect(fmtTime(150)).toBe("2:30");
    });

    it("formats 599 seconds as 9:59", () => {
      expect(fmtTime(599)).toBe("9:59");
    });

    it("handles zero minutes (sub-minute time) correctly", () => {
      expect(fmtTime(45)).toBe("0:45");
    });
  });

  // ── recordPlay() + getStats() ─────────────────────────────────────────────

  describe("recordPlay() + getStats()", () => {
    it("starts with zero plays and clears", () => {
      const s = getStats(3, 3);
      expect(s.plays).toBe(0);
      expect(s.clears).toBe(0);
      expect(s.bestTime).toBeNull();
    });

    it("increments plays and clears correctly", () => {
      recordPlay(3, 3, true);
      recordPlay(3, 3, false);
      recordPlay(3, 3, true);
      const s = getStats(3, 3);
      expect(s.plays).toBe(3);
      expect(s.clears).toBe(2);
    });

    it("tracks stats independently per N/level", () => {
      recordPlay(3, 3, true);
      recordPlay(3, 4, false);
      expect(getStats(3, 3).plays).toBe(1);
      expect(getStats(3, 4).plays).toBe(1);
      expect(getStats(3, 3).clears).toBe(1);
      expect(getStats(3, 4).clears).toBe(0);
    });

    it("includes bestTime from localStorage", () => {
      trySetBestTime(3, 3, 120);
      recordPlay(3, 3, true);
      expect(getStats(3, 3).bestTime).toBe(120);
    });
  });

  // ── getDailyStreak() + updateDailyStreak() ────────────────────────────────

  describe("getDailyStreak() + updateDailyStreak()", () => {
    const STREAK_KEY = "sochiblocks-streak";

    it("returns 0 when no streak is stored", () => {
      expect(getDailyStreak()).toBe(0);
    });

    it("starts streak at 1 on first update", () => {
      updateDailyStreak();
      expect(getDailyStreak()).toBe(1);
    });

    it("idempotent: calling twice today keeps streak at 1", () => {
      updateDailyStreak();
      updateDailyStreak();
      expect(getDailyStreak()).toBe(1);
    });

    it("increments streak when lastDate is yesterday", () => {
      const yesterday = new Date(Date.now() - 86_400_000).toISOString().slice(0, 10);
      localStorage.setItem(STREAK_KEY, JSON.stringify({ lastDate: yesterday, count: 5 }));
      updateDailyStreak();
      expect(getDailyStreak()).toBe(6);
    });

    it("resets streak to 1 when lastDate is older than yesterday", () => {
      localStorage.setItem(STREAK_KEY, JSON.stringify({ lastDate: "2020-01-01", count: 10 }));
      updateDailyStreak();
      expect(getDailyStreak()).toBe(1);
    });

    it("returns 0 after streak expires (lastDate older than yesterday)", () => {
      localStorage.setItem(STREAK_KEY, JSON.stringify({ lastDate: "2020-01-01", count: 5 }));
      expect(getDailyStreak()).toBe(0);
    });
  });
});
