from ..utils.logger import AppLogger

class Field:
    def __init__(self, N: int, logger=None, initial_data=None):
        self.logger = logger or AppLogger().get_logger()
        self.N = N # Nをインスタンス変数として保持
        self.board = [[[None for _ in range(self.N)] for _ in range(self.N)] for _ in range(self.N)]
        self.candidates = [[[[n for n in range(1, self.N + 1)] for _ in range(self.N)] for _ in range(self.N)] for _ in range(self.N)]

        if initial_data:
            for item in initial_data:
                pos = [p + 1 for p in item["pos"]]
                num = item["value"]
                self.set_point(pos, num)
                self.reflect(pos, num)

    def check(self, pos, num):
        x, y, z = [p - 1 for p in pos]  # Convert to 0-indexed
        self.logger.debug(f"check(pos={pos}, num={num})")
        if self.board[x][y][z] is not None:
            self.logger.debug(" - Already filled.")
            return False, "Already filled."
        if num not in self.candidates[x][y][z]:
            self.logger.debug(f" - {num} not in candidates {self.candidates[x][y][z]}")
            return False, "Not a candidate."

        # Check for duplicates along X-axis
        for i in range(self.N):
            if self.board[i][y][z] is not None and self.board[i][y][z] == num:
                self.logger.debug(f" - Duplicate {num} found at ({i+1},{y+1},{z+1}) along X-axis.")
                return False, "Duplicate number in line."
        
        # Check for duplicates along Y-axis
        for j in range(self.N):
            if self.board[x][j][z] is not None and self.board[x][j][z] == num:
                self.logger.debug(f" - Duplicate {num} found at ({x+1},{j+1},{z+1}) along Y-axis.")
                return False, "Duplicate number in line."

        # Check for duplicates along Z-axis
        for k in range(self.N):
            if self.board[x][y][k] is not None and self.board[x][y][k] == num:
                self.logger.debug(f" - Duplicate {num} found at ({x+1},{y+1},{k+1}) along Z-axis.")
                return False, "Duplicate number in line."

        self.logger.debug(" - OK")
        return True, "OK"

    def set_point(self, pos, num):
        x, y, z = [p - 1 for p in pos]
        self.board[x][y][z] = num
        self.logger.debug(f"Placed {num} at {pos}")

    def reflect(self, pos, num):
        x, y, z = [p - 1 for p in pos]
        self.logger.debug(f"reflect(pos={pos}, num={num})")
        self.candidates[x][y][z] = []
        # Remove 'num' from candidates of other cells on the same X-axis line
        for i_x in range(self.N):
            if i_x != x: # Exclude the placed cell itself
                self._remove_candidate(i_x, y, z, num)

        # Remove 'num' from candidates of other cells on the same Y-axis line
        for i_y in range(self.N):
            if i_y != y: # Exclude the placed cell itself
                self._remove_candidate(x, i_y, z, num)

        # Remove 'num' from candidates of other cells on the same Z-axis line
        for i_z in range(self.N):
            if i_z != z: # Exclude the placed cell itself
                self._remove_candidate(x, y, i_z, num)

    def reset(self):
        self.board = [[[None for _ in range(self.N)] for _ in range(self.N)] for _ in range(self.N)]
        self.candidates = [[[[n for n in range(1, self.N + 1)] for _ in range(self.N)] for _ in range(self.N)] for _ in range(self.N)]

    def _remove_candidate(self, x, y, z, num):
        if self.board[x][y][z] is None and num in self.candidates[x][y][z]:
            self.candidates[x][y][z].remove(num)
            self.logger.debug(f" - Removed {num} from ({x+1},{y+1},{z+1})")

    def is_line_complete(self, axis: str, fixed_idx1: int, fixed_idx2: int) -> bool:
        """指定されたラインが完成しているか判定する (1からNまでの数字が重複なく全て含まれているか)"""
        values = []
        if axis == 'x': # X軸に平行なライン (y, zが固定)
            for i in range(self.N):
                values.append(self.board[i][fixed_idx1][fixed_idx2])
        elif axis == 'y': # Y軸に平行なライン (x, zが固定)
            for j in range(self.N):
                values.append(self.board[fixed_idx1][j][fixed_idx2])
        elif axis == 'z': # Z軸に平行なライン (x, yが固定)
            for k in range(self.N):
                values.append(self.board[fixed_idx1][fixed_idx2][k])
        else:
            raise ValueError("Invalid axis. Must be 'x', 'y', or 'z'.")

        if None in values:
            return False

        expected_set = set(range(1, self.N + 1))
        actual_set = set(values)

        return len(values) == self.N and actual_set == expected_set

    def get_line_status(self, axis: str, fixed_idx1: int, fixed_idx2: int) -> tuple[int, set[int]]:
        """
        指定されたラインの現在の状態を返す。
        戻り値: (空きセルの数, 不足している数字のセット)
        """
        values = []
        if axis == 'x': # X軸に平行なライン (y, zが固定)
            for i in range(self.N):
                values.append(self.board[i][fixed_idx1][fixed_idx2])
        elif axis == 'y': # Y軸に平行なライン (x, zが固定)
            for j in range(self.N):
                values.append(self.board[fixed_idx1][j][fixed_idx2])
        elif axis == 'z': # Z軸に平行なライン (x, yが固定)
            for k in range(self.N):
                values.append(self.board[fixed_idx1][fixed_idx2][k])
        else:
            raise ValueError("Invalid axis. Must be 'x', 'y', or 'z'.")

        empty_cells = values.count(None)
        present_numbers = set(val for val in values if val is not None)
        missing_numbers = set(range(1, self.N + 1)) - present_numbers

        return empty_cells, missing_numbers

    def is_slice_complete(self, axis: str, index: int) -> bool:
        """指定された層が完成しているか判定する (全てのセルが埋まっており、各ラインが完成しているか)"""
        # まず、その層の全てのセルが埋まっているか確認
        if axis == 'x':
            for j in range(self.N):
                for k in range(self.N):
                    if self.board[index][j][k] is None:
                        return False
        elif axis == 'y':
            for i in range(self.N):
                for k in range(self.N):
                    if self.board[i][index][k] is None:
                        return False
        elif axis == 'z':
            for i in range(self.N):
                for j in range(self.N):
                    if self.board[i][j][index] is None:
                        return False
        else:
            raise ValueError("Invalid axis. Must be 'x', 'y', or 'z'.")

        # 次に、その層に含まれる全てのラインが完成しているか確認
        if axis == 'x': # X軸スライス (x=index固定)
            for j_fixed in range(self.N): # Iterate through y-coordinates (fixed_idx2 for Z-axis lines)
                # Check lines parallel to Z-axis (fixed x=index, fixed y=j_fixed)
                if not self.is_line_complete('z', index, j_fixed): return False
            for k_fixed in range(self.N): # Iterate through z-coordinates (fixed_idx2 for Y-axis lines)
                # Check lines parallel to Y-axis (fixed x=index, fixed z=k_fixed)
                if not self.is_line_complete('y', index, k_fixed): return False
        elif axis == 'y': # Y軸スライス (y=index固定)
            for i_fixed in range(self.N): # Iterate through x-coordinates (fixed_idx1 for Z-axis lines)
                # Check lines parallel to Z-axis (fixed x=i_fixed, fixed y=index)
                if not self.is_line_complete('z', i_fixed, index): return False
            for k_fixed in range(self.N): # Iterate through z-coordinates (fixed_idx2 for X-axis lines)
                # Check lines parallel to X-axis (fixed y=index, fixed z=k_fixed)
                if not self.is_line_complete('x', index, k_fixed): return False
        elif axis == 'z': # Z軸スライス (z=index固定)
            for i_fixed in range(self.N): # Iterate through x-coordinates (fixed_idx1 for Y-axis lines)
                # Check lines parallel to Y-axis (fixed x=i_fixed, fixed z=index)
                if not self.is_line_complete('y', i_fixed, index): return False
            for j_fixed in range(self.N): # Iterate through y-coordinates (fixed_idx1 for X-axis lines)
                # Check lines parallel to X-axis (fixed y=j_fixed, fixed z=index)
                if not self.is_line_complete('x', j_fixed, index): return False
        
        return True

    def get_all_numbers(self):
        # Noneを0に変換して返す
        return [[[0 if cell is None else cell for cell in row] for row in plane] for plane in self.board]

    def get_number(self, x: int, y: int, z: int):
        """指定された座標のセルの値を取得する (0-indexed)"""
        if 0 <= x < self.N and 0 <= y < self.N and 0 <= z < self.N:
            return self.board[x][y][z]
        return None

    def get_completed_lines_and_slices(self) -> dict:
        """現在の盤面で完成しているラインと層のリストを返す"""
        completed = {'lines': [], 'slices': []}

        # ラインのチェック
        for x_idx in range(self.N):
            for y_idx in range(self.N):
                if self.is_line_complete('z', x_idx, y_idx):
                    completed['lines'].append({'axis': 'z', 'fixed_idx1': x_idx, 'fixed_idx2': y_idx})
        for y_idx in range(self.N):
            for z_idx in range(self.N):
                if self.is_line_complete('x', y_idx, z_idx):
                    completed['lines'].append({'axis': 'x', 'fixed_idx1': y_idx, 'fixed_idx2': z_idx})
        for x_idx in range(self.N):
            for z_idx in range(self.N):
                if self.is_line_complete('y', x_idx, z_idx):
                    completed['lines'].append({'axis': 'y', 'fixed_idx1': x_idx, 'fixed_idx2': z_idx})

        # 層のチェック
        for axis in ['x', 'y', 'z']:
            for index in range(self.N):
                if self.is_slice_complete(axis, index):
                    completed['slices'].append({'axis': axis, 'index': index})
        
        return completed
