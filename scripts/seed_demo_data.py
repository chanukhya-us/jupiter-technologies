#!/usr/bin/env python3
from __future__ import annotations

from app import create_app
from app.cli import seed_demo_data_command


app = create_app()

with app.app_context():
    seed_demo_data_command.main(args=[], prog_name="seed-demo-data", standalone_mode=False)

print("Demo data seeded.")
