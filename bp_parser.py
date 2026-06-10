"""
Blue Prism Release Parser
Extracts metadata and process information from .bprelease files
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import json
from typing import Dict, List, Any
import re

class BluePrismParser:
    """Parser for Blue Prism release files (.bprelease)"""
    
    def __init__(self):
        self.processes = []
        self.objects = []
        self.work_queues = []
        self.environment_variables = []
        self.business_objects = []
        
    def parse_release(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a Blue Prism release file and extract all metadata
        
        Args:
            file_path: Path to the .bprelease file
            
        Returns:
            Dictionary containing parsed data
        """
        try:
            # .bprelease files are XML-based
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse XML - Blue Prism files have namespaces
            root = ET.fromstring(content)
            
            # Define namespaces (Blue Prism uses multiple namespaces)
            namespaces = {
                'bpr': 'http://www.blueprism.co.uk/product/release',
                'bp': 'http://www.blueprism.co.uk/product/process',
                'env': 'http://www.blueprism.co.uk/product/environment-variable'
            }
            
            # Store namespaces for use in extraction methods
            self.namespaces = namespaces
            
            # Extract processes
            processes = self._extract_processes(root)
            
            # Extract objects
            objects = self._extract_objects(root)
            
            # Extract work queues
            work_queues = self._extract_work_queues(root)
            
            # Extract environment variables
            env_vars = self._extract_environment_variables(root)
            
            # Build comprehensive data structure
            parsed_data = {
                'file_name': file_path.name,
                'processes': processes,
                'objects': objects,
                'work_queues': work_queues,
                'environment_variables': env_vars,
                'summary': {
                    'total_processes': len(processes),
                    'total_objects': len(objects),
                    'total_work_queues': len(work_queues),
                    'total_env_vars': len(env_vars)
                }
            }
            
            return parsed_data
            
        except ET.ParseError as e:
            # If XML parsing fails, try to extract basic information
            return self._parse_as_text(file_path)
        except Exception as e:
            raise Exception(f"Error parsing Blue Prism release: {str(e)}")
    
    def _extract_processes(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract process information from XML - only top-level processes, not nested ones in objects"""
        processes = []
        
        # Get contents element
        contents = root.find('bpr:contents', self.namespaces)
        if contents is None:
            return processes
        
        # Find only direct process children of contents (not nested in objects)
        # Use bp namespace for process elements
        for process_elem in contents.findall('bp:process', self.namespaces):
            # Get the actual process element (might be nested)
            # Blue Prism structure: <process id="..." name="..."><process name="..." version="...">...</process></process>
            nested_process = process_elem.find('bp:process', self.namespaces)
            actual_process = nested_process if nested_process is not None else process_elem
            
            # Get name and ID from outer element, details from inner
            process_name = process_elem.get('name', 'Unknown Process')
            process_id = process_elem.get('id', '')
            
            # If nested process exists, it has the detailed structure
            if nested_process is not None:
                process_name = nested_process.get('name', process_name)
            
            process_data = {
                'name': process_name,
                'id': process_id,
                'description': self._get_element_text(actual_process, 'narrative') or self._get_element_text(actual_process, 'description'),
                'stages': self._extract_stages(actual_process),
                'inputs': self._extract_inputs(actual_process),
                'outputs': self._extract_outputs(actual_process),
                'exception_handling': self._extract_exception_handling(actual_process),
                'applications_used': self._extract_applications(actual_process),
                'file_operations': self._extract_file_operations(actual_process),
                'subsheets': self._extract_subsheets(actual_process),
                'data_items': self._extract_data_items(actual_process)
            }
            processes.append(process_data)
        
        return processes
    
    def _extract_objects(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract object information from XML"""
        objects = []
        
        # Get contents element
        contents = root.find('bpr:contents', self.namespaces)
        if contents is None:
            return objects
        
        # Find all object elements in contents (they use bp namespace)
        for object_elem in contents.findall('bp:object', self.namespaces):
            # Check if this is a nested object element
            nested_object = object_elem.find('bp:process', self.namespaces)
            actual_object = nested_object if nested_object is not None else object_elem
            
            object_data = {
                'name': object_elem.get('name', 'Unknown Object'),
                'id': object_elem.get('id', ''),
                'type': 'VBO',
                'description': self._get_element_text(actual_object, 'description') or self._get_element_text(actual_object, 'narrative'),
                'actions': self._extract_actions(actual_object)
            }
            objects.append(object_data)
        
        return objects
    
    def _extract_work_queues(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract work queue information"""
        queues = []
        
        # Get contents element
        contents = root.find('bpr:contents', self.namespaces)
        if contents is None:
            return queues
        
        # Work queues might use different namespaces - try multiple patterns
        # Note: The sample file has no work queues, but we search for them anyway
        for queue_elem in contents.findall('bp:workqueue', self.namespaces):
            queue_data = {
                'name': queue_elem.get('name', 'Unknown Queue'),
                'id': queue_elem.get('id', ''),
                'description': self._get_element_text(queue_elem, 'description') or self._get_element_text(queue_elem, 'narrative')
            }
            queues.append(queue_data)
        
        return queues
    
    def _extract_environment_variables(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract environment variables"""
        env_vars = []
        
        # Get contents element
        contents = root.find('bpr:contents', self.namespaces)
        if contents is None:
            return env_vars
        
        # Find all environment-variable elements in contents (they use env namespace)
        for var_elem in contents.findall('env:environment-variable', self.namespaces):
            var_data = {
                'name': var_elem.get('name', 'Unknown Variable'),
                'id': var_elem.get('id', ''),
                'type': var_elem.get('type', 'text'),
                'value': var_elem.get('value', ''),
                'description': self._get_element_text(var_elem, 'description') or ''
            }
            env_vars.append(var_data)
        
        return env_vars
    
    # REMOVED: _extract_business_objects() method - no longer needed per user request
    
    def _extract_stages(self, process_elem: ET.Element) -> List[Dict[str, Any]]:
        """Extract process stages/steps"""
        stages = []
        
        # Try multiple search patterns for stages
        stage_elements = (
            process_elem.findall('.//stage') or
            process_elem.findall('.//{http://www.blueprism.co.uk/product/process}stage') or
            process_elem.findall('.//stages/stage')
        )
        
        for stage_elem in stage_elements:
            stage_data = {
                'name': stage_elem.get('name', 'Unknown Stage'),
                'type': stage_elem.get('type', 'Action'),
                'description': self._get_element_text(stage_elem, 'narrative')
            }
            stages.append(stage_data)
        
        return stages
    
    def _extract_inputs(self, process_elem: ET.Element) -> List[str]:
        """Extract process inputs"""
        inputs = []
        
        # Try multiple search patterns
        input_elements = (
            process_elem.findall('.//input') or
            process_elem.findall('.//{http://www.blueprism.co.uk/product/process}input') or
            process_elem.findall('.//inputs/input')
        )
        
        for input_elem in input_elements:
            input_name = input_elem.get('name') or input_elem.get('item') or 'Unknown Input'
            inputs.append(input_name)
        return inputs
    
    def _extract_outputs(self, process_elem: ET.Element) -> List[str]:
        """Extract process outputs"""
        outputs = []
        
        # Try multiple search patterns
        output_elements = (
            process_elem.findall('.//output') or
            process_elem.findall('.//{http://www.blueprism.co.uk/product/process}output') or
            process_elem.findall('.//outputs/output')
        )
        
        for output_elem in output_elements:
            output_name = output_elem.get('name') or output_elem.get('item') or 'Unknown Output'
            outputs.append(output_name)
        return outputs
    
    def _extract_subsheets(self, process_elem: ET.Element) -> List[str]:
        """Extract subsheets/subprocesses"""
        subsheets = []
        
        # Look for subsheet elements
        subsheet_elements = (
            process_elem.findall('.//subsheet') or
            process_elem.findall('.//{http://www.blueprism.co.uk/product/process}subsheet') or
            process_elem.findall('.//subsheets/subsheet')
        )
        
        for subsheet_elem in subsheet_elements:
            subsheet_name = subsheet_elem.get('name') or subsheet_elem.get('subsheetid') or 'Unknown Subsheet'
            subsheets.append(subsheet_name)
        
        return subsheets
    
    def _extract_data_items(self, process_elem: ET.Element) -> List[Dict[str, str]]:
        """Extract data items/variables"""
        data_items = []
        
        # Look for data item elements
        data_elements = (
            process_elem.findall('.//data') or
            process_elem.findall('.//{http://www.blueprism.co.uk/product/process}data') or
            process_elem.findall('.//initialvalues/data')
        )
        
        for data_elem in data_elements:
            data_item = {
                'name': data_elem.get('name', 'Unknown Data Item'),
                'type': data_elem.get('type', 'text'),
                'exposure': data_elem.get('exposure', 'internal')
            }
            data_items.append(data_item)
        
        return data_items
    
    def _extract_exception_handling(self, process_elem: ET.Element) -> Dict[str, Any]:
        """Extract exception handling information"""
        exception_stages = []
        
        # Try multiple search patterns for exception stages
        stage_elements = (
            process_elem.findall('.//stage') or
            process_elem.findall('.//{http://www.blueprism.co.uk/product/process}stage') or
            []
        )
        
        for stage in stage_elements:
            stage_type = stage.get('type', '')
            stage_name = stage.get('name', '')
            
            # Look for exception-related stages
            if stage_type.lower() in ['exception', 'recover', 'resume']:
                exception_stages.append(stage_name or 'Unknown Exception')
            elif 'exception' in stage_name.lower() or 'error' in stage_name.lower():
                exception_stages.append(stage_name)
        
        return {
            'has_exception_handling': len(exception_stages) > 0,
            'exception_stages': exception_stages
        }
    
    def _extract_applications(self, process_elem: ET.Element) -> List[str]:
        """Extract applications used in the process"""
        applications = set()
        
        # Try multiple search patterns for stages
        stage_elements = (
            process_elem.findall('.//stage') or
            process_elem.findall('.//{http://www.blueprism.co.uk/product/process}stage') or
            []
        )
        
        # Look for application references in stages
        for stage in stage_elements:
            stage_type = stage.get('type', '')
            narrative = self._get_element_text(stage, 'narrative')
            
            # Common application patterns
            if 'SAP' in narrative or 'SAP' in stage_type:
                applications.add('SAP')
            if 'Excel' in narrative or 'Excel' in stage_type:
                applications.add('Microsoft Excel')
            if 'Outlook' in narrative or 'Email' in stage_type:
                applications.add('Microsoft Outlook')
            if 'Oracle' in narrative:
                applications.add('Oracle')
            if 'Web' in stage_type or 'Browser' in narrative:
                applications.add('Web Browser')
        
        # Also look for appdef (application definition) elements
        appdef_elements = (
            process_elem.findall('.//appdef') or
            process_elem.findall('.//{http://www.blueprism.co.uk/product/process}appdef') or
            []
        )
        
        for appdef in appdef_elements:
            app_name = appdef.get('name') or appdef.get('id', '')
            if app_name:
                applications.add(app_name)
        
        return list(applications)
    
    def _extract_file_operations(self, process_elem: ET.Element) -> List[str]:
        """Extract file operations"""
        file_operations = []
        
        # Try multiple search patterns for stages
        stage_elements = (
            process_elem.findall('.//stage') or
            process_elem.findall('.//{http://www.blueprism.co.uk/product/process}stage') or
            []
        )
        
        for stage in stage_elements:
            narrative = self._get_element_text(stage, 'narrative')
            stage_name = stage.get('name', '')
            
            # Look for file-related keywords
            if any(keyword in narrative.lower() for keyword in ['file', 'excel', 'csv', 'pdf', 'xml', 'json']):
                file_operations.append(f"{stage_name}: {narrative}")
            elif any(keyword in stage_name.lower() for keyword in ['file', 'excel', 'csv', 'pdf', 'xml', 'json']):
                file_operations.append(stage_name)
        
        return file_operations
    
    def _extract_actions(self, object_elem: ET.Element) -> List[str]:
        """Extract actions from an object"""
        actions = []
        
        # Try multiple search patterns for actions
        action_elements = (
            object_elem.findall('.//action') or
            object_elem.findall('.//{http://www.blueprism.co.uk/product/process}action') or
            []
        )
        
        for action_elem in action_elements:
            action_name = action_elem.get('name', 'Unknown Action')
            actions.append(action_name)
        
        return actions
    
    def _get_element_text(self, parent: ET.Element, tag: str) -> str:
        """Safely get text from an XML element"""
        elem = parent.find(tag)
        return elem.text if elem is not None and elem.text else ''
    
    def _parse_as_text(self, file_path: Path) -> Dict[str, Any]:
        """Fallback parser for non-XML or corrupted files"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Try to extract basic information using regex
        process_names = re.findall(r'<process[^>]*name="([^"]*)"', content)
        object_names = re.findall(r'<object[^>]*name="([^"]*)"', content)
        
        return {
            'file_name': file_path.name,
            'processes': [{'name': name, 'stages': [], 'inputs': [], 'outputs': []} for name in process_names],
            'objects': [{'name': name, 'actions': []} for name in object_names],
            'work_queues': [],
            'environment_variables': [],
            'summary': {
                'total_processes': len(process_names),
                'total_objects': len(object_names),
                'total_work_queues': 0,
                'total_env_vars': 0
            }
        }
    
    # REMOVED: _create_sample_process() method
    # This was causing all files to produce the same output
    # Now the parser only returns actual data from the uploaded file

