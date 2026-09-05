"""
Unit tests and verification for ImageProcessor and StorageService.
Can be executed with: python3 test_processor.py
"""
import os
import tempfile
import unittest
from PIL import Image

from services.image_processor import ImageProcessor
from services.storage import StorageService
from utils.helpers import format_file_size, clamp

class TestImageProcessor(unittest.TestCase):

    def setUp(self):
        # Create a temporary RGB image for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_img_path = os.path.join(self.temp_dir, "test_input.png")
        
        # 400x200 image with RGBA transparency
        img = Image.new('RGBA', (400, 200), (255, 0, 0, 128))
        img.save(self.test_img_path, format='PNG')

    def tearDown(self):
        if os.path.exists(self.test_img_path):
            os.remove(self.test_img_path)

    def test_get_image_info(self):
        info = ImageProcessor.get_image_info(self.test_img_path)
        self.assertEqual(info['width'], 400)
        self.assertEqual(info['height'], 200)
        self.assertEqual(info['format'], 'PNG')
        self.assertTrue(info['has_alpha'])
        self.assertGreater(info['file_size'], 0)

    def test_resize_aspect_ratio_and_conversion_to_jpg(self):
        # Test converting transparent PNG to JPG at 200x100
        result = ImageProcessor.process_image(
            input_path=self.test_img_path,
            target_width=200,
            target_height=100,
            output_format='JPG',
            quality=85
        )
        self.assertEqual(result['width'], 200)
        self.assertEqual(result['height'], 100)
        self.assertEqual(result['format'], 'JPG')
        self.assertTrue(os.path.exists(result['path']))

        # Inspect resulting file
        with Image.open(result['path']) as res_img:
            self.assertEqual(res_img.size, (200, 100))
            self.assertEqual(res_img.mode, 'RGB')

    def test_resize_to_webp(self):
        result = ImageProcessor.process_image(
            input_path=self.test_img_path,
            target_width=100,
            target_height=50,
            output_format='WEBP',
            quality=90
        )
        self.assertEqual(result['width'], 100)
        self.assertEqual(result['height'], 50)
        self.assertEqual(result['format'], 'WEBP')
        self.assertTrue(os.path.exists(result['path']))

    def test_helpers(self):
        self.assertEqual(format_file_size(500), "500 B")
        self.assertEqual(format_file_size(2048), "2.0 KB")
        self.assertEqual(format_file_size(2500000), "2.4 MB")
        self.assertEqual(clamp(5, 10, 100), 10)
        self.assertEqual(clamp(150, 10, 100), 100)
        self.assertEqual(clamp(50, 10, 100), 50)

if __name__ == '__main__':
    unittest.main()
