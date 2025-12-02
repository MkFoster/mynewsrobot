"""
Integration tests for WeeklySummaryWorkflow

Tests verify that the workflow orchestration is correctly configured with:
- SequentialAgent with all 5 sub-agents
- Correct agent ordering
- Proper workflow metadata
"""

import pytest
from unittest.mock import Mock, patch

from google.adk.agents import SequentialAgent

from src.workflow import WeeklySummaryWorkflow


class TestWeeklySummaryWorkflow:
    """Tests for WeeklySummaryWorkflow configuration and orchestration."""

    def test_create_workflow_returns_sequential_agent(self):
        """Test that create_workflow returns a SequentialAgent instance."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        assert isinstance(workflow, SequentialAgent)

    def test_workflow_has_correct_name(self):
        """Test workflow has the correct name."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        assert workflow.name == "WeeklySummaryWorkflow"

    def test_workflow_has_description(self):
        """Test workflow has a description."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        assert workflow.description is not None
        assert len(workflow.description) > 0
        assert "weekly news summaries" in workflow.description.lower()

    def test_workflow_has_three_sub_agents(self):
        """Test workflow has exactly 3 sub-agents."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        assert workflow.sub_agents is not None
        assert len(workflow.sub_agents) == 3

    def test_workflow_agents_in_correct_order(self):
        """Test that agents are in the correct sequential order."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        
        agent_names = [agent.name for agent in workflow.sub_agents]
        expected_order = [
            "ContentAnalysisAgent",
            "ContentWritingAgent",
            "PublishingAgent",
        ]
        
        assert agent_names == expected_order

    def test_first_agent_is_content_analysis(self):
        """Test that the first agent is ContentAnalysisAgent."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        assert workflow.sub_agents[0].name == "ContentAnalysisAgent"

    def test_last_agent_is_publishing(self):
        """Test that the last agent is PublishingAgent."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        assert workflow.sub_agents[-1].name == "PublishingAgent"

    def test_get_workflow_info_returns_dict(self):
        """Test that get_workflow_info returns a dictionary."""
        info = WeeklySummaryWorkflow.get_workflow_info()
        assert isinstance(info, dict)

    def test_workflow_info_has_correct_structure(self):
        """Test workflow info has all required fields."""
        info = WeeklySummaryWorkflow.get_workflow_info()
        
        assert "name" in info
        assert "description" in info
        assert "agents" in info
        assert "total_agents" in info
        assert "workflow_type" in info

    def test_workflow_info_reports_correct_agent_count(self):
        """Test workflow info reports 3 total agents."""
        info = WeeklySummaryWorkflow.get_workflow_info()
        assert info["total_agents"] == 3

    def test_workflow_info_has_sequential_type(self):
        """Test workflow info indicates sequential type."""
        info = WeeklySummaryWorkflow.get_workflow_info()
        assert info["workflow_type"] == "sequential"

    def test_workflow_info_agents_list_correct_length(self):
        """Test workflow info agents list has 3 entries."""
        info = WeeklySummaryWorkflow.get_workflow_info()
        assert len(info["agents"]) == 3

    def test_workflow_info_agents_have_order(self):
        """Test each agent in workflow info has an order field."""
        info = WeeklySummaryWorkflow.get_workflow_info()
        
        for agent in info["agents"]:
            assert "order" in agent
            assert "name" in agent
            assert "purpose" in agent

    def test_workflow_info_agents_ordered_correctly(self):
        """Test agents in workflow info are numbered 1-3."""
        info = WeeklySummaryWorkflow.get_workflow_info()
        
        orders = [agent["order"] for agent in info["agents"]]
        assert orders == [1, 2, 3]

    def test_workflow_info_name_matches_constant(self):
        """Test workflow info name matches the workflow name."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        info = WeeklySummaryWorkflow.get_workflow_info()
        
        assert info["name"] == workflow.name

    def test_all_sub_agents_have_models(self):
        """Test that all sub-agents have model configuration."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        
        for agent in workflow.sub_agents:
            assert agent.model is not None
            assert len(agent.model) > 0

    def test_all_sub_agents_use_same_model(self):
        """Test that all sub-agents use the same Gemini model."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        
        models = [agent.model for agent in workflow.sub_agents]
        # All should be gemini-2.5-flash
        assert all(model == "gemini-2.5-flash" for model in models)

    def test_all_sub_agents_have_descriptions(self):
        """Test that all sub-agents have descriptions."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        
        for agent in workflow.sub_agents:
            assert agent.description is not None
            assert len(agent.description) > 0

    def test_all_sub_agents_have_instructions(self):
        """Test that all sub-agents have instruction prompts."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        
        for agent in workflow.sub_agents:
            assert agent.instruction is not None
            assert len(agent.instruction) > 0

    def test_workflow_can_be_created_multiple_times(self):
        """Test that workflow can be created multiple times independently."""
        workflow1 = WeeklySummaryWorkflow.create_workflow()
        workflow2 = WeeklySummaryWorkflow.create_workflow()
        
        # Should be different instances
        assert workflow1 is not workflow2
        # But same configuration
        assert workflow1.name == workflow2.name
        assert len(workflow1.sub_agents) == len(workflow2.sub_agents)

    def test_content_analysis_agent_has_tools(self):
        """Test that ContentAnalysisAgent (first) has tools configured."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        analysis_agent = workflow.sub_agents[0]
        
        # ContentAnalysisAgent should have 1 tool (get_topic_priorities)
        assert analysis_agent.tools is not None
        assert len(analysis_agent.tools) == 1

    def test_content_writing_agent_has_no_tools(self):
        """Test that ContentWritingAgent (second) has no tools (pure generation)."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        writing_agent = workflow.sub_agents[1]
        
        # ContentWritingAgent should have no tools
        assert writing_agent.tools is None or len(writing_agent.tools) == 0

    def test_publishing_agent_has_wordpress_tool(self):
        """Test that PublishingAgent (third) has publish_to_wordpress tool configured."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        publishing_agent = workflow.sub_agents[2]
        
        # PublishingAgent should have 1 tool (publish_to_wordpress)
        assert publishing_agent.tools is not None
        assert len(publishing_agent.tools) == 1
        # Verify it's the publish_to_wordpress function
        tool_name = publishing_agent.tools[0].__name__ if hasattr(publishing_agent.tools[0], '__name__') else type(publishing_agent.tools[0]).__name__
        assert tool_name == "publish_to_wordpress"


class TestWorkflowIntegration:
    """Integration tests for the complete workflow."""

    def test_workflow_structure_matches_project_plan(self):
        """Test that workflow structure matches the project plan requirements."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        info = WeeklySummaryWorkflow.get_workflow_info()
        
        # Should have 3 agents in correct order (RSS-only workflow)
        assert info["total_agents"] == 3
        assert info["workflow_type"] == "sequential"
        
        # Verify each agent's purpose matches requirements (RSS-only workflow)
        purposes = [agent["purpose"] for agent in info["agents"]]
        
        # New workflow: Analysis -> Writing -> Publishing (no discovery or extraction)
        assert any("rank" in p.lower() or "select" in p.lower() or "analyze" in p.lower() for p in purposes)
        assert any("write" in p.lower() or "summar" in p.lower() for p in purposes)
        assert any("publish" in p.lower() or "wordpress" in p.lower() for p in purposes)

    def test_workflow_agents_have_unique_names(self):
        """Test that all workflow agents have unique names."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        
        agent_names = [agent.name for agent in workflow.sub_agents]
        assert len(agent_names) == len(set(agent_names))

    def test_workflow_name_is_descriptive(self):
        """Test that workflow name is descriptive."""
        workflow = WeeklySummaryWorkflow.create_workflow()
        
        name = workflow.name.lower()
        assert "weekly" in name or "summary" in name or "workflow" in name
