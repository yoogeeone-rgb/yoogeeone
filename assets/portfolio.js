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
