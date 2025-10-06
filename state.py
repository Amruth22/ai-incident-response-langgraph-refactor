"""
State Schema for Incident Response Workflow
Pure data structure - NO business logic, NO orchestration logic
"""

from typing import TypedDict, List, Dict, Any, Annotated


def merge_lists(existing: List, new: List) -> List:
    """Reducer function for merging lists in parallel updates"""
    if existing is None:
        existing = []
    if new is None:
        new = []
    return existing + new


class IncidentState(TypedDict, total=False):
    """
    State schema for incident response workflow
    
    This is ONLY a data structure definition.
    All business logic lives in nodes/
    All orchestration logic lives in graph.py
    """
    
    # Basic incident information
    incident_id: str
    raw_alert: str
    timestamp: str
    
    # Parsed incident details
    service: str
    severity: str
    description: str
    
    # Analysis results (populated by nodes)
    log_analysis_results: Dict[str, Any]
    knowledge_lookup_results: Dict[str, Any]
    root_cause_results: Dict[str, Any]
    
    # Mitigation/Escalation results
    mitigation_results: Dict[str, Any]
    escalation_results: Dict[str, Any]
    
    # Coordination data
    coordination_summary: Dict[str, Any]
    
    # Decision results (populated by decision node)
    decision: str
    decision_metrics: Dict[str, Any]
    escalation_reason: str
    
    # Agent completion tracking (managed by graph, not nodes)
    agents_completed: Annotated[List[str], merge_lists]
    agent_errors: Annotated[List[Dict[str, Any]], merge_lists]
    
    # Email tracking
    emails_sent: Annotated[List[Dict[str, Any]], merge_lists]
    
    # Workflow control (managed by graph)
    retry_count: int
    error: str
    workflow_complete: bool
    updated_at: str
