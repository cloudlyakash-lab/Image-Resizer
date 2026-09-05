"""
Image Resizer - Pure Python Android Application
Main entry point and lifecycle manager.
"""
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.utils import platform

from screens.home import HomeScreen
from screens.resize import ResizeScreen
from screens.result import ResultScreen
from screens.settings import SettingsScreen
from utils.theme import theme

class ImageResizerApp(App):
    """
    Main Kivy Application lifecycle manager for Image Resizer.
    """

    def build(self):
        self.title = "Image Resizer"

        # Enable softinput resizing on mobile devices
        Window.softinput_mode = 'below_target'

        # Listen for Android hardware back button (keycode 27)
        Window.bind(on_keyboard=self._on_keyboard_back)

        # Initialize screen manager with smooth sliding transitions
        self.sm = ScreenManager(transition=SlideTransition(duration=0.25))

        # Register application screens
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(ResizeScreen(name='resize'))
        self.sm.add_widget(ResultScreen(name='result'))
        self.sm.add_widget(SettingsScreen(name='settings'))

        # Set initial screen
        self.sm.current = 'home'

        return self.sm

    def _on_keyboard_back(self, window, key, scancode, codepoint, modifier):
        """Handles Android hardware back button navigation."""
        if key == 27:  # Android back keycode
            if self.sm.current in ('resize', 'settings'):
                self.sm.current = 'home'
                return True
            elif self.sm.current == 'result':
                self.sm.current = 'resize'
                return True
        return False

    def on_start(self):
        """Lifecycle hook when application launches."""
        # Request Android permissions dynamically if running on Android
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE
                ])
            except Exception as e:
                print(f"[App] Android permission request error: {e}")

if __name__ == '__main__':
    ImageResizerApp().run()
