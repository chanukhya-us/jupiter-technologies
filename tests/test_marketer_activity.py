from __future__ import annotations

from datetime import UTC, date, datetime

from app.extensions import db
from app.marketer.service import process_marketer_reminders
from app.models import MarketerDailyLog, MarketerNotification, MarketerProfile, User
from tests.conftest import login


def test_dashboard_uses_local_chart_runtime(client):
    login(client, "owner")
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"vendor/chart.umd.min.js" in response.data
    assert b"cdn.jsdelivr.net/npm/chart.js" not in response.data


def test_marketer_rbac_scope(client):
    login(client, "marketer")

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200

    marketer_logs = client.get("/marketer-activity/logs")
    assert marketer_logs.status_code == 200

    blocked = client.get("/candidates", follow_redirects=False)
    assert blocked.status_code == 403


def test_marketer_log_validation_and_uniqueness(client, app):
    login(client, "marketer")
    today = date.today().isoformat()

    with app.app_context():
        marketer = User.query.filter_by(username="marketer").first()
        profile = MarketerProfile.query.filter_by(user_id=marketer.id).first()
        if profile is None:
            profile = MarketerProfile(user_id=marketer.id)
            db.session.add(profile)
        profile.daily_cutoff_local_time = "23:59"
        db.session.commit()

    invalid = client.post(
        "/marketer-activity/logs",
        data={
            "log_date": today,
            "jobs_applied": "0",
            "follow_ups": "0",
            "interviews_scheduled": "0",
            "pay_discussions": "0",
            "job_type": "unknown",
            "notes": "",
        },
        follow_redirects=True,
    )
    assert invalid.status_code == 200
    assert b"Notes are required when all activity counts are 0" in invalid.data

    created = client.post(
        "/marketer-activity/logs",
        data={
            "log_date": today,
            "jobs_applied": "5",
            "follow_ups": "3",
            "interviews_scheduled": "1",
            "pay_discussions": "1",
            "job_type": "c2c",
            "notes": "Reached out to key clients.",
        },
        follow_redirects=True,
    )
    assert created.status_code == 200
    assert b"Marketer activity log created" in created.data

    duplicate = client.post(
        "/marketer-activity/logs",
        data={
            "log_date": today,
            "jobs_applied": "2",
            "follow_ups": "1",
            "interviews_scheduled": "0",
            "pay_discussions": "0",
            "job_type": "w2",
            "notes": "Second attempt should block.",
        },
        follow_redirects=True,
    )
    assert duplicate.status_code == 200
    assert b"A log already exists for this marketer and date" in duplicate.data

    with app.app_context():
        marketer = User.query.filter_by(username="marketer").first()
        assert MarketerDailyLog.query.filter_by(marketer_user_id=marketer.id, log_date=date.today()).count() == 1


def test_marketer_submit_lock_with_admin_override(client, app):
    login(client, "marketer")
    today = date.today().isoformat()

    with app.app_context():
        marketer = User.query.filter_by(username="marketer").first()
        profile = MarketerProfile.query.filter_by(user_id=marketer.id).first()
        if profile is None:
            profile = MarketerProfile(user_id=marketer.id)
            db.session.add(profile)
        profile.daily_cutoff_local_time = "23:59"
        db.session.commit()

    create = client.post(
        "/marketer-activity/logs",
        data={
            "log_date": today,
            "jobs_applied": "4",
            "follow_ups": "2",
            "interviews_scheduled": "1",
            "pay_discussions": "0",
            "job_type": "contract",
            "notes": "Daily work done.",
        },
        follow_redirects=True,
    )
    assert create.status_code == 200

    with app.app_context():
        marketer = User.query.filter_by(username="marketer").first()
        profile = MarketerProfile.query.filter_by(user_id=marketer.id).first()
        if profile is None:
            profile = MarketerProfile(user_id=marketer.id)
            db.session.add(profile)
        profile.daily_cutoff_local_time = "00:00"
        db.session.commit()

        log = MarketerDailyLog.query.filter_by(marketer_user_id=marketer.id, log_date=date.today()).first()
        log_id = log.id

    blocked_submit = client.post(f"/marketer-activity/logs/{log_id}/submit", follow_redirects=True)
    assert blocked_submit.status_code == 200
    assert b"cannot be submitted because it is locked" in blocked_submit.data

    client.post("/logout", follow_redirects=True)
    login(client, "owner")

    admin_submit = client.post(f"/marketer-activity/logs/{log_id}/submit", follow_redirects=True)
    assert admin_submit.status_code == 200
    assert b"Marketer activity log submitted" in admin_submit.data



def test_marketer_reports_and_csv(client, app):
    login(client, "owner")

    with app.app_context():
        marketer = User.query.filter_by(username="marketer").first()
        existing = MarketerDailyLog.query.filter_by(marketer_user_id=marketer.id, log_date=date.today()).first()
        if existing is None:
            db.session.add(
                MarketerDailyLog(
                    marketer_user_id=marketer.id,
                    log_date=date.today(),
                    status="submitted",
                    jobs_applied=7,
                    follow_ups=3,
                    interviews_scheduled=2,
                    pay_discussions=1,
                    job_type="w2",
                    notes="Coverage for reporting",
                    created_by=marketer.id,
                    updated_by=marketer.id,
                )
            )
            db.session.commit()

    reports = client.get("/marketer-activity/reports")
    assert reports.status_code == 200
    assert b"Marketer Reports" in reports.data

    exported = client.get("/marketer-activity/reports/export.csv")
    assert exported.status_code == 200
    assert exported.mimetype == "text/csv"
    assert b"marketer_user_id" in exported.data



def test_process_marketer_reminders_is_idempotent(app):
    with app.app_context():
        marketer = User.query.filter_by(username="marketer").first()
        owner = User.query.filter_by(username="owner").first()

        profile = MarketerProfile.query.filter_by(user_id=marketer.id).first()
        if profile is None:
            profile = MarketerProfile(user_id=marketer.id)
            db.session.add(profile)
        profile.timezone = "America/New_York"
        profile.workdays_mask = "1,1,1,1,1,0,0"
        profile.daily_cutoff_local_time = "18:00"
        profile.reminder_enabled = True
        profile.reminder_times_local = "16:00,17:30"
        profile.escalation_after_misses = 1

        target_date = date(2026, 4, 13)
        MarketerDailyLog.query.filter_by(marketer_user_id=marketer.id, log_date=target_date).delete()
        MarketerNotification.query.filter_by(marketer_user_id=marketer.id, target_date=target_date).delete()
        db.session.commit()

        run_at = datetime(2026, 4, 13, 23, 0, tzinfo=UTC)
        first = process_marketer_reminders(run_at_utc=run_at)
        first_count = MarketerNotification.query.filter_by(marketer_user_id=marketer.id, target_date=target_date).count()
        assert first["logs_marked_missed"] >= 1
        assert first_count > 0

        second = process_marketer_reminders(run_at_utc=run_at)
        second_count = MarketerNotification.query.filter_by(marketer_user_id=marketer.id, target_date=target_date).count()
        assert second_count == first_count
        assert second["logs_marked_missed"] == 0



def test_marketer_onboarding(client, app):
    """Test that owner/admin can onboard new marketer users."""
    login(client, "owner")
    
    # Access onboarding page
    response = client.get("/marketer-activity/onboard")
    assert response.status_code == 200
    assert b"Onboard New Marketer" in response.data
    
    # Create new marketer
    response = client.post(
        "/marketer-activity/onboard",
        data={
            "username": "test_marketer",
            "full_name": "Test Marketer",
            "email": "test.marketer@jupiter.tech",
            "password": "password123",
            "timezone": "America/New_York",
            "daily_cutoff_local_time": "17:00",
            "reminder_times_local": "09:00,15:00",
            "escalation_after_misses": "2",
            "reminder_enabled": "1",
            "workday_0": "1",
            "workday_1": "1",
            "workday_2": "1",
            "workday_3": "1",
            "workday_4": "1",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"onboarded successfully" in response.data
    
    # Verify user was created
    with app.app_context():
        new_user = User.query.filter_by(username="test_marketer").first()
        assert new_user is not None
        assert new_user.full_name == "Test Marketer"
        assert new_user.email == "test.marketer@jupiter.tech"
        assert new_user.role.name == "marketer"
        
        # Verify profile was created
        profile = MarketerProfile.query.filter_by(user_id=new_user.id).first()
        assert profile is not None
        assert profile.timezone == "America/New_York"
        assert profile.daily_cutoff_local_time == "17:00"
        assert profile.reminder_enabled is True
        assert profile.escalation_after_misses == 2
    
    # Test duplicate username validation
    response = client.post(
        "/marketer-activity/onboard",
        data={
            "username": "test_marketer",
            "full_name": "Another Marketer",
            "email": "another@jupiter.tech",
            "password": "password123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"already exists" in response.data
