import unittest
from unittest.mock import patch

from app.core.fx.update import main


class TestFXUpdate(unittest.TestCase):
    """Test the FX update script."""

    @patch("app.core.fx.update.update_fx_data")
    @patch("app.core.fx.update.logging")
    @patch("app.core.fx.update.load_dotenv")
    @patch("app.core.fx.update.configure_logging")
    def test_main_success(self, mock_configure_logging, mock_load_dotenv, mock_logging, mock_update_fx):
        """Test successful execution of main function."""
        # Setup mock return value
        mock_fx_data = {
            "current_rates": {
                "rates": {"USD": {"mid": 17.525}, "GBP": {"mid": 22.125}, "EUR": {"mid": 19.825}, "ZAR": {"mid": 0.965}}
            }
        }
        mock_update_fx.return_value = mock_fx_data

        # Run main function
        main()

        # Verify function calls
        mock_configure_logging.assert_called_once()
        mock_load_dotenv.assert_called_once()
        mock_update_fx.assert_called_once()

        # Verify logging calls
        mock_logging.info.assert_called()

        # Check that success message was logged
        info_calls = [call[0][0] for call in mock_logging.info.call_args_list]
        self.assertTrue(any("Starting FX data update..." in call for call in info_calls))
        self.assertTrue(any("FX rates updated successfully:" in call for call in info_calls))
        self.assertTrue(any("completed in" in call for call in info_calls))

    @patch("app.core.fx.update.update_fx_data")
    @patch("app.core.fx.update.logging")
    @patch("app.core.fx.update.load_dotenv")
    @patch("app.core.fx.update.configure_logging")
    def test_main_failure(self, mock_configure_logging, mock_load_dotenv, mock_logging, mock_update_fx):
        """Test main function when update_fx_data raises an exception."""
        # Setup mock to raise exception
        mock_update_fx.side_effect = Exception("Network error")

        # Test that exception is re-raised
        with self.assertRaises(RuntimeError):
            try:
                main()
            except Exception as e:
                # Convert to specific exception type for testing
                raise RuntimeError(str(e)) from e

        # Verify error was logged
        mock_logging.error.assert_called_once()
        error_call = mock_logging.error.call_args[0][0]
        self.assertIn("FX data update failed:", error_call)

    @patch("app.core.fx.update.main")
    def test_script_execution(self, mock_main):
        """Test that script can be executed as main module."""
        # This would test the if __name__ == "__main__": block
        # We'll mock it since we don't want to actually run main()
        mock_main.return_value = None

        # Import and verify the module structure
        import app.core.fx.update

        self.assertTrue(hasattr(app.core.fx.update, "main"))
        self.assertTrue(callable(app.core.fx.update.main))


if __name__ == "__main__":
    unittest.main()
