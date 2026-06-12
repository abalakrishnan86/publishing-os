from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from app.database import engine
from app.models.dbmodels import ManuscriptDB, MarketingResultDB
from app.models.marketing import MarketingResponse
from app.services.ai_service import generate_marketing

router = APIRouter(prefix="/manuscripts", tags=["marketing"])


def _serialize(db: MarketingResultDB) -> MarketingResponse:
    return MarketingResponse(
        id=db.id,
        manuscript_id=db.manuscript_id,
        back_cover_blurb=db.back_cover_blurb,
        amazon_description=db.amazon_description,
        twitter_post=db.twitter_post,
        linkedin_post=db.linkedin_post,
        instagram_post=db.instagram_post,
        press_release_excerpt=db.press_release_excerpt,
        elevator_pitch=db.elevator_pitch,
        created_at=db.created_at,
    )


@router.post("/{manuscript_id}/marketing", response_model=MarketingResponse)
def run_marketing(manuscript_id: int) -> MarketingResponse:
    with Session(engine) as session:
        manuscript = session.get(ManuscriptDB, manuscript_id)
        if not manuscript:
            raise HTTPException(404, "Manuscript not found")
        if not manuscript.raw_text:
            raise HTTPException(400, "Manuscript text not yet extracted. Try again shortly.")

        existing = session.exec(
            select(MarketingResultDB).where(MarketingResultDB.manuscript_id == manuscript_id)
        ).first()
        if existing:
            return _serialize(existing)

        result = generate_marketing(manuscript.raw_text, manuscript.title)

        db = MarketingResultDB(
            manuscript_id=manuscript_id,
            back_cover_blurb=result.get("back_cover_blurb"),
            amazon_description=result.get("amazon_description"),
            twitter_post=result.get("twitter_post"),
            linkedin_post=result.get("linkedin_post"),
            instagram_post=result.get("instagram_post"),
            press_release_excerpt=result.get("press_release_excerpt"),
            elevator_pitch=result.get("elevator_pitch"),
        )
        session.add(db)
        session.commit()
        session.refresh(db)
        return _serialize(db)


@router.get("/{manuscript_id}/marketing", response_model=MarketingResponse)
def get_marketing(manuscript_id: int) -> MarketingResponse:
    with Session(engine) as session:
        db = session.exec(
            select(MarketingResultDB).where(MarketingResultDB.manuscript_id == manuscript_id)
        ).first()
        if not db:
            raise HTTPException(404, "Marketing content not yet generated")
        return _serialize(db)
