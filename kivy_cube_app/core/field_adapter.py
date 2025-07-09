from ..utils.logger import AppLogger
from .field import Field


class FieldAdapter:
    def __init__(self, N, logic=None, initial_data=None):
        self.N = N
        self.logger = AppLogger().get_logger()
        self.logic = logic
        self.f = Field(N=self.N, logger=self.logger, initial_data=initial_data)

    def check(self, pos, num):
        # もし logic に依存したチェックを組み込むならここで参照可能
        return self.f.check(pos, num)

    def reflect(self, pos, num):
        # Field に値をセット＆反映
        self.f.set_point(pos, num)
        self.f.reflect(pos, num)
        # 外部ロジック側にも何らか通知をしたい場合は……
        # if self.logic:
        #     self.logic.on_field_updated(pos, num)

    def get_all_numbers(self):
        return self.f.get_all_numbers()

    def reset(self):
        """盤面と候補を初期状態に戻す"""
        self.f = Field(logger=self.logger, N=self.N)
