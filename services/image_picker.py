"""
Android Image Picker with Native SAF / Intent and Desktop Fallback.
"""
import os
import sys
from kivy.utils import platform

class ImagePicker:
    """
    Manages image selection across Android and desktop development environments.
    """

    @staticmethod
    def open_picker(on_image_selected_callback):
        """
        Launches Android Intent picker if on device, or Kivy/Plyer file dialog on desktop.
        """
        if platform == 'android':
            try:
                from jnius import autoclass, cast
                from android.activity import bind as android_bind

                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                
                # Setup photo/image picker intent
                intent = Intent(Intent.ACTION_GET_CONTENT)
                intent.setType("image/*")
                intent.addCategory(Intent.CATEGORY_OPENABLE)

                def on_activity_result(request_code, result_code, intent_data):
                    if request_code == 1001 and result_code == -1 and intent_data is not None: # RESULT_OK == -1
                        uri = intent_data.getData()
                        if uri is not None:
                            # Resolve path or copy to cache
                            resolved_path = ImagePicker._resolve_android_uri(uri)
                            if resolved_path:
                                on_image_selected_callback(resolved_path)

                android_bind(on_new_intent=on_activity_result)
                currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                currentActivity.startActivityForResult(intent, 1001)
                return
            except Exception as e:
                print(f"[ImagePicker] Android native intent failed: {e}")

        # Fallback for testing / desktop environments
        ImagePicker._open_filechooser_fallback(on_image_selected_callback)

    @staticmethod
    def _resolve_android_uri(uri) -> str:
        """Copies URI stream to a cache file so Pillow can process it cleanly."""
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            content_resolver = context.getContentResolver()
            
            input_stream = content_resolver.openInputStream(uri)
            cache_dir = context.getCacheDir().getAbsolutePath()
            out_file_path = os.path.join(cache_dir, "selected_input_image.jpg")
            
            FileOutputStream = autoclass('java.io.FileOutputStream')
            output_stream = FileOutputStream(out_file_path)
            
            # Read buffer
            buffer = bytearray(4096)
            while True:
                bytes_read = input_stream.read(buffer)
                if bytes_read <= 0:
                    break
                output_stream.write(buffer, 0, bytes_read)
                
            input_stream.close()
            output_stream.close()
            return out_file_path
        except Exception as e:
            print(f"[ImagePicker] Failed to resolve Android URI: {e}")
            return None

    @staticmethod
    def _open_filechooser_fallback(callback):
        """Kivy fallback file picker modal for desktop testing."""
        from kivy.uix.modalview import ModalView
        from kivy.uix.filechooser import FileChooserListView
        from kivy.uix.boxlayout import BoxLayout
        from components.cards import RoundedCard
        from components.buttons import PrimaryButton, SecondaryButton
        from utils.theme import theme

        view = ModalView(size_hint=(0.9, 0.85), auto_dismiss=True)
        card = RoundedCard(orientation='vertical', padding=[12, 12, 12, 12], spacing=8)
        
        chooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.jpg', '*.jpeg', '*.png', '*.webp', '*.JPG', '*.PNG', '*.WEBP'],
            size_hint=(1, 1)
        )
        card.add_widget(chooser)

        btn_row = BoxLayout(size_hint_y=None, height=44, spacing=10)
        cancel_btn = SecondaryButton(text="Cancel")
        select_btn = PrimaryButton(text="Select Image")

        def on_select(*args):
            if chooser.selection:
                selected = chooser.selection[0]
                view.dismiss()
                callback(selected)

        cancel_btn.bind(on_release=lambda *a: view.dismiss())
        select_btn.bind(on_release=on_select)
        
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(select_btn)
        card.add_widget(btn_row)

        view.add_widget(card)
        view.open()
