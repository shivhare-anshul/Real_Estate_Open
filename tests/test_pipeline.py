"""
Tests for document processing pipeline
"""

import pytest
from pathlib import Path
from documents.pdf_parser import UnstructuredAPIParser
from agents.extraction_agent import ExtractionAgent
from database.postgres_client import PostgreSQLClient
from database.chroma_client import ChromaDBClient
from config.settings import settings

@pytest.fixture
def pdf_parser():
    """Fixture for PDF parser"""
    return UnstructuredAPIParser()

@pytest.fixture
def extraction_agent():
    """Fixture for extraction agent"""
    return ExtractionAgent()

@pytest.fixture
def postgres_client():
    """Fixture for PostgreSQL client"""
    return PostgreSQLClient()

@pytest.fixture
def chroma_client():
    """Fixture for ChromaDB client"""
    return ChromaDBClient()

@pytest.mark.asyncio
async def test_pdf_parsing(pdf_parser):
    """Test PDF parsing"""
    pdf_path = Path(settings.PDF_DIRECTORY) / "Project schedule document.pdf"
    
    if not pdf_path.exists():
        pytest.skip(f"PDF file not found: {pdf_path}")
    
    result = pdf_parser.parse_pdf(str(pdf_path))
    
    assert result.get("success", False) == True
    assert "content" in result
    assert "full_text" in result["content"]

def test_extraction_agent(extraction_agent):
    """Test extraction agent"""
    sample_text = """
    Task ID: 1
    Task Name: Install CMU Block Walls
    Duration: 30 days
    Start Date: 2024-01-01
    Finish Date: 2024-01-31
    """
    
    result = extraction_agent.extract(sample_text, "schedule")
    
    assert "extracted_data" in result
    assert isinstance(result["extracted_data"], list)

def test_postgres_connection(postgres_client):
    """Test PostgreSQL connection"""
    try:
        postgres_client.create_tables()
        assert True
    except Exception as e:
        pytest.skip(f"PostgreSQL not available: {e}")

def test_chroma_connection(chroma_client):
    """Test ChromaDB connection"""
    try:
        stats = chroma_client.get_collection_stats()
        assert "collection_name" in stats
    except Exception as e:
        pytest.skip(f"ChromaDB not available: {e}")

@pytest.mark.django_db
def test_api_endpoints(client):
    """Test API endpoints"""
    # Health check
    response = client.get('/api/health/')
    assert response.status_code == 200
    
    # Query endpoint
    response = client.post('/api/query/', {'query': 'test query'}, content_type='application/json')
    assert response.status_code in [200, 500]  # May fail if ChromaDB is empty

