"""
Database Initialization Module
Creates SQLite database with 7 days of hourly mock inflow data
"""

import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "arogya_setu.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


class PatientInflow(Base):
    """Model for patient inflow records"""
    __tablename__ = "patient_inflow"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_id = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    count = Column(Integer, nullable=False)
    severity_avg = Column(Float, nullable=True)
    department = Column(String(50), nullable=True)


HOSPITAL_IDS = ["H001", "H002", "H003", "H004", "H005", "H006", "H007", "H008"]
DEPARTMENTS = ["Emergency", "General", "ICU", "Pediatrics", "Cardiology", "Orthopedics"]


def generate_mock_inflow():
    """Generate 7 days of hourly mock inflow data"""
    records = []
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    current_time = start_time
    
    while current_time <= end_time:
        hour = current_time.hour
        is_weekend = current_time.weekday() >= 5
        
        if 8 <= hour <= 20:
            base_inflow = random.randint(8, 20)
        elif 6 <= hour <= 8 or 20 <= hour <= 23:
            base_inflow = random.randint(5, 12)
        else:
            base_inflow = random.randint(2, 6)
        
        if is_weekend:
            base_inflow = int(base_inflow * 0.85)
        
        for hospital_id in HOSPITAL_IDS:
            hospital_factor = 1.0 + (hash(hospital_id) % 30) / 100
            count = int(base_inflow * hospital_factor * random.uniform(0.8, 1.2))
            
            severity = random.uniform(1.5, 4.0)
            department = random.choice(DEPARTMENTS)
            
            records.append(PatientInflow(
                hospital_id=hospital_id,
                timestamp=current_time,
                count=max(1, count),
                severity_avg=round(severity, 2),
                department=department
            ))
        
        current_time += timedelta(hours=1)
    
    return records


def init_database():
    """Initialize the database with mock data if not exists"""
    Base.metadata.create_all(engine)
    
    session = SessionLocal()
    try:
        existing_count = session.query(PatientInflow).count()
        
        if existing_count == 0:
            print("Initializing database with mock inflow data...")
            records = generate_mock_inflow()
            session.bulk_save_objects(records)
            session.commit()
            print(f"Created {len(records)} inflow records")
        else:
            print(f"Database already contains {existing_count} records")
    except Exception as e:
        session.rollback()
        print(f"Database error: {e}")
    finally:
        session.close()


def get_history(limit: int = 200) -> list:
    """Retrieve the last N inflow records"""
    session = SessionLocal()
    try:
        records = session.query(PatientInflow)\
            .order_by(PatientInflow.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return [
            {
                "id": r.id,
                "hospital_id": r.hospital_id,
                "timestamp": r.timestamp.isoformat(),
                "count": r.count,
                "severity_avg": r.severity_avg,
                "department": r.department
            }
            for r in records
        ]
    finally:
        session.close()


def get_hospital_history(hospital_id: str, hours: int = 24) -> list:
    """Get inflow history for a specific hospital"""
    session = SessionLocal()
    try:
        cutoff = datetime.now() - timedelta(hours=hours)
        records = session.query(PatientInflow)\
            .filter(PatientInflow.hospital_id == hospital_id)\
            .filter(PatientInflow.timestamp >= cutoff)\
            .order_by(PatientInflow.timestamp.desc())\
            .all()
        
        return [
            {
                "id": r.id,
                "hospital_id": r.hospital_id,
                "timestamp": r.timestamp.isoformat(),
                "count": r.count,
                "severity_avg": r.severity_avg,
                "department": r.department
            }
            for r in records
        ]
    finally:
        session.close()
