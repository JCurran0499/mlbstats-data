import psycopg2
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def start_connection(connection_string: str) -> psycopg2.extensions.connection:
    logger.info("Starting Neon database connection...")
    return psycopg2.connect(connection_string)
