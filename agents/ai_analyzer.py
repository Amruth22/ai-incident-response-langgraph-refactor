"""
AI Analyzer - Pure Tool
Performs AI-powered analysis using Gemini
NO state management, NO orchestration logic
"""

import logging
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from config import get_config_value

logger = logging.getLogger("ai_analyzer")


class AIAnalyzer:
    """Pure AI analysis tool - reusable across workflows"""
    
    def __init__(self):
        api_key = get_config_value("GEMINI_API_KEY", "")
        model_name = get_config_value("GEMINI_MODEL", "gemini-2.0-flash")
        
        if not api_key:
            logger.warning("Gemini API key not configured")
            self.model = None
        else:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model_name)
                logger.info(f"Gemini client initialized with model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.model = None
    
    def parse_incident_alert(self, raw_alert: str) -> Dict[str, Any]:
        """
        Parse unstructured incident alert into structured data
        
        Args:
            raw_alert: Raw alert text
            
        Returns:
            Dictionary with parsed incident data (NO orchestration fields)
        """
        if not self.model:
            return self._default_parse(raw_alert)
        
        try:
            prompt = f"""Parse this incident alert and extract structured information.

Alert: {raw_alert}

Provide:
1. Service name (e.g., "Payment API", "Auth Service")
2. Severity level (HIGH, MEDIUM, LOW)
3. Brief description (1-2 sentences)

Format your response as:
Service: <service_name>
Severity: <severity_level>
Description: <description>
"""
            
            response = self.model.generate_content(prompt)
            text = response.text if hasattr(response, 'text') else str(response)
            
            # Parse response
            parsed = self._parse_ai_response(text)
            
            return {
                'service': parsed.get('service', 'Unknown Service'),
                'severity': parsed.get('severity', 'MEDIUM'),
                'description': parsed.get('description', raw_alert[:100])
            }
            
        except Exception as e:
            logger.error(f"AI parsing error: {e}")
            return self._default_parse(raw_alert)
    
    def analyze_root_cause(self, service: str, description: str, 
                          log_results: Dict[str, Any], 
                          knowledge_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform AI-powered root cause analysis
        
        Args:
            service: Service name
            description: Incident description
            log_results: Results from log analysis
            knowledge_results: Results from knowledge lookup
            
        Returns:
            Dictionary with root cause analysis (NO orchestration fields)
        """
        if not self.model:
            return self._default_root_cause(service)
        
        try:
            # Build context from other analyses
            context = self._build_context(log_results, knowledge_results)
            
            prompt = f"""Analyze this incident and determine the root cause.

Service: {service}
Description: {description}

Context:
{context}

Provide:
1. Root cause hypothesis
2. Confidence level (0.0 to 1.0)
3. Contributing factors
4. Recommended solution
5. Estimated resolution time

Be specific and actionable.
"""
            
            response = self.model.generate_content(prompt)
            text = response.text if hasattr(response, 'text') else str(response)
            
            # Parse response
            analysis = self._parse_root_cause_response(text)
            
            return {
                'root_cause': analysis.get('root_cause', 'Unknown'),
                'confidence': analysis.get('confidence', 0.7),
                'contributing_factors': analysis.get('contributing_factors', []),
                'recommended_solution': analysis.get('solution', 'Manual investigation required'),
                'urgency': analysis.get('urgency', 'MEDIUM'),
                'estimated_resolution_time': analysis.get('resolution_time', '30 minutes')
            }
            
        except Exception as e:
            logger.error(f"AI root cause analysis error: {e}")
            return self._default_root_cause(service)
    
    def _build_context(self, log_results: Dict, knowledge_results: Dict) -> str:
        """Build context string from other analyses"""
        context_parts = []
        
        # Log analysis context
        anomalies = log_results.get('anomalies', [])
        if anomalies:
            context_parts.append(f"Anomalies detected: {len(anomalies)}")
            for anomaly in anomalies[:2]:
                context_parts.append(f"  - {anomaly.get('type', 'unknown')}: {anomaly.get('pattern', '')}")
        
        # Knowledge base context
        similar = knowledge_results.get('similar_incidents', [])
        if similar:
            context_parts.append(f"\nSimilar past incidents: {len(similar)}")
            for incident in similar[:2]:
                context_parts.append(f"  - {incident.get('root_cause', 'unknown')}")
        
        return '\n'.join(context_parts) if context_parts else "No additional context available"
    
    def _parse_ai_response(self, text: str) -> Dict[str, Any]:
        """Parse AI response for incident parsing"""
        parsed = {}
        
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('Service:'):
                parsed['service'] = line.split(':', 1)[1].strip()
            elif line.startswith('Severity:'):
                parsed['severity'] = line.split(':', 1)[1].strip().upper()
            elif line.startswith('Description:'):
                parsed['description'] = line.split(':', 1)[1].strip()
        
        return parsed
    
    def _parse_root_cause_response(self, text: str) -> Dict[str, Any]:
        """Parse AI response for root cause analysis"""
        # Simple parsing (in production, would be more sophisticated)
        analysis = {
            'root_cause': 'Unknown root cause',
            'confidence': 0.7,
            'contributing_factors': [],
            'solution': 'Manual investigation required',
            'urgency': 'MEDIUM',
            'resolution_time': '30 minutes'
        }
        
        # Extract confidence if mentioned
        import re
        confidence_match = re.search(r'confidence[:\s]+(\d+\.?\d*)', text, re.IGNORECASE)
        if confidence_match:
            try:
                conf = float(confidence_match.group(1))
                if conf > 1:
                    conf = conf / 100  # Convert percentage
                analysis['confidence'] = min(1.0, max(0.0, conf))
            except ValueError:
                pass
        
        # Extract root cause (first substantial line)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            analysis['root_cause'] = lines[0][:200]  # Limit length
        
        return analysis
    
    def _default_parse(self, raw_alert: str) -> Dict[str, Any]:
        """Default parsing when AI is unavailable"""
        # Simple keyword extraction
        service = 'Unknown Service'
        severity = 'MEDIUM'
        
        if 'payment' in raw_alert.lower():
            service = 'Payment API'
        elif 'auth' in raw_alert.lower():
            service = 'Auth Service'
        elif 'database' in raw_alert.lower():
            service = 'Database'
        
        if 'critical' in raw_alert.lower() or 'high' in raw_alert.lower():
            severity = 'HIGH'
        elif 'low' in raw_alert.lower():
            severity = 'LOW'
        
        return {
            'service': service,
            'severity': severity,
            'description': raw_alert[:200]
        }
    
    def _default_root_cause(self, service: str) -> Dict[str, Any]:
        """Default root cause when AI is unavailable"""
        return {
            'root_cause': f'Unknown root cause for {service}',
            'confidence': 0.5,
            'contributing_factors': ['AI analysis unavailable'],
            'recommended_solution': 'Manual investigation required',
            'urgency': 'MEDIUM',
            'estimated_resolution_time': '30 minutes'
        }
