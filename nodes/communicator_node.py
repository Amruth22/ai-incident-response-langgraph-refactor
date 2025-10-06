"""
Communicator Node - Pure Business Logic
Generates final status report
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger("communicator_node")


def communicator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate final status report
    
    Pure business logic - NO orchestration
    Returns ONLY report data
    """
    incident_id = state.get("incident_id", "")
    decision = state.get("decision", "unknown")
    
    logger.info(f"Generating final report for {incident_id}")
    
    # Build final report
    report = {
        "incident_id": incident_id,
        "service": state.get("service", "Unknown"),
        "severity": state.get("severity", "MEDIUM"),
        "decision": decision,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add decision-specific details
    if decision == "auto_mitigation":
        mitigation_results = state.get("mitigation_results", {})
        report["status"] = "RESOLVED"
        report["resolution"] = "Automated mitigation executed successfully"
        report["actions_taken"] = mitigation_results.get("actions_taken", [])
    else:
        escalation_results = state.get("escalation_results", {})
        report["status"] = "ESCALATED"
        report["resolution"] = "Escalated to human operators"
        report["escalation_reason"] = state.get("escalation_reason", "Unknown")
        report["assigned_to"] = escalation_results.get("assigned_to", "Operations Team")
    
    # Add metrics
    decision_metrics = state.get("decision_metrics", {})
    report["metrics"] = decision_metrics
    
    logger.info(f"Final report generated: {report['status']}")
    
    # Return ONLY report data
    # NO workflow_complete flag - graph handles that
    return {
        "final_report": report,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
