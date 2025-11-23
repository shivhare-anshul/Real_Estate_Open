"""
Prefect pipeline for document processing
Extracts structured and unstructured data from PDFs
"""

import asyncio
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from prefect import flow, task, get_run_logger
from prefect.task_runners import ConcurrentTaskRunner
from utils.logger import logger
from documents.pdf_parser import UnstructuredParser
from agents.extraction_agent import ExtractionAgent
from database.postgres_client import PostgreSQLClient
from database.chroma_client import ChromaDBClient
from database.models import ProjectTask, CostItem, DocumentChunk
from pipelines.dlt_pipeline import load_to_postgres_with_dlt
from config.settings import settings

# Configure Prefect to run in ephemeral mode (no server required)
# This allows Prefect flows to run without connecting to a Prefect server
if not os.getenv("PREFECT_API_URL"):
    os.environ["PREFECT_API_URL"] = ""

@task(name="parse_pdf", retries=2, retry_delay_seconds=5)
def parse_pdf_task(pdf_path: str) -> Dict[str, Any]:
    """
    Task to parse a PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Parsed document data
    """
    logger.info(f"📄 Parsing PDF: {pdf_path}")
    parser = UnstructuredParser()
    result = parser.parse_pdf(pdf_path)
    
    if not result.get("success", False):
        raise Exception(f"Failed to parse PDF: {pdf_path}")
    
    return result

@task(name="extract_structured_data")
def extract_structured_data_task(
    parsed_data: Dict[str, Any],
    document_type: str
) -> Dict[str, Any]:
    """
    Task to extract structured data from parsed document
    
    Args:
        parsed_data: Parsed document data
        document_type: Type of document
        
    Returns:
        Extracted structured data
    """
    logger.info(f"🔍 Extracting structured data from {document_type} document")
    
    agent = ExtractionAgent()
    document_text = parsed_data.get("content", {}).get("full_text", "")
    
    result = agent.extract(document_text, document_type)
    
    if not result.get("success", False):
        logger.warning(f"⚠️ Extraction had errors: {result.get('errors', [])}")
    
    return result

@task(name="load_to_postgres")
def load_to_postgres_task(
    extracted_data: Dict[str, Any],
    document_type: str
) -> int:
    """
    Task to load structured data to PostgreSQL using dltHub
    
    Args:
        extracted_data: Extracted structured data
        document_type: Type of document
        
    Returns:
        Number of records inserted
    """
    logger.info(f"💾 Loading {document_type} data to PostgreSQL using dltHub")
    
    data = extracted_data.get("extracted_data", [])
    
    if not data:
        logger.warning("⚠️ No data to load")
        return 0
    
    try:
        # Use dltHub for loading
        if "schedule" in document_type.lower() or "project" in document_type.lower():
            load_to_postgres_with_dlt(project_tasks=data, connection_string=settings.DATABASE_URL)
            inserted_count = len(data)
        
        elif "cost" in document_type.lower() or "costing" in document_type.lower():
            load_to_postgres_with_dlt(cost_items=data, connection_string=settings.DATABASE_URL)
            inserted_count = len(data)
        
        elif "ura" in document_type.lower() or "regulatory" in document_type.lower() or "gfa" in document_type.lower():
            load_to_postgres_with_dlt(regulatory_rules=data, connection_string=settings.DATABASE_URL)
            inserted_count = len(data)
        else:
            inserted_count = 0
        
        logger.info(f"✅ Loaded {inserted_count} records to PostgreSQL using dltHub")
        return inserted_count
        
    except Exception as e:
        logger.error(f"❌ Error loading with dltHub, falling back to direct insert: {e}")
        # Fallback to direct database insert
        db_client = PostgreSQLClient()
        
        if "schedule" in document_type.lower() or "project" in document_type.lower():
            tasks = [ProjectTask(**item) for item in data]
            inserted_count = db_client.insert_project_tasks(tasks)
        elif "cost" in document_type.lower() or "costing" in document_type.lower():
            items = [CostItem(**item) for item in data]
            inserted_count = db_client.insert_cost_items(items)
        else:
            inserted_count = 0
        
        return inserted_count

@task(name="chunk_document")
def chunk_document_task(
    parsed_data: Dict[str, Any],
    document_name: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Dict[str, Any]]:
    """
    Task to chunk document for vector storage
    
    Args:
        parsed_data: Parsed document data
        document_name: Name of the document
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of document chunks
    """
    logger.info(f"📦 Chunking document: {document_name}")
    
    full_text = parsed_data.get("content", {}).get("full_text", "")
    
    if not full_text:
        logger.warning("⚠️ No text to chunk")
        return []
    
    # Simple chunking by character count with overlap
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(full_text):
        end = start + chunk_size
        chunk_text = full_text[start:end]
        
        chunks.append({
            "chunk_id": f"{Path(document_name).stem}_chunk_{chunk_index}",
            "document_name": document_name,
            "chunk_text": chunk_text,
            "chunk_index": chunk_index,
            "metadata": {
                "start_char": start,
                "end_char": end,
                "chunk_size": len(chunk_text)
            }
        })
        
        start = end - chunk_overlap
        chunk_index += 1
    
    logger.info(f"✅ Created {len(chunks)} chunks from {document_name}")
    return chunks

@task(name="load_to_chromadb")
def load_to_chromadb_task(chunks: List[Dict[str, Any]]) -> int:
    """
    Task to load chunks to ChromaDB
    
    Args:
        chunks: List of document chunks
        
    Returns:
        Number of chunks loaded
    """
    logger.info(f"💾 Loading {len(chunks)} chunks to ChromaDB")
    
    chroma_client = ChromaDBClient()
    
    # Convert to DocumentChunk objects
    document_chunks = [DocumentChunk(**chunk) for chunk in chunks]
    
    inserted_count = chroma_client.add_chunks(document_chunks)
    
    logger.info(f"✅ Loaded {inserted_count} chunks to ChromaDB")
    return inserted_count

@task(name="notify_failure")
def notify_failure_task(error: str, document_path: str):
    """
    Task to notify on extraction failure
    
    Args:
        error: Error message
        document_path: Path to failed document
    """
    logger.error(f"❌ Extraction failed for {document_path}: {error}")
    # In production, this could send email, Slack notification, etc.
    # For now, just log the error

@flow(
    name="process_document",
    task_runner=ConcurrentTaskRunner(),
    retries=1,
    retry_delay_seconds=10,
    persist_result=False
)
def process_document_flow(
    pdf_path: str,
    document_type: str
) -> Dict[str, Any]:
    """
    Main flow to process a single document
    
    Args:
        pdf_path: Path to PDF file
        document_type: Type of document (schedule, cost, regulatory)
        
    Returns:
        Processing results
    """
    logger.info(f"🚀 Starting document processing flow for: {pdf_path}")
    
    try:
        # Step 1: Parse PDF
        parsed_data = parse_pdf_task(pdf_path)
        
        # Step 2: Extract structured data
        extracted_data = extract_structured_data_task(parsed_data, document_type)
        
        # Step 3: Load to PostgreSQL (only if extraction was successful)
        postgres_count = 0
        if extracted_data.get("extracted_data"):
            postgres_count = load_to_postgres_task(extracted_data, document_type)
        
        # Step 4: Chunk document for vector storage
        document_name = Path(pdf_path).name
        chunks = chunk_document_task(parsed_data, document_name)
        
        # Step 5: Load to ChromaDB
        chroma_count = 0
        if chunks:
            chroma_count = load_to_chromadb_task(chunks)
        
        result = {
            "success": True,
            "pdf_path": pdf_path,
            "document_type": document_type,
            "postgres_records": postgres_count,
            "chroma_chunks": chroma_count,
            "extraction_errors": extracted_data.get("errors", [])
        }
        
        logger.info(f"✅ Document processing completed: {pdf_path}")
        return result
        
    except Exception as e:
        error_msg = str(e)
        notify_failure_task(error_msg, pdf_path)
        logger.error(f"❌ Document processing failed: {pdf_path} - {error_msg}")
        return {
            "success": False,
            "pdf_path": pdf_path,
            "error": error_msg
        }

@flow(name="process_all_documents", persist_result=False)
def process_all_documents_flow(
    pdf_directory: Optional[str] = None,
    document_types: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Flow to process all documents in a directory
    
    Args:
        pdf_directory: Directory containing PDF files
        document_types: Mapping of PDF filenames to document types
        
    Returns:
        List of processing results
    """
    pdf_dir = Path(pdf_directory or settings.PDF_DIRECTORY)
    
    if not pdf_dir.exists():
        logger.error(f"❌ PDF directory not found: {pdf_dir}")
        return []
    
    # Default document type mapping
    if document_types is None:
        document_types = {
            "Project schedule document.pdf": "schedule",
            "Construction planning and costing.pdf": "cost",
            "URA-Circular on GFA area definition.pdf": "regulatory",
            "construction approvals -long process chart.pdf": "regulatory"
        }
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    logger.info(f"📁 Found {len(pdf_files)} PDF files to process")
    
    results = []
    for pdf_file in pdf_files:
        # Determine document type
        doc_type = document_types.get(pdf_file.name, "general")
        
        # Process document
        result = process_document_flow(str(pdf_file), doc_type)
        results.append(result)
    
    # Summary
    successful = sum(1 for r in results if r.get("success", False))
    logger.info(f"📊 Processing complete: {successful}/{len(results)} documents processed successfully")
    
    return results

__all__ = ["process_document_flow", "process_all_documents_flow"]

