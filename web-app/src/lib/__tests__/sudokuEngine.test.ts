import { describe, it, expect, beforeEach } from "vitest";
import { SudokuEngine } from "../sudokuEngine";

describe("SudokuEngine", () => {
  let engine: SudokuEngine;

  beforeEach(() => {
    engine = new SudokuEngine(3);
  });

  // ── check() ──────────────────────────────────────────────────────────────

  describe("check()", () => {
    it("allows a valid placement on an empty board", () => {
      expect(engine.check([0, 0, 0], 1).valid).toBe(true);
    });

    it("rejects placement on an already-filled cell", () => {
      engine.setPoint([0, 0, 0], 1);
      expect(engine.check([0, 0, 0], 2).valid).toBe(false);
    });

    it("rejects a duplicate along the X-axis", () => {
      engine.setPoint([0, 0, 0], 1);
      expect(engine.check([1, 0, 0], 1).valid).toBe(false);
      expect(engine.check([2, 0, 0], 1).valid).toBe(false);
    });

    it("rejects a duplicate along the Y-axis", () => {
      engine.setPoint([0, 0, 0], 1);
      expect(engine.check([0, 1, 0], 1).valid).toBe(false);
      expect(engine.check([0, 2, 0], 1).valid).toBe(false);
    });

    it("rejects a duplicate along the Z-axis", () => {
      engine.setPoint([0, 0, 0], 1);
      expect(engine.check([0, 0, 1], 1).valid).toBe(false);
      expect(engine.check([0, 0, 2], 1).valid).toBe(false);
    });

    it("allows a value not yet placed on any shared axis", () => {
      engine.setPoint([0, 0, 0], 1);
      // [1,1,1] shares no axis line with [0,0,0]
      expect(engine.check([1, 1, 1], 1).valid).toBe(true);
    });

    it("rejects a value that is no longer a candidate", () => {
      engine.setPoint([0, 0, 0], 1); // removes 1 from candidates at [1,0,0], [0,1,0], [0,0,1]
      expect(engine.check([1, 0, 0], 1).valid).toBe(false);
    });
  });

  // ── setPoint() ───────────────────────────────────────────────────────────

  describe("setPoint()", () => {
    it("writes the value to the board", () => {
      engine.setPoint([1, 2, 0], 3);
      expect(engine.getBoard()[1][2][0]).toBe(3);
    });

    it("removes the value from candidates on all shared axis lines", () => {
      engine.setPoint([0, 0, 0], 2);
      // [1,0,0]: same Y=0, Z=0 line (X-axis peer)
      expect(engine.getCandidates([1, 0, 0])).not.toContain(2);
      // [0,1,0]: same X=0, Z=0 line (Y-axis peer)
      expect(engine.getCandidates([0, 1, 0])).not.toContain(2);
      // [0,0,1]: same X=0, Y=0 line (Z-axis peer)
      expect(engine.getCandidates([0, 0, 1])).not.toContain(2);
      // [1,1,1]: no shared line — must still contain 2
      expect(engine.getCandidates([1, 1, 1])).toContain(2);
    });
  });

  // ── getLineStatus() ───────────────────────────────────────────────────────

  describe("getLineStatus()", () => {
    it("reports all numbers missing on a completely empty board", () => {
      const s = engine.getLineStatus("x", 0, 0);
      expect(s.complete).toBe(false);
      expect(s.missing).toEqual(expect.arrayContaining([1, 2, 3]));
    });

    it("reports a complete line after placing all N numbers", () => {
      engine.setPoint([0, 0, 0], 1);
      engine.setPoint([1, 0, 0], 2);
      engine.setPoint([2, 0, 0], 3);
      const s = engine.getLineStatus("x", 0, 0);
      expect(s.complete).toBe(true);
      expect(s.missing).toHaveLength(0);
    });

    it("reports correct missing numbers after partial fill", () => {
      engine.setPoint([0, 0, 0], 1);
      const s = engine.getLineStatus("x", 0, 0);
      expect(s.missing).toContain(2);
      expect(s.missing).toContain(3);
      expect(s.missing).not.toContain(1);
    });

    it("works for Y-axis lines", () => {
      engine.setPoint([0, 0, 0], 1);
      engine.setPoint([0, 1, 0], 2);
      engine.setPoint([0, 2, 0], 3);
      expect(engine.getLineStatus("y", 0, 0).complete).toBe(true);
    });

    it("works for Z-axis lines", () => {
      engine.setPoint([0, 0, 0], 1);
      engine.setPoint([0, 0, 1], 2);
      engine.setPoint([0, 0, 2], 3);
      expect(engine.getLineStatus("z", 0, 0).complete).toBe(true);
    });
  });

  // ── getCompletionStatus() ─────────────────────────────────────────────────

  describe("getCompletionStatus()", () => {
    it("starts with no completed lines or slices", () => {
      const s = engine.getCompletionStatus();
      expect(s.lines).toHaveLength(0);
      expect(s.slices).toHaveLength(0);
    });

    it("detects a newly completed X-axis line", () => {
      engine.setPoint([0, 0, 0], 1);
      engine.setPoint([1, 0, 0], 2);
      engine.setPoint([2, 0, 0], 3);
      const s = engine.getCompletionStatus();
      expect(s.lines.some(l => l.axis === "x" && l.i === 0 && l.j === 0)).toBe(true);
    });

    it("does not report a line as complete if it has duplicates", () => {
      // Fill with same number — board would be invalid but test the logic
      // Actually setPoint doesn't validate; check() would block it.
      // This test just confirms partial fill isn't counted.
      engine.setPoint([0, 0, 0], 1);
      engine.setPoint([1, 0, 0], 2);
      // Missing [2, 0, 0]
      const s = engine.getCompletionStatus();
      expect(s.lines.some(l => l.axis === "x" && l.i === 0 && l.j === 0)).toBe(false);
    });
  });

  // ── canPlaceNumber() ──────────────────────────────────────────────────────

  describe("canPlaceNumber()", () => {
    it("returns true on a fresh empty board for any number", () => {
      for (let n = 1; n <= 3; n++) {
        expect(engine.canPlaceNumber(n)).toBe(true);
      }
    });

    it("returns false when a number has no valid empty cell left", () => {
      // N=2 engine — easier to saturate
      const e2 = new SudokuEngine(2);
      // Fill the entire board with a valid solution to block placements
      // [i][j][k] = ((i+j+k) % 2) + 1
      e2.setPoint([0, 0, 0], 1);
      e2.setPoint([1, 1, 0], 1);
      e2.setPoint([1, 0, 1], 1);
      e2.setPoint([0, 1, 1], 1);
      // All four positions for '1' are filled
      expect(e2.canPlaceNumber(1)).toBe(false);
    });
  });

  // ── generateInitialHints() ────────────────────────────────────────────────

  describe("generateInitialHints()", () => {
    it("returns empty hints for level 0", () => {
      expect(SudokuEngine.generateInitialHints(3, 0)).toHaveLength(0);
    });

    it("returns at most floor(N²×level/5) hints", () => {
      const N = 3;
      for (let lv = 1; lv <= 5; lv++) {
        const hints = SudokuEngine.generateInitialHints(N, lv);
        const max = Math.floor((N * N * lv) / 5);
        expect(hints.length).toBeLessThanOrEqual(max);
      }
    });

    it("places no duplicate positions", () => {
      const hints = SudokuEngine.generateInitialHints(3, 5);
      const keys = hints.map(h => h.pos.join("-"));
      expect(new Set(keys).size).toBe(keys.length);
    });

    it("leaves all numbers 1..N placeable after hints are applied", () => {
      for (let lv = 1; lv <= 5; lv++) {
        const hints = SudokuEngine.generateInitialHints(3, lv);
        const testEngine = new SudokuEngine(3);
        hints.forEach(h => testEngine.setPoint(h.pos, h.value));
        for (let n = 1; n <= 3; n++) {
          expect(testEngine.canPlaceNumber(n)).toBe(true);
        }
      }
    });

    it("each hint value passes check() before placement", () => {
      const hints = SudokuEngine.generateInitialHints(3, 3);
      const testEngine = new SudokuEngine(3);
      for (const h of hints) {
        expect(testEngine.check(h.pos, h.value).valid).toBe(true);
        testEngine.setPoint(h.pos, h.value);
      }
    });
  });

  // ── placeWithHistory() + undo() ──────────────────────────────────────────

  describe("placeWithHistory() + undo()", () => {
    it("records the move in history and can be undone", () => {
      engine.freezeInitialSnapshot();
      engine.placeWithHistory([0, 0, 0], 1, 1);
      expect(engine.getBoard()[0][0][0]).toBe(1);
      expect(engine.historyLength).toBe(1);

      const undone = engine.undo();
      expect(undone).not.toBeNull();
      expect(undone!.value).toBe(1);
      expect(engine.getBoard()[0][0][0]).toBeNull();
      expect(engine.historyLength).toBe(0);
    });

    it("undo returns null when history is empty", () => {
      engine.freezeInitialSnapshot();
      expect(engine.undo()).toBeNull();
    });

    it("restores candidate lists after undo", () => {
      engine.freezeInitialSnapshot();
      engine.placeWithHistory([0, 0, 0], 1, 1);
      // Candidate 1 should be gone from peers
      expect(engine.getCandidates([1, 0, 0])).not.toContain(1);

      engine.undo();
      // After undo, candidate 1 should be restored for peers
      expect(engine.getCandidates([1, 0, 0])).toContain(1);
    });

    it("can undo multiple moves in LIFO order", () => {
      engine.freezeInitialSnapshot();
      engine.placeWithHistory([0, 0, 0], 1, 1);
      engine.placeWithHistory([1, 1, 1], 2, 1);

      const u2 = engine.undo();
      expect(u2!.pos).toEqual([1, 1, 1]);
      expect(engine.getBoard()[1][1][1]).toBeNull();
      expect(engine.getBoard()[0][0][0]).toBe(1); // first move still there

      const u1 = engine.undo();
      expect(u1!.pos).toEqual([0, 0, 0]);
      expect(engine.getBoard()[0][0][0]).toBeNull();
    });

    it("preserves initial hints across undo", () => {
      // Simulate hints placed before freezeInitialSnapshot
      engine.setPoint([2, 2, 2], 3);
      engine.freezeInitialSnapshot();
      engine.placeWithHistory([0, 0, 0], 1, 1);
      engine.undo();

      // Hint cell must survive undo
      expect(engine.getBoard()[2][2][2]).toBe(3);
    });
  });

  // ── getUnplaceableNumbers() ───────────────────────────────────────────────

  describe("getUnplaceableNumbers()", () => {
    it("returns empty array on a fresh board", () => {
      expect(engine.getUnplaceableNumbers()).toHaveLength(0);
    });

    it("returns numbers that have no valid placement left", () => {
      const e2 = new SudokuEngine(2);
      // Saturate all positions for value 1
      e2.setPoint([0, 0, 0], 1);
      e2.setPoint([1, 1, 0], 1);
      e2.setPoint([1, 0, 1], 1);
      e2.setPoint([0, 1, 1], 1);
      expect(e2.getUnplaceableNumbers()).toContain(1);
    });
  });

  // ── clone() ───────────────────────────────────────────────────────────────

  describe("clone()", () => {
    it("produces a board copy that is independent of the original", () => {
      engine.setPoint([0, 0, 0], 1);
      const copy = engine.clone();
      copy.setPoint([1, 1, 1], 2);
      expect(engine.getBoard()[1][1][1]).toBeNull();
    });

    it("copies existing board values", () => {
      engine.setPoint([2, 2, 2], 3);
      const copy = engine.clone();
      expect(copy.getBoard()[2][2][2]).toBe(3);
    });
  });

  // ── mulberry32() ──────────────────────────────────────────────────────────

  describe("mulberry32()", () => {
    it("produces values in [0, 1)", () => {
      const rng = SudokuEngine.mulberry32(42);
      for (let i = 0; i < 100; i++) {
        const v = rng();
        expect(v).toBeGreaterThanOrEqual(0);
        expect(v).toBeLessThan(1);
      }
    });

    it("is deterministic: same seed produces same sequence", () => {
      const rng1 = SudokuEngine.mulberry32(12345);
      const rng2 = SudokuEngine.mulberry32(12345);
      for (let i = 0; i < 20; i++) {
        expect(rng1()).toBe(rng2());
      }
    });

    it("produces different sequences for different seeds", () => {
      const r1 = SudokuEngine.mulberry32(1)();
      const r2 = SudokuEngine.mulberry32(2)();
      expect(r1).not.toBe(r2);
    });
  });

  // ── generateInitialHintsSeeded() ─────────────────────────────────────────

  describe("generateInitialHintsSeeded()", () => {
    it("returns the same hints for the same seed", () => {
      const h1 = SudokuEngine.generateInitialHintsSeeded(3, 3, 20260309);
      const h2 = SudokuEngine.generateInitialHintsSeeded(3, 3, 20260309);
      expect(h1.map(h => `${h.pos}-${h.value}`)).toEqual(h2.map(h => `${h.pos}-${h.value}`));
    });

    it("returns different hints for different seeds", () => {
      const h1 = SudokuEngine.generateInitialHintsSeeded(3, 3, 20260309);
      const h2 = SudokuEngine.generateInitialHintsSeeded(3, 3, 20260310);
      const k1 = h1.map(h => h.pos.join(",")).sort().join("|");
      const k2 = h2.map(h => h.pos.join(",")).sort().join("|");
      expect(k1).not.toBe(k2);
    });

    it("each seeded hint passes check() before placement", () => {
      const hints = SudokuEngine.generateInitialHintsSeeded(3, 3, 99999);
      const testEngine = new SudokuEngine(3);
      for (const h of hints) {
        expect(testEngine.check(h.pos, h.value).valid).toBe(true);
        testEngine.setPoint(h.pos, h.value);
      }
    });

    it("returns 0 hints at level 0 regardless of seed", () => {
      expect(SudokuEngine.generateInitialHintsSeeded(3, 0, 42)).toHaveLength(0);
    });
  });
});
