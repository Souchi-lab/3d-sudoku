import random


def scramble_board(base_board: list[list[list[int]]] | None, N: int, seed: int | None = None):
    """完成盤テンプレ (N×N×N) を 3‑Layer ランダマイズして返す。"""
    rnd = random.Random(seed)

    # base_boardがNoneの場合、デフォルトの完成盤を生成
    if base_board is None:
        base_board = [[[0] * N for _ in range(N)] for _ in range(N)]
        # シンプルな数独の完成盤を生成 (例: N=3の場合)
        # これはあくまでランダム化のベースとなる盤面であり、
        # 実際の数独のルールに厳密に従う必要はない
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    base_board[i][j][k] = (i + j + k) % N + 1

    # ① 数字置換
    perm = list(range(1, N + 1))
    rnd.shuffle(perm)
    repl = {i + 1: perm[i] for i in range(N)}

    # ② 軸シャッフル + 反転
    axes = ["x", "y", "z"]
    rnd.shuffle(axes)
    flips = [rnd.choice([1, -1]) for _ in range(3)]

    # ③ 層スライド
    shifts = [rnd.randrange(N) for _ in range(3)]

    def map_pos(i, j, k):
        v = {"x": i, "y": j, "z": k}
        a, b, c = v[axes[0]], v[axes[1]], v[axes[2]]
        a = (flips[0] * (a + shifts[0])) % N
        b = (flips[1] * (b + shifts[1])) % N
        c = (flips[2] * (c + shifts[2])) % N
        return a, b, c

    board = [[[None] * N for _ in range(N)] for _ in range(N)]
    for i in range(N):
        for j in range(N):
            for k in range(N):
                # base_boardのインデックスは0からN-1
                # replのキーは1からNなので、base_boardの値を+1してreplに渡す
                # replの結果はpermの要素なので、そのままboardに格納
                original_value = base_board[i][j][k]
                if original_value is not None:
                    mapped_value = repl[original_value]
                else:
                    mapped_value = None  # Noneの場合はそのままNone

                x, y, z = map_pos(i, j, k)
                board[x][y][z] = mapped_value
    return board
