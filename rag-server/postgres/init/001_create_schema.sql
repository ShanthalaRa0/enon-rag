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

CREATE TABLE IF NOT EXISTS upload_history (
    id SERIAL PRIMARY KEY,
    workflow_id UUID NOT NULL UNIQUE,
    folder VARCHAR(255) NOT NULL DEFAULT 'documents',
    filename VARCHAR(255) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
    current_stage VARCHAR(100) DEFAULT 'UPLOADING',
    progress INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);