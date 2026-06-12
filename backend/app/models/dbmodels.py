from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class FileType(str, Enum):
    DOCX = "docx"
    PDF = "pdf"
    TXT = "txt"


class ManuscriptStatus(str, Enum):
    UPLOADED = "uploaded"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    FAILED = "failed"


class ManuscriptDB(SQLModel, table=True):
    __tablename__ = "manuscripts"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    filename: str
    filepath: str
    file_type: FileType
    status: ManuscriptStatus = Field(default=ManuscriptStatus.UPLOADED)
    word_count: Optional[int] = Field(default=None)
    raw_text: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AnalysisResultDB(SQLModel, table=True):
    __tablename__ = "analysis_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    manuscript_id: int = Field(foreign_key="manuscripts.id", index=True)
    genre: Optional[str] = Field(default=None)
    themes: Optional[str] = Field(default=None)
    writing_style: Optional[str] = Field(default=None)
    target_audience: Optional[str] = Field(default=None)
    readability_score: Optional[str] = Field(default=None)
    strengths: Optional[str] = Field(default=None)
    weaknesses: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MetadataResultDB(SQLModel, table=True):
    __tablename__ = "metadata_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    manuscript_id: int = Field(foreign_key="manuscripts.id", index=True)
    title_suggestions: Optional[str] = Field(default=None)
    subtitle: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    keywords: Optional[str] = Field(default=None)
    bisac_categories: Optional[str] = Field(default=None)
    author_bio_prompt: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MarketingResultDB(SQLModel, table=True):
    __tablename__ = "marketing_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    manuscript_id: int = Field(foreign_key="manuscripts.id", index=True)
    back_cover_blurb: Optional[str] = Field(default=None)
    amazon_description: Optional[str] = Field(default=None)
    twitter_post: Optional[str] = Field(default=None)
    linkedin_post: Optional[str] = Field(default=None)
    instagram_post: Optional[str] = Field(default=None)
    press_release_excerpt: Optional[str] = Field(default=None)
    elevator_pitch: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
