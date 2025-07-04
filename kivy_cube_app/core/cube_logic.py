
from ..utils.constants import *
from ..utils.logger import AppLogger

class CubeLogic:
    def __init__(self, field, N, initial_data=None):
        self.logger = AppLogger().get_logger()
        self.N = N
        self.field = field
        self._numbers = [[[None for _ in range(self.N)] for _ in range(self.N)] for _ in range(self.N)]
        self._last_error_message = ""

        if initial_data:
            for item in initial_data:
                pos = item["pos"]
                value = item["value"]
                self.set_number(pos[0], pos[1], pos[2], value)
                self.field.reflect([pos[0]+1, pos[1]+1, pos[2]+1], value)

    def get_number(self, i, j, k):
        val = self._numbers[i][j][k]
        return val

    def set_number(self, i, j, k, value):
        self._numbers[i][j][k] = value

    def get_all_numbers(self):
        return self._numbers

    def is_valid_position(self, i, j, k):
        return 0 <= i < self.N and 0 <= j < self.N and 0 <= k < self.N

    def attempt_input(self, i, j, k, value):
        if not self.is_valid_position(i, j, k):
            self._last_error_message = "Invalid coordinates."
            return False

        if self._numbers[i][j][k] is not None and self._numbers[i][j][k] != value:
            self._last_error_message = "Invalid input: already filled."
            return False

        pos = [i+1, j+1, k+1]
        ok, message = self.field.check(pos, value)
        if ok:
            self._numbers[i][j][k] = value
            self.field.reflect(pos, value)
            self.logger.info(f"Placed {value} at ({i}, {j}, {k})")
            return True
        else:
            self._last_error_message = f"Invalid input: {message}"
            return False

    def get_last_error(self):
        return self._last_error_message

    def reset(self):
        self._numbers = [[[None for _ in range(self.N)] for _ in range(self.N)] for _ in range(self.N)]
        self._last_error_message = ""

    def can_place_number(self, value: int) -> bool:
        """
        指定された数値をキューブのどこかに配置できるかどうかをチェックします。
        実際に配置は行いません。
        """
        for i in range(self.N):
            for j in range(self.N):
                for k in range(self.N):
                    if self._numbers[i][j][k] is None: # 空いているセルのみをチェック
                        pos = [i+1, j+1, k+1] # Fieldは1ベースのインデックスを期待
                        ok, _ = self.field.check(pos, value)
                        if ok:
                            return True
        return False
