import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'career-nova-ai-super-secret-key-2026')
    
    # Database config: prefer MYSQL_URL / DATABASE_URL if available, else SQLite
    # Example MySQL: mysql+pymysql://user:password@localhost/career_nova_db
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{BASE_DIR / 'career_nova.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    
    # AI / LLM configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    
    # Dataset path
    DATASET_PATH = BASE_DIR / 'datasets' / 'career_skills.csv'
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')

# Ensure required runtime directories exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BASE_DIR / 'datasets', exist_ok=True)
