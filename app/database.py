
import psycopg
from pgvector.psycopg import register_vector

from app.config import get_settings


def get_connection():
    """Create and return a PostgreSQL database connection."""
    settings = get_settings()

    if settings.database_url is None:
        raise ValueError("DATABASE_URL is not configured")

    connection = psycopg.connect(
        settings.database_url.get_secret_value()
    )

    register_vector(connection)

    return connection
