"""
Report Generator
Generates comprehensive migration assessment reports in Excel format
"""

import os
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
import json
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.styles import Alignment
    from openpyxl.styles import Font
    from openpyxl.styles.colors import Color
    from openpyxl.styles import PatternFill
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


wrap_alignment = Alignment(wrap_text=True)
class ReportGenerator:
    """
    Generates comprehensive migration assessment reports in Excel format
    """
    
    def __init__(self):
        """Initialize the Report Generator"""
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_report(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive migration assessment report
        
        Args:
            analysis_results: Complete analysis results from all agents
            
        Returns:
            Path to the generated report file
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if EXCEL_AVAILABLE:
                # Generate Excel report
                filename = f"Migration_Assessment_Report_{timestamp}.xlsx"
                filepath = self.output_dir / filename
                self._generate_excel_report(analysis_results, filepath)
            else:
                # Fallback to text report
                filename = f"Migration_Assessment_Report_{timestamp}.txt"
                filepath = self.output_dir / filename
                report_content = self._build_report_content(analysis_results)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(report_content)
            
            return str(filepath)
            
        except Exception as e:
            raise Exception(f"Error generating report: {str(e)}")
    
    def _generate_excel_report(self, results: Dict[str, Any], filepath: Path):
        """Generate Excel report with multiple sheets"""
        wb = openpyxl.Workbook()
        
        # Remove default sheet
        if 'Sheet' in wb.sheetnames:
            wb.remove(wb['Sheet'])
        
        # Create sheets
        self._create_executive_summary_sheet(wb, results)
        self._create_bp_summary_sheet(wb, results)
        self._create_process_overview_sheet(wb, results)
        self._create_complexity_sheet(wb, results)
        self._create_dependency_sheet(wb, results)
        self._create_migration_mapping_sheet(wb, results)
        self._create_effort_estimation_sheet(wb, results)
        
        # Save workbook
        wb.save(filepath)
    
    
    
    def _create_executive_summary_sheet(self, wb, results):
        """Create Executive Summary sheet"""
        ws = wb.create_sheet("Executive Summary")
        
        # Header styling
        header_fill = PatternFill(start_color="1F77B4", end_color="1F77B4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=14)
        
        # Title
        cell = ws['A1']
        cell.value = "RPA DISCOVERY INTELLIGENCE PLATFORM"
        cell.font = Font(bold=True, size=16, color="1F77B4")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.merge_cells('A1:B1')
        cell = ws['A2']
        cell.value = "Migration Assessment Report"
        cell.font = Font(bold=True, size=14,color="000000")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.merge_cells('A2:B2')
        
        # Report Info
        row = 4
        cell=ws[f'A{row}']
        cell.value = "Report Generated:"
        cell.font = Font(bold=True,color="969696")
        cell=ws[f'B{row}']
        cell.value = results.get('analysis_date', 'N/A')
        cell.font = Font(bold=True,color="969696")
        row += 1
        cell=ws[f'A{row}']
        cell.value = "Source Platform:"
        cell.font = Font(bold=True,color="969696")
        cell=ws[f'B{row}']
        cell.value = results.get('source_platform', 'N/A')
        cell.font = Font(bold=True,color="969696")
        row += 1
        cell=ws[f'A{row}']
        cell.value = "Target Platform:"
        cell.font = Font(bold=True,color="969696")
        cell=ws[f'B{row}']
        cell.value = results.get('target_platform', 'N/A')
        cell.font = Font(bold=True,color="969696")
        row += 1
        cell=ws[f'A{row}']
        cell.value = "Release File:"
        cell.font = Font(bold=True,color="969696")
        cell=ws[f'B{row}']
        cell.value = results.get('file_name', 'N/A')
        cell.font = Font(bold=True,color="969696")
        # Portfolio Overview
        row += 3
        cell=ws[f'A{row}']
        cell.value = "Portfolio Overview"
        cell.font = header_font
        cell.fill = header_fill
        ws.merge_cells(f'A{row}:B{row}')
        
        process_analysis = results.get('process_analysis', {})
        complexity = results.get('complexity_assessment', {})
        effort = results.get('effort_estimation', {})
        parsed_data=results.get('parsed_data',{})
        
        row += 1
        cell=ws[f'A{row}']
        cell.value = "Total Processes"
        cell.font = Font(bold=True,color="969696")
        cell=ws[f'B{row}']
        cell.value = process_analysis.get('process_count', 0)
        cell.font = Font(bold=True,color="969696")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        row += 1
        cell=ws[f'A{row}']
        cell.value = "Total Objects"
        cell.font = Font(bold=True,color="969696")
        cell=ws[f'B{row}']
        cell.value = parsed_data.get('summary', {}).get('total_objects', 0)
        cell.font = Font(bold=True,color="969696")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        row += 1
        cell=ws[f'A{row}']
        cell.value = "Overall Complexity"
        cell.font = Font(bold=True,color="969696")
        cell=ws[f'B{row}']
        cell.value = complexity.get('overall_complexity', 'N/A')
        cell.font = Font(bold=True,color="969696")
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
        
        # Effort Estimate
        row += 3
        cell=ws[f'A{row}']
        cell.value = "Effort Estimate(Timeline)"
        cell.font = header_font
        cell.fill = header_fill
        ws.merge_cells(f'A{row}:B{row}')
        
        row += 1
        cell=ws[f'A{row}']
        cell.value = "Total Effort"
        cell.font = Font(bold=True,color="969696")
        cell=ws[f'B{row}']
        cell.value = f"{effort.get('total_hours', 0)} hours ({effort.get('total_weeks', 0)} weeks)"
        cell.font = Font(bold=True,color="969696")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        row += 1
        cell=ws[f'A{row}']
        cell.value = "Estimated Weeks (with Buffer)"
        cell.font = Font(bold=True,color="969696")
        cell=ws[f'B{row}']
        cell.value = f"{effort.get('timeline', {}).get('with_buffer', 0)} weeks"
        cell.font = Font(bold=True,color="969696")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        row += 1
        cell=ws[f'A{row}']
        cell.value = "Estimated Months"
        cell.font = Font(bold=True,color="969696")
        cell=ws[f'B{row}']
        cell.value = f"{effort.get('timeline', {}).get('estimated_months', 0)} months"
        cell.font = Font(bold=True,color="969696")
        cell.alignment = Alignment(horizontal="center", vertical="center")
 
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 40
    
    def _create_bp_summary_sheet(self, wb, results):
        """Create Blue Prism Summary sheet"""
        ws = wb.create_sheet("Blue Prism Summary")
        
        # Headers
        headers = ["BP Processes", "BP Objects", "BP Environment Variables", "Value"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="1F77B4", end_color="1F77B4", fill_type="solid")
        # Data
        parsed_data = results.get('parsed_data', {})
        bp_processes = parsed_data.get('processes', [])
        bp_objects = parsed_data.get('objects', [])
        bp_env_vars = parsed_data.get('environment_variables', [])
        
        for row, process in enumerate(bp_processes, 2):
            ws.cell(row=row, column=1, value=process.get('name', 'None'))
            
        for row, object in enumerate(bp_objects, 2):
            ws.cell(row=row, column=2, value=object.get('name', 'None'))
        
        for row, env_var in enumerate(bp_env_vars, 2):
            ws.cell(row=row, column=3, value=env_var.get('name', 'None'))
            ws.cell(row=row, column=4, value=env_var.get('value', 'None'))
        
        autofit_all_columns(ws)
        
    def _create_process_overview_sheet(self, wb, results):
        """Create Process Overview sheet"""
        ws = wb.create_sheet("Process Overview")
        
        # Headers
        headers = ["Process Name", "Description", "High Level Process Steps"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="1F77B4", end_color="1F77B4", fill_type="solid")
        
        # Data
        process_analysis = results.get('process_analysis', {})
        processes = process_analysis.get('processes', [])
        
        
        
        for row, process in enumerate(processes, 2):
            ws.cell(row=row, column=1, value=process.get('process_name', 'None'))
            
            ws.cell(row=row, column=2, value=process.get('description', 'None')).alignment = wrap_alignment
            
            
            process_steps=process.get('ai_generated_steps', [])
            
            for row, step in enumerate(process_steps, 2):
                ws.cell(row=row, column=3, value=f"{row-1}. {step}")

        ws.column_dimensions["A"].width = 50
        ws.column_dimensions["B"].width = 60
        ws.column_dimensions["C"].width = 70
    
    def _create_complexity_sheet(self, wb, results):
        """Create Complexity Assessment sheet"""
        ws = wb.create_sheet("Complexity Assessment")
        
        complexity = results.get('complexity_assessment', {})
        
        # Overall metrics
        ws.column_dimensions["A"].width = 23
        ws.column_dimensions["B"].width = 18
        ws.column_dimensions["C"].width = 10
        ws['A1'] = "Overall Complexity Rating"
        ws['B1'] = complexity.get('overall_complexity', 'N/A')
        ws['A1'].font = Font(bold=True, color="FFFFFF")
        ws['A1'].fill = PatternFill(
        start_color="1F77B4",
        end_color="1F77B4",
        fill_type="solid"
        )
        
        ws['B1'].font = Font(bold=True, color="000000")
        ws['B1'].fill = PatternFill(
        start_color="FFFF00",
        end_color="FFFF00",
        fill_type="solid"
        )
        
        #ws['A2'] = "Overall Complexity Score"
        #ws['B2'] = f"{complexity.get('overall_score', 0)}"
        
        # Process assessments
        ws['B4'] = "Key Components"
        ws['B4'].font = Font(bold=True, color="FFFFFF")
        ws['B4'].fill = PatternFill(
        start_color="969696",
        end_color="969696",
        fill_type="solid"
        )
        
        ws['C4'] = "Value"
        ws['C4'].font = Font(bold=True, color="FFFFFF")
        ws['C4'].fill = PatternFill(
        start_color="969696",
        end_color="969696",
        fill_type="solid"
        )
        
        ws['D4'] = "Analysis"
        ws['D4'].font = Font(bold=True, color="FFFFFF")
        ws['D4'].fill = PatternFill(
        start_color="969696",
        end_color="969696",
        fill_type="solid"
        )
    
        ws['A5'] = "AI Insights"
        ws['A5'].font = Font(bold=True, color="FFFFFF")
        ws['A5'].fill = PatternFill(
        start_color="1F77B4",
        end_color="1F77B4",
        fill_type="solid"
        )
        
        row = 5
        
        metrics = complexity.get("ai_metric_analysis", {}).get("metric_counts", {})
        
        for row, (key, value) in enumerate(metrics.items(), start=row):
            ws.cell(row=row, column=2, value=f"{key.replace('_',' ').title()}").font = Font(bold=True)
            ws.cell(row=row, column=3, value=value).font = Font(bold=True)
        
        row = 5
        
        analysis = complexity.get("ai_metric_analysis", {})
        rationale = analysis.get("count_rationale", {}) 
        ws.column_dimensions["D"].width = 150        
        for row, (k, v) in enumerate(rationale.items(), start=row):
            ws.cell(row=row, column=4, value=f"{k.replace('_',' ').title()}: {v}").alignment = wrap_alignment
        
        row += 3
        
        cell = ws.cell(row=row, column=1, value="Assumptions")
        
        cell.font = Font(
        bold=True,
        color="FFFFFF" 
        )

        cell.fill = PatternFill(
        start_color="1F77B4", 
        end_color="1F77B4",
        fill_type="solid"
        )
        
        risk_factors = complexity.get('risk_factors', []) 
        
        serial_number = 1
        for row, factor in enumerate(risk_factors, row):
            ws.cell(row=row, column=3, value=serial_number).font = Font(bold=True)
            ws.cell(row=row, column=4, value=factor).alignment = wrap_alignment
            serial_number += 1      
    
                      
                
    
    def _create_dependency_sheet(self, wb, results):
        """Create Dependency Analysis sheet"""
        ws = wb.create_sheet("Dependency Analysis")
        
        # Headers
        headers = ["Applications", "File Dependencies","APIs", "Integrations"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="1F77B4", end_color="1F77B4", fill_type="solid")
        
        dependency = results.get('dependency_analysis', {})
        apps = dependency.get('applications', [])
        Files = dependency.get('files', [])
        APIs = dependency.get('apis', [])
        Integrations = dependency.get('integrations', [])
        # Applications
        row = 2
        for row, app in enumerate(apps, 2):
            ws.cell(row=row, column=1, value=app)
        # Files
        row = 2
        for row, file in enumerate(Files, 2):
            ws.cell(row=row, column=2, value=file)   
        # APIs
        row = 2
        for row, api in enumerate(APIs, 2):
            ws.cell(row=row, column=3, value=api)
        # Integrations
        row = 2
        for row, integration in enumerate(Integrations, 2):
            ws.cell(row=row, column=4, value=integration.get('name', 'None'))
        
        ws.column_dimensions["A"].width = 50
        ws.column_dimensions["B"].width = 50
        ws.column_dimensions["C"].width = 50
        ws.column_dimensions["D"].width = 70
    
    def _create_migration_mapping_sheet(self, wb, results):
        """Create Migration Mapping sheet"""
        ws = wb.create_sheet("Migration Mapping")
        
        mapping = results.get('migration_mapping', {})
        comp_mapping = mapping.get('component_mappings', [])
        process_mapping = mapping.get('process_mappings', [])
        arch_mapping = mapping.get('architecture_recommendations', [])
        opps_mapping = mapping.get('modernization_opportunities', [])
        
        row = 1
        
        headers = ["Source", "Target","Mapping Type", "Migration Notes"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="1F77B4", end_color="1F77B4", fill_type="solid")
    
        # Process Mappings
        for row, proc_map in enumerate(process_mapping, 2):
            ws.cell(row=row, column=1, value=proc_map.get('source_process', 'None'))
            ws.cell(row=row, column=2, value=proc_map.get('target_component', 'None'))
            ws.cell(row=row, column=3, value='Process')
            ws.cell(row=row, column=4, value=proc_map.get('recommended_approach', 'None')).alignment = wrap_alignment
        # Component Mappings
        row += 1
        for row, comp_map in enumerate(comp_mapping, row):
            ws.cell(row=row, column=1, value=comp_map.get('source_component', 'None'))
            ws.cell(row=row, column=2, value=comp_map.get('target_component', 'None'))
            ws.cell(row=row, column=3, value='Component')
            ws.cell(row=row, column=4, value=comp_map.get('migration_notes', 'None')).alignment = wrap_alignment
        # Architecture recommendation
        row += 1
        for row, arch_map in enumerate(arch_mapping, row):
            ws.cell(row=row, column=1, value='Architecture recommendation')
            ws.cell(row=row, column=2, value='-')
            ws.cell(row=row, column=3, value='-')
            ws.cell(row=row, column=4, value=arch_map).alignment = wrap_alignment     
        # Modernization opportunities
        row += 1
        for row, opps_map in enumerate(opps_mapping, row):
            ws.cell(row=row, column=1, value='Modernization opportunities')
            ws.cell(row=row, column=2, value='-')
            ws.cell(row=row, column=3, value='-')
            ws.cell(row=row, column=4, value=opps_map).alignment = wrap_alignment            
        
        ws.column_dimensions["A"].width = 50
        ws.column_dimensions["B"].width = 50
        ws.column_dimensions["C"].width = 15
        ws.column_dimensions["D"].width = 90        
        
    
    def _create_effort_estimation_sheet(self, wb, results):
        """Create Effort Estimation sheet"""
        ws = wb.create_sheet("Effort Estimation")
        
        effort = results.get('effort_estimation', {})
        
        row = 1
        

        
        
        # Summary
        cell = ws['A1']
        cell.value = "Effort Summary"
        cell.font = Font(bold=True, size=12,color="FFFFFF")
        cell.fill = PatternFill(start_color="1F77B4", end_color="1F77B4", fill_type="solid")
        
        ws['A2'] = "Total Hours"
        ws['B2'] = effort.get('total_hours', 0)
        ws['A3'] = "Total Days"
        ws['B3'] = effort.get('total_days', 0)
        ws['A4'] = "Total Weeks"
        ws['B4'] = effort.get('total_weeks', 0)
        
        # Effort Breakdown
        row = 7
        cell = ws[f'A{row}']
        cell.value = "Effort Breakdown"
        cell.font = Font(bold=True, size=12,color="FFFFFF")
        cell.fill = PatternFill(start_color="1F77B4", end_color="1F77B4", fill_type="solid")
        row += 1
        
        breakdown = effort.get('effort_breakdown', {})
        for activity, hours in breakdown.items():
            ws.cell(row=row, column=1, value=activity.replace('_', ' ').title())
            ws.cell(row=row, column=2, value=f"{hours} hours")
            row += 1
        
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 20
    

def autofit_all_columns(ws):
        for col in ws.columns:
            max_length = 0
            col_letter = get_column_letter(col[0].column)

            for cell in col:
                if cell.value is not None:
                    max_length = max(max_length, len(str(cell.value)))

            ws.column_dimensions[col_letter].width = max_length + 2