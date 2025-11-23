#!/usr/bin/env python3
"""
Component Testing Script
Tests each component individually: PDF parsing, data extraction, database operations
"""

import sys
from pathlib import Path
from utils.logger import logger

def test_pdf_parsing():
    """Test Unstructured.io PDF parsing"""
    logger.info("=" * 60)
    logger.info("TEST 1: PDF Parsing with Unstructured.io")
    logger.info("=" * 60)
    
    try:
        from documents.pdf_parser import UnstructuredParser
        
        # Test with Project Schedule Document
        pdf_path = Path("./Data/Project schedule document.pdf")
        if not pdf_path.exists():
            logger.error(f"❌ PDF not found: {pdf_path}")
            return False
        
        logger.info(f"📄 Parsing: {pdf_path}")
        parser = UnstructuredParser()
        result = parser.parse_pdf(str(pdf_path))
        
        if result.get("success"):
            logger.info(f"✅ PDF parsing successful!")
            logger.info(f"   Elements: {result['metadata']['total_elements']}")
            logger.info(f"   Text length: {result['metadata']['text_length']}")
            logger.info(f"   Chunks: {result['metadata']['total_chunks']}")
            return True
        else:
            logger.error(f"❌ PDF parsing failed: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ PDF parsing test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_data_extraction():
    """Test data extraction agent"""
    logger.info("=" * 60)
    logger.info("TEST 2: Data Extraction Agent")
    logger.info("=" * 60)
    
    try:
        from agents.extraction_agent import ExtractionAgent
        
        # Sample text for testing
        sample_text = """
        Task ID: 1
        Task Name: Install CMU Block Walls
        Duration: 30 days
        Start Date: 2024-01-01
        Finish Date: 2024-01-31
        """
        
        logger.info("🔄 Testing extraction with sample text...")
        agent = ExtractionAgent(use_llm=False)  # Test without LLM first
        
        result = agent.extract(sample_text, "schedule")
        
        logger.info(f"✅ Extraction test completed")
        logger.info(f"   Extracted items: {len(result.get('extracted_data', []))}")
        logger.info(f"   Errors: {len(result.get('errors', []))}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Extraction test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_postgres_connection():
    """Test PostgreSQL connection"""
    logger.info("=" * 60)
    logger.info("TEST 3: PostgreSQL Connection")
    logger.info("=" * 60)
    
    try:
        from database.postgres_client import PostgreSQLClient
        
        logger.info("🔄 Testing PostgreSQL connection...")
        client = PostgreSQLClient()
        
        # Test connection by creating tables
        client.create_tables()
        logger.info("✅ PostgreSQL connection successful!")
        logger.info("✅ Tables created/verified")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        logger.error("   Make sure PostgreSQL is running and credentials are correct in .env")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_chromadb_connection():
    """Test ChromaDB connection"""
    logger.info("=" * 60)
    logger.info("TEST 4: ChromaDB Connection")
    logger.info("=" * 60)
    
    try:
        from database.chroma_client import ChromaDBClient
        
        logger.info("🔄 Testing ChromaDB connection...")
        client = ChromaDBClient()
        
        # Get stats
        stats = client.get_collection_stats()
        logger.info(f"✅ ChromaDB connection successful!")
        logger.info(f"   Collection: {stats.get('collection_name')}")
        logger.info(f"   Total chunks: {stats.get('total_chunks', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ChromaDB connection failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_dlt_pipeline():
    """Test dltHub pipeline"""
    logger.info("=" * 60)
    logger.info("TEST 5: dltHub Pipeline")
    logger.info("=" * 60)
    
    try:
        from pipelines.dlt_pipeline import create_postgres_pipeline
        
        logger.info("🔄 Testing dltHub pipeline creation...")
        pipeline = create_postgres_pipeline()
        
        logger.info(f"✅ dltHub pipeline created successfully!")
        logger.info(f"   Pipeline name: {pipeline.pipeline_name}")
        logger.info(f"   Destination: {pipeline.destination}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ dltHub pipeline test failed: {e}")
        logger.warning("   This is okay if dltHub is not configured yet")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_prefect_flow():
    """Test Prefect flow definition"""
    logger.info("=" * 60)
    logger.info("TEST 6: Prefect Flow Definition")
    logger.info("=" * 60)
    
    try:
        from pipelines.document_pipeline import process_document_flow
        
        logger.info("🔄 Testing Prefect flow definition...")
        logger.info(f"✅ Prefect flow loaded successfully!")
        logger.info(f"   Flow name: {process_document_flow.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Prefect flow test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Run all component tests"""
    logger.info("🚀 Starting Component Tests")
    logger.info("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("PDF Parsing", test_pdf_parsing()))
    results.append(("Data Extraction", test_data_extraction()))
    results.append(("PostgreSQL Connection", test_postgres_connection()))
    results.append(("ChromaDB Connection", test_chromadb_connection()))
    results.append(("dltHub Pipeline", test_dlt_pipeline()))
    results.append(("Prefect Flow", test_prefect_flow()))
    
    # Summary
    logger.info("=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info("=" * 60)
    logger.info(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    logger.info("=" * 60)
    
    if failed == 0:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.warning(f"⚠️ {failed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

