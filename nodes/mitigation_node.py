"""
Mitigation Node - Pure Business Logic
Executes automated mitigation actions
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from agents.email_notifier import EmailNotifier

logger = logging.getLogger("mitigation_node")


def mitigation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute automated mitigation actions
    
    Pure business logic - NO orchestration
    Returns ONLY mitigation data
    """
    incident_id = state.get("incident_id", "")
    service = state.get("service", "Unknown Service")
    root_cause_results = state.get("root_cause_results", {})
    
    logger.info(f"Executing automated mitigation for {service}")
    
    # Get recommended solution
    solution = root_cause_results.get("recommended_solution", "Restart service")
    
    # Execute mitigation actions (simulated)
    actions_taken = _execute_mitigation_actions(service, solution)
    
    # Verify mitigation success (simulated)
    execution_status = "SUCCESS"
    verification_checks = {
        "service_health": "HEALTHY",
        "error_rate": "NORMAL",
        "response_time": "OPTIMAL"
    }
    
    logger.info(f"Mitigation executed: {execution_status}")
    
    # Send mitigation report email
    try:
        email_notifier = EmailNotifier()
        email_notifier.send_mitigation_report(incident_id, actions_taken, execution_status)
    except Exception as e:
        logger.warning(f"Failed to send email: {e}")
    
    # Return ONLY mitigation data
    # NO workflow_complete flag - graph handles that
    return {
        "mitigation_results": {
            "actions_taken": actions_taken,
            "execution_status": execution_status,
            "resolution_time": "12 minutes",
            "verification_checks": verification_checks
        },
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def _execute_mitigation_actions(service: str, solution: str) -> List[str]:
    """Execute mitigation actions based on solution"""
    actions = []
    
    # Parse solution and generate actions
    if 'scale' in solution.lower() or 'pool' in solution.lower():
        actions.append(f"Scaled {service} connection pool from 50 to 100 connections")
    
    if 'restart' in solution.lower():
        actions.append(f"Restarted {service} service instances")
    
    if 'cache' in solution.lower():
        actions.append(f"Cleared {service} cache and implemented warming strategy")
    
    if 'index' in solution.lower():
        actions.append(f"Added database index for {service} queries")
    
    if 'circuit' in solution.lower() or 'breaker' in solution.lower():
        actions.append(f"Implemented circuit breaker pattern for {service}")
    
    # Default action if no specific actions identified
    if not actions:
        actions.append(f"Applied recommended solution: {solution[:100]}")
        actions.append(f"Restarted {service} service")
    
    return actions
