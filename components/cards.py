"""
Custom Card and Container widgets in pure Python using Kivy Canvas instructions.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import ListProperty, NumericProperty
from utils.theme import theme

class RoundedCard(BoxLayout):
    """
    A modern container card with rounded corners, dynamic theme background, and border.
    """
    bg_color = ListProperty([1, 1, 1, 1])
    border_color = ListProperty([0.88, 0.90, 0.94, 1.0])
    radius = NumericProperty(16)
    border_width = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = kwargs.get('orientation', 'vertical')
        self.padding = kwargs.get('padding', [16, 16, 16, 16])
        self.spacing = kwargs.get('spacing', 12)
        self.bg_color = theme.surface
        self.border_color = theme.border

        with self.canvas.before:
            self._bg_color_instr = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._border_color_instr = Color(*self.border_color)
            self._border_line = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, self.radius], width=self.border_width)

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.bind(bg_color=self._update_colors, border_color=self._update_colors)
        theme.bind(surface=self._on_theme_change, border=self._on_theme_change)

    def _on_theme_change(self, instance, value):
        self.bg_color = theme.surface
        self.border_color = theme.border

    def _update_canvas(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border_line.rounded_rectangle = [self.x, self.y, self.width, self.height, self.radius]

    def _update_colors(self, *args):
        self._bg_color_instr.rgba = self.bg_color
        self._border_color_instr.rgba = self.border_color
