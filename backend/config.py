import os
from dotenv import load_dotenv

# Project root folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load .env from the project root
ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_FILE)


class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY")

    DATABASE_URL = os.environ.get("DATABASE_URL")

    # Convert MySQL URL to PyMySQL URL
    if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace(
            "mysql://",
            "mysql+pymysql://",
            1
        )

    # Aiven requires SSL
    if DATABASE_URL and "ssl-mode=REQUIRED" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace(
            "?ssl-mode=REQUIRED",
            "?ssl_check_hostname=false"
        )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "frontend",
        "static",
        "assets",
        "uploads"
    )