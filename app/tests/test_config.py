import unittest
from unittest.mock import patch

from peewee import PostgresqlDatabase

from app.core.db.config import close_database, database, initialize_database


class TestDatabaseConfig(unittest.TestCase):
    @patch("app.core.db.config.database")
    def test_initialize_database(self, mock_db):
        """Test database initialization"""
        initialize_database()

        # Verify database connection was attempted
        mock_db.connect.assert_called_once()

        # Verify tables creation was attempted
        mock_db.create_tables.assert_called_once()

        # Check if the correct tables were passed
        tables_arg = mock_db.create_tables.call_args[0][0]
        self.assertEqual(len(tables_arg), 3)  # Mp3, Episode, Article

    @patch("app.core.db.config.database")
    def test_close_database(self, mock_db):
        """Test database closure"""
        # Setup
        mock_db.is_closed.return_value = False

        # Execute
        close_database()

        # Verify
        mock_db.is_closed.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("app.core.db.config.database")
    def test_close_database_when_already_closed(self, mock_db):
        """Test database closure when already closed"""
        # Setup
        mock_db.is_closed.return_value = True

        # Execute
        close_database()

        # Verify
        mock_db.is_closed.assert_called_once()
        mock_db.close.assert_not_called()

    def test_database_configuration(self):
        """Test database configuration parameters"""
        self.assertIsInstance(database, PostgresqlDatabase)
        self.assertEqual(database.database, "zednews_dev_db")


if __name__ == "__main__":
    unittest.main()
