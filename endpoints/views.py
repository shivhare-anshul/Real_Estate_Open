"""
API Views for Real Estate Data Pipeline
"""

import asyncio
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from typing import Dict, Any
from utils.logger import logger
from pipelines.document_pipeline import process_document_flow, process_all_documents_flow
from database.postgres_client import PostgreSQLClient
from database.chroma_client import ChromaDBClient
from config.settings import settings

# Configure Prefect to run in ephemeral mode (no server required)
# This allows Prefect flows to run without connecting to a Prefect server
if not os.getenv("PREFECT_API_URL"):
    os.environ["PREFECT_API_URL"] = ""

# Initialize clients
chroma_client = ChromaDBClient()
postgres_client = PostgreSQLClient()

@api_view(['POST'])
def process_document(request):
    """
    Process a single document
    
    Request body:
    {
        "pdf_path": "/path/to/document.pdf",
        "document_type": "schedule" | "cost" | "regulatory"
    }
    """
    try:
        pdf_path = request.data.get('pdf_path')
        document_type = request.data.get('document_type', 'general')
        
        if not pdf_path:
            return Response(
                {"error": "pdf_path is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"📥 API request to process document: {pdf_path}")
        
        # Run Prefect flow
        result = process_document_flow(pdf_path, document_type)
        
        if result.get("success"):
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"❌ Error processing document: {e}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def process_all_documents(request):
    """
    Process all documents in the configured directory
    
    Request body (optional):
    {
        "pdf_directory": "/path/to/directory",
        "document_types": {
            "file1.pdf": "schedule",
            "file2.pdf": "cost"
        }
    }
    """
    try:
        # Get parameters from request (may be None if not provided)
        pdf_directory = request.data.get('pdf_directory') or None
        document_types = request.data.get('document_types') or None
        
        logger.info(f"📥 API request to process all documents")
        
        # Run Prefect flow - it will use defaults from settings if None
        results = process_all_documents_flow(
            pdf_directory=pdf_directory,
            document_types=document_types
        )
        
        return Response(
            {
                "success": True,
                "results": results,
                "total": len(results),
                "successful": sum(1 for r in results if r.get("success", False))
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing documents: {e}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def semantic_search(request):
    """
    Semantic search in ChromaDB
    
    Request body:
    {
        "query": "What is the total cost of bearing piles?",
        "n_results": 5
    }
    """
    try:
        user_query = request.data.get('query')
        n_results = request.data.get('n_results', 5)
        
        if not user_query:
            return Response(
                {"error": "query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"📥 Semantic search request: {user_query}")
        
        # Search in ChromaDB
        results = chroma_client.search(query=user_query, n_results=n_results)
        
        return Response(
            {
                "query": user_query,
                "results": results,
                "count": len(results)
            },
            status=status.HTTP_200_OK
        )
            
    except Exception as e:
        logger.error(f"❌ Error in semantic search: {e}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_project_tasks(request):
    """Get project tasks from PostgreSQL"""
    try:
        limit = int(request.query_params.get('limit', 100))
        tasks = postgres_client.query_project_tasks(limit=limit)
        return Response({"tasks": tasks}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"❌ Error querying project tasks: {e}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_cost_items(request):
    """Get cost items from PostgreSQL"""
    try:
        limit = int(request.query_params.get('limit', 100))
        items = postgres_client.query_cost_items(limit=limit)
        return Response({"items": items}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"❌ Error querying cost items: {e}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_chroma_stats(request):
    """Get ChromaDB collection statistics"""
    try:
        stats = chroma_client.get_collection_stats()
        return Response(stats, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"❌ Error getting ChromaDB stats: {e}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response(
        {
            "status": "healthy",
            "service": "Real Estate Data Pipeline API"
        },
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
def clear_databases(request):
    """
    Clear all data from PostgreSQL and ChromaDB
    WARNING: This will delete all data
    """
    try:
        logger.warning("🗑️ API request to clear all databases")
        
        # Clear PostgreSQL
        postgres_result = postgres_client.clear_all_data()
        
        # Clear ChromaDB
        chroma_result = chroma_client.clear_all_data()
        
        return Response(
            {
                "success": True,
                "message": "Databases cleared successfully",
                "postgres": postgres_result,
                "chroma": chroma_result
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"❌ Error clearing databases: {e}")
        return Response(
            {"error": str(e), "success": False},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

