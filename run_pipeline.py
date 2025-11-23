#!/usr/bin/env python3
"""
Main script to run the document processing pipeline

This script:
1. Initializes the PostgreSQL database (creates tables if needed)
2. Processes all PDF documents in the configured directory
3. Extracts structured data (tasks, costs, rules) and stores in PostgreSQL
4. Creates document chunks and stores in ChromaDB for semantic search
5. Provides a summary of processing results

Usage:
    python run_pipeline.py

Environment Variables:
    - PDF_DIRECTORY: Directory containing PDF files (default: ./Data)
    - DATABASE_URL: PostgreSQL connection string
    - GROQ_API_KEY: API key for Groq LLM (required for data extraction)
    - See .env file for all configuration options
"""

import sys
from pathlib import Path
from utils.logger import logger
from pipelines.document_pipeline import process_all_documents_flow
from database.postgres_client import PostgreSQLClient
from config.settings import settings

def main():
    """
    Main function to run the document processing pipeline
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    logger.info("=" * 70)
    logger.info("🚀 Starting Real Estate Document Processing Pipeline")
    logger.info("=" * 70)
    
    # Step 1: Initialize database
    # Create PostgreSQL tables if they don't exist
    try:
        logger.info("📊 Step 1: Initializing PostgreSQL database...")
        logger.info(f"   Database URL: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'configured'}")
        db_client = PostgreSQLClient()
        db_client.create_tables()
        logger.info("   ✅ Database tables created/verified")
        
        # Execute DDL if needed (for additional schema definitions)
        ddl_path = Path(__file__).parent / "database" / "ddl.sql"
        if ddl_path.exists():
            logger.info("   📝 Executing DDL script...")
            db_client.execute_ddl(str(ddl_path))
            logger.info("   ✅ DDL script executed")
        
        logger.info("✅ Database initialization completed successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.warning("⚠️ Continuing without database initialization...")
        logger.warning("⚠️ Some features may not work correctly without database")
    
    # Step 2: Process documents
    # This will parse PDFs, extract structured data, and store in both databases
    try:
        logger.info("")
        logger.info("📄 Step 2: Processing documents from PDF directory...")
        logger.info(f"   PDF Directory: {settings.PDF_DIRECTORY}")
        
        # Document type mapping - maps PDF filenames to document types
        # This helps the extraction agent understand what type of data to extract
        document_types = {
            "Project schedule document.pdf": "schedule",
            "Construction planning and costing.pdf": "cost",
            "URA-Circular on GFA area definition.pdf": "regulatory",
            "construction approvals -long process chart.pdf": "regulatory"
        }
        logger.info(f"   Document type mappings: {len(document_types)} configured")
        
        # Execute the Prefect pipeline flow
        # This will process all PDFs in parallel where possible
        logger.info("   🔄 Starting Prefect pipeline flow...")
        results = process_all_documents_flow(
            pdf_directory=settings.PDF_DIRECTORY,
            document_types=document_types
        )
        logger.info("   ✅ Pipeline flow execution completed")
        
        # Step 3: Generate summary report
        successful = sum(1 for r in results if r.get("success", False))
        total = len(results)
        total_postgres_records = sum(r.get("postgres_records", 0) for r in results if r.get("success"))
        total_chroma_chunks = sum(r.get("chroma_chunks", 0) for r in results if r.get("success"))
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("📊 PIPELINE EXECUTION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"📁 Total documents processed: {total}")
        logger.info(f"✅ Successfully processed: {successful}")
        logger.info(f"❌ Failed: {total - successful}")
        logger.info(f"💾 PostgreSQL records created: {total_postgres_records}")
        logger.info(f"📦 ChromaDB chunks created: {total_chroma_chunks}")
        logger.info("")
        logger.info("📋 Detailed Results:")
        logger.info("-" * 70)
        
        for i, result in enumerate(results, 1):
            if result.get("success"):
                pdf_name = Path(result.get('pdf_path', '')).name
                logger.info(f"  {i}. ✅ {pdf_name}")
                logger.info(f"     - PostgreSQL: {result.get('postgres_records', 0)} records")
                logger.info(f"     - ChromaDB: {result.get('chroma_chunks', 0)} chunks")
                if result.get('extraction_errors'):
                    logger.warning(f"     - ⚠️ Extraction warnings: {len(result.get('extraction_errors', []))}")
            else:
                pdf_name = Path(result.get('pdf_path', '')).name
                logger.error(f"  {i}. ❌ {pdf_name}")
                logger.error(f"     - Error: {result.get('error', 'Unknown error')}")
        
        logger.info("=" * 70)
        
        if successful == total:
            logger.info("")
            logger.info("🎉 All documents processed successfully!")
            logger.info("💡 Next steps:")
            logger.info("   - View data: python view_outputs.py")
            logger.info("   - Start dashboard: python manage.py runserver")
            logger.info("   - Access dashboard: http://localhost:8000")
            return 0
        else:
            logger.warning("")
            logger.warning(f"⚠️ {total - successful} document(s) failed to process")
            logger.warning("💡 Check logs for detailed error information")
            return 1
            
    except Exception as e:
        logger.error("")
        logger.error("=" * 70)
        logger.error("❌ Pipeline execution failed with error:")
        logger.error("=" * 70)
        logger.error(f"Error: {e}")
        logger.error("")
        logger.error("Full traceback:")
        import traceback
        logger.error(traceback.format_exc())
        logger.error("=" * 70)
        logger.error("💡 Troubleshooting tips:")
        logger.error("   - Check that PostgreSQL is running: docker-compose up -d")
        logger.error("   - Verify API keys are set in .env file")
        logger.error("   - Check logs/app.log for detailed error information")
        logger.error("   - Ensure PDF files exist in the configured directory")
        return 1

if __name__ == "__main__":
    """
    Entry point for the pipeline script
    Run this script directly to process all documents
    """
    exit_code = main()
    sys.exit(exit_code)

