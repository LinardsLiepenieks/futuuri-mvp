-- Migration: 0001_create_reports_table.sql
-- Creates the reports table to track report images and masks.

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT NOT NULL UNIQUE,
    report_image_path TEXT,
    mask_image_path TEXT,
    created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
    updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
);

-- A simple migrations tracking table (the runner will create it if missing)
-- Note: runner will record this file as applied after executing.
