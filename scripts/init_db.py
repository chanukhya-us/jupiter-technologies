#!/usr/bin/env python3
from __future__ import annotations

from app import create_app
from app.cli import init_db_command


app = create_app()

with app.app_context():
    init_db_command.main(args=[], prog_name="init-db", standalone_mode=False)

print("Database initialized.")
