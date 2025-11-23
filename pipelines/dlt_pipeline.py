"""
dltHub pipeline for data transformation and loading
"""

import dlt
from typing import List, Dict, Any
from utils.logger import logger
from database.models import ProjectTask, CostItem, RegulatoryRule

def create_postgres_pipeline(connection_string: str = None):
    """
    Create dlt pipeline for PostgreSQL
    
    Args:
        connection_string: Optional PostgreSQL connection string
        
    Returns:
        dlt pipeline instance
    """
    from config.settings import settings
    
    # Use provided connection string or from settings
    conn_str = connection_string or settings.DATABASE_URL
    
    try:
        # dlt uses environment variable or config file for credentials
        # Set it as environment variable
        import os
        os.environ["DESTINATION__POSTGRES__CREDENTIALS"] = conn_str
        
        return dlt.pipeline(
            pipeline_name="real_estate_pipeline",
            destination="postgres",
            dataset_name="real_estate_data"
        )
    except Exception as e:
        # If dlt fails, return None (will use fallback)
        logger.warning(f"⚠️ dltHub pipeline creation failed: {e}")
        return None

@dlt.resource
def project_tasks_resource(tasks: List[Dict[str, Any]]):
    """dlt resource for project tasks"""
    for task in tasks:
        yield task

@dlt.resource
def cost_items_resource(items: List[Dict[str, Any]]):
    """dlt resource for cost items"""
    for item in items:
        yield item

@dlt.resource
def regulatory_rules_resource(rules: List[Dict[str, Any]]):
    """dlt resource for regulatory rules"""
    for rule in rules:
        yield rule

def load_to_postgres_with_dlt(
    project_tasks: List[Dict[str, Any]] = None,
    cost_items: List[Dict[str, Any]] = None,
    regulatory_rules: List[Dict[str, Any]] = None,
    connection_string: str = None
):
    """
    Load data to PostgreSQL using dltHub
    
    Args:
        project_tasks: List of project task dictionaries
        cost_items: List of cost item dictionaries
        regulatory_rules: List of regulatory rule dictionaries
        connection_string: PostgreSQL connection string
    """
    try:
        logger.info("🔄 Loading data to PostgreSQL using dltHub...")
        
        # Create pipeline
        pipeline = create_postgres_pipeline()
        
        # Prepare resources
        resources = []
        
        if project_tasks:
            resources.append(project_tasks_resource(project_tasks))
        
        if cost_items:
            resources.append(cost_items_resource(cost_items))
        
        if regulatory_rules:
            resources.append(regulatory_rules_resource(regulatory_rules))
        
        if not resources:
            logger.warning("⚠️ No data to load")
            return
        
        # Run pipeline
        info = pipeline.run(resources)
        
        logger.info(f"✅ Data loaded successfully: {info}")
        return info
        
    except Exception as e:
        logger.error(f"❌ Error loading data with dltHub: {e}")
        raise

__all__ = ["load_to_postgres_with_dlt", "create_postgres_pipeline"]

