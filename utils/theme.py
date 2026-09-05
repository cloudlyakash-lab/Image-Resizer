"""
Centralized Theme Management for Image Resizer.
Provides full color schemes, typography sizes, and active theme dispatching in pure Python.
"""
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.utils import get_color_from_hex

class ThemeManager(EventDispatcher):
    """
    Manages active color schemes and emits change events across all active widgets.
    """
    mode = StringProperty('light') # 'light' or 'dark'

    # Dynamic Theme Colors
    primary = ListProperty([0.15, 0.45, 0.95, 1.0])       # Modern Royal Blue
    primary_variant = ListProperty([0.08, 0.35, 0.85, 1.0])
    secondary = ListProperty([0.0, 0.65, 0.55, 1.0])     # Modern Teal
    background = ListProperty([0.97, 0.98, 1.0, 1.0])    # Crisp light canvas
    surface = ListProperty([1.0, 1.0, 1.0, 1.0])         # Card background
    surface_variant = ListProperty([0.94, 0.95, 0.98, 1.0])
    border = ListProperty([0.88, 0.90, 0.94, 1.0])       # Card borders
    
    text_primary = ListProperty([0.10, 0.12, 0.16, 1.0])  # Near black high contrast
    text_secondary = ListProperty([0.45, 0.50, 0.58, 1.0])# Neutral gray
    text_hint = ListProperty([0.65, 0.70, 0.76, 1.0])
    text_on_primary = ListProperty([1.0, 1.0, 1.0, 1.0])

    success = ListProperty([0.13, 0.70, 0.44, 1.0])      # Emerald green
    error = ListProperty([0.92, 0.25, 0.25, 1.0])        # Modern red
    warning = ListProperty([0.98, 0.65, 0.12, 1.0])      # Amber orange

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_mode('light')

    def set_mode(self, mode_name: str):
        """Toggle between 'light' and 'dark' mode."""
        self.mode = mode_name
        if mode_name == 'dark':
            self.primary = get_color_from_hex('#3B82F6')
            self.primary_variant = get_color_from_hex('#2563EB')
            self.secondary = get_color_from_hex('#10B981')
            self.background = get_color_from_hex('#0F172A')       # Dark Slate
            self.surface = get_color_from_hex('#1E293B')          # Dark Card
            self.surface_variant = get_color_from_hex('#334155')
            self.border = get_color_from_hex('#334155')
            
            self.text_primary = get_color_from_hex('#F8FAFC')
            self.text_secondary = get_color_from_hex('#94A3B8')
            self.text_hint = get_color_from_hex('#64748B')
            self.text_on_primary = [1.0, 1.0, 1.0, 1.0]

            self.success = get_color_from_hex('#10B981')
            self.error = get_color_from_hex('#EF4444')
            self.warning = get_color_from_hex('#F59E0B')
        else:
            self.primary = get_color_from_hex('#2563EB')
            self.primary_variant = get_color_from_hex('#1D4ED8')
            self.secondary = get_color_from_hex('#059669')
            self.background = get_color_from_hex('#F8FAFC')
            self.surface = get_color_from_hex('#FFFFFF')
            self.surface_variant = get_color_from_hex('#F1F5F9')
            self.border = get_color_from_hex('#E2E8F0')
            
            self.text_primary = get_color_from_hex('#0F172A')
            self.text_secondary = get_color_from_hex('#64748B')
            self.text_hint = get_color_from_hex('#94A3B8')
            self.text_on_primary = [1.0, 1.0, 1.0, 1.0]

            self.success = get_color_from_hex('#10B981')
            self.error = get_color_from_hex('#EF4444')
            self.warning = get_color_from_hex('#F59E0B')

# Global theme singleton
theme = ThemeManager()
