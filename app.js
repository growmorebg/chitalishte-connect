/**
 * app.js — Shared logic for Chitalishte Connect
 * Handles: Hamburger menu toggle, active nav detection
 */

document.addEventListener('DOMContentLoaded', () => {
  // ─── Hamburger Menu Toggle ────────────────────────────────────────
  const hamburgerBtn = document.getElementById('hamburger-btn');
  const mobileMenu = document.getElementById('mobile-menu');

  if (hamburgerBtn && mobileMenu) {
    hamburgerBtn.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.contains('open');
      if (isOpen) {
        // Close: fade out first, then hide
        mobileMenu.style.opacity = '0';
        mobileMenu.style.transform = 'translateY(-10px)';
        setTimeout(() => {
          mobileMenu.classList.remove('open');
          mobileMenu.style.removeProperty('opacity');
          mobileMenu.style.removeProperty('transform');
        }, 300);
        hamburgerBtn.classList.remove('active');
      } else {
        // Open: show then animate in
        mobileMenu.classList.add('open');
        // Force reflow to trigger animation
        void mobileMenu.offsetHeight;
        mobileMenu.style.opacity = '1';
        mobileMenu.style.transform = 'translateY(0)';
        hamburgerBtn.classList.add('active');
      }
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (
        mobileMenu.classList.contains('open') &&
        !mobileMenu.contains(e.target) &&
        !hamburgerBtn.contains(e.target)
      ) {
        hamburgerBtn.click();
      }
    });

    // Close menu on window resize to desktop
    window.addEventListener('resize', () => {
      if (window.innerWidth >= 1024 && mobileMenu.classList.contains('open')) {
        mobileMenu.classList.remove('open');
        hamburgerBtn.classList.remove('active');
        mobileMenu.style.removeProperty('opacity');
        mobileMenu.style.removeProperty('transform');
      }
    });
  }

  // ─── Active Nav Detection ─────────────────────────────────────────
  // Determine current page from the filename
  const path = window.location.pathname;
  let currentPage = 'home';
  if (path.includes('events')) currentPage = 'events';
  else if (path.includes('contact')) currentPage = 'contact';

  // Desktop nav links
  document.querySelectorAll('[data-nav]').forEach((link) => {
    const navTarget = link.getAttribute('data-nav');
    if (navTarget === currentPage) {
      link.classList.add('text-[#1877F2]', 'border-b-4', 'border-[#1877F2]');
      link.classList.remove(
        'text-slate-600',
        'dark:text-slate-400',
        'hover:bg-slate-100',
        'dark:hover:bg-slate-800'
      );
    }
  });

  // Mobile nav links
  document.querySelectorAll('[data-mobile-nav]').forEach((link) => {
    const navTarget = link.getAttribute('data-mobile-nav');
    if (navTarget === currentPage) {
      link.classList.add('active');
    }
  });
});
