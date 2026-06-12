from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MarketingResponse(BaseModel):
    id: int
    manuscript_id: int
    back_cover_blurb: Optional[str]
    amazon_description: Optional[str]
    twitter_post: Optional[str]
    linkedin_post: Optional[str]
    instagram_post: Optional[str]
    press_release_excerpt: Optional[str]
    elevator_pitch: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
