const scheduleList = document.getElementById('schedule-list');
const overdueList = document.getElementById('overdue-list');
const toast = document.getElementById('toast');
const logoutBtn = document.getElementById('logout-btn');
const reminderOverlay = document.getElementById('reminder-overlay');
const reminderMessage = document.getElementById('reminder-message');
const reminderConfirmBtn = document.getElementById('reminder-confirm-btn');
const calendarEl = document.getElementById('calendar');
const scheduleTypeEl = document.getElementById('schedule_type');
const pointTimeGroupEl = document.getElementById('point-time-group');
const rangeTimeGroupEl = document.getElementById('range-time-group');
const dueAtEl = document.getElementById('due_at');
const startAtEl = document.getElementById('start_at');
const endAtEl = document.getElementById('end_at');
const locationEl = document.getElementById('location');
const reminderPhaseEl = document.getElementById('reminder_phase');
const repeatTypeEl = document.getElementById('repeat_type');
const weeklyRepeatGroupEl = document.getElementById('weekly-repeat-group');
let lastReminderCursor = localNaiveNowISO();
const acknowledgedReminderIds = new Set();
const reminderQueue = [];
let currentReminder = null;
let audioCtx = null;
let calendar = null;

const EVENT_COLORS = ['#0075de', '#2a9d99', '#dd5b00', '#391c57', '#ff64c8'];

function toNaiveISOFromLocal(localValue) {
    if (!localValue) return '';
    return `${localValue}:00`;
}

function localNaiveNowISO() {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, '0');
    const d = String(now.getDate()).padStart(2, '0');
    const hh = String(now.getHours()).padStart(2, '0');
    const mm = String(now.getMinutes()).padStart(2, '0');
    const ss = String(now.getSeconds()).padStart(2, '0');
    return `${y}-${m}-${d}T${hh}:${mm}:${ss}`;
}

function showToast(message) {
    toast.textContent = message;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3500);
}

function ensureAudioContext() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
}

function playBeepOnce() {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(820, audioCtx.currentTime);
    gain.gain.setValueAtTime(0.0001, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.22, audioCtx.currentTime + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.25);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.26);
}

function startAlertSound() {
    ensureAudioContext();
    playBeepOnce();
}

function stopAlertSound() {
    // Single-play mode has no active loop to clear.
}

function showReminderModal(item) {
    currentReminder = item;
    reminderMessage.textContent = `${item.title}（${new Date(item.due_at).toLocaleString()}）已到提醒时间，请确认。`;
    reminderOverlay.classList.remove('hidden');
    startAlertSound();
}

function hideReminderModal() {
    reminderOverlay.classList.add('hidden');
    stopAlertSound();
    currentReminder = null;
}

function pumpReminderQueue() {
    if (currentReminder || reminderQueue.length === 0) {
        return;
    }
    const next = reminderQueue.shift();
    showReminderModal(next);
}

function renderList(el, items) {
    el.innerHTML = '';
    if (!items.length) {
        el.innerHTML = '<li>暂无数据</li>';
        return;
    }
    items.forEach((item) => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${item.title}</strong><br><span>${new Date(item.due_at).toLocaleString()}</span>`;
        el.appendChild(li);
    });
}

function renderSchedules(items) {
    scheduleList.innerHTML = '';
    if (!items.length) {
        scheduleList.innerHTML = '<li>暂无日程</li>';
        return;
    }

    items.forEach((item) => {
        const scheduleType = item.schedule_type || 'point';
        const timeText = scheduleType === 'range'
            ? `时间段：${new Date(item.start_at).toLocaleString()} - ${new Date(item.end_at).toLocaleString()}`
            : `时间点：${new Date(item.due_at).toLocaleString()}`;

        const li = document.createElement('li');
        li.className = item.is_done ? 'item done' : 'item';
        const locationTag = item.location ? `<span class="tag">地点：${item.location}</span>` : '';
        const repeatTag = item.repeat_type && item.repeat_type !== 'none' ? `<span class="tag">重复：${item.repeat_type}</span>` : '';
        const reminderTag = item.reminder_offsets ? `<span class="tag">提醒：${item.reminder_offsets}(${item.reminder_phase || 'start'})</span>` : '';
        li.innerHTML = `
            <div class="item-main">
                <label class="check-row">
                    <input type="checkbox" data-action="toggle" data-id="${item.id}" ${item.is_done ? 'checked' : ''} />
                    <strong>${item.title}</strong>
                </label>
                <div class="meta">${timeText}</div>
                <div class="meta">${locationTag}${repeatTag}${reminderTag}</div>
                <div class="meta">${item.description || '无描述'}</div>
            </div>
            <div class="item-actions">
                <button class="btn btn-mini" data-action="edit" data-id="${item.id}">编辑</button>
                <button class="btn btn-mini btn-danger" data-action="delete" data-id="${item.id}">删除</button>
            </div>
        `;
        scheduleList.appendChild(li);
    });
}

function buildCalendarEvents(items) {
    const events = [];

    items.forEach((item) => {
        const scheduleType = item.schedule_type || 'point';
        const color = item.is_done
            ? '#a39e98'
            : EVENT_COLORS[item.id % EVENT_COLORS.length];
        const anchorStart = scheduleType === 'range'
            ? new Date(item.start_at)
            : new Date(item.due_at);
        const anchorEnd = scheduleType === 'range'
            ? new Date(item.end_at)
            : new Date(anchorStart.getTime() + 5 * 60 * 1000);

        const repeatType = item.repeat_type || 'none';
        const weekdays = String(item.repeat_weekdays || '')
            .split(',')
            .filter(Boolean)
            .map((v) => Number(v));

        const pushEvent = (start, end) => {
            events.push({
                id: String(item.id),
                title: item.title,
                start,
                end,
                backgroundColor: color,
                borderColor: color,
                classNames: scheduleType === 'range' ? ['range-event'] : ['point-event'],
                extendedProps: {
                    description: item.description || '无描述',
                    scheduleType,
                    location: item.location || ''
                }
            });
        };

        if (repeatType === 'none') {
            pushEvent(anchorStart, anchorEnd);
            return;
        }

        const dayMs = 24 * 60 * 60 * 1000;
        const windowStart = new Date();
        windowStart.setDate(windowStart.getDate() - 30);
        windowStart.setHours(0, 0, 0, 0);
        const windowEnd = new Date();
        windowEnd.setDate(windowEnd.getDate() + 60);
        windowEnd.setHours(23, 59, 59, 999);

        const durationMs = anchorEnd.getTime() - anchorStart.getTime();

        for (let cursor = new Date(windowStart); cursor <= windowEnd; cursor = new Date(cursor.getTime() + dayMs)) {
            if (repeatType === 'weekly' && weekdays.length > 0) {
                if (!weekdays.includes(cursor.getDay() === 0 ? 6 : cursor.getDay() - 1)) {
                    continue;
                }
            }

            const occStart = new Date(cursor);
            occStart.setHours(anchorStart.getHours(), anchorStart.getMinutes(), anchorStart.getSeconds(), 0);
            const occEnd = new Date(occStart.getTime() + durationMs);

            if (occEnd < windowStart || occStart > windowEnd) {
                continue;
            }

            pushEvent(occStart, occEnd);
        }
    });

    return events;
}

function renderCalendar(items) {
    if (!calendarEl || !window.FullCalendar) {
        return;
    }

    const initialView = window.innerWidth < 680 ? 'timeGridDay' : 'timeGridWeek';
    const events = buildCalendarEvents(items);

    if (!calendar) {
        calendar = new window.FullCalendar.Calendar(calendarEl, {
            initialView,
            locale: 'zh-cn',
            height: 'auto',
            nowIndicator: true,
            firstDay: 1,
            slotMinTime: '06:00:00',
            slotMaxTime: '23:00:00',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'timeGridWeek,timeGridDay,dayGridMonth'
            },
            eventClick(info) {
                const desc = info.event.extendedProps.description;
                const scheduleType = info.event.extendedProps.scheduleType;
                const location = info.event.extendedProps.location;
                const timeText = scheduleType === 'range'
                    ? `${info.event.start?.toLocaleString()} - ${info.event.end?.toLocaleString()}`
                    : `${info.event.start?.toLocaleString()}（时间点）`;
                const locationText = location ? `\n地点：${location}` : '';
                alert(`${info.event.title}\n${timeText}${locationText}\n${desc}`);
            }
        });
        calendar.render();
    }

    calendar.removeAllEvents();
    calendar.addEventSource(events);
}

async function updateSchedule(id, payload) {
    const res = await fetch(`/api/schedules/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return res;
}

async function deleteSchedule(id) {
    return fetch(`/api/schedules/${id}`, { method: 'DELETE' });
}

async function refreshSchedules() {
    const res = await fetch('/api/schedules');
    if (!res.ok) return;
    const items = await res.json();
    renderSchedules(items);
    renderCalendar(items);
}

async function refreshOverdue() {
    const res = await fetch('/api/reminders/overdue');
    if (!res.ok) return;
    const items = await res.json();
    renderList(overdueList, items);
}

async function checkLiveReminders() {
    const res = await fetch(`/api/reminders/live?since=${encodeURIComponent(lastReminderCursor)}`);
    if (!res.ok) return;
    const items = await res.json();
    const unseen = items.filter((item) => {
        const key = item.reminder_id || String(item.id);
        return !acknowledgedReminderIds.has(key);
    });

    unseen.forEach((item) => {
        const key = item.reminder_id || String(item.id);
        const currentKey = currentReminder ? (currentReminder.reminder_id || String(currentReminder.id)) : '';
        if (!reminderQueue.find((queued) => (queued.reminder_id || String(queued.id)) === key) && currentKey !== key) {
            reminderQueue.push(item);
        }
    });

    if (unseen.length) {
        showToast(`提醒：检测到 ${unseen.length} 条到时日程`);
    }

    pumpReminderQueue();
    lastReminderCursor = localNaiveNowISO();
}

document.getElementById('schedule-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const scheduleType = scheduleTypeEl?.value || 'point';
    const reminderOffsets = Array.from(document.querySelectorAll('input[name="reminder_offsets"]:checked'))
        .map((el) => el.value)
        .join(',') || '5m';
    const repeatWeekdays = Array.from(document.querySelectorAll('input[name="repeat_weekdays"]:checked'))
        .map((el) => el.value)
        .join(',');

    const payload = {
        title: document.getElementById('title').value.trim(),
        description: document.getElementById('description').value.trim(),
        location: locationEl?.value.trim() || '',
        reminder_offsets: reminderOffsets,
        reminder_phase: reminderPhaseEl?.value || 'start',
        repeat_type: repeatTypeEl?.value || 'none',
        repeat_weekdays: repeatWeekdays,
        schedule_type: scheduleType
    };

    if (scheduleType === 'range') {
        payload.start_at = toNaiveISOFromLocal(startAtEl?.value || '');
        payload.end_at = toNaiveISOFromLocal(endAtEl?.value || '');
    } else {
        payload.due_at = toNaiveISOFromLocal(dueAtEl?.value || '');
    }

    const res = await fetch('/api/schedules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (!res.ok) {
        alert('创建失败，请检查输入');
        return;
    }

    e.target.reset();
    syncScheduleTypeUI();
    await refreshSchedules();
    await refreshOverdue();
});

scheduleList?.addEventListener('click', async (e) => {
    const target = e.target;
    if (!(target instanceof HTMLElement)) return;
    const action = target.dataset.action;
    const id = Number(target.dataset.id || 0);
    if (!action || !id) return;

    if (action === 'delete') {
        const ok = window.confirm('确认删除这条日程吗？');
        if (!ok) return;
        const res = await deleteSchedule(id);
        if (!res.ok) {
            alert('删除失败');
            return;
        }
        await refreshSchedules();
        await refreshOverdue();
        return;
    }

    if (action === 'edit') {
        const newTitle = window.prompt('请输入新标题');
        if (!newTitle) return;
        const res = await updateSchedule(id, { title: newTitle.trim() });
        if (!res.ok) {
            alert('编辑失败');
            return;
        }
        await refreshSchedules();
        await refreshOverdue();
    }
});

scheduleList?.addEventListener('change', async (e) => {
    const target = e.target;
    if (!(target instanceof HTMLInputElement)) return;
    if (target.dataset.action !== 'toggle') return;
    const id = Number(target.dataset.id || 0);
    if (!id) return;
    const res = await updateSchedule(id, { is_done: target.checked });
    if (!res.ok) {
        alert('更新状态失败');
        return;
    }
    await refreshSchedules();
    await refreshOverdue();
});

logoutBtn?.addEventListener('click', async () => {
    const res = await fetch('/logout', { method: 'POST' });
    if (res.ok) {
        window.location.href = '/login';
    }
});

reminderConfirmBtn?.addEventListener('click', () => {
    if (!currentReminder) return;
    const key = currentReminder.reminder_id || String(currentReminder.id);
    acknowledgedReminderIds.add(key);
    hideReminderModal();
    pumpReminderQueue();
});

window.addEventListener('pointerdown', ensureAudioContext, { once: true });
window.addEventListener('keydown', ensureAudioContext, { once: true });

function syncScheduleTypeUI() {
    const scheduleType = scheduleTypeEl?.value || 'point';
    const isRange = scheduleType === 'range';

    pointTimeGroupEl?.classList.toggle('hidden', isRange);
    rangeTimeGroupEl?.classList.toggle('hidden', !isRange);

    if (dueAtEl) {
        dueAtEl.required = !isRange;
    }
    if (startAtEl) {
        startAtEl.required = isRange;
    }
    if (endAtEl) {
        endAtEl.required = isRange;
    }
}

function syncRepeatUI() {
    const repeatType = repeatTypeEl?.value || 'none';
    const isWeekly = repeatType === 'weekly';
    weeklyRepeatGroupEl?.classList.toggle('hidden', !isWeekly);
}

scheduleTypeEl?.addEventListener('change', syncScheduleTypeUI);
repeatTypeEl?.addEventListener('change', syncRepeatUI);

(async function boot() {
    syncScheduleTypeUI();
    syncRepeatUI();
    await refreshSchedules();
    await refreshOverdue();
    await checkLiveReminders();
    setInterval(checkLiveReminders, 30000);
})();
