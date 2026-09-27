(() => {
  'use strict';

  const gallery = document.querySelector('.illustration-gallery');
  if (!gallery) return;

  const works = Array.from(gallery.querySelectorAll('.gallery-work'));
  const filters = gallery.querySelector('.gallery-filters');
  const count = gallery.querySelector('[data-gallery-count]');
  const viewer = document.querySelector('.gallery-viewer');
  const image = viewer.querySelector('.viewer-image');
  const title = viewer.querySelector('#viewer-title');
  const number = viewer.querySelector('[data-viewer-number]');
  const position = viewer.querySelector('[data-viewer-position]');
  const previous = viewer.querySelector('.viewer-previous');
  const next = viewer.querySelector('.viewer-next');
  let currentIndex = 0;
  let returnFocus;

  const visibleLinks = () => works
    .filter(work => !work.hidden)
    .map(work => work.querySelector('.gallery-image-link'));

  filters.hidden = false;
  filters.addEventListener('click', event => {
    const button = event.target.closest('button[data-filter]');
    if (!button) return;
    filters.querySelectorAll('button').forEach(filter => {
      const active = filter === button;
      filter.classList.toggle('is-active', active);
      filter.setAttribute('aria-pressed', String(active));
    });
    works.forEach(work => {
      work.hidden = button.dataset.filter !== 'all' && work.dataset.category !== button.dataset.filter;
    });
    count.textContent = visibleLinks().length;
  });

  // The image links remain usable when native dialogs are unavailable.
  if (typeof viewer.showModal !== 'function') return;

  function showWork(index) {
    const links = visibleLinks();
    currentIndex = Math.max(0, Math.min(index, links.length - 1));
    const link = links[currentIndex];
    image.src = link.href;
    image.alt = link.dataset.title;
    title.textContent = link.dataset.title;
    number.textContent = link.dataset.number;
    position.textContent = `${currentIndex + 1} / ${links.length}`;
    previous.disabled = currentIndex === 0;
    next.disabled = currentIndex === links.length - 1;
  }

  gallery.addEventListener('click', event => {
    const link = event.target.closest('.gallery-image-link');
    if (!link || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    returnFocus = link;
    showWork(visibleLinks().indexOf(link));
    viewer.showModal();
    document.body.classList.add('gallery-viewer-open');
    viewer.querySelector('.viewer-close').focus();
  });

  viewer.querySelector('.viewer-close').addEventListener('click', () => viewer.close());
  previous.addEventListener('click', () => showWork(currentIndex - 1));
  next.addEventListener('click', () => showWork(currentIndex + 1));
  viewer.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      showWork(currentIndex + (event.key === 'ArrowLeft' ? -1 : 1));
    }
  });
  viewer.addEventListener('close', () => {
    document.body.classList.remove('gallery-viewer-open');
    image.removeAttribute('src');
    if (returnFocus) returnFocus.focus({ preventScroll: true });
  });
})();
