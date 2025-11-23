"""
Jinja2 prompt templates for agents
"""

from jinja2 import Template
from typing import Dict, Any

# Prompt for extracting project tasks from schedule document
PROJECT_TASK_EXTRACTION_PROMPT = Template("""
You are an expert data extraction agent specializing in construction project schedules.

Extract all project tasks from the following document text. Each task should have:
- task_id: A unique integer ID (extract from ID column if available, or assign sequentially)
- task_name: The name/description of the task
- duration_days: Duration in days (convert from weeks/months if needed)
- start_date: Start date in YYYY-MM-DD format
- finish_date: Finish date in YYYY-MM-DD format

Document Text:
{{ document_text }}

Return the extracted tasks as a JSON array. Each task should be a JSON object with the exact fields specified above.
If a date is not in YYYY-MM-DD format, convert it. If duration is not in days, convert it appropriately.

Example output format:
[
    {
        "task_id": 1,
        "task_name": "Install CMU Block Walls",
        "duration_days": 30,
        "start_date": "2024-01-01",
        "finish_date": "2024-01-31"
    }
]

Extract all tasks found in the document. Return only valid JSON, no additional text.
""")

# Prompt for extracting cost items from construction planning document
COST_ITEM_EXTRACTION_PROMPT = Template("""
You are an expert data extraction agent specializing in construction cost analysis.

Extract all cost items from the following document text. Each cost item should have:
- item_name: Description of the cost item
- quantity: Numeric quantity (extract the number, handle units like 't', 'm3', etc.)
- unit_price_yen: Unit price in Japanese Yen
- total_cost_yen: Total cost in Japanese Yen (calculate if not directly provided)
- cost_type: Either "Foreign cost" or "Local cost" (case-sensitive)

Document Text:
{{ document_text }}

Return the extracted cost items as a JSON array. Each item should be a JSON object with the exact fields specified above.
Extract numeric values accurately. If total_cost_yen is not provided, calculate it as quantity * unit_price_yen.

Example output format:
[
    {
        "item_name": "Bearing Pile",
        "quantity": 736.2,
        "unit_price_yen": 79000,
        "total_cost_yen": 58159800,
        "cost_type": "Foreign cost"
    }
]

Extract all cost items found in the document. Return only valid JSON, no additional text.
""")

# Prompt for extracting regulatory rules from URA circular
REGULATORY_RULE_EXTRACTION_PROMPT = Template("""
You are an expert data extraction agent specializing in regulatory documents.

Extract all regulatory rules and clarifications from the following URA circular document text. Each rule should have:
- rule_id: A unique identifier (e.g., Q1, Q2, Q17, or extract from question numbers)
- rule_summary: A concise summary of the rule or clarification
- measurement_basis: Key measurement principle and associated rule (e.g., "middle of the external wall", "edge of the covered area")

Document Text:
{{ document_text }}

Return the extracted rules as a JSON array. Each rule should be a JSON object with the exact fields specified above.

Example output format:
[
    {
        "rule_id": "Q1",
        "rule_summary": "Definition of GFA calculation method",
        "measurement_basis": "middle of the external wall"
    }
]

Extract all rules and clarifications found in the document. Return only valid JSON, no additional text.
""")

# Prompt for semantic search query understanding
QUERY_UNDERSTANDING_PROMPT = Template("""
You are a helpful assistant that understands queries about real estate and construction documents.

User Query: {{ user_query }}

Analyze this query and determine:
1. What type of information is the user looking for?
2. Which document(s) might contain this information?
3. What are the key terms and concepts?

Provide a brief analysis to help with semantic search.
""")

# Prompt for generating answers from retrieved context
ANSWER_GENERATION_PROMPT = Template("""
You are a helpful assistant answering questions about real estate and construction documents.

User Query: {{ user_query }}

Relevant Context from Documents:
{{ context }}

Based on the provided context, provide a clear and accurate answer to the user's query.
If the context doesn't contain enough information, say so.
Cite specific details from the context when possible.

Answer:
""")

def get_prompt(template: Template, **kwargs) -> str:
    """
    Render a Jinja2 prompt template
    
    Args:
        template: Jinja2 Template object
        **kwargs: Variables to render in the template
        
    Returns:
        Rendered prompt string
    """
    return template.render(**kwargs)

__all__ = [
    "PROJECT_TASK_EXTRACTION_PROMPT",
    "COST_ITEM_EXTRACTION_PROMPT",
    "REGULATORY_RULE_EXTRACTION_PROMPT",
    "QUERY_UNDERSTANDING_PROMPT",
    "ANSWER_GENERATION_PROMPT",
    "get_prompt"
]

