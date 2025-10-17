"""Database models for storage service"""

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Report(Base):
    """Report model - stores medical report metadata and file paths"""

    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, default="processing")  # processing, completed, failed

    # File paths
    original_image_path = Column(String, nullable=True)
    segmentation_mask_path = Column(String, nullable=True)

    # Analysis results (stored as JSON string)
    analysis_results = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "status": self.status,
            "original_image_path": self.original_image_path,
            "segmentation_mask_path": self.segmentation_mask_path,
            "analysis_results": self.analysis_results,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
