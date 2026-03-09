import { SudokuEngine, Position } from "./sudokuEngine";

/**
 * CPU player with 5 difficulty levels.
 *
 * Level 1 – Completely random valid move.
 * Level 2 – 60 % random, 40 % strategic.
 * Level 3 – Always picks the highest-scoring move (complete lines / slices).
 * Level 4 – Strategic + light blocking: prefers moves that reduce the human
 *            player's options for their upcoming turn (blockingWeight = 4).
 * Level 5 – Strategic + heavy blocking (blockingWeight = 10). The CPU
 *            actively tries to leave the human player with as few valid
 *            positions as possible, maximising the chance of a stuck state.
 */
export class CpuPlayer {
  private engine: SudokuEngine;
  private N: number;
  private level: number;

  constructor(engine: SudokuEngine, N: number, level: number = 3) {
    this.engine = engine;
    this.N = N;
    this.level = Math.max(1, Math.min(5, level));
  }

  // -------------------------------------------------------------------------
  // Public API
  // -------------------------------------------------------------------------

  public makeMove(currentNumber: number): Position | null {
    const moves = this.getValidMoves(currentNumber);
    if (moves.length === 0) return null;

    // Level 1: pure random
    if (this.level === 1) {
      return moves[Math.floor(Math.random() * moves.length)];
    }

    // Level 2: 60 % random
    if (this.level === 2 && Math.random() < 0.6) {
      return moves[Math.floor(Math.random() * moves.length)];
    }

    // Level 3-5: score each move
    const blockingWeight = this.level >= 5 ? 10 : this.level === 4 ? 4 : 0;
    // After the CPU places currentNumber, the player will use nextNum
    const nextNum = (currentNumber % this.N) + 1;

    const scored = moves.map(move => ({
      move,
      score: this.scoreMove(move, currentNumber, nextNum, blockingWeight),
    }));

    const best = scored.reduce((a, b) => (b.score > a.score ? b : a)).score;
    const top = scored.filter(s => s.score === best);
    return top[Math.floor(Math.random() * top.length)].move;
  }

  // -------------------------------------------------------------------------
  // Private helpers
  // -------------------------------------------------------------------------

  private getValidMoves(num: number): Position[] {
    const moves: Position[] = [];
    const board = this.engine.getBoard();
    for (let i = 0; i < this.N; i++)
      for (let j = 0; j < this.N; j++)
        for (let k = 0; k < this.N; k++)
          if (board[i][j][k] === null && this.engine.check([i, j, k], num).valid)
            moves.push([i, j, k]);
    return moves;
  }

  /**
   * Combined score = positional gain (lines / slices) − blockingWeight × playerOptions.
   * Higher score = better for CPU.
   * Subtracting (playerOptions × blockingWeight) means the CPU prefers moves that
   * leave the human with fewer choices.
   */
  private scoreMove(
    pos: Position,
    cpuNum: number,
    playerNextNum: number,
    blockingWeight: number
  ): number {
    const sim = this.engine.clone();
    sim.setPoint(pos, cpuNum);

    let score = this.evaluateCompletion(sim, cpuNum);

    if (blockingWeight > 0) {
      const playerOptions = this.countValidMoves(sim, playerNextNum);
      score -= blockingWeight * playerOptions;
    }

    return score;
  }

  /** Reward completed lines and slices. */
  private evaluateCompletion(sim: SudokuEngine, num: number): number {
    let score = 0;
    const completed = sim.getCompletionStatus();
    score += completed.lines.length * 10;
    score += completed.slices.length * 100;

    // Near-completion bonus (one cell away from finishing a line)
    for (const axis of ["x", "y", "z"] as const) {
      for (let i = 0; i < this.N; i++) {
        for (let j = 0; j < this.N; j++) {
          const status = sim.getLineStatus(axis, i, j);
          const board = sim.getBoard();
          let empty = 0;
          for (let k = 0; k < this.N; k++) {
            const v = axis === "x" ? board[k][i][j]
                    : axis === "y" ? board[i][k][j]
                    :                board[i][j][k];
            if (v === null) empty++;
          }
          if (empty === 1 && status.missing.includes(num)) score += 5;
        }
      }
    }
    return score;
  }

  /** Count how many valid positions exist for `num` in the given engine state. */
  private countValidMoves(engine: SudokuEngine, num: number): number {
    let count = 0;
    const board = engine.getBoard();
    for (let i = 0; i < this.N; i++)
      for (let j = 0; j < this.N; j++)
        for (let k = 0; k < this.N; k++)
          if (board[i][j][k] === null && engine.check([i, j, k], num).valid)
            count++;
    return count;
  }
}
