"""
Home Screen: Welcome header, large upload card, image stats card, and navigation.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle

from components.cards import RoundedCard
from components.buttons import PrimaryButton, SecondaryButton
from components.dialogs import AlertDialog
from services.image_processor import ImageProcessor
from services.image_picker import ImagePicker
from utils.helpers import format_file_size
from utils.theme import theme

class HomeScreen(Screen):
    """
    Landing screen for selecting photos and inspecting their metadata.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_image_info = None

        with self.canvas.before:
            self._bg_color_instr = Color(*theme.background)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        theme.bind(background=self._on_theme_change)

        self._build_ui()

    def _on_theme_change(self, *args):
        self._bg_color_instr.rgba = theme.background

    def _update_canvas(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _build_ui(self):
        root_layout = BoxLayout(orientation='vertical', padding=[16, 16, 16, 16], spacing=16)

        # 1. Top App Bar Header
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=56, spacing=10)

        header_titles = BoxLayout(orientation='vertical', spacing=2)
        app_title = Label(
            text="IMAGE RESIZER",
            color=theme.primary,
            font_size='22sp',
            bold=True,
            halign='left',
            valign='middle'
        )
        app_title.bind(size=app_title.setter('text_size'))
        theme.bind(primary=lambda i, v: setattr(app_title, 'color', v))

        subtitle = Label(
            text="Resize your images quickly and easily",
            color=theme.text_secondary,
            font_size='13sp',
            halign='left',
            valign='middle'
        )
        subtitle.bind(size=subtitle.setter('text_size'))
        theme.bind(text_secondary=lambda i, v: setattr(subtitle, 'color', v))

        header_titles.add_widget(app_title)
        header_titles.add_widget(subtitle)
        top_bar.add_widget(header_titles)

        # Settings icon button
        settings_btn = SecondaryButton(text="⚙", size_hint=(None, None), size=(44, 44), font_size='18sp')
        settings_btn.bind(on_release=lambda *a: self._go_to_settings())
        top_bar.add_widget(settings_btn)

        root_layout.add_widget(top_bar)

        # 2. Scrollable Body
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.body_box = BoxLayout(orientation='vertical', spacing=16, size_hint_y=None)
        self.body_box.bind(minimum_height=self.body_box.setter('height'))

        # Large Upload Card
        self.upload_card = RoundedCard(orientation='vertical', padding=[24, 28, 24, 28], spacing=14, size_hint_y=None, height=220)
        
        icon_lbl = Label(
            text="🖼️",
            font_size='48sp',
            size_hint_y=None,
            height=60,
            halign='center',
            valign='middle'
        )
        icon_lbl.bind(size=icon_lbl.setter('text_size'))

        card_title = Label(
            text="Select Image to Resize",
            color=theme.text_primary,
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=26,
            halign='center',
            valign='middle'
        )
        card_title.bind(size=card_title.setter('text_size'))
        theme.bind(text_primary=lambda i, v: setattr(card_title, 'color', v))

        card_desc = Label(
            text="Supports JPG, JPEG, PNG, and WEBP formats",
            color=theme.text_secondary,
            font_size='13sp',
            size_hint_y=None,
            height=20,
            halign='center',
            valign='middle'
        )
        card_desc.bind(size=card_desc.setter('text_size'))
        theme.bind(text_secondary=lambda i, v: setattr(card_desc, 'color', v))

        select_btn = PrimaryButton(text="Choose from Gallery / Files", height=48)
        select_btn.bind(on_release=lambda *a: self._open_image_picker())

        self.upload_card.add_widget(icon_lbl)
        self.upload_card.add_widget(card_title)
        self.upload_card.add_widget(card_desc)
        self.upload_card.add_widget(select_btn)

        self.body_box.add_widget(self.upload_card)

        # 3. Selected Image Preview & Metadata Card (Initially hidden until image chosen)
        self.stats_card = RoundedCard(orientation='vertical', padding=[16, 16, 16, 16], spacing=12, size_hint_y=None, height=360)
        self.stats_card.opacity = 0
        self.stats_card.disabled = True

        self.thumb_image = KivyImage(size_hint_y=None, height=180, allow_stretch=True, keep_ratio=True)
        self.stats_card.add_widget(self.thumb_image)

        self.info_label = Label(
            text="",
            color=theme.text_primary,
            font_size='14sp',
            halign='center',
            valign='middle'
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        theme.bind(text_primary=lambda i, v: setattr(self.info_label, 'color', v))
        self.stats_card.add_widget(self.info_label)

        # Continue Action Row
        action_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=48)
        
        change_btn = SecondaryButton(text="Change Image", size_hint_x=0.4)
        change_btn.bind(on_release=lambda *a: self._open_image_picker())
        
        continue_btn = PrimaryButton(text="Continue to Resize →", size_hint_x=0.6)
        continue_btn.bind(on_release=lambda *a: self._go_to_resize())

        action_row.add_widget(change_btn)
        action_row.add_widget(continue_btn)
        self.stats_card.add_widget(action_row)

        self.body_box.add_widget(self.stats_card)

        scroll.add_widget(self.body_box)
        root_layout.add_widget(scroll)
        self.add_widget(root_layout)

    def _open_image_picker(self):
        ImagePicker.open_picker(self._on_image_selected)

    def _on_image_selected(self, image_path: str):
        if not image_path:
            return
        try:
            info = ImageProcessor.get_image_info(image_path)
            self.selected_image_info = info

            self.thumb_image.source = image_path
            self.thumb_image.reload()

            self.info_label.text = (
                f"[b]{info['file_name']}[/b]\n"
                f"{info['width']} × {info['height']} px   •   {format_file_size(info['file_size'])}   •   {info['format']}"
            )
            self.info_label.markup = True

            # Reveal stats card and scroll down
            self.stats_card.opacity = 1
            self.stats_card.disabled = False
            self.upload_card.height = 140
        except Exception as e:
            dialog = AlertDialog(
                title="Invalid Image",
                message=f"Unable to inspect the selected image.\n{str(e)}",
                is_error=True
            )
            dialog.open()

    def _go_to_resize(self):
        if not self.selected_image_info:
            dialog = AlertDialog(title="Notice", message="Please select an image first.")
            dialog.open()
            return
        
        resize_screen = self.manager.get_screen('resize')
        resize_screen.set_image_data(self.selected_image_info)
        self.manager.current = 'resize'

    def _go_to_settings(self):
        self.manager.current = 'settings'
