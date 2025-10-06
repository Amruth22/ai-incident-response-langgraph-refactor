"""
Decision Node - Pure Business Logic
Makes automated decision based on analysis results
"""

import logging
from typing import Dict, Any
from config import get_config_value

logger = logging.getLogger("decision_node")


def decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make automated decision based on analysis results
    
    Pure business logic - NO orchestration
    Returns ONLY decision data
    """
    logger.info("Making automated decision")
    
    # Get configuration
    CONFIDENCE_THRESHOLD = get_config_value("CONFIDENCE_THRESHOLD", 0.8)
    MAX_RETRIES = get_config_value("MAX_RETRIES", 3)
    
    # Extract results
    log_results = state.get("log_analysis_results", {})
    knowledge_results = state.get("knowledge_lookup_results", {})
    root_cause_results = state.get("root_cause_results", {})
    retry_count = state.get("retry_count", 0)
    
    # Get key metrics
    confidence = root_cause_results.get("confidence", 0.0)
    anomalies_found = log_results.get("anomalies_found", False)
    similar_incidents = knowledge_results.get("total_matches", 0) > 0
    
    # Decision logic
    decision = "auto_mitigation"
    escalation_reason = ""
    
    # Check escalation conditions
    if retry_count >= MAX_RETRIES:
        decision = "escalation"
        escalation_reason = f"Max retries ({MAX_RETRIES}) reached without finding anomalies"
    elif not anomalies_found:
        decision = "escalation"
        escalation_reason = "No anomalies detected in log analysis"
    elif confidence < CONFIDENCE_THRESHOLD:
        decision = "escalation"
        escalation_reason = f"Low confidence ({confidence:.2f}) in root cause analysis"
    elif not similar_incidents:
        decision = "escalation"
        escalation_reason = "No similar historical incidents found for guidance"
    
    # Log decision
    if decision == "auto_mitigation":
        logger.info(f"HIGH CONFIDENCE ({confidence:.2f}) - Auto-mitigation approved")
    else:
        logger.warning(f"ESCALATING - {escalation_reason}")
    
    # Calculate decision metrics
    metrics = {
        "confidence": confidence,
        "anomalies_found": anomalies_found,
        "similar_incidents_count": knowledge_results.get("total_matches", 0),
        "retry_count": retry_count,
        "escalation_reason": escalation_reason
    }
    
    # Return ONLY decision data
    # NO routing, NO orchestration
    return {
        "decision": decision,
        "decision_metrics": metrics,
        "escalation_reason": escalation_reason
    }
