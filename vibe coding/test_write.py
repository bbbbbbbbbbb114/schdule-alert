css = """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg-white: #ffffff;
    --bg-warm: #f6f5f4;
    --bg-dark: #31302e;
    
    --text-primary: rgba(0, 0, 0, 0.95);
    --text-secondary: #615d59;
    --text-muted: #a39e98;
    
    --border-whisper: 1px solid rgba(0, 0, 0, 0.1);
    --border-color: rgba(0, 0, 0, 0.1);

    --blue: #0075de;
    --blue-dark: #005bab;
    --blue-light: #f2f9ff;
    --blue-text: #097fe8;
    --focus-ring: #097fe8;

    --status-success: #1aae39;
    --status-warning: #dd5b00;
    --status-danger: #d32f2f;
    --danger-bg: #ffe4e4;

    --shadow-card: rgba(0,0,0,0.04) 0px 4px 18px, rgba(0,0,0,0.027) 0px 2.025px 7.84688px, rgba(0,0,0,0.02) 0px 0.8px 2.925px, rgba(0,0,0,0.01) 0px 0.175px 1.04062px;
    --shadow-deep: rgba(0,0,0,0.01) 0px 1px 3px, rgba(0,0,0,0.02) 0px 3px 7px, rgba(0,0,0,0.02) 0px 7px 15px, rgba(0,0,0,0.04) 0px 14px 28px, rgba(0,0,0,0.05) 0px 23px 52px;

    --radius-small: 4px;
    --radius-standard: 12px;
    --radius-hero: 16px;
    --radius-pill: 9999px;

    --ease-spring: cubic-bezier(0.2, 0.8, 0.2, 1);
    --ease-squish: cubic-bezier(0.34, 1.56, 0.64, 1);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-feature-settings: "lnum", "locl";
    background-color: var(--bg-warm);
    color: var(--text-primary);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.96); }
    to { opacity: 1; transform: scale(1); }
}

.container {
    width: min(1080px, 92vw);
    margin: 0 auto;
    padding-bottom: 80px;
}

.topbar {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(12px);
    border-bottom: var(--border-whisper);
    padding: 16px 0;
    margin-bottom: 48px;
}

.brand {
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.2px;
}

.hero {
    margin: 64px 0 48px;
    animation: fadeUp 0.6s var(--ease-spring) both;
}

.hero-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 24px;
}

.hero h1 {
    font-size: 54px;
    font-weight: 700;
    line-height: 1.04;
    letter-spacing: -1.875px;
    margin-bottom: 12px;
}

.hero p.muted {
    font-size: 20px;
    font-weight: 500;
    color: var(--text-secondary);
    letter-spacing: -0.125px;
}

.card {
    background: var(--bg-white);
    border: var(--border-whisper);
    border-radius: var(--radius-standard);
    padding: 32px;
    margin-bottom: 32px;
    box-shadow: var(--shadow-card);
    animation: fadeUp 0.6s var(--ease-spring) both;
    transition: transform 0.3s var(--ease-spring), box-shadow 0.3s var(--ease-spring);
}

.card:nth-child(2) { animation-delay: 0.1s; }
.card:nth-child(3) { animation-delay: 0.15s; }
.card:nth-child(4) { animation-delay: 0.2s; }

.card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-deep);
}

h2 {
    font-size: 26px;
    font-weight: 700;
    line-height: 1.23;
    letter-spacing: -0.625px;
    margin-bottom: 6px;
}

.card > p.muted {
    font-size: 16px;
    color: var(--text-secondary);
    margin-bottom: 24px;
}

.form-grid {
    display: grid;
    gap: 16px;
    margin-top: 24px;
}

.time-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    background: var(--bg-warm);
    padding: 16px;
    border-radius: 8px;
    border: var(--border-whisper);
}

label {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: -10px;
    display: block;
}

input[type="text"], input[type="datetime-local"], select, textarea {
    width: 100%;
    background: var(--bg-white);
    border: var(--border-whisper);
    border-radius: var(--radius-small);
    padding: 10px 12px;
    font-family: inherit;
    font-size: 15px;
    transition: all 0.2s var(--ease-spring);
}

input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: var(--focus-ring);
    box-shadow: 0 0 0 2px rgba(9, 127, 232, 0.2);
}

textarea { min-height: 80px; resize: vertical; }

.inline-checks {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    align-items: center;
    padding-top: 8px;
}

.inline-checks label {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    cursor: pointer;
    margin-bottom: 0;
}

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: var(--border-whisper);
    border-radius: var(--radius-small);
    padding: 8px 16px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s var(--ease-spring);
}

.btn:active { transform: scale(0.96); }

.btn-primary {
    background: var(--blue);
    color: #fff;
    border-color: transparent;
    padding: 10px 20px;
}
.btn-primary:hover { background: var(--blue-dark); }

.btn-ghost { background: transparent; }
.btn-ghost:hover { background: rgba(0,0,0,0.04); }

.btn-mini {
    padding: 4px 10px;
    font-size: 13px;
    background: var(--bg-warm);
    border-radius: var(--radius-small);
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.btn-mini:hover { background: rgba(0,0,0,0.06); }

.btn-danger { color: var(--status-danger); }
.btn-danger:hover { background: var(--danger-bg); border-color: rgba(211,47,47,0.2); }

.btn-alert {
    background: var(--blue);
    color: #fff;
    width: 100%;
    font-size: 16px;
    padding: 12px;
}
.btn-alert:hover { background: var(--blue-dark); }

.list { display: grid; gap: 12px; list-style: none; }

.list li {
    padding: 16px;
    border: var(--border-whisper);
    border-radius: 8px;
    background: var(--bg-white);
    transition: all 0.2s var(--ease-spring);
}

.item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    position: relative;
    overflow: hidden;
}

.item::before {
    content: "";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background: transparent;
    transition: background 0.2s var(--ease-spring);
}

.item.done { opacity: 0.6; background: var(--bg-warm); }
.item.done::before { background: var(--text-muted); }
.item.done strong { text-decoration: line-through; color: var(--text-secondary); }

.item-main { flex: 1; min-width: 0; }
.check-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.check-row strong { font-size: 16px; font-weight: 600; }

.meta { color: var(--text-secondary); font-size: 14px; margin-top: 4px; line-height: 1.6; }

.tag {
    display: inline-flex;
    align-items: center;
    border-radius: var(--radius-pill);
    font-size: 12px;
    font-weight: 600;
    padding: 2px 8px;
    background: var(--bg-warm);
    color: var(--text-secondary);
    margin-right: 6px; margin-top: 6px;
    letter-spacing: 0.125px;
}

.item-actions {
    display: flex; gap: 8px; transition: opacity 0.2s var(--ease-spring);
}

.calendar-legend {
    display: flex; flex-wrap: wrap; gap: 12px; padding: 12px 16px;
    background: var(--bg-warm); border-radius: 8px; margin-bottom: 16px;
}
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: -4px; }

.fc {
    --fc-border-color: var(--border-color);
    --fc-page-bg-color: var(--bg-white);
    --fc-neutral-bg-color: var(--bg-warm);
    --fc-today-bg-color: var(--bg-warm);
    --fc-event-text-color: #fff;
    --fc-button-bg-color: var(--bg-white);
    --fc-button-border-color: var(--border-color);
    --fc-button-text-color: var(--text-primary);
    --fc-button-hover-bg-color: var(--bg-warm);
    font-family: inherit;
}
.fc .fc-toolbar-title { font-size: 20px; font-weight: 700; letter-spacing: -0.25px; }

.reminder-overlay {
    position: fixed; inset: 0; z-index: 9999;
    background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(4px);
    display: flex; align-items: center; justify-content: center;
    animation: fadeUp 0.3s var(--ease-spring);
}

.reminder-modal {
    width: min(460px, 100%); background: var(--bg-white);
    border: var(--border-whisper); border-radius: var(--radius-hero);
    padding: 32px; box-shadow: var(--shadow-deep);
    animation: scaleIn 0.4s var(--ease-squish); text-align: center;
}

.badge-danger {
    display: inline-block; border-radius: var(--radius-pill);
    padding: 4px 12px; font-size: 12px; font-weight: 600;
    color: var(--status-danger); background: var(--danger-bg); margin-bottom: 16px;
}

.toast {
    position: fixed; right: 24px; bottom: 24px;
    background: var(--text-primary); color: #fff;
    border-radius: var(--radius-standard); padding: 14px 20px;
    box-shadow: var(--shadow-deep); animation: fadeUp 0.4s var(--ease-squish); z-index: 9000;
}
.hidden { display: none !important; }

@media (max-width: 768px) {
    .container { width: 100%; padding: 0 16px 80px; }
    .hero h1 { font-size: 40px; }
    .hero-head { flex-direction: column; align-items: flex-start; }
    .time-group { grid-template-columns: 1fr; }
    .card { padding: 20px; }
}
"""
with open('app/static/css/styles.css', 'w', encoding='utf-8') as f:
    f.write(css)