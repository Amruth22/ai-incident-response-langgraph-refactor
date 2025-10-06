"""
AI-Powered Incident Response System - LangGraph Refactored
Main entry point for the application
"""

import sys
import argparse
import logging
from datetime import datetime

from config import validate_config, get_config_value
from graph import execute_incident_workflow
from utils.logging_utils import setup_logging


def main():
    """Main application entry point"""
    # Setup logging
    log_file = get_config_value("LOG_FILE", "logs/incident_response.log")
    log_level = get_config_value("LOG_LEVEL", "INFO")
    setup_logging(log_level, log_file)
    
    logger = logging.getLogger("main")
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="AI-Powered Incident Response System - LangGraph Multi-Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Payment API database timeout"
  python main.py --demo
        """
    )
    
    parser.add_argument(
        "--demo", "-d",
        action="store_true",
        help="Run interactive demo with sample scenarios"
    )
    
    parser.add_argument(
        "alert",
        nargs="*",
        help="Incident alert text to process"
    )
    
    args = parser.parse_args()
    
    try:
        # Validate configuration
        validate_config()
        print("Configuration validated successfully")
    except ValueError as e:
        print(f"ERROR: Configuration Error: {e}")
        print("\nSetup Instructions:")
        print("1. Copy .env.example to .env")
        print("2. Update .env with your actual credentials")
        print("3. Run the application again")
        sys.exit(1)
    
    # Handle different modes
    if args.demo:
        run_demo()
    elif args.alert:
        alert_text = " ".join(args.alert)
        run_incident_response(alert_text)
    else:
        # Interactive mode
        run_interactive_mode()


def run_incident_response(alert_text: str):
    """Run the incident response workflow"""
    print("\nTRUE PARALLEL MULTI-AGENT INCIDENT RESPONSE")
    print("=" * 50)
    start_time = datetime.now()
    
    try:
        result = execute_incident_workflow(alert_text)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\nWorkflow completed in {duration:.2f} seconds")
        print_workflow_summary(result)
        
    except Exception as e:
        print(f"ERROR: Workflow error: {e}")
        import traceback
        traceback.print_exc()


def run_demo():
    """Run interactive demo with sample scenarios"""
    print("\nINTERACTIVE DEMO - AI-Powered Incident Response")
    print("=" * 55)
    
    scenarios = [
        {
            "name": "Database Timeout",
            "alert": "Payment API experiencing database connection timeouts and high error rates",
            "description": "High confidence scenario - should auto-resolve"
        },
        {
            "name": "Memory Leak",
            "alert": "Auth Service showing memory leak patterns and degraded performance",
            "description": "Medium confidence scenario - may require escalation"
        },
        {
            "name": "Network Issues",
            "alert": "Load balancer reporting uneven traffic distribution and connection failures",
            "description": "Complex scenario - likely escalation"
        },
        {
            "name": "Unknown Service",
            "alert": "Critical system failure in unknown microservice with no clear symptoms",
            "description": "Low confidence scenario - definite escalation"
        }
    ]
    
    print("Available Demo Scenarios:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"  {i}. {scenario['name']} - {scenario['description']}")
    
    print("  5. Custom Alert - Enter your own incident")
    print("  0. Exit")
    
    while True:
        try:
            choice = input("\nSelect scenario (0-5): ").strip()
            
            if choice == "0":
                print("Demo completed!")
                break
            elif choice in ["1", "2", "3", "4"]:
                scenario = scenarios[int(choice) - 1]
                print(f"\nRunning scenario: {scenario['name']}")
                print(f"Alert: {scenario['alert']}")
                print("-" * 50)
                run_incident_response(scenario['alert'])
                    
            elif choice == "5":
                custom_alert = input("Enter custom incident alert: ").strip()
                if custom_alert:
                    run_incident_response(custom_alert)
                else:
                    print("ERROR: No alert provided")
                    
            else:
                print("ERROR: Invalid choice. Please select 0-5.")
                
        except KeyboardInterrupt:
            print("\nDemo interrupted!")
            break
        except Exception as e:
            print(f"ERROR: Demo error: {e}")


def run_interactive_mode():
    """Interactive mode for single incident processing"""
    print("\nAI-Powered Incident Response System")
    print("=" * 45)
    print("Options:")
    print("  1. Process Incident Alert")
    print("  2. Interactive Demo")
    print("  0. Exit")
    
    choice = input("\nSelect option (0-2): ").strip()
    
    if choice == "0":
        print("Goodbye!")
        return
    elif choice == "1":
        alert = input("Enter incident alert: ").strip()
        if alert:
            run_incident_response(alert)
        else:
            print("ERROR: No alert provided")
    elif choice == "2":
        run_demo()
    else:
        print("ERROR: Invalid choice")


def print_workflow_summary(result: dict):
    """Print a summary of workflow results"""
    print(f"\nWORKFLOW SUMMARY")
    print("-" * 40)
    print(f"Incident ID: {result.get('incident_id', 'Unknown')}")
    print(f"Service: {result.get('service', 'Unknown')}")
    print(f"Severity: {result.get('severity', 'Unknown')}")
    
    # Show decision
    decision = result.get('decision', 'unknown')
    print(f"Decision: {decision.upper()}")
    
    # Show metrics
    metrics = result.get("decision_metrics", {})
    if metrics:
        print(f"Confidence: {metrics.get('confidence', 0):.2f}")
        print(f"Anomalies Found: {metrics.get('anomalies_found', False)}")
        print(f"Similar Incidents: {metrics.get('similar_incidents_count', 0)}")
        
        if metrics.get("escalation_reason"):
            print(f"Escalation Reason: {metrics['escalation_reason']}")
    
    # Show final status
    final_report = result.get("final_report", {})
    if final_report:
        print(f"Final Status: {final_report.get('status', 'Unknown')}")
    
    print("-" * 40)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted!")
    except Exception as e:
        print(f"ERROR: Application error: {e}")
        sys.exit(1)
