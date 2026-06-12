from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class MetadataResponse(BaseModel):
    id: int
    manuscript_id: int
    title_suggestions: Optional[List[str]]
    subtitle: Optional[str]
    description: Optional[str]
    keywords: Optional[List[str]]
    bisac_categories: Optional[List[str]]
    author_bio_prompt: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
