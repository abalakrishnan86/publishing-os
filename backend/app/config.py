from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://posuser:pospass@localhost:5432/publishingos")
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
