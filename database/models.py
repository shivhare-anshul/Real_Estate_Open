"""
Pydantic models for structured data extraction
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

class ProjectTask(BaseModel):
    """Model for Project Task from Project Schedule Document"""
    task_id: int = Field(..., description="Unique ID for the task")
    task_name: str = Field(..., description="Name of the task")
    duration_days: int = Field(..., ge=0, description="Duration in days")
    start_date: date = Field(..., description="Start date of the task")
    finish_date: date = Field(..., description="Finish date of the task")
    
    @validator('finish_date')
    def validate_finish_after_start(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('finish_date must be after start_date')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": 1,
                "task_name": "Install CMU Block Walls",
                "duration_days": 30,
                "start_date": "2024-01-01",
                "finish_date": "2024-01-31"
            }
        }

class CostItem(BaseModel):
    """Model for Cost Item from Construction Planning and Costing Document"""
    item_name: str = Field(..., description="Description of the cost item")
    quantity: Decimal = Field(..., ge=0, description="Extracted quantity")
    unit_price_yen: Decimal = Field(..., ge=0, description="Unit price in Yen")
    total_cost_yen: Decimal = Field(..., ge=0, description="Total cost in Yen")
    cost_type: str = Field(..., description="Foreign cost or local cost")
    
    @validator('cost_type')
    def validate_cost_type(cls, v):
        allowed = ['Foreign cost', 'Local cost', 'foreign cost', 'local cost']
        if v not in allowed:
            raise ValueError(f'cost_type must be one of {allowed}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_name": "Bearing Pile",
                "quantity": 736.2,
                "unit_price_yen": 79000,
                "total_cost_yen": 58159800,
                "cost_type": "Foreign cost"
            }
        }

class RegulatoryRule(BaseModel):
    """Model for Regulatory Rules from URA Circular"""
    rule_id: str = Field(..., description="Unique identifier (e.g., Q1, Q2, Q17)")
    rule_summary: str = Field(..., description="Concise summary of the rule/clarification")
    measurement_basis: str = Field(..., description="Key measurement principle and associated rule")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rule_id": "Q1",
                "rule_summary": "Definition of GFA calculation method",
                "measurement_basis": "middle of the external wall"
            }
        }

class DocumentChunk(BaseModel):
    """Model for document chunks for vector storage"""
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    document_name: str = Field(..., description="Name of the source document")
    chunk_text: str = Field(..., description="Text content of the chunk")
    chunk_index: int = Field(..., ge=0, description="Index of the chunk in the document")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "doc1_chunk_0",
                "document_name": "Project schedule document.pdf",
                "chunk_text": "Task 1: Install CMU Block Walls...",
                "chunk_index": 0,
                "metadata": {"page": 1, "type": "table"}
            }
        }

__all__ = ["ProjectTask", "CostItem", "RegulatoryRule", "DocumentChunk"]

