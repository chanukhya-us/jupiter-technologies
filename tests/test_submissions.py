from __future__ import annotations

from tests.conftest import login
from app.extensions import db
from app.models import Candidate, Job, Submission


def test_duplicate_submission_blocked(client, app):
    login(client, "recruiter")

    with app.app_context():
        candidate = Candidate.query.first()
        job = Job.query.first()
        candidate_id = candidate.id
        job_id = job.id

    response_first = client.post(
        "/submissions",
        data={
            "candidate_id": candidate_id,
            "job_id": job_id,
            "recruiter_user_id": 2,
            "status": "submitted",
        },
        follow_redirects=True,
    )
    assert response_first.status_code == 200
    assert b"Submission created" in response_first.data

    response_second = client.post(
        "/submissions",
        data={
            "candidate_id": candidate_id,
            "job_id": job_id,
            "recruiter_user_id": 2,
            "status": "submitted",
        },
        follow_redirects=True,
    )
    assert response_second.status_code == 200
    assert b"Duplicate submission detected" in response_second.data

    with app.app_context():
        assert Submission.query.count() == 1


def test_closed_job_rejects_submission(client, app):
    login(client, "recruiter")

    with app.app_context():
        candidate = Candidate.query.first()
        job = Job.query.first()
        candidate_id = candidate.id
        job_id = job.id
        job.status = "closed"
        db.session.commit()

    response = client.post(
        "/submissions",
        data={
            "candidate_id": candidate_id,
            "job_id": job_id,
            "recruiter_user_id": 2,
            "status": "submitted",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Closed jobs cannot accept new submissions" in response.data
