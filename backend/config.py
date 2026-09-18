import os
from dotenv import load_dotenv

# Project root folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load .env from the project root
ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_FILE)


class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "frontend",
        "static",
        "assets",
        "uploads"
    )