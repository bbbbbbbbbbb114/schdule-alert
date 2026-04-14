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

const THEMES = [
    { bg: 'var(--badge-orange-bg)', text: 'var(--primary)', border: 'var(--primary)' },
    { bg: 'var(--badge-yellow-bg)', text: 'var(--status-warning)', border: 'var(--status-warning)' },
    { bg: 'var(--badge-green-bg)', text: 'var(--status-success)', border: 'var(--status-success)' },
    { bg: 'var(--badge-purple-bg)', text: '#722ED1', border: '#722ED1' },
    { bg: 'var(--badge-pink-bg)', text: '#EB2F96', border: '#EB2F96' }
];

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
        const locationTag = item.location ? `<span class="badge badge-purple" style="margin-right:4px;">地点：${item.location}</span>` : '';
        const repeatTag = item.repeat_type && item.repeat_type !== 'none' ? `<span class="badge badge-yellow" style="margin-right:4px;">重复：${item.repeat_type}</span>` : '';
        const reminderTag = item.reminder_offsets ? `<span class="badge badge-orange" style="margin-right:4px;">提醒：${item.reminder_offsets}(${item.reminder_phase || 'start'})</span>` : '';

        let timeAttrs = '';
        if (scheduleType === 'range') {
            timeAttrs = `data-start="${item.start_at}" data-end="${item.end_at}"`;
        } else {
            timeAttrs = `data-due="${item.due_at}"`;
        }

        li.innerHTML = `
            <div class="item-main" data-id="${item.id}">
                <label class="check-row">
                    <input type="checkbox" data-action="toggle" data-id="${item.id}" ${item.is_done ? 'checked' : ''} />
                    <strong>${item.title}</strong>
                </label>
                <div class="meta" ${timeAttrs}>${timeText} <span class="countdown"></span></div>
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
        const theme = item.is_done
            ? { bg: 'var(--bg-warm)', text: 'var(--text-muted)', border: 'var(--text-muted)' }
            : THEMES[item.id % THEMES.length];
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
                backgroundColor: theme.bg,
                textColor: theme.text,
                borderColor: scheduleType === 'range' ? 'transparent' : theme.border,
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

function getNextOccurrence(item, now) {
    const isRange = item.schedule_type === 'range';
    const anchorStart = isRange ? new Date(item.start_at) : new Date(item.due_at);
    // For point-in-time, we consider "end" to be the start time so it expires immediately
    const durationMs = isRange ? (new Date(item.end_at).getTime() - anchorStart.getTime()) : 0;
    const repeatType = item.repeat_type || 'none';

    if (repeatType === 'none') {
        const occEnd = new Date(anchorStart.getTime() + durationMs);
        return { start: anchorStart, end: occEnd, hasNext: occEnd >= now };
    }

    const weekdays = String(item.repeat_weekdays || '').split(',').filter(Boolean).map(Number);
    const dayMs = 24 * 60 * 60 * 1000;

    let cursor = new Date(anchorStart);
    if (now > cursor) {
        cursor = new Date(now);
        cursor.setHours(anchorStart.getHours(), anchorStart.getMinutes(), anchorStart.getSeconds(), 0);
        cursor = new Date(cursor.getTime() - dayMs);
    }

    for (let i = 0; i < 365; i++) {
        if (repeatType === 'weekly' && weekdays.length > 0) {
            const jsDay = cursor.getDay() === 0 ? 6 : cursor.getDay() - 1;
            if (!weekdays.includes(jsDay)) {
                cursor = new Date(cursor.getTime() + dayMs);
                continue;
            }
        }

        const occStart = new Date(cursor);
        occStart.setHours(anchorStart.getHours(), anchorStart.getMinutes(), anchorStart.getSeconds(), 0);
        const occEnd = new Date(occStart.getTime() + durationMs);

        if (occEnd >= now || (!isRange && occStart >= now)) {
            return { start: occStart, end: occEnd, hasNext: true };
        }
        cursor = new Date(cursor.getTime() + dayMs);
    }
    return { start: anchorStart, end: new Date(anchorStart.getTime() + durationMs), hasNext: false };
}

function updateCountdowns() {
    const now = new Date();
    document.querySelectorAll('#schedule-list .item').forEach(li => {
        if (li.classList.contains('done')) return;

        const mainEl = li.querySelector('.item-main');
        if (!mainEl) return;

        const itemId = Number(mainEl.getAttribute('data-id'));
        const item = currentSchedules.find(s => s.id === itemId);
        if (!item) return;

        const countdownEl = li.querySelector('.countdown');
        if (!countdownEl) return;

        const occ = getNextOccurrence(item, now);

        if (!occ.hasNext) {
            countdownEl.textContent = item.schedule_type === 'range' ? ' (已结束)' : ' (已过期)';
            countdownEl.style.color = '#d32f2f';
            return;
        }

        if (item.schedule_type === 'point') {
            const diff = occ.start - now;
            countdownEl.textContent = ` (距开始: ${formatDiff(diff)})`;
            countdownEl.style.color = '#e67300';
        } else {
            if (now < occ.start) {
                const diff = occ.start - now;
                countdownEl.textContent = ` (距开始: ${formatDiff(diff)})`;
                countdownEl.style.color = '#e67300';
            } else if (now >= occ.start && now < occ.end) {
                const diff = occ.end - now;
                countdownEl.textContent = ` (距结束: ${formatDiff(diff)})`;
                countdownEl.style.color = '#0075de';
            }
        }
    });
}

function formatDiff(ms) {
    const totalMins = Math.floor(ms / 60000);
    const d = Math.floor(totalMins / 1440);
    const h = Math.floor((totalMins % 1440) / 60);
    const m = totalMins % 60;

    let parts = [];
    if (d > 0) parts.push(`${d}天`);
    if (h > 0) parts.push(`${h}小时`);
    parts.push(`${m}分`);
    return parts.join('');
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

let editingId = null;
let currentSchedules = [];

async function refreshSchedules() {
    const res = await fetch('/api/schedules');
    if (!res.ok) return;
    const items = await res.json();
    currentSchedules = items;
    renderSchedules(items);
    renderCalendar(items);
    updateCountdowns();
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

    const isEdit = !!editingId;
    const url = isEdit ? `/api/schedules/${editingId}` : '/api/schedules';
    const method = isEdit ? 'PUT' : 'POST';

    const res = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (!res.ok) {
        alert((isEdit ? '更新' : '创建') + '失败，请检查输入');
        return;
    }

    e.target.reset();
    if (isEdit) {
        cancelEdit();
    }
    syncScheduleTypeUI();
    await refreshSchedules();
    await refreshOverdue();
});

function cancelEdit() {
    editingId = null;
    const form = document.getElementById('schedule-form');
    form.reset();
    form.querySelector('button[type="submit"]').textContent = '创建';
    const cancelBtn = form.querySelector('.cancel-edit-btn');
    if (cancelBtn) cancelBtn.remove();
    syncScheduleTypeUI();
    document.querySelector('.card h2').textContent = '新增日程';
}

scheduleList?.addEventListener('click', async (e) => {
    const target = e.target;
    if (!(target instanceof HTMLElement)) return;
    const action = target.dataset.action;
    const id = Number(target.dataset.id || 0);
    if (!action || !id) return;

    if (action === 'delete') {
        const isConfirming = target.dataset.confirm === 'true';

        if (!isConfirming) {
            target.dataset.confirm = 'true';
            const originalText = target.textContent;
            target.textContent = '确认删除？';
            target.classList.replace('btn-danger', 'btn-alert');
            target.style.color = '#fff';
            target.style.backgroundColor = 'var(--status-danger)';
            target.style.border = 'none';

            setTimeout(() => {
                if (target) {
                    target.dataset.confirm = 'false';
                    target.textContent = originalText;
                    target.classList.replace('btn-alert', 'btn-danger');
                    target.style.color = '';
                    target.style.backgroundColor = '';
                }
            }, 3000);
            return;
        }

        const li = target.closest('li');

        const res = await deleteSchedule(id);
        if (!res.ok) {
            alert('删除失败');
            return;
        }

        if (li) {
            li.style.transform = 'scale(0.95)';
            li.style.opacity = '0';
            li.style.transition = 'all 0.3s var(--ease-spring)';
            await new Promise(r => setTimeout(r, 300));
        }

        await refreshSchedules();
        await refreshOverdue();
        return;
    }

    if (action === 'edit') {
        const item = currentSchedules.find(s => s.id === id);
        if (!item) return;

        editingId = id;
        document.querySelector('.card h2').textContent = '编辑日程：' + item.title;
        scheduleTypeEl.value = item.schedule_type || 'point';
        document.getElementById('title').value = item.title || '';
        document.getElementById('description').value = item.description || '';
        locationEl.value = item.location || '';

        if (item.schedule_type === 'range') {
            if (item.start_at) startAtEl.value = item.start_at.slice(0, 16);
            if (item.end_at) endAtEl.value = item.end_at.slice(0, 16);
        } else {
            if (item.due_at) dueAtEl.value = item.due_at.slice(0, 16);
        }

        const offsets = item.reminder_offsets ? item.reminder_offsets.split(',') : [];
        document.querySelectorAll('input[name="reminder_offsets"]').forEach(cb => {
            cb.checked = offsets.includes(cb.value);
        });

        if (reminderPhaseEl) reminderPhaseEl.value = item.reminder_phase || 'start';
        if (repeatTypeEl) repeatTypeEl.value = item.repeat_type || 'none';

        const weekdays = item.repeat_weekdays ? item.repeat_weekdays.split(',') : [];
        document.querySelectorAll('input[name="repeat_weekdays"]').forEach(cb => {
            cb.checked = weekdays.includes(cb.value);
        });

        const dateEl = document.getElementById('current-date');
        if (dateEl) {
            const opts = { month: 'short', day: 'numeric', weekday: 'long' };
            dateEl.textContent = new Date().toLocaleDateString('zh-CN', opts);
        }

        syncScheduleTypeUI();
        syncRepeatUI();

        const form = document.getElementById('schedule-form');
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.textContent = '保存修改';
        if (!form.querySelector('.cancel-edit-btn')) {
            const cancelBtn = document.createElement('button');
            cancelBtn.type = 'button';
            cancelBtn.className = 'btn btn-ghost cancel-edit-btn';
            cancelBtn.textContent = '取消编辑';
            cancelBtn.style.marginLeft = '8px';
            cancelBtn.onclick = cancelEdit;
            submitBtn.parentNode.insertBefore(cancelBtn, submitBtn.nextSibling);
        }

        form.scrollIntoView({ behavior: 'smooth' });
    }
});

scheduleList?.addEventListener('change', async (e) => {
    const target = e.target;
    if (!(target instanceof HTMLInputElement)) return;
    if (target.dataset.action !== 'toggle') return;
    const id = Number(target.dataset.id || 0);
    if (!id) return;

    const li = target.closest('li');
    if (li) {
        if (target.checked) li.classList.add('done');
        else li.classList.remove('done');
        li.style.transform = 'scale(0.98)';
        setTimeout(() => li.style.transform = '', 150);
    }

    const res = await updateSchedule(id, { is_done: target.checked });
    if (!res.ok) {
        alert('更新状态失败');
        if (li) {
            if (target.checked) li.classList.remove('done');
            else li.classList.add('done');
        }
        return;
    }

    setTimeout(async () => {
        await refreshSchedules();
        await refreshOverdue();
    }, 300);
});

const addFab = document.getElementById('add-fab');
addFab?.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    document.getElementById('title').focus();
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

    if (reminderPhaseEl) {
        Array.from(reminderPhaseEl.options).forEach(opt => {
            if (opt.value === 'end' || opt.value === 'both') {
                opt.style.display = isRange ? '' : 'none';
                opt.disabled = !isRange;
            }
        });

        if (!isRange && (reminderPhaseEl.value === 'end' || reminderPhaseEl.value === 'both')) {
            reminderPhaseEl.value = 'start';
        }
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
    updateCountdowns();
    setInterval(checkLiveReminders, 30000);
    setInterval(updateCountdowns, 60000); // Update countdown every minute
})();
