import json
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import time
from pathlib import Path
import logging
from crewai import Crew, Agent, Task, Process
from textwrap import dedent
import requests
from perplexityai import Perplexity
from typing import TypedDict, List, Dict, Optional, Any
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('make_to_n8n')

class PerplexityResearcher:
    """Class for researching up-to-date information using Perplexity API"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.client = None
        if api_key:
            self.client = Perplexity(api_key=api_key)
    
    def set_api_key(self, api_key):
        """Set the Perplexity API key"""
        self.api_key = api_key
        if api_key:
            self.client = Perplexity(api_key=api_key)
        else:
            self.client = None
    
    def research(self, query, model="pplx-70b-online"):
        """
        Research information using Perplexity API
        
        Args:
            query: The research query
            model: The Perplexity model to use
            
        Returns:
            tuple: (success (bool), result (str or error message))
        """
        if not self.client:
            return False, "No Perplexity API key provided"
        
        try:
            response = self.client.query(query, model=model)
            return True, response.answer
        except Exception as e:
            logger.error(f"Perplexity API error: {str(e)}", exc_info=True)
            return False, f"Research error: {str(e)}"
    
    def research_make_to_n8n_conversion(self):
        """Research the latest information about Make.com and n8n conversion"""
        query = """
        I need detailed information about converting workflows from Make.com (formerly Integromat) to n8n:
        
        1. What are the latest formats and structures of Make.com JSON export files?
        2. What are the current node types and structures in n8n workflows?
        3. What is the mapping between Make.com modules and n8n nodes?
        4. Are there any official tools or guides for converting between these platforms?
        5. What are the key differences in how data is processed between Make.com and n8n?
        6. Are there any limitations or edge cases to be aware of when converting?
        
        Please provide detailed technical information with examples where possible.
        """
        return self.research(query)

class ConversionState(TypedDict):
    """State management for the Make.com to n8n conversion process"""
    # Input State
    make_json: Dict[str, Any]          # Original Make.com JSON input
    workflow_name: str                  # Name of the workflow
    
    # Analysis State
    analysis_results: Dict[str, Any]    # Results of Make.com structure analysis
    research_findings: Dict[str, Any]   # Platform research results
    learned_mappings: Dict[str, str]    # Module mappings learned from research
    
    # Mapping State
    node_mappings: Dict[str, str]      # Make.com to n8n node mappings
    parameter_mappings: Dict[str, Any]  # Parameter conversion mappings
    
    # Connection State
    connection_graph: Dict[str, Any]    # Node connection structure
    routing_rules: Dict[str, Any]       # Special routing/conditional logic
    
    # Validation State
    schema_validation: Dict[str, Any]   # Schema validation results
    validation_errors: List[str]        # Current validation issues
    
    # Process Control
    revision_number: int                # Current revision attempt
    max_revisions: int                  # Maximum revision attempts
    conversion_stage: str               # Current stage in process
    
    # Output State
    n8n_json: Optional[Dict[str, Any]]  # Generated n8n workflow
    conversion_logs: List[str]          # Detailed conversion logs

def initialize_conversion_state(make_json: Dict[str, Any]) -> ConversionState:
    """Initialize a new conversion state with default values"""
    return {
        # Input State
        "make_json": make_json,
        "workflow_name": make_json.get("name", "Converted Workflow"),
        
        # Analysis State
        "analysis_results": {},
        "research_findings": {},
        "learned_mappings": {},
        
        # Mapping State
        "node_mappings": {},
        "parameter_mappings": {},
        
        # Connection State
        "connection_graph": {},
        "routing_rules": {},
        
        # Validation State
        "schema_validation": {},
        "validation_errors": [],
        
        # Process Control
        "revision_number": 1,
        "max_revisions": 3,
        "conversion_stage": "init",
        
        # Output State
        "n8n_json": None,
        "conversion_logs": []
    }

class MakeToN8nCrewConverter:
    def __init__(self, api_key=None, perplexity_api_key=None):
        self.api_key = api_key
        self.perplexity_api_key = perplexity_api_key
        self.status_callback = None
        self.crew = None
        self.researcher = PerplexityResearcher(api_key=perplexity_api_key)
        self.research_results = {}
        self.current_state: Optional[ConversionState] = None
        self.setup_crew()
        
    def set_perplexity_api_key(self, api_key):
        """Set the API key for Perplexity research"""
        self.perplexity_api_key = api_key
        self.researcher.set_api_key(api_key)
        
    def setup_crew(self):
        """Initialize the Crew AI agents"""
        try:
            # Create specialized agents for different parts of the conversion process
            analyzer_agent = Agent(
                role="Make.com Structure Analyzer",
                goal="Thoroughly analyze Make.com JSON blueprints to identify all components and their connections",
                backstory=dedent("""
                    You are an expert in Make.com's automation platform. Your role is to dissect and understand 
                    Make.com JSON blueprints in great detail. You can identify every type of module, 
                    connection, and feature within the Make.com ecosystem.
                """),
                verbose=True,
                allow_delegation=True
            )
            
            mapper_agent = Agent(
                role="n8n Structure Mapper",
                goal="Map Make.com components to equivalent n8n nodes and structures",
                backstory=dedent("""
                    You are an expert in n8n's workflow automation platform. You know every node type, 
                    parameter, and connection structure. Your specialty is finding the closest equivalent 
                    n8n components for Make.com modules, ensuring functionality is preserved.
                """),
                verbose=True,
                allow_delegation=True
            )
            
            # New Agent: Connection Flow Specialist
            connection_specialist_agent = Agent(
                role="n8n Connection Flow Specialist",
                goal="Perfectly recreate the data flow between nodes in n8n format",
                backstory=dedent("""
                    You specialize in n8n's connection system, understanding how data flows between
                    nodes through main, error and additional outputs. You can translate Make.com's
                    connection paradigm to n8n's structure, handling parallel branches, multiple
                    outputs, and complex routing patterns. You understand exactly how n8n represents
                    connections in its JSON format and can recreate even the most complex workflows.
                """),
                verbose=True,
                allow_delegation=True
            )
            
            # New Agent: n8n Schema Expert
            schema_expert_agent = Agent(
                role="n8n Schema Expert",
                goal="Ensure adherence to n8n's specific JSON schema requirements",
                backstory=dedent("""
                    You are a specialized expert in n8n's JSON structure and schema validation. 
                    You understand all required fields, their proper formats, and version-specific
                    requirements. You know the exact structure of n8n workflow JSON, including 
                    all mandatory and optional fields, data types, and relationships. You can identify 
                    schema inconsistencies and ensure workflows will import correctly into any n8n instance.
                """),
                verbose=True,
                allow_delegation=True
            )
            
            validator_agent = Agent(
                role="n8n JSON Validator",
                goal="Ensure converted n8n JSON is properly structured and valid",
                backstory=dedent("""
                    You are a specialist in JSON validation and n8n's specific schema requirements. 
                    You can identify and fix structural issues, syntax errors, and n8n-specific quirks 
                    in workflow JSON files. Your attention to detail ensures the converted workflows 
                    will import and run correctly in n8n without errors.
                """),
                verbose=True,
                allow_delegation=True
            )
            
            # Create the crew with these agents
            self.crew = Crew(
                agents=[analyzer_agent, mapper_agent, connection_specialist_agent, schema_expert_agent, validator_agent],
                tasks=[],  # We'll add tasks dynamically during conversion
                verbose=True,
                process=Process.sequential  # Agents work in sequence
            )
            
            return True
        except Exception as e:
            logger.error(f"Error setting up Crew AI: {str(e)}", exc_info=True)
            return False
    
    def research_platforms(self) -> tuple[bool, Dict[str, Any]]:
        """Research Make.com and n8n platforms for latest information with enhanced mapping extraction"""
        try:
            research_results = {}
            
            # Research Make.com platform
            make_query = "Latest Make.com (formerly Integromat) workflow structure, node types, and connection patterns"
            make_success, make_results = self.researcher.research(make_query)
            if make_success:
                research_results["make_platform"] = make_results
            
            # Research n8n platform
            n8n_query = "Latest n8n workflow JSON structure, node types, and connection patterns"
            n8n_success, n8n_results = self.researcher.research(n8n_query)
            if n8n_success:
                research_results["n8n_platform"] = n8n_results
            
            # Specific query for module mappings
            mapping_query = "Provide a comprehensive list of Make.com modules and their equivalent n8n nodes, formatted as a mapping table"
            mapping_success, mapping_results = self.researcher.research(mapping_query)
            if mapping_success:
                research_results["module_mappings"] = mapping_results
            
            # Research conversion patterns
            conversion_query = "Common patterns for converting between Make.com and n8n workflows"
            conversion_success, conversion_results = self.researcher.research(conversion_query)
            if conversion_success:
                research_results["conversion_patterns"] = conversion_results
            
            if research_results:
                if self.current_state:
                    self.current_state["research_findings"] = research_results
                    # Extract and store mappings from research
                    discovered_mappings = self._store_research_mappings(research_results)
                    self.current_state["conversion_logs"].append(
                        f"Research completed successfully with {len(discovered_mappings)} module mappings discovered"
                    )
                return True, research_results
            return False, {}
            
        except Exception as e:
            logger.error(f"Error in platform research: {str(e)}", exc_info=True)
            if self.current_state:
                self.current_state["conversion_logs"].append(f"Research error: {str(e)}")
            return False, {}
    
    def set_status_callback(self, callback):
        """Set a callback function to update status messages in the UI"""
        self.status_callback = callback
        
    def update_status(self, message):
        """Update status with a message"""
        logger.info(message)
        if self.status_callback:
            self.status_callback(message)
    
    def convert_json(self, make_json: Dict[str, Any]) -> tuple[bool, Any]:
        """
        Convert Make.com JSON to n8n JSON using Crew AI framework
        
        Args:
            make_json: The Make.com JSON blueprint
            
        Returns:
            tuple: (success (bool), result (dict or error message))
        """
        try:
            self.update_status("Starting conversion process with Crew AI agents...")
            
            # Initialize conversion state
            self.current_state = initialize_conversion_state(make_json)
            
            # Perform research if Perplexity API key is available
            if self.perplexity_api_key:
                self.update_status("Researching latest platform information to improve conversion...")
                research_success, research_results = self.research_platforms()
                if research_success:
                    self.current_state["research_findings"] = research_results
                    self.update_status("Applying research findings to conversion process...")
            
            # Create the tasks for the crew
            tasks = self._create_conversion_tasks(self.current_state)
            
            # If no API key is provided, use simulated mode
            if not self.api_key:
                self.update_status("No API key provided. Using simulated conversion mode...")
                simulated_result = self._simulate_conversion(self.current_state)
                if simulated_result:
                    self.current_state["n8n_json"] = simulated_result
                    return True, simulated_result
                return False, "Simulation failed"
            
            # Set the tasks for the crew
            self.crew.tasks = tasks
            
            # Execute the crew's tasks
            self.update_status("Crew AI agents are working on the conversion...")
            result = self.crew.kickoff()
            
            # Process the result
            if isinstance(result, str):
                try:
                    # Try to parse the result as JSON
                    n8n_json = json.loads(result)
                    self.current_state["n8n_json"] = n8n_json
                    self.update_status("Conversion completed successfully!")
                    return True, n8n_json
                except json.JSONDecodeError:
                    # If not valid JSON, extract JSON from the text
                    self.update_status("Parsing Crew AI output...")
                    json_str = self._extract_json_from_text(result)
                    if json_str:
                        n8n_json = json.loads(json_str)
                        self.current_state["n8n_json"] = n8n_json
                        self.update_status("Conversion completed successfully!")
                        return True, n8n_json
                    else:
                        return False, "Failed to extract valid JSON from Crew AI output"
            else:
                return False, "Unexpected result format from Crew AI"
            
        except Exception as e:
            logger.error(f"Error in conversion process: {str(e)}", exc_info=True)
            if self.current_state:
                self.current_state["conversion_logs"].append(f"Error: {str(e)}")
            return False, f"Conversion error: {str(e)}"
    
    def _create_conversion_tasks(self, state: ConversionState):
        """Create the tasks for the Crew AI agents with state management"""
        make_json_str = json.dumps(state["make_json"], indent=2)
        
        # Create task context with state information
        task_context = {
            "workflow_name": state["workflow_name"],
            "revision_number": state["revision_number"],
            "research_findings": state["research_findings"],
            "current_stage": state["conversion_stage"]
        }
        
        tasks = [
            Task(
                description=f"Analyze the Make.com workflow structure:\n{make_json_str}",
                context=task_context,
                expected_output="Detailed analysis of the Make.com workflow structure"
            ),
            Task(
                description="Map Make.com components to n8n equivalents using the analysis",
                context={**task_context, "analysis_results": state["analysis_results"]},
                expected_output="Complete mapping of Make.com components to n8n"
            ),
            Task(
                description="Create connection structure for n8n workflow",
                context={**task_context, "node_mappings": state["node_mappings"]},
                expected_output="Detailed n8n connection configuration"
            ),
            Task(
                description="Validate and optimize the n8n workflow structure",
                context={
                    **task_context,
                    "connection_graph": state["connection_graph"],
                    "validation_errors": state["validation_errors"]
                },
                expected_output="Validated and optimized n8n workflow JSON"
            )
        ]
        
        return tasks
    
    def _extract_json_from_text(self, text):
        """Extract JSON from text that might contain additional content"""
        # Look for JSON between triple backticks
        import re
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
        if json_match:
            return json_match.group(1)
        
        # Look for JSON between single backticks
        json_match = re.search(r'`([\s\S]*?)`', text)
        if json_match:
            return json_match.group(1)
        
        # Look for JSON-like content (starting with { and ending with })
        json_match = re.search(r'(\{[\s\S]*\})', text)
        if json_match:
            return json_match.group(1)
        
        return None
    
    def _simulate_conversion(self, state: ConversionState) -> Optional[Dict[str, Any]]:
        """Simulate an AI conversion with state management"""
        try:
            # Update conversion stage
            state["conversion_stage"] = "simulation"
            
            # Extract workflow information from state
            workflow_name = state["workflow_name"]
            flow_items = state["make_json"].get("flow", [])
            
            # Create a simulated n8n workflow JSON
            n8n_workflow = {
                "id": str(uuid.uuid4()),
                "name": workflow_name,
                "active": True,
                "nodes": [],
                "connections": {},
                "settings": {
                    "executionOrder": "v1",
                    "saveExecutionProgress": True,
                    "saveManualExecutions": True,
                    "timezone": "America/New_York"
                },
                "tags": [],
                "pinData": {},
                "versionId": 1,
                "triggerCount": 1,
                "staticData": None,
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            }
            
            # Process each flow item
            for i, item in enumerate(flow_items):
                node = self._simulate_node_conversion(item, i)
                if node:
                    n8n_workflow["nodes"].append(node)
            
            # Update state with simulation results
            state["n8n_json"] = n8n_workflow
            state["conversion_stage"] = "completed"
            state["conversion_logs"].append("Simulation completed successfully")
            
            return n8n_workflow
            
        except Exception as e:
            logger.error(f"Error in simulation: {str(e)}", exc_info=True)
            state["conversion_logs"].append(f"Simulation error: {str(e)}")
            return None

    def _simulate_node_conversion(self, make_node: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Helper method to simulate node conversion"""
        try:
            node_type = make_node.get("type", "unknown")
            
            # Map Make.com node type to n8n equivalent
            n8n_type = self._get_n8n_node_type(node_type)
            
            # Create simulated n8n node
            n8n_node = {
                "id": str(uuid.uuid4()),
                "name": f"{n8n_type} {index + 1}",
                "type": n8n_type,
                "typeVersion": 1,
                "position": [index * 200, 0],
                "parameters": {},
                "disabled": False
            }
            
            if self.current_state:
                self.current_state["node_mappings"][make_node.get("id", str(uuid.uuid4()))] = n8n_node["id"]
            
            return n8n_node
            
        except Exception as e:
            logger.error(f"Error in node conversion: {str(e)}", exc_info=True)
            if self.current_state:
                self.current_state["conversion_logs"].append(f"Node conversion error: {str(e)}")
            return None

    def _get_n8n_node_type(self, make_type):
        """Map Make.com module types to n8n node types with improved research integration"""
        make_type_lower = make_type.lower()
        
        # Default mapping of common module types
        default_module_map = {
            "http": "n8n-nodes-base.httpRequest",
            "email": "n8n-nodes-base.emailSend",
            "webhook": "n8n-nodes-base.webhook",
            "googlesheets": "n8n-nodes-base.googleSheets",
            "gmail": "n8n-nodes-base.gmail",
            "filter": "n8n-nodes-base.if",
            "router": "n8n-nodes-base.switch",
            "airtable": "n8n-nodes-base.airtable",
            "slack": "n8n-nodes-base.slack",
            "text-parser": "n8n-nodes-base.splitInBatches",
            "iterator": "n8n-nodes-base.splitInBatches"
        }
        
        # Check for research-derived mappings in conversion state
        if self.current_state and "learned_mappings" in self.current_state:
            learned_mappings = self.current_state["learned_mappings"]
            if make_type_lower in learned_mappings:
                mapping = learned_mappings[make_type_lower]
                logger.info(f"Using research-derived mapping: {make_type} -> {mapping}")
                return mapping
        
        # Try to extract from research results (legacy approach for backward compatibility)
        if "platforms" in self.research_results:
            try:
                research_text = self.research_results["platforms"]
                
                import re
                mapping_pattern = re.compile(r'(?i)' + re.escape(make_type) + r'\s*(?:module|connector)?\s*(?:maps|corresponds|translates|converts)?\s*(?:to)?\s*[\'"]?(n8n-nodes-[a-zA-Z0-9.-]+)[\'"]?')
                
                matches = mapping_pattern.findall(research_text)
                if matches and len(matches) > 0:
                    logger.info(f"Found mapping for {make_type} in research: {matches[0]}")
                    return matches[0]
            except Exception as e:
                logger.debug(f"Error extracting module mapping from research: {str(e)}")
        
        # Fall back to default mapping or function node if not found
        result = default_module_map.get(make_type_lower, "n8n-nodes-base.function")
        logger.debug(f"Using default mapping: {make_type} -> {result}")
        return result

    def _parse_module_mappings_from_research(self, research_text: str) -> Dict[str, str]:
        """Extract Make.com to n8n module mappings from research text"""
        discovered_mappings = {}
        
        try:
            import re
            
            # Multiple pattern matching to increase chance of finding mappings
            basic_mapping_pattern = re.compile(
                r'([a-zA-Z0-9_.-]+)\s*(?:module|connector)?\s*(?:maps|corresponds|translates|converts)?\s*(?:to)?\s*[\'"]?(n8n-nodes-[a-zA-Z0-9.-]+)[\'"]?'
            )
            
            table_pattern = re.compile(
                r'(?:\|\s*)([a-zA-Z0-9_.-]+)(?:\s*\|\s*)(?:[a-zA-Z0-9_.\s-]+\|\s*)(n8n-nodes-[a-zA-Z0-9.-]+)'
            )
            
            list_pattern = re.compile(
                r'(?:[-*•]\s+)(?:"|\')?([a-zA-Z0-9_.-]+)(?:"|\')?\s*(?::|->|→|maps to|corresponds to)\s*(?:"|\')?([a-zA-Z0-9_.-]+\.n8n-nodes-[a-zA-Z0-9.-]+)(?:"|\')?'
            )
            
            # Find all mappings from different patterns
            basic_matches = basic_mapping_pattern.findall(research_text)
            table_matches = table_pattern.findall(research_text)
            list_matches = list_pattern.findall(research_text)
            
            # Process basic pattern matches
            for make_type, n8n_type in basic_matches:
                if make_type and n8n_type and n8n_type.startswith('n8n-nodes-'):
                    discovered_mappings[make_type.lower()] = n8n_type
                    logger.info(f"Discovered mapping from research (basic): {make_type} -> {n8n_type}")
            
            # Process table pattern matches
            for make_type, n8n_type in table_matches:
                if make_type and n8n_type and n8n_type.startswith('n8n-nodes-'):
                    discovered_mappings[make_type.lower()] = n8n_type
                    logger.info(f"Discovered mapping from research (table): {make_type} -> {n8n_type}")
            
            # Process list pattern matches
            for make_type, n8n_type in list_matches:
                if make_type and n8n_type and 'n8n-nodes-' in n8n_type:
                    discovered_mappings[make_type.lower()] = n8n_type
                    logger.info(f"Discovered mapping from research (list): {make_type} -> {n8n_type}")
            
            return discovered_mappings
            
        except Exception as e:
            logger.error(f"Error parsing module mappings from research: {str(e)}", exc_info=True)
            return {}
    
    def _store_research_mappings(self, research_findings: Dict[str, Any]) -> Dict[str, str]:
        """Process research findings and store mappings in state"""
        discovered_mappings = {}
        
        # Process each research section
        for section_key, section_text in research_findings.items():
            if isinstance(section_text, str):
                # Parse section text for mappings
                section_mappings = self._parse_module_mappings_from_research(section_text)
                # Update discovered mappings
                discovered_mappings.update(section_mappings)
        
        # Store the mappings in the conversion state
        if self.current_state:
            # Update with new mappings
            self.current_state["learned_mappings"].update(discovered_mappings)
            self.current_state["conversion_logs"].append(
                f"Discovered {len(discovered_mappings)} module mappings from research"
            )
        
        return discovered_mappings


class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Make.com to n8n Converter (Crew AI)")
        self.root.geometry("800x700")
        self.converter = MakeToN8nCrewConverter()
        self.converter.set_status_callback(self.update_status)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50")
        self.style.configure("TLabel", padding=6)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # API Key input
        api_frame = ttk.Frame(main_frame)
        api_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(api_frame, text="AI API Key (optional):").pack(side=tk.LEFT, padx=5)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show="*", width=40)
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(api_frame, text="Set API Key", command=self.set_api_key).pack(side=tk.RIGHT, padx=5)
        
        # Perplexity API Key input
        perplexity_frame = ttk.Frame(main_frame)
        perplexity_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(perplexity_frame, text="Perplexity API Key:").pack(side=tk.LEFT, padx=5)
        self.perplexity_api_key_var = tk.StringVar()
        self.perplexity_api_key_entry = ttk.Entry(perplexity_frame, textvariable=self.perplexity_api_key_var, show="*", width=40)
        self.perplexity_api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(perplexity_frame, text="Set Perplexity Key", command=self.set_perplexity_api_key).pack(side=tk.RIGHT, padx=5)
        
        # File input section
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(file_frame, text="Make.com JSON File:").pack(side=tk.LEFT, padx=5)
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.file_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).pack(side=tk.RIGHT, padx=5)
        
        # Research button
        research_frame = ttk.Frame(main_frame)
        research_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(research_frame, text="Research Platforms", command=self.research_platforms).pack(side=tk.LEFT, padx=5)
        
        # Convert button
        convert_frame = ttk.Frame(main_frame)
        convert_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.convert_btn = ttk.Button(convert_frame, text="Convert to n8n", command=self.convert_file)
        self.convert_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(convert_frame, text="Save n8n JSON", command=self.save_file, state=tk.DISABLED)
        self.save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Status message
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
        # Create notebook for JSON input/output
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab for input JSON
        input_frame = ttk.Frame(self.notebook)
        self.notebook.add(input_frame, text="Make.com JSON")
        
        # Input JSON text area
        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, width=80, height=20)
        self.input_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab for output JSON
        output_frame = ttk.Frame(self.notebook)
        self.notebook.add(output_frame, text="n8n JSON")
        
        # Output JSON text area
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=80, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab for research results
        research_frame = ttk.Frame(self.notebook)
        self.notebook.add(research_frame, text="Research Results")
        
        # Research results text area
        self.research_text = scrolledtext.ScrolledText(research_frame, wrap=tk.WORD, width=80, height=20)
        self.research_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.statusbar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def set_api_key(self):
        """Set the API key for the converter"""
        api_key = self.api_key_var.get().strip()
        if api_key:
            self.converter.api_key = api_key
            self.update_status("API key set successfully")
        else:
            self.converter.api_key = None
            self.update_status("API key cleared")
    
    def set_perplexity_api_key(self):
        """Set the Perplexity API key for research"""
        api_key = self.perplexity_api_key_var.get().strip()
        if api_key:
            self.converter.set_perplexity_api_key(api_key)
            self.update_status("Perplexity API key set successfully")
        else:
            self.converter.set_perplexity_api_key(None)
            self.update_status("Perplexity API key cleared")
    
    def research_platforms(self):
        """Research platforms using Perplexity API"""
        api_key = self.perplexity_api_key_var.get().strip()
        if not api_key:
            self.update_status("Please set a Perplexity API key first")
            return
            
        # Disable UI during research
        self.progress.start()
        
        # Run research in a separate thread to keep UI responsive
        self.root.after(100, self._run_platforms_research)
    
    def _run_platforms_research(self):
        """Run the platforms research process"""
        try:
            success, result = self.converter.research_platforms()
            if success:
                self.research_text.delete(1.0, tk.END)
                self.research_text.insert(tk.END, "RESEARCH ON MAKE.COM AND N8N PLATFORMS\n")
                self.research_text.insert(tk.END, "="*50 + "\n\n")
                self.research_text.insert(tk.END, result)
                self.notebook.select(2)  # Switch to research tab
                self.update_status("Platforms research completed successfully")
            else:
                self.update_status(f"Research failed: {result}")
        except Exception as e:
            self.update_status(f"Error during research: {str(e)}")
        finally:
            self.progress.stop()
    
    def browse_file(self):
        """Open file dialog to select a Make.com JSON file"""
        file_path = filedialog.askopenfilename(
            title="Select Make.com JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.load_file(file_path)
    
    def load_file(self, file_path):
        """Load and display the selected JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_content = json.load(f)
                
            # Display the formatted JSON in the input text area
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, json.dumps(json_content, indent=2))
            self.update_status(f"Loaded file: {os.path.basename(file_path)}")
            
        except json.JSONDecodeError:
            self.update_status("Error: Invalid JSON file")
        except Exception as e:
            self.update_status(f"Error loading file: {str(e)}")
    
    def convert_file(self):
        """Convert the loaded Make.com JSON to n8n format"""
        # Get JSON content from the input text area
        try:
            input_json_str = self.input_text.get(1.0, tk.END)
            input_json = json.loads(input_json_str)
        except json.JSONDecodeError:
            self.update_status("Error: Invalid JSON in input area")
            return
        except Exception as e:
            self.update_status(f"Error processing input: {str(e)}")
            return
        
        # Disable UI during conversion
        self.convert_btn.config(state=tk.DISABLED)
        self.progress.start()
        
        # Run conversion in a separate thread to keep UI responsive
        self.root.after(100, lambda: self._run_conversion(input_json))
    
    def _run_conversion(self, input_json):
        """Run the conversion process"""
        try:
            # Perform the conversion
            success, result = self.converter.convert_json(input_json)
            
            # Process the result
            if success:
                # Display the formatted n8n JSON in the output text area
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, json.dumps(result, indent=2))
                self.update_status("Conversion completed successfully")
                self.save_btn.config(state=tk.NORMAL)
                self.notebook.select(1)  # Switch to output tab
            else:
                self.update_status(f"Conversion failed: {result}")
        except Exception as e:
            self.update_status(f"Error during conversion: {str(e)}")
        finally:
            # Re-enable UI
            self.convert_btn.config(state=tk.NORMAL)
            self.progress.stop()
    
    def save_file(self):
        """Save the converted n8n JSON to a file"""
        try:
            # Get the output JSON
            output_json_str = self.output_text.get(1.0, tk.END)
            output_json = json.loads(output_json_str)
            
            # Open save file dialog
            file_path = filedialog.asksaveasfilename(
                title="Save n8n JSON File",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(output_json, f, indent=2)
                
                self.update_status(f"Saved n8n JSON to: {os.path.basename(file_path)}")
        except json.JSONDecodeError:
            self.update_status("Error: Invalid JSON in output area")
        except Exception as e:
            self.update_status(f"Error saving file: {str(e)}")
    
    def update_status(self, message):
        """Update the status message in the UI"""
        self.status_var.set(message)
        self.statusbar.config(text=message)
        self.root.update_idletasks()


def main():
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
