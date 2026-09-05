"""
Application constants, presets, and supported formats.
"""

SUPPORTED_INPUT_FORMATS = ('.jpg', '.jpeg', '.png', '.webp')
SUPPORTED_OUTPUT_FORMATS = ['JPG', 'PNG', 'WEBP']

PERCENTAGE_PRESETS = [25, 50, 75, 100, 150, 200]

SOCIAL_PRESETS = [
    {"name": "HD", "width": 1280, "height": 720, "desc": "1280 × 720 px (16:9)"},
    {"name": "Full HD", "width": 1920, "height": 1080, "desc": "1920 × 1080 px (16:9)"},
    {"name": "Instagram Post", "width": 1080, "height": 1080, "desc": "1080 × 1080 px (1:1)"},
    {"name": "Instagram Story", "width": 1080, "height": 1920, "desc": "1080 × 1920 px (9:16)"},
    {"name": "YouTube Thumb", "width": 1280, "height": 720, "desc": "1280 × 720 px (16:9)"},
    {"name": "Twitter / X Post", "width": 1200, "height": 675, "desc": "1200 × 675 px (16:9)"},
]

DEFAULT_QUALITY = 90
DEFAULT_FORMAT = 'JPG'
