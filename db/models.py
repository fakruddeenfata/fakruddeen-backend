from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class SpeechLog(Base):
    __tablename__ = "speech_logs"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class VisionCapture(Base):
    __tablename__ = "vision_captures"
    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SoftwareFile(Base):
    __tablename__ = "software_files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ErrorLog(Base):
    __tablename__ = "error_logs"
    id = Column(Integer, primary_key=True, index=True)
    error_message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
