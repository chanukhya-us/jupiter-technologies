from __future__ import annotations

from tests.conftest import login
from app.extensions import db
from app.models import Candidate, Employee, Note, Timesheet


def test_candidate_conversion_rule(client, app):
    login(client, "hr")

    with app.app_context():
        candidate = Candidate.query.first()
        candidate_id = candidate.id
        candidate.status = "screening"
        db.session.commit()

    response_invalid = client.post(
        f"/employees/convert-from-candidate/{candidate_id}",
        follow_redirects=True,
    )
    assert response_invalid.status_code == 200
    assert b"Only selected or joined candidates can be converted" in response_invalid.data

    with app.app_context():
        candidate = Candidate.query.first()
        candidate.status = "selected"
        db.session.commit()

    response_valid = client.post(
        f"/employees/convert-from-candidate/{candidate_id}",
        follow_redirects=True,
    )
    assert response_valid.status_code == 200
    assert b"Candidate converted to employee" in response_valid.data

    with app.app_context():
        assert Employee.query.filter_by(candidate_id=candidate_id).count() == 1


def test_timesheet_unique_and_approval_flow(client, app):
    login(client, "hr")

    with app.app_context():
        candidate = Candidate.query.first()
        candidate_id = candidate.id
        candidate.status = "selected"
        db.session.commit()

    client.post(f"/employees/convert-from-candidate/{candidate_id}", follow_redirects=True)

    with app.app_context():
        employee = Employee.query.first()
        employee_id = employee.id

    response_first = client.post(
        "/timesheets",
        data={
            "employee_id": employee_id,
            "week_start": "2026-01-05",
            "week_end": "2026-01-11",
            "total_hours": "40",
        },
        follow_redirects=True,
    )
    assert b"Timesheet created" in response_first.data

    response_duplicate = client.post(
        "/timesheets",
        data={
            "employee_id": employee_id,
            "week_start": "2026-01-05",
            "week_end": "2026-01-11",
            "total_hours": "38",
        },
        follow_redirects=True,
    )
    assert b"Timesheet already exists" in response_duplicate.data

    with app.app_context():
        timesheet = Timesheet.query.first()
        timesheet_id = timesheet.id

    client.post(f"/timesheets/{timesheet_id}/submit", follow_redirects=True)
    approve_response = client.post(
        f"/timesheets/{timesheet_id}/approve",
        data={"review_comments": "Looks good"},
        follow_redirects=True,
    )
    assert b"Timesheet approved" in approve_response.data

    readonly_response = client.post(
        f"/timesheets/{timesheet_id}/submit",
        follow_redirects=True,
    )
    assert b"Approved timesheets are read-only" in readonly_response.data


def test_note_delete_restricted_to_owner_admin(client, app):
    login(client, "recruiter")

    with app.app_context():
        candidate = Candidate.query.first()
        candidate_id = candidate.id

    create_response = client.post(
        "/notes",
        data={
            "entity_type": "candidate",
            "entity_id": candidate_id,
            "note_type": "internal",
            "content": "Follow up tomorrow",
            "redirect_to": f"/candidates/{candidate_id}",
        },
        follow_redirects=True,
    )
    assert b"Note added" in create_response.data

    with app.app_context():
        note = Note.query.first()
        note_id = note.id

    forbidden_delete = client.post(
        f"/notes/{note_id}/delete",
        data={"redirect_to": f"/candidates/{candidate_id}"},
        follow_redirects=True,
    )
    assert b"Only owner/admin can delete notes" in forbidden_delete.data

    client.post("/logout", follow_redirects=True)
    login(client, "owner")

    allowed_delete = client.post(
        f"/notes/{note_id}/delete",
        data={"redirect_to": f"/candidates/{candidate_id}"},
        follow_redirects=True,
    )
    assert b"Note deleted" in allowed_delete.data


def test_csv_report_exports(client):
    login(client, "owner")

    candidates_csv = client.get("/reports/candidates.csv")
    assert candidates_csv.status_code == 200
    assert candidates_csv.mimetype == "text/csv"

    submissions_csv = client.get("/reports/submissions.csv")
    assert submissions_csv.status_code == 200
    assert submissions_csv.mimetype == "text/csv"

    timesheets_csv = client.get("/reports/timesheets.csv")
    assert timesheets_csv.status_code == 200
    assert timesheets_csv.mimetype == "text/csv"
