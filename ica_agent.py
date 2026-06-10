"""
IBM Consulting Advantage (ICA) Agent Integration
Single API workflow with multiple agent prompts
"""

import requests
import json
import uuid
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ICA_API_URL = os.getenv("ICA_API_URL", "")
ICA_API_KEY = os.getenv("ICA_API_KEY", "")
confidence_score_prompt = """At the end of your JSON response, always include a "confidence" object.

Confidence Score Rules:
- Score range: 0.0 to 1.0 (e.g., 0.85)
- STEP 1: Determine your numeric score first.
- STEP 2: Derive the level using ONLY this logic — no exceptions, no overrides:
    IF score >= 0.75 THEN level = "High"
    IF score >= 0.50 AND score < 0.75 THEN level = "Medium"
    IF score < 0.50 THEN level = "Low"
- STEP 3: Do NOT let the rationale text influence the level. The level is determined purely by the number.
- STEP 4: Before writing the confidence object, state internally: "My score is X, therefore level is Y" and use that Y.
- rationale: Brief explanation of why this confidence score was assigned based on data availability and clarity.
- low_confidence_fields: List any specific fields where data was missing, ambiguous, or inferred. If none, return an empty array [].

STRICT RULE: A score of 0.75 or above is ALWAYS "High". Never "Medium". Never "Low".
STRICT RULE: A score of 0.50 to 0.74 is ALWAYS "Medium". Never "High". Never "Low".
STRICT RULE: A score below 0.50 is ALWAYS "Low". Never "High". Never "Medium".

Example — correct behavior:
  score: 0.76 → level: "High"   ✅
  score: 0.78 → level: "High"   ✅
  score: 0.74 → level: "Medium" ✅
  score: 0.49 → level: "Low"    ✅

Example — incorrect behavior (never do this):
  score: 0.76 → level: "Medium" ❌
  score: 0.78 → level: "Medium" ❌"""


class ICAAgentClient:
    """
    Client for IBM Consulting Advantage Agent API
    Handles all agent interactions through a single workflow
    """
    
    def __init__(self):
        """Initialize ICA Agent Client"""
        self.api_url = ICA_API_URL
        self.api_key = ICA_API_KEY
        
    def call_agent(self, agent_prompt: str, context_data: str, debug: bool = False, expected_keys: Optional[list] = None) -> Optional[Dict[str, Any]]:
        """
        Call ICA Agent with specific prompt and context
        
        Args:
            agent_prompt: The agent-specific prompt/instructions
            context_data: The data/context for the agent to analyze
            debug: If True, print debug information
            expected_keys: Optional list of expected top-level JSON keys for response validation
            
        Returns:
            Parsed JSON response from agent or None if error
        """
        # Build the complete user message with strict task isolation and explicit JSON context boundaries
        user_message = (
            "You must complete exactly one task only.\n"
            "Do not answer any other analysis type.\n"
            "Do not return fields from any other schema.\n\n"
            f"{agent_prompt}\n\n"
            "STRICT OUTPUT CONTRACT:\n"
            "1. Return only one JSON object.\n"
            "2. Use only the exact fields requested in the prompt schema.\n"
            "3. Do not include fields from complexity, dependency, migration, or effort estimation outputs unless explicitly requested.\n"
            "4. If information is missing, use best-effort inferred values within the requested schema only.\n\n"
            "Analyze the following JSON context data.\n"
            "The JSON payload starts after <JSON_CONTEXT> and ends before </JSON_CONTEXT>.\n"
            "Use the JSON content as the primary source for your analysis.\n\n"
            "<JSON_CONTEXT>\n"
            f"{context_data}\n"
            "</JSON_CONTEXT>\n\n"
            "Return only a valid JSON object. Do not include markdown fences or extra commentary."
        )
        
        # Request payload
        payload = {
            "output_type": "chat",
            "input_type": "chat",
            "input_value": user_message,
            "session_id": str(uuid.uuid4())
        }
        
        headers = {"x-api-key": self.api_key}
        
        try:
            if debug:
                print("\n" + "="*80)
                print("DEBUG: API Request")
                print("="*80)
                print(f"URL: {self.api_url}")
                print(f"Payload Keys: {list(payload.keys())}")
                print(f"User Message Length: {len(user_message)} characters")
                print(f"Context Data Length: {len(context_data)} characters")
                print(f"Session ID: {payload['session_id']}")
                print("Input Value Preview:")
                print(user_message[:4000] + ("..." if len(user_message) > 4000 else ""))
            
            # Send API request
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            if debug:
                print("\n" + "="*80)
                print("DEBUG: Raw API Response")
                print("="*80)
                print(json.dumps(result, indent=2))
                print("="*80 + "\n")
            
            # Extract the AI response from nested Langflow structure
            # Structure: outputs[0].outputs[0].outputs.message.message
            if "outputs" in result and len(result["outputs"]) > 0:
                first_output = result["outputs"][0]
                message_text = None
                
                if "outputs" in first_output and len(first_output["outputs"]) > 0:
                    nested_output = first_output["outputs"][0]
                    
                    # Path 1: outputs[0].outputs[0].outputs.message.message
                    if "outputs" in nested_output and "message" in nested_output["outputs"]:
                        message_obj = nested_output["outputs"]["message"]
                        message_text = message_obj.get("message", "") or message_obj.get("text", "")
                    
                    # Path 2: outputs[0].outputs[0].results.message.data.text
                    elif "results" in nested_output and "message" in nested_output["results"]:
                        message_data = nested_output["results"]["message"].get("data", {})
                        message_text = message_data.get("text", "")
                
                if debug and message_text:
                    print("\n" + "="*80)
                    print("DEBUG: Extracted Message Text")
                    print("="*80)
                    print(message_text[:500] + "..." if len(message_text) > 500 else message_text)
                    print("="*80 + "\n")
                
                if message_text:
                    # Try to parse as JSON
                    try:
                        parsed_json = json.loads(message_text)
                        if debug:
                            print("\n" + "="*80)
                            print("DEBUG: Parsed JSON Response")
                            print("="*80)
                            print(json.dumps(parsed_json, indent=2))
                            print("="*80 + "\n")
                        
                        if expected_keys and isinstance(parsed_json, dict):
                            matched_keys = [key for key in expected_keys if key in parsed_json]
                            if not matched_keys:
                                return {
                                    "error": "Agent returned JSON, but not in the expected schema",
                                    "expected_keys": expected_keys,
                                    "actual_keys": list(parsed_json.keys()),
                                    "raw_response": parsed_json
                                }
                        
                        return parsed_json
                    except json.JSONDecodeError as e:
                        if debug:
                            print(f"\nDEBUG: JSON Parse Error: {str(e)}")
                        # If not valid JSON, return as text in a dict
                        return {"response": message_text, "raw_text": True}
                else:
                    return {"error": "Could not find message text in response", "raw_response": result}
            else:
                return {"error": "No outputs found in response", "raw_response": result}
                
        except requests.exceptions.RequestException as e:
            if debug:
                print(f"\nDEBUG: Request Exception: {str(e)}")
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            if debug:
                print(f"\nDEBUG: Unexpected Exception: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}


class ProcessAnalyzerAgent:
    """Agent 1: Process Understanding Agent"""
    
    def __init__(self, ica_client: ICAAgentClient):
        self.client = ica_client
        self.prompt = """"You are an expert RPA Process Analyst specializing in Blue Prism automation analysis.

Analyze the provided Blue Prism process data and generate a comprehensive process understanding report.

Your analysis should include:
1. Process name and description
2. Business purpose (infer from process name and applications)
3. AI-generated process steps (business-readable steps)
4. Applications used
5. File dependencies

Important rules:
- In "applications_used", include only external business/user-facing applications or technologies actually interacted with by the process, such as Excel, Outlook, SAP, web apps, desktop apps, databases, APIs, or shared mailboxes.
- Do NOT include Blue Prism platform constructs or internal components such as Process, Object, Business Object, Work Queue, Environment Variable, Credential Manager, Release Package, Control Room, or Blue Prism itself unless Blue Prism is explicitly the target application being automated.
- In "file_dependencies", include only business/input/output/supporting files actually consumed or produced by the process at runtime.
- Do NOT include the uploaded .bprelease package, release XML, or Blue Prism export artifacts as runtime file dependencies.

{confidence_score_prompt}

Return a JSON object with this structure:
{
    "process_name": "string",
    "description": "string",
    "business_purpose": "string",
    "ai_generated_steps": ["step1", "step2", ...],
    "applications_used": ["app1", "app2", ...],
    "file_dependencies": ["file1", "file2", ...],
    
},
"confidence": {
    "score": 0.0,
    "level": "High|Medium|Low",
    "rationale": "string",
    "low_confidence_fields": ["field1", "field2", ...]
}"""
    
    def analyze(self, parsed_data: Dict[str, Any], debug: bool = False) -> Dict[str, Any]:
        """Analyze process using ICA Agent"""
        context = json.dumps(parsed_data, indent=2)
        result = self.client.call_agent(
            self.prompt,
            context,
            debug=debug,
            expected_keys=[
                "process_name",
                "description",
                "business_purpose",
                "ai_generated_steps",
                "applications_used",
                "file_dependencies"
            ]
        )
    
        if result and "error" not in result:
            return {
                "process_count": len(parsed_data.get('processes', [])),
                "processes": [result] if not isinstance(result, list) else result,
                "summary": f"Analyzed {len(parsed_data.get('processes', []))} process(es)",
                "reusable_components": [],
                "business_functions": []
            }
        else:
            error_msg = result.get("error", "Unknown error") if result else "No response from agent"
            error_response = {"error": error_msg, "processes": []}
            if result:
                if "actual_keys" in result:
                    error_response["actual_keys"] = result["actual_keys"]
                if "expected_keys" in result:
                    error_response["expected_keys"] = result["expected_keys"]
                if "raw_response" in result:
                    error_response["raw_response"] = result["raw_response"]
            return error_response


class ComplexityAssessorAgent:
    """Agent 2: Complexity Assessment Agent"""
    
    def __init__(self, ica_client: ICAAgentClient):
        self.client = ica_client
        self.prompt = """You are an expert RPA Complexity Analyst specializing in automation assessment.

Analyze the provided process data and derive workbook-aligned metric counts using the EXACT workbook definitions below.

STRICT WORKBOOK DEFINITIONS - FOLLOW THESE EXACTLY:

1. INTERFACE:
   Description: "Application used to perform the process, e.g. Web, Excel, Outlook"
   - Count distinct applications/systems the process interacts with
   - Examples: Web browser, Microsoft Excel, Outlook, SAP, Oracle, databases, APIs
   - DO NOT count Blue Prism internal components (Work Queue, Process, Object, etc.)

2. ACTIVITIES:
   Description: "Activity is single key step performed to execute a process containing no more than 7 tasks"
   Example Activity: "Login"
   Example Tasks: "Launch browser, goto URL, Enter User, Enter Password, Click on submit button, etc"
   - Use "ai_generated_steps" from process_analysis as PRIMARY source
   - Count high-level business activities, NOT individual technical tasks
   - Each activity should represent a logical business step (like "Login", "Extract Data", "Process Order")
   - If ai_generated_steps shows 10 business steps, count 10 activities
   - DO NOT count low-level technical actions (click, type, etc.) as separate activities

3. DATA TRANSFORMATION:
   Description: "Data transformation activities that require applying logic or calculations for downstream processing"
   Examples of Data Transformation:
   - Extracting specific values from text
   - Using reference tables to convert values
   - Having macros in the process or complex excel operations
   - Activities which start with words like: Calculate, Validate, Determine, Manipulate, Transform, Verify, Create, Apply rules, Assign, Vlookup, Check, etc.
   - Activities which work with encrypted data (to encrypt or to decrypt)
   - Look for these keywords in ai_generated_steps and stage names
   - Count each distinct transformation activity
   - Do Not include any Screenshot image files captured during exceptions.

4. DIGITAL LAYOUTS:
   Description: "Any different input/output file should be treated as separate layouts. This can relate to different digital file extensions (e.g. pdf, xls) or it can be different templates within one file extension (e.g. each unique worksheet within one Excel file is one digital layout, Month End Reconciliation Report, Approval Matrix)"
   - Count distinct file types/templates used as input or output
   - Different file extensions = different layouts (PDF, XLS, CSV, etc.)
   - Different worksheets in same Excel file = different layouts
   - Different report templates = different layouts
   - Look for file operations in parsed_data and ai_generated_steps

5. PROCESS FLOWS:
   Description: "Number of process paths including the standard happy path and each potential exception flow"
   Notes: "The process flows are derived from splits in the process. As a result the flowchart path splits off into different independent branches. The additional flow needs to contain more than 2 activities. The splits of the processes can derive from: decision points, Human action in the middle of the process flow, etc."
   - Use "ai_generated_steps" from process_analysis as PRIMARY source
   - Start with 1 for the standard happy path
   - Count ONLY splits/branches where the path diverges into independent branches with MORE THAN 2 ACTIVITIES
   - Splits can come from: decision points, human actions, exception handlers
   - DO NOT count every decision - only substantial branches (>2 activities)
   - Example: Linear process with 10 steps, no branching = 1 process flow
   - Example: Process with validation creating 2 paths (success with 5 steps, failure with 3 steps) = 2 process flows
   - Example: Process with error handling (>2 activities in error path) = 2 process flows (happy + error)

IMPORTANT RULES:
- Do not calculate final complexity scores - only count metrics
- Do not return dependency, migration, effort, or unrelated fields
- If information is missing, note it in risk_factors
- Use ai_generated_steps as your primary source for understanding the process

{confidence_score_prompt}

Return a JSON object with this structure:
{
    "metric_counts": {
        "interface": 0,
        "activities": 0,
        "data_transformation": 0,
        "digital_layouts": 0,
        "process_flows": 0
    },
    "count_rationale": {
        "interface": "Explain which applications were counted and why",
        "activities": "Explain which business activities were counted from ai_generated_steps",
        "data_transformation": "Explain which transformation activities were identified",
        "digital_layouts": "Explain which file types/templates were counted",
        "process_flows": "Explain how you derived the count from ai_generated_steps and branching logic"
    },
    "risk_factors": ["risk1", "risk2", ...]
},
"confidence": {
    "score": 0.0,
    "level": "High|Medium|Low",
    "rationale": "string",
    "low_confidence_fields": ["field1", "field2", ...]
}"""
    
    def assess(self, parsed_data: Dict[str, Any], process_analysis: Dict[str, Any], complexity_metrics: Optional[Dict[str, Any]] = None, debug: bool = False) -> Dict[str, Any]:
        """Assess complexity using ICA Agent"""
        context = json.dumps({
            "parsed_data": parsed_data,
            "process_analysis": process_analysis,
            "complexity_metrics": complexity_metrics
        }, indent=2)
        
        result = self.client.call_agent(
            self.prompt,
            context,
            debug=debug,
            expected_keys=[
                "metric_counts",
                "count_rationale",
                "risk_factors"
            ]
        )
        
        if result and "error" not in result:
            return result
        else:
            error_msg = result.get("error", "Unknown error") if result else "No response from agent"
            error_response = {"error": error_msg, "overall_complexity": "Unknown"}
            if result:
                if "actual_keys" in result:
                    error_response["actual_keys"] = result["actual_keys"]
                if "expected_keys" in result:
                    error_response["expected_keys"] = result["expected_keys"]
                if "raw_response" in result:
                    error_response["raw_response"] = result["raw_response"]
            return error_response


class DependencyAnalyzerAgent:
    """Agent 3: Dependency Analysis Agent"""
    
    def __init__(self, ica_client: ICAAgentClient):
        self.client = ica_client
        self.prompt = """You are an expert RPA Dependency Analyst specializing in automation architecture.

Analyze the provided process data and identify all dependencies including:
- Applications (SAP, Oracle, Excel, Outlook, etc.)
- File types (Excel, CSV, PDF, XML, etc.)
- Integration points and methods
- Databases
- APIs
- Do NOT include Blue Prism platform constructs or internal components such as Process, Object, Business Object, Work Queue, Environment Variable, Credential Manager, Release Package, Control Room, or Blue Prism itself unless Blue Prism is explicitly the target application being automated.
- In "file_dependencies", include only business/input/output/supporting files actually consumed or produced by the process at runtime.
- Do NOT include the uploaded .bprelease package, release XML, or Blue Prism export artifacts as runtime file dependencies.
- Do Not include anyScreenshot image files captured during exceptions as file dependencies.

Also identify dependency risks with severity levels and mitigation strategies.
{confidence_score_prompt}
Return a JSON object with this structure:
{
    "applications": ["app1", "app2", ...],
    "application_count": 0,
    "files": ["file1", "file2", ...],
    "file_count": 0,
    "integrations": [{
        "name": "string",
        "type": "string",
        "method": "string"
    }],
    "integration_count": 0,
    "databases": ["db1", "db2", ...],
    "apis": ["api1", "api2", ...],
    "dependency_risks": [{
        "category": "string",
        "severity": "High|Medium|Low",
        "description": "string"
    }]
},
"confidence": {
    "score": 0.0,
    "level": "High|Medium|Low",
    "rationale": "string",
    "low_confidence_fields": ["field1", "field2", ...]
}"""
    
    def analyze(self, parsed_data: Dict[str, Any], debug: bool = False) -> Dict[str, Any]:
        """Analyze dependencies using ICA Agent"""
        context = json.dumps(parsed_data, indent=2)
        result = self.client.call_agent(
            self.prompt,
            context,
            debug=debug,
            expected_keys=[
                "applications",
                "application_count",
                "files",
                "file_count",
                "integrations",
                "integration_count",
                "databases",
                "apis",
                "dependency_risks"
            ]
        )
        
        if result and "error" not in result:
            return result
        else:
            error_msg = result.get("error", "Unknown error") if result else "No response from agent"
            return {"error": error_msg, "applications": []}


class MigrationMapperAgent:
    """Agent 4: Migration Mapping Agent"""
    
    def __init__(self, ica_client: ICAAgentClient):
        self.client = ica_client
        self.prompt = """You are an expert RPA Migration Architect specializing in platform migrations.

Analyze the provided data and mapping file to generate migration mappings from Blue Prism to Power Automate:
{confidence_score_prompt}
Return a JSON object with this structure:
{
    "source_platform": "Blue Prism",
    "target_platform": "Power Automate",
    "component_mappings": [{
        "source_component": "string",
        "target_component": "string",
        "migration_notes": "string"
    }],
    "process_mappings": [{
        "source_process": "string",
        "target_component": "string",
        "target_architecture": "string",
        "recommended_approach": "string"
    }],
    "architecture_recommendations": ["rec1", "rec2", ...],
    "modernization_opportunities": ["opp1", "opp2", ...]
},
"confidence": {
    "score": 0.0,
    "level": "High|Medium|Low",
    "rationale": "string",
    "low_confidence_fields": ["field1", "field2", ...]
}"""
    
    def map_components(self, parsed_data: Dict[str, Any], mapping_data: Dict[str, Any], source_platform: str, target_platform: str, debug: bool = False) -> Dict[str, Any]:
        """Map components using ICA Agent"""
        context = json.dumps({
            "parsed_data": parsed_data,
            "mapping_data": mapping_data,
            "source_platform": source_platform,
            "target_platform": target_platform
        }, indent=2)
        
        result = self.client.call_agent(
            self.prompt,
            context,
            debug=debug,
            expected_keys=[
                "source_platform",
                "target_platform",
                "component_mappings",
                "process_mappings",
                "architecture_recommendations",
                "modernization_opportunities"
            ]
        )
        
        if result and "error" not in result:
            return result
        else:
            error_msg = result.get("error", "Unknown error") if result else "No response from agent"
            return {"error": error_msg, "component_mappings": []}


class EffortEstimatorAgent:
    """Agent 5: Effort Estimation Agent"""
    
    def __init__(self, ica_client: ICAAgentClient):
        self.client = ica_client
        self.prompt = """You are an expert RPA Project Estimator specializing in migration effort estimation.

Based on the complexity assessment and estimation matrix estimate the migration effort.
{confidence_score_prompt}
Return a JSON object with this structure:
{
    "Complexity":"string",
    "total_hours": 0,
    "total_days": 0,
    "total_weeks": 0,
    "effort_breakdown": {
        "development": 0,
        "sit_support": 0,
        "uat_support": 0,
        "deployment":0,
        "documentation": 0
    },
    "timeline": {
        "estimated_weeks": 0,
        "with_buffer": 0,
        "estimated_months": 0
    },
    "confidence": {
    "score": 0.0,
    "level": "High|Medium|Low",
    "rationale": "string",
    "low_confidence_fields": ["field1", "field2", ...]
}
}"""
    
    def estimate(self, complexity_assessment: Dict[str, Any], effort_matrix: Dict[str, Any], debug: bool = False) -> Dict[str, Any]:
        """Estimate effort using ICA Agent"""
        context = json.dumps({
            "complexity_assessment": complexity_assessment,
            "effort_matrix": effort_matrix
        }, indent=2)
        
        result = self.client.call_agent(
            self.prompt,
            context,
            debug=debug,
            expected_keys=[
                "Complexity",
                "total_hours",
                "total_days",
                "total_weeks",
                "effort_breakdown",
                "timeline"
            ]
        )
        
        if result and "error" not in result:
            return result
        else:
            error_msg = result.get("error", "Unknown error") if result else "No response from agent"
            return {"error": error_msg, "total_hours": 0}
