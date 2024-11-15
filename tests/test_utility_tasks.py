import unittest
from unittest.mock import patch
from workflows.tasks.utility import create_temporary_dir, delete_temporary_dir


class TestUtilityTasks(unittest.TestCase):
    @patch("workflows.tasks.utility.tempfile.mkdtemp")
    def test_create_temporary_dir_success(self, mock_mkdtemp):
        mock_mkdtemp.return_value = "/tmp/test_dir"
        result = create_temporary_dir()
        self.assertEqual(result, "/tmp/test_dir")
        mock_mkdtemp.assert_called_once()

    @patch("workflows.tasks.utility.tempfile.mkdtemp")
    def test_create_temporary_dir_exception(self, mock_mkdtemp):
        mock_mkdtemp.side_effect = OSError("Failed to create directory")
        with self.assertRaises(OSError):
            create_temporary_dir()

    @patch("workflows.tasks.utility.os.path.exists")
    @patch("workflows.tasks.utility.shutil.rmtree")
    def test_delete_temporary_dir_existing(self, mock_rmtree, mock_exists):
        mock_exists.return_value = True
        delete_temporary_dir("/tmp/test_dir")
        mock_exists.assert_called_once_with("/tmp/test_dir")
        mock_rmtree.assert_called_once_with("/tmp/test_dir")

    @patch("workflows.tasks.utility.os.path.exists")
    @patch("workflows.tasks.utility.shutil.rmtree")
    def test_delete_temporary_dir_non_existent(self, mock_rmtree, mock_exists):
        mock_exists.return_value = False
        delete_temporary_dir("/tmp/test_dir")
        mock_exists.assert_called_once_with("/tmp/test_dir")
        mock_rmtree.assert_not_called()

    @patch("workflows.tasks.utility.os.path.exists")
    @patch("workflows.tasks.utility.shutil.rmtree")
    def test_delete_temporary_dir_exception(self, mock_rmtree, mock_exists):
        mock_exists.return_value = True
        mock_rmtree.side_effect = OSError("Failed to delete directory")
        with self.assertRaises(OSError):
            delete_temporary_dir("/tmp/test_dir")

if __name__ == "__main__":
    unittest.main()