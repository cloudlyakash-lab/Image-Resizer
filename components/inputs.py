"""
Modern Rounded TextInput and Labeled Field Components in pure Python.
"""
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from utils.theme import theme

class RoundedTextInput(TextInput):
    """
    Modern TextInput with rounded border, dynamic placeholder, and clean cursor.
    """
    radius = NumericProperty(10)
    is_focused = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [0, 0, 0, 0]
        self.background_normal = ''
        self.background_active = ''
        self.cursor_color = theme.primary
        self.foreground_color = theme.text_primary
        self.hint_text_color = theme.text_hint
        self.padding = [14, 12, 14, 12]
        self.font_size = kwargs.get('font_size', '16sp')
        self.multiline = kwargs.get('multiline', False)
        self.size_hint_y = None
        self.height = kwargs.get('height', 48)

        with self.canvas.before:
            self._bg_color_instr = Color(*theme.surface_variant)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._border_color_instr = Color(*theme.border)
            self._border_line = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, self.radius], width=1.2)

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.bind(focus=self._on_focus)
        theme.bind(surface_variant=self._on_theme_change, border=self._on_theme_change, primary=self._on_theme_change, text_primary=self._on_theme_change)

    def _on_focus(self, instance, value):
        self.is_focused = value
        if value:
            self._border_color_instr.rgba = theme.primary
            self._border_line.width = 1.8
        else:
            self._border_color_instr.rgba = theme.border
            self._border_line.width = 1.2

    def _on_theme_change(self, *args):
        self.cursor_color = theme.primary
        self.foreground_color = theme.text_primary
        self.hint_text_color = theme.text_hint
        self._bg_color_instr.rgba = theme.surface_variant
        if not self.is_focused:
            self._border_color_instr.rgba = theme.border

    def _update_canvas(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border_line.rounded_rectangle = [self.x, self.y, self.width, self.height, self.radius]


class LabeledInputField(BoxLayout):
    """
    Combines a header label with a rounded text input.
    """
    def __init__(self, label_text: str, hint_text: str = "", input_filter: str = None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 6
        self.size_hint_y = None
        self.height = 76

        self.label = Label(
            text=label_text,
            color=theme.text_secondary,
            font_size='13sp',
            bold=True,
            size_hint_y=None,
            height=20,
            halign='left',
            valign='middle'
        )
        self.label.bind(size=self.label.setter('text_size'))
        theme.bind(text_secondary=self._update_label_color)

        self.input = RoundedTextInput(
            hint_text=hint_text,
            input_filter=input_filter,
            height=48
        )

        self.add_widget(self.label)
        self.add_widget(self.input)

    def _update_label_color(self, *args):
        self.label.color = theme.text_secondary
