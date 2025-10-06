"""
Email Notifier - Pure Tool
Sends email notifications
NO state management, NO orchestration logic
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from config import get_config_value

logger = logging.getLogger("email_notifier")


class EmailNotifier:
    """Pure email notification tool - reusable across workflows"""
    
    def __init__(self):
        self.email_from = get_config_value("EMAIL_FROM", "")
        self.email_password = get_config_value("EMAIL_PASSWORD", "")
        self.email_to = get_config_value("EMAIL_TO", "")
        self.smtp_server = get_config_value("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(get_config_value("SMTP_PORT", 587))
        
        if not all([self.email_from, self.email_password, self.email_to]):
            logger.warning("Email configuration incomplete - notifications disabled")
    
    def send_email(self, subject: str, content: str) -> bool:
        """Send email notification"""
        if not all([self.email_from, self.email_password, self.email_to]):
            logger.warning("Email not configured - skipping notification")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(content, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_incident_alert(self, incident_id: str, service: str, severity: str, description: str) -> bool:
        """Send incident alert notification"""
        subject = f"INCIDENT ALERT: {incident_id} - {service}"
        
        content = f"""
INCIDENT DETECTED
=================

Incident ID: {incident_id}
Service: {service}
Severity: {severity}

Description:
{description}

The AI-Powered Incident Response System is analyzing this incident.
You will receive updates as the analysis progresses.

This is an automated notification.
"""
        
        return self.send_email(subject, content)
    
    def send_analysis_update(self, incident_id: str, anomalies: List[str]) -> bool:
        """Send log analysis update"""
        subject = f"LOG ANALYSIS: {incident_id}"
        
        content = f"""
LOG ANALYSIS COMPLETE
====================

Incident ID: {incident_id}

Anomalies Detected:
{chr(10).join(f'  - {anomaly}' for anomaly in anomalies[:5])}

Root cause analysis is in progress.

This is an automated notification.
"""
        
        return self.send_email(subject, content)
    
    def send_root_cause_update(self, incident_id: str, root_cause: str, confidence: float, solution: str) -> bool:
        """Send root cause analysis update"""
        subject = f"ROOT CAUSE ANALYSIS: {incident_id}"
        
        content = f"""
ROOT CAUSE ANALYSIS COMPLETE
============================

Incident ID: {incident_id}

Root Cause:
{root_cause}

Confidence: {confidence:.0%}

Recommended Solution:
{solution}

Decision making in progress.

This is an automated notification.
"""
        
        return self.send_email(subject, content)
    
    def send_mitigation_report(self, incident_id: str, actions: List[str], status: str) -> bool:
        """Send mitigation execution report"""
        subject = f"MITIGATION COMPLETE: {incident_id}"
        
        content = f"""
AUTOMATED MITIGATION EXECUTED
=============================

Incident ID: {incident_id}
Status: {status}

Actions Taken:
{chr(10).join(f'  - {action}' for action in actions)}

Incident has been automatically resolved.

This is an automated notification.
"""
        
        return self.send_email(subject, content)
    
    def send_escalation_alert(self, incident_id: str, reason: str, context: Dict[str, Any]) -> bool:
        """Send escalation alert"""
        subject = f"ESCALATION REQUIRED: {incident_id}"
        
        content = f"""
HUMAN INTERVENTION REQUIRED
===========================

Incident ID: {incident_id}

Escalation Reason:
{reason}

Context:
  Service: {context.get('service', 'Unknown')}
  Severity: {context.get('severity', 'Unknown')}
  Confidence: {context.get('confidence', 0):.0%}

Please review and take appropriate action.

This is an automated notification.
"""
        
        return self.send_email(subject, content)
