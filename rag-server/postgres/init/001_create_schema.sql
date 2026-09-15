CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    workflow_id UUID NOT NULL UNIQUE,
    folder VARCHAR(255) NOT NULL DEFAULT 'documents',
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    original_language VARCHAR(30),
    translated BOOLEAN NOT NULL DEFAULT FALSE,
    file_extension VARCHAR(20),
    mime_type VARCHAR(100),
    file_size BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT documents_folder_filename_key
        UNIQUE (folder, original_filename)
);