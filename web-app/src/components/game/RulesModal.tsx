"use client";

interface RulesModalProps {
  N: number;
  onClose: () => void;
}

/** Small coloured badge for axis labels */
function AxisBadge({ label, color }: { label: string; color: string }) {
  return (
    <span
      className="inline-flex items-center justify-center w-7 h-7 rounded-md font-black text-white text-xs"
      style={{ background: color }}
    >
      {label}
    </span>
  );
}

/** A mini ASCII-style grid showing one axis rule */
function AxisRule({
  axis,
  color,
  desc,
  example,
}: {
  axis: string;
  color: string;
  desc: string;
  example: string[];
}) {
  return (
    <div className="bg-[#f5f5f5] rounded-xl p-4 flex gap-4 items-start">
      <AxisBadge label={axis} color={color} />
      <div className="flex-1">
        <p className="text-sm font-bold text-[#1e1e1e] mb-1">{axis} 軸方向のライン</p>
        <p className="text-xs text-[#666666] mb-2">{desc}</p>
        <div className="flex gap-1.5">
          {example.map((cell, i) => (
            <div
              key={i}
              className={`w-8 h-8 rounded-md flex items-center justify-center text-sm font-black border-2 ${
                cell === "?"
                  ? "bg-white border-dashed border-[#cccccc] text-[#888888]"
                  : "text-white border-transparent"
              }`}
              style={cell !== "?" ? { background: color, opacity: 0.85 } : {}}
            >
              {cell}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function RulesModal({ N, onClose }: RulesModalProps) {
  const nums = Array.from({ length: N }, (_, i) => String(i + 1));
  const q = "?";

  return (
    <div
      className="fixed inset-0 bg-black/45 backdrop-blur-sm flex items-center justify-center z-50 p-6"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-[#eeeeee]">
          <div>
            <h2 className="text-xl font-black text-[#1e1e1e]">ゲームルール</h2>
            <p className="text-xs text-[#888888] mt-0.5">
              {N}×{N}×{N} Hyper-Cube Sudoku
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-lg bg-[#f5f5f5] hover:bg-[#eeeeee] flex items-center justify-center text-[#666666] font-bold text-lg transition-colors"
          >
            ✕
          </button>
        </div>

        <div className="px-6 py-5 space-y-5">

          {/* Overview */}
          <section>
            <h3 className="text-xs font-black uppercase tracking-widest text-[#888888] mb-3">
              基本ルール
            </h3>
            <div className="bg-[#f0f4f8] border border-[#c3d9f0] rounded-xl p-4">
              <p className="text-sm text-[#1e1e1e] leading-relaxed font-medium">
                {N}×{N}×{N} の立体キューブに数字{" "}
                <strong>1〜{N}</strong> を配置します。<br />
                <strong>X・Y・Z の 3 軸すべて</strong>において、
                同じラインに同じ数字が{" "}
                <span className="text-[#e53e3e] font-black">重複してはいけません</span>。
              </p>
            </div>
          </section>

          {/* Axis rules */}
          <section>
            <h3 className="text-xs font-black uppercase tracking-widest text-[#888888] mb-3">
              軸ごとのルール
            </h3>
            <div className="space-y-3">
              <AxisRule
                axis="X"
                color="#2d7ee8"
                desc="X 方向のライン（横一列）に同じ数字を置けません。"
                example={[...nums.slice(0, N - 1), q]}
              />
              <AxisRule
                axis="Y"
                color="#2ec47a"
                desc="Y 方向のライン（縦一列）に同じ数字を置けません。"
                example={[nums[0], q, ...nums.slice(1, N - 1)]}
              />
              <AxisRule
                axis="Z"
                color="#e84444"
                desc="Z 方向のライン（奥行き一列）に同じ数字を置けません。"
                example={[q, ...nums.slice(0, N - 1)]}
              />
            </div>
          </section>

          {/* How to play */}
          <section>
            <h3 className="text-xs font-black uppercase tracking-widest text-[#888888] mb-3">
              操作方法
            </h3>
            <ol className="space-y-2">
              {[
                ["1回タップ", "セルを選択（オレンジ枠で強調）"],
                ["再タップ", "選択中のセルに Next Number を配置"],
                ["数字キー 1〜" + N, "配置したい数字を直接選択（キーボード）"],
                ["スライス表示", "特定の層だけを表示して内部を確認"],
                ["ドラッグ", "3D キューブを自由に回転"],
              ].map(([key, val]) => (
                <li key={key} className="flex gap-3 text-sm">
                  <span className="shrink-0 inline-block bg-[#333333] text-white text-[10px] font-black px-2 py-0.5 rounded-md mt-0.5">
                    {key}
                  </span>
                  <span className="text-[#666666]">{val}</span>
                </li>
              ))}
            </ol>
          </section>

          {/* Scoring */}
          <section>
            <h3 className="text-xs font-black uppercase tracking-widest text-[#888888] mb-3">
              スコアリング
            </h3>
            <div className="space-y-2 text-sm text-[#666666]">
              <div className="flex justify-between">
                <span>1マス配置成功</span>
                <span className="font-bold text-[#1e1e1e]">+10 pt</span>
              </div>
              <div className="flex justify-between">
                <span>コンボボーナス（5秒以内連続）</span>
                <span className="font-bold text-[#2e7d32]">+5〜50 pt</span>
              </div>
              <div className="flex justify-between border-t border-[#eeeeee] pt-2 mt-2">
                <span className="text-[#888888] text-xs">
                  ※ VS モードでは時間切れ・手詰まり時のスコアで勝敗を決定
                </span>
              </div>
            </div>
          </section>

        </div>

        {/* Footer */}
        <div className="px-6 pb-6">
          <button
            onClick={onClose}
            className="w-full bg-[#333333] hover:bg-[#555555] text-white font-bold py-3 rounded-lg transition-colors"
          >
            閉じる
          </button>
        </div>
      </div>
    </div>
  );
}
