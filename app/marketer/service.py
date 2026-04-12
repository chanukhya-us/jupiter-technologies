from __future__ import annotations

import json
import smtplib
from datetime import UTC, date, datetime, time, timedelta
from email.message import EmailMessage
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import current_app

from ..constants import (
    MARKETER_LOG_STATUSES,
    MARKETER_NOTIFICATION_CHANNELS,
    MARKETER_NOTIFICATION_STATUSES,
    MARKETER_NOTIFICATION_TYPES,
)
from ..extensions import db
from ..models import MarketerDailyLog, MarketerNotification, MarketerProfile, Role, User
from ..utils import add_activity, utcnow


def parse_workdays_mask(mask: str | None) -> set[int]:
    if not mask:
        return {0, 1, 2, 3, 4}
    parts = [item.strip() for item in mask.split(",")]
    if len(parts) != 7:
        return {0, 1, 2, 3, 4}

    workdays: set[int] = set()
    for idx, raw in enumerate(parts):
        if raw in {"1", "true", "True", "yes", "on"}:
            workdays.add(idx)
    return workdays or {0, 1, 2, 3, 4}


def format_workdays_mask(workdays: set[int]) -> str:
    normalized = []
    for day in range(7):
        normalized.append("1" if day in workdays else "0")
    return ",".join(normalized)


def parse_reminder_times(reminder_times_local: str | None) -> list[time]:
    values: list[time] = []
    if reminder_times_local:
        for raw in reminder_times_local.split(","):
            raw = raw.strip()
            if not raw:
                continue
            parsed = parse_local_time(raw)
            if parsed is not None:
                values.append(parsed)

    if not values:
        values = [time(16, 0), time(17, 30)]

    deduped: dict[str, time] = {}
    for item in values:
        deduped[item.strftime("%H:%M")] = item
    return sorted(deduped.values())


def serialize_reminder_times(reminders: list[time]) -> str:
    return ",".join(item.strftime("%H:%M") for item in reminders)


def parse_local_time(raw_value: str | None) -> time | None:
    if not raw_value:
        return None
    raw_value = raw_value.strip()
    try:
        parts = raw_value.split(":")
        if len(parts) < 2:
            return None
        hour = int(parts[0])
        minute = int(parts[1])
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            return None
        return time(hour=hour, minute=minute)
    except (TypeError, ValueError):
        return None


def parse_local_time_or_default(raw_value: str | None, default: time) -> time:
    parsed = parse_local_time(raw_value)
    if parsed is None:
        return default
    return parsed


def timezone_for_profile(profile: MarketerProfile) -> ZoneInfo:
    try:
        return ZoneInfo(profile.timezone)
    except ZoneInfoNotFoundError:
        fallback = current_app.config.get("MARKETER_DEFAULT_TIMEZONE", "America/New_York")
        return ZoneInfo(fallback)


def local_now_for_profile(
    profile: MarketerProfile,
    *,
    now_utc_value: datetime | None = None,
) -> datetime:
    reference = now_utc_value or utcnow()
    return reference.astimezone(timezone_for_profile(profile))


def ensure_marketer_profile(user_id: int) -> MarketerProfile:
    profile = MarketerProfile.query.filter_by(user_id=user_id).first()
    if profile is not None:
        return profile

    profile = MarketerProfile(
        user_id=user_id,
        timezone=current_app.config["MARKETER_DEFAULT_TIMEZONE"],
        workdays_mask="1,1,1,1,1,0,0",
        daily_cutoff_local_time=current_app.config["MARKETER_DEFAULT_CUTOFF_LOCAL"],
        reminder_enabled=True,
        reminder_times_local=current_app.config["MARKETER_DEFAULT_REMINDER_TIMES"],
        escalation_after_misses=max(current_app.config["MARKETER_DEFAULT_ESCALATION_AFTER_MISSES"], 1),
    )
    db.session.add(profile)
    db.session.flush()
    return profile


def ensure_profiles_for_all_marketers() -> list[MarketerProfile]:
    marketer_role = Role.query.filter_by(name="marketer").first()
    if marketer_role is None:
        return []

    marketers = (
        User.query.filter_by(role_id=marketer_role.id, is_active=True)
        .order_by(User.full_name.asc())
        .all()
    )
    profiles: list[MarketerProfile] = []
    for marketer in marketers:
        profiles.append(ensure_marketer_profile(marketer.id))
    return profiles


def is_workday(profile: MarketerProfile, target_date: date) -> bool:
    return target_date.weekday() in parse_workdays_mask(profile.workdays_mask)


def can_marketer_edit_date(
    profile: MarketerProfile,
    target_date: date,
    *,
    now_utc_value: datetime | None = None,
) -> bool:
    local_now = local_now_for_profile(profile, now_utc_value=now_utc_value)
    today = local_now.date()
    yesterday = today - timedelta(days=1)
    if target_date not in {today, yesterday}:
        return False

    cutoff = parse_local_time_or_default(profile.daily_cutoff_local_time, time(18, 0))
    cutoff_today = datetime.combine(today, cutoff, tzinfo=local_now.tzinfo)
    if local_now > cutoff_today:
        return False

    return True


def can_marketer_edit_log(
    log: MarketerDailyLog,
    profile: MarketerProfile,
    *,
    is_admin: bool = False,
    now_utc_value: datetime | None = None,
) -> bool:
    if is_admin:
        return True
    if log.status in {"submitted", "late", "missed", "waived"}:
        return False
    return can_marketer_edit_date(profile, log.log_date, now_utc_value=now_utc_value)


def submit_status_for_log(
    profile: MarketerProfile,
    log_date: date,
    *,
    now_utc_value: datetime | None = None,
) -> str:
    local_now = local_now_for_profile(profile, now_utc_value=now_utc_value)
    cutoff = parse_local_time_or_default(profile.daily_cutoff_local_time, time(18, 0))
    cutoff_dt = datetime.combine(log_date, cutoff, tzinfo=local_now.tzinfo)

    if local_now > cutoff_dt:
        return "late"
    return "submitted"


def create_notification(
    *,
    user_id: int,
    marketer_user_id: int,
    target_date: date,
    notification_type: str,
    channel: str,
    idempotency_key: str,
    message: str,
    payload: dict | None = None,
    status: str = "pending",
) -> tuple[MarketerNotification, bool]:
    existing = MarketerNotification.query.filter_by(idempotency_key=idempotency_key).first()
    if existing is not None:
        return existing, False

    if notification_type not in MARKETER_NOTIFICATION_TYPES:
        notification_type = "system"
    if channel not in MARKETER_NOTIFICATION_CHANNELS:
        channel = "in_app"
    if status not in MARKETER_NOTIFICATION_STATUSES:
        status = "pending"

    notification = MarketerNotification(
        user_id=user_id,
        marketer_user_id=marketer_user_id,
        target_date=target_date,
        notification_type=notification_type,
        channel=channel,
        status=status,
        idempotency_key=idempotency_key,
        message=message,
        payload_json=json.dumps(payload or {}, ensure_ascii=True),
        sent_at=utcnow() if status == "sent" else None,
    )
    db.session.add(notification)
    db.session.flush()
    return notification, True


def send_email_safe(
    *,
    recipient: str,
    subject: str,
    body: str,
) -> tuple[bool, str | None]:
    if not recipient:
        return False, "Missing recipient email"
    if not current_app.config.get("MAIL_ENABLED", False):
        return False, "MAIL_ENABLED is false"

    host = (current_app.config.get("SMTP_HOST") or "").strip()
    if not host:
        return False, "SMTP_HOST is not configured"

    port = int(current_app.config.get("SMTP_PORT", 587))
    username = (current_app.config.get("SMTP_USERNAME") or "").strip()
    password = current_app.config.get("SMTP_PASSWORD") or ""
    use_tls = bool(current_app.config.get("SMTP_USE_TLS", True))
    sender = (current_app.config.get("MAIL_FROM") or "noreply@recruittrack.local").strip()

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(host, port, timeout=12) as smtp:
            smtp.ehlo()
            if use_tls:
                smtp.starttls()
                smtp.ehlo()
            if username:
                smtp.login(username, password)
            smtp.send_message(message)
    except Exception as exc:  # pragma: no cover - network dependent
        return False, str(exc)

    return True, None


def _missed_streak_for_marketer(marketer_user_id: int, *, ending_on: date, workdays: set[int]) -> int:
    streak = 0
    cursor = ending_on
    checked = 0

    while checked < 90:
        checked += 1
        if cursor.weekday() not in workdays:
            cursor -= timedelta(days=1)
            continue

        log = MarketerDailyLog.query.filter_by(marketer_user_id=marketer_user_id, log_date=cursor).first()
        if log is None or log.status != "missed":
            break

        streak += 1
        cursor -= timedelta(days=1)

    return streak


def _admin_and_owner_users() -> list[User]:
    roles = Role.query.filter(Role.name.in_(["owner", "admin"]))
    role_ids = [role.id for role in roles]
    if not role_ids:
        return []
    return (
        User.query.filter(User.role_id.in_(role_ids), User.is_active.is_(True))
        .order_by(User.full_name.asc())
        .all()
    )


def process_marketer_reminders(*, run_at_utc: datetime | None = None) -> dict[str, int]:
    run_time = run_at_utc or utcnow()
    summary = {
        "profiles_checked": 0,
        "logs_marked_missed": 0,
        "reminders_created": 0,
        "emails_sent": 0,
        "emails_failed": 0,
        "escalations_created": 0,
    }

    marketer_role = Role.query.filter_by(name="marketer").first()
    if marketer_role is None:
        return summary

    marketers = (
        User.query.filter_by(role_id=marketer_role.id, is_active=True)
        .order_by(User.id.asc())
        .all()
    )
    admin_recipients = _admin_and_owner_users()

    for marketer in marketers:
        profile = ensure_marketer_profile(marketer.id)
        summary["profiles_checked"] += 1
        local_now = local_now_for_profile(profile, now_utc_value=run_time)
        local_date = local_now.date()

        if not is_workday(profile, local_date):
            continue

        cutoff_time = parse_local_time_or_default(profile.daily_cutoff_local_time, time(18, 0))
        reminders = parse_reminder_times(profile.reminder_times_local)
        log = MarketerDailyLog.query.filter_by(marketer_user_id=marketer.id, log_date=local_date).first()

        terminal_statuses = {"submitted", "late", "waived"}

        if profile.reminder_enabled and (log is None or log.status not in terminal_statuses):
            for reminder in reminders:
                if local_now.time() < reminder:
                    continue

                reminder_message = (
                    f"Reminder: submit your marketer activity log for {local_date.isoformat()}."
                )
                in_app_key = (
                    f"marketer-reminder-inapp:{marketer.id}:{local_date.isoformat()}:{reminder.strftime('%H%M')}"
                )
                _, created = create_notification(
                    user_id=marketer.id,
                    marketer_user_id=marketer.id,
                    target_date=local_date,
                    notification_type="reminder",
                    channel="in_app",
                    idempotency_key=in_app_key,
                    message=reminder_message,
                    payload={"time": reminder.strftime("%H:%M")},
                    status="sent",
                )
                if created:
                    summary["reminders_created"] += 1

                email_key = (
                    f"marketer-reminder-email:{marketer.id}:{local_date.isoformat()}:{reminder.strftime('%H%M')}"
                )
                email_notification, email_created = create_notification(
                    user_id=marketer.id,
                    marketer_user_id=marketer.id,
                    target_date=local_date,
                    notification_type="reminder",
                    channel="email",
                    idempotency_key=email_key,
                    message=reminder_message,
                    payload={"time": reminder.strftime("%H:%M")},
                )
                if not email_created:
                    continue

                sent, error = send_email_safe(
                    recipient=marketer.email or "",
                    subject="RecruitTrack reminder: submit today's marketer log",
                    body=reminder_message,
                )
                if sent:
                    email_notification.status = "sent"
                    email_notification.sent_at = run_time
                    summary["emails_sent"] += 1
                else:
                    email_notification.status = "failed"
                    summary["emails_failed"] += 1
                    add_activity(
                        "notification_fallback",
                        "marketer_notification",
                        email_notification.id,
                        f"Reminder email fallback for marketer {marketer.username}: {error}",
                    )

        marked_missed = False
        if local_now.time() >= cutoff_time and (log is None or log.status == "draft"):
            if log is None:
                log = MarketerDailyLog(
                    marketer_user_id=marketer.id,
                    log_date=local_date,
                    status="missed",
                    jobs_applied=0,
                    follow_ups=0,
                    interviews_scheduled=0,
                    pay_discussions=0,
                    job_type="unknown",
                    notes="Auto-marked as missed by reminder scheduler.",
                    created_by=None,
                    updated_by=None,
                )
                db.session.add(log)
            else:
                log.status = "missed"
                log.updated_by = None
                if not log.notes:
                    log.notes = "Auto-marked as missed by reminder scheduler."

            db.session.flush()
            marked_missed = True
            summary["logs_marked_missed"] += 1
            add_activity(
                "status_change",
                "marketer_daily_log",
                log.id,
                f"Auto-marked marketer log as missed for {marketer.username} on {local_date.isoformat()}",
            )

        if (marked_missed or (log is not None and log.status == "missed")) and profile.escalation_after_misses > 0:
            streak = _missed_streak_for_marketer(
                marketer.id,
                ending_on=local_date,
                workdays=parse_workdays_mask(profile.workdays_mask),
            )
            if streak >= profile.escalation_after_misses:
                for admin_user in admin_recipients:
                    escalation_message = (
                        f"Escalation: {marketer.full_name} has {streak} missed marketer activity logs."
                    )
                    in_app_key = (
                        f"marketer-escalation-inapp:{admin_user.id}:{marketer.id}:{local_date.isoformat()}:{streak}"
                    )
                    _, created = create_notification(
                        user_id=admin_user.id,
                        marketer_user_id=marketer.id,
                        target_date=local_date,
                        notification_type="escalation",
                        channel="in_app",
                        idempotency_key=in_app_key,
                        message=escalation_message,
                        payload={"missed_streak": streak},
                        status="sent",
                    )
                    if created:
                        summary["escalations_created"] += 1

                    email_key = (
                        f"marketer-escalation-email:{admin_user.id}:{marketer.id}:{local_date.isoformat()}:{streak}"
                    )
                    email_notification, email_created = create_notification(
                        user_id=admin_user.id,
                        marketer_user_id=marketer.id,
                        target_date=local_date,
                        notification_type="escalation",
                        channel="email",
                        idempotency_key=email_key,
                        message=escalation_message,
                        payload={"missed_streak": streak},
                    )
                    if not email_created:
                        continue

                    sent, error = send_email_safe(
                        recipient=admin_user.email or "",
                        subject="RecruitTrack escalation: repeated missed marketer logs",
                        body=escalation_message,
                    )
                    if sent:
                        email_notification.status = "sent"
                        email_notification.sent_at = run_time
                        summary["emails_sent"] += 1
                    else:
                        email_notification.status = "failed"
                        summary["emails_failed"] += 1
                        add_activity(
                            "notification_fallback",
                            "marketer_notification",
                            email_notification.id,
                            f"Escalation email fallback for {admin_user.username}: {error}",
                        )

    db.session.commit()
    return summary


__all__ = [
    "MARKETER_LOG_STATUSES",
    "can_marketer_edit_date",
    "can_marketer_edit_log",
    "create_notification",
    "ensure_marketer_profile",
    "ensure_profiles_for_all_marketers",
    "format_workdays_mask",
    "is_workday",
    "local_now_for_profile",
    "parse_local_time",
    "parse_local_time_or_default",
    "parse_reminder_times",
    "parse_workdays_mask",
    "process_marketer_reminders",
    "serialize_reminder_times",
    "submit_status_for_log",
]
