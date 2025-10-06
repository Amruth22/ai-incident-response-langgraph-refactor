#!/usr/bin/env python3
"""
Comprehensive test suite for the AI-Powered Incident Response System.
Tests all major components and services.

Run with: python tests.py
"""

import os
import sys
import unittest
import logging
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("tests")

# Import the required modules
try:
    from config import get_config, get_config_value, validate_config
    from state import IncidentState
    from graph import create_incident_workflow, create_initial_state
    from nodes.incident_trigger_node import incident_trigger_node
    from nodes.log_analysis_node import log_analysis_node
    from nodes.knowledge_lookup_node import knowledge_lookup_node
    from nodes.root_cause_node import root_cause_node
    from nodes.coordinator_node import coordinator_node
    from nodes.decision_node import decision_node
    from nodes.mitigation_node import mitigation_node
    from nodes.escalation_node import escalation_node
    from nodes.communicator_node import communicator_node
    from agents.log_analyzer import LogAnalyzer
    from agents.knowledge_searcher import KnowledgeSearcher
    from agents.ai_analyzer import AIAnalyzer
    from agents.email_notifier import EmailNotifier
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure you're running this test from the project root directory")
    sys.exit(1)


class TestIncidentResponseSystem(unittest.TestCase):
    """Test suite for AI-Powered Incident Response System"""
    
    SAMPLE_ALERT = "Payment API experiencing database connection timeouts and high error rates"
    
    def test_configuration(self):
        """Test configuration management"""
        logger.info("Testing configuration management...")
        
        # Test getting configuration
        config = get_config()
        self.assertIsNotNone(config, "Config should not be None")
        
        # Test getting specific values with defaults
        gemini_key = get_config_value("GEMINI_API_KEY", "default")
        self.assertIsNotNone(gemini_key, "GEMINI_API_KEY should not be None")
        
        # Test default value
        test_value = get_config_value("NON_EXISTENT_VALUE", "default_value")
        self.assertEqual(test_value, "default_value", "Default value should be returned for missing keys")
        
        # Test thresholds
        confidence_threshold = get_config_value("CONFIDENCE_THRESHOLD", 0.0)
        self.assertGreaterEqual(confidence_threshold, 0.0, "CONFIDENCE_THRESHOLD should be >= 0.0")
        self.assertLessEqual(confidence_threshold, 1.0, "CONFIDENCE_THRESHOLD should be <= 1.0")
        
        max_retries = get_config_value("MAX_RETRIES", 0)
        self.assertGreater(max_retries, 0, "MAX_RETRIES should be > 0")

        logger.info("Configuration tests passed")
    
    def test_state_creation(self):
        """Test state creation"""
        logger.info("Testing state creation...")
        
        # Test creating initial state
        state = create_initial_state(self.SAMPLE_ALERT)
        self.assertIsNotNone(state, "State should not be None")
        self.assertEqual(state["raw_alert"], self.SAMPLE_ALERT, "Raw alert should be set correctly")
        
        # Test incident ID format
        self.assertTrue("incident_id" in state, "State should contain incident_id")
        self.assertTrue(state["incident_id"].startswith("INC-"), "Incident ID should start with INC-")
        
        # Test timestamp format
        self.assertTrue("timestamp" in state, "State should contain timestamp")
        
        # Test initial values
        self.assertEqual(state["retry_count"], 0, "Initial retry count should be 0")
        self.assertEqual(state["workflow_complete"], False, "Workflow should not be complete initially")
        
        logger.info("State creation tests passed")
    
    def test_log_analyzer(self):
        """Test log analyzer (thin agent)"""
        logger.info("Testing log analyzer...")
        
        analyzer = LogAnalyzer()
        results = analyzer.analyze_logs("Payment API", "database timeout")
        
        self.assertIsNotNone(results, "Log analysis results should not be None")
        self.assertTrue("anomalies" in results, "Results should contain anomalies")
        self.assertTrue("anomalies_found" in results, "Results should contain anomalies_found")
        self.assertTrue("analysis_confidence" in results, "Results should contain analysis_confidence")
        
        # Should find anomalies for database timeout
        self.assertTrue(len(results["anomalies"]) > 0, "Should find anomalies for database timeout")
        
        logger.info("Log analyzer tests passed")
    
    def test_log_analysis_node(self):
        """Test log analysis node (pure business logic)"""
        logger.info("Testing log analysis node...")
        
        state = {
            "incident_id": "TEST-INC",
            "service": "Payment API",
            "description": "database timeout"
        }
        
        result = log_analysis_node(state)
        
        self.assertIsNotNone(result, "Log analysis node result should not be None")
        self.assertTrue("log_analysis_results" in result, "Result should contain log_analysis_results")
        self.assertFalse("agents_completed" in result, "Node should NOT return agents_completed")
        self.assertFalse("next" in result, "Node should NOT return next")
        self.assertFalse("stage" in result, "Node should NOT return stage")
        
        logger.info("Log analysis node tests passed")
    
    def test_knowledge_searcher(self):
        """Test knowledge searcher (thin agent)"""
        logger.info("Testing knowledge searcher...")
        
        searcher = KnowledgeSearcher()
        results = searcher.search_similar_incidents(
            "Payment API",
            "database timeout",
            [{"type": "database_timeout"}]
        )
        
        self.assertIsNotNone(results, "Knowledge search results should not be None")
        self.assertTrue("similar_incidents" in results, "Results should contain similar_incidents")
        self.assertTrue("total_matches" in results, "Results should contain total_matches")
        self.assertTrue("confidence" in results, "Results should contain confidence")
        
        # Should find similar incidents for Payment API database issues
        self.assertGreater(results["total_matches"], 0, "Should find similar incidents")
        
        logger.info("Knowledge searcher tests passed")
    
    def test_knowledge_lookup_node(self):
        """Test knowledge lookup node (pure business logic)"""
        logger.info("Testing knowledge lookup node...")
        
        state = {
            "incident_id": "TEST-INC",
            "service": "Payment API",
            "description": "database timeout",
            "log_analysis_results": {
                "anomalies": [{"type": "database_timeout"}]
            }
        }
        
        result = knowledge_lookup_node(state)
        
        self.assertIsNotNone(result, "Knowledge lookup node result should not be None")
        self.assertTrue("knowledge_lookup_results" in result, "Result should contain knowledge_lookup_results")
        self.assertFalse("agents_completed" in result, "Node should NOT return agents_completed")
        self.assertFalse("next" in result, "Node should NOT return next")
        
        logger.info("Knowledge lookup node tests passed")
    
    def test_ai_analyzer(self):
        """Test AI analyzer (thin agent)"""
        logger.info("Testing AI analyzer...")
        
        analyzer = AIAnalyzer()
        
        # Test alert parsing
        parsed = analyzer.parse_incident_alert(self.SAMPLE_ALERT)
        
        self.assertIsNotNone(parsed, "Parsed result should not be None")
        self.assertTrue("service" in parsed, "Parsed should contain service")
        self.assertTrue("severity" in parsed, "Parsed should contain severity")
        self.assertTrue("description" in parsed, "Parsed should contain description")
        
        logger.info("AI analyzer tests passed")
    
    def test_incident_trigger_node(self):
        """Test incident trigger node (pure business logic)"""
        logger.info("Testing incident trigger node...")
        
        state = {
            "incident_id": "TEST-INC",
            "raw_alert": self.SAMPLE_ALERT
        }
        
        result = incident_trigger_node(state)
        
        self.assertIsNotNone(result, "Incident trigger node result should not be None")
        self.assertTrue("service" in result, "Result should contain service")
        self.assertTrue("severity" in result, "Result should contain severity")
        self.assertTrue("description" in result, "Result should contain description")
        self.assertFalse("agents_completed" in result, "Node should NOT return agents_completed")
        self.assertFalse("next" in result, "Node should NOT return next")
        
        logger.info("Incident trigger node tests passed")
    
    def test_decision_node(self):
        """Test decision node logic"""
        logger.info("Testing decision node...")
        
        # Create mock state with high confidence
        state = {
            "incident_id": "TEST-INC",
            "retry_count": 0,
            "log_analysis_results": {
                "anomalies_found": True,
                "anomalies": [{"type": "database_timeout"}]
            },
            "knowledge_lookup_results": {
                "total_matches": 2,
                "similar_incidents": [{"incident_id": "INC-001"}]
            },
            "root_cause_results": {
                "confidence": 0.85,
                "root_cause": "Database connection pool exhaustion"
            }
        }
        
        result = decision_node(state)
        
        self.assertIsNotNone(result, "Decision result should not be None")
        self.assertTrue("decision" in result, "Result should contain decision")
        self.assertTrue("decision_metrics" in result, "Result should contain decision_metrics")
        self.assertFalse("next" in result, "Node should NOT return next")
        
        # High confidence should lead to auto_mitigation
        self.assertEqual(result["decision"], "auto_mitigation", "High confidence should auto-mitigate")
        
        logger.info("Decision node tests passed")
    
    def test_decision_node_escalation(self):
        """Test decision node escalation logic"""
        logger.info("Testing decision node escalation...")
        
        # Create mock state with low confidence
        state = {
            "incident_id": "TEST-INC",
            "retry_count": 0,
            "log_analysis_results": {
                "anomalies_found": True,
                "anomalies": [{"type": "unknown"}]
            },
            "knowledge_lookup_results": {
                "total_matches": 0,
                "similar_incidents": []
            },
            "root_cause_results": {
                "confidence": 0.5,
                "root_cause": "Unknown"
            }
        }
        
        result = decision_node(state)
        
        self.assertIsNotNone(result, "Decision result should not be None")
        self.assertEqual(result["decision"], "escalation", "Low confidence should escalate")
        self.assertTrue(len(result.get("escalation_reason", "")) > 0, "Should have escalation reason")
        
        logger.info("Decision node escalation tests passed")
    
    def test_workflow_structure(self):
        """Test workflow structure and graph setup"""
        logger.info("Testing workflow structure...")
        
        workflow = create_incident_workflow()
        
        self.assertIsNotNone(workflow, "Compiled workflow should not be None")
        
        logger.info("Workflow structure tests passed")
    
    def test_full_pipeline(self):
        """Test the full pipeline"""
        logger.info("Testing full pipeline execution...")
        
        # Create initial state
        state = create_initial_state(self.SAMPLE_ALERT)
        
        # Execute incident trigger
        trigger_result = incident_trigger_node(state)
        state.update(trigger_result)
        
        # Execute parallel analyses
        log_result = log_analysis_node(state)
        knowledge_result = knowledge_lookup_node(state)
        root_cause_result = root_cause_node(state)
        
        # Combine results
        state.update(log_result)
        state.update(knowledge_result)
        state.update(root_cause_result)
        
        # Execute coordinator
        coord_result = coordinator_node(state)
        state.update(coord_result)
        
        # Execute decision
        decision_result = decision_node(state)
        state.update(decision_result)
        
        self.assertIsNotNone(decision_result, "Decision result should not be None")
        self.assertTrue("decision" in decision_result, "Decision result should contain decision")
        
        logger.info(f"Pipeline decision: {decision_result.get('decision', 'unknown')}")
        logger.info("Full pipeline tests passed")
    
    def test_node_purity(self):
        """Test that nodes are pure functions (no orchestration)"""
        logger.info("Testing node purity...")
        
        state = {
            "incident_id": "TEST-INC",
            "raw_alert": self.SAMPLE_ALERT,
            "service": "Payment API",
            "description": "database timeout",
            "log_analysis_results": {"anomalies": []},
            "knowledge_lookup_results": {},
            "root_cause_results": {}
        }
        
        # Test all nodes
        nodes = [
            incident_trigger_node,
            log_analysis_node,
            knowledge_lookup_node,
            root_cause_node,
            coordinator_node,
            decision_node
        ]
        
        for node in nodes:
            result = node(state)
            
            # Verify nodes return ONLY business data
            self.assertFalse("agents_completed" in result, 
                           f"{node.__name__} should NOT return agents_completed")
            self.assertFalse("next" in result, 
                           f"{node.__name__} should NOT return next")
            self.assertFalse("stage" in result, 
                           f"{node.__name__} should NOT return stage")
        
        logger.info("Node purity tests passed")
    
    def test_mitigation_node(self):
        """Test mitigation node"""
        logger.info("Testing mitigation node...")
        
        state = {
            "incident_id": "TEST-INC",
            "service": "Payment API",
            "root_cause_results": {
                "recommended_solution": "Scale database connection pool"
            }
        }
        
        result = mitigation_node(state)
        
        self.assertIsNotNone(result, "Mitigation result should not be None")
        self.assertTrue("mitigation_results" in result, "Result should contain mitigation_results")
        self.assertFalse("workflow_complete" in result, "Node should NOT set workflow_complete")
        
        logger.info("Mitigation node tests passed")
    
    def test_escalation_node(self):
        """Test escalation node"""
        logger.info("Testing escalation node...")
        
        state = {
            "incident_id": "TEST-INC",
            "service": "Payment API",
            "severity": "HIGH",
            "escalation_reason": "Low confidence in root cause"
        }
        
        result = escalation_node(state)
        
        self.assertIsNotNone(result, "Escalation result should not be None")
        self.assertTrue("escalation_results" in result, "Result should contain escalation_results")
        self.assertFalse("workflow_complete" in result, "Node should NOT set workflow_complete")
        
        logger.info("Escalation node tests passed")


def run_tests():
    """Run all tests"""
    logger.info("=" * 70)
    logger.info("AI-Powered Incident Response System - Test Suite")
    logger.info("LangGraph-Compliant Architecture")
    logger.info("=" * 70)
    
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


if __name__ == "__main__":
    run_tests()
