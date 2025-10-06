"""
Log Analysis Node - Pure Business Logic
Analyzes system logs for anomalies
"""

import logging
from typing import Dict, Any
from agents.log_analyzer import LogAnalyzer
from agents.email_notifier import EmailNotifier

logger = logging.getLogger("log_analysis_node")


def log_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze system logs for anomalies
    
    Pure business logic - NO orchestration
    Returns ONLY business data
    """
    service = state.get("service", "Unknown Service")
    description = state.get("description", "")
    incident_id = state.get("incident_id", "")
    
    logger.info(f"Analyzing logs for {service}")
    
    # Use log analyzer (thin tool)
    analyzer = LogAnalyzer()
    results = analyzer.analyze_logs(service, description)
    
    # Send email if anomalies found
    if results.get('anomalies_found'):
        try:
            email_notifier = EmailNotifier()
            anomaly_list = [a.get('pattern', '') for a in results.get('anomalies', [])]
            email_notifier.send_analysis_update(incident_id, anomaly_list)
        except Exception as e:
            logger.warning(f"Failed to send email: {e}")
    
    logger.info(f"Log analysis complete: {len(results.get('anomalies', []))} anomalies found")
    
    # Return ONLY business data
    # NO agents_completed, NO next, NO stage
    return {
        "log_analysis_results": results
    }
