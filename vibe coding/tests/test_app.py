from datetime import datetime, timedelta, timezone

from app import create_app
from app.models import db


def create_test_app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-key",
        }
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app


def test_app_created():
    app = create_test_app()
    assert app is not None
    assert app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite")


def test_schedule_crud_and_reminders():
    app = create_test_app()
    client = app.test_client()

    login_res = client.post("/login", json={"username": "alice"})
    assert login_res.status_code == 200

    future_due = (datetime.now(timezone.utc) + timedelta(minutes=2)).isoformat()
    create_res = client.post(
        "/api/schedules",
        json={
            "title": "write report",
            "description": "finish chapter 1",
            "due_at": future_due,
        },
    )
    assert create_res.status_code == 201
    item_id = create_res.get_json()["id"]

    list_res = client.get("/api/schedules")
    assert list_res.status_code == 200
    assert len(list_res.get_json()) == 1

    update_res = client.put(
        f"/api/schedules/{item_id}",
        json={"title": "write final report", "is_done": True},
    )
    assert update_res.status_code == 200
    assert update_res.get_json()["is_done"] is True

    overdue_res = client.get("/api/reminders/overdue")
    assert overdue_res.status_code == 200
    assert overdue_res.get_json() == []

    live_res = client.get("/api/reminders/live")
    assert live_res.status_code == 200

    delete_res = client.delete(f"/api/schedules/{item_id}")
    assert delete_res.status_code == 200

    list_res_after_delete = client.get("/api/schedules")
    assert list_res_after_delete.status_code == 200
    assert list_res_after_delete.get_json() == []


def test_range_schedule_create_and_list():
    app = create_test_app()
    client = app.test_client()

    login_res = client.post("/login", json={"username": "bob"})
    assert login_res.status_code == 200

    start_at = (datetime.now(timezone.utc) + timedelta(hours=1)).replace(microsecond=0)
    end_at = start_at + timedelta(hours=2)

    create_res = client.post(
        "/api/schedules",
        json={
            "title": "deep work block",
            "description": "focus session",
            "schedule_type": "range",
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
        },
    )
    assert create_res.status_code == 201
    created = create_res.get_json()
    assert created["schedule_type"] == "range"
    assert created["start_at"] is not None
    assert created["end_at"] is not None

    list_res = client.get("/api/schedules")
    assert list_res.status_code == 200
    data = list_res.get_json()
    assert len(data) == 1
    assert data[0]["schedule_type"] == "range"


def test_live_reminders_with_offsets_phase_and_repeat_daily():
    app = create_test_app()
    client = app.test_client()

    login_res = client.post("/login", json={"username": "zoe"})
    assert login_res.status_code == 200

    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    start_today = now + timedelta(minutes=10)
    start_yesterday = start_today - timedelta(days=1)
    end_yesterday = start_yesterday + timedelta(hours=1)

    create_res = client.post(
        "/api/schedules",
        json={
            "title": "daily standup",
            "schedule_type": "range",
            "start_at": start_yesterday.isoformat(),
            "end_at": end_yesterday.isoformat(),
            "repeat_type": "daily",
            "reminder_offsets": "10m",
            "reminder_phase": "start",
            "location": "Room A",
        },
    )
    assert create_res.status_code == 201

    live_res = client.get(f"/api/reminders/live?since={now.isoformat()}")
    assert live_res.status_code == 200
    payload = live_res.get_json()
    assert len(payload) >= 1
    assert payload[0]["reminder_id"]
    assert payload[0]["location"] == "Room A"


def test_create_schedule_with_weekly_repeat_defaults_and_fields():
    app = create_test_app()
    client = app.test_client()

    login_res = client.post("/login", json={"username": "amy"})
    assert login_res.status_code == 200

    due_at = (datetime.now(timezone.utc) + timedelta(hours=2)).replace(microsecond=0)
    create_res = client.post(
        "/api/schedules",
        json={
            "title": "weekly review",
            "due_at": due_at.isoformat(),
            "schedule_type": "point",
            "repeat_type": "weekly",
            "reminder_offsets": "5m,1d",
            "reminder_phase": "both",
        },
    )
    assert create_res.status_code == 201
    created = create_res.get_json()
    assert created["repeat_type"] == "weekly"
    assert created["repeat_weekdays"] != ""
    assert created["reminder_offsets"] == "5m,1d"
    assert created["reminder_phase"] == "both"


def test_live_reminder_includes_on_time_trigger():
    app = create_test_app()
    client = app.test_client()

    login_res = client.post("/login", json={"username": "nina"})
    assert login_res.status_code == 200

    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    due_at = now + timedelta(seconds=30)

    create_res = client.post(
        "/api/schedules",
        json={
            "title": "on-time reminder",
            "schedule_type": "point",
            "due_at": due_at.isoformat(),
            "reminder_offsets": "5m",
            "reminder_phase": "start",
        },
    )
    assert create_res.status_code == 201

    live_res = client.get(f"/api/reminders/live?since={now.isoformat()}")
    assert live_res.status_code == 200
    payload = live_res.get_json()
    assert len(payload) >= 1
    assert any(item["title"] == "on-time reminder" for item in payload)
