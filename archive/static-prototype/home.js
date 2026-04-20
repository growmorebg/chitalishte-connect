/**
 * home.js — Home page logic for Chitalishte Connect
 * Handles: Dynamic news feed rendering, Like button toggle
 */

// ─── Mock Feed Data ─────────────────────────────────────────────────
const feedData = [
  {
    id: 1,
    title: 'Предстояща фолклорна работилница',
    category: 'event',
    icon: 'event',
    tag: '12 члена ще присъстват',
    tagColor: 'primary',
    borderColor: 'border-[#0058bc]',
    iconBg: 'bg-[#0070eb]',
    timestamp: 'Публикувано преди 2 часа • София център',
    description:
      'Записването за есенния интензивен курс по народни танци е отворено. Научете нюансите на „Граовско хоро“ с майстор Калин Иванов. Подходящо за всички нива!',
    image:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuAzVQtxd202JzkSyNKD53pAws9pTrbFGwEc9uIa4gCx0wjU1_I3A-6h2hUR7WQdeKxcYpqGkxxnMOclX2LUhIbT8W6g6mxh7CODSMbzWA1s0usAYXqcEKWfef8NUok1bRfUkoTV5ROSwRABszm2q6EApV68zkBDgirJcSIxTK94Sn_lDxE5sPt31vGTnjCPY1kGEWOw9P6WyPvlEH1aKC20s0TLRYdexBqcucyoYb1UCjs121Xa3JZV-fDa6N1Xr9yvgjSw_4Z7iHw',
    imageAlt: 'Интериор на светла танцова зала с дървен под',
    likes: 5,
    liked: false,
  },
  {
    id: 2,
    title: 'Ново дарение за архива',
    category: 'archive',
    icon: 'auto_stories',
    tag: 'Актуализация от архива',
    tagColor: 'secondary',
    borderColor: 'border-[#365ca7]',
    iconBg: 'bg-[#8cafff]',
    timestamp: 'Публикувано вчера • Архив на библиотеката',
    description:
      'С гордост приемаме колекция от редки ръкописи от XIX век от семейство Димитрови. Ще бъдат дигитализирани и достъпни за публика от следващия месец.',
    image: '',
    imageAlt: '',
    likes: 8,
    liked: false,
  },
  {
    id: 3,
    title: 'Резултати от лятната читателска програма',
    category: 'library',
    icon: 'menu_book',
    tag: 'Новини от библиотеката',
    tagColor: 'tertiary',
    borderColor: 'border-[#0058be]',
    iconBg: 'bg-[#2b71de]',
    timestamp: 'Публикувано преди 3 дни • Библиотека',
    description:
      'Лятната ни читателска програма беше голям успех! Над 150 деца участваха и прочетоха общо 2300 книги. Благодарим на всички доброволци, които направиха времето за приказки магично.',
    image: '',
    imageAlt: '',
    likes: 22,
    liked: false,
  },
  {
    id: 4,
    title: 'Актуализация за ремонта на театъра',
    category: 'news',
    icon: 'construction',
    tag: 'Ремонт',
    tagColor: 'secondary',
    borderColor: 'border-[#365ca7]',
    iconBg: 'bg-[#8cafff]',
    timestamp: 'Публикувано миналата седмица • Администрация',
    description:
      'Втора фаза от ремонта на историческия ни театър е завършена на 70%. Новите места са монтирани, монтират се акустични панели. Очакваме повторно отваряне на голямата зала до декември.',
    image:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuBfh4zSeSvypkZJedrl_eHaCSn_SN4L8wAXz8FxnwOXGFy7_cK7Smzuwn01S6i3h68DCs5eaJUIY2GySYX-usZ_kCqabqR8ZSM9SWmZ8M1b0wk4GaIr1AqxLVKauyTgfv35wvf8nZSrjEOZxAB9pMFlWjkwdYw83tWLgNJ1Drzhxo7KQXg-tFlmSKmkUBOsRLAxOXs11u3Y4IFZOXSS5TCHvsTaTxbR356czZVrgbKVi4-HyA4wKkViH758yFI_qBFuPClCVvugyUU',
    imageAlt: 'Традиционна българска фолклорна сцена',
    likes: 15,
    liked: false,
  },
];

// ─── Render Feed ────────────────────────────────────────────────────
function renderFeed() {
  const feedContainer = document.getElementById('feed-container');
  if (!feedContainer) return;

  feedContainer.innerHTML = feedData
    .map(
      (item) => `
    <article class="bg-surface-container-lowest border-t-4 ${item.borderColor} rounded-lg p-6 mb-6 hover:shadow-md transition-shadow">
      <!-- Header -->
      <div class="flex items-center gap-4 mb-4">
        <div class="w-12 h-12 rounded-full ${item.iconBg} flex items-center justify-center text-white">
          <span class="material-symbols-outlined">${item.icon}</span>
        </div>
        <div>
          <h4 class="font-bold text-on-surface">${item.title}</h4>
          <span class="text-xs text-on-surface-variant font-medium">${item.timestamp}</span>
        </div>
      </div>

      <!-- Body -->
      <p class="text-on-surface-variant mb-6 leading-relaxed">${item.description}</p>

      ${
        item.image
          ? `<div class="rounded-xl overflow-hidden mb-6 h-64 bg-surface-container">
              <img alt="${item.imageAlt}" class="w-full h-full object-cover" src="${item.image}" />
            </div>`
          : ''
      }

      <!-- Footer -->
      <div class="flex items-center justify-between pt-4 border-t border-outline-variant/20">
        <div class="flex gap-3">
          <button
            class="like-btn ${item.liked ? 'liked' : ''}"
            data-id="${item.id}"
            onclick="toggleLike(${item.id})"
            id="like-btn-${item.id}"
          >
            <span class="material-symbols-outlined text-lg">thumb_up</span>
            <span class="like-label">${item.liked ? 'Харесано' : 'Интересува ме'}</span>
            <span class="like-count text-xs opacity-70">(${item.likes})</span>
          </button>
          <button class="like-btn">
            <span class="material-symbols-outlined text-lg">share</span>
            Сподели
          </button>
        </div>
        <span class="text-xs font-bold text-${item.tagColor} px-3 py-1 bg-${item.tagColor}/10 rounded-full hidden sm:inline">${item.tag}</span>
      </div>
    </article>
  `
    )
    .join('');
}

// ─── Toggle Like ────────────────────────────────────────────────────
function toggleLike(id) {
  const item = feedData.find((f) => f.id === id);
  if (!item) return;

  item.liked = !item.liked;
  item.likes += item.liked ? 1 : -1;

  // Update only the affected button for smooth animation
  const btn = document.getElementById(`like-btn-${id}`);
  if (btn) {
    btn.classList.toggle('liked', item.liked);
    btn.querySelector('.like-label').textContent = item.liked
      ? 'Харесано'
      : 'Интересува ме';
    btn.querySelector('.like-count').textContent = `(${item.likes})`;
  }
}

// ─── Init ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', renderFeed);
