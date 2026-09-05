"""
Result Screen: Displays before/after comparison, saved path status, and save/share triggers.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.graphics import Color, Rectangle

from components.cards import RoundedCard
from components.buttons import PrimaryButton, SecondaryButton
from components.dialogs import AlertDialog
from services.storage import StorageService
from services.sharing import SharingService
from utils.helpers import format_file_size
from utils.theme import theme

class ResultScreen(Screen):
    """
    Displays the resized image result, metadata comparison, and export actions.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_info = None
        self.resized_info = None
        self.saved_output_path = None

        with self.canvas.before:
            self._bg_color_instr = Color(*theme.background)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        theme.bind(background=lambda i, v: setattr(self._bg_color_instr, 'rgba', v))

        self._build_ui()

    def _update_canvas(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def set_results(self, original_info: dict, resized_info: dict):
        """Populates before/after metrics and loads resized preview."""
        self.original_info = original_info
        self.resized_info = resized_info
        self.saved_output_path = None

        self.result_preview.source = resized_info['path']
        self.result_preview.reload()

        # Update stats text
        orig_size_str = format_file_size(original_info['file_size'])
        res_size_str = format_file_size(resized_info['file_size'])

        self.orig_stats_lbl.text = (
            f"[b]Original[/b]\n"
            f"{original_info['width']} × {original_info['height']} px\n"
            f"{orig_size_str} • {original_info['format']}"
        )
        self.orig_stats_lbl.markup = True

        # Calculate reduction percentage
        saved_bytes = original_info['file_size'] - resized_info['file_size']
        if original_info['file_size'] > 0 and saved_bytes > 0:
            reduction_pct = round((saved_bytes / original_info['file_size']) * 100)
            reduction_badge = f" [color=10B981](-{reduction_pct}%)[/color]"
        else:
            reduction_badge = ""

        self.res_stats_lbl.text = (
            f"[b]Resized Result[/b]\n"
            f"{resized_info['width']} × {resized_info['height']} px\n"
            f"{res_size_str}{reduction_badge} • {resized_info['format']}"
        )
        self.res_stats_lbl.markup = True

    def _build_ui(self):
        root_layout = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=12)

        # 1. Top Header
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
        title_lbl = Label(
            text="✨ Resize Complete",
            color=theme.success,
            font_size='20sp',
            bold=True,
            halign='center',
            valign='middle'
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))
        theme.bind(success=lambda i, v: setattr(title_lbl, 'color', v))
        top_bar.add_widget(title_lbl)
        root_layout.add_widget(top_bar)

        # 2. Scrollable Body
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content_box = BoxLayout(orientation='vertical', spacing=14, size_hint_y=None)
        content_box.bind(minimum_height=content_box.setter('height'))

        # Large Resized Preview Card
        preview_card = RoundedCard(orientation='vertical', padding=[12, 12, 12, 12], spacing=8, size_hint_y=None, height=240)
        self.result_preview = KivyImage(size_hint_y=None, height=216, allow_stretch=True, keep_ratio=True)
        preview_card.add_widget(self.result_preview)
        content_box.add_widget(preview_card)

        # Comparison Card
        comp_card = RoundedCard(orientation='vertical', padding=[16, 16, 16, 16], spacing=12, size_hint_y=None, height=140)
        
        comp_grid = GridLayout(cols=2, spacing=10)
        
        self.orig_stats_lbl = Label(
            text="Original",
            color=theme.text_secondary,
            font_size='13sp',
            halign='left',
            valign='middle'
        )
        self.orig_stats_lbl.bind(size=self.orig_stats_lbl.setter('text_size'))
        theme.bind(text_secondary=lambda i, v: setattr(self.orig_stats_lbl, 'color', v))

        self.res_stats_lbl = Label(
            text="Resized",
            color=theme.text_primary,
            font_size='13sp',
            halign='left',
            valign='middle'
        )
        self.res_stats_lbl.bind(size=self.res_stats_lbl.setter('text_size'))
        theme.bind(text_primary=lambda i, v: setattr(self.res_stats_lbl, 'color', v))

        comp_grid.add_widget(self.orig_stats_lbl)
        comp_grid.add_widget(self.res_stats_lbl)
        comp_card.add_widget(comp_grid)
        content_box.add_widget(comp_card)

        scroll.add_widget(content_box)
        root_layout.add_widget(scroll)

        # 3. Action Buttons
        actions_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=160)

        # Save Button
        save_btn = PrimaryButton(text="💾 Save to Gallery / Pictures", height=48)
        save_btn.bind(on_release=lambda *a: self._save_image())
        actions_box.add_widget(save_btn)

        # Share Button
        share_btn = SecondaryButton(text="↗ Share Image", height=44)
        share_btn.bind(on_release=lambda *a: self._share_image())
        actions_box.add_widget(share_btn)

        # Resize Another Button
        another_btn = SecondaryButton(text="🔄 Resize Another Image", height=44)
        another_btn.bind(on_release=lambda *a: self._resize_another())
        actions_box.add_widget(another_btn)

        root_layout.add_widget(actions_box)
        self.add_widget(root_layout)

    def _save_image(self):
        if not self.resized_info or not self.original_info:
            return

        try:
            saved_path = StorageService.save_resized_image(
                temp_image_path=self.resized_info['path'],
                original_file_name=self.original_info['file_name'],
                target_format=self.resized_info['format']
            )
            self.saved_output_path = saved_path
            
            dialog = AlertDialog(
                title="Image Saved",
                message=f"Successfully saved to:\n{saved_path}"
            )
            dialog.open()
        except Exception as e:
            dialog = AlertDialog(
                title="Save Failed",
                message=f"Could not save image to device storage.\n{str(e)}",
                is_error=True
            )
            dialog.open()

    def _share_image(self):
        target_path = self.saved_output_path or (self.resized_info['path'] if self.resized_info else None)
        if not target_path:
            dialog = AlertDialog(title="Notice", message="No processed image available to share.")
            dialog.open()
            return

        try:
            mime = f"image/{self.resized_info['format'].lower()}"
            SharingService.share_image(target_path, mime_type=mime)
        except Exception as e:
            dialog = AlertDialog(
                title="Share Error",
                message=f"Failed to trigger share dialog.\n{str(e)}",
                is_error=True
            )
            dialog.open()

    def _resize_another(self):
        self.manager.current = 'home'
