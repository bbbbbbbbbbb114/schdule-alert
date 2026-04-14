from flask import Flask
from sqlalchemy import inspect, text

from config import Config
from app.models import db


def ensure_schedule_schema() -> None:
    inspector = inspect(db.engine)
    if not inspector.has_table("schedules"):
        return

    columns = {col["name"] for col in inspector.get_columns("schedules")}

    if "schedule_type" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE schedules ADD COLUMN schedule_type "
                "VARCHAR(16) NOT NULL DEFAULT 'point'"
            )
        )
    if "location" not in columns:
        db.session.execute(text("ALTER TABLE schedules ADD COLUMN location VARCHAR(120)"))
    if "reminder_offsets" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE schedules ADD COLUMN reminder_offsets "
                "VARCHAR(64) NOT NULL DEFAULT '5m'"
            )
        )
    if "reminder_phase" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE schedules ADD COLUMN reminder_phase "
                "VARCHAR(16) NOT NULL DEFAULT 'start'"
            )
        )
    if "repeat_type" not in columns:
        db.session.execute(
            text(
                "ALTER TABLE schedules ADD COLUMN repeat_type "
                "VARCHAR(16) NOT NULL DEFAULT 'none'"
            )
        )
    if "repeat_weekdays" not in columns:
        db.session.execute(text("ALTER TABLE schedules ADD COLUMN repeat_weekdays VARCHAR(32)"))
    if "start_at" not in columns:
        db.session.execute(text("ALTER TABLE schedules ADD COLUMN start_at DATETIME"))
    if "end_at" not in columns:
        db.session.execute(text("ALTER TABLE schedules ADD COLUMN end_at DATETIME"))

    db.session.execute(
        text(
            "UPDATE schedules "
            "SET schedule_type = COALESCE(schedule_type, 'point'), "
            "location = COALESCE(location, ''), "
            "reminder_offsets = COALESCE(reminder_offsets, '5m'), "
            "reminder_phase = COALESCE(reminder_phase, 'start'), "
            "repeat_type = COALESCE(repeat_type, 'none'), "
            "repeat_weekdays = COALESCE(repeat_weekdays, ''), "
            "start_at = COALESCE(start_at, due_at)"
        )
    )
    db.session.commit()


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from app.routes import bp

    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()
        ensure_schedule_schema()

    return app
