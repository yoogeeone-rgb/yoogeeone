const wordmark = document.querySelector('.site-wordmark');
const fadeDistance = 100;
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

function updateWordmark() {
  const scrolled = Math.max(0, window.scrollY);
  const opacity = reduceMotion.matches
    ? Number(scrolled < fadeDistance)
    : Math.max(0, 1 - scrolled / fadeDistance);
  wordmark.style.opacity = opacity;
  wordmark.style.visibility = opacity === 0 ? 'hidden' : '';
}

updateWordmark();
window.addEventListener('scroll', updateWordmark, { passive: true });
window.addEventListener('pageshow', updateWordmark);
reduceMotion.addEventListener('change', updateWordmark);

const contact = document.querySelector('.contact-dialog');
const contactLink = document.querySelector('[data-contact-open]');
contactLink.setAttribute('aria-haspopup', 'dialog');
contactLink.addEventListener('click', (event) => {
  if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  contact.showModal();
});
contact.addEventListener('click', (event) => {
  if (event.target === contact) contact.close();
});
