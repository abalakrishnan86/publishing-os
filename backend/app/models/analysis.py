from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    id: int
    manuscript_id: int
    genre: Optional[str]
    themes: Optional[List[str]]
    writing_style: Optional[str]
    target_audience: Optional[str]
    readability_score: Optional[str]
    strengths: Optional[List[str]]
    weaknesses: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True
