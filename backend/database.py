from sqlalchemy import create_engine
import os
from . import settings


def get_db_engine():
    if not os.path.exists(settings.DB_FILE):
        raise Exception("Database file not found. Please run import script first.")
    return create_engine(settings.DB_URL)
