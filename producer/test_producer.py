import unittest
import os
import sys

# Append the directory containing producer.py to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions we want to test
from producer import validate_sync_data, get_carabiner_binary, SYSTEM_OS


class TestProducerLogic(unittest.TestCase):
    def test_validate_sync_data_valid(self):
        """Test valid BPM and beat validation."""
        self.assertTrue(validate_sync_data(120.0, 10.0))
        self.assertTrue(validate_sync_data(85, 0))
        self.assertTrue(validate_sync_data(200.5, 432.1))

    def test_validate_sync_data_invalid(self):
        """Test invalid BPM and beat values."""
        self.assertFalse(validate_sync_data(0, 10.0))
        self.assertFalse(validate_sync_data(-120.0, 10.0))
        self.assertFalse(validate_sync_data("120", 10.0))
        self.assertFalse(validate_sync_data(120.0, "10"))
        self.assertFalse(validate_sync_data(120.0, None))
        self.assertFalse(validate_sync_data(None, 10))

    def test_get_carabiner_binary(self):
        """Test that get_carabiner_binary returns the expected name for the platform."""
        binary = get_carabiner_binary()
        if SYSTEM_OS == "Windows":
            self.assertTrue(binary.endswith("Carabiner.exe"))
        else:
            self.assertTrue(binary.endswith("Carabiner_Linux_x64"))


if __name__ == "__main__":
    unittest.main()
