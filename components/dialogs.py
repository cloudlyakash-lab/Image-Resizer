"""
Modern Modal Dialogs and Alert Popups in pure Python.
"""
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from components.cards import RoundedCard
from components.buttons import PrimaryButton, SecondaryButton
from utils.constants import SOCIAL_PRESETS
from utils.theme import theme

class LoadingDialog(ModalView):
    """
    Non-cancellable loading indicator modal shown during image processing.
    """
    def __init__(self, message: str = "Resizing...", **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, None)
        self.height = 140
        self.auto_dismiss = False
        self.background_color = [0, 0, 0, 0.4]

        card = RoundedCard(orientation='vertical', padding=[20, 20, 20, 20], spacing=12)
        
        self.title_label = Label(
            text="⚙ " + message,
            color=theme.text_primary,
            font_size='18sp',
            bold=True,
            halign='center',
            valign='middle'
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))

        self.sub_label = Label(
            text="Please wait while your image is being optimized...",
            color=theme.text_secondary,
            font_size='13sp',
            halign='center',
            valign='middle'
        )
        self.sub_label.bind(size=self.sub_label.setter('text_size'))

        card.add_widget(self.title_label)
        card.add_widget(self.sub_label)
        self.add_widget(card)


class AlertDialog(ModalView):
    """
    Generic alert dialog for error and success notifications.
    """
    def __init__(self, title: str, message: str, is_error: bool = False, on_dismiss_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.85, None)
        self.height = 200
        self.auto_dismiss = True
        self.background_color = [0, 0, 0, 0.5]
        self.callback = on_dismiss_callback

        card = RoundedCard(orientation='vertical', padding=[20, 20, 20, 20], spacing=14)

        icon = "❌ " if is_error else "ℹ️ "
        title_color = theme.error if is_error else theme.primary

        title_lbl = Label(
            text=icon + title,
            color=title_color,
            font_size='17sp',
            bold=True,
            size_hint_y=None,
            height=26,
            halign='center',
            valign='middle'
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))

        msg_lbl = Label(
            text=message,
            color=theme.text_primary,
            font_size='14sp',
            halign='center',
            valign='middle'
        )
        msg_lbl.bind(size=msg_lbl.setter('text_size'))

        ok_btn = PrimaryButton(text="OK", height=44)
        ok_btn.bind(on_release=self._on_btn_click)

        card.add_widget(title_lbl)
        card.add_widget(msg_lbl)
        card.add_widget(ok_btn)
        self.add_widget(card)

    def _on_btn_click(self, *args):
        self.dismiss()
        if self.callback:
            self.callback()


class PresetsDialog(ModalView):
    """
    Social Media & Resolution Presets Selection Modal.
    """
    def __init__(self, on_select_preset, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.75)
        self.auto_dismiss = True
        self.background_color = [0, 0, 0, 0.5]
        self.on_select_preset = on_select_preset

        card = RoundedCard(orientation='vertical', padding=[16, 16, 16, 16], spacing=12)

        header = Label(
            text="Quick Presets",
            color=theme.text_primary,
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=32,
            halign='left',
            valign='middle'
        )
        header.bind(size=header.setter('text_size'))
        card.add_widget(header)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        content_box.bind(minimum_height=content_box.setter('height'))

        for preset in SOCIAL_PRESETS:
            item_btn = SecondaryButton(
                text=f"{preset['name']}\n{preset['desc']}",
                height=56,
                font_size='13sp'
            )
            # Capture preset in closure
            item_btn.bind(on_release=lambda btn, p=preset: self._select(p))
            content_box.add_widget(item_btn)

        scroll.add_widget(content_box)
        card.add_widget(scroll)

        close_btn = SecondaryButton(text="Cancel", height=42)
        close_btn.bind(on_release=lambda *a: self.dismiss())
        card.add_widget(close_btn)

        self.add_widget(card)

    def _select(self, preset):
        self.dismiss()
        if self.on_select_preset:
            self.on_select_preset(preset)
