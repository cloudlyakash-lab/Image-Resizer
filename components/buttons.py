"""
Modern Buttons and Interactive Chips in pure Python.
"""
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import ListProperty, NumericProperty, BooleanProperty
from utils.theme import theme

class PrimaryButton(Button):
    """
    High-visibility primary action button.
    """
    bg_color = ListProperty([0.15, 0.45, 0.95, 1.0])
    radius = NumericProperty(12)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [0, 0, 0, 0] # Transparent default texture
        self.background_normal = ''
        self.background_down = ''
        self.color = theme.text_on_primary
        self.font_size = kwargs.get('font_size', '16sp')
        self.bold = True
        self.size_hint_y = None
        self.height = kwargs.get('height', 52)
        self.bg_color = theme.primary

        with self.canvas.before:
            self._bg_color_instr = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.bind(state=self._on_state_change)
        theme.bind(primary=self._on_theme_change, primary_variant=self._on_theme_change)

    def _on_state_change(self, instance, value):
        if value == 'down':
            self._bg_color_instr.rgba = theme.primary_variant
        else:
            self._bg_color_instr.rgba = theme.primary

    def _on_theme_change(self, *args):
        self._bg_color_instr.rgba = theme.primary
        self.color = theme.text_on_primary

    def _update_canvas(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size


class SecondaryButton(Button):
    """
    Outlined secondary action button.
    """
    bg_color = ListProperty([0, 0, 0, 0])
    border_color = ListProperty([0.88, 0.90, 0.94, 1.0])
    radius = NumericProperty(12)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [0, 0, 0, 0]
        self.background_normal = ''
        self.background_down = ''
        self.color = theme.text_primary
        self.font_size = kwargs.get('font_size', '15sp')
        self.bold = True
        self.size_hint_y = None
        self.height = kwargs.get('height', 48)
        self.border_color = theme.border

        with self.canvas.before:
            self._bg_color_instr = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._border_color_instr = Color(*self.border_color)
            self._border_line = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, self.radius], width=1.5)

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.bind(state=self._on_state_change)
        theme.bind(border=self._on_theme_change, text_primary=self._on_theme_change, surface_variant=self._on_theme_change)

    def _on_state_change(self, instance, value):
        if value == 'down':
            self._bg_color_instr.rgba = theme.surface_variant
        else:
            self._bg_color_instr.rgba = [0, 0, 0, 0]

    def _on_theme_change(self, *args):
        self.border_color = theme.border
        self._border_color_instr.rgba = self.border_color
        self.color = theme.text_primary

    def _update_canvas(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border_line.rounded_rectangle = [self.x, self.y, self.width, self.height, self.radius]


class ChipButton(Button):
    """
    Selectable toggle chip for presets and options.
    """
    is_active = BooleanProperty(False)
    radius = NumericProperty(10)

    def __init__(self, **kwargs):
        self.is_active = kwargs.pop('is_active', False)
        super().__init__(**kwargs)
        self.background_color = [0, 0, 0, 0]
        self.background_normal = ''
        self.background_down = ''
        self.font_size = kwargs.get('font_size', '14sp')
        self.size_hint_y = None
        self.height = kwargs.get('height', 38)
        self.size_hint_x = kwargs.get('size_hint_x', None)
        self.width = kwargs.get('width', 70)

        with self.canvas.before:
            self._bg_color_instr = Color(1, 1, 1, 1)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._border_color_instr = Color(0, 0, 0, 0)
            self._border_line = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, self.radius], width=1)

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.bind(is_active=self._update_active_state)
        theme.bind(primary=self._update_active_state, surface_variant=self._update_active_state, text_primary=self._update_active_state)
        self._update_active_state()

    def _update_active_state(self, *args):
        if self.is_active:
            self._bg_color_instr.rgba = theme.primary
            self._border_color_instr.rgba = theme.primary
            self.color = theme.text_on_primary
            self.bold = True
        else:
            self._bg_color_instr.rgba = theme.surface_variant
            self._border_color_instr.rgba = theme.border
            self.color = theme.text_primary
            self.bold = False

    def _update_canvas(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border_line.rounded_rectangle = [self.x, self.y, self.width, self.height, self.radius]
