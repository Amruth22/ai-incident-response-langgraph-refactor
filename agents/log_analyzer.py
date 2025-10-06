"""
Log Analyzer - Pure Tool
Analyzes system logs for anomalies
NO state management, NO orchestration logic
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger("log_analyzer")


class LogAnalyzer:
    """Pure log analysis tool - reusable across workflows"""
    
    def analyze_logs(self, service: str, description: str) -> Dict[str, Any]:
        """
        Analyze logs for anomalies
        
        Args:
            service: Service name
            description: Incident description
            
        Returns:
            Dictionary with log analysis data (NO orchestration fields)
        """
        logger.info(f"Analyzing logs for {service}")
        
        # Simulate log analysis (in production, would query actual log systems)
        anomalies = self._detect_anomalies(service, description)
        
        # Generate log patterns
        log_patterns = self._generate_log_patterns(service, anomalies)
        
        # Calculate confidence
        analysis_confidence = 0.85 if anomalies else 0.3
        
        return {
            'service': service,
            'anomalies': anomalies,
            'anomalies_found': len(anomalies) > 0,
            'log_patterns': log_patterns,
            'analysis_confidence': analysis_confidence,
            'analysis_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _detect_anomalies(self, service: str, description: str) -> List[Dict[str, Any]]:
        """Detect anomalies based on service and description"""
        anomalies = []
        
        # Pattern matching for common issues
        if 'timeout' in description.lower() or 'database' in description.lower():
            anomalies.append({
                'type': 'database_timeout',
                'severity': 'HIGH',
                'pattern': 'Connection timeout after 30s',
                'frequency': 15,
                'time_range': '10:25-10:30'
            })
        
        if 'memory' in description.lower() or 'leak' in description.lower():
            anomalies.append({
                'type': 'memory_leak',
                'severity': 'HIGH',
                'pattern': 'Memory usage increasing continuously',
                'frequency': 8,
                'time_range': '10:20-10:30'
            })
        
        if 'error' in description.lower() or 'failure' in description.lower():
            anomalies.append({
                'type': 'error_spike',
                'severity': 'MEDIUM',
                'pattern': 'Error rate above threshold',
                'frequency': 25,
                'time_range': '10:25-10:30'
            })
        
        if 'network' in description.lower() or 'connection' in description.lower():
            anomalies.append({
                'type': 'network_issue',
                'severity': 'MEDIUM',
                'pattern': 'Connection failures detected',
                'frequency': 12,
                'time_range': '10:28-10:30'
            })
        
        return anomalies
    
    def _generate_log_patterns(self, service: str, anomalies: List[Dict]) -> List[str]:
        """Generate realistic log patterns"""
        patterns = []
        
        for anomaly in anomalies:
            anomaly_type = anomaly.get('type', '')
            
            if anomaly_type == 'database_timeout':
                patterns.append(f"ERROR: {service} - Connection timeout after 30s")
                patterns.append(f"WARN: {service} - Connection pool exhausted")
            elif anomaly_type == 'memory_leak':
                patterns.append(f"WARN: {service} - Memory usage at 95%")
                patterns.append(f"ERROR: {service} - OutOfMemoryError")
            elif anomaly_type == 'error_spike':
                patterns.append(f"ERROR: {service} - Request failed with 500")
                patterns.append(f"ERROR: {service} - Internal server error")
            elif anomaly_type == 'network_issue':
                patterns.append(f"ERROR: {service} - Connection refused")
                patterns.append(f"WARN: {service} - Network timeout")
        
        return patterns[:5]  # Limit to top 5
