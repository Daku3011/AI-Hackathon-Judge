import unittest
from unittest.mock import MagicMock, patch
import json
import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from services.judge_engine import run_consensus_panel

class TestConsensus(unittest.TestCase):
    @patch('services.judge_engine.genai')
    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"})
    def test_consensus_aggregation(self, mock_genai):
        # Mock the model and response
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        async def mock_generate(*args, **kwargs):
            return MagicMock(text=json.dumps({
                "judge_name": "TestJudge",
                "innovation_score": 8,
                "technical_score": 7,
                "relevance_score": 9,
                "ui_ux_score": 6,
                "impact_score": 8,
                "presentation_score": 7,
                "win_probability": 85,
                "key_strengths": ["Strong AI", "Good UI"],
                "areas_for_improvement": ["Better docs"],
                "suggested_questions": ["Is it scalable?"],
                "summary_feedback": "Good job.",
                "why_it_wont_win": "Too competitive.",
                "ppt_analysis": {"is_relevant": True}
            }))

        mock_model.generate_content_async = mock_generate
        
        # Run the consensus panel
        result_json = asyncio.run(run_consensus_panel("repo", "transcript", "docs", "ppt"))
        result = json.loads(result_json)
        
        print("Result:", result)
        
        self.assertEqual(result["innovation_score"], 8)
        self.assertEqual(result["win_probability"], 85)
        self.assertIn("key_strengths", result)
        self.assertIn("Strong AI", result["key_strengths"])

if __name__ == '__main__':
    unittest.main()
