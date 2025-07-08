from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget    import Widget
from kivy.uix.label     import Label
from kivy.uix.slider    import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button    import Button
from kivy.uix.popup     import Popup
from kivy.graphics      import Color, Rectangle, Ellipse, Mesh, Line
from kivy.core.text     import Label as CoreLabel
from kivy.core.window   import Window
from kivy.properties    import NumericProperty, ListProperty, StringProperty
from kivy.metrics       import sp
from time                import time
from math                import cos, sin, radians
from ..utils.constants import LENGTH_OF_SIDE

class Cube3DWidget(BoxLayout):
    # --- Full view state ---
    angle_x = NumericProperty(30)
    angle_y = NumericProperty(30)
    zoom    = NumericProperty(1.0) # Will be calculated dynamically
    cube_alpha = NumericProperty(0.7) # New property for transparency

    # --- Slice view state (independent) ---
    slice_angle_x = NumericProperty(30)
    slice_angle_y = NumericProperty(30)
    slice_zoom    = NumericProperty(1.0)

    # Slice control
    slice_axis   = StringProperty('z')     # 'x' or 'z'
    slice_index  = NumericProperty(1)      # 0～LENGTH_OF_SIDE-1
    selected_index = ListProperty([-1, -1, -1])

    cube_spacing = 80 # Original value
    box_size     = 25 # Original value

    def __init__(self, logic, get_current_number_fn, get_upcoming_fn, initial_filled=None, **kwargs):
        super().__init__(orientation='vertical', padding=0, spacing=0, **kwargs)
        Window.bind(on_scroll=self.on_mouse_scroll)

        self.logic              = logic
        self.get_current_number = get_current_number_fn
        self.get_upcoming       = get_upcoming_fn
        self.initial_filled     = initial_filled or []
        self._pending_number    = None
        self._error_time        = 0

        # === Header: Upcoming sequence and Timer ===
        header = BoxLayout(size_hint_y=None, height=sp(40), padding=(sp(5),0), spacing=sp(1))
        header.add_widget(Widget(size_hint_x=1))
        self.lbl_now  = Label(size_hint_x=None, width=sp(35), font_size=sp(30), bold=True)
        self.lbl_next = Label(size_hint_x=None, width=sp(30), font_size=sp(20))
        self.lbl_n2   = Label(size_hint_x=None, width=sp(30), font_size=sp(20))
        self.lbl_rest = Label(size_hint_x=None, width=sp(200), font_size=sp(12), shorten=True, shorten_from='right')
        self.lbl_timer = Label(size_hint_x=None, width=sp(100), font_size=sp(20), text='00:00') # New timer label
        self.lbl_status_message = Label(size_hint_x=None, width=sp(300), font_size=sp(16), text='', halign='center', valign='middle') # New status message label
        for lbl in (self.lbl_now, self.lbl_next, self.lbl_n2, self.lbl_rest, self.lbl_timer, self.lbl_status_message): # Add status message label
            header.add_widget(lbl)
        header.add_widget(Widget(size_hint_x=1))
        self.add_widget(header)

        # === Body: Two canvases side by side ===
        body = BoxLayout(orientation='horizontal', size_hint=(1,0.8), spacing=sp(10))
        self.full_canvas  = Widget()
        self.slice_canvas = Widget()
        # Bind redraw on resize/pos
        self.full_canvas.bind(pos=self.redraw, size=self.redraw)
        self.slice_canvas.bind(pos=self.redraw, size=self.redraw)
        # Full canvas: allow touch rotate
        self.full_canvas.bind(on_touch_down=self._on_full_touch_down,
                              on_touch_move=self._on_full_touch_move,
                              on_touch_up=self._on_full_touch_up)
        # Slice canvas: allow touch for number placement only
        self.slice_canvas.bind(on_touch_down=self._on_slice_touch_down)
        body.add_widget(self.full_canvas)
        body.add_widget(self.slice_canvas)
        self.add_widget(body)

        # === Full view controls ===
        buttons = BoxLayout(size_hint_y=None, height=sp(50), spacing=sp(5))
        for txt, fn in [('SPIN X+', lambda: self.rotate('x',10)),
                       ('SPIN X-', lambda: self.rotate('x',-10)),
                       ('SPIN Y+', lambda: self.rotate('y',10)),
                       ('SPIN Y-', lambda: self.rotate('y',-10)),
                       ('+ALPHA',  lambda: self.adjust_alpha(0.1)),
                       ('-ALPHA',  lambda: self.adjust_alpha(-0.1)),
                       ('RESET VIEW', lambda: self.reset_view())]:
            b = Button(text=txt, size_hint_x=None, width=sp(70))
            b.bind(on_release=lambda inst, fn=fn: fn())
            buttons.add_widget(b)
        self.add_widget(buttons)

        # === Slice view controls ===
        ctrl = BoxLayout(size_hint_y=None, height=sp(40), spacing=sp(5))
        ctrl.add_widget(Label(text='Axis:', size_hint_x=None, width=sp(40)))
        btn_x = ToggleButton(text='X', group='axis', state='normal', size_hint_x=None, width=sp(40))
        btn_z = ToggleButton(text='Z', group='axis', state='down',   size_hint_x=None, width=sp(40))
        btn_x.bind(on_release=lambda *_: self._set_slice_axis('x'))
        btn_z.bind(on_release=lambda *_: self._set_slice_axis('z'))
        ctrl.add_widget(btn_x); ctrl.add_widget(btn_z)
        ctrl.add_widget(Label(text='Depth:', size_hint_x=None, width=sp(50)))
        slider = Slider(min=0, max=LENGTH_OF_SIDE-1, step=1, value=self.slice_index)
        slider.bind(value=lambda _, v: self._on_slice_index_changed(int(v)))
        ctrl.add_widget(slider)
        self.add_widget(ctrl)

        # Initial display
        self.update_upcoming_display()
        self._calculate_optimal_zoom() # Calculate initial zoom

    def set_on_success_input(self, fn):
        self._on_success_input = fn

    def update_upcoming_display(self, *args):
        ups = self.get_upcoming()
        self.lbl_now.text  = str(ups[0]) if len(ups)>0 else ''
        self.lbl_next.text = str(ups[1]) if len(ups)>1 else ''
        self.lbl_n2.text   = str(ups[2]) if len(ups)>2 else ''
        self.lbl_rest.text = ','.join(map(str,ups[3:]))

    def update_timer_display(self, elapsed_time_seconds):
        minutes = int(elapsed_time_seconds // 60)
        seconds = int(elapsed_time_seconds % 60)
        self.lbl_timer.text = f"{minutes:02d}:{seconds:02d}"

    def set_number_skip_notification_callback(self, fn):
        self._on_number_skip_notification = fn

    def _on_number_skip_notification(self, skipped_number):
        # ポップアップ表示
        popup_content = BoxLayout(orientation='vertical')
        popup_content.add_widget(Label(text=f"Number {skipped_number} skipped!", font_size=sp(24)))
        popup = Popup(title='Number Skipped',
                      content=popup_content,
                      size_hint=(0.5, 0.3))
        popup.open()

        # ステータスバーに表示
        self.lbl_status_message.text = f"Number {skipped_number} skipped!"
        # 3秒後にメッセージをクリア
        Clock.schedule_once(lambda dt: self._clear_status_message(), 3)

    def _clear_status_message(self):
        self.lbl_status_message.text = ''

    def on_mouse_scroll(self, window, x, y, scroll_x, scroll_y):
        self.adjust_alpha(scroll_y * 0.1)

    # --- Full view rotation handlers ---
    def _on_full_touch_down(self, widget, touch):
        if widget is self.full_canvas and self.full_canvas.collide_point(*touch.pos):
            touch.grab(self.full_canvas)
            return True
        return False

    def _on_full_touch_move(self, widget, touch):
        if touch.grab_current is self.full_canvas:
            if getattr(touch,'is_mouse_scrolling',False): return
            self.angle_y += touch.dx * 0.3
            self.angle_x -= touch.dy * 0.3
            self.redraw(); self.redraw_info()
            return True
        return False

    def _on_full_touch_up(self, widget, touch):
        if touch.grab_current is self.full_canvas:
            touch.ungrab(self.full_canvas)
            return True
        return False

    def _on_slice_touch_down(self, widget, touch):
        # 右側スライスキャンバス上でのみ有効
        cvs = self.slice_canvas
        if widget is cvs and cvs.collide_point(*touch.pos):
            self.logic.field.logger.debug(f"Slice touch down at {touch.pos}")
            # グリッドサイズを計算
            side   = LENGTH_OF_SIDE
            rect_w = cvs.width  / side
            rect_h = cvs.height / side
            self.logic.field.logger.debug(f"DEBUG: cvs.x={cvs.x}, cvs.y={cvs.y}, cvs.width={cvs.width}, cvs.height={cvs.height}")
            self.logic.field.logger.debug(f"DEBUG: rect_w={rect_w}, rect_h={rect_h}")
            # タッチ位置から列・行を取得
            col = int((touch.x - cvs.x) // rect_w)
            row = int((touch.y - cvs.y) // rect_h)
            self.logic.field.logger.debug(f"DEBUG: touch.x={touch.x}, touch.y={touch.y}, col={col}, row={row}")
            # 範囲チェック
            if 0 <= col < side and 0 <= row < side:
                # スライス軸に応じて(i,j,k)を決定
                if self.slice_axis == 'x':
                    i, j, k = self.slice_index, row, col
                else:  # 'z'
                    i, j, k = col, row, self.slice_index
                self.logic.field.logger.debug(f"Calculated cube coords: ({i}, {j}, {k})")
                # 固定セルは入力不可
                if [i, j, k] in [item["pos"] for item in self.initial_filled]:
                    self.logic.field.logger.debug(f"Cell ({i}, {j}, {k}) is an initial filled cell. Not selectable.")
                    return True
                
                self.logic.field.logger.debug(f"Current selected_index: {self.selected_index}")
                # 選択中のセルを再度タップした場合に配置
                if tuple(self.selected_index) == (i, j, k):
                    self.logic.field.logger.debug(f"Double tap on ({i}, {j}, {k}). Attempting input.")
                    val     = self.get_current_number()
                    success = self.logic.attempt_input(i, j, k, val)
                    if not success:
                        self.logic.field.logger.debug(f"Input failed: {self.logic.get_last_error()}")
                        from kivy.uix.popup import Popup
                        from kivy.uix.label import Label
                        Popup(title='Invalid Input',
                            content=Label(text=self.logic.get_last_error()),
                            size_hint=(0.6,0.3)).open()
                    else:
                        self.logic.field.logger.debug(f"Input successful for ({i}, {j}, {k}) with value {val}.")
                        # 成功時のコールバック
                        if hasattr(self, "_on_success_input"):
                            self._on_success_input()
                        self.update_upcoming_display()
                    self.selected_index = [-1, -1, -1] # 選択解除
                    self.logic.field.logger.debug(f"Selected index after input: {self.selected_index}")
                else:
                    self.selected_index = [i, j, k]
                    self.logic.field.logger.debug(f"Selected index updated to: {self.selected_index}")
                self.redraw(); self.redraw_info()
                return True
        return False

    # Buttons
    def rotate(self, axis, amount):
        if axis=='x': self.angle_x += amount
        else:         self.angle_y += amount
        self.redraw(); self.redraw_info()

    def adjust_alpha(self, delta):
        self.cube_alpha = max(0.1, min(1.0, self.cube_alpha + delta))
        self.redraw(); self.redraw_info()

    def reset_view(self):
        self.angle_x = 30
        self.angle_y = 30
        self.zoom = 1.0 # Reset zoom to default
        self.cube_alpha = 0.7 # Reset alpha to default
        self.redraw(); self.redraw_info()

    def redraw_info(self):
        self.update_upcoming_display()

    def _calculate_optimal_zoom(self):
        # Calculate the maximum extent of the cube in its local coordinate system
        # This is the distance from the center of the first cube to the center of the last cube,
        # plus the size of one cube (2 * box_size)
        max_extent = (LENGTH_OF_SIDE - 1) * self.cube_spacing + (2 * self.box_size)

        # Determine the available space in the full_canvas
        # We want to fit the cube within the smaller dimension of the canvas
        # Add some padding (e.g., 1.2 to leave some margin)
        if self.full_canvas.width > 0 and self.full_canvas.height > 0:
            available_space = min(self.full_canvas.width, self.full_canvas.height)
            # Adjust zoom to fit the cube with some margin
            self.zoom = (available_space / max_extent) * 0.4 # Adjusted factor for better fit
            # Ensure zoom is within reasonable bounds
            self.zoom = max(0.1, min(2.5, self.zoom))

    # --- Redraw both canvases ---
    def redraw(self, *args):
        from ..utils.constants import LENGTH_OF_SIDE
        # Recalculate optimal zoom on redraw if canvas size changes
        self._calculate_optimal_zoom()

        # --- 全体ビュー (左) ---
        cvs = self.full_canvas
        cvs.canvas.clear(); cvs.canvas.before.clear()
        with cvs.canvas.before:
            Color(1,1,1,1); Rectangle(pos=cvs.pos, size=cvs.size)
        with cvs.canvas:
            # （既存の3D描画ロジックをそのまま流用）
            coords = [i - (LENGTH_OF_SIDE // 2) for i in range(LENGTH_OF_SIDE)]
            for i, x in enumerate(coords):
                for j, y in enumerate(coords):
                    for k, z in enumerate(coords):
                        num = self.logic.get_number(i,j,k)
                        initial_cell = next((item for item in self.initial_filled if item["pos"] == [i, j, k]), None)
                        if initial_cell:
                            num = initial_cell["value"]
                        cx, cy, cz = x*self.cube_spacing, y*self.cube_spacing, z*self.cube_spacing
                        highlight = (
                            (self.slice_axis=='x' and i==self.slice_index) or
                            (self.slice_axis=='z' and k==self.slice_index)
                        )
                        is_initial = initial_cell is not None
                        self._draw_box(cvs, cx, cy, cz,
                                       num,
                                       highlight=highlight,
                                       error=False,
                                       layer=j,
                                       is_initial=is_initial)
        # --- スライスビュー 2Dフラット (右) ---
        from kivy.graphics import RoundedRectangle
        cvs = self.slice_canvas
        cvs.canvas.clear(); cvs.canvas.before.clear()
        with cvs.canvas.before:
            Color(0.95,0.95,0.95,1); Rectangle(pos=cvs.pos, size=cvs.size)
        with cvs.canvas:
            rect_w = cvs.width  / LENGTH_OF_SIDE
            rect_h = cvs.height / LENGTH_OF_SIDE
            for row in range(LENGTH_OF_SIDE):
                for col in range(LENGTH_OF_SIDE):
                    # マッピング
                    if self.slice_axis == 'x':
                        i, j, k = self.slice_index, row, col
                    else:
                        i, j, k = col, row, self.slice_index
                    num = self.logic.get_number(i,j,k)
                    initial_cell = next((item for item in self.initial_filled if item["pos"] == [i, j, k]), None)
                    if initial_cell:
                        num = initial_cell["value"]
                    x0  = cvs.x + col * rect_w
                    y0  = cvs.y + row * rect_h
                    # 背景色
                    bg = self.get_color_by_number(num) if num else (1,1,1)
                    Color(*bg,1)
                    RoundedRectangle(pos=(x0, y0),
                                    size=(rect_w, rect_h),
                                    radius=[(8,8),(8,8),(8,8),(8,8)])
                    # 枠線＋選択セルハイライト
                    if (i,j,k) == tuple(self.selected_index):
                        Color(1,0.5,0,1)
                        Line(rectangle=(x0+1, y0+1, rect_w-2, rect_h-2), width=2)
                    else:
                        Color(0.2,0.2,0.2,1)
                        Line(rectangle=(x0, y0, rect_w, rect_h), width=1)
                    # 数字描画
                    if num:
                        lbl = CoreLabel(text=str(num), font_size=sp(24), bold=True)
                        lbl.refresh()
                        tx = x0 + rect_w/2 - lbl.texture.width/2
                        ty = y0 + rect_h/2 - lbl.texture.height/2
                        Color(0,0,0,1)
                        Rectangle(texture=lbl.texture,
                                pos=(tx, ty),
                                size=lbl.texture.size)

    # Draw a single cube on specified canvas
    def _draw_box(self, cvs, cx, cy, cz, num, highlight, error, layer, is_initial=False):
        half = self.box_size
        pts = [(cx+dx*half, cy+dy*half, cz+dz*half)
               for dx in (-1,1) for dy in (-1,1) for dz in (-1,1)]
        edges = [(0,1),(1,3),(3,2),(2,0),(4,5),(5,7),(7,6),(6,4),(0,4),(1,5),(2,6),(3,7)]
        # 全6面分のフェイス定義
        # (前面, 背面, 上面, 底面, 右面, 左面)
        faces = [
            (4, 5, 7, 6),  # 前面 (z+)
            (0, 1, 3, 2),  # 背面 (z-)
            (2, 3, 7, 6),  # 上面 (y+)
            (0, 1, 5, 4),  # 底面 (y-)
            (1, 3, 7, 5),  # 右面 (x+)
            (0, 2, 6, 4),  # 左面 (x-)
        ]
        # --- Use cube_alpha for transparency ---
        if not num and not highlight:
            # Empty & not highlighted -> very faint
            alpha_val = self.cube_alpha * 0.2
            face_color = (0.8, 0.8, 0.8)
        elif not num and  highlight:
            # Empty & highlighted -> slightly more visible
            alpha_val = self.cube_alpha * 0.4
            face_color = (0.8, 0.8, 0.8)
        else:
            # Numbered cell / highlighted -> full alpha
            alpha_val = self.cube_alpha
            face_color = self.get_color_by_number(num) if num else (0.8, 0.8, 0.8)
        Color(face_color[0], face_color[1], face_color[2], alpha_val)
        for f in faces:
            verts = []
            for idx in f:
                sx, sy = self._project_to(cvs, *pts[idx])
                verts += [sx, sy, 0, 0]
            Mesh(vertices=verts, indices=[0,1,2,0,2,3], mode='triangles')
        # 強調表示なら黄色の太線、そうでないなら黒の細線
        if highlight:
            Color(0.7, 0.7, 0, 0.4)  # 黄色
            w = 1.5
        else:
            Color(0.7, 0.7, 0.7, 0.4)  # 灰色
            w = 0.8
        for a,b in edges:
            x1,y1 = self._project_to(cvs, *pts[a]); x2,y2 = self._project_to(cvs, *pts[b])
            Line(points=[x1,y1,x2,y2], width=w)
        if num:
            sx, sy = self._project_to(cvs, cx, cy, cz)
            lbl = CoreLabel(text=str(num), font_size=18); lbl.refresh()
            Color(0,0,0,1)
            Rectangle(texture=lbl.texture,
                      pos=(sx-lbl.texture.width/2, sy-lbl.texture.height/2),
                      size=lbl.texture.size)

    # 3D projection using respective view state
    def _project_to(self, cvs, x, y, z):
        if cvs is self.full_canvas:
            ax, ay, zoom = radians(self.angle_x), radians(self.angle_y), self.zoom
        else:
            ax, ay, zoom = radians(self.slice_angle_x), radians(self.slice_angle_y), self.slice_zoom
        dx = cos(ay)*x - sin(ay)*z
        dz = sin(ay)*x + cos(ay)*z
        dy = cos(ax)*y - sin(ax)*dz
        dz = sin(ax)*y + cos(ax)*dz
        return cvs.center_x + dx*zoom, cvs.center_y + dy*zoom

    def get_color_by_number(self, num):
        return {1:(0.3,0.6,1),2:(0.3,1,0.3),3:(1,0.3,0.3)}.get(num,(0,0,0))

    def _set_slice_axis(self, axis):
        self.slice_axis = axis
        self.redraw()

    def _on_slice_index_changed(self, idx):
        self.slice_index = idx
        self.redraw()


