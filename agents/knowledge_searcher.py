"""
Knowledge Searcher - Pure Tool
Searches historical incidents for similar patterns
NO state management, NO orchestration logic
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("knowledge_searcher")


class KnowledgeSearcher:
    """Pure knowledge search tool - reusable across workflows"""
    
    def __init__(self):
        self.past_incidents = self._load_knowledge_base()
    
    def search_similar_incidents(self, service: str, description: str, anomalies: List[Dict]) -> Dict[str, Any]:
        """
        Search for similar historical incidents
        
        Args:
            service: Service name
            description: Incident description
            anomalies: List of detected anomalies
            
        Returns:
            Dictionary with similar incidents data (NO orchestration fields)
        """
        logger.info(f"Searching knowledge base for {service}")
        
        # Find similar incidents
        similar = self._find_similar(service, description, anomalies)
        
        # Extract recommended solutions
        recommended_solutions = self._extract_solutions(similar)
        
        # Calculate confidence
        confidence = self._calculate_confidence(similar)
        
        return {
            'similar_incidents': similar,
            'total_matches': len(similar),
            'confidence': confidence,
            'recommended_solutions': recommended_solutions
        }
    
    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """Load historical incidents from knowledge base"""
        return [
            {
                'incident_id': 'INC-001',
                'service': 'Payment API',
                'anomaly': 'Database connection timeout',
                'root_cause': 'Traffic spike exceeded connection pool limits',
                'solution': 'Scale database connection pool from 50 to 100, restart service',
                'keywords': ['database', 'timeout', 'connection', 'pool']
            },
            {
                'incident_id': 'INC-002',
                'service': 'Auth Service',
                'anomaly': 'Memory leak',
                'root_cause': 'Session objects not being garbage collected',
                'solution': 'Deploy memory leak fix, restart service instances',
                'keywords': ['memory', 'leak', 'session', 'garbage']
            },
            {
                'incident_id': 'INC-003',
                'service': 'Payment API',
                'anomaly': 'High error rate',
                'root_cause': 'Database query timeout due to missing index',
                'solution': 'Add database index, optimize queries',
                'keywords': ['error', 'database', 'query', 'timeout']
            },
            {
                'incident_id': 'INC-004',
                'service': 'Load Balancer',
                'anomaly': 'Uneven traffic distribution',
                'root_cause': 'Sticky session configuration issue',
                'solution': 'Reconfigure load balancer session affinity',
                'keywords': ['load', 'balancer', 'traffic', 'distribution']
            },
            {
                'incident_id': 'INC-005',
                'service': 'Auth Service',
                'anomaly': 'Slow response time',
                'root_cause': 'Cache invalidation storm',
                'solution': 'Implement cache warming strategy',
                'keywords': ['cache', 'slow', 'response', 'performance']
            },
            {
                'incident_id': 'INC-006',
                'service': 'Payment API',
                'anomaly': 'Connection pool exhaustion',
                'root_cause': 'Connection leak in payment processor',
                'solution': 'Fix connection leak, increase pool size',
                'keywords': ['connection', 'pool', 'exhaustion', 'leak']
            },
            {
                'incident_id': 'INC-007',
                'service': 'API Gateway',
                'anomaly': 'Rate limit exceeded',
                'root_cause': 'DDoS attack from single IP range',
                'solution': 'Block malicious IPs, increase rate limits',
                'keywords': ['rate', 'limit', 'ddos', 'attack']
            },
            {
                'incident_id': 'INC-008',
                'service': 'Database',
                'anomaly': 'Replication lag',
                'root_cause': 'Large batch update blocking replication',
                'solution': 'Optimize batch updates, increase replication capacity',
                'keywords': ['database', 'replication', 'lag', 'batch']
            }
        ]
    
    def _find_similar(self, service: str, description: str, anomalies: List[Dict]) -> List[Dict[str, Any]]:
        """Find similar incidents using keyword matching"""
        similar = []
        
        # Extract keywords from current incident
        current_keywords = set(description.lower().split())
        current_keywords.add(service.lower())
        
        # Add anomaly types as keywords
        for anomaly in anomalies:
            anomaly_type = anomaly.get('type', '').replace('_', ' ')
            current_keywords.update(anomaly_type.split())
        
        # Match against historical incidents
        for incident in self.past_incidents:
            # Calculate similarity score
            incident_keywords = set(incident['keywords'])
            matched_keywords = current_keywords & incident_keywords
            
            if matched_keywords:
                similarity_score = len(matched_keywords) / len(incident_keywords)
                
                # Include if similarity > 0.3
                if similarity_score > 0.3:
                    similar.append({
                        'incident_id': incident['incident_id'],
                        'service': incident['service'],
                        'similarity_score': round(similarity_score, 2),
                        'root_cause': incident['root_cause'],
                        'solution': incident['solution'],
                        'keywords_matched': list(matched_keywords)
                    })
        
        # Sort by similarity score
        similar.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similar[:5]  # Return top 5
    
    def _extract_solutions(self, similar_incidents: List[Dict]) -> List[str]:
        """Extract recommended solutions from similar incidents"""
        solutions = []
        
        for incident in similar_incidents[:3]:  # Top 3
            solution = incident.get('solution', '')
            if solution and solution not in solutions:
                solutions.append(solution)
        
        return solutions
    
    def _calculate_confidence(self, similar_incidents: List[Dict]) -> float:
        """Calculate confidence based on similarity scores"""
        if not similar_incidents:
            return 0.0
        
        # Average of top 3 similarity scores
        top_scores = [inc['similarity_score'] for inc in similar_incidents[:3]]
        return round(sum(top_scores) / len(top_scores), 2)
