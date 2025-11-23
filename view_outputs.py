#!/usr/bin/env python3
"""
View Outputs Script
Shows PostgreSQL and ChromaDB data in a readable format
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database.postgres_client import PostgreSQLClient
from database.chroma_client import ChromaDBClient
import json

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def view_postgresql_data():
    """View PostgreSQL data"""
    print_section("PostgreSQL Data")
    
    try:
        client = PostgreSQLClient()
        
        # Project Tasks
        print("\n📋 PROJECT TASKS:")
        print("-" * 80)
        tasks = client.query_project_tasks(limit=20)
        if tasks:
            print(f"Found {len(tasks)} tasks:\n")
            for i, task in enumerate(tasks, 1):
                print(f"{i}. Task ID: {task.get('task_id', 'N/A')}")
                print(f"   Name: {task.get('task_name', 'N/A')}")
                print(f"   Duration: {task.get('duration_days', 'N/A')} days")
                print(f"   Start: {task.get('start_date', 'N/A')} → Finish: {task.get('finish_date', 'N/A')}")
                print()
        else:
            print("❌ No project tasks found in database")
        
        # Cost Items
        print("\n💰 COST ITEMS:")
        print("-" * 80)
        items = client.query_cost_items(limit=20)
        if items:
            print(f"Found {len(items)} cost items:\n")
            for i, item in enumerate(items, 1):
                print(f"{i}. Item: {item.get('item_name', 'N/A')}")
                print(f"   Quantity: {item.get('quantity', 'N/A')}")
                print(f"   Unit Price: {item.get('unit_price_yen', 'N/A'):,.0f} Yen")
                print(f"   Total Cost: {item.get('total_cost_yen', 'N/A'):,.0f} Yen")
                print(f"   Type: {item.get('cost_type', 'N/A')}")
                print()
        else:
            print("❌ No cost items found in database")
        
        # Regulatory Rules
        print("\n📜 REGULATORY RULES:")
        print("-" * 80)
        try:
            rules = client.query_regulatory_rules(limit=20)
            if rules:
                print(f"Found {len(rules)} regulatory rules:\n")
                for i, rule in enumerate(rules, 1):
                    print(f"{i}. Rule ID: {rule.get('rule_id', 'N/A')}")
                    print(f"   Summary: {rule.get('rule_summary', 'N/A')[:100]}...")
                    print(f"   Measurement Basis: {rule.get('measurement_basis', 'N/A')[:80]}...")
                    print()
            else:
                print("❌ No regulatory rules found in database")
        except AttributeError:
            print("⚠️  Regulatory rules query not available (method not implemented)")
            
    except Exception as e:
        print(f"❌ Error accessing PostgreSQL: {e}")

def view_chromadb_data():
    """View ChromaDB data"""
    print_section("ChromaDB Data")
    
    try:
        client = ChromaDBClient()
        
        # Get statistics
        try:
            count = client.collection.count()
            print(f"\n📊 Total Chunks Stored: {count}")
        except:
            print(f"\n📊 ChromaDB Collection: {client.collection_name}")
        
        # Test semantic search
        print("\n🔍 SEMANTIC SEARCH TEST:")
        print("-" * 80)
        
        test_queries = [
            "What are the project tasks?",
            "What are the cost items?",
            "What are the regulatory rules?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            print("-" * 80)
            results = client.search(query, n_results=3)
            
            if results:
                for i, result in enumerate(results, 1):
                    metadata = result.get('metadata', {})
                    doc_name = metadata.get('document_name', 'Unknown')
                    distance = result.get('distance', 0)
                    relevance = (1 - distance) * 100
                    text = result.get('document', '')[:150] if 'document' in result else result.get('chunk_text', '')[:150]
                    
                    print(f"\n  {i}. Document: {doc_name}")
                    print(f"     Relevance: {relevance:.1f}%")
                    print(f"     Text: {text}...")
            else:
                print("  ❌ No results found")
                
    except Exception as e:
        print(f"❌ Error accessing ChromaDB: {e}")

def main():
    """Main function"""
    print("\n" + "="*80)
    print("  REAL ESTATE PIPELINE - DATA VIEWER")
    print("="*80)
    
    # View PostgreSQL data
    view_postgresql_data()
    
    # View ChromaDB data
    view_chromadb_data()
    
    print("\n" + "="*80)
    print("  ✅ Data viewing complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

