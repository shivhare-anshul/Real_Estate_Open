"""
PostgreSQL database client and operations
"""

import asyncio
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Date, Numeric, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from utils.logger import logger
from utils.profiler import time_function
from config.settings import settings
from database.models import ProjectTask, CostItem, RegulatoryRule

Base = declarative_base()

# SQLAlchemy Models
class ProjectTaskModel(Base):
    __tablename__ = 'project_tasks'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, unique=True, nullable=False)
    task_name = Column(String(500), nullable=False)
    duration_days = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    finish_date = Column(Date, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class CostItemModel(Base):
    __tablename__ = 'cost_items'
    
    id = Column(Integer, primary_key=True)
    item_name = Column(String(500), nullable=False)
    quantity = Column(Numeric(15, 2), nullable=False)
    unit_price_yen = Column(Numeric(15, 2), nullable=False)
    total_cost_yen = Column(Numeric(20, 2), nullable=False)
    cost_type = Column(String(50), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class RegulatoryRuleModel(Base):
    __tablename__ = 'regulatory_rules'
    
    id = Column(Integer, primary_key=True)
    rule_id = Column(String(50), unique=True, nullable=False)
    rule_summary = Column(Text, nullable=False)
    measurement_basis = Column(String(500), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class PostgreSQLClient:
    """PostgreSQL database client"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize PostgreSQL client
        
        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = create_engine(
            self.database_url,
            poolclass=NullPool,
            echo=False
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info("✅ PostgreSQL client initialized")
    
    def create_tables(self):
        """Create all tables if they don't exist"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("✅ Database tables created/verified")
        except Exception as e:
            logger.error(f"❌ Error creating tables: {e}")
            raise
    
    def execute_ddl(self, ddl_file_path: str):
        """
        Execute DDL from file
        
        Args:
            ddl_file_path: Path to DDL SQL file
        """
        try:
            with open(ddl_file_path, 'r') as f:
                ddl_sql = f.read()
            
            with self.engine.connect() as conn:
                conn.execute(text(ddl_sql))
                conn.commit()
            
            logger.info(f"✅ DDL executed from {ddl_file_path}")
        except Exception as e:
            logger.error(f"❌ Error executing DDL: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Database session error: {e}")
            raise
        finally:
            session.close()
    
    @time_function
    def insert_project_tasks(self, tasks: List[ProjectTask]) -> int:
        """
        Insert project tasks into database
        
        Args:
            tasks: List of ProjectTask objects
            
        Returns:
            Number of inserted tasks
        """
        try:
            with self.get_session() as session:
                inserted_count = 0
                for task in tasks:
                    # Use upsert (insert or update)
                    stmt = insert(ProjectTaskModel).values(
                        task_id=task.task_id,
                        task_name=task.task_name,
                        duration_days=task.duration_days,
                        start_date=task.start_date,
                        finish_date=task.finish_date
                    )
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['task_id'],
                        set_=dict(
                            task_name=stmt.excluded.task_name,
                            duration_days=stmt.excluded.duration_days,
                            start_date=stmt.excluded.start_date,
                            finish_date=stmt.excluded.finish_date
                        )
                    )
                    session.execute(stmt)
                    inserted_count += 1
                
                logger.info(f"✅ Inserted {inserted_count} project tasks")
                return inserted_count
        except Exception as e:
            logger.error(f"❌ Error inserting project tasks: {e}")
            raise
    
    @time_function
    def insert_cost_items(self, items: List[CostItem]) -> int:
        """
        Insert cost items into database
        
        Args:
            items: List of CostItem objects
            
        Returns:
            Number of inserted items
        """
        try:
            with self.get_session() as session:
                inserted_count = 0
                for item in items:
                    stmt = insert(CostItemModel).values(
                        item_name=item.item_name,
                        quantity=float(item.quantity),
                        unit_price_yen=float(item.unit_price_yen),
                        total_cost_yen=float(item.total_cost_yen),
                        cost_type=item.cost_type
                    )
                    session.execute(stmt)
                    inserted_count += 1
                
                logger.info(f"✅ Inserted {inserted_count} cost items")
                return inserted_count
        except Exception as e:
            logger.error(f"❌ Error inserting cost items: {e}")
            raise
    
    @time_function
    def insert_regulatory_rules(self, rules: List[RegulatoryRule]) -> int:
        """
        Insert regulatory rules into database
        
        Args:
            rules: List of RegulatoryRule objects
            
        Returns:
            Number of inserted rules
        """
        try:
            with self.get_session() as session:
                inserted_count = 0
                for rule in rules:
                    stmt = insert(RegulatoryRuleModel).values(
                        rule_id=rule.rule_id,
                        rule_summary=rule.rule_summary,
                        measurement_basis=rule.measurement_basis
                    )
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['rule_id'],
                        set_=dict(
                            rule_summary=stmt.excluded.rule_summary,
                            measurement_basis=stmt.excluded.measurement_basis
                        )
                    )
                    session.execute(stmt)
                    inserted_count += 1
                
                logger.info(f"✅ Inserted {inserted_count} regulatory rules")
                return inserted_count
        except Exception as e:
            logger.error(f"❌ Error inserting regulatory rules: {e}")
            raise
    
    def query_project_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Query project tasks from dltHub tables or SQLAlchemy models"""
        try:
            # First try to query from dltHub schema (real_estate_data.project_tasks_resource)
            with self.engine.connect() as conn:
                try:
                    query = text("""
                        SELECT task_id, task_name, duration_days, start_date, finish_date
                        FROM real_estate_data.project_tasks_resource
                        LIMIT :limit
                    """)
                    result = conn.execute(query, {"limit": limit})
                    rows = result.fetchall()
                    if rows:
                        return [
                            {
                                "task_id": row[0],
                                "task_name": row[1],
                                "duration_days": row[2],
                                "start_date": str(row[3]),
                                "finish_date": str(row[4])
                            }
                            for row in rows
                        ]
                except Exception as e:
                    logger.debug(f"dltHub table not found, trying SQLAlchemy models: {e}")
            
            # Fallback to SQLAlchemy models (public.project_tasks)
            with self.get_session() as session:
                results = session.query(ProjectTaskModel).limit(limit).all()
                return [
                    {
                        "task_id": r.task_id,
                        "task_name": r.task_name,
                        "duration_days": r.duration_days,
                        "start_date": str(r.start_date),
                        "finish_date": str(r.finish_date)
                    }
                    for r in results
                ]
        except Exception as e:
            logger.error(f"❌ Error querying project tasks: {e}")
            return []
    
    def query_cost_items(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Query cost items from dltHub tables or SQLAlchemy models"""
        try:
            # First try to query from dltHub schema (real_estate_data.cost_items_resource)
            with self.engine.connect() as conn:
                try:
                    query = text("""
                        SELECT item_name, quantity, unit_price_yen, total_cost_yen, cost_type
                        FROM real_estate_data.cost_items_resource
                        LIMIT :limit
                    """)
                    result = conn.execute(query, {"limit": limit})
                    rows = result.fetchall()
                    if rows:
                        return [
                            {
                                "item_name": row[0],
                                "quantity": float(row[1]),
                                "unit_price_yen": float(row[2]),
                                "total_cost_yen": float(row[3]),
                                "cost_type": row[4]
                            }
                            for row in rows
                        ]
                except Exception as e:
                    logger.debug(f"dltHub table not found, trying SQLAlchemy models: {e}")
            
            # Fallback to SQLAlchemy models (public.cost_items)
            with self.get_session() as session:
                results = session.query(CostItemModel).limit(limit).all()
                return [
                    {
                        "item_name": r.item_name,
                        "quantity": float(r.quantity),
                        "unit_price_yen": float(r.unit_price_yen),
                        "total_cost_yen": float(r.total_cost_yen),
                        "cost_type": r.cost_type
                    }
                    for r in results
                ]
        except Exception as e:
            logger.error(f"❌ Error querying cost items: {e}")
            return []
    
    def clear_all_data(self):
        """
        Clear all data from PostgreSQL tables
        WARNING: This will delete all data from project_tasks, cost_items, and regulatory_rules tables
        """
        try:
            with self.get_session() as session:
                # Delete all records from each table
                deleted_tasks = session.query(ProjectTaskModel).delete()
                deleted_items = session.query(CostItemModel).delete()
                deleted_rules = session.query(RegulatoryRuleModel).delete()
                
                logger.warning(f"⚠️ Cleared PostgreSQL data: {deleted_tasks} tasks, {deleted_items} items, {deleted_rules} rules")
                return {
                    "tasks_deleted": deleted_tasks,
                    "items_deleted": deleted_items,
                    "rules_deleted": deleted_rules
                }
        except Exception as e:
            logger.error(f"❌ Error clearing PostgreSQL data: {e}")
            raise

__all__ = ["PostgreSQLClient", "ProjectTaskModel", "CostItemModel", "RegulatoryRuleModel"]

