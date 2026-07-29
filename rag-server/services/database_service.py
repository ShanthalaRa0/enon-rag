import logging
import uuid

import psycopg2
from psycopg2.extras import RealDictCursor

from config.settings import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
)

logger = logging.getLogger(__name__)


class DatabaseService:

    def __init__(self):

        self.connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor,
        )

        self.connection.autocommit = True

    # =====================================================
    # Create Document
    # =====================================================

    def create_document(
        self,
        workflow_id: str,
        original_filename: str,
        stored_filename: str,
        file_extension: str,
        mime_type: str,
        file_size: int,
    ):

        query = """
        INSERT INTO documents
        (
            workflow_id,
            original_filename,
            stored_filename,
            file_extension,
            mime_type,
            file_size
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    workflow_id,
                    original_filename,
                    stored_filename,
                    file_extension,
                    mime_type,
                    file_size,
                ),
            )

        logger.info(
            f"[DOCUMENT CREATED] {workflow_id}"
        )

    # =====================================================
    # Update Translation
    # =====================================================

    def update_translation(
        self,
        workflow_id: str,
        original_language: str,
        translated: bool,
    ):

        query = """
        UPDATE documents
        SET
            original_language = %s,
            translated = %s
        WHERE workflow_id = %s
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    original_language,
                    translated,
                    workflow_id,
                ),
            )

        logger.info(
            f"[DOCUMENT UPDATED] {workflow_id}"
        )

    # =====================================================
    # Get Document
    # =====================================================

    def get_document(
        self,
        workflow_id: str,
    ):

        query = """
        SELECT *
        FROM documents
        WHERE workflow_id = %s
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    workflow_id,
                ),
            )

            return cursor.fetchone()

    # =====================================================
    # Delete Document
    # =====================================================

    def delete_document(
        self,
        workflow_id: str,
    ):

        query = """
        DELETE FROM documents
        WHERE workflow_id = %s
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    workflow_id,
                ),
            )

        logger.info(
            f"[DOCUMENT DELETED] {workflow_id}"
        )


database_service = DatabaseService()