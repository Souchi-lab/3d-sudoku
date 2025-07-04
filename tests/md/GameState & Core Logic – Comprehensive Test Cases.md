# GameState & Core Logic – Comprehensive Test Cases

本ドキュメントでは **ビジネスロジックの中心を成すモジュール**（`GameState`, `Player`, `CubeLogic`, `FieldAdapter`/`Field`, `CpuPlayer`, `Scramble`, 主要サービス層）に対して、ユニット・結合・総合（E2E）テストを網羅的に整理します。

> **軽量メソッド（純粋 getter / setter / 定数返却）は "共通ユーティリティテスト" に一括まとめ** とし、重複を避けています。

---

## 1️⃣ 単体テスト (Unit)

### 1.1 `Player` クラス

| ID    | メソッド          | 観点   | 入力         | 期待結果                 |
| ----- | ------------- | ---- | ---------- | -------------------- |
| PL-01 | `add_score`   | 正常加算 | `value=5`  | `score` が +5         |
| PL-02 | "             | 0加算  | `value=0`  | 変化なし                 |
| PL-03 | "             | 負数防御 | `value=-1` | `ValueError` 発生      |
| PL-04 | `reset_score` | リセット | —          | `score=0`, `combo=0` |

### 1.2 `GameState` クラス

| ID       | サブ領域               | テスト観点       | 期待                                     |
| -------- | ------------------ | ----------- | -------------------------------------- |
| GS-CN-01 | **create\_nums**   | ヒント除外       | 初期配置に含む `num` がシーケンスに無い                |
| GS-CN-02 | "                  | シャッフル再現     | 同一 seed ⇒ 同順序                          |
| GS-NT-01 | **next\_turn**     | プレイヤー切替     | `current_player` トグル                   |
| GS-NT-02 | "                  | シーケンス短縮     | `len(nums)` が -1                       |
| GS-SK-01 | **skip\_turn**     | スコア減算 & ターン | `score`‑1 & `next_turn` 呼出し            |
| GS-TM-01 | **timer**          | 期限切れ        | `elapsed >= limit` → `is_time_up=True` |
| GS-GO-01 | **is\_game\_over** | 完成盤面        | 盤面フル ⇒ True                            |
| GS-GO-02 | "                  | 配置不能        | `can_place_number=False` ⇒ True        |

> **Getter 共通**：`get_*` 系は *値が内部状態と一致* を1ケースで代表。

### 1.3 `FieldAdapter` & `Field`

| ID       | メソッド      | 観点    | 期待                     |
| -------- | --------- | ----- | ---------------------- |
| FA-CK-01 | `check`   | OK 位置 | `(True, "OK")`         |
| FA-CK-02 | "         | 重複    | `(False, "duplicate")` |
| FA-RF-01 | `reflect` | 候補更新  | 行・列・柱候補数 ‑1            |
| FA-RS-01 | `reset`   | 初期化   | `board` All `None`     |

### 1.4 `CubeLogic`

| ID       | メソッド               | 観点     | 期待                                |
| -------- | ------------------ | ------ | --------------------------------- |
| CL-AI-01 | `attempt_input`    | 成功     | True, board 反映                    |
| CL-AI-02 | "                  | 重複セル   | False + `last_error='duplicate'`  |
| CL-AI-03 | "                  | 範囲外    | False + `last_error='invalidPos'` |
| CL-CP-01 | `can_place_number` | 置き場所あり | True                              |
| CL-CP-02 | "                  | 全滅     | False                             |
| CL-RS-01 | `reset`            | 盤面クリア  | 全 `None` + `last_error=''`        |

### 1.5 `CpuPlayer`

| ID     | 観点                 | 期待                         |
| ------ | ------------------ | -------------------------- |
| CPU-01 | 可動セル有              | `make_move` True & board更新 |
| CPU-02 | 配置不可               | False                      |
| CPU-03 | 非法`current_number` | `ValueError`               |

### 1.6 `Scramble`

| ID    | 観点     | 期待               |
| ----- | ------ | ---------------- |
| SC-01 | seed再現 | 同seed ⇒ 同盤面      |
| SC-02 | 完成維持   | シャッフル後も行/列/柱ユニーク |

### 1.7 **共通ユーティリティテスト**

* 対象: 純粋 `get_*`, `set_*`, `property` 取得のみのメソッド
* テスト: **“呼び出し＝内部状態一致”** をパラメタライズで一括検証

---

## 2️⃣ 結合テスト (Integration)

### 2.1 *CubeLogic ↔ FieldAdapter ↔ GameState*

1. 成功入力 → 反映 → スコア加算 → ターン交替
2. 失敗入力 (重複) → エラー伝搬 → スコア不変

### 2.2 *Timer Loop*

`Clock` モック → `GameState.update_timer` → `GameController` コールバック

### 2.3 *CPU Interaction*

`CpuPlayer.make_move` 成功/失敗パス

### 2.4 *DB ランキング連携*

`add_rank` & `get_ranks` 正常系 / 例外系

---

## 3️⃣ 総合テスト (E2E)

| シナリオ   | 概要        | 分岐                   | 成果                   |
| ------ | --------- | -------------------- | -------------------- |
| SYS-01 | タイムアタック勝利 | —                    | 勝利Popup, ランク登録       |
| SYS-02 | 時間切れ敗北    | —                    | GAME\_OVER=TIMEUP    |
| SYS-03 | 配置不可敗北    | —                    | GAME\_OVER=NO\_PLACE |
| SYS-04 | 2P対戦      | P1>P2 / P2>P1 / Draw |                      |
| SYS-05 | CPU戦      | 難易度別勝敗               |                      |
| SYS-06 | リセット      | 途中→初期状態              |                      |

---

### 付録: Fixture / モック

* `RandomSeedContext` / `FakeClock`
* `StubUI` / `TempDB`

---

> **このファイル単体で `pytest` のテスト設計レビューが可能** です。実装生成は Gemini CLI に移譲してください。
