# UI Helpers & Logger – Test Cases **(責務 ↔ 観点 ↔ 実装状況対応版)**

UI 描画ヘルパ & ロギング層の **「各メソッドの責務」**と、
それを検証する**テスト観点**、そして\*\*実装状況（テスト名）\*\*を 1 対 1 対応で記述しています。

---

## 1️⃣ 単体テスト (Unit)

### 1.1 `Cube3DWidget` – 描画/入力ヘルパ群

| ID         | メソッド                     | 責務 (What)   | テスト観点 (Why / How)   | 入力例                | 期待結果                | 実装状況                                      |
| ---------- | ------------------------ | ----------- | ------------------- | ------------------ | ------------------- | ----------------------------------------- |
| UI-SEL-01  | `_get_cell_at_touch`     | 座標をセルにマッピング | 中央ヒットで正変換           | `(150,220)`        | `(1,1,1)` を返す       | ✅ `test_ui_sel_01_get_cell_at_touch_hit`  |
| UI-SEL-02  | "                        | 同上          | 境界外クリックを無視          | `(-10,0)`          | `None`              | ✅ `test_ui_sel_02_get_cell_at_touch_miss` |
| UI-HL-01   | `_handle_cell_selection` | ハイライト処理     | 初回選択で index セット     | `(0,0,0)`          | `selected_index` 反映 | ❌ 未検出                                     |
| UI-HL-02   | "                        | 既選択セルで入力    | attempt\_input 呼出確認 | 連続タップ              | callback 呼出         | ❌ 未検出                                     |
| UI-DRW-01  | `_draw_cube`             | 全体描画        | 描画命令生成され例外なし        | —                  | Canvas 指示あり         | ❌ 未検出                                     |
| UI-DRW-02  | `_draw_slice_view`       | スライス描画      | 軸・深度変更で再描画          | 軸 `Z`, depth 2     | Canvas 再構築          | ❌ 未検出                                     |
| UI-RW-01   | `redraw`                 | 全面再描画       | 状態遷移後 redraw 呼出     | board 更新後          | 状態反映                | ❌ 未検出                                     |
| UI-INFO-01 | `redraw_info`            | 数列・スコア表示    | 数字更新時にラベル反映         | `current_number=5` | ラベル text "5"        | ❌ 未検出                                     |

#### 描画細分化メソッド（検証視点のみ記述）

| メソッド                 | 責務     | 代表テスト観点                | 実装状況  |
| -------------------- | ------ | ---------------------- | ----- |
| `_draw_numbers`      | 数字描画   | 入力=3 → テキスト "3" が指示される | ❌ 未検出 |
| `_draw_grid`         | グリッド描画 | セル数に応じ Line 数が変化       | ❌ 未検出 |
| `_draw_highlight`    | ハイライト  | index=(1,1,1) → 矩形が一致  | ❌ 未検出 |
| `_draw_text_in_cell` | 文字描画   | box サイズに応じ ±1px に収まる   | ❌ 未検出 |

### 1.2 UI コールバック & タイマー

| ID        | メソッド                        | 責務       | テスト観点         | 期待              | 実装状況                                        |
| --------- | --------------------------- | -------- | ------------- | --------------- | ------------------------------------------- |
| UI-CB-01  | `set_on_success_input`      | 成功入力通知登録 | 登録後に呼ばれるか     | callback 呼出し 1回 | ✅ `test_ui_cb_01_set_on_success_input`      |
| UI-CB-02  | `set_timer_update_callback` | タイマー更新通知 | Clockモックで定期呼出 | 秒数に応じ呼出し        | ✅ `test_ui_cb_02_set_timer_update_callback` |
| UI-SKP-01 | `_on_number_skipped`        | スキップUI反映 | スキップ後ラベル変更    | "Skipped" 表示    | ✅ `test_ui_skp_01_on_number_skipped`        |

### 1.3 `AppLogger` / `ConsoleLogger`

| ID        | メソッド                     | 責務            | テスト観点            | 期待                        | 実装状況                                   |
| --------- | ------------------------ | ------------- | ---------------- | ------------------------- | -------------------------------------- |
| LG-INI-01 | `AppLogger.__init__`     | ハンドラー2種の生成    | ハンドラー数 = 2       | `len(logger.handlers)==2` | ✅ `test_lg_ini_01_app_logger_init`     |
| LG-LV-01  | `set_level`              | ログレベル変更       | DEBUG→INFO に反映   | `logger.level==INFO`      | ✅ `test_lg_lv_01_set_level`            |
| LG-ID-01  | `set_game_id`            | game\_id を付加  | ログに game\_id 追加  | `record.game_id==id`      | ✅ `test_lg_id_01_set_game_id`          |
| LG-GET-01 | `get_logger`             | 名前ごとのシングルトン取得 | 同名で同一オブジェクト      | `logger1 is logger2`      | ✅ `test_lg_get_01_get_logger`          |
| CL-INI-01 | `ConsoleLogger.__init__` | フォーマット設定      | 日付+level+msg 含むか | 書式確認                      | ✅ `test_cl_ini_01_console_logger_init` |

### 1.4 `GameIDFilter`

| ID    | メソッド     | 責務                 | テスト観点         | 期待                      | 実装状況                                  |
| ----- | -------- | ------------------ | ------------- | ----------------------- | ------------------------------------- |
| GF-01 | `filter` | game\_id 有り時付加     | 明示的 game\_id  | `record.game_id==123`   | ✅ `test_gf_01_filter_with_game_id`    |
| GF-02 | "        | game\_id 無し時 N/A付加 | 無指定で 'N/A' 代入 | `record.game_id=='N/A'` | ✅ `test_gf_02_filter_without_game_id` |

---

## 2️⃣ 結合テスト (Integration)

| ID        | 組み合わせ               | 責務             | テスト観点                | 期待             | 実装状況                                                         |
| --------- | ------------------- | -------------- | -------------------- | -------------- | ------------------------------------------------------------ |
| IN-UI-01  | UI ↔ GameController | 成功入力連鎖反映       | 配置→GameState更新→UIラベル | スコア+1 表示       | ✅ `test_on_success_input` + `test_set_score_update_callback` |
| IN-LOG-01 | Logger Filter chain | game\_id 付与一貫性 | 複数ハンドラで同一 game\_id   | Console/File同値 | ❌ 未検出                                                        |

---

## 3️⃣ 総合テスト (E2E – UI 視点)

| ID        | シナリオ          | 責務         | テスト観点 & 成功条件                        | 実装状況                                         |
| --------- | ------------- | ---------- | ----------------------------------- | -------------------------------------------- |
| UI-SYS-01 | ピンチズーム        | 3D ビューを縮放  | 2本指ズーム → zoom 変化し redraw される        | ✅ `test_ui_sys_01_pinch_zoom`                |
| UI-SYS-02 | キューブ回転ドラッグ    | 角度更新・描画反映  | ドラッグ操作で `angle_x/y` 更新 & 角度が変化      | ✅ `test_ui_sys_02_drag_rotation`             |
| UI-SYS-03 | スライス切替        | 表示スライスの更新  | ボタン押下で `slice_axis/depth` 変更 & 描画反映 | ✅ `test_ui_sys_03_slice_switch`              |
| UI-SYS-04 | ハイライト＋数字配置    | 配置後ハイライト解除 | 正解セル配置 → highlight OFF & 盤面更新       | ✅ `test_ui_sys_04_place_and_clear_highlight` |
| UI-SYS-05 | ゲームオーバー Popup | 終了UI表示     | `is_game_over==True` → popup 表示     | ✅ `test_show_game_over_popup_player1_wins`   |

---

### 凡例

| アイコン | 意味                |
| ---- | ----------------- |
| ✅    | 実装済み & `.xml`で確認済 |
| ❌    | 未実装 or `.xml`未検出  |
