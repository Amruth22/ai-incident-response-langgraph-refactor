"""
Incident Trigger Node - Pure Business Logic
Parses unstructured alerts into structured data
"""

import logging
from typing import Dict, Any
from datetime import datetime
from agents.ai_analyzer import AIAnalyzer
from agents.email_notifier import EmailNotifier

logger = logging.getLogger("incident_trigger_node")


def incident_trigger_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse incident alert and initialize response
    
    Pure business logic - NO orchestration
    Returns ONLY business data
    """
    raw_alert = state.get("raw_alert", "")
    incident_id = state.get("incident_id", "")
    
    logger.info(f"Parsing incident alert: {incident_id}")
    
    # Use AI analyzer to parse alert
    ai_analyzer = AIAnalyzer()
    parsed = ai_analyzer.parse_incident_alert(raw_alert)
    
    service = parsed.get('service', 'Unknown Service')
    severity = parsed.get('severity', 'MEDIUM')
    description = parsed.get('description', raw_alert[:100])
    
    logger.info(f"Parsed - Service: {service}, Severity: {severity}")
    
    # Send initial alert email
    try:
        email_notifier = EmailNotifier()
        email_notifier.send_incident_alert(incident_id, service, severity, description)
    except Exception as e:
        logger.warning(f"Failed to send email: {e}")
    
    # Return ONLY business data - no orchestration fields
    return {
        "service": service,
        "severity": severity,
        "description": description,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
