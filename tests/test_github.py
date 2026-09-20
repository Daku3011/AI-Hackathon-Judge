import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from services.github_analyzer import analyze_repo

class TestGitHubAnalyzer(unittest.TestCase):

    def test_invalid_github_url(self):
        result = analyze_repo("https://github.com/invalid")
        self.assertEqual(result.get("files_count"), 0)
        self.assertIn("Invalid GitHub URL", result.get("summary"))

    @patch('services.github_analyzer.Github')
    def test_analyze_repo_success(self, mock_github_cls):
        mock_github = MagicMock()
        mock_github_cls.return_value = mock_github
        
        mock_repo = MagicMock()
        mock_repo.description = "Test project description"
        mock_repo.stargazers_count = 42
        mock_repo.language = "Python"
        
        # Mock get_languages returning metadata like 'url' as well as counts
        mock_repo.get_languages.return_value = {
            "Python": 4000,
            "JavaScript": 2000,
            "url": "https://api.github.com/repos/test/repo/languages"
        }
        
        mock_readme = MagicMock()
        mock_readme.decoded_content.decode.return_value = "# Project Title\nDemo project"
        mock_repo.get_readme.return_value = mock_readme

        # Mock root contents
        mock_file1 = MagicMock()
        mock_file1.type = "file"
        mock_file1.name = "main.py"
        mock_file1.path = "main.py"
        mock_file1.size = 500
        mock_file1.decoded_content.decode.return_value = "print('hello world')"

        mock_repo.get_contents.return_value = [mock_file1]
        mock_github.get_repo.return_value = mock_repo

        result = analyze_repo("https://github.com/testowner/testrepo")

        self.assertGreater(result["files_count"], 0)
        self.assertEqual(result["languages"], {"Python": 4000, "JavaScript": 2000})
        # LOC: (4000 // 40) + (2000 // 40) = 100 + 50 = 150
        self.assertEqual(result["estimated_loc"], 150)
        self.assertIn("Repository: testowner/testrepo", result["summary"])

    @patch('services.github_analyzer.Github')
    def test_security_pattern_detection(self, mock_github_cls):
        mock_github = MagicMock()
        mock_github_cls.return_value = mock_github
        
        mock_repo = MagicMock()
        mock_repo.description = "Security test"
        mock_repo.stargazers_count = 1
        mock_repo.language = "Python"
        mock_repo.get_languages.return_value = {"Python": 1000}
        mock_repo.get_readme.side_effect = Exception("No README")

        mock_secret_file = MagicMock()
        mock_secret_file.type = "file"
        mock_secret_file.name = "config.py"
        mock_secret_file.path = "config.py"
        mock_secret_file.size = 200
        mock_secret_file.decoded_content.decode.return_value = "API_KEY = 'abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx'"

        mock_repo.get_contents.return_value = [mock_secret_file]
        mock_github.get_repo.return_value = mock_repo

        result = analyze_repo("https://github.com/testowner/secretrepo")
        self.assertTrue(any("OpenAI Key" in issue for issue in result["security_issues"]))

if __name__ == '__main__':
    unittest.main()
