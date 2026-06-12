import json

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from app.database import engine
from app.models.analysis import AnalysisResponse
from app.models.dbmodels import AnalysisResultDB, ManuscriptDB
from app.services.ai_service import analyze_manuscript

router = APIRouter(prefix="/manuscripts", tags=["analysis"])


def _serialize(db: AnalysisResultDB) -> AnalysisResponse:
    return AnalysisResponse(
        id=db.id,
        manuscript_id=db.manuscript_id,
        genre=db.genre,
        themes=json.loads(db.themes) if db.themes else None,
        writing_style=db.writing_style,
        target_audience=db.target_audience,
        readability_score=db.readability_score,
        strengths=json.loads(db.strengths) if db.strengths else None,
        weaknesses=json.loads(db.weaknesses) if db.weaknesses else None,
        created_at=db.created_at,
    )


@router.post("/{manuscript_id}/analysis", response_model=AnalysisResponse)
def run_analysis(manuscript_id: int) -> AnalysisResponse:
    with Session(engine) as session:
        manuscript = session.get(ManuscriptDB, manuscript_id)
        if not manuscript:
            raise HTTPException(404, "Manuscript not found")
        if not manuscript.raw_text:
            raise HTTPException(400, "Manuscript text not yet extracted. Try again shortly.")

        existing = session.exec(
            select(AnalysisResultDB).where(AnalysisResultDB.manuscript_id == manuscript_id)
        ).first()
        if existing:
            return _serialize(existing)

        result = analyze_manuscript(manuscript.raw_text)

        db = AnalysisResultDB(
            manuscript_id=manuscript_id,
            genre=result.get("genre"),
            themes=json.dumps(result.get("themes", [])),
            writing_style=result.get("writing_style"),
            target_audience=result.get("target_audience"),
            readability_score=result.get("readability_score"),
            strengths=json.dumps(result.get("strengths", [])),
            weaknesses=json.dumps(result.get("weaknesses", [])),
        )
        session.add(db)
        session.commit()
        session.refresh(db)
        return _serialize(db)


@router.get("/{manuscript_id}/analysis", response_model=AnalysisResponse)
def get_analysis(manuscript_id: int) -> AnalysisResponse:
    with Session(engine) as session:
        db = session.exec(
            select(AnalysisResultDB).where(AnalysisResultDB.manuscript_id == manuscript_id)
        ).first()
        if not db:
            raise HTTPException(404, "Analysis not yet generated")
        return _serialize(db)
