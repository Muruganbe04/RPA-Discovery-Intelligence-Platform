# 🤖 RPA Discovery Intelligence Platform

> An Agentic AI solution for automation portfolio discovery, complexity assessment, and migration readiness — purpose-built for **Blue Prism → Microsoft Power Automate** migrations.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Agent Pipeline](#agent-pipeline)
- [Complexity Engine](#complexity-engine)
- [Project Structure](#project-structure)
- [Configuration Files](#configuration-files)
- [How It Fits in the RPA Migration Lifecycle](#how-it-fits-in-the-rpa-migration-lifecycle)
- [Extending the Platform](#extending-the-platform)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **RPA Discovery Intelligence Platform** automates the most time-consuming part of any RPA migration project — the **Explore phase**. Instead of manually reviewing Blue Prism release packages, estimating complexity on spreadsheets, and hand-mapping components to Power Automate equivalents, this platform runs a sequential pipeline of five IBM ICA AI agents that do it in minutes.

**What it produces:**

| Output | Used for |
|--------|----------|
| AI-generated process steps | Process understanding and documentation |
| Complexity rating (Extra Simple → Extra Complex) | Sprint sizing and resourcing |
| Dependency map (apps, files, DBs, APIs) | Risk identification and infrastructure planning |
| Component migration mapping (BP → PA) | Design phase blueprinting |
| Effort estimate (hours / days / weeks) | Project planning and commercial proposals |
| Downloadable Excel report | Stakeholder sign-off and audit trail |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Presentation Layer                  │
│         Streamlit Web App (app.py)               │
│  Home · Effort Matrix · Migration Mapping ·     │
│  Complexity Matrix · Results Dashboard           │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│            Orchestration Layer                   │
│    analyze_bp_release() — sequential pipeline    │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│              Agentic AI Layer                    │
│                                                  │
│  Prompt 1          Prompt 2       Prompt 3       │
│  Process       Complexity       Dependency       │
│  Analyzer      Assessor         Analyzer         │
│                                                  │
│  Agent 4         Prompt 5       Unified ICA Agent|                 
│  Migration       Effort                          │
│  Mapper          Estimator                       │
│                                                  │
│  ┌─────────────────────────────────────────┐     │
│  │  Workbook Complexity Engine             │    │
│  │  AI metric counts → bucket → weighted   │     │
│  │  matrix score → complexity label        │     │
│  └─────────────────────────────────────────┘     │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│               Parsing Layer                      │
│     BluePrismParser — .bprelease (ZIP/XML)       │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│          Configuration & Data Layer              │
│  Complexity Matrix (.xlsx) · Effort Matrix (.json)│
│  Migration Mapping (.xlsx)                       │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│             External Services                    │
│  IBM ICA Agent API · Blue Prism source files     │
│  .env configuration                             │
└─────────────────────────────────────────────────┘
```

---

## Key Features

- **Zero-touch parsing** — upload a `.bprelease` file; the platform handles all XML extraction automatically
- **AI-powered process understanding** — generates human-readable process step descriptions via IBM ICA agents
- **Workbook-driven complexity scoring** — uses your organisation's own complexity matrix Excel file; no hardcoded thresholds
- **Configurable effort estimation** — effort matrix is editable in-app; no code changes required
- **Editable migration mapping** — BP-to-PA component mappings are stored in Excel and editable via the UI
- **Debug mode** — toggle to inspect raw agent request/response payloads in-browser
- **Excel report generation** — multi-sheet downloadable report for stakeholder presentation
- **Extensible architecture** — clean separation of agents, parser, and UI; add new source/target platforms with minimal changes

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.9 or higher |
| pip | Latest |
| IBM ICA API access | Credentials from your IBM Consulting Advantage account |
| Blue Prism | Any version that exports `.bprelease` files |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-org/rpa-discovery-platform.git
cd rpa-discovery-platform
```

### 2. Create a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

### Environment variables

Create a `.env` file in the project root. Copy the template:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Path to the effort matrix JSON file
Effort_Matrix_File=config/effort_matrix.json

# Path to the migration mapping Excel file
Mapping_File=config/migration_mapping.xlsx

# Path to the complexity matrix Excel workbook
Complexity_Matrix_File=config/complexity_matrix.xlsx

# IBM ICA API configuration
ICA_API_URL=https://your-ica-instance.ibm.com/api
ICA_API_KEY=your_api_key_here
```

### Preparing configuration files

#### Complexity matrix (`complexity_matrix.xlsx`)

The workbook must contain a sheet named **"Complexity Matrix"** with:

- **Metric rows** at rows 17–21 representing: Interfaces, Activities, Data Transformation, Digital Layouts, Process Flows
- **Bucket value columns** AI–AM (Extra Simple through Extra Complex base values)
- **Weighted contribution columns** AC–AG
- **Equivalence range cells** AQ16–AR20 and AP20 (define score-to-label thresholds)

Additional sheets used for AI agent context: `Interfaces`, `Activities`, `Layouts`, `Happy Path and Major Exceptions`

#### Effort matrix (`config/effort_matrix.json`)

```json
[
  {
    "Complexity": "Extra Simple",
    "development": 8,
    "sit_support": 2,
    "uat_support": 2,
    "deployment": 1,
    "documentation": 2
  },
  {
    "Complexity": "Simple",
    "development": 16,
    "sit_support": 4,
    "uat_support": 4,
    "deployment": 2,
    "documentation": 4
  }
]
```

#### Migration mapping (`config/migration_mapping.xlsx`)

An Excel file with columns mapping Blue Prism component types/names to their Power Automate equivalents. Editable directly in the app via **⚙️ Configuration → 🗃️ Migration Mapping**.

---

## Running the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

To run on a specific port:

```bash
streamlit run app.py --server.port 8502
```

---

## Usage Guide

### Step 1 — Select platforms

On the Home page, select:
- **Source Platform:** Blue Prism
- **Target Platform:** Power Automate

Other combinations display an "Under Development" message.

### Step 2 — Upload a `.bprelease` file

Export a release package from your Blue Prism environment. Drag and drop or browse to select the file.

### Step 3 — Start analysis

Click **🚀 Start AI-Powered Analysis**. The platform will:

1. Parse the release file and show a file summary
2. Run five IBM ICA agents sequentially with progress tracking
3. Display results across tabbed sections on completion

### Step 4 — Review results

Navigate the results tabs:

| Tab | Content |
|-----|---------|
| 📝 Process Overview | AI-generated process description and step-by-step breakdown |
| 📊 Complexity Assessment | Complexity label, metric counts with rationale, assumptions |
| 🔗 Dependencies | Applications, files, databases, and APIs identified |
| 🗺️ Migration Mapping | Source process → target component and architecture |
| ⏱️ Effort Estimation | Hours/days/weeks breakdown by activity |
| 📄 Download Report | Generate and download Excel migration assessment report |

### Step 5 — Configure (optional)

Use the sidebar to adjust:
- **📊 Effort Matrix** — edit hours per complexity level per activity
- **🗃️ Migration Mapping** — edit component mappings inline
- **🧮 Complexity Matrix** — upload a replacement `.xlsx` workbook

### Debug mode

Check **🐛 Enable Debug Mode** before starting analysis to see:
- Raw parsed JSON structure sent to agents
- Agent response payloads
- Complexity computation details

---

## Agent Pipeline

The five IBM ICA agents run in sequence. Each receives the parsed Blue Prism data and the outputs of preceding agents where relevant.

```
.bprelease
    │
    ▼
BluePrismParser
    │  parsed_data (processes, objects, queues, env vars)
    ▼
Prompt 1: ProcessAnalyzerAgent
    │  process_analysis (process name, description, AI-generated steps)
    ▼
Prompt 2: ComplexityAssessorAgent
    │  ai_metric_analysis (metric counts + rationale)
    │  → compute_workbook_complexity()
    │  complexity_assessment (rating, score, drivers, risk factors)
    ▼
Prompt 3: DependencyAnalyzerAgent
    │  dependency_analysis (applications, files, databases, APIs)
    ▼
Prompt 4: MigrationMapperAgent  ← migration_mapping.xlsx
    │  migration_mapping (source process → target component + architecture)
    ▼
Prompt 5: EffortEstimatorAgent  ← effort_matrix.json
    │  effort_estimation (total hours/days/weeks, activity breakdown)
    ▼
ICA Agent : Unified Orchestrator Agent 
    │  Return Responses based on the prompt
    ▼
ReportGenerator
    │  Migration_Assessment_*.xlsx
    ▼
```

---

## Complexity Engine

The complexity engine translates AI-derived metric counts into a calibrated complexity rating using your organisation's workbook.

### Metrics assessed

| Metric | What is counted |
|--------|----------------|
| Interface | Number of system interfaces (applications automated) |
| Activities | Total number of process activities/actions |
| Data transformation | Calculations, validations, lookups, format conversions |
| Digital layouts | Screens, forms, or UI elements interacted with |
| Process flows | Happy paths plus major exception flows |

### Bucketing

Each metric count maps to a complexity bucket:

| Bucket | Code | Example (activities) |
|--------|------|----------------------|
| Extra Simple | ES | ≤ 4 activities |
| Simple | S | 5 – 10 |
| Medium | M | 11 – 20 |
| Complex | C | 21 – 40 |
| Extra Complex | XC | > 40 |

### Scoring

Each bucket resolves to a weighted contribution from the complexity matrix workbook. The sum of weighted contributions is divided by the maximum possible score and normalised to 100. The score maps to a label (Extra Simple → Extra Complex) via the equivalence range in cells AQ16–AR20.

---

## Project Structure

```
rpa-discovery-platform/
│
├── app.py                      # Main Streamlit application
├── ica_agent.py                # IBM ICA agent client and all five agents
├── bp_parser.py                # Blue Prism .bprelease parser
├── report_generator.py         # Excel report generator
│
├── config/
│   ├── effort_matrix.json      # Effort hours by complexity and activity
│   ├── migration_mapping.xlsx  # BP → PA component mapping table
│   └── complexity_matrix.xlsx  # Complexity scoring workbook
│
├── assets/
│   ├── newlogo.png             # Sidebar logo
│   └── ComplexityMatrix.png    # Complexity matrix reference image
│
├── temp/                       # Temporary upload directory (auto-created)
│
├── .env                        # Local environment variables (not committed)
├── .env.example                # Template for .env
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## Configuration Files

### `.gitignore` recommendations

```gitignore
# Environment
.env
venv/
__pycache__/
*.pyc

# Temporary files
temp/

# Sensitive config (keep examples, not actuals)
config/complexity_matrix.xlsx
config/migration_mapping.xlsx
config/effort_matrix.json
```

> **Note:** Commit `.env.example` and sample/anonymised config files. Never commit `.env` or proprietary workbooks.

---

## How It Fits in the RPA Migration Lifecycle

| Phase | Activities | Platform involvement |
|-------|-----------|----------------------|
| **1 · Explore** | Portfolio discovery, complexity assessment, dependency mapping, migration mapping, effort estimation | ✅ **Primary — fully automated** |
| **2 · Design** | Solution architecture, PA flow design, environment setup | Feeds complexity rating and migration mapping outputs |
| **3 · Build** | Power Automate development, connector configuration | Feeds effort breakdown (development hours) |
| **4 · Test** | SIT, UAT | Feeds SIT/UAT hour estimates |
| **5 · Deploy** | Production deployment, hypercare | Feeds deployment effort estimate |

The platform is purpose-built for **Phase 1**. Its outputs are the inputs to every subsequent phase — reducing the Explore phase from weeks of manual effort to a same-day automated assessment.

---

## Extending the Platform

### Adding a new source platform

1. Create `<platform>_parser.py` implementing the same interface as `BluePrismParser`
2. In `app.py`, add the new platform to the `source_platform` selectbox
3. Update the routing condition (currently `if source_platform == "Blue Prism" and target_platform == "Power Automate"`)
4. Create a `show_<platform>_to_<target>_migration()` function

### Adding a new agent

1. Create a new agent class in `ica_agent.py` following the pattern of existing agents
2. Add the agent call to the `analyze_bp_release()` function in `app.py`
3. Add a results display section in `display_analysis_results()`

### Customising complexity thresholds

Update `config/complexity_matrix.xlsx`. The engine reads bucket boundaries from the workbook at runtime — no code changes required.

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `⚠️ No complexity matrix loaded` | `Complexity_Matrix_File` not set or file missing | Set the correct path in `.env` |
| Agent returns `"error"` key | IBM ICA API connectivity or auth issue | Check `ICA_API_URL` and `ICA_API_KEY` in `.env` |
| Empty metric counts | Source `.bprelease` has minimal content | Enable debug mode; review parsed JSON |
| Excel report fails | `openpyxl` not installed | `pip install openpyxl` |
| `temp/` directory permission error | Missing write permissions | `mkdir temp && chmod 755 temp` |
| Complexity shows "No Data" | All metric counts resolved to 0 | Verify agent 2 response; check workbook cells AQ16–AQ20 are populated |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: describe your change"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

Please follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

*Built with ❤️ using Streamlit, IBM Consulting Advantage (ICA) Agents, and Python.*
