const menu = document.querySelector('#site-menu');
const menuButton = document.querySelector('.menu-open');

menuButton.addEventListener('click', () => {
  menu.showModal();
  menuButton.setAttribute('aria-expanded', 'true');
});

menu.addEventListener('close', () => {
  menuButton.setAttribute('aria-expanded', 'false');
});

menu.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => menu.close());
});

const scenes = [...document.querySelectorAll('.studio-stack .scene')];
const incomingScenes = scenes.slice(1);
const hero = document.querySelector('.hero, .project-hero');
const opening = document.querySelector('.opening');
const galleries = [...document.querySelectorAll('.moving-gallery')];
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let scrollFrame = 0;

opening?.classList.add('has-layer-motion');

function updateScrollEffects() {
  scrollFrame = 0;
  if (reducedMotion.matches) return;

  const viewportBottom = document.documentElement.clientHeight;
  if (hero) {
    const height = hero.getBoundingClientRect().height;
    const top = (opening ?? hero).getBoundingClientRect().top;
    const progress = Math.max(0, Math.min(-top / height, 1));
    hero.style.setProperty('--hero-progress', progress);
    hero.style.setProperty('--hero-offset', `${progress * height * (opening ? -.14 : .05)}px`);
  }
  if (incomingScenes.length) {
    const pinTop = Number.parseFloat(getComputedStyle(scenes[0]).top);
    const travel = viewportBottom - pinTop;
    if (travel <= 0) return;

    const progress = incomingScenes.map((scene) => {
      const distance = viewportBottom - scene.getBoundingClientRect().top;
      return Math.max(0, Math.min(distance / travel, 1));
    });
    progress.forEach((amount, index) => {
      scenes[index].style.setProperty('--scene-progress', amount);
    });
  }
  const offsets = galleries.map((gallery) => {
    const { top, height } = gallery.getBoundingClientRect();
    const progress = Math.max(0, Math.min((viewportBottom - top) / (viewportBottom + height), 1));
    const distance = gallery.scrollWidth - gallery.clientWidth;
    return distance * (gallery.hasAttribute('data-reverse') ? 1 - progress : progress);
  });
  galleries.forEach((gallery, index) => {
    gallery.scrollLeft = offsets[index];
  });
}

function requestScrollUpdate() {
  if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScrollEffects);
}

window.addEventListener('scroll', requestScrollUpdate, { passive: true });
window.addEventListener('resize', requestScrollUpdate);
window.addEventListener('pageshow', requestScrollUpdate);
reducedMotion.addEventListener('change', requestScrollUpdate);
requestScrollUpdate();

document.querySelectorAll('[data-roll]').forEach((label) => {
  const clip = document.createElement('span');
  clip.className = 'roll-window';
  const track = document.createElement('span');
  track.className = 'roll-track';
  const text = document.createElement('span');
  text.textContent = label.textContent.trim();
  const copy = text.cloneNode(true);
  copy.setAttribute('aria-hidden', 'true');
  track.append(text, copy);
  clip.append(track);
  label.replaceChildren(clip);
});

const pointerAvailable = window.matchMedia('(hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)');
const ring = document.createElement('div');
ring.className = 'pointer-ring';
ring.setAttribute('aria-hidden', 'true');
document.body.append(ring);

function resetPointer() {
  document.documentElement.classList.toggle('pointer-enabled', pointerAvailable.matches);
  ring.classList.remove('visible', 'has-label');
}

resetPointer();
pointerAvailable.addEventListener('change', resetPointer);
document.addEventListener('pointermove', (event) => {
  if (!pointerAvailable.matches || event.pointerType === 'touch') return;
  const target = event.target.closest('[data-pointer]');
  ring.classList.toggle('visible', Boolean(target));
  if (!target) return;
  const label = target.dataset.pointer;
  ring.textContent = label;
  ring.classList.toggle('has-label', Boolean(label));
  ring.style.transform = `translate(${event.clientX}px, ${event.clientY}px) translate(-50%, -50%)`;
}, { passive: true });
document.addEventListener('pointerout', (event) => {
  if (!event.relatedTarget) ring.classList.remove('visible');
});
window.addEventListener('scroll', () => ring.classList.remove('visible'), { passive: true });
