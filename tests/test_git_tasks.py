import unittest
from unittest.mock import patch, MagicMock, call
from prefect.logging import disable_run_logger
from workflows.tasks.git import clone_repository, create_branch, commit_changes, push_changes
from git import GitCommandError


class TestGitTasks(unittest.TestCase):
    @patch('workflows.tasks.git.Repo')
    @patch('workflows.tasks.git.os.path.exists')
    def test_clone_repository(self, mock_exists, mock_repo):
        with disable_run_logger():
            mock_exists.return_value = False
            result = clone_repository.fn("https://github.com/example/repo.git", "/tmp/repo")

            mock_repo.clone_from.assert_called_once_with(
                "https://github.com/example/repo.git", "/tmp/repo"
            )
            self.assertEqual(result, "/tmp/repo")

    @patch('workflows.tasks.git.Repo')
    @patch('workflows.tasks.git.os.path.exists')
    def test_clone_repository_existing_dir(self, mock_exists, mock_repo):
        with disable_run_logger():
            mock_exists.return_value = True
            result = clone_repository.fn("https://github.com/example/repo.git", "/tmp/repo")

            mock_repo.clone_from.assert_called_once_with(
                "https://github.com/example/repo.git", "/tmp/repo"
            )
            self.assertEqual(result, "/tmp/repo")

    @patch('workflows.tasks.git.Repo')
    def test_create_branch(self, mock_repo):
        with disable_run_logger():
            mock_instance = mock_repo.return_value
            mock_new_branch = MagicMock()
            mock_instance.create_head.return_value = mock_new_branch

            result = create_branch.fn("/tmp/repo", "feature-branch")

            mock_repo.assert_called_once_with("/tmp/repo")
            mock_instance.create_head.assert_called_once_with("feature-branch")
            mock_new_branch.checkout.assert_called_once()
            self.assertEqual(result, "feature-branch")

    @patch('workflows.tasks.git.Repo')
    def test_commit_changes_with_changes(self, mock_repo):
        with disable_run_logger():
            mock_instance = mock_repo.return_value
            mock_instance.is_dirty.return_value = True
            mock_instance.untracked_files = ['new_file.txt']

            result = commit_changes.fn("/tmp/repo", "Test commit")

            mock_instance.git.add.assert_called_once_with(all=True)
            mock_instance.index.commit.assert_called_once_with("Test commit")
            self.assertTrue(result)

    @patch('workflows.tasks.git.Repo')
    def test_commit_changes_without_changes(self, mock_repo):
        with disable_run_logger():
            mock_instance = mock_repo.return_value
            mock_instance.is_dirty.return_value = False
            mock_instance.untracked_files = []

            result = commit_changes.fn("/tmp/repo", "Test commit")

            mock_instance.git.add.assert_not_called()
            mock_instance.index.commit.assert_not_called()
            self.assertFalse(result)

    @patch('workflows.tasks.git.Repo')
    def test_push_changes_with_unpushed_commits(self, mock_repo):
        with disable_run_logger():
            mock_instance = mock_repo.return_value
            mock_remote = MagicMock()
            mock_instance.remote.return_value = mock_remote
            mock_instance.git.branch.return_value = 'origin/feature-branch'
            mock_instance.iter_commits.return_value = [MagicMock()]  # Simulate unpushed commits

            result = push_changes.fn("/tmp/repo", "feature-branch")

            mock_instance.remote.assert_called_once_with(name="origin")
            mock_remote.fetch.assert_called_once()
            mock_instance.git.branch.assert_called_once_with('-r')
            mock_instance.iter_commits.assert_called_once_with('origin/feature-branch..feature-branch')
            mock_remote.push.assert_called_once_with(refspec="feature-branch:feature-branch")
            self.assertTrue(result)

    @patch('workflows.tasks.git.Repo')
    def test_push_changes_without_unpushed_commits(self, mock_repo):
        with disable_run_logger():
            mock_instance = mock_repo.return_value
            mock_remote = MagicMock()
            mock_instance.remote.return_value = mock_remote
            mock_instance.git.branch.return_value = 'origin/feature-branch'
            mock_instance.iter_commits.return_value = []  # Simulate no unpushed commits

            result = push_changes.fn("/tmp/repo", "feature-branch")

            mock_instance.remote.assert_called_once_with(name="origin")
            mock_remote.fetch.assert_called_once()
            mock_instance.git.branch.assert_called_once_with('-r')
            mock_instance.iter_commits.assert_called_once_with('origin/feature-branch..feature-branch')
            mock_remote.push.assert_not_called()
            self.assertFalse(result)

    @patch('workflows.tasks.git.Repo')
    def test_push_changes_new_branch(self, mock_repo):
        with disable_run_logger():
            mock_instance = mock_repo.return_value
            mock_remote = MagicMock()
            mock_instance.remote.return_value = mock_remote
            mock_instance.git.branch.return_value = ''  # Simulate remote branch not existing

            result = push_changes.fn("/tmp/repo", "feature-branch")

            mock_instance.remote.assert_called_once_with(name="origin")
            mock_remote.fetch.assert_called_once()
            mock_instance.git.branch.assert_called_once_with('-r')
            mock_remote.push.assert_called_once_with(refspec="feature-branch:feature-branch")
            self.assertTrue(result)

    @patch('workflows.tasks.git.Repo')
    def test_push_changes_git_command_error(self, mock_repo):
        with disable_run_logger():
            mock_instance = mock_repo.return_value
            mock_remote = MagicMock()
            mock_instance.remote.return_value = mock_remote
            mock_instance.git.branch.return_value = 'origin/feature-branch'
            mock_instance.iter_commits.side_effect = GitCommandError('git', 'error')

            result = push_changes.fn("/tmp/repo", "feature-branch")

            mock_instance.remote.assert_called_once_with(name="origin")
            mock_remote.fetch.assert_called_once()
            mock_instance.git.branch.assert_called_once_with('-r')
            mock_instance.iter_commits.assert_called_once_with('origin/feature-branch..feature-branch')
            mock_remote.push.assert_not_called()
            self.assertFalse(result)
