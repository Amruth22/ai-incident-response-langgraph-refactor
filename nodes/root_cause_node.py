"""
Root Cause Node - Pure Business Logic
Performs AI-powered root cause analysis
"""

import logging
from typing import Dict, Any
from agents.ai_analyzer import AIAnalyzer
from agents.email_notifier import EmailNotifier

logger = logging.getLogger("root_cause_node")


def root_cause_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform AI-powered root cause analysis
    
    Pure business logic - NO orchestration
    Returns ONLY business data
    """
    service = state.get("service", "Unknown Service")
    description = state.get("description", "")
    incident_id = state.get("incident_id", "")
    
    # Get context from other analyses
    log_results = state.get("log_analysis_results", {})
    knowledge_results = state.get("knowledge_lookup_results", {})
    
    logger.info(f"Performing root cause analysis for {service}")
    
    # Use AI analyzer (thin tool)
    ai_analyzer = AIAnalyzer()
    results = ai_analyzer.analyze_root_cause(service, description, log_results, knowledge_results)
    
    confidence = results.get('confidence', 0.0)
    root_cause = results.get('root_cause', 'Unknown')
    
    logger.info(f"Root cause analysis complete: Confidence {confidence:.2f}")
    
    # Send email notification
    try:
        email_notifier = EmailNotifier()
        email_notifier.send_root_cause_update(
            incident_id,
            root_cause,
            confidence,
            results.get('recommended_solution', '')
        )
    except Exception as e:
        logger.warning(f"Failed to send email: {e}")
    
    # Return ONLY business data
    # NO agents_completed, NO next, NO stage
    return {
        "root_cause_results": results
    }
