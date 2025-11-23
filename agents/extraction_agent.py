"""
Data Extraction Agent
Extracts structured data from parsed documents using LLM or rule-based methods
"""

import json
import re
from typing import List, Dict, Any, Optional
from utils.logger import logger
from utils.profiler import time_function
from agents.prompts import (
    PROJECT_TASK_EXTRACTION_PROMPT,
    COST_ITEM_EXTRACTION_PROMPT,
    REGULATORY_RULE_EXTRACTION_PROMPT,
    get_prompt
)
from database.models import ProjectTask, CostItem, RegulatoryRule

class ExtractionAgent:
    """Agent for extracting structured data from documents"""
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize extraction agent
        
        Args:
            use_llm: Whether to use LLM for extraction (default: True)
        """
        self.use_llm = use_llm
        if use_llm:
            try:
                from utils.llm_client import llm_client
                self.llm_client = llm_client
                logger.info("✅ Extraction Agent initialized with LLM support")
            except Exception as e:
                logger.warning(f"⚠️ LLM client not available: {e}. Falling back to rule-based extraction.")
                self.use_llm = False
        else:
            logger.info("✅ Extraction Agent initialized (rule-based only)")
    
    @time_function
    def extract(
        self, 
        document_text: str, 
        document_type: str
    ) -> Dict[str, Any]:
        """
        Extract structured data from document
        
        Args:
            document_text: Text content of the document
            document_type: Type of document (schedule, cost, regulatory)
            
        Returns:
            Dictionary with extracted_data and errors
        """
        try:
            logger.info(f"🔄 Extracting data from {document_type} document...")
            
            if self.use_llm:
                extracted_data = self._extract_with_llm(document_text, document_type)
            else:
                extracted_data = self._extract_with_rules(document_text, document_type)
            
            # Validate extracted data
            validated_data, errors = self._validate_data(extracted_data, document_type)
            
            return {
                "extracted_data": validated_data,
                "errors": errors,
                "success": len(errors) == 0
            }
            
        except Exception as e:
            logger.error(f"❌ Extraction agent error: {e}")
            return {
                "extracted_data": [],
                "errors": [str(e)],
                "success": False
            }
    
    def _extract_with_llm(self, document_text: str, document_type: str) -> List[Dict[str, Any]]:
        """Extract data using LLM"""
        try:
            # Select appropriate prompt based on document type
            if "schedule" in document_type.lower() or "project" in document_type.lower():
                prompt = get_prompt(PROJECT_TASK_EXTRACTION_PROMPT, document_text=document_text)
                system_prompt = "You are a data extraction expert. Extract project tasks from the document and return valid JSON only."
            elif "cost" in document_type.lower() or "costing" in document_type.lower():
                prompt = get_prompt(COST_ITEM_EXTRACTION_PROMPT, document_text=document_text)
                system_prompt = "You are a data extraction expert. Extract cost items from the document and return valid JSON only."
            elif "ura" in document_type.lower() or "regulatory" in document_type.lower() or "gfa" in document_type.lower():
                prompt = get_prompt(REGULATORY_RULE_EXTRACTION_PROMPT, document_text=document_text)
                system_prompt = "You are a data extraction expert. Extract regulatory rules from the document and return valid JSON only."
            else:
                logger.warning(f"⚠️ Unknown document type: {document_type}")
                return []
            
            # Call LLM
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            
            if not response or not response.strip():
                logger.error("❌ LLM returned empty response")
                return []
            
            # Parse JSON from response - try multiple strategies
            extracted_data = None
            
            # Strategy 1: Look for JSON array in response
            json_match = re.search(r'\[[\s\S]*\]', response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(0)
                    extracted_data = json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            # Strategy 2: Try parsing entire response as JSON
            if extracted_data is None:
                try:
                    extracted_data = json.loads(response.strip())
                except json.JSONDecodeError:
                    pass
            
            # Strategy 3: Look for JSON object and wrap in array
            if extracted_data is None:
                json_obj_match = re.search(r'\{[\s\S]*\}', response, re.DOTALL)
                if json_obj_match:
                    try:
                        json_str = json_obj_match.group(0)
                        obj = json.loads(json_str)
                        extracted_data = [obj] if isinstance(obj, dict) else obj
                    except json.JSONDecodeError:
                        pass
            
            if extracted_data is None:
                logger.error(f"❌ Failed to parse JSON from LLM response. Response preview: {response[:200]}")
                return []
            
            # Ensure it's a list
            if isinstance(extracted_data, dict):
                extracted_data = [extracted_data]
            
            logger.info(f"✅ Extracted {len(extracted_data)} items using LLM")
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Response was: {response[:500] if 'response' in locals() else 'N/A'}")
            return []
        except Exception as e:
            logger.error(f"❌ LLM extraction failed: {e}")
            return []
    
    def _extract_with_rules(self, document_text: str, document_type: str) -> List[Dict[str, Any]]:
        """Extract data using rule-based methods (fallback)"""
        logger.warning("⚠️ Rule-based extraction not fully implemented. Using LLM is recommended.")
        # This can be extended with regex patterns, table parsing, etc.
        return []
    
    def _validate_data(self, extracted_data: List[Dict[str, Any]], document_type: str) -> tuple:
        """
        Validate extracted data against Pydantic models
        
        Returns:
            Tuple of (validated_data, errors)
        """
        validated_data = []
        errors = []
        
        if not extracted_data:
            return validated_data, errors
        
        # Validate based on document type
        if "schedule" in document_type.lower() or "project" in document_type.lower():
            for item in extracted_data:
                try:
                    validated_item = ProjectTask(**item)
                    validated_data.append(validated_item.dict())
                except Exception as e:
                    errors.append(f"Validation error for task {item.get('task_id', 'unknown')}: {e}")
                    logger.warning(f"⚠️ Validation error: {e}")
        
        elif "cost" in document_type.lower() or "costing" in document_type.lower():
            for item in extracted_data:
                try:
                    validated_item = CostItem(**item)
                    validated_data.append(validated_item.dict())
                except Exception as e:
                    errors.append(f"Validation error for cost item {item.get('item_name', 'unknown')}: {e}")
                    logger.warning(f"⚠️ Validation error: {e}")
        
        elif "ura" in document_type.lower() or "regulatory" in document_type.lower() or "gfa" in document_type.lower():
            for item in extracted_data:
                try:
                    validated_item = RegulatoryRule(**item)
                    validated_data.append(validated_item.dict())
                except Exception as e:
                    errors.append(f"Validation error for rule {item.get('rule_id', 'unknown')}: {e}")
                    logger.warning(f"⚠️ Validation error: {e}")
        
        logger.info(f"✅ Validated {len(validated_data)} items, {len(errors)} errors")
        return validated_data, errors

__all__ = ["ExtractionAgent"]
