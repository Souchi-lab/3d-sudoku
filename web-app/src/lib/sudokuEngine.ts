export type Position = [number, number, number];

export interface Cell {
  pos: Position;
  value: number;
}

export interface Player {
  id: number;
  name: string;
  score: number;
  consecutiveSuccesses: number;
}

export interface GameState {
  N: number;
  isTAMode: boolean;
  level: number;
  players: Record<number, Player>;
  currentPlayerId: number;
  initialFilledCells: Cell[];
  sequence: number[];
  currentIndex: number;
  currentNumber: number | null;
  timeLeft: number;
  skipCount: number;
}

/** A single move that can be undone. */
export interface MoveRecord {
  pos: Position;
  value: number;
  player: number;
}

export class SudokuEngine {
  private board: (number | null)[][][];
  private candidates: number[][][][];
  public readonly N: number;

  /** Stack of placed moves (excludes initial hints). */
  private history: MoveRecord[] = [];

  constructor(N: number) {
    this.N = N;
    this.board = this.createBoard(N);
    this.candidates = this.createCandidates(N);
  }

  private createBoard(N: number): (number | null)[][][] {
    return Array.from({ length: N }, () =>
      Array.from({ length: N }, () => Array(N).fill(null))
    );
  }

  private createCandidates(N: number): number[][][][] {
    return Array.from({ length: N }, () =>
      Array.from({ length: N }, () =>
        Array.from({ length: N }, () =>
          Array.from({ length: N }, (_, i) => i + 1)
        )
      )
    );
  }

  public check(pos: Position, num: number): { valid: boolean; message: string } {
    const [x, y, z] = pos;

    if (this.board[x][y][z] !== null) {
      return { valid: false, message: "Already filled." };
    }

    if (!this.candidates[x][y][z].includes(num)) {
      return { valid: false, message: "Not a candidate." };
    }

    for (let i = 0; i < this.N; i++) {
      if (this.board[i][y][z] === num) return { valid: false, message: "Duplicate in X-axis." };
    }
    for (let j = 0; j < this.N; j++) {
      if (this.board[x][j][z] === num) return { valid: false, message: "Duplicate in Y-axis." };
    }
    for (let k = 0; k < this.N; k++) {
      if (this.board[x][y][k] === num) return { valid: false, message: "Duplicate in Z-axis." };
    }

    return { valid: true, message: "OK" };
  }

  public setPoint(pos: Position, num: number): void {
    const [x, y, z] = pos;
    this.board[x][y][z] = num;
    this.reflect(pos, num);
  }

  /**
   * Place `num` at `pos` and record the move in the undo history.
   * Use this for player moves (not for loading initial hints).
   */
  public placeWithHistory(pos: Position, num: number, player: number): void {
    this.history.push({ pos, value: num, player });
    this.setPoint(pos, num);
  }

  /**
   * Undo the last recorded move.
   * Returns the undone MoveRecord, or null if history is empty.
   *
   * Because the candidate lists are hard to revert incrementally, we
   * rebuild the entire engine state from scratch using the remaining history
   * and the initial board snapshot stored at construction time.
   */
  public undo(): MoveRecord | null {
    if (this.history.length === 0) return null;
    const undone = this.history.pop()!;

    // Rebuild board + candidates from the initial snapshot
    const snapshot = this._initialSnapshot;
    this.board = JSON.parse(JSON.stringify(snapshot.board));
    this.candidates = JSON.parse(JSON.stringify(snapshot.candidates));

    // Re-apply all remaining history
    for (const move of this.history) {
      this.setPoint(move.pos, move.value);
    }

    return undone;
  }

  /** Number of moves that can be undone. */
  public get historyLength(): number {
    return this.history.length;
  }

  // Snapshot of the board+candidates right after hints are applied.
  // Stored lazily by freezeInitialSnapshot().
  private _initialSnapshot: { board: (number | null)[][][]; candidates: number[][][][] } = {
    board: [],
    candidates: [],
  };

  /**
   * Call this once after all initial hints have been placed.
   * This snapshot is used by undo() as the "reset point".
   */
  public freezeInitialSnapshot(): void {
    this._initialSnapshot = {
      board: JSON.parse(JSON.stringify(this.board)),
      candidates: JSON.parse(JSON.stringify(this.candidates)),
    };
  }

  private reflect(pos: Position, num: number): void {
    const [x, y, z] = pos;
    this.candidates[x][y][z] = [];
    for (let i = 0; i < this.N; i++) {
      if (i !== x) this.removeCandidate(i, y, z, num);
      if (i !== y) this.removeCandidate(x, i, z, num);
      if (i !== z) this.removeCandidate(x, y, i, num);
    }
  }

  private removeCandidate(x: number, y: number, z: number, num: number): void {
    if (this.board[x][y][z] === null) {
      this.candidates[x][y][z] = this.candidates[x][y][z].filter(c => c !== num);
    }
  }

  public scramble(): (number | null)[][][] {
    const N = this.N;
    const base: number[][][] = Array.from({ length: N }, () =>
      Array.from({ length: N }, () => Array(N).fill(0))
    );
    for (let i = 0; i < N; i++)
      for (let j = 0; j < N; j++)
        for (let k = 0; k < N; k++)
          base[i][j][k] = ((i + j + k) % N) + 1;

    const repl = Array.from({ length: N }, (_, i) => i + 1).sort(() => Math.random() - 0.5);
    const newBoard = this.createBoard(N);
    for (let i = 0; i < N; i++)
      for (let j = 0; j < N; j++)
        for (let k = 0; k < N; k++)
          newBoard[i][j][k] = repl[base[i][j][k] - 1];

    return newBoard;
  }

  /**
   * Generate initial hints for the given difficulty level.
   *
   * Target hint count = floor(N² × level / 5).
   * Each candidate hint is verified: after placing it, every number 1..N
   * must still have at least one valid empty cell. This prevents immediate
   * "stuck" states at game start.
   */
  public static generateInitialHints(N: number, level: number): Cell[] {
    const target = Math.max(0, Math.floor((N * N * level) / 5));
    if (target === 0) return [];

    const solverEngine = new SudokuEngine(N);
    const solved = solverEngine.scramble();

    const positions: Position[] = [];
    for (let i = 0; i < N; i++)
      for (let j = 0; j < N; j++)
        for (let k = 0; k < N; k++)
          positions.push([i, j, k]);
    positions.sort(() => Math.random() - 0.5);

    const hints: Cell[] = [];
    const testEngine = new SudokuEngine(N);

    for (const pos of positions) {
      if (hints.length >= target) break;

      const value = solved[pos[0]][pos[1]][pos[2]]!;

      const trial = testEngine.clone();
      trial.setPoint(pos, value);

      let safe = true;
      for (let n = 1; n <= N; n++) {
        if (!trial.canPlaceNumber(n)) { safe = false; break; }
      }

      if (safe) {
        testEngine.setPoint(pos, value);
        hints.push({ pos, value });
      }
    }

    return hints;
  }

  public getLineStatus(
    axis: "x" | "y" | "z",
    fixedIdx1: number,
    fixedIdx2: number
  ): { complete: boolean; missing: number[] } {
    const values: (number | null)[] = [];
    for (let i = 0; i < this.N; i++) {
      if (axis === "x") values.push(this.board[i][fixedIdx1][fixedIdx2]);
      else if (axis === "y") values.push(this.board[fixedIdx1][i][fixedIdx2]);
      else values.push(this.board[fixedIdx1][fixedIdx2][i]);
    }
    const present = new Set(values.filter((v): v is number => v !== null));
    const missing = Array.from({ length: this.N }, (_, i) => i + 1).filter(n => !present.has(n));
    return {
      complete: values.every(v => v !== null) && present.size === this.N,
      missing
    };
  }

  public getCompletionStatus(): { lines: { axis: string; i: number; j: number }[]; slices: { axis: string; index: number }[] } {
    const completed = { lines: [] as any[], slices: [] as any[] };
    for (let i = 0; i < this.N; i++) {
      for (let j = 0; j < this.N; j++) {
        if (this.getLineStatus("x", i, j).complete) completed.lines.push({ axis: "x", i, j });
        if (this.getLineStatus("y", i, j).complete) completed.lines.push({ axis: "y", i, j });
        if (this.getLineStatus("z", i, j).complete) completed.lines.push({ axis: "z", i, j });
      }
    }
    for (const axis of ["x", "y", "z"] as const) {
      for (let i = 0; i < this.N; i++) {
        let sliceComplete = true;
        for (let j = 0; j < this.N; j++) {
          const checkAxis = axis === "z" ? "x" : "z";
          if (!this.getLineStatus(checkAxis, i, j).complete) { sliceComplete = false; break; }
        }
        if (sliceComplete) completed.slices.push({ axis, index: i });
      }
    }
    return completed;
  }

  public getCandidates(pos: Position): number[] {
    const [x, y, z] = pos;
    return this.candidates[x][y][z];
  }

  public canPlaceNumber(num: number): boolean {
    for (let i = 0; i < this.N; i++)
      for (let j = 0; j < this.N; j++)
        for (let k = 0; k < this.N; k++)
          if (this.board[i][j][k] === null && this.check([i, j, k], num).valid)
            return true;
    return false;
  }

  /**
   * Returns the list of numbers 1..N that can no longer be placed anywhere.
   * Used to explain "stuck" states to the player.
   */
  public getUnplaceableNumbers(): number[] {
    const result: number[] = [];
    for (let n = 1; n <= this.N; n++) {
      if (!this.canPlaceNumber(n)) result.push(n);
    }
    return result;
  }

  public getBoard(): (number | null)[][][] { return this.board; }

  public clone(): SudokuEngine {
    const copy = new SudokuEngine(this.N);
    copy.board = JSON.parse(JSON.stringify(this.board));
    copy.candidates = JSON.parse(JSON.stringify(this.candidates));
    return copy;
  }
}
