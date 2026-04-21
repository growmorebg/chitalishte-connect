/**
 * contact.js — Contact page logic for Chitalishte Connect
 * Handles: Form validation, simulated submission with loading state, success toast
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('contact-form');
  const submitBtn = document.getElementById('submit-btn');
  const submitLabel = document.getElementById('submit-label');
  const submitIcon = document.getElementById('submit-icon');

  if (!form) return;

  // ─── Field references ─────────────────────────────────────────────
  const fields = {
    name: {
      input: document.getElementById('field-name'),
      error: document.getElementById('error-name'),
      validate: (val) => val.trim().length > 0,
      message: 'Моля, въведете име.',
    },
    email: {
      input: document.getElementById('field-email'),
      error: document.getElementById('error-email'),
      validate: (val) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val.trim()),
      message: 'Моля, въведете валиден имейл адрес.',
    },
    message: {
      input: document.getElementById('field-message'),
      error: document.getElementById('error-message'),
      validate: (val) => val.trim().length > 0,
      message: 'Моля, въведете съобщение.',
    },
  };

  // ─── Real-time validation on blur ─────────────────────────────────
  Object.values(fields).forEach(({ input, error, validate, message }) => {
    if (!input) return;

    // Validate on blur
    input.addEventListener('blur', () => {
      const isValid = validate(input.value);
      toggleError(input, error, isValid, message);
    });

    // Clear error when user starts typing
    input.addEventListener('input', () => {
      if (input.parentElement.classList.contains('error')) {
        toggleError(input, error, true, '');
      }
    });
  });

  // ─── Toggle error state ───────────────────────────────────────────
  function toggleError(input, errorEl, isValid, message) {
    const wrapper = input.closest('.form-field');
    if (!wrapper || !errorEl) return;

    if (isValid) {
      wrapper.classList.remove('error');
      errorEl.classList.remove('visible');
      input.style.boxShadow = '';
    } else {
      wrapper.classList.add('error');
      errorEl.textContent = message;
      errorEl.classList.add('visible');
      input.style.boxShadow = '0 0 0 2px #ba1a1a';
    }
  }

  // ─── Form submission ──────────────────────────────────────────────
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    // Validate all fields
    let allValid = true;
    Object.values(fields).forEach(({ input, error, validate, message }) => {
      if (!input) return;
      const isValid = validate(input.value);
      toggleError(input, error, isValid, message);
      if (!isValid) allValid = false;
    });

    if (!allValid) {
      // Focus first invalid field
      const firstInvalid = form.querySelector('.form-field.error input, .form-field.error textarea');
      if (firstInvalid) firstInvalid.focus();
      return;
    }

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.style.opacity = '0.7';
    submitLabel.textContent = 'Изпращане...';
    if (submitIcon) submitIcon.innerHTML = '<span class="btn-spinner"></span>';

    // Simulate network delay
    setTimeout(() => {
      // Reset button
      submitBtn.disabled = false;
      submitBtn.style.opacity = '1';
      submitLabel.textContent = 'Изпрати запитване';
      if (submitIcon) submitIcon.innerHTML = '<span class="material-symbols-outlined text-lg">send</span>';

      // Clear form
      form.reset();

      // Show success toast
      showSuccessToast('Съобщението е изпратено успешно!');
    }, 1500);
  });

  // ─── Success Toast ────────────────────────────────────────────────
  function showSuccessToast(message) {
    let toast = document.getElementById('contact-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'contact-toast';
      toast.className = 'success-toast';
      document.body.appendChild(toast);
    }
    toast.innerHTML = `<span class="material-symbols-outlined filled">check_circle</span> ${message}`;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 4000);
  }
});
