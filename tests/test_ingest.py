import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from PIL import Image

# Add src to the module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ingest_images import add_timestamp, run

class TestImageIngestion(unittest.TestCase):

    def setUp(self):
        """Set up temporary test directory and dummy image."""
        self.test_dir = "./test_output"
        os.makedirs(self.test_dir, exist_ok=True)
        self.dummy_image_path = os.path.join(self.test_dir, "test_site.jpg")
        
        # Create a simple 200x200 red image for testing
        img = Image.new("RGB", (200, 200), color="red")
        img.save(self.dummy_image_path)

    def tearDown(self):
        """Clean up temporary test files."""
        if os.path.exists(self.dummy_image_path):
            os.remove(self.dummy_image_path)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_add_timestamp_success(self):
        """Verify that add_timestamp executes on an image file without throwing exceptions."""
        timestamp_str = "2026-09-01 12:00:00"
        try:
            add_timestamp(self.dummy_image_path, timestamp_str)
        except Exception as e:
            self.fail(f"add_timestamp raised an unexpected exception: {e}")
            
        # Verify image remains valid and readable
        with Image.open(self.dummy_image_path) as img:
            self.assertIsNotNone(img)

    @patch.dict(os.environ, {}, clear=True)
    def test_run_missing_bearer_token(self):
        """Verify that run() exits safely when HYDRO_VIEW_BEARER_TOKEN is missing."""
        with self.assertRaises(SystemExit) as cm:
            run()
        self.assertEqual(cm.exception.code, 1)

    @patch("ingest_images.get_resilient_session")
    @patch.dict(os.environ, {"HYDRO_VIEW_BEARER_TOKEN": "mock_token"})
    def test_run_successful_api_flow(self, mock_get_session):
        """Mock network responses to verify API parsing flow."""
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        # Mock query_images response
        mock_api_resp = MagicMock()
        mock_api_resp.status_code = 200
        mock_api_resp.json.return_value = {
            "sites": [
                {
                    "site_id": "vBmHRDhnfnAxN54wonpWzrKEoP4tVpnB5xb6stjz4G4",
                    "blob_id": "mock_blob_123"
                }
            ]
        }

        # Mock image download response (1x1 red PNG blob)
        mock_img_resp = MagicMock()
        mock_img_resp.status_code = 200
        mock_img_resp.content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82'

        mock_session.get.side_effect = [mock_api_resp, mock_img_resp]

        # Run ingestion logic pointing to local test directory
        with patch.dict(os.environ, {"OUTPUT_IMAGE_FOLDER": self.test_dir}):
            run()

        expected_file = os.path.join(self.test_dir, "Site_02_30163.jpg")
        self.assertTrue(os.path.exists(expected_file))

if __name__ == "__main__":
    unittest.main()
