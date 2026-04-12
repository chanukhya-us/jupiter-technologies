# Scripts Directory

Utility scripts for database management and testing.

For complete documentation, see the main [README.md](../README.md).

## Available Scripts

### load_test_data.py

Interactive script to load comprehensive test data (479+ records).

```bash
python scripts/load_test_data.py
```

See [Test Data section](../README.md#test-data) in main README for details.

### backup_db.py

Create timestamped backup of the database.

```bash
python scripts/backup_db.py
```

### zip_uploads.py

Create zip archive of uploads directory.

```bash
python scripts/zip_uploads.py
```

### init_db.py

Initialize database (use Flask CLI instead).

```bash
flask --app app.py init-db
```

### seed_demo_data.py

Load demo data (use load_test_data.py instead for better experience).

```bash
python scripts/load_test_data.py
```

## Quick Reference

**Load test data:**
```bash
python scripts/load_test_data.py
```

**Backup:**
```bash
python scripts/backup_db.py
python scripts/zip_uploads.py
```

**Restore:**
```bash
cp backups/app_YYYYMMDD_HHMMSS.db instance/app.db
unzip backups/uploads_YYYYMMDD_HHMMSS.zip -d .
```

For more information, see the [Scripts section](../README.md#scripts) in the main README.
