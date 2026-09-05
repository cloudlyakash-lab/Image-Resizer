"""
Resize Screen: Interactive controls for dimensions, aspect ratio, percentages, quality, and format.
"""
import threading
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

from components.cards import RoundedCard
from components.buttons import PrimaryButton, SecondaryButton, ChipButton
from components.inputs import RoundedTextInput, LabeledInputField
from components.dialogs import LoadingDialog, AlertDialog, PresetsDialog
from services.image_processor import ImageProcessor
from utils.constants import PERCENTAGE_PRESETS, SUPPORTED_OUTPUT_FORMATS, DEFAULT_QUALITY, DEFAULT_FORMAT
from utils.helpers import format_file_size
from utils.theme import theme

class ResizeScreen(Screen):
    """
    Main editor screen for configuring resizing dimensions, quality compression, and formats.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_info = None
        self.orig_width = 1920
        self.orig_height = 1080
        self.aspect_locked = True
        self.is_updating_programmatically = False
        self.selected_format = DEFAULT_FORMAT
        self.selected_quality = DEFAULT_QUALITY

        with self.canvas.before:
            self._bg_color_instr = Color(*theme.background)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        theme.bind(background=lambda i, v: setattr(self._bg_color_instr, 'rgba', v))

        self._build_ui()

    def _update_canvas(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def set_image_data(self, image_info: dict):
        """Called by HomeScreen when transitioning to pass selected image metadata."""
        self.image_info = image_info
        self.orig_width = image_info['width']
        self.orig_height = image_info['height']

        self.preview_image.source = image_info['path']
        self.preview_image.reload()

        self.orig_size_label.text = f"Original: {self.orig_width} × {self.orig_height} px  ({format_file_size(image_info['file_size'])})"

        # Initialize dimension inputs
        self.is_updating_programmatically = True
        self.width_input.text = str(self.orig_width)
        self.height_input.text = str(self.orig_height)
        self.is_updating_programmatically = False

        # Reset percentage chips to 100%
        self._set_percentage_active(100)

    def _build_ui(self):
        root_layout = BoxLayout(orientation='vertical', padding=[16, 12, 16, 12], spacing=12)

        # 1. Header Bar
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=44, spacing=10)
        
        back_btn = SecondaryButton(text="← Back", size_hint=(None, None), size=(80, 40), font_size='13sp')
        back_btn.bind(on_release=lambda *a: self._go_back())
        
        title_lbl = Label(
            text="Resize Settings",
            color=theme.text_primary,
            font_size='18sp',
            bold=True,
            halign='center',
            valign='middle'
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))
        theme.bind(text_primary=lambda i, v: setattr(title_lbl, 'color', v))

        presets_btn = SecondaryButton(text="⚡ Presets", size_hint=(None, None), size=(90, 40), font_size='13sp')
        presets_btn.bind(on_release=lambda *a: self._open_presets_dialog())

        top_bar.add_widget(back_btn)
        top_bar.add_widget(title_lbl)
        top_bar.add_widget(presets_btn)
        root_layout.add_widget(top_bar)

        # 2. Scrollable Body
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        content_box = BoxLayout(orientation='vertical', spacing=14, size_hint_y=None)
        content_box.bind(minimum_height=content_box.setter('height'))

        # Card 1: Image Preview & Original Size
        preview_card = RoundedCard(orientation='vertical', padding=[12, 12, 12, 12], spacing=8, size_hint_y=None, height=210)
        self.preview_image = KivyImage(size_hint_y=None, height=150, allow_stretch=True, keep_ratio=True)
        self.orig_size_label = Label(
            text="Original: 1920 × 1080 px",
            color=theme.text_secondary,
            font_size='13sp',
            bold=True,
            size_hint_y=None,
            height=20,
            halign='center',
            valign='middle'
        )
        self.orig_size_label.bind(size=self.orig_size_label.setter('text_size'))
        theme.bind(text_secondary=lambda i, v: setattr(self.orig_size_label, 'color', v))

        preview_card.add_widget(self.preview_image)
        preview_card.add_widget(self.orig_size_label)
        content_box.add_widget(preview_card)

        # Card 2: Dimensions & Aspect Ratio
        dim_card = RoundedCard(orientation='vertical', padding=[16, 14, 16, 14], spacing=10, size_hint_y=None, height=150)
        
        dim_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=26)
        dim_title = Label(text="Custom Dimensions (px)", color=theme.text_primary, font_size='15sp', bold=True, halign='left', valign='middle')
        dim_title.bind(size=dim_title.setter('text_size'))
        theme.bind(text_primary=lambda i, v: setattr(dim_title, 'color', v))

        self.aspect_btn = SecondaryButton(
            text="🔒 Locked",
            size_hint=(None, None),
            size=(96, 28),
            font_size='12sp'
        )
        self.aspect_btn.bind(on_release=self._toggle_aspect_ratio)

        dim_header.add_widget(dim_title)
        dim_header.add_widget(self.aspect_btn)
        dim_card.add_widget(dim_header)

        # Inputs Row
        inputs_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=64)
        
        # Width Box
        w_box = BoxLayout(orientation='vertical', spacing=4)
        w_lbl = Label(text="Width", color=theme.text_secondary, font_size='12sp', size_hint_y=None, height=16, halign='left', valign='middle')
        w_lbl.bind(size=w_lbl.setter('text_size'))
        self.width_input = RoundedTextInput(hint_text="Width", input_filter='int', height=44)
        self.width_input.bind(text=self._on_width_changed)
        w_box.add_widget(w_lbl)
        w_box.add_widget(self.width_input)

        # Height Box
        h_box = BoxLayout(orientation='vertical', spacing=4)
        h_lbl = Label(text="Height", color=theme.text_secondary, font_size='12sp', size_hint_y=None, height=16, halign='left', valign='middle')
        h_lbl.bind(size=h_lbl.setter('text_size'))
        self.height_input = RoundedTextInput(hint_text="Height", input_filter='int', height=44)
        self.height_input.bind(text=self._on_height_changed)
        h_box.add_widget(h_lbl)
        h_box.add_widget(self.height_input)

        inputs_row.add_widget(w_box)
        inputs_row.add_widget(h_box)
        dim_card.add_widget(inputs_row)

        content_box.add_widget(dim_card)

        # Card 3: Percentage Scale Presets
        scale_card = RoundedCard(orientation='vertical', padding=[16, 14, 16, 14], spacing=10, size_hint_y=None, height=110)
        
        scale_title = Label(text="Scale by Percentage", color=theme.text_primary, font_size='15sp', bold=True, size_hint_y=None, height=22, halign='left', valign='middle')
        scale_title.bind(size=scale_title.setter('text_size'))
        theme.bind(text_primary=lambda i, v: setattr(scale_title, 'color', v))
        scale_card.add_widget(scale_title)

        chips_box = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=40)
        self.percentage_chips = {}
        for pct in PERCENTAGE_PRESETS:
            chip = ChipButton(text=f"{pct}%", is_active=(pct == 100), size_hint_x=1)
            chip.bind(on_release=lambda btn, p=pct: self._apply_percentage(p))
            self.percentage_chips[pct] = chip
            chips_box.add_widget(chip)

        scale_card.add_widget(chips_box)
        content_box.add_widget(scale_card)

        # Card 4: Quality Compression Control
        quality_card = RoundedCard(orientation='vertical', padding=[16, 14, 16, 14], spacing=10, size_hint_y=None, height=130)
        
        q_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=24)
        q_title = Label(text="Image Quality", color=theme.text_primary, font_size='15sp', bold=True, halign='left', valign='middle')
        q_title.bind(size=q_title.setter('text_size'))
        theme.bind(text_primary=lambda i, v: setattr(q_title, 'color', v))

        self.quality_val_lbl = Label(
            text=f"{DEFAULT_QUALITY}%",
            color=theme.primary,
            font_size='15sp',
            bold=True,
            size_hint_x=None,
            width=50,
            halign='right',
            valign='middle'
        )
        self.quality_val_lbl.bind(size=self.quality_val_lbl.setter('text_size'))
        theme.bind(primary=lambda i, v: setattr(self.quality_val_lbl, 'color', v))

        q_header.add_widget(q_title)
        q_header.add_widget(self.quality_val_lbl)
        quality_card.add_widget(q_header)

        self.quality_slider = Slider(min=10, max=100, value=DEFAULT_QUALITY, step=1, size_hint_y=None, height=36)
        self.quality_slider.bind(value=self._on_quality_slider_change)
        quality_card.add_widget(self.quality_slider)

        self.q_hint_lbl = Label(
            text="Higher quality preserves fine detail; lower quality creates smaller files.",
            color=theme.text_secondary,
            font_size='11sp',
            size_hint_y=None,
            height=16,
            halign='left',
            valign='middle'
        )
        self.q_hint_lbl.bind(size=self.q_hint_lbl.setter('text_size'))
        theme.bind(text_secondary=lambda i, v: setattr(self.q_hint_lbl, 'color', v))
        quality_card.add_widget(self.q_hint_lbl)

        content_box.add_widget(quality_card)

        # Card 5: Output Format
        format_card = RoundedCard(orientation='vertical', padding=[16, 14, 16, 14], spacing=10, size_hint_y=None, height=105)
        
        fmt_title = Label(text="Output Format", color=theme.text_primary, font_size='15sp', bold=True, size_hint_y=None, height=22, halign='left', valign='middle')
        fmt_title.bind(size=fmt_title.setter('text_size'))
        theme.bind(text_primary=lambda i, v: setattr(fmt_title, 'color', v))
        format_card.add_widget(fmt_title)

        fmt_row = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        self.format_chips = {}
        for fmt in SUPPORTED_OUTPUT_FORMATS:
            chip = ChipButton(text=fmt, is_active=(fmt == DEFAULT_FORMAT), size_hint_x=1)
            chip.bind(on_release=lambda btn, f=fmt: self._select_format(f))
            self.format_chips[fmt] = chip
            fmt_row.add_widget(chip)

        format_card.add_widget(fmt_row)
        content_box.add_widget(format_card)

        scroll.add_widget(content_box)
        root_layout.add_widget(scroll)

        # 3. Bottom Sticky Action Button
        action_btn = PrimaryButton(text="⚡ RESIZE IMAGE", height=52)
        action_btn.bind(on_release=lambda *a: self._start_resizing())
        root_layout.add_widget(action_btn)

        self.add_widget(root_layout)

    # --- Dimension & Aspect Ratio Calculations ---
    def _toggle_aspect_ratio(self, *args):
        self.aspect_locked = not self.aspect_locked
        if self.aspect_locked:
            self.aspect_btn.text = "🔒 Locked"
            # Re-lock: synchronize height to current width
            try:
                curr_w = int(self.width_input.text or self.orig_width)
                calc_h = max(1, round(self.orig_height * (curr_w / self.orig_width)))
                self.is_updating_programmatically = True
                self.height_input.text = str(calc_h)
                self.is_updating_programmatically = False
            except Exception:
                pass
        else:
            self.aspect_btn.text = "🔓 Unlocked"

    def _on_width_changed(self, instance, value):
        if self.is_updating_programmatically or not self.aspect_locked:
            return
        if not value or not value.isdigit() or int(value) <= 0:
            return
        try:
            w = int(value)
            # new_height = original_height * (new_width / original_width)
            h = max(1, round(self.orig_height * (w / self.orig_width)))
            self.is_updating_programmatically = True
            self.height_input.text = str(h)
            self.is_updating_programmatically = False
            self._clear_percentage_active()
        except Exception:
            pass

    def _on_height_changed(self, instance, value):
        if self.is_updating_programmatically or not self.aspect_locked:
            return
        if not value or not value.isdigit() or int(value) <= 0:
            return
        try:
            h = int(value)
            # new_width = original_width * (new_height / original_height)
            w = max(1, round(self.orig_width * (h / self.orig_height)))
            self.is_updating_programmatically = True
            self.width_input.text = str(w)
            self.is_updating_programmatically = False
            self._clear_percentage_active()
        except Exception:
            pass

    def _apply_percentage(self, percentage: int):
        self._set_percentage_active(percentage)
        self.is_updating_programmatically = True
        new_w = max(1, round(self.orig_width * (percentage / 100.0)))
        new_h = max(1, round(self.orig_height * (percentage / 100.0)))
        self.width_input.text = str(new_w)
        self.height_input.text = str(new_h)
        self.is_updating_programmatically = False

    def _set_percentage_active(self, active_pct: int):
        for pct, chip in self.percentage_chips.items():
            chip.is_active = (pct == active_pct)

    def _clear_percentage_active(self):
        for chip in self.percentage_chips.values():
            chip.is_active = False

    # --- Quality & Formats ---
    def _on_quality_slider_change(self, instance, value):
        self.selected_quality = int(value)
        self.quality_val_lbl.text = f"{self.selected_quality}%"

    def _select_format(self, fmt: str):
        self.selected_format = fmt
        for f_name, chip in self.format_chips.items():
            chip.is_active = (f_name == fmt)
        if fmt == 'PNG':
            self.q_hint_lbl.text = "PNG uses lossless compression (quality slider adjusts compression effort)."
        else:
            self.q_hint_lbl.text = "Higher quality preserves fine detail; lower quality creates smaller files."

    def _open_presets_dialog(self):
        dialog = PresetsDialog(on_select_preset=self._apply_social_preset)
        dialog.open()

    def _apply_social_preset(self, preset: dict):
        self.is_updating_programmatically = True
        self.width_input.text = str(preset['width'])
        self.height_input.text = str(preset['height'])
        self.is_updating_programmatically = False
        self._clear_percentage_active()

    # --- Execution & Background Threading ---
    def _start_resizing(self):
        # Validate inputs
        w_str = self.width_input.text.strip()
        h_str = self.height_input.text.strip()

        if not w_str.isdigit() or int(w_str) <= 0:
            dialog = AlertDialog(title="Invalid Width", message="Please enter a positive numeric width.", is_error=True)
            dialog.open()
            return

        if not h_str.isdigit() or int(h_str) <= 0:
            dialog = AlertDialog(title="Invalid Height", message="Please enter a positive numeric height.", is_error=True)
            dialog.open()
            return

        target_w = int(w_str)
        target_h = int(h_str)

        # Show non-blocking loading spinner
        self.loading_dialog = LoadingDialog(message="Resizing image...")
        self.loading_dialog.open()

        # Execute in background thread to avoid freezing UI
        threading.Thread(
            target=self._run_image_processing_thread,
            args=(self.image_info['path'], target_w, target_h, self.selected_format, self.selected_quality),
            daemon=True
        ).start()

    def _run_image_processing_thread(self, path, w, h, fmt, quality):
        try:
            result = ImageProcessor.process_image(
                input_path=path,
                target_width=w,
                target_height=h,
                output_format=fmt,
                quality=quality
            )
            # Dispatch back to UI thread
            Clock.schedule_once(lambda dt: self._on_processing_success(result), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_processing_error(str(e)), 0)

    def _on_processing_success(self, result_dict: dict):
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.dismiss()

        result_screen = self.manager.get_screen('result')
        result_screen.set_results(
            original_info=self.image_info,
            resized_info=result_dict
        )
        self.manager.current = 'result'

    def _on_processing_error(self, error_message: str):
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.dismiss()

        dialog = AlertDialog(
            title="Processing Failed",
            message=f"Could not resize the image.\n{error_message}",
            is_error=True
        )
        dialog.open()

    def _go_back(self):
        self.manager.current = 'home'
