// @vitest-environment jsdom
import { describe, it, expect, beforeEach } from "vitest";
import { getBestTime, trySetBestTime, fmtTime } from "../bestTime";

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
});
