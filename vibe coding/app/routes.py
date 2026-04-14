from datetime import datetime, timedelta, timezone

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.models import Schedule, db


bp = Blueprint("main", __name__)

ALLOWED_REMINDER_PHASES = {"start", "end", "both"}
ALLOWED_REPEAT_TYPES = {"none", "daily", "weekly"}


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def current_user() -> str | None:
    return session.get("username")


def parse_iso_datetime(raw: str, field_name: str) -> datetime:
    try:
        return datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be ISO format") from exc


def parse_reminder_offsets(raw: str) -> tuple[str, list[timedelta]]:
    normalized = (raw or "5m").replace(" ", "")
    tokens = [token for token in normalized.split(",") if token]
    if not tokens:
        tokens = ["5m"]

    deltas: list[timedelta] = []
    valid_tokens: list[str] = []
    for token in tokens:
        if token.endswith("m"):
            try:
                minutes = int(token[:-1])
            except ValueError as exc:
                raise ValueError("invalid minute reminder offset") from exc
            if minutes < 0:
                raise ValueError("reminder offset minutes must be non-negative")
            valid_tokens.append(f"{minutes}m")
            deltas.append(timedelta(minutes=minutes))
            continue

        if token.endswith("d"):
            try:
                days = int(token[:-1])
            except ValueError as exc:
                raise ValueError("invalid day reminder offset") from exc
            if days <= 0:
                raise ValueError("reminder offset days must be positive")
            valid_tokens.append(f"{days}d")
            deltas.append(timedelta(days=days))
            continue

        raise ValueError("reminder_offsets supports only Xm or Xd, e.g. 5m,10m,1d")

    unique_pairs = sorted(zip(valid_tokens, deltas), key=lambda pair: pair[1])
    
    # 构建去重后的字符串和对应的 timedelta 列表
    # (先构建字典利用 keys 去重，虽然由于 sorted + set 可能已经不需要，但保留兼容)
    dedup_dict = dict((token, delta) for token, delta in unique_pairs)
    merged_tokens = ",".join(dedup_dict.keys())
    merged_deltas = list(dedup_dict.values())

    return merged_tokens, merged_deltas


def parse_repeat_weekdays(raw: str) -> str:
    cleaned = (raw or "").replace(" ", "")
    if not cleaned:
        return ""
    values: list[int] = []
    for part in cleaned.split(","):
        if not part:
            continue
        day = int(part)
        if day < 0 or day > 6:
            raise ValueError("repeat_weekdays must be in range 0..6")
        values.append(day)
    values = sorted(set(values))
    return ",".join(str(v) for v in values)


def resolve_schedule_options(data: dict, existing: Schedule | None = None) -> dict:
    location = str(data.get("location") if "location" in data else (existing.location if existing else "") or "").strip()
    if len(location) > 120:
        raise ValueError("location is too long (max 120)")

    offsets_raw = (
        str(data.get("reminder_offsets"))
        if "reminder_offsets" in data
        else str(existing.reminder_offsets if existing else "5m")
    )
    reminder_offsets, _ = parse_reminder_offsets(offsets_raw)

    reminder_phase = str(
        data.get("reminder_phase")
        if "reminder_phase" in data
        else (existing.reminder_phase if existing else "start")
    ).strip().lower()
    if reminder_phase not in ALLOWED_REMINDER_PHASES:
        raise ValueError("reminder_phase must be start, end, or both")

    repeat_type = str(
        data.get("repeat_type")
        if "repeat_type" in data
        else (existing.repeat_type if existing else "none")
    ).strip().lower()
    if repeat_type not in ALLOWED_REPEAT_TYPES:
        raise ValueError("repeat_type must be none, daily, or weekly")

    repeat_weekdays_raw = (
        str(data.get("repeat_weekdays"))
        if "repeat_weekdays" in data
        else str(existing.repeat_weekdays if existing else "")
    )
    repeat_weekdays = parse_repeat_weekdays(repeat_weekdays_raw)
    if repeat_type == "weekly" and not repeat_weekdays:
        repeat_weekdays = str((existing.start_at or existing.due_at).weekday()) if existing else ""

    return {
        "location": location,
        "reminder_offsets": reminder_offsets,
        "reminder_phase": reminder_phase,
        "repeat_type": repeat_type,
        "repeat_weekdays": repeat_weekdays,
    }


def iterate_occurrences(item: Schedule, range_start: datetime, range_end: datetime):
    anchor_start = item.start_at or item.due_at
    anchor_end = item.end_at
    duration = (anchor_end - anchor_start) if anchor_end else None
    repeat_type = (item.repeat_type or "none").lower()

    if repeat_type == "none":
        yield anchor_start, anchor_end
        return

    day_start = (range_start - timedelta(days=1)).date()
    day_end = (range_end + timedelta(days=1)).date()

    weekly_days = {
        int(day)
        for day in (item.repeat_weekdays or "").split(",")
        if day.strip().isdigit()
    }
    if repeat_type == "weekly" and not weekly_days:
        weekly_days = {anchor_start.weekday()}

    current = day_start
    while current <= day_end:
        if repeat_type == "daily" or (repeat_type == "weekly" and current.weekday() in weekly_days):
            occ_start = datetime.combine(current, anchor_start.time())
            occ_end = occ_start + duration if duration else None
            yield occ_start, occ_end
        current += timedelta(days=1)


def build_live_reminders_for_schedule(item: Schedule, now: datetime, window_end: datetime) -> list[dict]:
    _, deltas = parse_reminder_offsets(item.reminder_offsets or "5m")
    max_offset = max(deltas) if deltas else timedelta()
    phase_window_end = window_end + max_offset

    phase_mode = (item.reminder_phase or "start").lower()
    phase_names = ["start", "end"] if phase_mode == "both" else [phase_mode]

    reminders: list[dict] = []
    for occ_start, occ_end in iterate_occurrences(item, now, phase_window_end):
        phase_time_map = {
            "start": occ_start,
            "end": occ_end or occ_start,
        }

        for phase in phase_names:
            phase_time = phase_time_map[phase]
            for offset in deltas:
                reminder_time = phase_time - offset
                if reminder_time < now or reminder_time > window_end:
                    continue

                row = item.to_dict()
                row["reminder_id"] = (
                    f"{item.id}:{phase}:{int(offset.total_seconds())}:{occ_start.isoformat()}"
                )
                row["reminder_phase"] = phase
                row["reminder_at"] = reminder_time.isoformat()
                row["due_at"] = phase_time.isoformat()
                row["start_at"] = occ_start.isoformat()
                row["end_at"] = occ_end.isoformat() if occ_end else None
                reminders.append(row)

    reminders.sort(key=lambda entry: entry["reminder_at"])
    return reminders


def resolve_create_time_fields(data: dict) -> tuple[str, datetime, datetime, datetime | None]:
    schedule_type = str(data.get("schedule_type") or "point").strip().lower()
    if schedule_type not in {"point", "range"}:
        raise ValueError("schedule_type must be point or range")

    if schedule_type == "point":
        point_raw = str(data.get("due_at") or data.get("point_at") or "").strip()
        if not point_raw:
            raise ValueError("due_at is required for point schedule")
        point_at = parse_iso_datetime(point_raw, "due_at")
        return "point", point_at, point_at, None

    start_raw = str(data.get("start_at") or "").strip()
    end_raw = str(data.get("end_at") or "").strip()
    if not start_raw or not end_raw:
        raise ValueError("start_at and end_at are required for range schedule")

    start_at = parse_iso_datetime(start_raw, "start_at")
    end_at = parse_iso_datetime(end_raw, "end_at")
    if end_at <= start_at:
        raise ValueError("end_at must be later than start_at")
    return "range", start_at, start_at, end_at


def resolve_update_time_fields(item: Schedule, data: dict) -> tuple[str, datetime, datetime, datetime | None]:
    current_type = item.schedule_type or ("range" if item.end_at else "point")
    schedule_type = str(data.get("schedule_type") or current_type).strip().lower()
    if schedule_type not in {"point", "range"}:
        raise ValueError("schedule_type must be point or range")

    if schedule_type == "point":
        point_raw = data.get("due_at")
        if point_raw is None:
            point_raw = data.get("point_at")
        point_at = (
            parse_iso_datetime(str(point_raw), "due_at")
            if point_raw is not None
            else item.due_at
        )
        return "point", point_at, point_at, None

    start_raw = data.get("start_at")
    end_raw = data.get("end_at")
    start_at = (
        parse_iso_datetime(str(start_raw), "start_at")
        if start_raw is not None
        else (item.start_at or item.due_at)
    )
    end_at = (
        parse_iso_datetime(str(end_raw), "end_at")
        if end_raw is not None
        else item.end_at
    )
    if end_at is None:
        end_at = start_at + timedelta(minutes=30)
    if end_at <= start_at:
        raise ValueError("end_at must be later than start_at")
    return "range", start_at, start_at, end_at


@bp.get("/")
def home():
    if not current_user():
        return redirect(url_for("main.login_page"))
    return render_template("index.html", username=current_user())


@bp.get("/login")
def login_page():
    return render_template("login.html")


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    if not username:
        return jsonify({"error": "username is required"}), 400
    session["username"] = username
    return jsonify({"message": "ok"})


@bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "ok"})


@bp.get("/api/schedules")
def list_schedules():
    user = current_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    items = (
        Schedule.query.filter_by(username=user)
        .order_by(Schedule.due_at.asc())
        .all()
    )
    return jsonify([item.to_dict() for item in items])


@bp.post("/api/schedules")
def create_schedule():
    user = current_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()

    if not title:
        return jsonify({"error": "title is required"}), 400

    try:
        schedule_type, due_at, start_at, end_at = resolve_create_time_fields(data)
        options = resolve_schedule_options(data)
        if options["repeat_type"] == "weekly" and not options["repeat_weekdays"]:
            options["repeat_weekdays"] = str(start_at.weekday())
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    item = Schedule(
        username=user,
        title=title,
        description=description,
        location=options["location"],
        schedule_type=schedule_type,
        reminder_offsets=options["reminder_offsets"],
        reminder_phase=options["reminder_phase"],
        repeat_type=options["repeat_type"],
        repeat_weekdays=options["repeat_weekdays"],
        due_at=due_at,
        start_at=start_at,
        end_at=end_at,
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@bp.put("/api/schedules/<int:item_id>")
def update_schedule(item_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    item = Schedule.query.filter_by(id=item_id, username=user).first()
    if not item:
        return jsonify({"error": "not found"}), 404

    data = request.get_json(silent=True) or {}

    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "title cannot be empty"}), 400
        item.title = title
    if "description" in data:
        item.description = (data.get("description") or "").strip()
    if "is_done" in data:
        item.is_done = bool(data.get("is_done"))

    if any(
        key in data
        for key in ["location", "reminder_offsets", "reminder_phase", "repeat_type", "repeat_weekdays"]
    ):
        try:
            options = resolve_schedule_options(data, item)
            item.location = options["location"]
            item.reminder_offsets = options["reminder_offsets"]
            item.reminder_phase = options["reminder_phase"]
            item.repeat_type = options["repeat_type"]
            item.repeat_weekdays = options["repeat_weekdays"]
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    if any(key in data for key in ["schedule_type", "due_at", "point_at", "start_at", "end_at"]):
        try:
            schedule_type, due_at, start_at, end_at = resolve_update_time_fields(item, data)
            item.schedule_type = schedule_type
            item.due_at = due_at
            item.start_at = start_at
            item.end_at = end_at
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    db.session.commit()
    return jsonify(item.to_dict())


@bp.delete("/api/schedules/<int:item_id>")
def delete_schedule(item_id: int):
    user = current_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    item = Schedule.query.filter_by(id=item_id, username=user).first()
    if not item:
        return jsonify({"error": "not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "deleted"})


@bp.get("/api/reminders/overdue")
def overdue_reminders():
    user = current_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    now = utc_now_naive()
    items = (
        Schedule.query.filter(
            Schedule.username == user,
            Schedule.is_done.is_(False),
            Schedule.due_at < now,
        )
        .order_by(Schedule.due_at.asc())
        .all()
    )
    return jsonify([item.to_dict() for item in items])


@bp.get("/api/reminders/live")
def live_reminders():
    user = current_user()
    if not user:
        return jsonify({"error": "unauthorized"}), 401

    now = utc_now_naive()
    since_raw = request.args.get("since", "").strip()
    if since_raw:
        try:
            now = datetime.fromisoformat(since_raw)
        except ValueError:
            return jsonify({"error": "since must be ISO format"}), 400

    window_end = now + timedelta(minutes=1)
    schedules = (
        Schedule.query.filter(
            Schedule.username == user,
            Schedule.is_done.is_(False),
        )
        .all()
    )

    reminders: list[dict] = []
    for item in schedules:
        reminders.extend(build_live_reminders_for_schedule(item, now, window_end))

    reminders.sort(key=lambda entry: entry["reminder_at"])
    return jsonify(reminders[:100])
