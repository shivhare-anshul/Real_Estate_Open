#!/usr/bin/env python3
"""
Unstructured.io PDF Parser (Open Source Version)
This module provides PDF parsing functionality using Unstructured.io library
"""

import os
import json
import time
import asyncio
import warnings
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from utils.logger import logger
from utils.profiler import time_function
from config.settings import settings

# Suppress pdfminer warnings about invalid color values (harmless PDF parsing warnings)
warnings.filterwarnings("ignore", category=UserWarning, module="pdfminer")
warnings.filterwarnings("ignore", message=".*invalid float value.*")

# Suppress pdfminer logging warnings
logging.getLogger("pdfminer").setLevel(logging.ERROR)

try:
    from unstructured.partition.pdf import partition_pdf
    from unstructured.staging.base import elements_to_json
    from unstructured.chunking.title import chunk_by_title
except ImportError:
    logger.error("❌ Unstructured.io not installed. Please install with: pip install unstructured[pdf]")
    raise

class UnstructuredParser:
    """
    PDF Parser using Unstructured.io Open Source Library
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the Unstructured parser
        
        Args:
            output_dir: Directory to save parsed outputs (defaults to settings)
        """
        self.output_dir = Path(output_dir or settings.PARSED_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectory for unstructured outputs
        self.unstructured_dir = self.output_dir / "Unstructured_OpenSource_Parsed_output"
        self.unstructured_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Unstructured Parser initialized")
    
    @time_function
    def parse_pdf(self, pdf_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> Dict[str, Any]:
        """
        Parse a PDF file using Unstructured.io
        
        Args:
            pdf_path: Path to the PDF file
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Dictionary containing parsed content and metadata
        """
        try:
            logger.info(f"🔍 Parsing PDF with Unstructured.io: {pdf_path}")
            start_time = time.time()
            
            # Suppress pdfminer warnings during parsing
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="pdfminer")
                warnings.filterwarnings("ignore", message=".*invalid float value.*")
                
                # Parse PDF into elements
                elements = partition_pdf(
                    filename=pdf_path,
                    strategy="hi_res",  # High resolution strategy for better accuracy
                    extract_images_in_pdf=False,
                    infer_table_structure=False
                )
            
            # Convert elements to JSON for structured output
            elements_json = elements_to_json(elements)
            
            # Chunk the content by title for better organization
            chunks = chunk_by_title(elements, max_characters=chunk_size, combine_text_under_n_chars=chunk_overlap)
            
            # Extract text content
            full_text = "\n\n".join([str(element) for element in elements])
            
            # Extract structured information
            structured_content = self._extract_structured_content(elements)
            
            # Prepare result
            result = {
                "method": "unstructured",
                "pdf_path": pdf_path,
                "timestamp": datetime.now().isoformat(),
                "processing_time": time.time() - start_time,
                "success": True,
                "metadata": {
                    "total_elements": len(elements),
                    "total_chunks": len(chunks),
                    "text_length": len(full_text),
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap
                },
                "content": {
                    "full_text": full_text,
                    "structured_content": structured_content,
                    "elements_json": elements_json,
                    "chunks": [str(chunk) for chunk in chunks]
                }
            }
            
            # Save result to file
            self._save_result(result, pdf_path)
            
            logger.info(f"✅ Successfully parsed PDF: {pdf_path}")
            logger.info(f"📊 Elements: {len(elements)}, Chunks: {len(chunks)}, Text length: {len(full_text)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error parsing PDF {pdf_path}: {e}")
            return self._create_error_result(pdf_path, str(e))
    
    async def parse_pdf_async(self, pdf_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> Dict[str, Any]:
        """
        Async version of parse_pdf for parallel processing
        
        Args:
            pdf_path: Path to the PDF file
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Dictionary containing parsed content and metadata
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.parse_pdf, pdf_path, chunk_size, chunk_overlap)
    
    def _extract_structured_content(self, elements) -> Dict[str, Any]:
        """
        Extract structured content from elements
        
        Args:
            elements: List of parsed elements
            
        Returns:
            Dictionary with structured content
        """
        structured = {
            "titles": [],
            "paragraphs": [],
            "tables": [],
            "lists": [],
            "headers": [],
            "footers": []
        }
        
        for element in elements:
            element_type = type(element).__name__
            element_text = str(element)
            
            if element_type == "Title":
                structured["titles"].append(element_text)
            elif element_type == "NarrativeText":
                structured["paragraphs"].append(element_text)
            elif element_type == "Table":
                structured["tables"].append(element_text)
            elif element_type == "ListItem":
                structured["lists"].append(element_text)
            elif element_type == "Header":
                structured["headers"].append(element_text)
            elif element_type == "Footer":
                structured["footers"].append(element_text)
        
        return structured
    
    def _create_error_result(self, pdf_path: str, error_msg: str) -> Dict[str, Any]:
        """Create error result dictionary"""
        return {
            "method": "unstructured",
            "pdf_path": pdf_path,
            "timestamp": datetime.now().isoformat(),
            "error": error_msg,
            "success": False
        }
    
    def _save_result(self, result: Dict[str, Any], pdf_path: str):
        """
        Save parsing result to file
        
        Args:
            result: Parsing result dictionary
            pdf_path: Original PDF path for naming
        """
        try:
            # Create filename based on PDF name
            pdf_name = Path(pdf_path).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"unstructured_{pdf_name}_{timestamp}.json"
            
            # Save to unstructured subdirectory
            output_path = self.unstructured_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Saved result to: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Error saving result: {e}")
    
    @time_function
    def parse_multiple_pdfs(self, pdf_directory: str) -> List[Dict[str, Any]]:
        """
        Parse multiple PDF files from a directory
        
        Args:
            pdf_directory: Directory containing PDF files
            
        Returns:
            List of parsing results
        """
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            logger.error(f"❌ Directory not found: {pdf_directory}")
            return []
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        logger.info(f"📁 Found {len(pdf_files)} PDF files to parse")
        
        results = []
        for pdf_file in pdf_files:
            logger.info(f"🔄 Processing: {pdf_file.name}")
            result = self.parse_pdf(str(pdf_file))
            results.append(result)
        
        return results
    
    def get_parsing_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary of parsing results
        
        Args:
            results: List of parsing results
            
        Returns:
            Summary dictionary
        """
        successful = [r for r in results if r.get("success", True)]
        failed = [r for r in results if not r.get("success", True)]
        
        total_elements = sum(r.get("metadata", {}).get("total_elements", 0) for r in successful)
        total_text_length = sum(r.get("metadata", {}).get("text_length", 0) for r in successful)
        avg_processing_time = sum(r.get("processing_time", 0) for r in successful) / len(successful) if successful else 0
        
        return {
            "total_files": len(results),
            "successful_parses": len(successful),
            "failed_parses": len(failed),
            "total_elements_extracted": total_elements,
            "total_text_length": total_text_length,
            "average_processing_time": avg_processing_time,
            "method": "unstructured",
            "timestamp": datetime.now().isoformat()
        }

__all__ = ["UnstructuredParser"]

