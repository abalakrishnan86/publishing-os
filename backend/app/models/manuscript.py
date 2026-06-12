from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ManuscriptResponse(BaseModel):
    id: int
    title: str
    filename: str
    file_type: str
    status: str
    word_count: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
