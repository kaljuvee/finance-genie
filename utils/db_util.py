"""Database utility module for PostgreSQL operations with SQLAlchemy."""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()

# Database connection
DB_URL = os.getenv("PGVECTOR_CONNECTION", "").replace(", schema:", "?options=-c%20search_path%3D")
if not DB_URL:
    raise ValueError("PGVECTOR_CONNECTION environment variable not set")

# Ensure schema is genie
if "search_path" not in DB_URL:
    DB_URL += "?options=-c%20search_path%3Dgenie"

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class TradingRun(Base):
    """Model for trading runs."""
    __tablename__ = "trading_runs"
    __table_args__ = {"schema": "genie"}

    id = Column(Integer, primary_key=True)
    run_id = Column(String(255), unique=True, nullable=False)
    symbol = Column(String(10), nullable=False)
    youtube_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    decisions = relationship("TradingDecision", back_populates="run")
    performance = relationship("PerformanceMetric", back_populates="run")


class TradingDecision(Base):
    """Model for trading decisions."""
    __tablename__ = "trading_decisions"
    __table_args__ = {"schema": "genie"}

    id = Column(Integer, primary_key=True)
    run_id = Column(String(255), ForeignKey("genie.trading_runs.run_id"), nullable=False)
    symbol = Column(String(10), nullable=False)
    median_return = Column(Float)
    q25_return = Column(Float)
    q75_return = Column(Float)
    action = Column(String(10))
    raw_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("TradingRun", back_populates="decisions")


class PerformanceMetric(Base):
    """Model for performance metrics."""
    __tablename__ = "performance_metrics"
    __table_args__ = {"schema": "genie"}

    id = Column(Integer, primary_key=True)
    run_id = Column(String(255), ForeignKey("genie.trading_runs.run_id"), nullable=False)
    symbol = Column(String(10), nullable=False)
    predicted_action = Column(String(10))
    actual_return = Column(Float)
    predicted_median = Column(Float)
    predicted_q25 = Column(Float)
    predicted_q75 = Column(Float)
    accuracy_flag = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("TradingRun", back_populates="performance")


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def get_session():
    """Get a database session."""
    return SessionLocal()


def store_trading_run(run_id: str, symbol: str, youtube_url: str = None):
    """Store a trading run."""
    session = get_session()
    try:
        run = TradingRun(run_id=run_id, symbol=symbol, youtube_url=youtube_url)
        session.add(run)
        session.commit()
        return run
    except Exception as e:
        session.rollback()
        print(f"Error storing trading run: {e}")
        return None
    finally:
        session.close()


def store_trading_decision(run_id: str, symbol: str, median: float, q25: float, q75: float, action: str, raw_response: str):
    """Store a trading decision."""
    session = get_session()
    try:
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
        session.commit()
        return decision
    except Exception as e:
        session.rollback()
        print(f"Error storing trading decision: {e}")
        return None
    finally:
        session.close()


def get_trading_runs(limit: int = 50):
    """Get recent trading runs."""
    session = get_session()
    try:
        runs = session.query(TradingRun).order_by(TradingRun.created_at.desc()).limit(limit).all()
        return runs
    finally:
        session.close()


def get_trading_run_details(run_id: str):
    """Get details for a specific trading run."""
    session = get_session()
    try:
        run = session.query(TradingRun).filter(TradingRun.run_id == run_id).first()
        return run
    finally:
        session.close()


def get_performance_summary(symbol: str = None):
    """Get performance summary."""
    session = get_session()
    try:
        query = session.query(PerformanceMetric)
        if symbol:
            query = query.filter(PerformanceMetric.symbol == symbol)
        metrics = query.all()
        return metrics
    finally:
        session.close()
