/**
 * events.js — Events page logic for Chitalishte Connect
 * Handles: Dynamic calendar, event filtering, create-event modal, localStorage CRUD
 */

// ─── Seed Event Data ────────────────────────────────────────────────
const STORAGE_KEY = 'chitalishte_events';

const seedEvents = [
  {
    id: 'seed-1',
    title: 'Horo - Intermediate Folk Dance',
    date: '2026-03-22',
    time: '18:00',
    description: 'Master the complex rhythms of the Rodopi region with Maestro Georgiev. Open for all registered members.',
    category: 'Dance Workshop',
    categoryColor: 'primary-fixed',
    categoryTextColor: 'on-primary-fixed',
    image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBzqLJr3877Rx2hGGBT4VxyxWiAuhARMDeq04ht2bx9hkniLWh7SZrovGNqpxMjfgGC2kVI_xreqj7X4Kno642R23rUOJEefeCvHVV6LZYPnrPxnmiVzOt1vkVnqEB0ELXeNwXsTy-RfK6rSNFdPglJKUnIFjdT1OTPc2GDdaKg83QAb-2-QZMg7L0KWSqwWvojRoFxXuAWGru1M3ibw-UPtFEbGqpGOV7QbrRmVch2N2lTH-kGkqbjQQZamVuoxtreIvkfUwBCDYQ',
    attendees: 14,
  },
  {
    id: 'seed-2',
    title: 'Preserving the Unwritten Archive',
    date: '2026-03-25',
    time: '16:30',
    description: 'Join our chief librarian for a deep dive into the 19th-century manuscripts preserved in our community archives.',
    category: 'Heritage Talk',
    categoryColor: 'tertiary-fixed',
    categoryTextColor: 'on-tertiary-fixed',
    image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCT3Am-DvUQWDByHIxgmU1QdF4pXkhnht6AZJrbe105g_mgFP_pM7TCVt03HgwLRzFUNlEhAjsiQikV9rcz1Hrph1oH8Sv3oRtYzPb5LUYsP3kRceR3XkGqy_Zgh_WNPY3oTFw-asFNQ4bWox3bxGLBW1qaIg7jMNg9Jr2m37bCc4ljL8V2dKuSpP2ixQKM55vUZKkpTDhpH06PxMRvlz0BGzXBQBBhwzmtzu_9uby6LOqUx8mkHch8hN4xLcHfbiiRZZZNIwgH3Vg',
    attendees: 46,
  },
  {
    id: 'seed-3',
    title: 'Autumn Equinox Concert',
    date: '2026-03-28',
    time: '19:00',
    description: 'A special performance by the regional choir and folk orchestra. Free admission for the entire neighborhood.',
    category: 'Community Gathering',
    categoryColor: 'secondary-fixed',
    categoryTextColor: 'on-secondary-fixed',
    image: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBtOsuFEJksvmj8tAywNFdsMcx5suXuRuQvOJs5rNFSiPBfkld3S_QkDbEJTEfJIT_9A2q5l3c9HElAi73gbC32WY6LTOPSP5gxvUBsFP_hRvzb5tzGZoiP32kxSvzqAtO103G6EuBPXGqCfHr-BERu_i1VE_lNCVtGDBsFqnAo2XtT9aF3XjDWzyiwUOK5aXScZvxOAzah-MZRhbkwPU_XGJjEZRbh0jRSIx1HbVZmxaSEkY4Jt3j8b7CoRmklgO1SAQLWQeWQ2xo',
    attendees: 102,
  },
  {
    id: 'seed-4',
    title: 'Poetry Slam: Balkan Voices',
    date: '2026-04-05',
    time: '18:30',
    description: 'An evening celebrating the rich poetic tradition of the Balkans. Open mic for aspiring poets.',
    category: 'Literary Event',
    categoryColor: 'primary-fixed',
    categoryTextColor: 'on-primary-fixed',
    image: '',
    attendees: 30,
  },
  {
    id: 'seed-5',
    title: 'Kids Folk Art Class',
    date: '2026-04-12',
    time: '16:00',
    description: 'Creative workshop for children ages 6–12 to learn traditional Bulgarian art techniques: embroidery, woodcarving, and pottery.',
    category: 'Workshop',
    categoryColor: 'secondary-fixed',
    categoryTextColor: 'on-secondary-fixed',
    image: '',
    attendees: 20,
  },
];

// ─── Event Storage Helpers ──────────────────────────────────────────
function loadEvents() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored) {
    try { return JSON.parse(stored); } catch (e) { /* fall through */ }
  }
  // Seed on first visit
  localStorage.setItem(STORAGE_KEY, JSON.stringify(seedEvents));
  return [...seedEvents];
}

function saveEvents(events) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(events));
}

// ─── State ──────────────────────────────────────────────────────────
let allEvents = loadEvents();
let currentYear, currentMonth; // 0-indexed month
let selectedDate = null; // 'YYYY-MM-DD' or null (show all)

// ─── Calendar Rendering ─────────────────────────────────────────────
const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];
const DAY_LABELS = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];

function initCalendar() {
  const now = new Date();
  currentYear = now.getFullYear();
  currentMonth = now.getMonth();
  renderCalendar();
}

function renderCalendar() {
  const titleEl = document.getElementById('cal-title');
  const gridEl = document.getElementById('cal-grid');
  if (!titleEl || !gridEl) return;

  titleEl.textContent = `${MONTH_NAMES[currentMonth]} ${currentYear}`;

  // First day of month (0=Sun … 6=Sat) → convert to Monday-start
  const firstDay = new Date(currentYear, currentMonth, 1).getDay();
  const startOffset = (firstDay === 0 ? 6 : firstDay - 1); // Monday=0
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
  const daysInPrevMonth = new Date(currentYear, currentMonth, 0).getDate();

  // Build set of dates with events for this month
  const eventDates = new Set();
  allEvents.forEach((ev) => {
    const d = new Date(ev.date);
    if (d.getFullYear() === currentYear && d.getMonth() === currentMonth) {
      eventDates.add(d.getDate());
    }
  });

  const today = new Date();
  const todayDate =
    today.getFullYear() === currentYear && today.getMonth() === currentMonth
      ? today.getDate()
      : -1;

  let html = '';

  // Previous month trailing days
  for (let i = startOffset - 1; i >= 0; i--) {
    html += `<div class="cal-day outside">${daysInPrevMonth - i}</div>`;
  }

  // Current month days
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    const isToday = d === todayDate;
    const isSelected = selectedDate === dateStr;
    const hasEvent = eventDates.has(d);

    let classes = 'cal-day';
    if (isToday) classes += ' today';
    if (isSelected) classes += ' selected';

    html += `<div class="${classes}" data-date="${dateStr}" onclick="selectDate('${dateStr}')">
      ${d}
      ${hasEvent ? '<span class="event-dot"></span>' : ''}
    </div>`;
  }

  // Next month leading days — fill to complete the grid row
  const totalCells = startOffset + daysInMonth;
  const remaining = totalCells % 7 === 0 ? 0 : 7 - (totalCells % 7);
  for (let i = 1; i <= remaining; i++) {
    html += `<div class="cal-day outside">${i}</div>`;
  }

  gridEl.innerHTML = html;
}

function prevMonth() {
  currentMonth--;
  if (currentMonth < 0) { currentMonth = 11; currentYear--; }
  selectedDate = null;
  renderCalendar();
  renderEventList();
}

function nextMonth() {
  currentMonth++;
  if (currentMonth > 11) { currentMonth = 0; currentYear++; }
  selectedDate = null;
  renderCalendar();
  renderEventList();
}

function selectDate(dateStr) {
  if (selectedDate === dateStr) {
    // Deselect → show all
    selectedDate = null;
  } else {
    selectedDate = dateStr;
  }
  renderCalendar();
  renderEventList();
}

function showAll() {
  selectedDate = null;
  renderCalendar();
  renderEventList();
}

// ─── Event List Rendering ───────────────────────────────────────────
function renderEventList() {
  const container = document.getElementById('event-list');
  const filterInfo = document.getElementById('filter-info');
  if (!container) return;

  // Filter events
  let filtered = [...allEvents];
  if (selectedDate) {
    filtered = filtered.filter((ev) => ev.date === selectedDate);
  } else {
    // Show events for current month + future
    filtered = filtered.filter((ev) => {
      const d = new Date(ev.date);
      return (
        (d.getFullYear() === currentYear && d.getMonth() === currentMonth) ||
        d >= new Date()
      );
    });
  }

  // Sort by date
  filtered.sort((a, b) => new Date(a.date) - new Date(b.date));

  // Update filter info
  if (filterInfo) {
    if (selectedDate) {
      const dateObj = new Date(selectedDate + 'T00:00:00');
      const formatted = dateObj.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
      filterInfo.innerHTML = `
        <div class="flex items-center gap-3 mb-6 p-3 bg-primary/5 rounded-lg">
          <span class="material-symbols-outlined text-primary">filter_alt</span>
          <span class="text-sm font-medium text-on-surface">Showing events for <strong>${formatted}</strong></span>
          <button onclick="showAll()" class="ml-auto text-xs font-bold text-primary hover:underline">Show All</button>
        </div>
      `;
    } else {
      filterInfo.innerHTML = '';
    }
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <span class="material-symbols-outlined">event_busy</span>
        <p class="font-semibold text-on-surface mb-1">No events found</p>
        <p class="text-sm">${selectedDate ? 'No events on this date. Try another day or' : 'No upcoming events.'} <button onclick="showAll()" class="text-primary font-bold hover:underline">show all</button></p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered
    .map((ev) => {
      const dateObj = new Date(ev.date + 'T00:00:00');
      const monthStr = MONTH_NAMES[dateObj.getMonth()].substring(0, 3);
      const dayStr = dateObj.getDate();
      const yearStr = dateObj.getFullYear();
      const catColor = ev.categoryColor || 'primary-fixed';
      const catTextColor = ev.categoryTextColor || 'on-primary-fixed';

      return `
        <article class="bg-surface-container-lowest rounded-xl shadow-[0_12px_32px_rgba(25,28,30,0.06)] overflow-hidden flex flex-col md:flex-row group transition-all duration-300 hover:-translate-y-1">
          ${
            ev.image
              ? `<div class="md:w-64 h-48 md:h-auto overflow-hidden shrink-0">
                  <img class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" src="${ev.image}" alt="${ev.title}" />
                </div>`
              : `<div class="md:w-64 h-48 md:h-auto overflow-hidden shrink-0 bg-gradient-to-br from-primary/10 to-primary/5 flex items-center justify-center">
                  <span class="material-symbols-outlined text-primary/30" style="font-size:64px">event</span>
                </div>`
          }
          <div class="p-6 flex-1 flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-2 flex-wrap gap-2">
                <span class="px-3 py-1 bg-${catColor} text-${catTextColor} text-[10px] font-bold uppercase tracking-widest rounded-full">${ev.category}</span>
                <span class="text-xs font-medium text-on-surface-variant">${monthStr} ${dayStr}, ${yearStr} • ${ev.time}</span>
              </div>
              <h3 class="text-xl font-bold text-on-surface mb-2">${ev.title}</h3>
              <p class="text-sm text-on-surface-variant line-clamp-2">${ev.description}</p>
            </div>
            <div class="mt-6 flex items-center justify-between">
              <span class="text-xs font-medium text-on-surface-variant">${ev.attendees || 0} attending</span>
              <button class="text-primary font-bold text-sm flex items-center gap-1 group/btn hover:underline">
                Learn More
                <span class="material-symbols-outlined text-sm group-hover/btn:translate-x-1 transition-transform">arrow_forward</span>
              </button>
            </div>
          </div>
        </article>
      `;
    })
    .join('');
}

// ─── Create Event Modal ─────────────────────────────────────────────
function openCreateModal() {
  const modal = document.getElementById('create-event-modal');
  if (modal) {
    modal.classList.add('open');
    document.body.classList.add('modal-open');

    // Pre-fill date if one is selected on calendar
    if (selectedDate) {
      const dateInput = document.getElementById('event-date');
      if (dateInput) dateInput.value = selectedDate;
    }
  }
}

function closeCreateModal() {
  const modal = document.getElementById('create-event-modal');
  if (modal) {
    modal.classList.remove('open');
    document.body.classList.remove('modal-open');
  }
}

function handleCreateEvent(e) {
  e.preventDefault();

  const title = document.getElementById('event-title').value.trim();
  const date = document.getElementById('event-date').value;
  const time = document.getElementById('event-time').value;
  const desc = document.getElementById('event-desc').value.trim();

  // Simple validation
  if (!title || !date || !time) {
    alert('Please fill in at least the Title, Date, and Time.');
    return;
  }

  const newEvent = {
    id: 'usr-' + Date.now(),
    title,
    date,
    time,
    description: desc || 'No description provided.',
    category: 'Community Event',
    categoryColor: 'secondary-fixed',
    categoryTextColor: 'on-secondary-fixed',
    image: '',
    attendees: 1,
  };

  allEvents.push(newEvent);
  saveEvents(allEvents);

  // Reset form & close modal
  document.getElementById('create-event-form').reset();
  closeCreateModal();

  // Re-render
  renderCalendar();
  renderEventList();

  // Show success toast
  showToast('Event created successfully!');
}

function showToast(message) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'success-toast';
    document.body.appendChild(toast);
  }
  toast.innerHTML = `<span class="material-symbols-outlined filled">check_circle</span> ${message}`;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

// ─── Init ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initCalendar();
  renderEventList();

  // Wire up create-event form
  const form = document.getElementById('create-event-form');
  if (form) form.addEventListener('submit', handleCreateEvent);

  // Wire up modal close on overlay click
  const modal = document.getElementById('create-event-modal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeCreateModal();
    });
  }

  // ESC key closes modal
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeCreateModal();
  });
});
