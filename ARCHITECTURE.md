# Architecture Documentation

## AI-Powered Incident Response System - LangGraph Refactored

This document describes the LangGraph-compliant architecture with proper separation of concerns.

---

## Design Principles

### 1. Separation of Concerns

The system is built on three distinct layers:

```
ORCHESTRATION LAYER (graph.py)
    ↓
BUSINESS LOGIC LAYER (nodes/)
    ↓
TOOL LAYER (agents/)
```

### 2. Single Responsibility Principle

Each component has ONE job:

| Component | Responsibility | Does NOT Do |
|-----------|---------------|-------------|
| **graph.py** | Orchestrate workflow | Analyze logs |
| **nodes/** | Process data | Manage routing |
| **agents/** | Analyze data | Track state |
| **state.py** | Define schema | Execute logic |

### 3. Pure Functions

All nodes are pure functions:
- **Input**: State dictionary
- **Output**: Dictionary with business data only
- **No side effects** (except external service calls)
- **No orchestration logic**

### 4. Thin, Reusable Agents

Agents are tools, not controllers:
- No state management
- No workflow knowledge
- No completion tracking
- Can be used in any workflow

---

## Component Architecture

### 1. State Management (state.py)

**Purpose**: Define data structure ONLY

```python
class IncidentState(TypedDict, total=False):
    # Basic info
    incident_id: str
    raw_alert: str
    service: str
    
    # Analysis results
    log_analysis_results: Dict[str, Any]
    knowledge_lookup_results: Dict[str, Any]
    root_cause_results: Dict[str, Any]
    
    # Decision data
    decision: str
    decision_metrics: Dict[str, Any]
```

**Key Features**:
- Pure data structure
- Type definitions
- Reducer functions for parallel updates
- NO business logic
- NO orchestration logic

### 2. Graph Orchestration (graph.py)

**Purpose**: Define workflow structure and routing

```python
def create_incident_workflow():
    workflow = StateGraph(IncidentState)
    
    # Add nodes
    workflow.add_node("log_analysis", log_analysis_node)
    workflow.add_node("knowledge_lookup", knowledge_lookup_node)
    
    # Define routing
    workflow.add_conditional_edges("trigger", route_to_parallel)
    workflow.add_edge("log_analysis", "coordinator")
    
    return workflow.compile()
```

**Key Features**:
- Defines node connections
- Manages routing logic
- Tracks completion
- Handles errors
- NO business logic
- NO data processing

**Routing Functions**:

```python
def route_after_trigger(state: IncidentState) -> List[str]:
    """Graph decides what runs next"""
    if state.get("error"):
        return [END]
    
    # Launch parallel analyses
    return ["log_analysis", "knowledge_lookup", "root_cause"]
```

### 3. Business Logic Nodes (nodes/)

**Purpose**: Perform specific analysis tasks

**Pattern**:
```python
def log_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Pure business logic - NO orchestration"""
    
    # Get data from state
    service = state.get("service")
    description = state.get("description")
    
    # Use thin agent/tool
    analyzer = LogAnalyzer()
    
    # Process data
    results = analyzer.analyze_logs(service, description)
    
    # Return ONLY business data
    return {"log_analysis_results": results}
    # NO agents_completed
    # NO next
    # NO stage
```

**Key Features**:
- Pure function
- Receives state
- Calls thin agents
- Returns data only
- NO completion tracking
- NO routing decisions
- NO state management

**Node Catalog**:

| Node | Purpose | Agent Used |
|------|---------|-----------|
| `incident_trigger_node` | Parse alert | AIAnalyzer |
| `log_analysis_node` | Detect anomalies | LogAnalyzer |
| `knowledge_lookup_node` | Search history | KnowledgeSearcher |
| `root_cause_node` | AI analysis | AIAnalyzer |
| `coordinator_node` | Aggregate results | None |
| `decision_node` | Make decision | None |
| `mitigation_node` | Execute solution | EmailNotifier |
| `escalation_node` | Escalate to humans | EmailNotifier |
| `communicator_node` | Final report | None |

### 4. Thin Agents (agents/)

**Purpose**: Reusable analysis tools

**Pattern**:
```python
class LogAnalyzer:
    """Pure analyzer - NO state management"""
    
    def analyze_logs(self, service: str, description: str) -> Dict[str, Any]:
        """Analyze logs - return data only"""
        anomalies = []
        
        # Analysis logic
        anomalies = self._detect_anomalies(service, description)
        
        # Return ONLY analysis data
        return {
            'service': service,
            'anomalies': anomalies,
            'anomalies_found': len(anomalies) > 0
        }
        # NO state updates
        # NO workflow knowledge
```

**Key Features**:
- Pure analyzer
- Reusable across workflows
- No dependencies on workflow
- NO state management
- NO orchestration
- NO completion tracking

**Agent Catalog**:

| Agent | Purpose | Output |
|-------|---------|--------|
| `LogAnalyzer` | Detect log anomalies | Anomaly list + confidence |
| `KnowledgeSearcher` | Search history | Similar incidents + solutions |
| `AIAnalyzer` | AI-powered analysis | Root cause + confidence |
| `EmailNotifier` | Send notifications | Email status |

---

## Workflow Execution Flow

### Visual Workflow Diagram

```mermaid
graph TD
    %% Entry Point
    START([🚀 Incident Alert Received]) --> TRIGGER[🔔 Incident Trigger Agent]
    
    %% Incident Parsing and Setup
    TRIGGER --> |"AI-Powered Alert Parsing<br/>Extract Service & Severity<br/>Send Initial Alert Email"| PARALLEL{"🎯 Launch Parallel Analysis"}
    
    %% TRUE Parallel Agent Execution (All 3 agents run simultaneously)
    PARALLEL --> |"Simultaneously"| LOG_ANALYSIS[📊 Log Analysis Agent]
    PARALLEL --> |"Simultaneously"| KNOWLEDGE[📚 Knowledge Lookup Agent]
    PARALLEL --> |"Simultaneously"| ROOT_CAUSE[🔍 Root Cause Agent]
    
    %% Agent Specializations and Results
    LOG_ANALYSIS --> |"Detect Anomalies<br/>Pattern Matching<br/>Retry Logic (Max 3)"| LOG_RESULT[📊 Log Analysis Results<br/>Anomalies: Found/Not Found<br/>Patterns: CPU, Memory, Network<br/>Retry Count: 0-3]
    
    KNOWLEDGE --> |"Search Historical DB<br/>8 Past Incidents<br/>Solution Matching"| KNOWLEDGE_RESULT[📚 Knowledge Results<br/>Similar Incidents: 0-8<br/>Solutions Found: Yes/No<br/>Confidence: 0.0-1.0]
    
    ROOT_CAUSE --> |"Gemini AI Analysis<br/>Context Integration<br/>Confidence Scoring"| ROOT_RESULT[🔍 Root Cause Results<br/>Root Cause: Identified<br/>Confidence: 0.0-1.0<br/>Recommendations: List]
    
    %% Agent Coordination
    LOG_RESULT --> COORDINATOR[🎯 Agent Coordinator]
    KNOWLEDGE_RESULT --> COORDINATOR
    ROOT_RESULT --> COORDINATOR
    
    %% Coordination Logic
    COORDINATOR --> |"All 3 Agents Complete?"| CHECK{"✅ All Agents<br/>Completed?"}
    CHECK --> |"No - Wait"| WAIT[⏳ Wait for<br/>Remaining Agents]
    WAIT --> CHECK
    CHECK --> |"Yes - Proceed"| SUMMARY[📋 Generate<br/>Multi-Agent Summary]
    
    %% Decision Making with Multi-Factor Criteria
    SUMMARY --> DECISION{"⚖️ Decision Maker<br/>Multi-Factor Analysis"}
    
    %% Multi-Dimensional Decision Matrix
    DECISION --> |"Retry Count ≥ 3<br/>No Anomalies After Retries"| ESCALATE_RETRY[🔴 Escalation<br/>Max Retries Reached]
    DECISION --> |"No Anomalies Found<br/>Log Analysis Failed"| ESCALATE_LOGS[🔴 Escalation<br/>No Anomalies Detected]
    DECISION --> |"Confidence < 0.8<br/>Uncertain Root Cause"| ESCALATE_CONF[🔴 Escalation<br/>Low AI Confidence]
    DECISION --> |"No Similar Incidents<br/>No Historical Guidance"| ESCALATE_HIST[🔴 Escalation<br/>Unknown Pattern]
    DECISION --> |"All Criteria Met<br/>High Confidence ≥ 0.8"| AUTO_MITIGATE[✅ Auto-Mitigation<br/>Execute Solution]
    
    %% Action Paths
    AUTO_MITIGATE --> MITIGATION[🔧 Mitigation Agent<br/>Execute Automated Solution]
    ESCALATE_RETRY --> ESCALATION[🚨 Escalation Agent<br/>Human Intervention Required]
    ESCALATE_LOGS --> ESCALATION
    ESCALATE_CONF --> ESCALATION
    ESCALATE_HIST --> ESCALATION
    
    %% Mitigation Actions
    MITIGATION --> |"Apply Solution<br/>Restart Service<br/>Clear Cache<br/>Scale Resources"| MITIGATION_RESULT[🔧 Mitigation Results<br/>Actions Taken: List<br/>Status: Success/Failure<br/>Timestamp: Recorded]
    
    %% Escalation Actions
    ESCALATION --> |"Create Ticket<br/>Notify On-Call<br/>Provide Context<br/>Escalation Reason"| ESCALATION_RESULT[🚨 Escalation Results<br/>Ticket ID: Created<br/>On-Call: Notified<br/>Reason: Documented]
    
    %% Communication and Reporting
    MITIGATION_RESULT --> COMMUNICATOR[📧 Communicator Agent<br/>Final Report Generation]
    ESCALATION_RESULT --> COMMUNICATOR
    
    %% Email Notifications Throughout Workflow
    TRIGGER --> EMAIL1[📧 Incident Alert Email]
    LOG_RESULT --> EMAIL2[📧 Log Analysis Complete]
    KNOWLEDGE_RESULT --> EMAIL3[📧 Knowledge Search Complete]
    ROOT_RESULT --> EMAIL4[📧 Root Cause Identified]
    MITIGATION_RESULT --> EMAIL5[📧 Mitigation Applied]
    ESCALATION_RESULT --> EMAIL6[📧 Escalation Notice]
    COMMUNICATOR --> EMAIL7[📧 Final Status Report]
    
    %% Final Report Generation
    COMMUNICATOR --> |"Aggregate All Results<br/>Generate Summary<br/>Include Metrics"| FINAL_REPORT[📄 Final Report<br/>Incident Summary<br/>Actions Taken<br/>Resolution Status]
    
    %% Final States
    FINAL_REPORT --> END_SUCCESS([🟢 INCIDENT RESOLVED<br/>Auto-Mitigation Successful])
    FINAL_REPORT --> END_ESCALATED([🟡 INCIDENT ESCALATED<br/>Human Review Required])
    
    %% Error Handling
    TRIGGER --> |"Error"| ERROR[❌ Error Handler]
    LOG_ANALYSIS --> |"Error"| ERROR
    KNOWLEDGE --> |"Error"| ERROR
    ROOT_CAUSE --> |"Error"| ERROR
    COORDINATOR --> |"Error"| ERROR
    MITIGATION --> |"Error"| ERROR
    ESCALATION --> |"Error"| ERROR
    ERROR --> END_ERROR([🔴 WORKFLOW ERROR<br/>System Failure])
    
    %% Retry Logic for Log Analysis
    LOG_ANALYSIS --> |"No Anomalies & Retry < 3"| RETRY_LOG[🔄 Retry Log Analysis]
    RETRY_LOG --> LOG_ANALYSIS
    
    %% Styling with Black Text
    classDef agentNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000000
    classDef resultNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000000
    classDef decisionNode fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000000
    classDef escalationNode fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000000
    classDef mitigationNode fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px,color:#000000
    classDef errorNode fill:#fce4ec,stroke:#ad1457,stroke-width:2px,color:#000000
    classDef emailNode fill:#fff9c4,stroke:#f57f17,stroke-width:1px,color:#000000
    classDef defaultNode fill:#f9f9f9,stroke:#333333,stroke-width:2px,color:#000000
    classDef successNode fill:#c8e6c9,stroke:#1b5e20,stroke-width:2px,color:#000000
    
    class LOG_ANALYSIS,KNOWLEDGE,ROOT_CAUSE agentNode
    class LOG_RESULT,KNOWLEDGE_RESULT,ROOT_RESULT,MITIGATION_RESULT,ESCALATION_RESULT,FINAL_REPORT resultNode
    class DECISION,CHECK decisionNode
    class ESCALATE_RETRY,ESCALATE_LOGS,ESCALATE_CONF,ESCALATE_HIST,ESCALATION,END_ESCALATED escalationNode
    class AUTO_MITIGATE,MITIGATION,END_SUCCESS mitigationNode
    class ERROR,END_ERROR errorNode
    class EMAIL1,EMAIL2,EMAIL3,EMAIL4,EMAIL5,EMAIL6,EMAIL7 emailNode
    class START,TRIGGER,PARALLEL,COORDINATOR,SUMMARY,WAIT,COMMUNICATOR,RETRY_LOG defaultNode
```

### Detailed Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    graph.py                                 │
│                                                             │
│  1. create_initial_state()                                 │
│     └─> Creates IncidentState with incident_id             │
│                                                             │
│  2. workflow.invoke(initial_state)                         │
│     └─> Starts execution                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  NODE: incident_trigger_node                                │
│  - Calls AIAnalyzer.parse_incident_alert()                 │
│  - Calls EmailNotifier.send_incident_alert()               │
│  - Returns: {service, severity, description}               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  ROUTING: route_after_trigger()                             │
│  - Checks for errors                                        │
│  - Checks for service info                                  │
│  - Returns: ["log_analysis", "knowledge_lookup",           │
│              "root_cause"]                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├──────┬──────┬──────┐
                            ▼      ▼      ▼      
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ log_analysis │  │ knowledge_   │  │ root_cause_  │
│ _node        │  │ lookup_node  │  │ node         │
│              │  │              │  │              │
│ Uses:        │  │ Uses:        │  │ Uses:        │
│ LogAnalyzer  │  │ Knowledge    │  │ AIAnalyzer   │
│              │  │ Searcher     │  │              │
│              │  │              │  │              │
│ Returns:     │  │ Returns:     │  │ Returns:     │
│ log_analysis │  │ knowledge_   │  │ root_cause_  │
│ _results     │  │ lookup_      │  │ results      │
│              │  │ results      │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  NODE: coordinator_node                                     │
│  - Aggregates all results                                   │
│  - Calculates summary metrics                               │
│  - Returns: {coordination_summary}                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  ROUTING: route_after_coordination()                        │
│  - Checks if all analyses completed                         │
│  - Returns: "decision"                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  NODE: decision_node                                        │
│  - Checks confidence threshold                              │
│  - Evaluates anomalies and history                          │
│  - Makes decision                                           │
│  - Returns: {decision, decision_metrics}                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  ROUTING: route_after_decision()                            │
│  - Routes based on decision                                 │
│  - Returns: "mitigation" OR "escalation"                    │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
┌──────────────────────┐  ┌──────────────────────┐
│  mitigation_node     │  │  escalation_node     │
│  - Execute solution  │  │  - Escalate to human │
│  - Send email        │  │  - Send email        │
│  - Returns: results  │  │  - Returns: results  │
└──────────────────────┘  └──────────────────────┘
                │                       │
                └───────────┬───────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  NODE: communicator_node                                    │
│  - Generates final report                                   │
│  - Returns: {final_report}                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                          [END]
```

---

## Parallel Execution

### How Parallelism Works

1. **Graph Returns List of Nodes**:
```python
def route_after_trigger(state):
    return ["log_analysis", "knowledge_lookup", "root_cause"]
```

2. **LangGraph Executes All Simultaneously**:
- Each node runs in parallel
- Each node updates different state keys
- LangGraph merges results automatically

3. **State Merging with Reducers**:
```python
# state.py
agents_completed: Annotated[List[str], merge_lists]

def merge_lists(existing: List, new: List) -> List:
    return (existing or []) + (new or [])
```

### Performance Characteristics

| Metric | Sequential | Parallel | Improvement |
|--------|-----------|----------|-------------|
| Total Time | 15-20s | 6-8s | **3x faster** |
| Execution | One by one | Simultaneous | **Concurrent** |
| Scalability | O(n) | O(1) | **Excellent** |

---

## Testing Strategy

### Unit Testing Nodes

```python
def test_log_analysis_node():
    # Arrange
    state = {
        "service": "Payment API",
        "description": "database timeout"
    }
    
    # Act
    result = log_analysis_node(state)
    
    # Assert
    assert "log_analysis_results" in result
    assert "agents_completed" not in result  # Node purity
```

### Unit Testing Agents

```python
def test_log_analyzer():
    # Arrange
    analyzer = LogAnalyzer()
    
    # Act
    result = analyzer.analyze_logs("Payment API", "timeout")
    
    # Assert
    assert "anomalies" in result
    assert len(result["anomalies"]) > 0
```

### Integration Testing Graph

```python
def test_workflow_execution():
    # Arrange
    workflow = create_incident_workflow()
    initial_state = create_initial_state("Test alert")
    
    # Act
    final_state = workflow.invoke(initial_state)
    
    # Assert
    assert "decision" in final_state
    assert "final_report" in final_state
```

---

## Comparison: Old vs New

| Aspect | Old Design | New Design |
|--------|-----------|------------|
| **Architecture** | Fat agents | Thin nodes + graph |
| **Orchestration** | In agents | In graph.py |
| **Completion** | Agents track | Graph tracks |
| **Routing** | Agents decide | Graph decides |
| **Reusability** | Low | High |
| **Testability** | Hard | Easy |
| **Maintainability** | Complex | Simple |
| **LangGraph Compliance** | No | Yes |

---

## Key Takeaways

1. **Nodes = Workers**: They do work, not orchestration
2. **Graph = Manager**: It orchestrates, not processes
3. **Agents = Tools**: They're reusable, not controllers
4. **State = Data**: It's structure, not logic

This architecture follows the **Single Responsibility Principle** and makes the system:
- More testable
- More maintainable
- More scalable
- LangGraph-compliant

---

**Built following LangGraph best practices**
