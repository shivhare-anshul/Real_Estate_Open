# Real Estate Document Processing Pipeline

A comprehensive Prefect-based data pipeline that extracts structured and unstructured information from real estate and construction documents, storing data in PostgreSQL and ChromaDB for querying and semantic search.

## 🎯 Overview

This pipeline processes PDF documents and extracts:
- **Structured Data**: Project tasks, cost items, and regulatory rules → PostgreSQL
- **Unstructured Data**: Document chunks with embeddings → ChromaDB (for semantic search)

## 📹 Recorded Video

Watch a complete demonstration of the Real Estate Document Processing Pipeline:

🎥 **[View Recorded Demonstration on Loom](https://www.loom.com/share/9cf8d24dd26145a8bddb934814fb6e64)**

This video demonstrates:
- Pipeline execution and document processing
- Data extraction and storage in PostgreSQL
- Semantic search functionality in ChromaDB
- Web dashboard interface and features

## 🏗️ Architecture

```
PDF Documents
    ↓
[Unstructured.io Parser] (Open Source)
    ↓
[Prefect Flow Orchestration]
    ├─> [Extraction Agent] → Structured Data
    │   └─> [PostgreSQL] (via dltHub or direct insert)
    │
    └─> [Chunking] → Document Chunks
        └─> [ChromaDB] → Vector Embeddings
```

## 📋 Prerequisites

- Python 3.10+ (AI_Agents conda environment)
- Docker (for PostgreSQL)
- Conda environment activated

## 🚀 Quick Start

### 1. Start PostgreSQL with Docker

```bash
docker-compose up -d
```

### 2. Configure Environment

The `.env` file is already created with default values. Edit it to add your API keys:

```bash
# Edit .env file to add your API keys
# Required: GROQ_API_KEY (get from https://console.groq.com/)
# Optional: OPENAI_API_KEY (only if using OpenAI models)
```

**Important**: The `.env` file is in `.gitignore` and will not be committed to version control.

### 3. Install Dependencies

```bash
conda activate AI_Agents
pip install django djangorestframework prefect "dlt[postgres]" chromadb pytest pytest-django
```

### 4. Initialize Database

```bash
python manage.py shell
>>> from database.postgres_client import PostgreSQLClient
>>> from pathlib import Path
>>> client = PostgreSQLClient()
>>> client.create_tables()
>>> client.execute_ddl(str(Path("database/ddl.sql")))
```

### 5. Run Pipeline

```bash
PREFECT_API_URL="" python run_pipeline.py
```

## 📖 Documentation

All documentation is included in this README. For detailed information about:
- **Architecture**: See the Architecture section above
- **API Endpoints**: See the API Endpoints section below
- **Configuration**: See the Configuration section below
- **Usage Examples**: See the Usage Examples section below

## 🔌 API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### Endpoints

#### 1. Health Check

**GET** `/api/health/`

**Description**: Check if API is running

**Response**:
```json
{
    "status": "healthy",
    "service": "Real Estate Data Pipeline API"
}
```

#### 2. Process Document

**POST** `/api/process-document/`

**Description**: Process a single PDF document

**Request Body**:
```json
{
    "pdf_path": "./Data/Project schedule document.pdf",
    "document_type": "schedule"
}
```

**Response**:
```json
{
    "success": true,
    "pdf_path": "./Data/Project schedule document.pdf",
    "document_type": "schedule",
    "postgres_records": 38,
    "chroma_chunks": 21,
    "extraction_errors": []
}
```

#### 3. Process All Documents

**POST** `/api/process-all-documents/`

**Description**: Process all PDFs in the configured directory

**Request Body** (optional):
```json
{
    "pdf_directory": "./Data",
    "document_types": {
        "Project schedule document.pdf": "schedule",
        "Construction planning and costing.pdf": "cost"
    }
}
```

**Response**:
```json
{
    "success": true,
    "results": [
        {
            "success": true,
            "pdf_path": "./Data/Project schedule document.pdf",
            "postgres_records": 38,
            "chroma_chunks": 21
        }
    ],
    "total": 4,
    "successful": 4
}
```

#### 4. Semantic Search

**POST** `/api/semantic-search/`

**Description**: Perform semantic search in ChromaDB

**Request Body**:
```json
{
    "query": "What are the project tasks?",
    "n_results": 5
}
```

**Response**:
```json
{
    "query": "What are the project tasks?",
    "results": [
        {
            "chunk_id": "Project schedule document_chunk_0",
            "document_name": "Project schedule document.pdf",
            "chunk_text": "...",
            "distance": 0.23,
            "metadata": {
                "chunk_index": 0,
                "document_name": "Project schedule document.pdf"
            }
        }
    ],
    "count": 5
}
```

#### 5. Get Project Tasks

**GET** `/api/project-tasks/?limit=10`

**Description**: Get project tasks from PostgreSQL

**Query Parameters**:
- `limit` (optional): Number of records to return (default: 100)

**Response**:
```json
{
    "tasks": [
        {
            "task_id": 1,
            "task_name": "Install CMU Block Walls",
            "duration_days": 30,
            "start_date": "2024-01-01",
            "finish_date": "2024-01-31"
        }
    ]
}
```

#### 6. Get Cost Items

**GET** `/api/cost-items/?limit=10`

**Description**: Get cost items from PostgreSQL

**Query Parameters**:
- `limit` (optional): Number of records to return (default: 100)

**Response**:
```json
{
    "items": [
        {
            "item_name": "Bearing Pile",
            "quantity": 736.2,
            "unit_price_yen": 79000,
            "total_cost_yen": 58159800,
            "cost_type": "Foreign cost"
        }
    ]
}
```

#### 7. Get ChromaDB Statistics

**GET** `/api/chroma-stats/`

**Description**: Get ChromaDB collection statistics

**Response**:
```json
{
    "collection_name": "real_estate_documents",
    "total_chunks": 150,
    "db_path": "./chroma_db"
}
```

## 🧪 Testing

### Run Component Tests

```bash
python test_components.py
```

### Run Pipeline Tests

```bash
pytest tests/test_pipeline.py -v
```

## 📁 Project Structure

```
Real_Estate/
├── agents/                  # AI Agents
│   ├── extraction_agent.py  # Data extraction agent
│   └── prompts.py           # Jinja2 prompt templates
├── config/                  # Configuration
│   ├── settings.py          # Application settings
│   └── llm_config.py        # LLM configuration
├── database/                # Database clients
│   ├── postgres_client.py   # PostgreSQL client
│   ├── chroma_client.py     # ChromaDB client
│   ├── models.py            # Pydantic models
│   └── ddl.sql              # Database schema
├── documents/               # PDF parsing
│   └── pdf_parser.py        # Unstructured.io parser
├── endpoints/               # Django REST API
│   ├── views.py             # API views
│   └── urls.py              # URL routing
├── pipelines/               # Prefect pipelines
│   ├── document_pipeline.py # Main pipeline
│   └── dlt_pipeline.py      # dltHub integration
├── tests/                   # Test suite
│   └── test_pipeline.py     # Pipeline tests
├── utils/                   # Utilities
│   ├── logger.py            # Logging utility
│   ├── profiler.py          # Performance profiling
│   └── llm_client.py        # LLM client with fallback
├── Data/                    # Input PDF documents
├── docker-compose.yml       # Docker PostgreSQL setup
├── test_components.py       # Component testing
├── run_pipeline.py          # Main pipeline script
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables (.env)

The project uses a `.env` file for configuration. A template is provided with default values.

**Important**: 
- The `.env` file is in `.gitignore` and will not be committed to version control
- You must add your API keys to the `.env` file before running the pipeline
- Never commit API keys to version control

**Required Configuration**:
```env
# LLM API Key (Required for data extraction)
GROQ_API_KEY=your_groq_api_key_here  # Get from https://console.groq.com/
```

**Optional Configuration** (defaults work with Docker):
```env
# Database (Docker PostgreSQL) - defaults work with docker-compose.yml
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/real_estate_db
POSTGRES_DB=real_estate_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# ChromaDB
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=real_estate_documents

# OpenAI (Optional - only if using OpenAI models)
OPENAI_API_KEY=your_openai_api_key_here

# Logging
ENABLE_LOGGING=True
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/app.log

# Application
PDF_DIRECTORY=./Data
PARSED_OUTPUT_DIR=./parsed_outputs
MAX_WORKERS=4
```

See the `.env` file in the project root for all available configuration options.

## 🎯 Key Features

### 1. PDF Parsing
- Uses **Unstructured.io** (open-source, no API key)
- Extracts text, tables, and structured elements
- Handles complex PDF layouts

### 2. Data Extraction
- **LLM-based extraction** (optional, recommended)
- Extracts structured data (tasks, costs, rules)
- Validates with Pydantic models

### 3. Dual Storage
- **PostgreSQL**: Structured, queryable data
- **ChromaDB**: Vector embeddings for semantic search

### 4. Prefect Orchestration
- Workflow orchestration with tasks and flows
- Error handling and retries
- Parallel processing support

### 5. REST API
- Django REST Framework endpoints
- Easy integration with other systems
- Standard JSON responses

## 📊 Data Schemas

### PostgreSQL Tables

#### project_tasks
```sql
- task_id (INTEGER, UNIQUE)
- task_name (VARCHAR)
- duration_days (INTEGER)
- start_date (DATE)
- finish_date (DATE)
```

#### cost_items
```sql
- item_name (VARCHAR)
- quantity (NUMERIC)
- unit_price_yen (NUMERIC)
- total_cost_yen (NUMERIC)
- cost_type (VARCHAR)
```

#### regulatory_rules
```sql
- rule_id (VARCHAR, UNIQUE)
- rule_summary (TEXT)
- measurement_basis (VARCHAR)
```

### ChromaDB Collection

- **Collection**: `real_estate_documents`
- **Embeddings**: `all-MiniLM-L6-v2` (384 dimensions)
- **Metadata**: document_name, chunk_index, etc.

## 🎬 Quick Demo (Sequential Steps)

### Option 1: Automated Script (Easiest)

```bash
./run_sequential_demo.sh
```

This will:
1. Start PostgreSQL
2. Initialize database
3. Run pipeline
4. Show outputs
5. Start web dashboard

### Option 2: Manual Steps

```bash
# 1. Start PostgreSQL
docker-compose up -d

# 2. Run pipeline
PREFECT_API_URL="" python run_pipeline.py

# 3. View outputs
python view_outputs.py

# 4. Start web dashboard
python manage.py runserver
# Open: http://localhost:8000
```

## 🔍 Usage Examples

### Process Documents

```python
from pipelines.document_pipeline import process_all_documents_flow

results = process_all_documents_flow()
print(f"Processed {len(results)} documents")
```

### View Outputs

```bash
# View PostgreSQL and ChromaDB data
python view_outputs.py
```

### Query PostgreSQL

```python
from database.postgres_client import PostgreSQLClient

client = PostgreSQLClient()
tasks = client.query_project_tasks(limit=10)
for task in tasks:
    print(task['task_name'])
```

### Semantic Search

```python
from database.chroma_client import ChromaDBClient

client = ChromaDBClient()
results = client.search("What are the project tasks?", n_results=5)
for result in results:
    print(result['chunk_text'])
```

## 🐛 Troubleshooting

### PostgreSQL Connection Failed
```bash
# Check if Docker container is running
docker ps | grep postgres

# Restart if needed
docker-compose restart postgres
```

### ChromaDB Issues
```bash
# Clear ChromaDB
rm -rf ./chroma_db
```

### Import Errors
```bash
# Ensure conda environment is activated
conda activate AI_Agents

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## 📝 Code Functioning

### Main Pipeline Flow

1. **Entry Point**: `run_pipeline.py` → `main()`
2. **Orchestration**: `process_all_documents_flow()` (Prefect flow)
3. **For Each Document**:
   - Parse PDF → `parse_pdf_task()`
   - Extract Data → `extract_structured_data_task()`
   - Load to PostgreSQL → `load_to_postgres_task()`
   - Chunk Document → `chunk_document_task()`
   - Load to ChromaDB → `load_to_chromadb_task()`

### Key Components

- **PDF Parser**: `documents/pdf_parser.py` - Unstructured.io integration
- **Extraction Agent**: `agents/extraction_agent.py` - LLM-based extraction
- **PostgreSQL Client**: `database/postgres_client.py` - Database operations
- **ChromaDB Client**: `database/chroma_client.py` - Vector storage
- **Prefect Pipeline**: `pipelines/document_pipeline.py` - Workflow orchestration

## 📚 Documentation

All documentation is included in this README file. Key sections:

- **Architecture**: System design and data flow
- **Quick Start**: Step-by-step setup instructions
- **API Endpoints**: REST API documentation
- **Configuration**: Environment variables and settings
- **Usage Examples**: Code examples for common tasks

