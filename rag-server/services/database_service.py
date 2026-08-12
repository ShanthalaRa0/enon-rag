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
        stored_filename: str,
    ):

        query = """
        UPDATE documents
        SET
            original_language = %s,
            translated = %s,
            stored_filename = %s
        WHERE workflow_id = %s
        """

        with self.connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    original_language,
                    translated,
                    stored_filename,
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

    def get_document_by_filename(self,original_filename: str):
        query = """
            SELECT
                id,
                workflow_id,
                original_filename,
                stored_filename,
                file_extension,
                mime_type,
                file_size
            FROM documents
            WHERE original_filename = %s
            LIMIT 1
        """

        with self.connection.cursor() as cursor: 
            cursor.execute(query, (original_filename,))
            return cursor.fetchone()

    # =====================================================
    # Get All Documents
    # =====================================================

    def get_all_documents(self):

        query = """
        SELECT *
        FROM documents
        ORDER BY created_at DESC
        """

        with self.connection.cursor() as cursor:

            cursor.execute(query)

            return cursor.fetchall()
        
database_service = DatabaseService()