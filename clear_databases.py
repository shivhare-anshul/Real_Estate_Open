#!/usr/bin/env python3
"""
Script to clear PostgreSQL and ChromaDB data
Use this before demonstrations to start with a clean slate
"""

import sys
from pathlib import Path
from utils.logger import logger
from database.postgres_client import PostgreSQLClient
from database.chroma_client import ChromaDBClient

def kill_previous_servers():
    """Kill any running Django or Prefect servers"""
    import subprocess
    import os
    
    logger.info("🔍 Checking for running servers...")
    
    # Kill Django servers on port 8000
    try:
        result = subprocess.run(
            ["lsof", "-ti:8000"],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), 15)  # SIGTERM
                    logger.info(f"✅ Killed Django server (PID: {pid})")
                except:
                    pass
        else:
            logger.info("ℹ️ No Django server running on port 8000")
    except Exception as e:
        logger.warning(f"⚠️ Could not check for Django servers: {e}")
    
    # Kill any manage.py runserver processes
    try:
        result = subprocess.run(
            ["pkill", "-f", "manage.py runserver"],
            capture_output=True,
            stderr=subprocess.DEVNULL
        )
        logger.info("✅ Killed any remaining Django server processes")
    except:
        pass
    
    # Kill Prefect servers (if any)
    try:
        result = subprocess.run(
            ["pkill", "-f", "prefect"],
            capture_output=True,
            stderr=subprocess.DEVNULL
        )
        logger.info("✅ Killed any Prefect server processes")
    except:
        pass

def clear_postgresql():
    """Clear all data from PostgreSQL"""
    try:
        logger.info("🗑️  Clearing PostgreSQL data...")
        client = PostgreSQLClient()
        result = client.clear_all_data()
        logger.info(f"✅ PostgreSQL cleared: {result['tasks_deleted']} tasks, {result['items_deleted']} items, {result['rules_deleted']} rules")
        return True
    except Exception as e:
        logger.error(f"❌ Error clearing PostgreSQL: {e}")
        return False

def clear_chromadb():
    """Clear all data from ChromaDB"""
    try:
        logger.info("🗑️  Clearing ChromaDB data...")
        client = ChromaDBClient()
        result = client.clear_all_data()
        logger.info(f"✅ ChromaDB cleared: {result['chunks_deleted']} chunks deleted")
        return True
    except Exception as e:
        logger.error(f"❌ Error clearing ChromaDB: {e}")
        return False

def main():
    """Main function"""
    print("\n" + "="*80)
    print("  CLEAR DATABASES - Reset PostgreSQL and ChromaDB")
    print("="*80)
    print()
    
    # Confirm action
    response = input("⚠️  This will delete ALL data from PostgreSQL and ChromaDB. Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Operation cancelled")
        return 1
    
    print()
    
    # Kill previous servers
    kill_previous_servers()
    print()
    
    # Clear databases
    postgres_ok = clear_postgresql()
    print()
    chroma_ok = clear_chromadb()
    print()
    
    # Summary
    print("="*80)
    if postgres_ok and chroma_ok:
        print("✅ All databases cleared successfully!")
        print("="*80)
        return 0
    else:
        print("⚠️  Some errors occurred during clearing")
        print("="*80)
        return 1

if __name__ == "__main__":
    sys.exit(main())

