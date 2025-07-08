# GameState & Core Logic – Comprehensive Test Cases

本ドキュメントでは **ビジネスロジックの中心を成すモジュール**（`GameState`, `Player`, `CubeLogic`, `FieldAdapter`/`Field`, `CpuPlayer`, `Scramble`, 主要サービス層）に対して、ユニット・結合・総合（E2E）テストを網羅的に整理します。

> **軽量メソッド（純粋 getter / setter / 定数返却）は "共通ユーティリティテスト" に一括まとめ** とし、重複を避けています。

---

## 1️⃣ 単体テスト (Unit)

### 1.1 `Player` クラス

| ID    | メソッド          | 観点   | 入力         | 期待結果                 | 実装状況                              |
| ----- | ------------- | ---- | ---------- | -------------------- | --------------------------------- |
| PL-01 | `add_score`   | 正常加算 | `value=5`  | `score` が +5         | ✅ `test_add_score_normal`         |
| PL-02 | "             | 0加算  | `value=0`  | 変化なし                 | ✅ `test_add_score_zero`           |
| PL-03 | "             | 負数防御 | `value=-1` | `ValueError` 発生      | ✅ `test_add_score_negative_value` |
| PL-04 | `reset_score` | リセット | —          | `score=0`, `combo=0` | ✅ `test_reset_score`              |

### 1.2 `GameState` クラス

| ID       | サブ領域           | テスト観点       | 期待                                     | 実装状況                                                 |
| -------- | -------------- | ----------- | -------------------------------------- | ---------------------------------------------------- |
| GS-CN-01 | `create_nums`  | ヒント除外       | 初期配置に含む `num` がシーケンスに無い                | ✅ `test_create_nums_hint_exclusion`                  |
| GS-CN-02 | "              | シャッフル再現     | 同一 seed ⇒ 同順序                          | ✅ `test_create_nums_shuffle_reproducibility`         |
| GS-NT-01 | `next_turn`    | プレイヤー切替     | `current_player` トグル                   | ✅ `test_next_turn`                                   |
| GS-NT-02 | "              | シーケンス短縮     | `len(nums)` が -1                       | ✅ `test_next_turn_sequence_shortens`                 |
| GS-SK-01 | `skip_turn`    | スコア減算 & ターン | `score`‑1 & `next_turn` 呼出し            | ✅ `test_skip_turn` / `test_skip_turn_max_skip_count` |
| GS-TM-01 | `timer`        | 期限切れ        | `elapsed >= limit` → `is_time_up=True` | ✅ `test_timer_expiration`                            |
| GS-GO-01 | `is_game_over` | 完成盤面        | 盤面フル ⇒ True                            | ✅ `test_is_game_over_all_cells_filled`               |
| GS-GO-02 | "              | 配置不能        | `can_place_number=False` ⇒ True        | ✅ `test_is_game_over_no_valid_placement`             |

### 1.3 `FieldAdapter` & `Field`

| ID       | メソッド      | 観点    | 期待                     | 実装状況                       |
| -------- | --------- | ----- | ---------------------- | -------------------------- |
| FA-CK-01 | `check`   | OK 位置 | `(True, "OK")`         | ✅ `test_check_ok_position` |
| FA-CK-02 | "         | 重複    | `(False, "duplicate")` | ✅ `test_check_duplicate`   |
| FA-RF-01 | `reflect` | 候補更新  | 行・列・柱候補数 ‑1            | ✅ `test_reflect`           |
| FA-RS-01 | `reset`   | 初期化   | `board` All `None`     | ✅ `test_reset`             |

### 1.4 `CubeLogic`

| ID       | メソッド               | 観点     | 期待                                | 実装状況                                  |
| -------- | ------------------ | ------ | --------------------------------- | ------------------------------------- |
| CL-AI-01 | `attempt_input`    | 成功     | True, board 反映                    | ✅ `test_attempt_input_success`        |
| CL-AI-02 | "                  | 重複セル   | False + `last_error='duplicate'`  | ✅ `test_attempt_input_duplicate_cell` |
| CL-AI-03 | "                  | 範囲外    | False + `last_error='invalidPos'` | ✅ `test_attempt_input_out_of_range`   |
| CL-CP-01 | `can_place_number` | 置き場所あり | True                              | ✅ `test_can_place_number_true`        |
| CL-CP-02 | "                  | 全滅     | False                             | ✅ `test_can_place_number_false`       |
| CL-RS-01 | `reset`            | 盤面クリア  | 全 `None` + `last_error=''`        | ✅ `test_reset`                        |

### 1.5 `CpuPlayer`

| ID     | 観点                 | 期待                         | 実装状況                                      |
| ------ | ------------------ | -------------------------- | ----------------------------------------- |
| CPU-01 | 可動セル有              | `make_move` True & board更新 | ✅ `test_make_move_success`                |
| CPU-02 | 配置不可               | False                      | ✅ `test_make_move_no_placement`           |
| CPU-03 | 非法`current_number` | `ValueError`               | ✅ `test_make_move_invalid_current_number` |

### 1.6 `Scramble`

| ID    | 観点     | 期待               | 実装状況                                         |
| ----- | ------ | ---------------- | -------------------------------------------- |
| SC-01 | seed再現 | 同seed ⇒ 同盤面      | ✅ `test_scramble_board_seed_reproducibility` |
| SC-02 | 完成維持   | シャッフル後も行/列/柱ユニーク | ✅ `test_scramble_board_maintains_uniqueness` |

### 1.7 共通ユーティリティテスト

* 対象: 純粋 `get_*`, `set_*`, `property` 取得のみのメソッド
* テスト: "呼び出し＝内部状態一致" をパラメタライズで一括検証
* 実装状況: ✅ `test_field.py`, `test_game_state.py` 等にて確認済

---

## 2️⃣ 結合テスト (Integration)

| ID     | 内容                                     | 実装状況                                                                                    |
| ------ | -------------------------------------- | --------------------------------------------------------------------------------------- |
| INT-01 | `CubeLogic → Field → GameState` の成功・失敗 | ✅ `test_successful_input_flow`, `test_failed_input_error_propagation`                   |
| INT-02 | Timer ループ処理                            | ✅ `test_timer_loop`                                                                     |
| INT-03 | CPU配置処理                                | ✅ `test_cpu_interaction_success`, `test_cpu_interaction_no_placement`                   |
| INT-04 | DBランキング操作（正常／異常）                       | ⚠️ `test_get_ranks_all`, `test_get_ranks_by_level`, `test_get_ranks_empty`（初期化漏れにより失敗中） |

---

## 3️⃣ 総合テスト (E2E)

| シナリオ   | 概要        | 成果                   | 実装状況                                    |
| ------ | --------- | -------------------- | --------------------------------------- |
| SYS-01 | タイムアタック勝利 | 勝利Popup, ランク登録       | ⚠️ `test_sys_01_time_attack_win`（スキップ中） |
| SYS-02 | 時間切れ敗北    | GAME\_OVER=TIMEUP    | ✅ `test_sys_02_time_up_lose`            |
| SYS-03 | 配置不可敗北    | GAME\_OVER=NO\_PLACE | ✅ `test_sys_03_no_place_lose`           |
| SYS-04 | 2P対戦      | 勝敗検出                 | ✅ `test_sys_04_two_player_game`         |
| SYS-05 | CPU戦      | 難易度別動作               | ✅ `test_sys_05_cpu_game`                |
| SYS-06 | リセット      | 途中→初期状態              | ✅ `test_sys_06_reset_game`              |

---

### 付録: Fixture / モック

* `RandomSeedContext` / `FakeClock`
* `StubUI` / `TempDB`

---

### 凡例

| アイコン | 意味                |
| ---- | ----------------- |
| ✅    | 実装済み & `.xml`で確認済 |
| ⚠️   | 実装あるが失敗中またはスキップ   |
| ❌    | 未実装（なし）           |
