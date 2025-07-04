
from random import shuffle
import copy
from ..utils.constants import *

class CpuPlayer:
    def __init__(self, logic, field, N):
        self.logic = logic
        self.field = field
        self.N = N

    def make_move(self, current_number):
        possible_moves = []
        val = current_number
        for i in range(self.N):
            for j in range(self.N):
                for k in range(self.N):
                    if self.logic.get_number(i, j, k) is None:
                        pos = [i + 1, j + 1, k + 1]
                        ok, message = self.field.check(pos, val)
                        if ok:
                            possible_moves.append((i, j, k))
                        else:
                            self.logic.field.logger.debug(f"Check failed for pos {pos} with num {val}: {message}")

        if possible_moves:
            # 各手を評価し、最適な手を選択する
            best_move = None
            best_score = -1 # 評価スコア。高いほど良い手

            for move in possible_moves:
                i, j, k = move
                # 仮に手を打ってみる (ボードの状態を直接変更しない)
                # ここでは、FieldAdapterのcheck/reflectを直接呼び出すのではなく、
                # 仮想的なボードの状態をシミュレートする必要がある。
                # しかし、FieldAdapterはFieldのインスタンスを直接持っているので、
                # Fieldのメソッドを直接呼び出すことでシミュレーションが可能。

                # 仮想的なボードの状態をコピー
                original_board = copy.deepcopy(self.field.f.board)
                original_candidates = copy.deepcopy(self.field.f.candidates)

                # 仮に手を打つ
                self.field.f.set_point([i+1, j+1, k+1], val)
                self.field.f.reflect([i+1, j+1, k+1], val)

                # 手を評価する
                current_score = 0
                completed_info = self.field.f.get_completed_lines_and_slices()
                current_score += len(completed_info['lines']) * 10 # 完成ラインは高得点
                current_score += len(completed_info['slices']) * 100 # 完成層はさらに高得点

                # リーチの評価
                one_away_lines = 0
                one_away_slices = 0

                # ラインのリーチチェック
                for x_idx in range(self.N):
                    for y_idx in range(self.N):
                        empty, missing = self.field.f.get_line_status('z', x_idx, y_idx)
                        if empty == 1 and current_number in missing:
                            one_away_lines += 1
                for y_idx in range(self.N):
                    for z_idx in range(self.N):
                        empty, missing = self.field.f.get_line_status('x', y_idx, z_idx)
                        if empty == 1 and current_number in missing:
                            one_away_lines += 1
                for x_idx in range(self.N):
                    for z_idx in range(self.N):
                        empty, missing = self.field.f.get_line_status('y', x_idx, z_idx)
                        if empty == 1 and current_number in missing:
                            one_away_lines += 1
                
                # 層のリーチチェック (簡略化: 層内のいずれかのラインがリーチであれば層もリーチとみなす)
                for axis in ['x', 'y', 'z']:
                    for index in range(self.N):
                        is_slice_one_away = False
                        if axis == 'x': # X軸スライス (x=index固定)
                            for j_fixed in range(self.N):
                                empty, missing = self.field.f.get_line_status('z', index, j_fixed)
                                if empty == 1 and current_number in missing:
                                    is_slice_one_away = True
                                    break
                            if not is_slice_one_away:
                                for k_fixed in range(self.N):
                                    empty, missing = self.field.f.get_line_status('y', index, k_fixed)
                                    if empty == 1 and current_number in missing:
                                        is_slice_one_away = True
                                        break
                        elif axis == 'y': # Y軸スライス (y=index固定)
                            for i_fixed in range(self.N):
                                empty, missing = self.field.f.get_line_status('z', i_fixed, index)
                                if empty == 1 and current_number in missing:
                                    is_slice_one_away = True
                                    break
                            if not is_slice_one_away:
                                for k_fixed in range(self.N):
                                    empty, missing = self.field.f.get_line_status('x', index, k_fixed)
                                    if empty == 1 and current_number in missing:
                                        is_slice_one_away = True
                                        break
                        elif axis == 'z': # Z軸スライス (z=index固定)
                            for i_fixed in range(self.N):
                                empty, missing = self.field.f.get_line_status('y', i_fixed, index)
                                if empty == 1 and current_number in missing:
                                    is_slice_one_away = True
                                    break
                            if not is_slice_one_away:
                                for j_fixed in range(self.N):
                                    empty, missing = self.field.f.get_line_status('x', j_fixed, index)
                                    if empty == 1 and current_number in missing:
                                        is_slice_one_away = True
                                        break
                        
                        if is_slice_one_away:
                            one_away_slices += 1

                current_score += one_away_lines * 5 # リーチラインは中程度の得点
                current_score += one_away_slices * 50 # リーチ層は高得点
                # 評価後、ボードの状態を元に戻す
                self.field.f.board = original_board
                self.field.f.candidates = original_candidates

                if current_score > best_score:
                    best_score = current_score
                    best_move = move
            
            if best_move:
                i, j, k = best_move
                if self.logic.attempt_input(i, j, k, val):
                    self.logic.field.logger.debug(f"Selected best move: {best_move} with score {best_score}. Placed {val}.")
                    return True
        return False
