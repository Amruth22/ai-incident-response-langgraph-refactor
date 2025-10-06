"""
Coordinator Node - Pure Business Logic
Aggregates results from all analysis nodes
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger("coordinator_node")


def coordinator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregate results from all analysis nodes
    
    Pure business logic - NO orchestration
    Just prepares aggregated data for decision making
    """
    logger.info("Coordinating results from all analysis nodes")
    
    # Extract results
    log_results = state.get("log_analysis_results", {})
    knowledge_results = state.get("knowledge_lookup_results", {})
    root_cause_results = state.get("root_cause_results", {})
    
    # Count results
    anomalies_count = len(log_results.get("anomalies", []))
    similar_incidents_count = knowledge_results.get("total_matches", 0)
    confidence = root_cause_results.get("confidence", 0.0)
    
    logger.info(f"Results collected:")
    logger.info(f"  Anomalies: {anomalies_count}")
    logger.info(f"  Similar Incidents: {similar_incidents_count}")
    logger.info(f"  AI Confidence: {confidence:.2f}")
    
    # Calculate summary
    summary = {
        "total_anomalies": anomalies_count,
        "similar_incidents_count": similar_incidents_count,
        "ai_confidence": confidence,
        "analyses_completed": []
    }
    
    # Track which analyses completed
    if log_results:
        summary["analyses_completed"].append("log_analysis")
    if knowledge_results:
        summary["analyses_completed"].append("knowledge_lookup")
    if root_cause_results:
        summary["analyses_completed"].append("root_cause")
    
    logger.info("Coordination complete - ready for decision making")
    
    # Return ONLY business data
    # NO routing decisions, NO completion tracking
    return {
        "coordination_summary": summary,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
