"""
Storage and File Management Service.
Handles saving images with collision avoidance (_resized.jpg, _resized_1.jpg) and Android media scanning.
"""
import os
import shutil
from kivy.utils import platform

class StorageService:
    """
    Handles saving files with automatic deduplication and Android MediaStore notification.
    """

    @staticmethod
    def get_output_directory() -> str:
        """Returns the appropriate output folder (Pictures/ImageResizer on Android or ~/Pictures on desktop)."""
        if platform == 'android':
            try:
                from jnius import autoclass
                Environment = autoclass('android.os.Environment')
                pictures_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES).getAbsolutePath()
                app_dir = os.path.join(pictures_dir, "ImageResizer")
                os.makedirs(app_dir, exist_ok=True)
                return app_dir
            except Exception as e:
                print(f"[StorageService] Error getting Android Pictures dir: {e}")

        # Desktop / Fallback
        home_dir = os.path.expanduser('~')
        pictures_dir = os.path.join(home_dir, "Pictures", "ImageResizer")
        os.makedirs(pictures_dir, exist_ok=True)
        return pictures_dir

    @staticmethod
    def save_resized_image(temp_image_path: str, original_file_name: str, target_format: str) -> str:
        """
        Copies the temporary processed image into the public output folder with a unique name.
        Example: photo_resized.jpg, photo_resized_1.jpg
        """
        output_dir = StorageService.get_output_directory()
        base_name, _ = os.path.splitext(original_file_name)
        ext = target_format.lower()
        if ext == 'jpeg':
            ext = 'jpg'

        # Generate unique non-colliding file name
        candidate_name = f"{base_name}_resized.{ext}"
        candidate_path = os.path.join(output_dir, candidate_name)
        counter = 1

        while os.path.exists(candidate_path):
            candidate_name = f"{base_name}_resized_{counter}.{ext}"
            candidate_path = os.path.join(output_dir, candidate_name)
            counter += 1

        shutil.copy2(temp_image_path, candidate_path)

        # Trigger Android Media Scanner so the image shows immediately in Gallery/Google Photos
        StorageService._trigger_media_scan(candidate_path)

        return candidate_path

    @staticmethod
    def _trigger_media_scan(file_path: str):
        """Scans the saved file in Android MediaStore."""
        if platform == 'android':
            try:
                from jnius import autoclass
                MediaScannerConnection = autoclass('android.media.MediaScannerConnection')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                MediaScannerConnection.scanFile(
                    PythonActivity.mActivity,
                    [file_path],
                    None,
                    None
                )
            except Exception as e:
                print(f"[StorageService] Media scan notification error: {e}")
