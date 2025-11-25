"""
Database utility module for PostgreSQL operations with SQLAlchemy.
Centralizes all database connections and operations.
"""

import os
import logging
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy.exc import OperationalError, ArgumentError

from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# ============ Configuration ============
DB_URL = os.getenv("PGVECTOR_CONNECTION", "").strip()
DB_SCHEMA = os.getenv("DB_SCHEMA", "genie")

# Validate database URL
if not DB_URL:
    logger.warning("PGVECTOR_CONNECTION not set. Database operations will be unavailable.")
    DB_URL = None
    DB_AVAILABLE = False
else:
    DB_AVAILABLE = True

# Database Base for ORM models
Base = declarative_base()

# Global session factory
_SessionLocal = None
_engine = None


def get_engine():
    """Get or create the SQLAlchemy engine."""
    global _engine
    
    if _engine is not None:
        return _engine
    
    if not DB_URL:
        raise RuntimeError("Database URL not configured. Set PGVECTOR_CONNECTION in .env")
    
    try:
        # Create engine with connection pooling
        _engine = create_engine(
            DB_URL,
            echo=False,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
        )
        
        logger.info("Database engine created successfully")
        return _engine
    
    except (ArgumentError, OperationalError) as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


def get_session_factory():
    """Get or create the SQLAlchemy session factory."""
    global _SessionLocal
    
    if _SessionLocal is not None:
        return _SessionLocal
    
    try:
        engine = get_engine()
        _SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
        logger.info("Session factory created successfully")
        return _SessionLocal
    
    except Exception as e:
        logger.error(f"Failed to create session factory: {e}")
        raise


@contextmanager
def get_session() -> Session:
    """
    Context manager for database sessions.
    Ensures proper cleanup and error handling.
    
    Usage:
        with get_session() as session:
            # perform operations
    """
    if not DB_AVAILABLE:
        raise RuntimeError("Database not available. Configure PGVECTOR_CONNECTION in .env")
    
    session = None
    try:
        SessionLocal = get_session_factory()
        session = SessionLocal()
        yield session
        session.commit()
    
    except Exception as e:
        if session:
            session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    
    finally:
        if session:
            session.close()


def init_db():
    """Initialize database tables."""
    if not DB_AVAILABLE:
        logger.warning("Database not available. Skipping initialization.")
        return False
    
    try:
        engine = get_engine()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False


# ============ ORM Models ============

class TradingRun(Base):
    """Model for trading runs."""
    __tablename__ = "trading_runs"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(Integer, primary_key=True)
    run_id = Column(String(255), unique=True, nullable=False, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    youtube_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    decisions = relationship("TradingDecision", back_populates="run", cascade="all, delete-orphan")
    performance = relationship("PerformanceMetric", back_populates="run", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TradingRun(run_id={self.run_id}, symbol={self.symbol})>"


class TradingDecision(Base):
    """Model for trading decisions."""
    __tablename__ = "trading_decisions"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(Integer, primary_key=True)
    run_id = Column(String(255), ForeignKey(f"{DB_SCHEMA}.trading_runs.run_id"), nullable=False, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    median_return = Column(Float)
    q25_return = Column(Float)
    q75_return = Column(Float)
    action = Column(String(10))  # BUY, SELL, HOLD
    raw_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    run = relationship("TradingRun", back_populates="decisions")

    def __repr__(self):
        return f"<TradingDecision(symbol={self.symbol}, action={self.action}, median={self.median_return})>"


class PerformanceMetric(Base):
    """Model for performance metrics."""
    __tablename__ = "performance_metrics"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(Integer, primary_key=True)
    run_id = Column(String(255), ForeignKey(f"{DB_SCHEMA}.trading_runs.run_id"), nullable=False, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    predicted_action = Column(String(10))
    actual_return = Column(Float)
    predicted_median = Column(Float)
    predicted_q25 = Column(Float)
    predicted_q75 = Column(Float)
    accuracy_flag = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    run = relationship("TradingRun", back_populates="performance")

    def __repr__(self):
        return f"<PerformanceMetric(symbol={self.symbol}, accuracy={self.accuracy_flag})>"


# ============ CRUD Operations ============

def store_trading_run(run_id: str, symbol: str, youtube_url: Optional[str] = None) -> Optional[TradingRun]:
    """Store a new trading run."""
    if not DB_AVAILABLE:
        logger.warning("Database not available. Trading run not stored.")
        return None
    
    try:
        with get_session() as session:
            run = TradingRun(run_id=run_id, symbol=symbol, youtube_url=youtube_url)
            session.add(run)
            session.flush()
            logger.info(f"Trading run stored: {run_id}")
            return run
    
    except Exception as e:
        logger.error(f"Error storing trading run: {e}")
        return None


def store_trading_decision(
    run_id: str,
    symbol: str,
    median: Optional[float] = None,
    q25: Optional[float] = None,
    q75: Optional[float] = None,
    action: Optional[str] = None,
    raw_response: Optional[str] = None
) -> Optional[TradingDecision]:
    """Store a trading decision."""
    if not DB_AVAILABLE:
        logger.warning("Database not available. Trading decision not stored.")
        return None
    
    try:
        with get_session() as session:
            decision = TradingDecision(
                run_id=run_id,
                symbol=symbol,
                median_return=median,
                q25_return=q25,
                q75_return=q75,
                action=action,
                raw_response=raw_response
            )
            session.add(decision)
            session.flush()
            logger.info(f"Trading decision stored for {symbol}: {action}")
            return decision
    
    except Exception as e:
        logger.error(f"Error storing trading decision: {e}")
        return None


def store_performance_metric(
    run_id: str,
    symbol: str,
    predicted_action: Optional[str] = None,
    actual_return: Optional[float] = None,
    predicted_median: Optional[float] = None,
    predicted_q25: Optional[float] = None,
    predicted_q75: Optional[float] = None,
    accuracy_flag: Optional[bool] = None
) -> Optional[PerformanceMetric]:
    """Store a performance metric."""
    if not DB_AVAILABLE:
        logger.warning("Database not available. Performance metric not stored.")
        return None
    
    try:
        with get_session() as session:
            metric = PerformanceMetric(
                run_id=run_id,
                symbol=symbol,
                predicted_action=predicted_action,
                actual_return=actual_return,
                predicted_median=predicted_median,
                predicted_q25=predicted_q25,
                predicted_q75=predicted_q75,
                accuracy_flag=accuracy_flag
            )
            session.add(metric)
            session.flush()
            logger.info(f"Performance metric stored for {symbol}")
            return metric
    
    except Exception as e:
        logger.error(f"Error storing performance metric: {e}")
        return None


def get_trading_runs(limit: int = 50, symbol: Optional[str] = None) -> List[TradingRun]:
    """Get recent trading runs."""
    if not DB_AVAILABLE:
        logger.warning("Database not available. Returning empty list.")
        return []
    
    try:
        with get_session() as session:
            query = session.query(TradingRun).order_by(TradingRun.created_at.desc())
            
            if symbol:
                query = query.filter(TradingRun.symbol == symbol)
            
            runs = query.limit(limit).all()
            logger.info(f"Retrieved {len(runs)} trading runs")
            return runs
    
    except Exception as e:
        logger.error(f"Error retrieving trading runs: {e}")
        return []


def get_trading_run_details(run_id: str) -> Optional[TradingRun]:
    """Get details for a specific trading run."""
    if not DB_AVAILABLE:
        logger.warning("Database not available.")
        return None
    
    try:
        with get_session() as session:
            run = session.query(TradingRun).filter(TradingRun.run_id == run_id).first()
            logger.info(f"Retrieved trading run: {run_id}")
            return run
    
    except Exception as e:
        logger.error(f"Error retrieving trading run details: {e}")
        return None


def get_performance_summary(symbol: Optional[str] = None) -> List[PerformanceMetric]:
    """Get performance summary."""
    if not DB_AVAILABLE:
        logger.warning("Database not available. Returning empty list.")
        return []
    
    try:
        with get_session() as session:
            query = session.query(PerformanceMetric)
            
            if symbol:
                query = query.filter(PerformanceMetric.symbol == symbol)
            
            metrics = query.order_by(PerformanceMetric.created_at.desc()).all()
            logger.info(f"Retrieved {len(metrics)} performance metrics")
            return metrics
    
    except Exception as e:
        logger.error(f"Error retrieving performance summary: {e}")
        return []


def get_trading_decisions(run_id: Optional[str] = None, symbol: Optional[str] = None) -> List[TradingDecision]:
    """Get trading decisions."""
    if not DB_AVAILABLE:
        logger.warning("Database not available. Returning empty list.")
        return []
    
    try:
        with get_session() as session:
            query = session.query(TradingDecision)
            
            if run_id:
                query = query.filter(TradingDecision.run_id == run_id)
            
            if symbol:
                query = query.filter(TradingDecision.symbol == symbol)
            
            decisions = query.order_by(TradingDecision.created_at.desc()).all()
            logger.info(f"Retrieved {len(decisions)} trading decisions")
            return decisions
    
    except Exception as e:
        logger.error(f"Error retrieving trading decisions: {e}")
        return []


def get_db_stats() -> Dict[str, Any]:
    """Get database statistics."""
    if not DB_AVAILABLE:
        return {"available": False, "error": "Database not configured"}
    
    try:
        with get_session() as session:
            try:
                total_runs = session.query(TradingRun).count()
                total_decisions = session.query(TradingDecision).count()
                total_metrics = session.query(PerformanceMetric).count()
                
                return {
                    "available": True,
                    "total_runs": total_runs,
                    "total_decisions": total_decisions,
                    "total_metrics": total_metrics,
                    "schema": DB_SCHEMA
                }
            except Exception as table_error:
                if "does not exist" in str(table_error):
                    return {
                        "available": True,
                        "total_runs": 0,
                        "total_decisions": 0,
                        "total_metrics": 0,
                        "schema": DB_SCHEMA,
                        "note": "Tables not initialized"
                    }
                raise
    
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {"available": False, "error": str(e)}


# ============ Cleanup ============

def close_db():
    """Close database connections."""
    global _engine, _SessionLocal
    
    if _engine:
        _engine.dispose()
        _engine = None
    
    _SessionLocal = None
    logger.info("Database connections closed")
