import io
import json
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, HRFlowable
from sqlmodel import Session, select

from app.database import engine
from app.models.dbmodels import (
    AnalysisResultDB,
    ManuscriptDB,
    MarketingResultDB,
    MetadataResultDB,
)

router = APIRouter(prefix="/manuscripts", tags=["export"])


def _get_all(manuscript_id: int, session: Session) -> tuple:
    manuscript = session.get(ManuscriptDB, manuscript_id)
    if not manuscript:
        raise HTTPException(404, "Manuscript not found")
    analysis = session.exec(
        select(AnalysisResultDB).where(AnalysisResultDB.manuscript_id == manuscript_id)
    ).first()
    meta = session.exec(
        select(MetadataResultDB).where(MetadataResultDB.manuscript_id == manuscript_id)
    ).first()
    marketing = session.exec(
        select(MarketingResultDB).where(MarketingResultDB.manuscript_id == manuscript_id)
    ).first()
    return manuscript, analysis, meta, marketing


@router.get("/{manuscript_id}/export/json")
def export_json(manuscript_id: int) -> JSONResponse:
    with Session(engine) as session:
        manuscript, analysis, meta, marketing = _get_all(manuscript_id, session)

        def _json_list(val):
            if val is None:
                return None
            try:
                return json.loads(val)
            except Exception:
                return val

        payload = {
            "manuscript": {
                "id": manuscript.id,
                "title": manuscript.title,
                "file_type": manuscript.file_type,
                "status": manuscript.status,
                "word_count": manuscript.word_count,
                "created_at": manuscript.created_at.isoformat(),
            },
            "analysis": {
                "genre": analysis.genre,
                "themes": _json_list(analysis.themes),
                "writing_style": analysis.writing_style,
                "target_audience": analysis.target_audience,
                "readability_score": analysis.readability_score,
                "strengths": _json_list(analysis.strengths),
                "weaknesses": _json_list(analysis.weaknesses),
            } if analysis else None,
            "metadata": {
                "title_suggestions": _json_list(meta.title_suggestions),
                "subtitle": meta.subtitle,
                "description": meta.description,
                "keywords": _json_list(meta.keywords),
                "bisac_categories": _json_list(meta.bisac_categories),
                "author_bio_prompt": meta.author_bio_prompt,
            } if meta else None,
            "marketing": {
                "back_cover_blurb": marketing.back_cover_blurb,
                "amazon_description": marketing.amazon_description,
                "twitter_post": marketing.twitter_post,
                "linkedin_post": marketing.linkedin_post,
                "instagram_post": marketing.instagram_post,
                "press_release_excerpt": marketing.press_release_excerpt,
                "elevator_pitch": marketing.elevator_pitch,
            } if marketing else None,
            "exported_at": datetime.utcnow().isoformat(),
        }

    safe_title = "".join(c for c in manuscript.title if c.isalnum() or c in " _-")[:50]
    return JSONResponse(
        content=payload,
        headers={"Content-Disposition": f'attachment; filename="{safe_title}_report.json"'},
    )


@router.get("/{manuscript_id}/export/pdf")
def export_pdf(manuscript_id: int) -> StreamingResponse:
    with Session(engine) as session:
        manuscript, analysis, meta, marketing = _get_all(manuscript_id, session)

    def _json_list(val):
        if val is None:
            return []
        try:
            return json.loads(val)
        except Exception:
            return []

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()

    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=18, spaceAfter=6)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceAfter=4, textColor=colors.HexColor("#1a365d"))
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, spaceAfter=4, leading=14)
    label = ParagraphStyle("Label", parent=styles["Normal"], fontSize=10, fontName="Helvetica-Bold", spaceAfter=2)

    def section(title: str):
        return [
            Spacer(1, 0.15 * inch),
            HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")),
            Spacer(1, 0.05 * inch),
            Paragraph(title, h2),
        ]

    def field(lbl: str, val: str | None):
        if not val:
            return []
        return [Paragraph(lbl, label), Paragraph(val, body)]

    def bullet_list(items: list[str]):
        return [Paragraph(f"• {item}", body) for item in items if item]

    story = [
        Paragraph("Publishing OS Report", h1),
        Paragraph(f"<b>Title:</b> {manuscript.title}", body),
        Paragraph(f"<b>File type:</b> {manuscript.file_type.upper()}  |  <b>Word count:</b> {manuscript.word_count or 'N/A'}", body),
        Paragraph(f"<b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", body),
    ]

    if analysis:
        story += section("Manuscript Analysis")
        story += field("Genre", analysis.genre)
        story += field("Target Audience", analysis.target_audience)
        story += field("Readability Score", analysis.readability_score)
        story += field("Writing Style", analysis.writing_style)
        themes = _json_list(analysis.themes)
        if themes:
            story.append(Paragraph("Themes", label))
            story += bullet_list(themes)
        strengths = _json_list(analysis.strengths)
        if strengths:
            story.append(Paragraph("Strengths", label))
            story += bullet_list(strengths)
        weaknesses = _json_list(analysis.weaknesses)
        if weaknesses:
            story.append(Paragraph("Areas for Improvement", label))
            story += bullet_list(weaknesses)

    if meta:
        story += section("Publishing Metadata")
        titles = _json_list(meta.title_suggestions)
        if titles:
            story.append(Paragraph("Title Suggestions", label))
            story += bullet_list(titles)
        story += field("Subtitle", meta.subtitle)
        story += field("Description", meta.description)
        keywords = _json_list(meta.keywords)
        if keywords:
            story += field("Keywords", ", ".join(keywords))
        bisac = _json_list(meta.bisac_categories)
        if bisac:
            story += field("BISAC Categories", " | ".join(bisac))
        story += field("Author Bio Prompt", meta.author_bio_prompt)

    if marketing:
        story += section("Marketing Content")
        story += field("Elevator Pitch", marketing.elevator_pitch)
        story += field("Back Cover Blurb", marketing.back_cover_blurb)
        story += field("Amazon Description", marketing.amazon_description)
        story += field("Twitter Post", marketing.twitter_post)
        story += field("LinkedIn Post", marketing.linkedin_post)
        story += field("Instagram Post", marketing.instagram_post)
        story += field("Press Release Excerpt", marketing.press_release_excerpt)

    doc.build(story)
    buf.seek(0)

    safe_title = "".join(c for c in manuscript.title if c.isalnum() or c in " _-")[:50]
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_title}_report.pdf"'},
    )
