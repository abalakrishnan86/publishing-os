import logging
import os
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File
from sqlmodel import Session, select

from app.config import MAX_FILE_SIZE_MB
from app.database import engine
from app.models.dbmodels import FileType, ManuscriptDB, ManuscriptStatus
from app.models.manuscript import ManuscriptResponse
from app.services.extractor import count_words, extract_text
from app.utils.file_utils import delete_file, save_upload_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/manuscripts", tags=["manuscripts"])

ALLOWED_EXTENSIONS = {"docx": FileType.DOCX, "pdf": FileType.PDF, "txt": FileType.TXT}
MAX_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def _run_extraction(manuscript_id: int) -> None:
    with Session(engine) as session:
        manuscript = session.get(ManuscriptDB, manuscript_id)
        if not manuscript:
            return
        manuscript.status = ManuscriptStatus.EXTRACTING
        manuscript.updated_at = datetime.utcnow()
        session.add(manuscript)
        session.commit()

        try:
            text = extract_text(manuscript.filepath, manuscript.file_type)
            manuscript.raw_text = text
            manuscript.word_count = count_words(text)
            manuscript.status = ManuscriptStatus.COMPLETED
        except Exception as exc:
            logger.error("Extraction failed for manuscript %s: %s", manuscript_id, exc)
            manuscript.status = ManuscriptStatus.FAILED

        manuscript.updated_at = datetime.utcnow()
        session.add(manuscript)
        session.commit()


@router.post("/upload", response_model=ManuscriptResponse, status_code=201)
async def upload_manuscript(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> ManuscriptResponse:
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(422, f"Unsupported file type '.{ext}'. Allowed: docx, pdf, txt")

    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(413, f"File exceeds {MAX_FILE_SIZE_MB} MB limit")

    # Reset stream so save_upload_file can read it
    import io
    file.file = io.BytesIO(content)

    stored_name, filepath = save_upload_file(file)
    title = filename.rsplit(".", 1)[0]

    with Session(engine) as session:
        manuscript = ManuscriptDB(
            title=title,
            filename=stored_name,
            filepath=filepath,
            file_type=ALLOWED_EXTENSIONS[ext],
        )
        session.add(manuscript)
        session.commit()
        session.refresh(manuscript)
        manuscript_id = manuscript.id

    background_tasks.add_task(_run_extraction, manuscript_id)

    with Session(engine) as session:
        manuscript = session.get(ManuscriptDB, manuscript_id)
        return ManuscriptResponse.model_validate(manuscript)


@router.get("", response_model=list[ManuscriptResponse])
def list_manuscripts() -> list[ManuscriptResponse]:
    with Session(engine) as session:
        manuscripts = session.exec(
            select(ManuscriptDB).order_by(ManuscriptDB.created_at.desc())
        ).all()
        return [ManuscriptResponse.model_validate(m) for m in manuscripts]


@router.get("/{manuscript_id}", response_model=ManuscriptResponse)
def get_manuscript(manuscript_id: int) -> ManuscriptResponse:
    with Session(engine) as session:
        manuscript = session.get(ManuscriptDB, manuscript_id)
        if not manuscript:
            raise HTTPException(404, "Manuscript not found")
        return ManuscriptResponse.model_validate(manuscript)


@router.delete("/{manuscript_id}")
def delete_manuscript(manuscript_id: int) -> dict:
    with Session(engine) as session:
        manuscript = session.get(ManuscriptDB, manuscript_id)
        if not manuscript:
            raise HTTPException(404, "Manuscript not found")
        delete_file(manuscript.filepath)
        session.delete(manuscript)
        session.commit()
    return {"message": "Manuscript deleted"}
