/**
 * gallery.js — Галерия от Django API + lightbox
 */

function getApiBase() {
  const b = typeof window !== 'undefined' && window.CHITALISHTE_API_BASE;
  return (b && String(b).trim().replace(/\/$/, '')) || '';
}

function getApiCandidates() {
  const candidates = [];
  const configured = getApiBase();
  const origin =
    typeof window !== 'undefined' &&
    window.location &&
    window.location.origin &&
    window.location.origin !== 'null'
      ? window.location.origin.replace(/\/$/, '')
      : '';

  if (configured) candidates.push(configured);
  if (origin && origin !== configured) candidates.push(origin);

  // When previewing static files locally, Django usually runs on :8000.
  if (!configured || ['localhost', '127.0.0.1', ''].includes(window.location.hostname)) {
    ['http://127.0.0.1:8000', 'http://localhost:8000'].forEach((base) => {
      if (!candidates.includes(base)) candidates.push(base);
    });
  }

  return candidates;
}

function buildGalleryUrl(base) {
  return `${base}/api/gallery/`;
}

document.addEventListener('DOMContentLoaded', () => {
  const root = document.getElementById('gallery-lightbox');
  const lightboxImg = document.getElementById('gallery-lightbox-img');
  const caption = document.getElementById('gallery-lightbox-caption');
  const grid = document.getElementById('gallery-grid');
  const statusEl = document.getElementById('gallery-status');

  if (!root || !lightboxImg || !caption || !grid) return;

  function showStatus(msg, isError) {
    if (!statusEl) return;
    statusEl.textContent = msg;
    statusEl.classList.remove('hidden');
    statusEl.style.color = isError ? '#dc2626' : '';
  }

  function hideStatus() {
    statusEl?.classList.add('hidden');
  }

  function renderMessage(icon, title, text) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <span class="material-symbols-outlined">${icon}</span>
        <p class="font-semibold text-on-surface mb-1">${title}</p>
        <p class="text-sm">${text}</p>
      </div>
    `;
  }

  function openLightbox(src, text) {
    lightboxImg.src = src;
    lightboxImg.alt = text || '';
    caption.textContent = text || '';
    root.hidden = false;
    document.body.classList.add('modal-open');
    root.querySelector('.gallery-lightbox-close')?.focus();
  }

  function closeLightbox() {
    root.hidden = true;
    lightboxImg.src = '';
    document.body.classList.remove('modal-open');
  }

  grid.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-gallery-open]');
    if (!btn || !grid.contains(btn)) return;
    openLightbox(btn.dataset.src || '', btn.dataset.caption || '');
  });

  root.querySelectorAll('[data-gallery-close]').forEach((el) => {
    el.addEventListener('click', closeLightbox);
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !root.hidden) closeLightbox();
  });

  function renderTile(item) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'gallery-tile group';
    btn.setAttribute('data-gallery-open', '');
    btn.dataset.src = item.image_url;
    btn.dataset.caption = item.caption || '';

    const imgEl = document.createElement('img');
    imgEl.src = item.image_url;
    imgEl.alt = item.caption || '';
    imgEl.className = 'gallery-tile-img';
    imgEl.loading = 'lazy';

    const cap = document.createElement('span');
    cap.className = 'gallery-tile-caption';
    cap.textContent = item.caption || '';

    btn.appendChild(imgEl);
    btn.appendChild(cap);
    return btn;
  }

  showStatus('Зареждане на галерията…', false);

  async function fetchGallery() {
    const endpoints = getApiCandidates().map(buildGalleryUrl);
    let lastError = null;

    for (const endpoint of endpoints) {
      try {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        return await response.json();
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError || new Error('No reachable gallery endpoint');
  }

  fetchGallery()
    .then((data) => {
      hideStatus();
      const payload = data;
      const items = Array.isArray(payload) ? payload : payload?.results || [];
      grid.innerHTML = '';

      if (items.length === 0) {
        renderMessage(
          'imagesmode',
          'Няма качени снимки',
          'Добавете изображения от админ панела и се уверете, че са маркирани като публикувани.'
        );
        return;
      }

      items.forEach((item) => grid.appendChild(renderTile(item)));
    })
    .catch(() => {
      showStatus(
        'Неуспешно зареждане на галерията. Проверете дали Django API работи и дали CHITALISHTE_API_BASE сочи към правилния сървър.',
        true
      );
      renderMessage(
        'wifi_off',
        'Галерията не можа да се зареди',
        'Ако сте в локална среда, стартирайте Django с `python manage.py runserver` в `/backend`.'
      );
    });
});
