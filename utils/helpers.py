"""
Helper utilities for format formatting, file size calculations, and data parsing.
"""
import os

def format_file_size(bytes_size: int) -> str:
    """Format bytes into readable string (e.g. 2.4 MB, 850 KB)."""
    if bytes_size <= 0:
        return "0 B"
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(bytes_size)
    unit_index = 0
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    if unit_index == 0:
        return f"{int(size)} B"
    return f"{size:.1f} {units[unit_index]}"

def get_file_name_from_path(path: str) -> str:
    """Extract file name from absolute path."""
    if not path:
        return ""
    return os.path.basename(path)

def clamp(val, min_val, max_val):
    """Clamp a value between min and max."""
    return max(min_val, min(val, max_val))
