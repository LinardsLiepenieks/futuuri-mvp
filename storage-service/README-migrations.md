# Simple Migrations for Storage Service

This project includes a tiny, dependency-free migration runner to manage the SQLite schema.

Files:

- `migrations/versions/0001_create_reports_table.sql` - creates the `reports` table
- `app/migrate.py` - simple runner that applies `.sql` files and records applied migrations

Usage (inside container or dev environment):

```bash
# from repository root
cd storage-service
python app/migrate.py
```

This will create `/app/data/database.db` and apply the migration.

Note: This runner is intentionally minimal. If you prefer a full-featured migration tool, use Alembic.
