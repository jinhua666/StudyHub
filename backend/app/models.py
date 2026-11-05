from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Table, UniqueConstraint
from .database import Base

def now(): return datetime.now(timezone.utc)
note_tags = Table('note_tags', Base.metadata, Column('note_id', ForeignKey('notes.id', ondelete='CASCADE'), primary_key=True), Column('tag_id', ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True))
class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), index=True)
    sort_order = Column(Integer, nullable=False, default=0)
    is_system = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=now)
    updated_at = Column(DateTime(timezone=True), default=now, onupdate=now)
class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    summary = Column(Text, default='')
    content_md = Column(Text, default='')
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, index=True)
    status = Column(String(30), default='not_started', index=True)
    difficulty = Column(String(30), default='beginner')
    is_favorite = Column(Boolean, default=False, index=True)
    source_url = Column(Text, default='')
    created_at = Column(DateTime(timezone=True), default=now)
    updated_at = Column(DateTime(timezone=True), default=now, onupdate=now)
    last_viewed_at = Column(DateTime(timezone=True), nullable=True, index=True)
class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
class Attachment(Base):
    __tablename__ = 'attachments'
    id = Column(Integer, primary_key=True)
    note_id = Column(Integer, ForeignKey('notes.id', ondelete='CASCADE'), nullable=False, index=True)
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), unique=True, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now)
