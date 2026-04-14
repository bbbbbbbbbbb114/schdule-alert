# Vibe Schedule - Schedule Management Web App

A lightweight Flask-based schedule management application with time point/range support, configurable reminders, repeat rules, and FullCalendar visualization.

**Built with AI-assisted development ("Vibe Coding")** — iterative feature development with real-time testing and documentation.

> ⚠️ **AI Coding Guidelines / AI编程强制规范**: 
> Any AI or LLM assistant working on this repository **MUST** read and strictly follow the comprehensive guidelines defined in [`CLAUDE.md`](CLAUDE.md) before executing tasks. Key principles include:
> - Think Before Coding (State assumptions explicitly)
> - Simplicity First (Minimum code, no speculative features)
> - Surgical Changes (Touch only what you must)
> - Goal-Driven Execution (Loop until verified)

## ✨ Features

- **Dual Time Support**: Point-in-time or time-range scheduling
- **Configurable Reminders**: 5m/10m/1d offsets with start/end/both phases
- **Repeat Rules**: Daily/weekly recurrence with custom weekday selection
- **Visual Calendar**: FullCalendar integration with current-time indicator (red line)
- **Real-Time Alerts**: 0-level popup modal with mandatory confirmation
- **Location Tracking**: Optional location field for each schedule
- **Local Persistence**: SQLite database (no external services)
- **Responsive Design**: Grid-based UI with CSS Flexbox/Grid

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/vibe-coding.git
cd vibe-coding
```

2. **Create virtual environment** (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python run.py
```

5. **Open in browser**
```
http://127.0.0.1:5000
```

Default login: `user` / `password`

## 📋 Project Structure

```
vibe-coding/
├── app/
│   ├── __init__.py          # App factory & schema migration
│   ├── models.py            # Schedule database model
│   ├── routes.py            # API endpoints & reminder logic
│   ├── static/
│   │   ├── css/styles.css   # Styling and layout
│   │   └── js/app.js        # Frontend logic & calendar
│   └── templates/
│       ├── base.html        # Base template
│       ├── index.html       # Schedule management page
│       └── login.html       # Authentication page
├── tests/
│   └── test_app.py          # Automated test suite (6 tests)
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
├── DEMO.md                  # Step-by-step usage demo
├── TESTING.md               # Test documentation
└── UPDATE_LOG_2026-04-13.md # Daily update log
```

## 🧪 Testing

Run the automated test suite (6 tests included):

```bash
pytest -q
```

Expected output:
```
6 passed in 0.XXs
```

Coverage includes:
- Schedule CRUD operations
- Time range scheduling
- Reminder offset calculation with phases
- Daily/weekly recurrence expansion
- On-time reminder triggers (0-offset)

## 📖 Documentation

- **[DEMO.md](DEMO.md)** — Step-by-step class demonstration guide
- **[TESTING.md](TESTING.md)** — Test suite documentation
- **[DEV_PROCESS.md](DEV_PROCESS.md)** — Development workflow and decisions
- **[UPDATE_LOG_2026-04-13.md](UPDATE_LOG_2026-04-13.md)** — Latest changes and improvements

## 🔧 Tech Stack

| Component | Technology                |
| --------- | ------------------------- |
| Backend   | Flask 3.1.1               |
| ORM       | Flask-SQLAlchemy 3.1.1    |
| Database  | SQLite (local file)       |
| Frontend  | Vanilla JavaScript, HTML5 |
| Calendar  | FullCalendar 6.1.15 (CDN) |
| Styling   | CSS Grid/Flexbox          |

## 📝 API Endpoints

| Method | Endpoint                 | Purpose                         |
| ------ | ------------------------ | ------------------------------- |
| POST   | `/api/schedules`         | Create new schedule             |
| GET    | `/api/schedules`         | List all schedules              |
| PUT    | `/api/schedules/<id>`    | Update schedule                 |
| DELETE | `/api/schedules/<id>`    | Delete schedule                 |
| GET    | `/api/reminders/live`    | Get active reminders (30s poll) |
| GET    | `/api/reminders/overdue` | Get overdue schedules           |

## 🎯 Key Implementation Details

### Reminder System
- Server-side calculation of reminder instances
- Expansion of recurrence rules (daily/weekly)
- Offset-based triggering (5m, 10m, 1d before/after schedule time)
- Phase support (start time, end time, or both)
- Client-side deduplication via composite `reminder_id`

### Calendar Visualization
- Event expansion for recurring schedules (±30 day window)
- Color coding by schedule
- Current-time indicator (red line updates every minute)
- Point vs range event styling (dashed borders for ranges)
- Click to view location and full details

### Data Migration
- Backward-compatible schema migration on app startup
- Automatic table structuring without data loss
- Support for existing SQLite databases

## 🔐 Authentication

Basic session-based authentication included:
- Login page at `/login`
- Default credentials: `user` / `password`
- Session timeout after browser close

## 🐛 Known Issues & Fixes

### Fixed (Apr 13, 2026)
- ✅ Timezone offset bug (18:22 → 10:22): Fixed with local-naive ISO formatting
- ✅ Missing on-time reminders: Auto-include 0-offset in reminder triggers
- ✅ Reminder deduplication: Composite `reminder_id` for multi-phase reminders

### Future Enhancements
- [ ] Edit modal for full configuration (currently title-only editing)
- [ ] Production WSGI server deployment
- [ ] Advanced recurrence patterns (monthly, nth weekday, etc.)

## 📊 Statistics

- **Lines of Code**: ~600 (app.js), 300+ (routes.py)
- **Test Coverage**: 6 test cases covering major workflows
- **Time to Demo**: <5 minutes after startup
- **Database Size**: <1 MB (SQLite local file)

## 👨‍💻 Development Approach

This project demonstrates "Vibe Coding" — AI-assisted rapid development with:
1. **Iterative Feature Addition**: Add one feature per cycle with immediate testing
2. **Real-Time Bug Fixes**: Identify and repair issues before moving forward
3. **Comprehensive Documentation**: Document as you build, not after
4. **Test-Driven Validation**: Automated tests catch regressions early

## 📄 License

MIT License - Feel free to use this project for learning or as a starting template.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 📧 Contact

For questions or feedback about this project, please open an issue on GitHub.
