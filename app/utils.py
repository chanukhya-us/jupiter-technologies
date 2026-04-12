from __future__ import annotations

import csv
import io
import uuid
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Iterable, Sequence

from flask import current_app, send_file
from flask_login import current_user
from werkzeug.utils import secure_filename

from .extensions import db
from .models import ActivityLog

CHART_COLORS = [
    "#2563eb",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#06b6d4",
    "#f97316",
    "#84cc16",
]


def utcnow() -> datetime:
    return datetime.now(tz=UTC)


def parse_date(raw_value: str | None) -> date | None:
    if not raw_value:
        return None
    try:
        return datetime.strptime(raw_value, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_datetime(raw_value: str | None) -> datetime | None:
    if not raw_value:
        return None
    for fmt in ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try:
            dt = datetime.strptime(raw_value, fmt)
            return dt.replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def add_activity(
    action_type: str,
    entity_type: str,
    entity_id: int | None,
    message: str,
    metadata_json: str | None = None,
) -> None:
    user_id = current_user.id if getattr(current_user, "is_authenticated", False) else None
    log = ActivityLog(
        user_id=user_id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        message=message,
        metadata_json=metadata_json,
    )
    db.session.add(log)


def save_uploaded_file(upload, subfolder: str = "resumes") -> str | None:
    if not upload or upload.filename == "":
        return None

    extension = Path(upload.filename).suffix.lower()
    allowed_extensions = current_app.config["UPLOAD_EXTENSIONS"]
    if extension not in allowed_extensions:
        raise ValueError("Unsupported file type.")

    sanitized_name = secure_filename(upload.filename)
    unique_name = f"{uuid.uuid4().hex}_{sanitized_name}"
    target_dir = Path(current_app.config["UPLOAD_FOLDER"]) / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / unique_name
    upload.save(target_path)
    return str(target_path.relative_to(Path(current_app.root_path).parent))


def csv_response(filename: str, headers: list[str], rows: list[list[str]]) -> tuple:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    mem = io.BytesIO(output.getvalue().encode("utf-8"))
    output.close()
    mem.seek(0)
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name=filename)


def build_donut_chart(
    values: Iterable[str | None],
    *,
    preferred_order: Sequence[str] | None = None,
    empty_label: str = "Unspecified",
    top_n: int | None = None,
) -> dict:
    counter: Counter[str] = Counter()

    for raw_value in values:
        normalized = (raw_value or "").strip()
        counter[normalized or empty_label] += 1

    ordered_entries: list[tuple[str, int]] = []
    if preferred_order:
        for label in preferred_order:
            count = counter.pop(label, 0)
            if count > 0:
                ordered_entries.append((label, count))

    remaining_entries = sorted(counter.items(), key=lambda item: (-item[1], item[0].lower()))
    if top_n and top_n > 0 and len(remaining_entries) > top_n:
        top_entries = remaining_entries[:top_n]
        remainder_total = sum(count for _, count in remaining_entries[top_n:])
        remaining_entries = top_entries + [("Other", remainder_total)]
    ordered_entries.extend(remaining_entries)

    total = sum(count for _, count in ordered_entries)
    labels = [label for label, _ in ordered_entries]
    counts = [count for _, count in ordered_entries]
    colors = [CHART_COLORS[index % len(CHART_COLORS)] for index in range(len(ordered_entries))]

    items = []
    for index, (label, count) in enumerate(ordered_entries):
        percentage = round((count / total) * 100, 1) if total else 0
        items.append(
            {
                "label": label,
                "value": count,
                "percentage": percentage,
                "color": colors[index],
            }
        )

    return {
        "labels": labels,
        "values": counts,
        "colors": colors,
        "items": items,
        "total": total,
    }
