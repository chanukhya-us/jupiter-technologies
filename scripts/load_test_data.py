#!/usr/bin/env python3
"""
Load comprehensive test data into Jupiter Technologies database.

This script populates the database with 30+ records for each entity type,
providing realistic test data for development and testing purposes.

Usage:
    python scripts/load_test_data.py

Note: This will use the seed-demo-data CLI command which is idempotent
(safe to run multiple times - won't create duplicates).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.cli import seed_demo_data_command


def main():
    """Load test data into the database."""
    print("=" * 60)
    print("Jupiter Technologies - Test Data Loader")
    print("=" * 60)
    print()
    print("This script will load comprehensive test data including:")
    print("  - 36 Users (recruiters, HR, admins)")
    print("  - 35 Clients across various industries")
    print("  - 40 Jobs with different statuses")
    print("  - 55 Candidates in various stages")
    print("  - 40 Submissions linking candidates to jobs")
    print("  - 14 Employees (converted candidates)")
    print("  - 35 Projects across clients")
    print("  - 55 Tasks with various priorities")
    print("  - 42 Timesheets in different approval states")
    print("  - 56 Notes across all entities")
    print("  - 57 Activity logs for audit trail")
    print()
    print("Total: 479+ records")
    print()
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Aborted.")
        return
    
    print()
    print("Loading test data...")
    print("-" * 60)
    
    app = create_app()
    with app.app_context():
        try:
            seed_demo_data_command.main(
                args=[],
                prog_name="seed-demo-data",
                standalone_mode=False
            )
            print("-" * 60)
            print()
            print("✓ Test data loaded successfully!")
            print()
            print("Login credentials:")
            print("  Username: admin")
            print("  Password: admin123")
            print()
            print("Additional test users (password: password123):")
            print("  - recruiter1, recruiter2 (Recruiters)")
            print("  - hr1, hr2 (HR)")
            print("  - admin1 (Admin)")
            print("  - user5-user34 (Various roles)")
            print()
            print("See TEST_DATA_SUMMARY.md for complete details.")
            print()
        except Exception as e:
            print(f"✗ Error loading test data: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
