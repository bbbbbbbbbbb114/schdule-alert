from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Schedule(db.Model):
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(120), nullable=True)
    schedule_type = db.Column(db.String(16), nullable=False, default="point")
    reminder_offsets = db.Column(db.String(64), nullable=False, default="5m")
    reminder_phase = db.Column(db.String(16), nullable=False, default="start")
    repeat_type = db.Column(db.String(16), nullable=False, default="none")
    repeat_weekdays = db.Column(db.String(32), nullable=True)
    due_at = db.Column(db.DateTime, nullable=False, index=True)
    start_at = db.Column(db.DateTime, nullable=True)
    end_at = db.Column(db.DateTime, nullable=True)
    is_done = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now_naive)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now_naive,
        onupdate=utc_now_naive,
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "title": self.title,
            "description": self.description or "",
            "location": self.location or "",
            "schedule_type": self.schedule_type or "point",
            "reminder_offsets": self.reminder_offsets or "5m",
            "reminder_phase": self.reminder_phase or "start",
            "repeat_type": self.repeat_type or "none",
            "repeat_weekdays": self.repeat_weekdays or "",
            "due_at": self.due_at.isoformat(),
            "start_at": self.start_at.isoformat() if self.start_at else None,
            "end_at": self.end_at.isoformat() if self.end_at else None,
            "is_done": self.is_done,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
