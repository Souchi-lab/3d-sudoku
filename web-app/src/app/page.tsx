"use client";

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import HyperCube, { LayerFilter } from "@/components/game/HyperCube";
import RulesModal from "@/components/game/RulesModal";
import { SudokuEngine, Position } from "@/lib/sudokuEngine";
import {
  getBestTime, trySetBestTime, fmtTime,
  recordPlay, getStats, getDailyStreak, updateDailyStreak,
} from "@/lib/bestTime";
import {
  Timer, Trophy, RotateCcw, HelpCircle, User, Cpu, Users,
  Layers, Lightbulb, Undo2, CalendarDays, CheckCircle2,
} from "lucide-react";
import { CpuPlayer } from "@/lib/cpuPlayer";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const NUMBER_COLORS: Record<number, string> = {
  1: "#2d7ee8",
  2: "#2ec47a",
  3: "#e84444",
  4: "#f5a623",
  5: "#9b5de5",
};

const TIME_BY_LEVEL: Record<number, number> = { 1: 600, 2: 540, 3: 480, 4: 420, 5: 360 };

const LEVEL_LABELS: Record<number, string> = {
  1: "Beginner",
  2: "Easy",
  3: "Normal",
  4: "Hard",
  5: "Expert",
};

const CPU_LABEL: Record<number, string> = {
  1: "ランダム",
  2: "やや弱め",
  3: "標準",
  4: "強め",
  5: "最強（妨害あり）",
};

/** Today's date as YYYYMMDD integer seed (deterministic daily challenge). */
function todaySeed(): number {
  const d = new Date();
  return d.getFullYear() * 10000 + (d.getMonth() + 1) * 100 + d.getDate();
}

// ---------------------------------------------------------------------------
// Styled helper components
// ---------------------------------------------------------------------------

function DarkButton({ onClick, className = "", children, disabled }: {
  onClick?: () => void;
  className?: string;
  children: React.ReactNode;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`bg-[#333333] hover:bg-[#555555] active:bg-[#111111] disabled:opacity-40 text-white font-bold rounded-lg transition-colors ${className}`}
    >
      {children}
    </button>
  );
}

function LightButton({ onClick, className = "", children }: {
  onClick?: () => void;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`bg-white hover:bg-[#f5f5f5] active:bg-[#ececec] text-[#666666] font-semibold border border-[#dddddd] rounded-lg transition-colors ${className}`}
    >
      {children}
    </button>
  );
}

// ---------------------------------------------------------------------------
// Game config ref type
// ---------------------------------------------------------------------------
interface GameConfig { N: number; level: number; mode: 'solo' | 'versus-cpu' | 'versus-human' | 'daily' }

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
export default function GamePage() {
  // ── Config (mode select) ──────────────────────────────────────────────────
  const [selectedN,     setSelectedN]     = useState(3);
  const [selectedLevel, setSelectedLevel] = useState(3);
  const [gameMode, setGameMode] = useState<'solo' | 'versus-cpu' | 'versus-human' | 'daily' | null>(null);

  // ── Live game state ───────────────────────────────────────────────────────
  const engineRef     = useRef<SudokuEngine | null>(null);
  const cpuRef        = useRef<CpuPlayer | null>(null);
  const configRef     = useRef<GameConfig>({ N: 3, level: 3, mode: 'solo' });
  const gameActiveRef = useRef(false);
  const startTimeRef  = useRef(0);

  const [N,             setN]             = useState(3);
  const [board,         setBoard]         = useState<(number | null)[][][]>([]);
  const [selectedPos,   setSelectedPos]   = useState<Position | null>(null);
  const [currentNumber, setCurrentNumber] = useState(1);
  const [currentPlayer, setCurrentPlayer] = useState(1);
  const [scores,        setScores]        = useState<Record<number, number>>({ 1: 0, 2: 0 });
  const [combos,        setCombos]        = useState<Record<number, number>>({ 1: 0, 2: 0 });
  const [lastSuccessTimes, setLastSuccessTimes] = useState<Record<number, number>>({ 1: 0, 2: 0 });
  const [timeLeft,      setTimeLeft]      = useState(480);
  const [lastPlacedPos, setLastPlacedPos] = useState<Position | null>(null);
  const [showGameOverOverlay, setShowGameOverOverlay] = useState(false);
  const [isShaking,     setIsShaking]     = useState(false);
  const [successFlash,  setSuccessFlash]  = useState(false);
  const [isStuck,       setIsStuck]       = useState(false);
  const [isCpuThinking, setIsCpuThinking] = useState(false);
  const [showRules,     setShowRules]     = useState(false);
  const [layerFilter,   setLayerFilter]   = useState<LayerFilter>(null);

  // ── Flash / hint / best-time / undo state ────────────────────────────────
  const [flashingCells,   setFlashingCells]   = useState<Set<string>>(new Set());
  const [flashStartTime,  setFlashStartTime]  = useState(0);
  const [hintPos,         setHintPos]         = useState<Position | null>(null);
  const [bestTimeDisplay, setBestTimeDisplay] = useState<number | null>(null);
  const [boardComplete,   setBoardComplete]   = useState(false);
  const [clearTime,       setClearTime]       = useState<number | null>(null);
  const [isNewBest,       setIsNewBest]       = useState(false);
  const [canUndo,         setCanUndo]         = useState(false);
  const [stuckNumbers,    setStuckNumbers]    = useState<number[]>([]);
  const [showHandoff,     setShowHandoff]     = useState(false);

  // ── New feature states ────────────────────────────────────────────────────
  const [justPlacedPos,  setJustPlacedPos]  = useState<Position | null>(null);
  const [justPlacedTime, setJustPlacedTime] = useState(0);
  const [hintCellKeys,   setHintCellKeys]   = useState<Set<string>>(new Set());
  const [showOnboarding, setShowOnboarding] = useState(false);

  // ── First-run onboarding ──────────────────────────────────────────────────
  useEffect(() => {
    if (typeof window !== "undefined" && !localStorage.getItem("sochiblocks-onboarded")) {
      setShowOnboarding(true);
    }
  }, []);

  // ── Derived values ────────────────────────────────────────────────────────
  const numberCounts = useMemo(() => {
    const counts: Record<number, number> = {};
    for (let n = 1; n <= N; n++) counts[n] = 0;
    board.flat(2).forEach(v => { if (v !== null) counts[v] = (counts[v] ?? 0) + 1; });
    return counts;
  }, [board, N]);

  const filledCount = useMemo(() => board.flat(2).filter(v => v !== null).length, [board]);
  const totalCells  = N * N * N;

  // ── Start game ────────────────────────────────────────────────────────────
  const startGame = useCallback((mode: 'solo' | 'versus-cpu' | 'versus-human' | 'daily', n: number, lv: number) => {
    const engine = new SudokuEngine(n);

    const hints = mode === 'daily'
      ? SudokuEngine.generateInitialHintsSeeded(n, lv, todaySeed())
      : SudokuEngine.generateInitialHints(n, lv);

    hints.forEach(h => engine.setPoint(h.pos, h.value));
    engine.freezeInitialSnapshot();

    const keySet = new Set<string>(hints.map(h => `${h.pos[0]}-${h.pos[1]}-${h.pos[2]}`));

    engineRef.current = engine;
    cpuRef.current    = new CpuPlayer(engine, n, lv);
    configRef.current = { N: n, level: lv, mode };
    startTimeRef.current = Date.now();
    gameActiveRef.current = false;

    setN(n);
    setBoard([...engine.getBoard()]);
    setSelectedPos(null);
    setCurrentNumber(1);
    setCurrentPlayer(1);
    setScores({ 1: 0, 2: 0 });
    setCombos({ 1: 0, 2: 0 });
    setLastSuccessTimes({ 1: 0, 2: 0 });
    setTimeLeft(TIME_BY_LEVEL[lv] ?? 480);
    setLastPlacedPos(null);
    setShowGameOverOverlay(false);
    setIsShaking(false);
    setSuccessFlash(false);
    setIsStuck(false);
    setIsCpuThinking(false);
    setShowRules(false);
    setLayerFilter(null);
    setFlashingCells(new Set());
    setFlashStartTime(0);
    setHintPos(null);
    setBoardComplete(false);
    setClearTime(null);
    setIsNewBest(false);
    setCanUndo(false);
    setStuckNumbers([]);
    setShowHandoff(false);
    setJustPlacedPos(null);
    setJustPlacedTime(0);
    setHintCellKeys(keySet);
    setBestTimeDisplay(getBestTime(n, lv));
    setGameMode(mode);

    setTimeout(() => { gameActiveRef.current = true; }, 0);
  }, []);

  // ── Timer ─────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!gameMode || isStuck || boardComplete || timeLeft <= 0) return;
    const id = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) { clearInterval(id); return 0; }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [gameMode, isStuck, boardComplete]);

  useEffect(() => {
    if (timeLeft === 0 && gameMode && !boardComplete) {
      setShowGameOverOverlay(true);
      const { mode, N: cn, level } = configRef.current;
      if (mode === 'solo' || mode === 'daily') recordPlay(cn, level, false);
    }
  }, [timeLeft, gameMode, boardComplete]);

  // ── Stuck check ───────────────────────────────────────────────────────────
  useEffect(() => {
    if (!gameActiveRef.current || !engineRef.current) return;
    if (!engineRef.current.canPlaceNumber(currentNumber)) {
      const unplaceable = engineRef.current.getUnplaceableNumbers();
      setStuckNumbers(unplaceable);
      setIsStuck(true);
      setShowGameOverOverlay(true);
      const { mode, N: cn, level } = configRef.current;
      if (mode === 'solo' || mode === 'daily') recordPlay(cn, level, false);
    }
  }, [board, currentNumber]);

  // ── CPU turn ──────────────────────────────────────────────────────────────
  useEffect(() => {
    const { mode } = configRef.current;
    if (mode !== 'versus-cpu' || currentPlayer !== 2 || isStuck || boardComplete || timeLeft <= 0 || !gameMode) return;
    if (!cpuRef.current || !engineRef.current) return;

    const capturedNumber = currentNumber;
    setIsCpuThinking(true);

    const t1 = setTimeout(() => {
      const move = cpuRef.current!.makeMove(capturedNumber);
      if (!move) {
        setIsCpuThinking(false);
        setIsStuck(true);
        setShowGameOverOverlay(true);
        return;
      }
      setSelectedPos(move);

      const t2 = setTimeout(() => {
        commitMove(move, capturedNumber, 2);
        setIsCpuThinking(false);
      }, 900);
      return () => clearTimeout(t2);
    }, 1400);

    return () => clearTimeout(t1);
  }, [currentPlayer, gameMode, currentNumber, isStuck, boardComplete]);

  // ── commitMove ────────────────────────────────────────────────────────────
  const commitMove = useCallback((pos: Position, num: number, player: number) => {
    const engine = engineRef.current;
    if (!engine) return;

    const result = engine.check(pos, num);
    if (!result.valid) {
      if (result.message === "Already filled.") return;
      setCombos(prev => ({ ...prev, [player]: 0 }));
      setIsShaking(true);
      setTimeout(() => setIsShaking(false), 500);
      return;
    }

    const beforeLineKeys = new Set(
      engine.getCompletionStatus().lines.map(l => `${l.axis}-${l.i}-${l.j}`)
    );

    engine.placeWithHistory(pos, num, player);
    setCanUndo(true);
    setBoard([...engine.getBoard()]);
    setLastPlacedPos(pos);
    setJustPlacedPos(pos);
    setJustPlacedTime(performance.now());
    setHintPos(null);

    // Flash newly completed lines
    const afterStatus = engine.getCompletionStatus();
    const newFlashCells = new Set<string>();
    const cn = configRef.current.N;

    for (const line of afterStatus.lines) {
      const key = `${line.axis}-${line.i}-${line.j}`;
      if (!beforeLineKeys.has(key)) {
        for (let k = 0; k < cn; k++) {
          if (line.axis === 'x')      newFlashCells.add(`${k}-${line.i}-${line.j}`);
          else if (line.axis === 'y') newFlashCells.add(`${line.i}-${k}-${line.j}`);
          else                        newFlashCells.add(`${line.i}-${line.j}-${k}`);
        }
      }
    }

    if (newFlashCells.size > 0) {
      setFlashingCells(newFlashCells);
      setFlashStartTime(performance.now());
      setTimeout(() => setFlashingCells(new Set()), 1500);
    }

    // Scoring
    const now = Date.now();
    setLastSuccessTimes(prev => {
      const newTimes = { ...prev, [player]: now };
      const isCombo = now - prev[player] < 5000;
      setCombos(c => {
        const newCombo = isCombo ? c[player] + 1 : 1;
        const bonus = Math.min(newCombo * 5, 50);
        setScores(s => ({ ...s, [player]: s[player] + 10 + bonus }));
        return { ...c, [player]: newCombo };
      });
      return newTimes;
    });

    setSuccessFlash(true);
    setTimeout(() => setSuccessFlash(false), 300);

    const { N: cn2, mode } = configRef.current;
    setCurrentNumber(n => (n % cn2) + 1);
    setSelectedPos(null);
    if (mode !== 'solo' && mode !== 'daily') {
      const nextPlayer = player === 1 ? 2 : 1;
      setCurrentPlayer(nextPlayer);
      if (mode === 'versus-human') setShowHandoff(true);
    }

    // Board complete
    const allFilled = engine.getBoard().flat(2).every(v => v !== null);
    if (allFilled) {
      gameActiveRef.current = false;
      setBoardComplete(true);
      setShowGameOverOverlay(true);
      if (mode === 'solo' || mode === 'daily') {
        const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
        setClearTime(elapsed);
        const newRecord = trySetBestTime(configRef.current.N, configRef.current.level, elapsed);
        setIsNewBest(newRecord);
        setBestTimeDisplay(getBestTime(configRef.current.N, configRef.current.level));
        recordPlay(configRef.current.N, configRef.current.level, true);
        updateDailyStreak();
      }
    }
  }, []);

  // ── Hint ──────────────────────────────────────────────────────────────────
  const handleHint = useCallback(() => {
    const engine = engineRef.current;
    if (!engine) return;
    const { N: cn } = configRef.current;

    const b = engine.getBoard();
    const validCells: Position[] = [];
    for (let i = 0; i < cn; i++)
      for (let j = 0; j < cn; j++)
        for (let k = 0; k < cn; k++)
          if (b[i][j][k] === null && engine.check([i, j, k], currentNumber).valid)
            validCells.push([i, j, k]);

    if (validCells.length === 0) return;
    const pick = validCells[Math.floor(Math.random() * validCells.length)];
    setHintPos(pick);
    setTimeout(() => setHintPos(null), 3000);
  }, [currentNumber]);

  // ── Undo ──────────────────────────────────────────────────────────────────
  const handleUndo = useCallback(() => {
    const engine = engineRef.current;
    if (!engine) return;
    const undone = engine.undo();
    if (!undone) return;

    setBoard([...engine.getBoard()]);
    setLastPlacedPos(null);
    setJustPlacedPos(null);
    setSelectedPos(null);
    setHintPos(null);
    setIsStuck(false);
    setStuckNumbers([]);
    setShowGameOverOverlay(false);
    setBoardComplete(false);
    setCanUndo(engine.historyLength > 0);
    gameActiveRef.current = true;
    setShowHandoff(false);

    setCurrentNumber(undone.value);
    const { mode } = configRef.current;
    if (mode !== 'solo' && mode !== 'daily') setCurrentPlayer(undone.player);
  }, []);

  // ── Human cell click ──────────────────────────────────────────────────────
  const handleCellClick = useCallback((pos: Position) => {
    const { mode } = configRef.current;
    if (mode === 'versus-cpu' && currentPlayer === 2) return;
    if (isCpuThinking) return;
    if (showHandoff) return;

    const isSame = selectedPos &&
      selectedPos[0] === pos[0] && selectedPos[1] === pos[1] && selectedPos[2] === pos[2];

    if (isSame) {
      commitMove(pos, currentNumber, currentPlayer);
    } else {
      setSelectedPos(pos);
    }
  }, [selectedPos, currentNumber, currentPlayer, isCpuThinking, showHandoff, commitMove]);

  // ── Body scroll lock ──────────────────────────────────────────────────────
  useEffect(() => {
    const locked = showGameOverOverlay || showRules || showHandoff || showOnboarding;
    document.body.style.overflow = locked ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [showGameOverOverlay, showRules, showHandoff, showOnboarding]);

  // ── Keyboard shortcuts ────────────────────────────────────────────────────
  useEffect(() => {
    if (!gameMode) return;
    const handler = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      const n = parseInt(e.key);
      if (!isNaN(n) && n >= 1 && n <= configRef.current.N) {
        setCurrentNumber(n);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [gameMode]);

  // ==========================================================================
  // ONBOARDING OVERLAY (M4)
  // ==========================================================================
  if (showOnboarding) {
    return (
      <div className="fixed inset-0 bg-black/55 backdrop-blur-sm flex items-center justify-center z-50 p-6">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-8 text-center">
          <div className="w-16 h-16 bg-[#333333] rounded-2xl flex items-center justify-center mx-auto mb-5">
            <span className="text-3xl font-black text-white">S</span>
          </div>
          <h1 className="text-2xl font-black text-[#1e1e1e] mb-1">SoChi BLOCKS</h1>
          <p className="text-sm text-[#888888] mb-6">3D Hyper-Cube Sudoku へようこそ！</p>
          <div className="text-left space-y-3 mb-7">
            {[
              ["1回タップ", "セルを選択（オレンジ枠）"],
              ["再タップ",  "選択セルに数字を配置"],
              ["キー 1〜N", "配置する数字を直接切り替え"],
              ["ドラッグ",  "3D キューブを自由に回転"],
            ].map(([key, val]) => (
              <div key={key} className="flex gap-3 items-start text-sm">
                <span className="shrink-0 bg-[#333333] text-white text-[10px] font-black px-2 py-0.5 rounded-md mt-0.5">
                  {key}
                </span>
                <span className="text-[#666666]">{val}</span>
              </div>
            ))}
          </div>
          <DarkButton
            className="w-full py-3"
            onClick={() => {
              localStorage.setItem("sochiblocks-onboarded", "1");
              setShowOnboarding(false);
            }}
          >
            はじめる
          </DarkButton>
        </div>
      </div>
    );
  }

  // ==========================================================================
  // MODE SELECT SCREEN
  // ==========================================================================
  if (!gameMode) {
    const modes = [
      { id: 'solo'          as const, name: 'Solo Training',   icon: User,        desc: '一人でキューブを完成させよう。' },
      { id: 'versus-cpu'    as const, name: 'VS CPU',          icon: Cpu,         desc: 'AI対戦。難易度でCPUの強さが変わる。' },
      { id: 'versus-human'  as const, name: 'VS Human',        icon: Users,       desc: 'ローカル2人対戦。同じ画面で対決。' },
      { id: 'daily'         as const, name: 'Daily Challenge', icon: CalendarDays, desc: `今日のパズル。毎日同じ問題にチャレンジ！` },
    ];

    const nOptions = [
      { n: 2, label: "2×2×2", sub: "8マス / 数字1〜2" },
      { n: 3, label: "3×3×3", sub: "27マス / 数字1〜3" },
      { n: 4, label: "4×4×4", sub: "64マス / 数字1〜4" },
    ];

    const streak = getDailyStreak();
    const stats  = getStats(selectedN, selectedLevel);

    return (
      <main className="min-h-dvh bg-[#fcfcfc] flex items-center justify-center p-6 md:p-8 pt-safe">
        <div className="max-w-3xl w-full space-y-8">

          {/* Brand header */}
          <div className="text-center">
            <h1 className="text-4xl font-black tracking-[0.04em] text-[#1e1e1e] mb-1">SoChi BLOCKS</h1>
            <p className="text-sm font-semibold text-[#888888] tracking-widest uppercase">Hyper-Cube Sudoku</p>
            {streak >= 2 && (
              <p className="mt-2 text-sm font-bold text-[#2e7d32]">
                🔥 {streak}日連続プレイ中！
              </p>
            )}
          </div>

          {/* ── Cube size ── */}
          <section className="bg-white border border-[#dddddd] rounded-xl p-6 shadow-sm">
            <p className="text-[10px] font-black uppercase tracking-widest text-[#888888] mb-4">
              立方体サイズ
            </p>
            <div className="grid grid-cols-3 gap-3">
              {nOptions.map(({ n, label, sub }) => (
                <button
                  key={n}
                  onClick={() => setSelectedN(n)}
                  className={`rounded-xl p-4 border text-center transition-all ${
                    selectedN === n
                      ? 'bg-[#333333] border-[#333333] text-white shadow-md'
                      : 'bg-white border-[#dddddd] text-[#1e1e1e] hover:border-[#333333]'
                  }`}
                >
                  <div className="text-lg font-black">{label}</div>
                  <div className={`text-[10px] mt-0.5 ${selectedN === n ? 'text-[#cccccc]' : 'text-[#888888]'}`}>{sub}</div>
                </button>
              ))}
            </div>
          </section>

          {/* ── Difficulty ── */}
          <section className="bg-white border border-[#dddddd] rounded-xl p-6 shadow-sm">
            <p className="text-[10px] font-black uppercase tracking-widest text-[#888888] mb-4">
              難易度
            </p>
            <div className="flex gap-2 mb-3">
              {[1, 2, 3, 4, 5].map(lv => (
                <button
                  key={lv}
                  onClick={() => setSelectedLevel(lv)}
                  className={`flex-1 py-2 rounded-lg text-sm font-bold border transition-colors ${
                    selectedLevel === lv
                      ? 'bg-[#333333] text-white border-[#333333]'
                      : 'bg-white text-[#666666] border-[#dddddd] hover:bg-[#f5f5f5]'
                  }`}
                >
                  Lv {lv}
                </button>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs text-[#666666]">
              <div>難易度: <strong className="text-[#1e1e1e]">{LEVEL_LABELS[selectedLevel]}</strong></div>
              <div>CPU: <strong className="text-[#1e1e1e]">{CPU_LABEL[selectedLevel]}</strong></div>
              <div>初期ヒント: <strong className="text-[#1e1e1e]">
                {Math.floor((selectedN * selectedN * selectedLevel) / 5)} マス
              </strong></div>
              <div>制限時間: <strong className="text-[#1e1e1e]">{(TIME_BY_LEVEL[selectedLevel] ?? 480) / 60} 分</strong></div>

              {/* Best time */}
              {(() => {
                const bt = getBestTime(selectedN, selectedLevel);
                return bt !== null ? (
                  <div className="col-span-2 flex items-center gap-1.5 mt-1 text-[#2e7d32]">
                    <Trophy className="w-3 h-3" />
                    Best: <strong>{fmtTime(bt)}</strong>
                  </div>
                ) : null;
              })()}

              {/* Stats */}
              {stats.plays > 0 && (
                <div className="col-span-2 flex gap-4 text-xs text-[#888888] mt-0.5">
                  <span>プレイ: <strong className="text-[#1e1e1e]">{stats.plays}</strong></span>
                  <span>クリア: <strong className="text-[#1e1e1e]">{stats.clears}</strong></span>
                  {stats.clears > 0 && (
                    <span>成功率: <strong className="text-[#1e1e1e]">{Math.round(stats.clears / stats.plays * 100)}%</strong></span>
                  )}
                </div>
              )}
            </div>
          </section>

          {/* ── Mode cards ── */}
          <section>
            <p className="text-[10px] font-black uppercase tracking-widest text-[#888888] mb-4 text-center">
              ゲームモードを選択
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {modes.map(m => (
                <button
                  key={m.id}
                  onClick={() => startGame(m.id, selectedN, selectedLevel)}
                  className={`bg-white hover:bg-[#f5f5f5] active:bg-[#ececec] border hover:border-[#333333] rounded-xl p-5 flex flex-col items-center gap-3 text-center transition-all shadow-sm hover:shadow-md ${
                    m.id === 'daily' ? 'border-[#f5a623]' : 'border-[#dddddd]'
                  }`}
                >
                  <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${
                    m.id === 'daily' ? 'bg-[#fff8ec]' : 'bg-[#f5f5f5]'
                  }`}>
                    <m.icon className={`w-5 h-5 ${m.id === 'daily' ? 'text-[#f5a623]' : 'text-[#333333]'}`} />
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-[#1e1e1e]">{m.name}</h2>
                    <p className="text-[10px] text-[#888888] leading-relaxed mt-0.5">{m.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </section>

        </div>
      </main>
    );
  }

  // ==========================================================================
  // GAME SCREEN
  // ==========================================================================
  const numColor   = NUMBER_COLORS[currentNumber] ?? "#333333";
  const p2Label    = configRef.current.mode === 'versus-cpu' ? 'CPU' : 'Player 2';
  const isGameOver = timeLeft === 0 || isStuck || boardComplete;
  const winner =
    scores[1] > scores[2] ? 'Player 1' :
    scores[2] > scores[1] ? p2Label : null;

  // Timer urgency class (M2)
  const timerClass = timeLeft < 10
    ? 'bg-[#fff5f5] border-[#e53e3e] text-[#e53e3e] animate-timer-urgent'
    : timeLeft < 30
      ? 'bg-[#fff5f5] border-[#e53e3e] text-[#e53e3e] animate-timer-pulse'
      : timeLeft < 60
        ? 'bg-[#fff5f5] border-[#e53e3e] text-[#e53e3e]'
        : 'bg-[#f5f5f5] border-[#dddddd] text-[#333333]';

  const progressPct = totalCells > 0 ? Math.round((filledCount / totalCells) * 100) : 0;

  return (
    <main className="min-h-dvh bg-[#fcfcfc] font-sans">

      {/* Header */}
      <header className="bg-white border-b border-[#eeeeee] shadow-[0_1px_4px_rgba(0,0,0,0.06)] pt-safe">
        <div className="max-w-6xl mx-auto px-4 md:px-6 h-14 flex items-center gap-2 md:gap-4">
          <LightButton
            onClick={() => { gameActiveRef.current = false; setGameMode(null); }}
            className="px-4 py-1.5 text-sm"
          >
            ← Back
          </LightButton>

          <div className="flex-1 text-center">
            <span className="text-base font-black tracking-[0.04em] text-[#1e1e1e]">SoChi BLOCKS</span>
            <span className="text-[#888888] text-sm font-semibold mx-2">·</span>
            <span className="text-sm font-semibold text-[#666666]">
              {N}×{N}×{N}  Lv {configRef.current.level} – {LEVEL_LABELS[configRef.current.level]}
              {configRef.current.mode === 'daily' && ' · Daily'}
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Best time badge (solo/daily only) */}
            {(configRef.current.mode === 'solo' || configRef.current.mode === 'daily') && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border bg-[#e8f5e9] border-[#a5d6a7] text-[#2e7d32] text-sm font-bold">
                <Trophy className="w-3.5 h-3.5" />
                Best: {bestTimeDisplay !== null ? fmtTime(bestTimeDisplay) : '--:--'}
              </div>
            )}

            {/* Timer (M2) */}
            <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-sm font-bold ${timerClass}`}>
              <Timer className="w-3.5 h-3.5" />
              {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
            </div>
          </div>
        </div>

        {/* Progress bar (H2) */}
        <div className="h-1.5 bg-[#f5f5f5]">
          <div
            className="h-full bg-[#333333] transition-all duration-500"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </header>

      {/* Score bar */}
      <div className="bg-[#f5f5f5] border-b border-[#eeeeee]">
        <div className="max-w-6xl mx-auto px-6 py-3 grid grid-cols-3 gap-4 items-center">
          {[1, 2].map(pid => {
            const isActive = currentPlayer === pid;
            const label = pid === 1 ? 'Player 1' : p2Label;
            const Icon = pid === 2 && configRef.current.mode === 'versus-cpu' ? Cpu : User;
            return (
              <div key={pid} className={`relative flex items-center gap-3 px-4 py-2 rounded-xl border overflow-hidden transition-all ${
                isActive ? 'bg-white border-[#333333] shadow-sm' : 'bg-transparent border-transparent opacity-50'
              } ${pid === 2 ? 'justify-end' : ''}`}>
                <div className="w-7 h-7 rounded-lg bg-[#f5f5f5] flex items-center justify-center">
                  <Icon className="w-4 h-4 text-[#333333]" />
                </div>
                <div>
                  <div className="text-[10px] font-black uppercase tracking-widest text-[#888888]">{label}</div>
                  <div className="text-xl font-black text-[#1e1e1e]">{scores[pid]}</div>
                </div>
                {combos[pid] > 1 && (
                  <span
                    key={combos[pid]}
                    className="ml-auto text-[10px] font-black text-[#2e7d32] bg-[#e8f5e9] px-2 py-0.5 rounded-full animate-combo-pop"
                  >
                    {combos[pid]}x
                  </span>
                )}
                {/* H3: Combo shrink bar */}
                {combos[pid] > 0 && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-transparent">
                    <div
                      key={lastSuccessTimes[pid]}
                      className="h-full w-full bg-[#2ec47a] animate-combo-shrink"
                    />
                  </div>
                )}
              </div>
            );
          })}

          <div className="text-center order-first md:order-none col-start-2 row-start-1">
            <div className="text-xs font-bold text-[#888888] uppercase tracking-widest">
              {isCpuThinking ? "CPU 思考中..." : `Player ${currentPlayer} のターン`}
            </div>
            {/* H2: filled count */}
            <div className="text-[10px] text-[#aaaaaa] mt-0.5">
              {filledCount} / {totalCells}
            </div>
          </div>
        </div>
      </div>

      {/* Main */}
      <div className="max-w-6xl mx-auto px-4 md:px-6 py-4 md:py-8 grid grid-cols-1 lg:grid-cols-4 gap-4 md:gap-8">

        {/* 3D cube */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <HyperCube
            board={board}
            N={N}
            onCellClick={handleCellClick}
            selectedPos={selectedPos}
            lastPlacedPos={lastPlacedPos}
            isShaking={isShaking && (configRef.current.mode === 'solo' || configRef.current.mode === 'daily' || !isCpuThinking)}
            layerFilter={layerFilter}
            flashingCells={flashingCells}
            flashStartTime={flashStartTime}
            hintPos={hintPos}
            justPlacedPos={justPlacedPos}
            justPlacedTime={justPlacedTime}
            hintCellKeys={hintCellKeys}
          />

          {/* Slice display controller */}
          <div className="bg-white border border-[#dddddd] rounded-xl px-5 py-4 shadow-sm">
            <div className="flex items-center gap-3 flex-wrap">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-[#888888]" />
                <span className="text-xs font-black uppercase tracking-widest text-[#888888]">
                  スライス表示
                </span>
              </div>

              <button
                onClick={() => setLayerFilter(lf => lf ? null : { axis: 'z', index: 0 })}
                className={`px-3 py-1 rounded-lg text-xs font-bold border transition-colors ${
                  layerFilter
                    ? 'bg-[#333333] text-white border-[#333333]'
                    : 'bg-white text-[#666666] border-[#dddddd] hover:border-[#333333]'
                }`}
              >
                {layerFilter ? 'ON' : 'OFF'}
              </button>

              {layerFilter && (
                <>
                  <div className="flex gap-1">
                    {(['x', 'y', 'z'] as const).map(ax => (
                      <button
                        key={ax}
                        onClick={() => setLayerFilter({ axis: ax, index: 0 })}
                        className={`w-10 h-10 rounded-lg text-xs font-black border transition-colors ${
                          layerFilter.axis === ax
                            ? 'bg-[#333333] text-white border-[#333333]'
                            : 'bg-white text-[#666666] border-[#dddddd] hover:border-[#333333]'
                        }`}
                      >
                        {ax.toUpperCase()}
                      </button>
                    ))}
                  </div>

                  <div className="flex items-center gap-1">
                    <span className="text-xs text-[#888888]">層:</span>
                    {Array.from({ length: N }, (_, i) => i).map(idx => (
                      <button
                        key={idx}
                        onClick={() => setLayerFilter(lf => lf ? { ...lf, index: idx } : null)}
                        className={`w-10 h-10 rounded-lg text-xs font-bold border transition-colors ${
                          layerFilter.index === idx
                            ? 'bg-[#333333] text-white border-[#333333]'
                            : 'bg-white text-[#666666] border-[#dddddd] hover:border-[#333333]'
                        }`}
                      >
                        {idx + 1}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Analysis panel */}
          <div className={`bg-white border rounded-xl p-5 transition-all duration-200 shadow-sm ${
            successFlash ? 'border-[#a5d6a7] shadow-[0_0_0_3px_rgba(46,125,50,0.10)]' : 'border-[#dddddd]'
          }`}>
            <h2 className="text-[10px] font-black uppercase tracking-widest text-[#888888] mb-3">Analysis</h2>
            <p className="text-sm text-[#666666] leading-relaxed mb-3">
              {selectedPos ? (
                <>
                  選択中: <span className="font-bold text-[#1e1e1e]">({selectedPos[0]+1},{selectedPos[1]+1},{selectedPos[2]+1})</span>
                  {"  "}候補: <span className="font-bold text-[#2e7d32]">
                    {engineRef.current?.getCandidates(selectedPos).join(", ") || "なし"}
                  </span>
                </>
              ) : "セルをタップして選択してください。"}
            </p>
            {/* M3: Number buttons with completion indicator */}
            <div className="flex gap-2">
              {Array.from({ length: N }, (_, i) => i + 1).map(n => {
                const isCandidate = selectedPos ? engineRef.current?.getCandidates(selectedPos).includes(n) : false;
                const col = NUMBER_COLORS[n] ?? "#999";
                const isDone = numberCounts[n] >= N * N;
                return (
                  <div key={n} className="relative">
                    <button
                      title={`数字 ${n} を選択 (キー: ${n})`}
                      onClick={() => setCurrentNumber(n)}
                      style={currentNumber === n ? { background: col, borderColor: col } : {}}
                      className={`w-10 h-10 rounded-lg flex items-center justify-center text-sm font-black border transition-all cursor-pointer hover:scale-105 active:scale-95 ${
                        isDone
                          ? 'bg-[#f5f5f5] border-[#eeeeee] text-[#cccccc] cursor-default'
                          : currentNumber === n
                            ? 'text-white scale-110 shadow-md'
                            : isCandidate
                              ? 'bg-[#e8f5e9] border-[#a5d6a7] text-[#2e7d32] hover:shadow-sm'
                              : 'bg-[#f5f5f5] border-[#eeeeee] text-[#aaaaaa] hover:border-[#cccccc]'
                      }`}
                    >
                      {isDone ? <CheckCircle2 className="w-4 h-4 text-[#a5d6a7]" /> : n}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="flex flex-col gap-4">
          {/* Current target */}
          <div className="bg-white border border-[#dddddd] rounded-xl p-5 shadow-sm text-center">
            <h2 className="text-[10px] font-black uppercase tracking-widest text-[#888888] mb-4">Next Number</h2>
            <div
              className="flex items-center justify-center h-24 rounded-xl border-2"
              style={{ borderColor: numColor, background: numColor + "18" }}
            >
              <span className="text-6xl font-black" style={{ color: numColor }}>{currentNumber}</span>
            </div>
          </div>

          {/* Controls */}
          <div className="grid grid-cols-2 gap-3">
            <LightButton
              onClick={() => { gameActiveRef.current = false; setGameMode(null); }}
              className="flex flex-col items-center justify-center gap-1.5 h-20 text-xs"
            >
              <RotateCcw className="w-5 h-5" />
              Quit
            </LightButton>
            <button
              onClick={() => setShowRules(true)}
              className="flex flex-col items-center justify-center gap-1.5 h-20 bg-[#f0f4f8] hover:bg-[#dce8f5] text-[#2b6cb0] font-semibold rounded-lg border border-[#c3d9f0] text-xs transition-colors"
            >
              <HelpCircle className="w-5 h-5" />
              Rules
            </button>
          </div>

          {/* Hint button */}
          <button
            onClick={handleHint}
            disabled={!!hintPos || isStuck || boardComplete || isGameOver}
            className={`w-full flex items-center justify-center gap-2 py-3 rounded-lg border text-sm font-bold transition-all ${
              hintPos
                ? 'bg-[#fffbeb] border-[#fcd34d] text-[#b45309] opacity-70 cursor-not-allowed'
                : 'bg-[#fffbeb] hover:bg-[#fef3c7] border-[#fcd34d] text-[#b45309] hover:shadow-sm active:scale-95'
            }`}
          >
            <Lightbulb className="w-4 h-4" />
            {hintPos ? 'ヒント表示中...' : 'Hint'}
          </button>

          {/* Undo button */}
          <button
            onClick={handleUndo}
            disabled={!canUndo || boardComplete}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-lg border text-sm font-semibold transition-all bg-white hover:bg-[#f5f5f5] border-[#dddddd] text-[#666666] disabled:opacity-30 disabled:cursor-not-allowed active:scale-95"
          >
            <Undo2 className="w-4 h-4" />
            Undo
          </button>

          {/* Instructions */}
          <div className="bg-white border border-[#dddddd] rounded-xl p-5 shadow-sm">
            <h2 className="text-[10px] font-black uppercase tracking-widest text-[#888888] mb-3">操作方法</h2>
            <p className="text-sm text-[#666666] leading-relaxed">
              セルを<strong className="text-[#1e1e1e]">1回</strong>で選択、
              <strong className="text-[#1e1e1e]">再タップ</strong>で配置。
              {configRef.current.mode !== 'solo' && configRef.current.mode !== 'daily' && (
                <> {p2Label}と交互にプレイします。</>
              )}
            </p>
          </div>

          {/* Settings info */}
          <div className="bg-[#f5f5f5] border border-[#eeeeee] rounded-xl p-4">
            <h2 className="text-[10px] font-black uppercase tracking-widest text-[#888888] mb-2">設定</h2>
            <div className="space-y-1 text-xs text-[#666666]">
              <div>サイズ: <strong className="text-[#1e1e1e]">{N}×{N}×{N}</strong></div>
              <div>難易度: <strong className="text-[#1e1e1e]">{LEVEL_LABELS[configRef.current.level]}</strong></div>
              {configRef.current.mode === 'versus-cpu' && (
                <div>CPU: <strong className="text-[#1e1e1e]">{CPU_LABEL[configRef.current.level]}</strong></div>
              )}
              {configRef.current.mode === 'daily' && (
                <div>シード: <strong className="text-[#1e1e1e]">{todaySeed()}</strong></div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Rules modal */}
      {showRules && (
        <RulesModal N={N} onClose={() => setShowRules(false)} />
      )}

      {/* VS Human: turn handoff screen */}
      {showHandoff && !isGameOver && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-40 cursor-pointer"
          onClick={() => setShowHandoff(false)}
        >
          <div className="bg-white rounded-2xl shadow-2xl p-10 text-center max-w-xs w-full mx-4 pointer-events-none">
            <div className="w-16 h-16 rounded-2xl bg-[#f5f5f5] flex items-center justify-center mx-auto mb-5">
              <Users className="w-8 h-8 text-[#333333]" />
            </div>
            <h2 className="text-2xl font-black text-[#1e1e1e] mb-2">
              Player {currentPlayer} の番
            </h2>
            <p className="text-sm text-[#888888] mb-6">
              画面をタップして開始してください
            </p>
            <div className="w-full h-1 bg-[#f5f5f5] rounded-full overflow-hidden">
              <div className="h-full bg-[#333333] rounded-full" style={{ width: '100%' }} />
            </div>
          </div>
        </div>
      )}

      {/* Game Over / Clear overlay */}
      {isGameOver && (
        <>
          {!showGameOverOverlay && (
            <button
              onClick={() => setShowGameOverOverlay(true)}
              className="fixed left-1/2 -translate-x-1/2 z-50 bg-[#333333] text-white px-6 py-3 rounded-full font-bold text-sm flex items-center gap-2 shadow-lg hover:bg-[#555555] transition-colors"
              style={{ bottom: "max(2rem, env(safe-area-inset-bottom, 0px) + 0.5rem)" }}
            >
              <Trophy className="w-4 h-4 text-yellow-400" />
              結果を見る
            </button>
          )}

          {showGameOverOverlay && (
            <div className="fixed inset-0 bg-black/45 backdrop-blur-sm flex items-center justify-center z-50 p-8">
              {/* M1: celebrate-pop animation on board clear */}
              <div className={`bg-white rounded-2xl shadow-2xl max-w-sm w-full p-8 text-center ${boardComplete ? 'animate-celebrate-pop' : ''}`}>
                <Trophy className={`w-16 h-16 mx-auto mb-4 ${boardComplete ? 'text-yellow-500' : 'text-[#888888]'}`} />
                <h1 className={`text-3xl font-black mb-1 ${boardComplete ? 'text-[#2e7d32]' : 'text-[#1e1e1e]'}`}>
                  {boardComplete ? "クリア！" : isStuck ? "手詰まり" : "時間切れ"}
                </h1>
                <p className="text-sm text-[#888888] uppercase tracking-widest font-semibold mb-3">
                  {boardComplete ? "Puzzle Complete" : isStuck ? "No Valid Moves" : "Time Expired"}
                </p>

                {/* Stuck reason */}
                {isStuck && stuckNumbers.length > 0 && (
                  <div className="mb-5 bg-[#fff5f5] border border-[#feb2b2] rounded-xl px-4 py-3 text-sm text-left">
                    <p className="font-bold text-[#c53030] mb-1.5">置けなくなった数字:</p>
                    <div className="flex gap-2 flex-wrap">
                      {stuckNumbers.map(n => (
                        <span
                          key={n}
                          className="inline-flex items-center justify-center w-8 h-8 rounded-lg text-white text-sm font-black"
                          style={{ background: ({ 1:'#2d7ee8',2:'#2ec47a',3:'#e84444',4:'#f5a623',5:'#9b5de5' } as Record<number,string>)[n] ?? '#888' }}
                        >
                          {n}
                        </span>
                      ))}
                    </div>
                    <p className="text-xs text-[#888888] mt-2">
                      これらの数字が置けるセルがなくなりました。Undo で直前の手に戻れます。
                    </p>
                  </div>
                )}

                {/* Clear time & record */}
                {boardComplete && (configRef.current.mode === 'solo' || configRef.current.mode === 'daily') && clearTime !== null && (
                  <div className="mb-5">
                    <div className="text-2xl font-black text-[#1e1e1e]">{fmtTime(clearTime)}</div>
                    <div className="text-xs text-[#888888] mt-0.5">クリアタイム</div>
                    {isNewBest && (
                      <div className="mt-2 inline-flex items-center gap-1.5 bg-[#e8f5e9] border border-[#a5d6a7] text-[#2e7d32] text-xs font-black px-3 py-1 rounded-full">
                        <Trophy className="w-3 h-3" /> 新記録！
                      </div>
                    )}
                    {!isNewBest && bestTimeDisplay !== null && (
                      <div className="text-xs text-[#888888] mt-1">Best: {fmtTime(bestTimeDisplay)}</div>
                    )}
                  </div>
                )}

                <div className="bg-[#f5f5f5] rounded-xl p-6 mb-6 space-y-3 text-left">
                  <div className="flex justify-between items-center pb-3 border-b border-[#eeeeee]">
                    <span className="text-xs font-black uppercase tracking-widest text-[#888888]">Player 1</span>
                    <span className="text-2xl font-black text-[#1e1e1e]">{scores[1]}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-black uppercase tracking-widest text-[#888888]">{p2Label}</span>
                    <span className="text-2xl font-black text-[#1e1e1e]">{scores[2]}</span>
                  </div>
                  {!boardComplete && (
                    <div className="pt-3 border-t border-[#eeeeee]">
                      {winner ? (
                        <div className="bg-[#e8f5e9] border border-[#a5d6a7] rounded-lg px-4 py-2 text-center">
                          <div className="text-[10px] font-black uppercase tracking-widest text-[#888888] mb-0.5">Winner</div>
                          <div className="text-lg font-black text-[#2e7d32]">{winner}</div>
                        </div>
                      ) : (
                        <div className="bg-[#f5f5f5] border border-[#dddddd] rounded-lg px-4 py-2 text-center">
                          <div className="text-sm font-bold text-[#666666]">引き分け</div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className={`grid gap-3 ${isStuck && canUndo ? 'grid-cols-3' : 'grid-cols-2'}`}>
                  {isStuck && canUndo && (
                    <button
                      onClick={() => { handleUndo(); setShowGameOverOverlay(false); }}
                      className="py-3 text-sm flex items-center justify-center gap-1.5 bg-[#fffbeb] hover:bg-[#fef3c7] border border-[#fcd34d] text-[#b45309] font-bold rounded-lg transition-colors"
                    >
                      <Undo2 className="w-4 h-4" /> Undo
                    </button>
                  )}
                  <DarkButton
                    onClick={() => startGame(configRef.current.mode, configRef.current.N, configRef.current.level)}
                    className="py-3 text-sm"
                  >
                    もう一度
                  </DarkButton>
                  <LightButton
                    onClick={() => { gameActiveRef.current = false; setGameMode(null); }}
                    className="py-3 text-sm"
                  >
                    設定に戻る
                  </LightButton>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </main>
  );
}
