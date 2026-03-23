import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the script dir to sys path so we can import it
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import run_scenarios

def test_scenario_prompts_are_correctly_formed():
    """Test that run_scenario constructs the expected simulation_requirement for A, B, and C."""
    with patch('requests.post') as mock_post, patch('requests.get') as mock_get:
        # Mock responses to short-circuit the function
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        # Test Scenario A
        run_scenarios.run_scenario("Scenario A", "Strategy A", "Keyword A", 2)
        
        # Look at the first post call (Ontology generation)
        call_args = mock_post.call_args_list[0][1]
        data = call_args['data']
        assert "This is Scenario A." in data['simulation_requirement']
        assert "MARKETING STRATEGY: Strategy A." in data['simulation_requirement']
        assert "(Keyword A)" in data['simulation_requirement']

        # Test Scenario B
        mock_post.reset_mock()
        run_scenarios.run_scenario("Scenario B", "Strategy B", "Keyword B", 2)
        call_args = mock_post.call_args_list[0][1]
        data = call_args['data']
        assert "This is Scenario B." in data['simulation_requirement']
        assert "MARKETING STRATEGY: Strategy B." in data['simulation_requirement']
        assert "(Keyword B)" in data['simulation_requirement']

        # Test Scenario C
        mock_post.reset_mock()
        run_scenarios.run_scenario("Scenario C", "Strategy C", "Keyword C", 2)
        call_args = mock_post.call_args_list[0][1]
        data = call_args['data']
        assert "This is Scenario C." in data['simulation_requirement']
        assert "MARKETING STRATEGY: Strategy C." in data['simulation_requirement']
        assert "(Keyword C)" in data['simulation_requirement']
