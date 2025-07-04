from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import sp

class RuleExplanationPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Game Rules'
        self.size_hint = (0.9, 0.9)

        layout = BoxLayout(orientation='vertical', padding=sp(10), spacing=sp(10))

        rules_text = """
        [b]3D 対戦数独アプリ[/b]

        [b]目的:[/b]
        3x3x3の立体数独盤に、交互に数字を配置していきます。
        最終的に、より多くのセルに正しく数字を配置できたプレイヤーの勝利です。

        [b]ルール:[/b]
        1. 各セルには1から3までの数字を配置できます。
        2. 同じ数字は、以下のいずれかのライン上に重複して配置できません。
           - X軸方向のライン (横一列)
           - Y軸方向のライン (縦一列)
           - Z軸方向のライン (奥行き一列)
        3. 配置する数字は、画面上部に表示される「Number: [数字]」に従います。
        4. 配置可能なセルは、スライスビューで選択し、再度タップすることで確定します。
        5. ルール違反の配置はできません。

        [b]操作方法:[/b]
        - [b]3D全体表示 (左側):[/b]
          - ドラッグ: 視点回転
          - スクロール/ZOOMボタン: ズームイン/アウト
          - RESET VIEWボタン: 視点を初期状態に戻す
        - [b]スライスビュー (右側):[/b]
          - Axis (X/Z): 表示する軸を選択
          - Depthスライダー: 表示する層を選択
          - セルタップ: セルを選択 (ハイライト表示)
          - 選択中のセルを再度タップ: 数字を配置 (ルールに従って)

        [b]スコア:[/b]
        - 数字を配置するごとにスコアが加算されます。
        - 最終的なスコアで勝敗が決まります。
        """
        rules_label = Label(text=rules_text, markup=True, font_size=sp(14),
                            halign='left', valign='top', size_hint_y=None)
        rules_label.bind(texture_size=rules_label.setter('size'))
        layout.add_widget(rules_label)

        close_button = Button(text='Close', size_hint_y=None, height=sp(40))
        close_button.bind(on_release=self.dismiss)
        layout.add_widget(close_button)

        self.content = layout
