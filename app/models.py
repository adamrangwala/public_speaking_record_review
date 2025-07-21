from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    original_name = Column(String)
    file_size = Column(Integer)
    duration = Column(Float, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="uploaded")  # uploaded, processing, completed, error
    
    # Relationship with notes
    notes = relationship("Note", back_populates="video", cascade="all, delete-orphan")

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    view_type = Column(String)  # video, audio, text
    prompt_id = Column(Integer, ForeignKey("prompts.id"))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    video = relationship("Video", back_populates="notes")
    prompt = relationship("Prompt", back_populates="notes")

class Prompt(Base):
    __tablename__ = "prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    view_type = Column(String)  # video, audio, text
    question_text = Column(Text)
    order_index = Column(Integer)
    active = Column(Boolean, default=True)
    
    # Relationship with notes
    notes = relationship("Note", back_populates="prompt")