/**
 * home.js — Home page logic for Chitalishte Connect
 * Handles: Dynamic news feed rendering, Like button toggle
 */

// ─── Mock Feed Data ─────────────────────────────────────────────────
const feedData = [
  {
    id: 1,
    title: 'Upcoming Folk Workshop',
    category: 'event',
    icon: 'event',
    tag: '12 Members attending',
    tagColor: 'primary',
    borderColor: 'border-[#0058bc]',
    iconBg: 'bg-[#0070eb]',
    timestamp: 'Posted 2 hours ago • Sofia Center',
    description:
      'Registration is now open for our Autumn Folk Dance intensive. Learn the intricacies of the "Graovsko Horo" from Master Kalin Ivanov. All skill levels welcome!',
    image:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuAzVQtxd202JzkSyNKD53pAws9pTrbFGwEc9uIa4gCx0wjU1_I3A-6h2hUR7WQdeKxcYpqGkxxnMOclX2LUhIbT8W6g6mxh7CODSMbzWA1s0usAYXqcEKWfef8NUok1bRfUkoTV5ROSwRABszm2q6EApV68zkBDgirJcSIxTK94Sn_lDxE5sPt31vGTnjCPY1kGEWOw9P6WyPvlEH1aKC20s0TLRYdexBqcucyoYb1UCjs121Xa3JZV-fDa6N1Xr9yvgjSw_4Z7iHw',
    imageAlt: 'Interior of a bright dance studio with wooden floors',
    likes: 5,
    liked: false,
  },
  {
    id: 2,
    title: 'New Archive Donation',
    category: 'archive',
    icon: 'auto_stories',
    tag: 'Archive Update',
    tagColor: 'secondary',
    borderColor: 'border-[#365ca7]',
    iconBg: 'bg-[#8cafff]',
    timestamp: 'Posted yesterday • Library Archive',
    description:
      'We are honored to receive a collection of rare 19th-century manuscripts from the Dimitrov family. These will be digitized and available for public viewing starting next month.',
    image: '',
    imageAlt: '',
    likes: 8,
    liked: false,
  },
  {
    id: 3,
    title: 'Summer Reading Program Results',
    category: 'library',
    icon: 'menu_book',
    tag: 'Library News',
    tagColor: 'tertiary',
    borderColor: 'border-[#0058be]',
    iconBg: 'bg-[#2b71de]',
    timestamp: 'Posted 3 days ago • Library',
    description:
      'Our summer reading program was a great success! Over 150 children participated, reading a total of 2,300 books. Special thanks to all the volunteer readers who made storytime magical.',
    image: '',
    imageAlt: '',
    likes: 22,
    liked: false,
  },
  {
    id: 4,
    title: 'Theater Renovation Update',
    category: 'news',
    icon: 'construction',
    tag: 'Renovation',
    tagColor: 'secondary',
    borderColor: 'border-[#365ca7]',
    iconBg: 'bg-[#8cafff]',
    timestamp: 'Posted last week • Administration',
    description:
      'Phase 2 of our historic theater renovation is 70% complete. The new seating has been installed and acoustic panels are being fitted. We expect to reopen the main hall by December.',
    image:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuBfh4zSeSvypkZJedrl_eHaCSn_SN4L8wAXz8FxnwOXGFy7_cK7Smzuwn01S6i3h68DCs5eaJUIY2GySYX-usZ_kCqabqR8ZSM9SWmZ8M1b0wk4GaIr1AqxLVKauyTgfv35wvf8nZSrjEOZxAB9pMFlWjkwdYw83tWLgNJ1Drzhxo7KQXg-tFlmSKmkUBOsRLAxOXs11u3Y4IFZOXSS5TCHvsTaTxbR356czZVrgbKVi4-HyA4wKkViH758yFI_qBFuPClCVvugyUU',
    imageAlt: 'Traditional Bulgarian folk scene',
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
            <span class="like-label">${item.liked ? 'Liked' : 'Interested'}</span>
            <span class="like-count text-xs opacity-70">(${item.likes})</span>
          </button>
          <button class="like-btn">
            <span class="material-symbols-outlined text-lg">share</span>
            Share
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
      ? 'Liked'
      : 'Interested';
    btn.querySelector('.like-count').textContent = `(${item.likes})`;
  }
}

// ─── Init ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', renderFeed);
