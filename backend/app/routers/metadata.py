import json

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from app.database import engine
from app.models.dbmodels import ManuscriptDB, MetadataResultDB
from app.models.metadata import MetadataResponse
from app.services.ai_service import generate_metadata

router = APIRouter(prefix="/manuscripts", tags=["metadata"])


def _serialize(db: MetadataResultDB) -> MetadataResponse:
    return MetadataResponse(
        id=db.id,
        manuscript_id=db.manuscript_id,
        title_suggestions=json.loads(db.title_suggestions) if db.title_suggestions else None,
        subtitle=db.subtitle,
        description=db.description,
        keywords=json.loads(db.keywords) if db.keywords else None,
        bisac_categories=json.loads(db.bisac_categories) if db.bisac_categories else None,
        author_bio_prompt=db.author_bio_prompt,
        created_at=db.created_at,
    )


@router.post("/{manuscript_id}/metadata", response_model=MetadataResponse)
def run_metadata(manuscript_id: int) -> MetadataResponse:
    with Session(engine) as session:
        manuscript = session.get(ManuscriptDB, manuscript_id)
        if not manuscript:
            raise HTTPException(404, "Manuscript not found")
        if not manuscript.raw_text:
            raise HTTPException(400, "Manuscript text not yet extracted. Try again shortly.")

        existing = session.exec(
            select(MetadataResultDB).where(MetadataResultDB.manuscript_id == manuscript_id)
        ).first()
        if existing:
            return _serialize(existing)

        result = generate_metadata(manuscript.raw_text)

        db = MetadataResultDB(
            manuscript_id=manuscript_id,
            title_suggestions=json.dumps(result.get("title_suggestions", [])),
            subtitle=result.get("subtitle"),
            description=result.get("description"),
            keywords=json.dumps(result.get("keywords", [])),
            bisac_categories=json.dumps(result.get("bisac_categories", [])),
            author_bio_prompt=result.get("author_bio_prompt"),
        )
        session.add(db)
        session.commit()
        session.refresh(db)
        return _serialize(db)


@router.get("/{manuscript_id}/metadata", response_model=MetadataResponse)
def get_metadata(manuscript_id: int) -> MetadataResponse:
    with Session(engine) as session:
        db = session.exec(
            select(MetadataResultDB).where(MetadataResultDB.manuscript_id == manuscript_id)
        ).first()
        if not db:
            raise HTTPException(404, "Metadata not yet generated")
        return _serialize(db)
