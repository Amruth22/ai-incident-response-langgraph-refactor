"""
Escalation Node - Pure Business Logic
Escalates incident to human operators
"""

import logging
from typing import Dict, Any
from datetime import datetime
from agents.email_notifier import EmailNotifier

logger = logging.getLogger("escalation_node")


def escalation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Escalate incident to human operators
    
    Pure business logic - NO orchestration
    Returns ONLY escalation data
    """
    incident_id = state.get("incident_id", "")
    service = state.get("service", "Unknown Service")
    severity = state.get("severity", "MEDIUM")
    escalation_reason = state.get("escalation_reason", "Unknown reason")
    
    logger.info(f"Escalating incident to human operators: {escalation_reason}")
    
    # Prepare context for human operators
    context = _prepare_escalation_context(state)
    
    # Determine priority
    priority = "HIGH" if severity == "HIGH" else "MEDIUM"
    
    # Send escalation alert
    try:
        email_notifier = EmailNotifier()
        email_notifier.send_escalation_alert(incident_id, escalation_reason, context)
    except Exception as e:
        logger.warning(f"Failed to send escalation email: {e}")
    
    logger.info(f"Incident escalated with priority: {priority}")
    
    # Return ONLY escalation data
    # NO workflow_complete flag - graph handles that
    return {
        "escalation_results": {
            "escalation_reason": escalation_reason,
            "assigned_to": "Senior Operations Team",
            "priority": priority,
            "context_provided": context,
            "escalation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def _prepare_escalation_context(state: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare context information for human operators"""
    log_results = state.get("log_analysis_results", {})
    knowledge_results = state.get("knowledge_lookup_results", {})
    root_cause_results = state.get("root_cause_results", {})
    
    context = {
        "service": state.get("service", "Unknown"),
        "severity": state.get("severity", "MEDIUM"),
        "description": state.get("description", ""),
        "confidence": root_cause_results.get("confidence", 0.0)
    }
    
    # Add analysis summary
    if log_results:
        context["anomalies_detected"] = len(log_results.get("anomalies", []))
    
    if knowledge_results:
        context["similar_incidents"] = knowledge_results.get("total_matches", 0)
    
    if root_cause_results:
        context["ai_root_cause"] = root_cause_results.get("root_cause", "Unknown")
        context["suggested_solution"] = root_cause_results.get("recommended_solution", "Manual investigation")
    
    return context
