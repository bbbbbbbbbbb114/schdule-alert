# write_styles.py
import sys

css_content = """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    /* Design.md: Warm Neutral Scale */
    --bg-white: #ffffff;
    --bg-warm: #f6f5f4; /* Notion Warm White */
    --bg-warm-darker: #e8e6e3;
    
    /* Subtle Orange Background instead of default gray/blue for the vitality request */
    --bg-orange-tint: #fff8f5;
    
    /* Text Colors */
    --text-primary: rgba(0, 0, 0, 0.95);
    --text-secondary: #615d59;
    --text-muted: #a39e98;
    
    /* Design.md: Whisper Border */
    --border-color: rgba(0, 0, 0, 0.1);
    --border-whisper: 1px solid var(--border-color);

    /* Primary Accent: Swapped Blue for Notion-compatible Orange (#dd5b00 / #e56828) */
    --primary: #dd5b00;
    --primary-dark: #b84a00;
    --primary-light: #fff0e5;
    --focus-ring: rgba(221, 91, 0, 0.25);

    /* Semantic Status */
    --status-success: #1aae39;
    --status-warning: #dd5b00;
    --status-danger: #d32f2f;
    --danger-bg: #ffe4e4;

    /* Design.md: Shadows & Depth */
    --shadow-card: rgba(0,0,0,0.04) 0px 4px 18px, rgba(0,0,0,0.027) 0px 2.025px 7.84688px, rgba(0,0,0,0.02) 0px 0.8px 2.925px, rgba(0,0,0,0.01) 0px 0.175px 1.04062px;
    --shadow-deep: rgba(0,0,0,0.01) 0px 1px 3px, rgba(0,0,0,0.02) 0px 3px 7px, rgba(0,0,0,0.02) 0px 7px 15px, rgba(0,0,0,0.04) 0px 14px 28px, rgba(0,0,0,0.05) 0px 23px 52px;

    /* Base Units */
    --radius-small: 4px;
    --radius-standard: 12px;
    --radius-hero: 16px;
    --radius-pill: 9999px;

    /* Design.md: Smooth Interactions */
    --ease-spring: cubic-bezier(0.2, 0.8, 0.2, 1);
    --ease-squish: cubic-bezier(0.34, 1.56, 0.64, 1);

    /* Badges */
    --badge-orange-bg: #fff0e5;
    --badge-yellow-bg: #fffbe6;
    --badge-green-bg: #e6fffb;
    --badge-purple-bg: #f9f0ff;
    --badge-pink-bg: #fff0f6;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-feature-settings: 'lnum', 'locl';
    background-color: var(--bg-white);
    color: var(--text-primary);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
}

/* Animations */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.96); }
    to { opacity: 1; transform: scale(1); }
}

/* ====================================================
   APP LAYOUT (Sidebar + Main) 
==================================================== */
.app-layout {
    display: flex;
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    background-color: var(--bg-orange-tint); 
}

/* --- SIDEBAR --- */
.sidebar {
    width: 260px;
    background-color: var(--bg-warm);
    border-right: var(--border-whisper);
    display: flex;
    flex-direction: column;
    padding: 32px 16px;
    flex-shrink: 0;
    z-index: 100;
}

.sidebar .brand {
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.25px;
    color: var(--text-primary);
    margin-bottom: 40px;
    padding: 0 12px;
}

.side-nav {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.nav-item {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    border-radius: var(--radius-small);
    color: var(--text-secondary);
    font-weight: 500;
    font-size: 15px;
    text-decoration: none;
    transition: all 0.2s var(--ease-spring);
}

.nav-item:hover, .nav-item.active {
    background-color: rgba(0,0,0,0.05);
    color: var(--text-primary);
}
.nav-item.active {
    font-weight: 600;
    background-color: var(--primary-light);
    color: var(--primary);
}

/* --- MAIN WRAPPER --- */
.main-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow-y: auto;
    scroll-behavior: smooth;
}

/* --- TOPBAR --- */
.topbar {
    height: 64px;
    background: transparent;
    padding: 0 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
    margin-top: 16px;
    z-index: 50;
}
.topbar-left h2 { 
    font-size: 26px; 
    font-weight: 700; 
    letter-spacing: -0.625px; 
    margin-bottom: 0;
}
.topbar-right {
    display: flex;
    align-items: center;
    gap: 12px;
}
.date-display {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
}

/* --- DASHBOARD GRID --- */
.content-scroll {
    flex: 1;
    padding: 24px 40px 80px;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: 360px minmax(0, 1fr);
    gap: 32px;
    max-width: 1440px;
}

.col-left { display: flex; flex-direction: column; gap: 24px; }
.col-right { display: flex; flex-direction: column; gap: 24px; }

/* ====================================================
   CARDS & TYPOGRAPHY
==================================================== */
.card {
    background: var(--bg-white);
    border: var(--border-whisper);
    border-radius: var(--radius-standard);
    padding: 24px;
    box-shadow: var(--shadow-card);
    animation: fadeUp 0.6s var(--ease-spring) both;
}

h2 {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.25px;
    margin-bottom: 16px;
}

p.muted {
    font-size: 14px;
    color: var(--text-secondary);
    margin-bottom: 20px;
}

/* ====================================================
   FORMS & INPUTS 
==================================================== */
.form-grid { display: grid; gap: 16px; }

.time-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    background: var(--bg-warm);
    padding: 16px;
    border-radius: var(--radius-small);
    border: var(--border-whisper);
}

label {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-secondary);
    display: block;
    margin-bottom: 4px;
}

input[type="text"], input[type="datetime-local"], select, textarea {
    width: 100%;
    background: var(--bg-white);
    border: var(--border-whisper);
    border-radius: var(--radius-small);
    padding: 8px 12px;
    font-family: inherit;
    font-size: 14px;
    transition: all 0.2s var(--ease-spring);
}

input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 2px var(--focus-ring);
}

textarea { min-height: 80px; resize: vertical; }

.inline-checks {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.inline-checks label {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    margin: 0;
}

/* ====================================================
   BUTTONS
==================================================== */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: transparent;
    border-radius: var(--radius-small);
    padding: 8px 16px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s var(--ease-spring);
}

.btn:active { transform: scale(0.96); }

.btn-primary {
    background: var(--primary);
    color: #fff;
    width: 100%;
    padding: 10px;
}
.btn-primary:hover { background: var(--primary-dark); }

.btn-ghost {
    background: transparent;
    color: var(--text-secondary);
}
.btn-ghost:hover {
    background: rgba(0,0,0,0.05);
    color: var(--text-primary);
}

.btn-mini {
    padding: 6px 12px;
    font-size: 13px;
    background: rgba(0,0,0,0.05);
    color: var(--text-primary);
    border-radius: var(--radius-small);
    width: auto;
}
.btn-mini:hover { background: rgba(0,0,0,0.08); }

.btn-danger { color: var(--status-danger); background: transparent; }
.btn-danger:hover { background: var(--danger-bg); }

/* ====================================================
   LISTS & ITEMS
==================================================== */
.list { display: grid; gap: 8px; list-style: none; }

.list li {
    padding: 12px 16px;
    border: var(--border-whisper);
    border-radius: 8px;
    background: var(--bg-white);
    transition: all 0.2s var(--ease-spring);
}

.item { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }

.item.done { opacity: 0.6; background: var(--bg-warm); }
.item.done strong { text-decoration: line-through; color: var(--text-muted); }

.item-main { flex: 1; min-width: 0; }
.check-row { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.check-row strong { font-size: 15px; font-weight: 600; color: var(--text-primary); }

.meta { color: var(--text-secondary); font-size: 13px; margin-top: 4px; line-height: 1.5; }
.item-actions { display: flex; gap: 8px; }

/* ====================================================
   BADGES & CALENDAR (Overrides)
==================================================== */
.badge {
    display: inline-flex;
    align-items: center;
    border-radius: var(--radius-pill);
    font-size: 12px;
    font-weight: 600;
    padding: 2px 8px;
    letter-spacing: 0.125px;
}
.badge-orange { background-color: var(--badge-orange-bg); color: var(--primary); }
.badge-yellow { background-color: var(--badge-yellow-bg); color: #faad14; }
.badge-green { background-color: var(--badge-green-bg); color: #13c2c2; }
.badge-purple { background-color: var(--badge-purple-bg); color: #722ed1; }
.badge-pink { background-color: var(--badge-pink-bg); color: #eb2f96; }

.calendar-legend { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }

.fc {
    --fc-border-color: var(--border-color);
    --fc-page-bg-color: transparent;
    --fc-neutral-bg-color: var(--bg-warm);
    --fc-today-bg-color: var(--badge-orange-bg);
    --fc-button-bg-color: var(--bg-white);
    --fc-button-border-color: rgba(0,0,0,0.1);
    --fc-button-text-color: var(--text-primary);
    --fc-button-hover-bg-color: var(--bg-warm);
    font-family: inherit;
    font-size: 13px;
}
.fc .fc-toolbar-title { font-size: 18px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.25px;}
.fc-theme-standard td, .fc-theme-standard th { border-color: var(--border-color); }
.fc-daygrid-event {
    border-radius: 4px;
    padding: 2px 4px;
    font-size: 12px;
    font-weight: 600;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    border: none;
}
.fc-v-event {
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    font-size: 12px;
    border: none;
}
.fc .fc-now-indicator-line { border-color: var(--status-danger); border-width: 2px; }
.fc .fc-now-indicator-arrow { border-color: var(--status-danger); border-width: 5px; }

/* ====================================================
   MODALS & TOASTS
==================================================== */
.reminder-overlay {
    position: fixed; inset: 0; z-index: 9999;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    display: flex; align-items: center; justify-content: center;
    animation: fadeUp 0.3s var(--ease-spring);
}
.reminder-modal {
    width: min(440px, 90%);
    background: var(--bg-white);
    border: var(--border-whisper);
    border-radius: var(--radius-hero);
    padding: 32px;
    box-shadow: var(--shadow-deep);
    animation: scaleIn 0.4s var(--ease-squish);
    text-align: center;
}
.badge-danger {
    display: inline-block;
    border-radius: var(--radius-pill);
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
    color: var(--status-danger);
    background: var(--danger-bg);
    margin-bottom: 16px;
}
.toast {
    position: fixed; right: 24px; bottom: 24px;
    background: var(--text-primary);
    color: #fff;
    border-radius: var(--radius-standard);
    padding: 14px 20px;
    box-shadow: var(--shadow-deep);
    animation: fadeUp 0.4s var(--ease-squish);
    z-index: 9000;
    font-size: 14px;
}
.hidden { display: none !important; }

@media (max-width: 900px) {
    .dashboard-grid { grid-template-columns: 1fr; }
    .sidebar { display: none; }
    .content-scroll { padding: 16px; }
}
"""

try:
    with open('app/static/css/styles.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
