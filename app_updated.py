"""
RPA Discovery Intelligence Platform
Main Streamlit Application for Blue Prism to Power Automate Migration Assessment
"""

from urllib import response

import streamlit as st
import os
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
import json
from io import BytesIO
from openpyxl import load_workbook
from dotenv import load_dotenv
import pandas as pd
from PIL import Image

# Load environment variables
load_dotenv()

# Configuration
Effort_Matrix_File = os.getenv("Effort_Matrix_File", "")
Mapping_File = os.getenv("Mapping_File", "")
Complexity_Matrix_File = os.getenv("Complexity_Matrix_File", "")


# Import modules
from ica_agent import (
    ICAAgentClient,
    ProcessAnalyzerAgent,
    ComplexityAssessorAgent,
    DependencyAnalyzerAgent,
    MigrationMapperAgent,
    EffortEstimatorAgent
)
from report_generator import ReportGenerator
from bp_parser import BluePrismParser

# Page configuration
st.set_page_config(
    page_title="RPA Discovery Intelligence Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .agent-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .under-development {
        background-color: #fff3cd;
        padding: 3rem;
        border-radius: 10px;
        text-align: center;
        border: 2px dashed #ffc107;
    }
    /* Reduce metric value font size */
    [data-testid="stMetricValue"] {
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'complexity_metrics_data' not in st.session_state:
    st.session_state.complexity_metrics_data = None
if 'complexity_metrics_filename' not in st.session_state:
    st.session_state.complexity_metrics_filename = None

def main():
    # Header
    st.markdown('<div class="main-header">🤖 RPA Discovery Intelligence Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">An Agentic AI Solution for Automation Portfolio Discovery, Complexity Assessment, and Migration Readiness</div>', unsafe_allow_html=True)
    
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if "effort_matrix" not in st.session_state:
        st.session_state.effort_matrix = load_effort_matrix()
    if "migration_mapping" not in st.session_state:
        st.session_state.migration_mapping = load_mapping()


    if st.session_state.complexity_metrics_data is None:
        st.session_state.complexity_metrics_data = load_complexity_matrix()
        st.session_state.complexity_metrics_filename = os.path.basename(Complexity_Matrix_File) if Complexity_Matrix_File else None
    
    
    # Sidebar
    with st.sidebar:
        st.sidebar.image("newlogo.png", width=180)
        #st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=IBM+Consulting", use_container_width=True)
        if st.button("🏠 Home"):
            st.session_state.page = "home"
            st.rerun() 
        st.markdown("### ⚙️ Configuration")
        if st.button("📊 Effort Matrix"):
            st.session_state.page = "effort_matrix"
            st.rerun()
        if st.button("🗃️ Migration Mapping"):
            st.session_state.page = "migration_mapping"
            st.rerun()
        if st.button("🧮 Complexity Matrix"):
            st.session_state.page = "complexity_matrix"
            st.rerun()

       
        st.markdown("---")
        st.markdown("### 📋 Platform Features")
        st.markdown("""
        - ✅ AI-Powered Analysis
        - ✅ Complexity Assessment
        - ✅ Dependency Mapping
        - ✅ Effort Estimation
        - ✅ Migration Mapping
        - 🔃 Multi-Platform Discovery
        """)
        st.markdown("---")
        st.markdown("### 🔧 Supported Platforms")
        st.markdown("""
        **Source:**
        - Blue Prism ✓
        - Automation Anywhere (Coming Soon)
        - UiPath (Coming Soon)
        - Power Automate (Coming Soon)
        
        **Target:**
        - Power Automate ✓
        - Automation Anywhere (Coming Soon)
        - UiPath (Coming Soon)
        - Blue Prism (Coming Soon)
        """)
        
    # =====================================================
    # Effort Matrix Page
    # =====================================================

    if st.session_state.page == "effort_matrix":

        st.title("📊 Effort Matrix Configuration")

        st.info(
        "Update the effort matrix values and click Save.")
        
        # ALWAYS reload fresh from session_state
        df = st.session_state.effort_matrix

        #edited_df = st.data_editor(st.session_state.effort_matrix,use_container_width=True,num_rows="fixed")

        edited_df = st.data_editor(df,
        use_container_width=True,
        num_rows="fixed",
        key="effort_editor")

        col1, col2 = st.columns([1, 1])

        with col1:

            if st.button("💾 Save Changes", type="primary"):

                # Update session state
                st.session_state.effort_matrix = edited_df

                # Save to JSON
                save_effort_matrix(edited_df)
                
                st.success("Effort Matrix saved successfully.")

                # Navigate back to Home
                st.session_state.page = "home"

                st.rerun()

        with col2:

            if st.button("❌ Cancel"):
                st.session_state.page = "home"
                st.rerun()
                
    # =====================================================
    # Migration Mapping Page
    # =====================================================

    if st.session_state.page == "migration_mapping":

        st.title("🗃️ Migration Mapping")

        st.info(
        "Update the migration mappings and click Save.")
        
        # ALWAYS reload fresh from session_state
        mapping_df = st.session_state.migration_mapping

        #edited_df = st.data_editor(st.session_state.migration_mapping,use_container_width=True,num_rows="fixed")

        edited_mapping_df = st.data_editor(mapping_df,
        use_container_width=True,
        num_rows="fixed",
        key="migration_editor")

        col1, col2 = st.columns([1, 1])

        with col1:

            if st.button("💾 Save Changes", type="primary"):

                # Update session state
                st.session_state.migration_mapping = edited_mapping_df

                # Save to JSON
                save_mapping(edited_mapping_df)
                
                st.success("Migration Mapping saved successfully.")

                # Navigate back to Home
                st.session_state.page = "home"

                st.rerun()

        with col2:

            if st.button("❌ Cancel"):
                st.session_state.page = "home"
                st.rerun()

    # =====================================================

    if st.session_state.page == "complexity_matrix":

        st.title("🧮 Complexity Matrix Configuration")

        st.info("The complexity matrix is loaded from the path configured in your .env file (Complexity_Matrix_File). Upload a new file below to replace it.")

        uploaded_complexity = st.file_uploader(
            "Replace complexity matrix file (.xlsx)",
            type=["xlsx"],
            help="Upload a new .xlsx file to replace the current complexity matrix at the configured path.",
            key="complexity_matrix_replace_uploader"
        )
    
        if uploaded_complexity is not None:
            try:
                with open(Complexity_Matrix_File, "wb") as f:
                    f.write(uploaded_complexity.getbuffer())
                st.session_state.complexity_metrics_data = load_complexity_matrix()
                st.session_state.complexity_metrics_filename = uploaded_complexity.name
                st.success(f"✅ Complexity matrix replaced with: {uploaded_complexity.name}")
            except Exception as e:
                st.error(f"❌ Failed to replace complexity matrix: {str(e)}")

        if st.session_state.complexity_metrics_data:
            st.markdown(f"**Active file:** `{st.session_state.complexity_metrics_filename}`")
            #with st.expander("📋 View Loaded Complexity Matrix Summary"):
            #    st.json(st.session_state.complexity_metrics_data)
        else:
            st.warning("⚠️ No complexity matrix loaded. Ensure Complexity_Matrix_File is set correctly in your .env file.")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 Reload from File", type="primary"):
                st.session_state.complexity_metrics_data = load_complexity_matrix()
                st.session_state.complexity_metrics_filename = os.path.basename(Complexity_Matrix_File) if Complexity_Matrix_File else None
                st.success("✅ Complexity matrix reloaded from file.")
                st.session_state.page = "home"
                st.rerun()
            # Image displayed below the button
            st.image(
            "ComplexityMatrix.png",
            caption="Complexity Matrix",
            use_container_width=True)
        
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.page = "home"
                st.rerun()


    # =====================================================
    # Home Page
    # =====================================================

    if st.session_state.page == "home":
    
    # Main content
        st.markdown("## 🎯 Migration Assessment Configuration")
    
        # Platform selection
        col1, col2 = st.columns(2)
    
        with col1:
            source_platform = st.selectbox(
            "📤 Select Source Platform",
            ["Blue Prism", "Automation Anywhere 360", "UiPath", "Power Automate"],
            help="Select the RPA platform you are migrating FROM")
    
        with col2:
            target_platform = st.selectbox(
            "📥 Select Target Platform",
            ["Power Automate", "Automation Anywhere 360", "UiPath", "Blue Prism"],
            help="Select the RPA platform you are migrating TO")
    
        # Check if Blue Prism to Power Automate is selected
        if source_platform == "Blue Prism" and target_platform == "Power Automate":
            show_bp_to_pa_migration()
        else:
            show_under_development(source_platform, target_platform)

def summarize_complexity_metrics_excel(uploaded_excel_file):
    """Read full workbook content and matrix cells for workbook-driven complexity scoring."""
    workbook_values = load_workbook(filename=BytesIO(uploaded_excel_file.getvalue()), data_only=True, read_only=False)
    workbook_formulas = load_workbook(filename=BytesIO(uploaded_excel_file.getvalue()), data_only=False, read_only=False)
    
    summary = {
        "workbook_name": uploaded_excel_file.name,
        "sheet_names": workbook_values.sheetnames,
        "sheets": {},
        "matrix_cells": {}
    }
    
    for worksheet in workbook_values.worksheets:
        rows = []
        for row in worksheet.iter_rows(values_only=True):
            rows.append(["" if cell is None else str(cell) for cell in row])
        
        summary["sheets"][worksheet.title] = {
            "row_count": len(rows),
            "rows": rows,
            "preview_rows": rows[:25]
        }
    
    matrix_sheet_values = workbook_values["Complexity Matrix"] if "Complexity Matrix" in workbook_values.sheetnames else None
    matrix_sheet_formulas = workbook_formulas["Complexity Matrix"] if "Complexity Matrix" in workbook_formulas.sheetnames else None
    
    if matrix_sheet_values and matrix_sheet_formulas:
        tracked_cells = [
            "I17", "I18", "I19", "I20", "I21",
            "AI17", "AJ17", "AK17", "AL17", "AM17",
            "AI18", "AJ18", "AK18", "AL18", "AM18",
            "AI19", "AJ19", "AK19", "AL19", "AM19",
            "AI20", "AJ20", "AK20", "AL20", "AM20",
            "AI21", "AJ21", "AK21", "AL21", "AM21",
            "AC17", "AD17", "AE17", "AF17", "AG17",
            "AC18", "AD18", "AE18", "AF18", "AG18",
            "AC19", "AD19", "AE19", "AF19", "AG19",
            "AC20", "AD20", "AE20", "AF20", "AG20",
            "AC21", "AD21", "AE21", "AF21", "AG21",
            "AC22", "AD22", "AE22", "AF22", "AG22",
            "AQ16", "AR16", "AQ17", "AR17", "AQ18", "AR18", "AQ19", "AR19", "AQ20", "AR20", "AP20"
        ]
        for cell_ref in tracked_cells:
            summary["matrix_cells"][cell_ref] = {
                "value": matrix_sheet_values[cell_ref].value,
                "formula": matrix_sheet_formulas[cell_ref].value
            }
    
    return summary


def _normalize_text_list(values):
    return [str(v).strip() for v in values if str(v).strip()]


def _get_sheet_rows(complexity_metrics_data, sheet_name):
    return complexity_metrics_data.get("sheets", {}).get(sheet_name, {}).get("rows", [])


def _count_sheet_entries(rows):
    return len([
        row for row in rows
        if row and any(str(cell).strip() for cell in row)
    ])


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_complexity_label(label):
    normalized = str(label or "").strip().upper()
    mapping = {
        "VERY SIMPLE": "Extra Simple",
        "EXTRA SIMPLE": "Extra Simple",
        "SIMPLE": "Simple",
        "MEDIUM": "Medium",
        "COMPLEX": "Complex",
        "VERY COMPLEX": "Extra Complex",
        "EXTRA COMPLEX": "Extra Complex"
    }
    return mapping.get(normalized, str(label or "").strip().title() or "Unknown")


def _classify_from_equivalence(matrix_score, matrix_cells):
  
    ap20 = _safe_float(matrix_cells.get("AP20", {}).get("value"))
    aq16 = _safe_float(matrix_cells.get("AQ16", {}).get("value"))
    aq17 = _safe_float(matrix_cells.get("AQ17", {}).get("value"))
    aq18 = _safe_float(matrix_cells.get("AQ18", {}).get("value"))
    aq19 = _safe_float(matrix_cells.get("AQ19", {}).get("value"))
    ap20 = _safe_float(matrix_cells.get("AP20", {}).get("value"), aq19)

    if matrix_score == 0:
        return "No Data"
    # Score ranges: [0, aq16) = VERY SIMPLE, [aq16, aq17) = SIMPLE, [aq17, aq18) = MEDIUM, [aq18, aq19) = COMPLEX, [aq19+) = VERY COMPLEX
    if matrix_score < aq16:
        return _normalize_complexity_label(matrix_cells.get("AR16", {}).get("value"))
    elif matrix_score < aq17:
        return _normalize_complexity_label(matrix_cells.get("AR17", {}).get("value"))
    elif matrix_score < aq18:
        return _normalize_complexity_label(matrix_cells.get("AR18", {}).get("value"))
    elif matrix_score < aq19:
        return _normalize_complexity_label(matrix_cells.get("AR19", {}).get("value"))
    elif matrix_score >= ap20:
        return _normalize_complexity_label(matrix_cells.get("AR20", {}).get("value"))
    else:
        return _normalize_complexity_label(matrix_cells.get("AR19", {}).get("value"))


def _bucket_metric(metric_name, count):
    if metric_name == "interface":
        if count <= 1:
            return "ES"
        if count == 2:
            return "S"
        if 3 <= count <= 4:
            return "M"
        if 5 <= count <= 6:
            return "C"
        return "XC"

    if metric_name == "activities":
        if count <= 4:
            return "ES"
        if count <= 10:
            return "S"
        if count <= 20:
            return "M"
        if count <= 40:
            return "C"
        return "XC"

    if metric_name == "data_transformation":
        if count <= 5:
            return "ES"
        if count <= 10:
            return "S"
        if count <= 20:
            return "M"
        if count <= 40:
            return "C"
        return "XC"

    if metric_name == "digital_layouts":
        if count <= 2:
            return "ES"
        if count <= 4:
            return "S"
        if count <= 6:
            return "M"
        if count <= 10:
            return "C"
        return "XC"

    if metric_name == "process_flows":
        if count <= 2:
            return "ES"
        if count <= 4:
            return "S"
        if count <= 6:
            return "M"
        if count <= 8:
            return "C"
        return "XC"

    return "ES"


def compute_workbook_complexity(parsed_data, process_analysis, complexity_metrics_data, metric_counts=None, agent_risk_factors=None, count_rationale=None):
    """Compute complexity from workbook matrix using AI-derived metric counts and workbook formulas."""
    processes = parsed_data.get("processes", [])
    process_result = process_analysis.get("processes", [{}])
    process_info = process_result[0] if process_result else {}
    matrix_cells = complexity_metrics_data.get("matrix_cells", {})

    metric_counts = metric_counts or {}
    metric_counts = {
        "interface": int(metric_counts.get("interface", 0) or 0),
        "activities": int(metric_counts.get("activities", 0) or 0),
        "data_transformation": int(metric_counts.get("data_transformation", 0) or 0),
        "digital_layouts": int(metric_counts.get("digital_layouts", 0) or 0),
        "process_flows": int(metric_counts.get("process_flows", 0) or 0)
    }

    metric_rows = {
        "interface": 17,
        "activities": 18,
        "data_transformation": 19,
        "digital_layouts": 20,
        "process_flows": 21
    }
    bucket_to_value_col = {"ES": "AI", "S": "AJ", "M": "AK", "C": "AL", "XC": "AM"}
    bucket_to_weighted_col = {"ES": "AC", "S": "AD", "M": "AE", "C": "AF", "XC": "AG"}

    selected_buckets = {}
    selected_base_values = {}
    weighted_contributions = {}
    risk_factors = list(agent_risk_factors or [])
    count_rationale = count_rationale or {}

    for metric_name, row_num in metric_rows.items():
        count = metric_counts[metric_name]
        selected_bucket = _bucket_metric(metric_name, count)
        selected_buckets[metric_name] = selected_bucket

        value_col = bucket_to_value_col[selected_bucket]
        weighted_col = bucket_to_weighted_col[selected_bucket]

        selected_base_values[metric_name] = _safe_float(matrix_cells.get(f"{value_col}{row_num}", {}).get("value"))
        weighted_contributions[metric_name] = _safe_float(matrix_cells.get(f"{weighted_col}{row_num}", {}).get("value"))

        if count <= 0:
            risk_factors.append(
                f"{metric_name} count was {count}; workbook bucketed as {selected_bucket}. Verify whether source JSON had enough evidence."
            )

    matrix_weighted_score = round(sum(weighted_contributions.values()), 4)
    overall_complexity = _classify_from_equivalence(matrix_weighted_score, matrix_cells)
    max_score = max(_safe_float(matrix_cells.get("AG22", {}).get("value"), 0.0), 1.0)
    overall_score = min(100, round((matrix_weighted_score / max_score) * 100))

    process_name = process_info.get("process_name") or (processes[0].get("name") if processes else "Unknown Process")

    support_data = {
        "workbook_name": complexity_metrics_data.get("workbook_name"),
        "metric_counts": metric_counts,
        "count_rationale": count_rationale,
        "selected_buckets": selected_buckets,
        "selected_base_values": selected_base_values,
        "weighted_contributions": weighted_contributions,
        "matrix_weighted_score": matrix_weighted_score,
        "equivalence_cells": {
            key: matrix_cells.get(key, {}).get("value")
            for key in ["AQ16", "AR16", "AQ17", "AR17", "AQ18", "AR18", "AQ19", "AR19", "AQ20", "AR20", "AP20"]
        }
    }

    return {
        "overall_complexity": overall_complexity,
        "overall_score": overall_score,
        "process_assessments": [{
            "process_name": process_name,
            "complexity_rating": overall_complexity,
            "total_score": overall_score,
            "complexity_drivers": [
                f"Workbook metric interface count = {metric_counts['interface']} mapped to {selected_buckets['interface']}",
                f"Workbook metric activities count = {metric_counts['activities']} mapped to {selected_buckets['activities']}",
                f"Workbook metric data transformation count = {metric_counts['data_transformation']} mapped to {selected_buckets['data_transformation']}",
                f"Workbook metric digital layouts count = {metric_counts['digital_layouts']} mapped to {selected_buckets['digital_layouts']}",
                f"Workbook metric process flows count = {metric_counts['process_flows']} mapped to {selected_buckets['process_flows']}",
                f"Workbook matrix weighted score = {matrix_weighted_score}"
            ]
        }],
        "risk_factors": risk_factors,
        "workbook_support_data": support_data
    }


def show_bp_to_pa_migration():
    """Show Blue Prism to Power Automate migration interface"""
    
    st.markdown("---")
    st.markdown("## 📁 Upload Blue Prism Release Package")
    
    st.info("📌 Upload a Blue Prism release file (.bprelease) to begin the automated assessment process.")

    if st.session_state.complexity_metrics_data:
        st.info(f"📘 Active complexity metrics workbook: **{st.session_state.complexity_metrics_filename}** — To change, go to ⚙️ Configuration → 🧮 Complexity Matrix in the sidebar.")
    else:
        st.warning("⚠️ No complexity matrix loaded. Please configure the Complexity_Matrix_File path in your .env file or upload via ⚙️ Configuration → 🧮 Complexity Matrix in the sidebar.")
    
    # Debug mode checkbox
    debug_mode = st.checkbox(
        "🐛 Enable Debug Mode",
        value=False,
        help="Enable debug mode to see detailed API request/response information in the console"
    )
    
    uploaded_file = st.file_uploader(
        "Choose a .bprelease file",
        type=['bprelease'],
        help="Upload the Blue Prism release package exported from your Blue Prism environment"
    )
    
    if uploaded_file is not None:
        # Display file information
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
        #with col3:
        #    st.metric("File Type", uploaded_file.type)
        
        # Analyze button
        if st.button("🚀 Start AI-Powered Analysis", type="primary", use_container_width=True):
            analyze_bp_release(uploaded_file, debug_mode)
    
    # Show results if analysis is complete
    if st.session_state.analysis_complete and st.session_state.analysis_results:
        display_analysis_results()

def analyze_bp_release(uploaded_file, debug_mode=False):
    """Analyze Blue Prism release file using IBM ICA Agents"""
    
    st.markdown("---")
    st.markdown("## 🤖 IBM Consulting Advantage Agentic AI Assessment")
    st.markdown("The platform uses IBM ICA Agents through a unified workflow to perform comprehensive analysis:")
    
    if debug_mode:
        st.warning("🐛 Debug Mode Enabled - Check console for detailed API logs")
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Save uploaded file temporarily
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        temp_file_path = temp_dir / uploaded_file.name
        
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Initialize results dictionary
        results = {
            "file_name": uploaded_file.name,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_platform": "Blue Prism",
            "target_platform": "Power Automate"
        }
        
        # Parse Blue Prism release
        status_text.markdown("### 📄 Parsing Blue Prism Release File")
        with st.spinner("Extracting process metadata from .bprelease file..."):
            parser = BluePrismParser()
            parsed_data = parser.parse_release(temp_file_path)
            results['parsed_data'] = parsed_data
            st.success("✅ File parsed successfully")
        
        if debug_mode:         
            # Display parsed data summary
            with st.expander("📊 View Parsed Blue Prism Data (This is what gets sent to agents)", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Processes", parsed_data.get('summary', {}).get('total_processes', 0))
                with col2:
                    st.metric("Objects", parsed_data.get('summary', {}).get('total_objects', 0))
                with col3:
                    st.metric("Work Queues", parsed_data.get('summary', {}).get('total_work_queues', 0))
                with col4:
                    st.metric("Env Variables", parsed_data.get('summary', {}).get('total_env_vars', 0))
                
                st.markdown("#### 📋 Complete Parsed Data Structure")
                st.json(parsed_data)
                
                st.info("💡 **Note**: This JSON structure is sent to each IBM ICA Agent for analysis. Each agent should analyze this data differently based on their specialized prompts.")
        
        progress_bar.progress(10)
        
        # Initialize ICA Agent Client
        ica_client = ICAAgentClient()
        
        # Agent 1: Process Understanding Agent
        status_text.markdown("### 🔍 IBM ICA Agent: Process Understanding Inprogress")
        with st.spinner("Calling IBM ICA Agent for process analysis..."):
            agent1 = ProcessAnalyzerAgent(ica_client)
            process_analysis = agent1.analyze(parsed_data, debug=debug_mode)
            results['process_analysis'] = process_analysis
            
            if "error" in process_analysis:
                st.warning(f"⚠️ Process analysis completed with issues: {process_analysis['error']}")
            else:
                st.success("✅ Process analysis complete")
            if debug_mode:
                with st.expander("View Process Analysis Details"):
                    st.json(process_analysis)
        
        progress_bar.progress(30)
        
        # Agent 2: Complexity Assessment Agent
        status_text.markdown("### 📊 IBM ICA Agent: Complexity Assessment Inprogress")
        with st.spinner("Calling IBM ICA Agent for complexity assessment..."):
            agent2 = ComplexityAssessorAgent(ica_client)
            if st.session_state.complexity_metrics_data:
                complexity_metric_context = {
                    "workbook_name": st.session_state.complexity_metrics_filename,
                    "metric_definitions": {
                        "interface": _get_sheet_rows(st.session_state.complexity_metrics_data, "Interfaces"),
                        "activities": _get_sheet_rows(st.session_state.complexity_metrics_data, "Activities"),
                        "digital_layouts": _get_sheet_rows(st.session_state.complexity_metrics_data, "Layouts"),
                        "process_flows": _get_sheet_rows(st.session_state.complexity_metrics_data, "Happy Path and Major Exceptions"),
                        "data_transformation_description": [
                            "Count data transformation activities based on workbook intent: calculations, validations, determinations, manipulations, transformations, assignments, lookups, encryption/decryption, formatting, and rule-based data changes."
                        ]
                    }
                }
                ai_metric_analysis = agent2.assess(
                    parsed_data,
                    process_analysis,
                    complexity_metrics=complexity_metric_context,
                    debug=debug_mode
                )
                if ai_metric_analysis and "error" not in ai_metric_analysis and "metric_counts" in ai_metric_analysis:
                    complexity_assessment = compute_workbook_complexity(
                        parsed_data,
                        process_analysis,
                        st.session_state.complexity_metrics_data,
                        metric_counts=ai_metric_analysis.get("metric_counts", {}),
                        agent_risk_factors=ai_metric_analysis.get("risk_factors", []),
                        count_rationale=ai_metric_analysis.get("count_rationale", {})
                    )
                    complexity_assessment["ai_metric_analysis"] = ai_metric_analysis
                else:
                    complexity_assessment = {
                        "error": "AI metric counting failed for workbook-driven complexity",
                        "risk_factors": ai_metric_analysis.get("risk_factors", []) if ai_metric_analysis else []
                    }
            else:
                complexity_assessment = agent2.assess(
                    parsed_data,
                    process_analysis,
                    complexity_metrics=st.session_state.complexity_metrics_data,
                    debug=debug_mode
                )
            results['complexity_assessment'] = complexity_assessment
            
            if "error" in complexity_assessment:
                st.warning(f"⚠️ Complexity assessment completed with issues: {complexity_assessment['error']}")
            else:
                st.success("✅ Complexity assessment complete")
            if debug_mode:
                with st.expander("View Complexity Assessment"):
                    st.json(complexity_assessment)
        
        progress_bar.progress(50)
        
        # Agent 3: Dependency Analysis Agent
        status_text.markdown("### 🔗 IBM ICA Agent: Dependency Analysis Inprogress")
        with st.spinner("Calling IBM ICA Agent for dependency analysis..."):
            agent3 = DependencyAnalyzerAgent(ica_client)
            dependency_analysis = agent3.analyze(parsed_data, debug=debug_mode)
            results['dependency_analysis'] = dependency_analysis
            
            if "error" in dependency_analysis:
                st.warning(f"⚠️ Dependency analysis completed with issues: {dependency_analysis['error']}")
            else:
                st.success("✅ Dependency analysis complete")
            if debug_mode:
                with st.expander("View Dependency Analysis"):
                    st.json(dependency_analysis)
        
        progress_bar.progress(70)
        
        # Agent 4: Migration Mapping Agent
        
        mapping_df=load_mapping()
        mapping_json = mapping_df.to_dict(orient="records")
        
        status_text.markdown("### 🗺️ IBM ICA Agent: Migration Mapping Inprogress")
        with st.spinner("Calling IBM ICA Agent for migration mapping..."):
            agent4 = MigrationMapperAgent(ica_client)
            migration_mapping = agent4.map_components(parsed_data, mapping_json, "Blue Prism", "Power Automate", debug=debug_mode)
            results['migration_mapping'] = migration_mapping
            
            if "error" in migration_mapping:
                st.warning(f"⚠️ Migration mapping completed with issues: {migration_mapping['error']}")
            else:
                st.success("✅ Migration mapping complete")
            if debug_mode:
                with st.expander("View Migration Mapping"):
                    st.json(migration_mapping)
        
        progress_bar.progress(85)
        
        # Agent 5: Effort Estimation Agent
        
# Effort matrix values

        effort_df=load_effort_matrix()
        effort_json = effort_df.to_dict(orient="records")
        
        status_text.markdown("### ⏱️ IBM ICA Agent: Effort Estimation Inprogress")
        with st.spinner("Calling IBM ICA Agent for effort estimation..."):
            agent5 = EffortEstimatorAgent(ica_client)
            #effort_estimation = agent5.estimate(complexity_assessment, dependency_analysis, migration_mapping, debug=debug_mode)
            effort_estimation = agent5.estimate(complexity_assessment, effort_json, debug=debug_mode)
            results['effort_estimation'] = effort_estimation
            
            if "error" in effort_estimation:
                st.warning(f"⚠️ Effort estimation completed with issues: {effort_estimation['error']}")
            else:
                st.success("✅ Effort estimation complete")
            if debug_mode:
                with st.expander("View Effort Estimation"):
                    st.json(effort_estimation)
        
        progress_bar.progress(100)
        
        # Store results in session state
        st.session_state.analysis_results = results
        st.session_state.analysis_complete = True
        
        # Clean up temp file
        temp_file_path.unlink()
        
        st.success("🎉 IBM ICA Agent Analysis Complete!")
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        st.exception(e)

def display_analysis_results():
    """Display comprehensive analysis results"""
    
    st.markdown("---")
    st.markdown("## 📊 Migration Assessment Report")
    
    results = st.session_state.analysis_results
    
    # Executive Summary
    st.markdown("### 📋 Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    mapping = results.get('migration_mapping', {})
    source_pf= mapping.get('source_platform', 'None')
    target_pf= mapping.get('target_platform', 'None')
    
    with col1:
        st.metric("Source Platform", source_pf)
        
    with col2:
        st.metric("Target Platform", target_pf)
    
    with col3:
        complexity = results['complexity_assessment'].get('overall_complexity', 'N/A')
        st.metric("Complexity Rating", complexity)
    
    with col4:
        total_hours = results['effort_estimation'].get('total_hours', 0)
        total_weeks = results['effort_estimation'].get('total_weeks', 0)
        #st.metric("Estimated Effort", f"{total_hours} hours")
        st.metric("Estimated Effort", f"{total_hours} hours / {total_weeks} weeks")
    

       
    #with col3:
    #    process_count = results['process_analysis'].get('process_count', 0)
    #    st.metric("Processes Found", process_count)
    
    #with col4:
    #    app_count = len(results['dependency_analysis'].get('applications', []))
    #    st.metric("Applications Used", app_count)
    
    # Tabs for detailed information
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Process Overview",
        "📊 Complexity Assessment",
        "🔗 Dependencies",
        "🗺️ Migration Mapping",
        "⏱️ Effort Estimation",
        "📄 Download Report"
    ])
    
    with tab1:
        st.markdown("#### Process Information")
        #st.json(results['process_analysis']
        proc_data = results.get('process_analysis', {})
        processes = proc_data.get('processes', [])
        col1 = st.columns(1)[0]
        with col1:
            st.markdown("##### Process Details")

            for process in processes:
                process_name = process.get('process_name', 'N/A')
                process_desc= process.get('description', '')
                st.markdown(f"**Use case Name:** {process_name}")
                
                st.markdown(f"**Description:** {process_desc}")

                st.markdown("##### AI Generated Process Steps #####")
                steps = process.get("ai_generated_steps", [])

                for step_no, step in enumerate(steps, start=1):
                    st.markdown(f"{step_no}. {step}")
        
    
    with tab2:
        complexity_data = results['complexity_assessment']
        
        col1 = st.columns(1)[0]
        with col1:
                Complexity_level= complexity_data.get('overall_complexity', '')
                st.markdown(f"##### Complexity: {Complexity_level}")
                
                st.markdown(f"##### AI Complexity Insights")
                
                metrics = complexity_data.get("ai_metric_analysis", {}).get("metric_counts", {})

                cols = st.columns(len(metrics))

                for col, (key, value) in zip(cols, metrics.items()):
                    with col:
                        st.metric(label=key.replace("_", " ").title(), value=value)
                
                analysis = complexity_data.get("ai_metric_analysis", {})
                rationale = analysis.get("count_rationale", {}) 
                
                for k, v in rationale.items():
                     st.markdown(f"**{k.replace('_',' ').title()}**: {v}")
                
                risk_factors = complexity_data.get('risk_factors', []) 
                st.markdown(f"##### Assumptions:")   
                for factor in risk_factors:
                    st.markdown(f"{factor}")
                
  
    
    with tab3:
        st.markdown("#### Dependency Analysis")
        dep_data = results['dependency_analysis']
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Applications")
            apps = dep_data.get('applications', [])
            for app in apps:
                st.markdown(f"- {app}")
        
        with col2:
            st.markdown("##### File Dependencies")
            files = dep_data.get('files', [])
            for file in files:
                st.markdown(f"- {file}")
        with col1:
            st.markdown("##### Databases")
            dbs = dep_data.get('databases', [])
            for db in dbs:
                st.markdown(f"- {db}")
        
        with col2:
            st.markdown("##### APIs")
            apis = dep_data.get('apis', [])
            for api in apis:
                st.markdown(f"- {api}")
    
    with tab4:
        st.markdown("#### Source to Target Mapping")
        mapping_data = results['migration_mapping']
        
        Source= mapping_data.get('source_platform', '')
        st.markdown(f"##### Source Platform: {Source}")
        
        Target= mapping_data.get('target_platform', '')
        st.markdown(f"##### Target Platform: {Target}")
        
        mappings = mapping_data.get("process_mappings", [])
        for mapping in mappings:
            source = mapping.get("source_process", "")
            target_component = mapping.get("target_component", "")
            target_architecture = mapping.get("target_architecture", "")

            st.markdown(f"**Source Process:** {source}")
            st.markdown(f"**Target Component:** {target_component}")
            st.markdown(f"**Target Architecture:** {target_architecture}")
        st.markdown("##### **** Generate Migration Report for detailed mapping ****")
    
    with tab5:
        st.markdown("## Effort Estimation")
        effort_data = results['effort_estimation']
        
        eff_complexity= effort_data.get('Complexity', '')
        st.markdown(f"#### Complexity Level: {eff_complexity}")
    
        total_hrs= effort_data.get('total_hours', '')
        st.markdown(f"###### Total Hours Required: {total_hrs} hours")    
        
        total_days= effort_data.get('total_days', '')
        st.markdown(f"###### Total Days Required: {total_days} days")
        
        total_wks= effort_data.get('total_weeks', '')
        st.markdown(f"###### Total Weeks Required: {total_wks} weeks")
        
        st.markdown("### Effort Breakdown")
        
        #effort_detail = effort_data["effort_breakdown"]
        
        effort_df = pd.DataFrame(
        effort_data["effort_breakdown"].items(),
        columns=["Activity", "Hours"])
        
        # Custom display names
        activity_map = {
        "development": "Development",
        "sit_support": "SIT",
        "uat_support": "UAT",
        "deployment": "Deployment",
        "documentation": "Documentation"}

        effort_df["Activity"] = effort_df["Activity"].replace(activity_map)        
        col1, col2 = st.columns([1, 2])

        with col1:
            
            #st.table(effort_df)
            st.dataframe(effort_df, hide_index=True)
        
    
    with tab6:
        st.markdown("#### Generate Comprehensive Report")
        st.info("📊 Report will be generated in Excel format (.xlsx) with multiple sheets for easy analysis")
        
        # Initialize report generation state
        if 'report_generated' not in st.session_state:
            st.session_state.report_generated = False
            st.session_state.report_path = None
        
        if st.button("📥 Generate Excel Report", type="primary", use_container_width=True):
            with st.spinner("Generating comprehensive migration assessment report in Excel format..."):
                try:
                    report_gen = ReportGenerator()
                    report_path = report_gen.generate_report(results)
                    
                    # Store in session state
                    st.session_state.report_generated = True
                    st.session_state.report_path = report_path
                    
                    st.success("✅ Report generated successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
        
        # Show download button if report is generated
        if st.session_state.report_generated and st.session_state.report_path:
            report_path = st.session_state.report_path
            
            # Determine file extension
            file_ext = ".xlsx" if report_path.endswith(".xlsx") else ".txt"
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if file_ext == ".xlsx" else "text/plain"
            
            with open(report_path, "rb") as report_file:
                st.download_button(
                    label=f"⬇️ Download Migration Assessment Report ({file_ext.upper()})",
                    data=report_file,
                    file_name=f"Migration_Assessment_{results['file_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}",
                    mime=mime_type,
                    use_container_width=True
                )
            
            if file_ext == ".xlsx":
                st.success("✅ Excel report generated successfully! The report contains multiple sheets with detailed analysis.")
            else:
                st.warning("⚠️ Excel library not available. Generated text report instead. Install openpyxl for Excel reports: `pip install openpyxl`")

def show_under_development(source, target):
    """Show under development message for other platform combinations"""
    
    st.markdown("---")
    st.markdown(f"""
    <div class="under-development">
        <h2>🚧 Under Development</h2>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Migration assessment for <strong>{source}</strong> to <strong>{target}</strong> 
            is currently under development.
        </p>
        <p style="margin-top: 1rem; color: #666;">
            Currently supported: <strong>Blue Prism → Power Automate</strong>
        </p>
        <p style="margin-top: 1rem; color: #666;">
            Coming soon: All platform combinations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 Please select **Blue Prism** as source and **Power Automate** as target to use the platform.")

def load_effort_matrix():
    """
    Load configuration from JSON.
    """
    if os.path.exists(Effort_Matrix_File):
        with open(Effort_Matrix_File, "r") as f:
            data = json.load(f)

        return pd.DataFrame(data)

    return pd.DataFrame()

def save_effort_matrix(df):
    """
    Save configuration back to JSON.
    """
    with open(Effort_Matrix_File, "w") as f:
        json.dump(
            df.to_dict(orient="records"),
            f,
            indent=4
        )

def load_complexity_matrix():
    """
    Load complexity matrix from the file path configured in .env (Complexity_Matrix_File).
    Reuses the existing summarize_complexity_metrics_excel function unchanged.
    """
    if Complexity_Matrix_File and os.path.exists(Complexity_Matrix_File):
        try:
            with open(Complexity_Matrix_File, "rb") as f:
                file_bytes = f.read()

            class _FileWrapper:
                """Wraps raw bytes to mimic Streamlit UploadedFile interface."""
                def __init__(self, name, data):
                    self.name = name
                    self._data = data
                def getvalue(self):
                    return self._data

            wrapper = _FileWrapper(os.path.basename(Complexity_Matrix_File), file_bytes)
            return summarize_complexity_metrics_excel(wrapper)
        except Exception as e:
            st.warning(f"⚠️ Could not load complexity matrix from configured path: {str(e)}")
            return None
    return None

# -----------------------------
# Load data from Excel
# -----------------------------
def load_mapping():
    if os.path.exists(Mapping_File):
        return pd.read_excel(Mapping_File)
    return pd.DataFrame()


# -----------------------------
# Save to Excel
# -----------------------------
def save_mapping(df):
    df.to_excel(Mapping_File, index=False)

        
if __name__ == "__main__":
    main()