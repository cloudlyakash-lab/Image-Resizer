"""
Settings Screen: Appearance (Light/Dark), defaults configuration, and About info.
"""
import json
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

from components.cards import RoundedCard
from components.buttons import PrimaryButton, SecondaryButton, ChipButton
from utils.constants import SUPPORTED_OUTPUT_FORMATS
from utils.theme import theme

SETTINGS_FILE = os.path.join(os.path.expanduser('~'), '.imageresizer_settings.json')

class SettingsScreen(Screen):
    """
    Manages local preferences (theme, default quality, default format) and About details.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_data = self._load_settings()

        with self.canvas.before:
            self._bg_color_instr = Color(*theme.background)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        theme.bind(background=lambda i, v: setattr(self._bg_color_instr, 'rgba', v))

        self._build_ui()

    def _update_canvas(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _load_settings(self) -> dict:
        default = {
            "theme": "light",
            "default_quality": 90,
            "default_format": "JPG"
        }
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    return {**default, **json.load(f)}
            except Exception:
                pass
        return default

    def _save_settings(self):
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings_data, f, indent=2)
        except Exception as e:
            print(f"[SettingsScreen] Save settings error: {e}")

    def _build_ui(self):
        root_layout = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=12)

        # 1. Top Header
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=44, spacing=10)
        back_btn = SecondaryButton(text="← Back", size_hint=(None, None), size=(80, 40), font_size='13sp')
        back_btn.bind(on_release=lambda *a: self._go_back())
        
        title_lbl = Label(
            text="Settings & About",
            color=theme.text_primary,
            font_size='18sp',
            bold=True,
            halign='center',
            valign='middle'
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))
        theme.bind(text_primary=lambda i, v: setattr(title_lbl, 'color', v))

        top_bar.add_widget(back_btn)
        top_bar.add_widget(title_lbl)
        root_layout.add_widget(top_bar)

        # 2. Scrollable Body
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content_box = BoxLayout(orientation='vertical', spacing=14, size_hint_y=None)
        content_box.bind(minimum_height=content_box.setter('height'))

        # Card 1: Appearance
        theme_card = RoundedCard(orientation='vertical', padding=[16, 14, 16, 14], spacing=10, size_hint_y=None, height=110)
        theme_title = Label(text="Appearance", color=theme.text_primary, font_size='15sp', bold=True, size_hint_y=None, height=22, halign='left', valign='middle')
        theme_title.bind(size=theme_title.setter('text_size'))
        theme.bind(text_primary=lambda i, v: setattr(theme_title, 'color', v))
        theme_card.add_widget(theme_title)

        theme_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        self.light_chip = ChipButton(text="☀️ Light Mode", is_active=(self.settings_data['theme'] == 'light'), size_hint_x=1)
        self.dark_chip = ChipButton(text="🌙 Dark Mode", is_active=(self.settings_data['theme'] == 'dark'), size_hint_x=1)

        self.light_chip.bind(on_release=lambda *a: self._set_theme('light'))
        self.dark_chip.bind(on_release=lambda *a: self._set_theme('dark'))

        theme_row.add_widget(self.light_chip)
        theme_row.add_widget(self.dark_chip)
        theme_card.add_widget(theme_row)
        content_box.add_widget(theme_card)

        # Card 2: Default Quality
        q_card = RoundedCard(orientation='vertical', padding=[16, 14, 16, 14], spacing=10, size_hint_y=None, height=110)
        q_title = Label(text="Default Quality", color=theme.text_primary, font_size='15sp', bold=True, size_hint_y=None, height=22, halign='left', valign='middle')
        q_title.bind(size=q_title.setter('text_size'))
        theme.bind(text_primary=lambda i, v: setattr(q_title, 'color', v))
        q_card.add_widget(q_title)

        q_row = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=40)
        self.q_chips = {}
        for q_val in [80, 90, 95, 100]:
            chip = ChipButton(text=f"{q_val}%", is_active=(self.settings_data['default_quality'] == q_val), size_hint_x=1)
            chip.bind(on_release=lambda btn, q=q_val: self._set_default_quality(q))
            self.q_chips[q_val] = chip
            q_row.add_widget(chip)

        q_card.add_widget(q_row)
        content_box.add_widget(q_card)

        # Card 3: Default Format
        fmt_card = RoundedCard(orientation='vertical', padding=[16, 14, 16, 14], spacing=10, size_hint_y=None, height=110)
        fmt_title = Label(text="Default Format", color=theme.text_primary, font_size='15sp', bold=True, size_hint_y=None, height=22, halign='left', valign='middle')
        fmt_title.bind(size=fmt_title.setter('text_size'))
        theme.bind(text_primary=lambda i, v: setattr(fmt_title, 'color', v))
        fmt_card.add_widget(fmt_title)

        fmt_row = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=40)
        self.fmt_chips = {}
        for f_val in SUPPORTED_OUTPUT_FORMATS:
            chip = ChipButton(text=f_val, is_active=(self.settings_data['default_format'] == f_val), size_hint_x=1)
            chip.bind(on_release=lambda btn, f=f_val: self._set_default_format(f))
            self.fmt_chips[f_val] = chip
            fmt_row.add_widget(chip)

        fmt_card.add_widget(fmt_row)
        content_box.add_widget(fmt_card)

        # Card 4: About Information
        about_card = RoundedCard(orientation='vertical', padding=[16, 16, 16, 16], spacing=8, size_hint_y=None, height=150)
        
        about_title = Label(text="About Image Resizer", color=theme.text_primary, font_size='15sp', bold=True, size_hint_y=None, height=22, halign='left', valign='middle')
        about_title.bind(size=about_title.setter('text_size'))
        theme.bind(text_primary=lambda i, v: setattr(about_title, 'color', v))

        about_text = Label(
            text="[b]Version:[/b] 1.0.0 (Pure Python)\n[b]Engine:[/b] Kivy + Pillow\n[b]Offline First:[/b] Processes 100% locally on device.",
            color=theme.text_secondary,
            font_size='13sp',
            halign='left',
            valign='middle'
        )
        about_text.bind(size=about_text.setter('text_size'))
        about_text.markup = True
        theme.bind(text_secondary=lambda i, v: setattr(about_text, 'color', v))

        about_card.add_widget(about_title)
        about_card.add_widget(about_text)
        content_box.add_widget(about_card)

        scroll.add_widget(content_box)
        root_layout.add_widget(scroll)

        self.add_widget(root_layout)

    def _set_theme(self, mode: str):
        self.settings_data['theme'] = mode
        self.light_chip.is_active = (mode == 'light')
        self.dark_chip.is_active = (mode == 'dark')
        theme.set_mode(mode)
        self._save_settings()

    def _set_default_quality(self, quality: int):
        self.settings_data['default_quality'] = quality
        for q, chip in self.q_chips.items():
            chip.is_active = (q == quality)
        self._save_settings()

    def _set_default_format(self, fmt: str):
        self.settings_data['default_format'] = fmt
        for f, chip in self.fmt_chips.items():
            chip.is_active = (f == fmt)
        self._save_settings()

    def _go_back(self):
        self.manager.current = 'home'
