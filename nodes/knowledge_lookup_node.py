"""
Knowledge Lookup Node - Pure Business Logic
Searches historical incidents for similar patterns
"""

import logging
from typing import Dict, Any
from agents.knowledge_searcher import KnowledgeSearcher

logger = logging.getLogger("knowledge_lookup_node")


def knowledge_lookup_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search historical incidents for similar patterns
    
    Pure business logic - NO orchestration
    Returns ONLY business data
    """
    service = state.get("service", "Unknown Service")
    description = state.get("description", "")
    
    # Get anomalies from log analysis (if available)
    log_results = state.get("log_analysis_results", {})
    anomalies = log_results.get("anomalies", [])
    
    logger.info(f"Searching knowledge base for {service}")
    
    # Use knowledge searcher (thin tool)
    searcher = KnowledgeSearcher()
    results = searcher.search_similar_incidents(service, description, anomalies)
    
    similar_count = results.get('total_matches', 0)
    logger.info(f"Knowledge lookup complete: {similar_count} similar incidents found")
    
    # Return ONLY business data
    # NO agents_completed, NO next, NO stage
    return {
        "knowledge_lookup_results": results
    }
