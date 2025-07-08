### `kivy_cube_app/core/game_state.py`

このファイルは、ゲームの現在の状態（プレイヤー、スコア、ターン、時間、盤面上の数字シーケンスなど）を管理するロジックを含みます。

*   **クラス: `Player`**
    *   **責務**: ゲームに参加する個々のプレイヤーの情報を保持し、スコア管理機能を提供します。
    *   `__init__(self, player_id: int, name: str = "Player") -> None`
        *   **引数**:
            *   `player_id` (int): プレイヤーを一意に識別するID（例: 1, 2）。
            *   `name` (str): プレイヤーの表示名。デフォルトは "Player"。
        *   **戻り値**: なし
        *   **責務**: プレイヤーオブジェクトを初期化します。プレイヤーID、名前、現在のスコア（初期値0）、連続成功回数（初期値0）を設定します。
    *   `add_score(self, value: int = 1) -> None`
        *   **引数**:
            *   `value` (int): 加算するスコアの量。デフォルトは1。
        *   **戻り値**: なし
        *   **責務**: プレイヤーの現在のスコアに指定された値を加算します。
    *   `reset_score(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: プレイヤーのスコアと連続成功回数を0にリセットします。ゲームのリセット時に使用されます。

*   **クラス: `GameState`**
    *   **責務**: ゲーム全体の進行状況、プレイヤーの状態、時間、および盤面に配置される数字のシーケンスを一元的に管理します。ゲームのルール適用や状態遷移のハブとなります。
    *   `__init__(self, N: int, is_ta_mode: bool = False, level: int = 1) -> None`
        *   **引数**:
            *   `N` (int): キューブの一辺のサイズ（例: 3, 4, 5）。ゲームの複雑さを決定します。
            *   `is_ta_mode` (bool): タイムアタックモードかどうかを示すフラグ。デフォルトはFalse。
            *   `level` (int): ゲームの難易度レベル。初期配置の数やTAモードの持ち時間に影響します。デフォルトは1。
        *   **戻り値**: なし
        *   **責務**: ゲームの状態を初期化します。プレイヤー情報、Nの値、TAモード設定、難易度レベル、現在のターン、数字シーケンス、初期配置セル、タイマー関連の変数を設定します。
    *   `_generate_initial_filled_cells(self, level: int) -> list[dict]`
        *   **引数**:
            *   `level` (int): 難易度レベル。
        *   **戻り値**: `list[dict]` - 各辞書は `{"pos": [x, y, z], "value": int}` の形式で、初期配置されるセルの座標と値を示します。
        *   **責務**: 指定された難易度レベルに基づいて、ゲーム開始時に盤面に事前に配置される「ヒントセル」のリストを生成します。`scramble_board` を使用して解決済みのボードを生成し、そこからランダムにヒントを選択します。
    *   `create_nums(self, initial_filled_cells: list[dict]) -> list[int]`
        *   **引数**:
            *   `initial_filled_cells` (list[dict]): 初期配置として既に盤面に置かれているセルの情報。
        *   **戻り値**: `list[int]` - プレイヤーが配置すべき数字のシャッフルされたシーケンス。
        *   **責務**: ゲーム中にプレイヤーが配置する数字のシーケンスを生成します。各数字（1からNまで）をN²個ずつ用意し、全体でN³個の数列を作成します。この際、`initial_filled_cells` に含まれる数字はシーケンスから除外され、重複がないようにします。生成後、数列はシャッフルされます。
    *   `next_turn(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: 現在のプレイヤーを交代させ、数字シーケンスから現在の数字を削除し、次のターンで配置すべき数字を更新します。ゲームのターン進行を管理します。
    *   `get_upcoming(self, count: int | None = None) -> list[int]`
        *   **引数**:
            *   `count` (int | None): 取得する次の数字の数。Noneの場合、残りの全ての数字を返します。
        *   **戻り値**: `list[int]` - 現在の数字以降の、指定された数または全ての数字のリスト。
        *   **責務**: プレイヤーが次に配置できる数字の候補（シーケンスの残り）を提供します。UIでの「次の数字」表示などに利用されます。
    *   `add_score(self, value: int = 1) -> None`
        *   **引数**:
            *   `value` (int): 加算するスコアの量。デフォルトは1。
        *   **戻り値**: なし
        *   **責務**: 現在のターンのプレイヤーのスコアに指定された値を加算します。
    *   `get_score(self, player_id: int) -> int`
        *   **引数**:
            *   `player_id` (int): スコアを取得したいプレイヤーのID。
        *   **戻り値**: `int` - 指定されたプレイヤーの現在のスコア。
        *   **責務**: 特定のプレイヤーの現在のスコアを返します。
    *   `get_current_player(self) -> Player`
        *   **引数**: なし
        *   **戻り値**: `Player` - 現在のターンのプレイヤーオブジェクト。
        *   **責務**: 現在のターンを担当しているプレイヤーのオブジェクトを返します。
    *   `reset_game(self, N: int, is_ta_mode: bool = False, level: int = 1) -> None`
        *   **引数**:
            *   `N` (int): キューブの一辺のサイズ。
            *   `is_ta_mode` (bool): タイムアタックモードかどうか。
            *   `level` (int): 難易度レベル。
        *   **戻り値**: なし
        *   **責務**: ゲームの状態を初期状態にリセットします。スコア、ターン、数字シーケンス、初期配置、タイマーを再初期化し、新しいゲームを開始できる状態にします。
    *   `is_game_over(self, cube_logic: 'CubeLogic') -> bool`
        *   **引数**:
            *   `cube_logic` (`CubeLogic`): キューブのロジックを扱うオブジェクト。セルの埋まり具合や配置可能性のチェックに使用されます。
        *   **戻り値**: `bool` - ゲームが終了条件を満たしている場合はTrue、そうでない場合はFalse。
        *   **責務**: ゲームが終了したかどうかを判定します。全てのセルが埋まった場合、現在の数字を配置できる場所がない場合、またはTAモードで時間切れになった場合にゲームオーバーと判断します。
    *   `start_timer(self, level: int) -> None`
        *   **引数**:
            *   `level` (int): 難易度レベル。TAモードの基本持ち時間を決定します。
        *   **戻り値**: なし
        *   **責務**: タイムアタックモードのタイマーを開始します。指定されたレベルに応じた初期持ち時間を設定し、タイマーの最終更新時刻を記録します。
    *   `update_timer(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: タイムアタックモードの残り時間を更新します。前回の更新からの経過時間を計算し、残り時間から減算します。
    *   `get_elapsed_time(self) -> float`
        *   **引数**: なし
        *   **戻り値**: `float` - 現在の残り時間（秒）。0未満にはなりません。
        *   **責務**: タイムアタックモードにおける現在の残り時間を返します。
    *   `add_time(self, amount: float) -> None`
        *   **引数**:
            *   `amount` (float): 加算する時間（秒）。
        *   **戻り値**: なし
        *   **責務**: タイムアタックモードの残り時間に指定された時間を加算します。
    *   `subtract_time(self, amount: float) -> None`
        *   **引数**:
            *   `amount` (float): 減算する時間（秒）。
        *   **戻り値**: なし
        *   **責務**: タイムアタックモードの残り時間から指定された時間を減算します。
    *   `is_time_up(self) -> bool`
        *   **引数**: なし
        *   **戻り値**: `bool` - 時間切れの場合はTrue、そうでない場合はFalse。
        *   **責務**: タイムアタックモードにおいて、残り時間が0以下になったかどうかを判定します。
    *   `can_skip(self) -> bool`
        *   **引数**: なし
        *   **戻り値**: `bool` - スキップが可能な場合はTrue、そうでない場合はFalse。
        *   **責務**: プレイヤーがターンをスキップできる残り回数があるかどうかを判定します。
    *   `skip_turn(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: プレイヤーがターンをスキップする処理を実行します。スキップ回数を増やし、TAモードでは時間ペナルティとスコアペナルティを適用し、次のターンへ進めます。
    *   `set_number_skip_callback(self, callback_fn: Callable[[int], None]) -> None`
        *   **引数**:
            *   `callback_fn` (`Callable[[int], None]`): 数字がスキップされた際に呼び出される関数。スキップされた数字を引数として受け取ります。
        *   **戻り値**: なし
        *   **責務**: 数字スキップ通知のためのコールバック関数を設定します。
    *   `next_number_only(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: プレイヤーを交代させずに、数字シーケンスの次の数字に進めます。主にCPUプレイヤーが手を見つけられなかった場合などに使用されます。

---

### `kivy_cube_app/core/cube_logic.py`

このファイルは、3Dキューブの盤面における数字の配置、取得、および基本的なルールチェック（有効な座標か、既に埋まっているかなど）を管理するコアロジックを含みます。

*   **クラス: `CubeLogic`**
    *   **責務**: 3D数独の盤面（`_numbers`）の状態を直接管理し、数字の配置、取得、および配置の妥当性に関する基本的なチェック機能を提供します。`FieldAdapter` と連携してより複雑なルールチェックを行います。
    *   `__init__(self, field: 'FieldAdapter', N: int, initial_data: list[dict] | None = None) -> None`
        *   **引数**:
            *   `field` (`FieldAdapter`): 盤面の候補数管理や複雑なルールチェックを行うためのアダプターオブジェクト。
            *   `N` (int): キューブの一辺のサイズ。
            *   `initial_data` (list[dict] | None): ゲーム開始時に既に配置されているセルの情報。各辞書は `{"pos": [x, y, z], "value": int}` の形式。デフォルトはNone。
        *   **戻り値**: なし
        *   **責務**: `CubeLogic` オブジェクトを初期化します。内部的に3D配列 `_numbers` を作成し、全てのセルをNoneで初期化します。`FieldAdapter` のインスタンスとNの値を保持します。`initial_data` が提供された場合、そのデータに基づいて初期セルを盤面に配置し、`FieldAdapter` にも反映させます。
    *   `get_number(self, i: int, j: int, k: int) -> int | None`
        *   **引数**:
            *   `i` (int): X座標（0からN-1）。
            *   `j` (int): Y座標（0からN-1）。
            *   `k` (int): Z座標（0からN-1）。
        *   **戻り値**: `int | None` - 指定された座標に配置されている数字、またはNone（空の場合）。
        *   **責務**: 指定された3D座標にあるセルの現在の数字を返します。
    *   `set_number(self, i: int, j: int, k: int, value: int) -> None`
        *   **引数**:
            *   `i` (int): X座標。
            *   `j` (int): Y座標。
            *   `k` (int): Z座標。
            *   `value` (int): 配置する数字。
        *   **戻り値**: なし
        *   **責務**: 指定された3D座標のセルに、指定された数字を直接設定します。このメソッドはルールチェックを行いません。
    *   `get_all_numbers(self) -> list[list[list[int | None]]]`
        *   **引数**: なし
        *   **戻り値**: `list[list[list[int | None]]]` - キューブ全体の現在の数字の状態を表す3D配列。
        *   **責務**: キューブ盤面全体の現在の状態（各セルに配置されている数字）を3D配列として返します。
    *   `is_valid_position(self, i: int, j: int, k: int) -> bool`
        *   **引数**:
            *   `i` (int): X座標。
            *   `j` (int): Y座標。
            *   `k` (int): Z座標。
        *   **戻り値**: `bool` - 座標がキューブの範囲内であればTrue、そうでなければFalse。
        *   **責務**: 指定された3D座標が、現在のキューブサイズ（N）の有効な範囲内にあるかどうかをチェックします。
    *   `attempt_input(self, i: int, j: int, k: int, value: int) -> bool`
        *   **引数**:
            *   `i` (int): X座標。
            *   `j` (int): Y座標。
            *   `k` (int): Z座標。
            *   `value` (int): 配置を試みる数字。
        *   **戻り値**: `bool` - 配置が成功した場合はTrue、失敗した場合はFalse。
        *   **責務**: 指定された3D座標に指定された数字を配置しようと試みます。まず座標の有効性をチェックし、次にそのセルが既に埋まっていないか、または同じ数字で上書きしようとしているかを確認します。その後、`FieldAdapter` を使用して数独のルール（行、列、柱での重複）に違反しないかチェックします。全てのチェックを通過した場合のみ、数字を盤面に配置し、`FieldAdapter` にもその変更を反映させます。失敗した場合はエラーメッセージを記録します。
    *   `get_last_error(self) -> str`
        *   **引数**: なし
        *   **戻り値**: `str` - 最後に `attempt_input` が失敗した際のエラーメッセージ。
        *   **責務**: `attempt_input` メソッドが最後に失敗した理由を示すエラーメッセージを返します。
    *   `reset(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: キューブ盤面（`_numbers`）を全てのセルがNoneの状態にリセットし、エラーメッセージもクリアします。
    *   `can_place_number(self, value: int) -> bool`
        *   **引数**:
            *   `value` (int): 配置可能かチェックする数字。
        *   **戻り値**: `bool` - 指定された数字をキューブのどこか（空いているセルで、かつルールに違反しない場所）に配置できる可能性がある場合はTrue、そうでない場合はFalse。
        *   **責務**: 指定された数字が、現在の盤面において少なくとも1つ以上の合法な空きセルに配置可能であるかどうかをチェックします。実際に数字を配置するわけではなく、可能性のみを評価します。

---

### `kivy_cube_app/services/game_controller.py`

このファイルは、Kivy UIとゲームのコアロジック（`GameState`, `CubeLogic`, `FieldAdapter`, `CpuPlayer`）間の仲介役として機能します。UIからのイベントを受け取り、ゲームの状態を更新し、UIに表示を反映させる役割を担います。

*   **クラス: `GameController`**
    *   **責務**: KivyアプリケーションのUI要素とゲームのバックエンドロジックを連携させ、ゲームのフロー全体を制御します。ゲームの初期化、ターン管理、スコア更新、タイマー処理、ゲームオーバー判定、UIへのフィードバックなどを担当します。
    *   `__init__(self, root_widget: 'kivy.uix.screenmanager.Screen', is_ta_mode: bool = False, level: int = 1, N: int = 3) -> None`
        *   **引数**:
            *   `root_widget` (`kivy.uix.screenmanager.Screen`): Kivyアプリケーションのルートウィジェット（通常は`GameScreen`のインスタンス）。UI要素へのアクセスや更新のために使用されます。
            *   `is_ta_mode` (bool): タイムアタックモードかどうかを示すフラグ。デフォルトはFalse。
            *   `level` (int): ゲームの難易度レベル。デフォルトは1。
            *   `N` (int): キューブの一辺のサイズ。デフォルトは3。
        *   **戻り値**: なし
        *   **責務**: ゲームコントローラを初期化します。`AppLogger` を設定し、新しいゲームIDを生成してログに記録します。`GameState`, `FieldAdapter`, `CubeLogic`, `CpuPlayer` のインスタンスを作成し、ゲームのコアコンポーネントをセットアップします。タイマーの更新や数字スキップ通知のためのコールバックを設定し、ゲーム開始時のボード状態をログに出力します。
    *   `_log_board(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: 現在のゲームボードの状態を、各層（Z軸）ごとに整形してログに出力します。主にデバッグやゲーム開始時の状態確認に利用されます。
    *   `set_cube_callbacks(self, cube_widget: 'kivy_cube_app.ui.cube_view.Cube3DWidget') -> None`
        *   **引数**:
            *   `cube_widget` (`kivy_cube_app.ui.cube_view.Cube3DWidget`): 3Dキューブを表示するUIウィジェット。
        *   **戻り値**: なし
        *   **責務**: `Cube3DWidget` からのイベント（例: 成功した入力）を受け取るためのコールバック関数を設定します。これにより、UI操作がゲームロジックに連携されます。
    *   `set_timer_update_callback(self, callback_fn: Callable[[float], None]) -> None`
        *   **引数**:
            *   `callback_fn` (`Callable[[float], None]`): タイマーが更新されるたびに呼び出される関数。残り時間（float）を引数として受け取ります。
        *   **戻り値**: なし
        *   **責務**: UI上のタイマー表示を更新するためのコールバック関数を設定します。
    *   `set_score_update_callback(self, callback_fn: Callable[[], None]) -> None`
        *   **引数**:
            *   `callback_fn` (`Callable[[], None]`): スコアやゲームステータスが更新されるたびに呼び出される関数。引数はありません。
        *   **戻り値**: なし
        *   **責務**: UI上のスコアや現在のターン表示を更新するためのコールバック関数を設定します。
    *   `set_number_skip_notification_callback(self, callback_fn: Callable[[int], None]) -> None`
        *   **引数**:
            *   `callback_fn` (`Callable[[int], None]`): 数字がスキップされた際に呼び出される関数。スキップされた数字を引数として受け取ります。
        *   **戻り値**: なし
        *   **責務**: UIに数字スキップの通知を表示するためのコールバック関数を設定します。
    *   `_on_number_skipped(self, skipped_number: int) -> None`
        *   **引数**:
            *   `skipped_number` (int): スキップされた数字。
        *   **戻り値**: なし
        *   **責務**: `GameState` から数字スキップの通知を受け取った際に、設定されているコールバック関数を呼び出し、UIにその情報を伝達します。
    *   `_update_timer(self, dt: float) -> None`
        *   **引数**:
            *   `dt` (float): 前回の呼び出しからの経過時間（KivyのClockスケジューラから渡される）。
        *   **戻り値**: なし
        *   **責務**: Kivyの`Clock.schedule_interval`によって定期的に呼び出され、`GameState`のタイマーを更新し、設定されているタイマー更新コールバックを呼び出してUIに残り時間を反映させます。
    *   `get_initial_filled(self) -> list[dict]`
        *   **引数**: なし
        *   **戻り値**: `list[dict]` - 初期配置されたセルの情報。
        *   **責務**: `GameState` からゲーム開始時に配置されたヒントセルの情報を取得し、UI（`Cube3DWidget`）に渡します。
    *   `on_success_input(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: プレイヤーがセルに数字を正常に配置した後に呼び出される主要な処理です。`GameState` のスコアを加算し、次のターンへ進めます。スコア更新コールバックを呼び出してUIを更新し、ゲームが終了したかどうかを判定し、必要であればゲームオーバーポップアップを表示します。
    *   `show_game_over_popup(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: ゲームが終了した際に、プレイヤーのスコアと勝者を表示するポップアップウィンドウをUI上に表示します。リセットボタンと終了ボタンを提供します。
    *   `reset_game(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: ゲームを初期状態にリセットします。`FieldAdapter`, `CubeLogic`, `GameState` の状態をリセットし、UI（`Cube3DWidget`）を再描画して、新しいゲームを開始できる状態にします。

---

### `kivy_cube_app/core/ai_autoplay.py`

このファイルは、ゲームを自動でプレイするAIボットのロジックを含みます。主にゲームのテストやパフォーマンス測定のために使用されます。

*   **クラス: `AutoPlayBot`**
    *   **責務**: 指定されたNとレベルでゲームを自動的にプレイし、その結果（クリア時間、スコア）を記録します。CPUプレイヤーのロジックとゲームの状態管理を利用して、ゲームのシミュレーションを行います。
    *   `__init__(self, n: int, level: int, app_logger: 'AppLogger') -> None`
        *   **引数**:
            *   `n` (int): キューブの一辺のサイズ。
            *   `level` (int): ゲームの難易度レベル。
            *   `app_logger` (`AppLogger`): ログ出力に使用するロガーインスタンス。
        *   **戻り値**: なし
        *   **責務**: `AutoPlayBot` オブジェクトを初期化します。`FieldAdapter`, `CubeLogic`, `GameState`, `CpuPlayer` のインスタンスを生成し、ゲームの自動プレイに必要なコンポーネントをセットアップします。
    *   `run_game(self) -> Tuple[float, int]`
        *   **引数**: なし
        *   **戻り値**: `Tuple[float, int]` - ゲームのクリア時間（秒）と最終スコア。
        *   **責務**: ゲームの開始から終了までを自動で実行します。`GameState.is_game_over` がTrueになるまでループし、各ターンで `CpuPlayer.make_move` を呼び出して手を打ちます。CPUが手を打てない場合のスキップ処理やゲームオーバー判定も行い、ゲーム終了時のボード状態をログに出力します。
    *   `_log_board(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: 現在のゲームボードの状態を、各層（Z軸）ごとに整形してログに出力します。`run_game` メソッド内でゲーム終了時に呼び出され、最終的な盤面状態を記録します。

*   **関数: `main() -> None`**
    *   **引数**: なし
    *   **戻り値**: なし
    *   **責務**: `AutoPlayBot` のエントリポイントとして機能します。複数のNとレベルの組み合わせでゲームを繰り返し実行し、各ゲームのクリア時間とスコアを収集します。最終的に、これらの結果を `autoplay_results.csv` ファイルにCSV形式で書き出します。

---

### `kivy_cube_app/core/field_adapter.py`

このファイルは、`Field` クラスへのアダプターとして機能し、`CubeLogic` や他のコンポーネントが `Field` の詳細な実装に直接依存することなく、盤面操作を行えるようにします。

*   **クラス: `FieldAdapter`**
    *   **責務**: `Field` クラスのラッパーとして機能し、`CubeLogic` や他の上位レイヤーのモジュールが `Field` の内部実装（例: 0-indexed vs 1-indexed座標）を意識することなく、盤面操作を行えるように抽象化します。
    *   `__init__(self, N: int) -> None`
        *   **引数**:
            *   `N` (int): キューブの一辺のサイズ。
        *   **戻り値**: なし
        *   **責務**: `FieldAdapter` オブジェクトを初期化します。内部的に `Field` クラスのインスタンスを生成し、そのインスタンスを介して盤面操作を行います。
    *   `check(self, pos: List[int], num: int) -> Tuple[bool, str]`
        *   **引数**:
            *   `pos` (List[int]): 配置をチェックするセルの座標（1-indexed, [x, y, z]）。
            *   `num` (int): 配置をチェックする数字。
        *   **戻り値**: `Tuple[bool, str]` - 配置が妥当な場合は `(True, "OK")`、妥当でない場合は `(False, エラーメッセージ)`。
        *   **責務**: 指定された座標に指定された数字を配置することが、数独のルール（行、列、柱での重複）に違反しないかどうかを `Field` クラスの `check` メソッドを呼び出して確認します。
    *   `reflect(self, pos: List[int], num: int) -> None`
        *   **引数**:
            *   `pos` (List[int]): 配置を反映するセルの座標（1-indexed, [x, y, z]）。
            *   `num` (int): 配置する数字。
        *   **戻り値**: なし
        *   **責務**: 指定された座標に指定された数字が配置されたことを `Field` クラスの `reflect` メソッドを呼び出して通知し、`Field` 内部の候補数管理を更新させます。
    *   `reset(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: `Field` クラスの `reset` メソッドを呼び出し、盤面と候補数の状態を初期化します。
    *   `get_all_numbers(self) -> List[List[List[int]]]`
        *   **引数**: なし
        *   **戻り値**: `List[List[List[int]]]` - `Field` クラスが保持する現在のボードの状態（3D配列）。
        *   **責務**: `Field` クラスが保持する現在のボードの状態を直接取得します。

---

### `kivy_cube_app/ui/cube_view.py`

このファイルは、Kivyアプリケーションにおける3Dキューブの視覚化とユーザーインタラクション（タッチ操作、スライスビューなど）を管理します。

*   **クラス: `Cube3DWidget`**
    *   **責務**: 3D数独のキューブをKivyのCanvas上に描画し、ユーザーのタッチ操作（回転、ズーム、セル選択）を処理します。また、スライスビューの表示や、ゲームロジックからの情報（現在の数字、次の数字、初期配置）をUIに反映させます。
    *   `__init__(self, logic: 'CubeLogic', get_current_number_fn: Callable[[], int | None], get_upcoming_fn: Callable[[int | None], List[int]], initial_filled: List[Dict], **kwargs) -> None`
        *   **引数**:
            *   `logic` (`CubeLogic`): キューブのロジックを扱うオブジェクト。セルの状態取得や配置試行に使用されます。
            *   `get_current_number_fn` (`Callable[[], int | None]`): 現在配置すべき数字を取得するための関数。
            *   `get_upcoming_fn` (`Callable[[int | None], List[int]]`): 次に配置される数字のシーケンスを取得するための関数。
            *   `initial_filled` (List[Dict]): ゲーム開始時に既に配置されているセルの情報。各辞書は `{"pos": [x, y, z], "value": int}` の形式。
            *   `**kwargs`: Kivyウィジェットの標準引数。
        *   **戻り値**: なし
        *   **責務**: 3Dキューブウィジェットを初期化します。ゲームロジックへの参照、数字取得関数、初期配置データなどを設定し、描画に必要な変数を準備します。
    *   `on_touch_down(self, touch: Touch) -> bool`
        *   **引数**:
            *   `touch` (`Touch`): Kivyのタッチイベントオブジェクト。
        *   **戻り値**: `bool` - イベントが処理された場合はTrue。
        *   **責務**: ユーザーが画面をタッチした際のイベントを処理します。タッチ位置が3Dキューブまたはスライスビュー内にあるか判定し、セル選択やカメラ操作の開始を検出します。
    *   `on_touch_move(self, touch: Touch) -> bool`
        *   **引数**:
            *   `touch` (`Touch`): Kivyのタッチイベントオブジェクト。
        *   **戻り値**: `bool` - イベントが処理された場合はTrue。
        *   **責務**: ユーザーが画面をドラッグした際のイベントを処理します。3Dキューブ上でのドラッグはカメラの回転に、スライスビュー上でのドラッグはセル選択のハイライト移動に利用されます。
    *   `on_touch_up(self, touch: Touch) -> bool`
        *   **引数**:
            *   `touch` (`Touch`): Kivyのタッチイベントオブジェクト。
        *   **戻り値**: `bool` - イベントが処理された場合はTrue。
        *   **責務**: ユーザーが画面から指を離した際のイベントを処理します。セル選択の確定や、カメラ操作の終了を検出します。
    *   `_get_cell_at_touch(self, touch: Touch) -> Tuple[int, int, int] | None`
        *   **引数**:
            *   `touch` (`Touch`): Kivyのタッチイベントオブジェクト。
        *   **戻り値**: `Tuple[int, int, int] | None` - タッチされたセルの座標 (0-indexed) またはNone。
        *   **責務**: タッチイベントの座標から、それがどの3Dキューブのセルに対応するかを計算し、そのセルの座標を返します。
    *   `_handle_cell_selection(self, cell_pos: Tuple[int, int, int]) -> None`
        *   **引数**:
            *   `cell_pos` (Tuple[int, int, int]): 選択されたセルの座標 (0-indexed)。
        *   **戻り値**: なし
        *   **責務**: ユーザーがセルを選択した際のロジックを処理します。選択されたセルをハイライト表示し、再度同じセルが選択された場合は、現在の数字をそのセルに配置する試みを行います。配置が成功した場合は、`on_success_input` コールバックを呼び出します。
    *   `_draw_cube(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: KivyのCanvas APIを使用して、3Dキューブのグリッド線、数字、ハイライトなどを描画します。カメラの視点やズームに応じて描画を調整します。
    *   `_draw_slice_view(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: KivyのCanvas APIを使用して、選択された軸と深度に応じた2Dのスライスビューを描画します。スライス内のセルに数字やハイライトを表示します。
    *   `_draw_numbers(self, canvas: Canvas, board: List[List[List[int | None]]], offset_x: float, offset_y: float, cell_size: float) -> None`
        *   **引数**:
            *   `canvas` (`Canvas`): 描画対象のKivy Canvas。
            *   `board` (List[List[List[int | None]]]): 描画するボードの状態。
            *   `offset_x` (float): 描画領域のXオフセット。
            *   `offset_y` (float): 描画領域のYオフセット。
            *   `cell_size` (float): 各セルのサイズ。
        *   **戻り値**: なし
        *   **責務**: 指定されたボードの状態に基づいて、各セルに数字を描画します。
    *   `_draw_grid(self, canvas: Canvas, offset_x: float, offset_y: float, cell_size: float) -> None`
        *   **引数**:
            *   `canvas` (`Canvas`): 描画対象のKivy Canvas。
            *   `offset_x` (float): 描画領域のXオフセット。
            *   `offset_y` (float): 描画領域のYオフセット。
            *   `cell_size` (float): 各セルのサイズ。
        *   **戻り値**: なし
        *   **責務**: 指定された描画領域にグリッド線を描画します。
    *   `_draw_highlight(self, canvas: Canvas, pos: Tuple[int, int, int], offset_x: float, offset_y: float, cell_size: float, color: Tuple[float, float, float, float]) -> None`
        *   **引数**:
            *   `canvas` (`Canvas`): 描画対象のKivy Canvas。
            *   `pos` (Tuple[int, int, int]): ハイライトするセルの座標 (0-indexed)。
            *   `offset_x` (float): 描画領域のXオフセット。
            *   `offset_y` (float): 描画領域のYオフセット。
            *   `cell_size` (float): 各セルのサイズ。
            *   `color` (Tuple[float, float, float, float]): ハイライトの色 (RGBA)。
        *   **戻り値**: なし
        *   **責務**: 指定されたセルの位置にハイライトを描画します。
    *   `_draw_text_in_cell(self, canvas: Canvas, text: str, x: float, y: float, cell_size: float, color: Tuple[float, float, float, float]) -> None`
        *   **引数**:
            *   `canvas` (`Canvas`): 描画対象のKivy Canvas。
            *   `text` (str): 描画するテキスト。
            *   `x` (float): テキストのX座標。
            *   `y` (float): テキストのY座標。
            *   `cell_size` (float): セルのサイズ。
            *   `color` (Tuple[float, float, float, float]): テキストの色 (RGBA)。
        *   **戻り値**: なし
        *   **責務**: 指定されたセル内にテキスト（数字）を描画します。
    *   `redraw(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: 3Dキューブとスライスビューを含むウィジェット全体を再描画します。ゲームの状態が変化した際に呼び出されます。
    *   `redraw_info(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: UI上の情報表示部分（例: 次の数字）を再描画します。
    *   `set_on_success_input(self, fn: Callable[[], None]) -> None`
        *   **引数**:
            *   `fn` (`Callable[[], None]`): ユーザーが数字を正常に配置した際に呼び出されるコールバック関数。
        *   **戻り値**: なし
        *   **責務**: 数字の配置成功をゲームコントローラに通知するためのコールバック関数を設定します。
    *   `set_number_skip_notification_callback(self, fn: Callable[[int], None]) -> None`
        *   **引数**:
            *   `fn` (`Callable[[int], None]`): 数字がスキップされた際に呼び出されるコールバック関数。スキップされた数字を引数として受け取ります。
        *   **戻り値**: なし
        *   **責務**: 数字スキップの通知をUIに表示するためのコールバック関数を設定します。
    *   `reset_view(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: 3Dキューブのカメラ視点とズームレベルを初期状態にリセットします。
    *   `zoom_in(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: 3Dキューブの表示をズームインします。
    *   `zoom_out(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: 3Dキューブの表示をズームアウトします。
    *   `set_slice_axis(self, axis: str) -> None`
        *   **引数**:
            *   `axis` (str): スライス表示する軸（'x', 'y', 'z'）。
        *   **戻り値**: なし
        *   **責務**: スライスビューで表示する軸を設定し、UIを更新します。
    *   `set_slice_depth(self, depth: int) -> None`
        *   **引数**:
            *   `depth` (int): スライス表示する深度（0からN-1）。
        *   **戻り値**: なし
        *   **責務**: スライスビューで表示する深度を設定し、UIを更新します。

---

### `kivy_cube_app/core/cpu_player.py`

このファイルは、ゲームのCPUプレイヤーのロジックを定義します。

*   **クラス: `CpuPlayer`**
    *   **責務**: ゲームのルールに基づいて、CPUが自動的に数字を配置するロジックを提供します。現在のゲーム状態と利用可能な候補を考慮して、最適な（または単純な）手を決定します。
    *   `__init__(self, cube_logic: 'CubeLogic', field: 'FieldAdapter', N: int) -> None`
        *   **引数**:
            *   `cube_logic` (`CubeLogic`): キューブのロジックを扱うオブジェクト。数字の配置試行に使用されます。
            *   `field` (`FieldAdapter`): 盤面の候補数管理を行うアダプターオブジェクト。
            *   `N` (int): キューブの一辺のサイズ。
        *   **戻り値**: なし
        *   **責務**: CPUプレイヤーオブジェクトを初期化します。ゲームのロジックとフィールドアダプターへの参照を保持し、CPUが手を打つために必要な情報を設定します。
    *   `make_move(self, current_number: int) -> bool`
        *   **引数**:
            *   `current_number` (int): 現在配置すべき数字。
        *   **戻り値**: `bool` - 手を打つことに成功した場合はTrue、失敗した場合はFalse。
        *   **責務**: CPUが現在の数字を盤面に配置しようと試みます。利用可能な空きセルを探索し、`cube_logic.attempt_input` を使用して数字の配置を試みます。成功した場合はTrueを返し、配置できる場所が見つからなかった場合はFalseを返します。

---

### `kivy_cube_app/core/field.py`

このファイルは、3D数独の盤面における数字の配置と、各セルの候補数（配置可能な数字）の管理、および数独のルールチェック（行、列、柱での重複）を詳細に実装します。

*   **クラス: `Field`**
    *   **責務**: 3D数独の盤面（`board`）と、各セルに配置可能な数字の候補（`candidates`）を管理します。数字の配置、候補数の更新、および数独のルール（行、列、柱での重複禁止）に基づいた配置の妥当性チェックを行います。
    *   `__init__(self, N: int) -> None`
        *   **引数**:
            *   `N` (int): キューブの一辺のサイズ。
        *   **戻り値**: なし
        *   **責務**: `Field` オブジェクトを初期化します。`N` の値に基づいて、`board`（盤面）と `candidates`（各セルの候補数）の3D配列を生成し、初期状態に設定します。
    *   `_initialize_board(self) -> List[List[List[int]]]`
        *   **引数**: なし
        *   **戻り値**: `List[List[List[int]]]` - 全て0で初期化された3Dボード配列。
        *   **責務**: 盤面を全て0（空）で初期化します。
    *   `_initialize_candidates(self) -> List[List[List[List[int]]]]`
        *   **引数**: なし
        *   **戻り値**: `List[List[List[List[int]]]]` - 各セルに1からNまでの全ての数字が候補として含まれる3D候補配列。
        *   **責務**: 各セルに配置可能な数字の候補リストを初期化します。最初は全てのセルに1からNまでの全ての数字が候補として含まれます。
    *   `check(self, pos: List[int], num: int) -> Tuple[bool, str]`
        *   **引数**:
            *   `pos` (List[int]): 配置をチェックするセルの座標（1-indexed, [x, y, z]）。
            *   `num` (int): 配置をチェックする数字。
        *   **戻り値**: `Tuple[bool, str]` - 配置が妥当な場合は `(True, "OK")`、妥当でない場合は `(False, エラーメッセージ)`。
        *   **責務**: 指定された座標に指定された数字を配置することが、現在の盤面と数独のルールに照らして妥当であるかをチェックします。具体的には、そのセルが既に埋まっていないか、指定された数字がそのセルの候補に含まれているか、そして同じ行、列、柱に同じ数字が既に存在しないかを確認します。
    *   `reflect(self, pos: List[int], num: int) -> None`
        *   **引数**:
            *   `pos` (List[int]): 配置を反映するセルの座標（1-indexed, [x, y, z]）。
            *   `num` (int): 配置する数字。
        *   **戻り値**: なし
        *   **責務**: 指定された座標に指定された数字が配置されたことを盤面（`board`）に反映させ、その数字が配置されたことによって影響を受ける他のセルの候補数（`candidates`）を更新します。具体的には、配置されたセルの行、列、柱にある他のセルから、配置された数字を候補から削除します。
    *   `set_point(self, pos: List[int], num: int) -> None`
        *   **引数**:
            *   `pos` (List[int]): 数字を設定するセルの座標（1-indexed, [x, y, z]）。
            *   `num` (int): 設定する数字。
        *   **戻り値**: なし
        *   **責務**: 指定された座標のセルに、指定された数字を直接設定します。このメソッドはルールチェックを行わず、主に初期配置やテストのために使用されます。
    *   `reset(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: 盤面（`board`）と候補数（`candidates`）を初期状態にリセットします。

---

### `kivy_cube_app/core/scramble.py`

このファイルは、3D数独の盤面をランダムにシャッフルする機能を提供します。

*   **関数: `scramble_board(base_board: List[List[List[int]]], N: int, seed: int | None = None) -> List[List[List[int]]]`**
    *   **引数**:
        *   `base_board` (List[List[List[int]]]): スクランブルの元となる完成済みの3Dボード。通常はNoneで、関数内で自動生成されます。
        *   `N` (int): キューブの一辺のサイズ。
        *   `seed` (int | None): 乱数生成器のシード。Noneの場合、ランダムなシードが使用されます。
    *   **戻り値**: `List[List[List[int]]]` - ランダマイズされた新しい3Dボード。
    *   **責務**: 完成済みの3D数独ボードを、以下の3つのランダマイズ手法を組み合わせてシャッフルします。
        1.  **数字置換**: 1からNまでの数字をランダムに別の数字に置き換えます。
        2.  **軸シャッフル + 反転**: X, Y, Z軸をランダムにシャッフルし、各軸の方向を反転させます。
        3.  **層スライド**: 各軸に沿って層をランダムにスライドさせます。
    これにより、盤面の暗記を防止し、毎回異なるパズルを提供します。

---

### `kivy_cube_app/ui/rule_screen.py`

このファイルは、ゲームのルール説明を表示するためのKivyポップアップウィジェットを定義します。

*   **クラス: `RuleExplanationPopup`**
    *   **責務**: ユーザーがゲームのルールを確認できるように、ルール説明テキストを含むポップアップウィンドウを表示します。
    *   `__init__(self, **kwargs) -> None`
        *   **引数**:
            *   `**kwargs`: Kivyウィジェットの標準引数。
        *   **戻り値**: なし
        *   **責務**: ルール説明ポップアップを初期化します。ポップアップのタイトル、コンテンツ（ルール説明テキストと閉じるボタン）、サイズヒントを設定します。

---

### `kivy_cube_app/utils/constants.py`

このファイルは、アプリケーション全体で使用される様々な定数を定義します。

*   **定数群**:
    *   `N_VALUE` (int): キューブの一辺のデフォルトサイズ。
    *   `CPU_PLAYER_ID` (int): CPUプレイヤーのID。
    *   `LOG_FILE_PATH` (str): ログファイルの保存パス。
    *   `LOG_FILE_NAME` (str): ログファイル名。
    *   `LOG_MAX_BYTES` (int): ログファイルの最大サイズ。
    *   `LOG_BACKUP_COUNT` (int): ログファイルのバックアップ数。
    *   `LOG_ENCODE` (str): ログファイルのエンコーディング。
    *   `APP_LOG_FORMAT` (str): アプリケーションログのフォーマット。
    *   `CONSOLE_LOG_FORMAT` (str): コンソールログのフォーマット。
    *   `TA_BASE_TIME_LV1` - `TA_BASE_TIME_LV5` (int): タイムアタックモードの各レベルの基本持ち時間。
    *   `TIME_GAIN_LINE_COMPLETE` (int): ライン完成時の時間ボーナス。
    *   `TIME_GAIN_SLICE_COMPLETE` (int): 層完成時の時間ボーナス。
    *   `TIME_GAIN_5_CONSECUTIVE_SUCCESS` (int): 5手連続成功時の時間ボーナス。
    *   `TIME_PENALTY_WRONG_PLACEMENT` (int): 誤配置時の時間ペナルティ。
    *   `MAX_SKIP_COUNT` (int): ターンをスキップできる最大回数。
    *   **責務**: アプリケーションの動作を制御する様々な設定値やマジックナンバーを中央集約し、コードの可読性、保守性、および将来的な変更の容易性を向上させます。

---

### `kivy_cube_app/utils/logger.py`

このファイルは、アプリケーションのログ出力システムを定義します。

*   **クラス: `GameIDFilter`**
    *   **責務**: ログレコードに現在のゲームIDを追加するためのカスタムログフィルターを提供します。これにより、ログメッセージがどのゲームセッションに属するかが識別可能になります。
    *   `__init__(self, game_id: str | None = None) -> None`
        *   **引数**:
            *   `game_id` (str | None): ログに含めるゲームID。デフォルトはNone。
        *   **戻り値**: なし
        *   **責務**: フィルターを初期化し、オプションで初期ゲームIDを設定します。
    *   `filter(self, record: logging.LogRecord) -> bool`
        *   **引数**:
            *   `record` (`logging.LogRecord`): 処理中のログレコード。
        *   **戻り値**: `bool` - 常にTrue（レコードを通過させるため）。
        *   **責務**: 各ログレコードに `game_id` 属性を追加します。`game_id` が設定されていない場合は 'N/A' を使用します。

*   **クラス: `AppLogger`**
    *   **責務**: アプリケーション全体のログ出力機能を提供します。ファイルハンドラーとストリームハンドラーを設定し、ログレベル、フォーマット、ゲームIDフィルターを管理します。シングルトンパターンを模倣し、アプリケーション全体で単一のロガーインスタンスを共有します。
    *   `logger: logging.Logger = None` (クラス変数)
    *   `NAME = 'appLogger'` (クラス変数)
    *   `__init__(self, log_lv: int = logging.INFO) -> None`
        *   **引数**:
            *   `log_lv` (int): ロガーの初期ログレベル（例: `logging.INFO`, `logging.DEBUG`）。デフォルトは`logging.INFO`。
        *   **戻り値**: なし
        *   **責務**: `AppLogger` のインスタンスを初期化します。ロガーがまだ設定されていない場合、ファイルハンドラーとストリームハンドラーを設定し、フォーマッターと `GameIDFilter` を追加します。指定されたログレベルを設定します。
    *   `get_logger(self) -> logging.Logger`
        *   **引数**: なし
        *   **戻り値**: `logging.Logger` - 設定済みのロガーオブジェクト。
        *   **責務**: 設定済みのロガーオブジェクトを返します。
    *   `set_level(self, log_lv: int) -> None`
        *   **引数**:
            *   `log_lv` (int): 設定するログレベル。
        *   **戻り値**: なし
        *   **責務**: ロガーのログレベルを設定します。
    *   `set_game_id(self, game_id: str) -> None`
        *   **引数**:
            *   `game_id` (str): 設定するゲームID。
        *   **戻り値**: なし
        *   **責務**: `GameIDFilter` にゲームIDを設定し、以降のログメッセージにそのIDが含まれるようにします。
    *   `__set_logger(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: ロガーオブジェクト、ハンドラー（ストリームとファイル）、フォーマッター、およびカスタムフィルターを実際に設定するプライベートメソッドです。ロガーが既に設定されている場合は再設定しません。

*   **クラス: `ConsoleLogger`**
    *   **責務**: コンソール出力に特化したログ機能を提供します。`AppLogger` と同様にファイルハンドラーとストリームハンドラーを設定しますが、異なるフォーマットを使用する場合があります。
    *   `logger: logging.Logger = None` (クラス変数)
    *   `NAME = 'consoleLogger'` (クラス変数)
    *   `__init__(self, log_lv: int = logging.INFO) -> None`
        *   **引数**:
            *   `log_lv` (int): ロガーの初期ログレベル。デフォルトは`logging.INFO`。
        *   **戻り値**: なし
        *   **責務**: `ConsoleLogger` のインスタンスを初期化します。ロガーがまだ設定されていない場合、ファイルハンドラーとストリームハンドラーを設定し、フォーマッターを設定します。指定されたログレベルを設定します。
    *   `get_logger(self) -> logging.Logger`
        *   **引数**: なし
        *   **戻り値**: `logging.Logger` - 設定済みのロガーオブジェクト。
        *   **責務**: 設定済みのロガーオブジェクトを返します。
    *   `set_level(self, log_lv: int) -> None`
        *   **引数**:
            *   `log_lv` (int): 設定するログレベル。
        *   **戻り値**: なし
        *   **責務**: ロガーのログレベルを設定します。
    *   `__set_logger(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: ロガーオブジェクト、ハンドラー（ストリームとファイル）、およびフォーマッターを実際に設定するプライベートメソッドです。ロガーが既に設定されている場合は再設定しません。

---

### `main.py`

このファイルは、Kivyアプリケーションのエントリポイントであり、UIの主要な画面構成とナビゲーションを定義します。

*   **クラス: `LevelSelectScreen`**
    *   **責務**: ユーザーがゲームの難易度レベルを選択するためのUI画面を提供します。
    *   `__init__(self, **kwargs) -> None`
        *   **引数**:
            *   `**kwargs`: Kivyウィジェットの標準引数。
        *   **戻り値**: なし
        *   **責務**: レベル選択画面のUI要素（タイトル、レベル選択ボタン）を初期化し、レイアウトに配置します。
    *   `select_level(self, level: int) -> None`
        *   **引数**:
            *   `level` (int): 選択された難易度レベル。
        *   **戻り値**: なし
        *   **責務**: ユーザーがレベル選択ボタンを押した際に呼び出されます。選択されたレベルを `GameScreen` に渡し、ゲーム画面へ遷移します。

*   **クラス: `GameScreen`**
    *   **責務**: 実際のゲームプレイが行われるUI画面を提供します。ゲームの3Dキューブ表示、ステータスバー（スコア、ターン、タイマー）、および操作ボタン（リセット、ルール、レベル選択に戻る）を管理します。
    *   `__init__(self, **kwargs) -> None`
        *   **引数**:
            *   `**kwargs`: Kivyウィジェットの標準引数。
        *   **戻り値**: なし
        *   **責務**: ゲーム画面の基本的な構造を初期化します。`GameController` と `Cube3DWidget` のインスタンスを保持するための変数を準備します。
    *   `start_game(self, level: int) -> None`
        *   **引数**:
            *   `level` (int): 開始するゲームの難易度レベル。
        *   **戻り値**: なし
        *   **責務**: 指定されたレベルで新しいゲームを開始します。既存のウィジェットをクリアし、ステータスバー、`GameController`、`Cube3DWidget`、および操作ボタンを再構築して画面に配置します。`GameController` と `Cube3DWidget` 間のコールバックを設定し、初期ステータス表示を更新します。
    *   `update_status(self) -> None`
        *   **引数**: なし
        *   **戻り値**: なし
        *   **責務**: UI上のスコア表示と現在のターン表示を更新します。`GameController` から最新のゲーム状態を取得し、プレイヤーのスコア、現在のプレイヤー名、配置すべき数字をラベルに反映させます。
    *   `update_time(self, elapsed_seconds: float) -> None`
        *   **引数**:
            *   `elapsed_seconds` (float): 経過時間または残り時間（秒）。
        *   **戻り値**: なし
        *   **責務**: UI上のタイマー表示を更新します。秒数を分と秒に変換し、整形してラベルに表示します。
    *   `go_to_level_select(self, instance: Button) -> None`
        *   **引数**:
            *   `instance` (`Button`): イベントを発生させたボタンのインスタンス。
        *   **戻り値**: なし
        *   **責務**: レベル選択画面に戻るボタンが押された際に呼び出されます。現在のゲームを停止し、画面マネージャーを介してレベル選択画面へ遷移します。

*   **クラス: `SudokuApp`**
    *   **責務**: Kivyアプリケーションのメインクラスであり、アプリケーションのライフサイクルと画面管理を制御します。
    *   `build(self) -> ScreenManager`
        *   **引数**: なし
        *   **戻り値**: `ScreenManager` - アプリケーションのルートウィジェットとなる画面マネージャー。
        *   **責務**: KivyアプリケーションのUIを構築します。`ScreenManager` を作成し、`LevelSelectScreen` と `GameScreen` を追加して、画面間の遷移を可能にします。

---

### `api/app.py`

このファイルは、ランキング機能を提供するRESTful APIのFlaskアプリケーションを定義します。

*   **関数: `create_app() -> Flask`**
    *   **引数**: なし
    *   **戻り値**: `Flask` - 設定済みのFlaskアプリケーションインスタンス。
    *   **責務**: Flaskアプリケーションを作成し、データベースを初期化します。ランキングAPIのエンドポイント（`/api/rank`）を定義し、POST（データ登録）とGET（データ取得）のリクエストを処理します。
*   **関数: `init_db() -> None`**
    *   **引数**: なし
    *   **戻り値**: なし
    *   **責務**: アプリケーションコンテキスト内でデータベースを初期化します。`database.py` の `init_db` 関数を呼び出して、データベース接続とテーブル作成を行います。
*   **ルート: `/api/rank` (POST)**
    *   **責務**: クライアントから送信されたランキングデータをJSON形式で受け取り、データベースに保存します。成功した場合はステータス201（Created）を返します。
*   **ルート: `/api/rank` (GET)**
    *   **責務**: クライアントからのリクエストに基づいて、データベースからランキングデータを取得し、JSON形式で返します。レベル、サイズ、取得件数（limit）でフィルタリング可能です。

---

### `api/database.py`

このファイルは、ランキングデータを保存するためのSQLiteデータベースとのインタラクションを管理します。SQLAlchemyを使用してデータベースモデルと操作を定義します。

*   **クラス: `Rank`**
    *   **責務**: ランキングデータのデータベーススキーマを定義するSQLAlchemyモデルです。各ランキングエントリの属性（ユーザー名、レベル、サイズ、時間、スコア、最大コンボ）とデータ型をマッピングします。
    *   `id` (`Column[int]`): プライマリキー、自動インクリメント。
    *   `user` (`Column[str]`): ユーザー名。
    *   `level` (`Column[int]`): ゲームレベル。
    *   `size` (`Column[int]`): キューブサイズ（N）。
    *   `time` (`Column[int]`): クリア時間（秒）。
    *   `score` (`Column[int]`): 獲得スコア。
    *   `max_combo` (`Column[int]`): 最大コンボ数。
    *   `timestamp` (`Column[DateTime]`): 記録日時、自動設定。
    *   `__repr__(self) -> str`: オブジェクトの文字列表現。
    *   **責務**: データベーステーブル `ranks` の構造を定義し、Pythonオブジェクトとデータベースレコード間のマッピングを提供します。

*   **関数: `init_db() -> None`**
    *   **引数**: なし
    *   **戻り値**: なし
    *   **責務**: データベースエンジンとセッションファクトリを初期化し、`Rank` モデルに基づいてデータベーステーブルを作成します（テーブルが存在しない場合）。これにより、アプリケーションがデータベースと対話するための準備が整います。

*   **関数: `add_rank(user: str, level: int, size: int, time: int, score: int, max_combo: int) -> None`**
    *   **引数**:
            *   `user` (str): ユーザー名。
            *   `level` (int): ゲームレベル。
            *   `size` (int): キューブサイズ（N）。
            *   `time` (int): クリア時間（秒）。
            *   `score` (int): 獲得スコア。
            *   `max_combo` (int): 最大コンボ数。
    *   **戻り値**: なし
    *   **責務**: 新しいランキングエントリをデータベースに追加します。提供されたデータを使用して `Rank` オブジェクトを作成し、データベースセッションを介してコミットします。

*   **関数: `get_ranks(level: int | None = None, size: int | None = None, limit: int = 50) -> List[Rank]`**
    *   **引数**:
            *   `level` (int | None): フィルタリングするゲームレベル。Noneの場合、全てのレベル。
            *   `size` (int | None): フィルタリングするキューブサイズ。Noneの場合、全てのサイズ。
            *   `limit` (int): 取得するランキングエントリの最大数。デフォルトは50。
    *   **戻り値**: `List[Rank]` - フィルタリングされ、ソートされたランキングエントリのリスト。
    *   **責務**: 指定された条件（レベル、サイズ）に基づいてデータベースからランキングデータを取得します。結果はスコアの降順、時間の昇順でソートされ、指定された件数に制限されます。
