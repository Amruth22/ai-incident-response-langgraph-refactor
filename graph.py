"""
Graph - Pure Orchestration Logic
Defines the incident response workflow structure and routing
NO business logic - that's in nodes/
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import uuid
from langgraph.graph import StateGraph, END

from state import IncidentState
from nodes import (
    incident_trigger_node,
    log_analysis_node,
    knowledge_lookup_node,
    root_cause_node,
    coordinator_node,
    decision_node,
    mitigation_node,
    escalation_node,
    communicator_node
)

logger = logging.getLogger("graph")


def create_incident_workflow():
    """
    Create the incident response workflow graph
    
    This is PURE orchestration - defines:
    - What nodes exist
    - How they connect
    - When they execute
    - Routing logic
    
    NO business logic here!
    """
    logger.info("Building LangGraph incident response workflow...")
    
    # Create workflow with state schema
    workflow = StateGraph(IncidentState)
    
    # Add nodes (pure business logic functions)
    workflow.add_node("incident_trigger", incident_trigger_node)
    workflow.add_node("log_analysis", log_analysis_node)
    workflow.add_node("knowledge_lookup", knowledge_lookup_node)
    workflow.add_node("root_cause", root_cause_node)
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("decision", decision_node)
    workflow.add_node("mitigation", mitigation_node)
    workflow.add_node("escalation", escalation_node)
    workflow.add_node("communicator", communicator_node)
    
    # Set entry point
    workflow.set_entry_point("incident_trigger")
    
    # Define routing (orchestration logic)
    # After incident trigger, launch 3 analysis nodes in parallel
    workflow.add_conditional_edges(
        "incident_trigger",
        route_after_trigger
    )
    
    # All analysis nodes route to coordinator
    workflow.add_edge("log_analysis", "coordinator")
    workflow.add_edge("knowledge_lookup", "coordinator")
    workflow.add_edge("root_cause", "coordinator")
    
    # Coordinator routes to decision
    workflow.add_conditional_edges(
        "coordinator",
        route_after_coordination
    )
    
    # Decision routes to mitigation or escalation
    workflow.add_conditional_edges(
        "decision",
        route_after_decision
    )
    
    # Both mitigation and escalation route to communicator
    workflow.add_edge("mitigation", "communicator")
    workflow.add_edge("escalation", "communicator")
    
    # Communicator ends workflow
    workflow.add_edge("communicator", END)
    
    logger.info("LangGraph workflow created successfully")
    logger.info("Flow: Trigger → [3 Parallel Analyses] → Coordinator → Decision → Action → Communicator")
    
    return workflow.compile()


# Routing Functions (Orchestration Logic)

def route_after_trigger(state: IncidentState) -> List[str]:
    """
    Route after incident trigger
    
    Orchestration logic - decides what runs next
    """
    # Check for errors
    if state.get("error"):
        logger.error(f"Incident trigger failed: {state['error']}")
        return [END]
    
    # Check if we have service info
    service = state.get("service")
    if not service or service == "Unknown Service":
        logger.warning("Could not identify service - ending workflow")
        return [END]
    
    # Launch all 3 analysis nodes in parallel
    logger.info("Launching 3 analysis nodes in parallel...")
    return ["log_analysis", "knowledge_lookup", "root_cause"]


def route_after_coordination(state: IncidentState) -> str:
    """
    Route after coordination
    
    Orchestration logic - checks if all analyses completed
    """
    # Check which analyses have completed
    expected_analyses = {"log_analysis", "knowledge_lookup", "root_cause"}
    
    # Check if we have results from all analyses
    has_log = bool(state.get("log_analysis_results"))
    has_knowledge = bool(state.get("knowledge_lookup_results"))
    has_root_cause = bool(state.get("root_cause_results"))
    
    completed = []
    if has_log:
        completed.append("log_analysis")
    if has_knowledge:
        completed.append("knowledge_lookup")
    if has_root_cause:
        completed.append("root_cause")
    
    logger.info(f"Analyses completed: {', '.join(completed)}")
    
    # Check if all expected analyses completed
    if set(completed) >= expected_analyses:
        logger.info("All analyses complete - proceeding to decision")
        return "decision"
    else:
        missing = expected_analyses - set(completed)
        logger.warning(f"Still waiting for: {', '.join(missing)}")
        # Proceed to decision with available results
        return "decision"


def route_after_decision(state: IncidentState) -> str:
    """
    Route after decision making
    
    Orchestration logic - routes to mitigation or escalation
    """
    decision = state.get("decision", "escalation")
    
    if decision == "auto_mitigation":
        logger.info("Routing to automated mitigation")
        return "mitigation"
    else:
        logger.info("Routing to human escalation")
        return "escalation"


# Workflow Execution

def execute_incident_workflow(raw_alert: str) -> Dict[str, Any]:
    """
    Execute the incident response workflow
    
    This is the main entry point for processing an incident
    """
    logger.info("=" * 70)
    logger.info("STARTING INCIDENT RESPONSE WORKFLOW")
    logger.info(f"Alert: {raw_alert[:100]}...")
    logger.info("=" * 70)
    
    # Create workflow
    workflow = create_incident_workflow()
    
    # Create initial state
    initial_state = create_initial_state(raw_alert)
    
    # Execute workflow
    logger.info("Executing workflow...")
    final_state = workflow.invoke(initial_state)
    
    # Display results
    display_results(final_state)
    
    return final_state


def create_initial_state(raw_alert: str) -> IncidentState:
    """
    Create initial state for workflow
    
    This is orchestration-level state initialization
    """
    incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    return IncidentState(
        incident_id=incident_id,
        raw_alert=raw_alert,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        
        service="",
        severity="",
        description="",
        
        log_analysis_results={},
        knowledge_lookup_results={},
        root_cause_results={},
        mitigation_results={},
        escalation_results={},
        
        coordination_summary={},
        
        decision="",
        decision_metrics={},
        escalation_reason="",
        
        agents_completed=[],
        agent_errors=[],
        
        emails_sent=[],
        
        retry_count=0,
        error="",
        workflow_complete=False,
        updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


def display_results(state: IncidentState) -> None:
    """Display workflow results"""
    logger.info("=" * 70)
    logger.info("WORKFLOW COMPLETED")
    logger.info(f"Incident ID: {state['incident_id']}")
    logger.info("=" * 70)
    
    # Display decision
    decision = state.get("decision", "unknown")
    logger.info(f"Decision: {decision.upper()}")
    
    # Display metrics
    metrics = state.get("decision_metrics", {})
    if metrics:
        logger.info(f"Confidence: {metrics.get('confidence', 0):.2f}")
        logger.info(f"Anomalies Found: {metrics.get('anomalies_found', False)}")
        logger.info(f"Similar Incidents: {metrics.get('similar_incidents_count', 0)}")
        
        if metrics.get("escalation_reason"):
            logger.warning(f"Escalation Reason: {metrics['escalation_reason']}")
    
    # Display final status
    final_report = state.get("final_report", {})
    if final_report:
        logger.info(f"Final Status: {final_report.get('status', 'Unknown')}")
    
    logger.info("=" * 70)
