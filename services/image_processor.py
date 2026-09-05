"""
Dedicated Python Image Processing Engine using Pillow.
Handles EXIF orientation, Lanczos resizing, alpha blending, format conversion, and compression.
"""
import os
import tempfile
from PIL import Image, ImageOps

class ImageProcessor:
    """
    Thread-safe image processing engine for resizing, compression, and format conversion.
    """

    @staticmethod
    def get_image_info(image_path: str) -> dict:
        """
        Inspects an image file and extracts dimensions, format, and file size.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")

        file_size = os.path.getsize(image_path)
        with Image.open(image_path) as img:
            # Check for EXIF orientation transpose if present
            try:
                img = ImageOps.exif_transpose(img) or img
            except Exception:
                pass

            width, height = img.size
            img_format = (img.format or os.path.splitext(image_path)[1].replace('.', '')).upper()
            if img_format == 'JPEG':
                img_format = 'JPG'

            has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)

            return {
                "path": image_path,
                "file_name": os.path.basename(image_path),
                "width": width,
                "height": height,
                "format": img_format,
                "file_size": file_size,
                "has_alpha": has_alpha
            }

    @staticmethod
    def process_image(
        input_path: str,
        target_width: int,
        target_height: int,
        output_format: str = 'JPG',
        quality: int = 90
    ) -> dict:
        """
        Resizes and compresses the source image into an optimized temporary result file.
        Returns a dict with path, dimensions, format, and file size.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input image not found: {input_path}")

        if target_width <= 0 or target_height <= 0:
            raise ValueError("Target dimensions must be positive integers.")

        output_format = output_format.upper()
        if output_format not in ('JPG', 'PNG', 'WEBP'):
            output_format = 'JPG'

        with Image.open(input_path) as img:
            # 1. Apply EXIF orientation
            try:
                img = ImageOps.exif_transpose(img) or img
            except Exception:
                pass

            # 2. High-quality resampling using Lanczos
            resized_img = img.resize((int(target_width), int(target_height)), Image.Resampling.LANCZOS)

            # 3. Handle Color Modes and Alpha Channels
            if output_format == 'JPG':
                # JPG does not support alpha channel: blend on a crisp white background
                if resized_img.mode in ('RGBA', 'LA') or (resized_img.mode == 'P' and 'transparency' in resized_img.info):
                    rgba = resized_img.convert('RGBA')
                    background = Image.new('RGB', rgba.size, (255, 255, 255))
                    background.paste(rgba, mask=rgba.split()[3]) # Use alpha as mask
                    final_img = background
                elif resized_img.mode != 'RGB':
                    final_img = resized_img.convert('RGB')
                else:
                    final_img = resized_img
            elif output_format == 'PNG':
                if resized_img.mode not in ('RGB', 'RGBA', 'L', 'LA'):
                    final_img = resized_img.convert('RGBA')
                else:
                    final_img = resized_img
            elif output_format == 'WEBP':
                if resized_img.mode not in ('RGB', 'RGBA'):
                    final_img = resized_img.convert('RGBA')
                else:
                    final_img = resized_img

            # 4. Save to temporary working file
            ext = output_format.lower()
            if ext == 'jpg':
                ext = 'jpg'
            
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"resizer_output_{os.getpid()}_{target_width}x{target_height}.{ext}")

            save_kwargs = {}
            if output_format == 'JPG':
                save_kwargs['quality'] = max(10, min(100, quality))
                save_kwargs['optimize'] = True
                final_img.save(temp_file, format='JPEG', **save_kwargs)
            elif output_format == 'WEBP':
                save_kwargs['quality'] = max(10, min(100, quality))
                save_kwargs['method'] = 4
                final_img.save(temp_file, format='WEBP', **save_kwargs)
            elif output_format == 'PNG':
                save_kwargs['optimize'] = True
                save_kwargs['compress_level'] = 9
                final_img.save(temp_file, format='PNG', **save_kwargs)

            res_size = os.path.getsize(temp_file)

            return {
                "path": temp_file,
                "file_name": os.path.basename(temp_file),
                "width": target_width,
                "height": target_height,
                "format": output_format,
                "file_size": res_size,
                "quality": quality
            }
