// AM Pop desktop scatter, mobile layout, and photo zoom.
(function (w, d) {
  'use strict';
  var MOBILE = '(max-width: 1024px)';
  var mq = w.matchMedia(MOBILE);
  var each = function (l, f) { Array.prototype.forEach.call(l || [], f); };
  var reduce = w.matchMedia('(prefers-reduced-motion: reduce)');

  function rng(seed) { // mulberry32
    return function () {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  var visitSeed = Math.floor(Math.random() * 1e9);

  function num(name, fallback) {
    var v = parseFloat(w.getComputedStyle(d.documentElement).getPropertyValue(name));
    return isNaN(v) ? fallback : v;
  }

  function grids() { return d.querySelectorAll('[data-am-type="scatter"] .am-grid:not(.am-grid--priority)'); }

  function ratioOf(li) {
    var img = li.querySelector('.am-card__img');
    return img ? Number(img.getAttribute('height')) / Number(img.getAttribute('width')) : 1.25;
  }

  function layout() {
    var shuffle = d.body.getAttribute('data-am-pop-shuffle') === 'random';
    each(grids(), function (grid) {
      var items = grid.querySelectorAll(':scope > li');
      var rand = rng(shuffle ? visitSeed : 7);
      if (mq.matches) {
        grid.style.height = '';
        each(items, function (li, i) {
          li.style.left = li.style.top = li.style.width = '';
          li.style.setProperty('--mw', Math.round(82 + rand() * 18) + '%');
          li.style.setProperty('--mj', rand() < .5 ? 'start' : 'end');
          li.style.setProperty('--mdy', (i % 2 ? Math.round(10 + rand() * 50) : Math.round(rand() * 20)) + 'px');
        });
        grid.classList.add('is-laid');
        return;
      }
      var W = grid.clientWidth;
      if (!W) return;
      var scale = num('--am-pop-size', 1);
      var gap = num('--am-pop-gap', .03) * W;
      // sizes: x screen width (1440px screen: about 100-245px). Taken from a shuffled bag so every size
      // comes up equally often and the same size rarely sits twice in a row
      var SIZES = [.07, .085, .1, .115, .135, .17];
      var bag = [];
      function nextSize() {
        if (!bag.length) {
          bag = SIZES.slice();
          for (var b = bag.length - 1; b > 0; b--) { var r = Math.floor(rand() * (b + 1)), tmp = bag[b]; bag[b] = bag[r]; bag[r] = tmp; }
        }
        return bag.pop();
      }
      // the width is cut into 12 thin lanes; each photo drops into the lowest free place
      // (nearly) (so the screen fills up evenly but never in straight rows), with a little air at the sides.
      // Photos landing near the middle come out bigger (up to x 1.5) and the middle is slightly preferred,
      // so the centre of the screen does not look empty
      var N = 12, lane = W / N, air = lane * .22, sky = [], i, j;
      for (j = 0; j < N; j++) sky[j] = 0;
      function fit(w0) {
        var sp = Math.min(N, Math.ceil((w0 + air) / lane));
        return { w: Math.min(w0, sp * lane - air), span: sp };
      }
      each(items, function (li) {
        var base = Math.min(W * nextSize() * scale, W * .4);
        var best = -1, bestY = Infinity, bestScore = Infinity, bestFit = null;
        // every lane start is tried; a little random weight keeps it from becoming a neat masonry grid
        for (var s = 0; s < N; s++) {
          var f0 = fit(base);
          var mid = (s + f0.span / 2) / N;                       // 0 = left edge, .5 = centre, 1 = right edge
          var cen = Math.max(0, 1 - Math.abs(mid - .5) * 2.4);   // 1 in the middle, 0 near the edges
          var ft = fit(Math.min(base * (1 + .5 * cen * cen), W * .4));
          if (s + ft.span > N) continue;
          var y0 = 0;
          for (j = s; j < s + ft.span; j++) y0 = Math.max(y0, sky[j]);
          var score = y0 - cen * W * .02 + rand() * W * .04;
          if (score < bestScore) { bestScore = score; bestY = y0; best = s; bestFit = ft; }
        }
        if (!bestFit) { bestFit = fit(base); best = 0; bestY = 0; for (j = 0; j < bestFit.span; j++) bestY = Math.max(bestY, sky[j]); }
        var iw = bestFit.w, span = bestFit.span;
        // inside its lanes the photo leans toward the middle of the screen (the air goes to the outer side)
        var lean = (best + span / 2) / N < .5 ? .55 + rand() * .45 : rand() * .45;
        var x = best * lane + air / 2 + lean * (span * lane - air - iw);
        var y = bestY + rand() * W * .015;
        var ih = iw * ratioOf(li);
        li.style.left = Math.round(x) + 'px';
        li.style.top = Math.round(y) + 'px';
        li.style.width = Math.round(iw) + 'px';
        for (j = best; j < best + span; j++) sky[j] = y + ih + gap;
      });
      var H = 0;
      for (j = 0; j < N; j++) H = Math.max(H, sky[j]);
      grid.style.height = Math.round(H - gap) + 'px';
      grid.classList.add('is-laid');
    });
  }

  var lt;
  function relayout() { clearTimeout(lt); lt = setTimeout(layout, 60); }

  /* ---------- zoom ---------- */
  var box, img, closeButton, trigger, card = null, busy = false;

  function cards() {
    return Array.from(d.querySelectorAll('[data-am-type="scatter"] .am-grid > li'));
  }

  function fill(li) {
    var thumb = li.querySelector('.am-card__img');
    img.alt = thumb.alt;
    img.width = Number(thumb.dataset.fullWidth);
    img.height = Number(thumb.dataset.fullHeight);
    img.src = thumb.closest('a').href;
  }

  function flip(from, done) { // animate the large photo from the rectangle "from" to its own place (or back)
    if (reduce.matches || !from) { done && done(); return; }
    var to = img.getBoundingClientRect();
    if (!to.width) { done && done(); return; }
    var s = from.width / to.width;
    img.style.transition = 'none';
    img.style.transform = 'translate(' + (from.left - to.left) + 'px,' + (from.top - to.top) + 'px) scale(' + s + ')';
    img.getBoundingClientRect();
    img.style.transition = '';
    img.style.transform = '';
    setTimeout(function () { done && done(); }, 520);
  }

  function thumbRect(li) {
    var t = li && li.querySelector('.am-card__img');
    return t ? t.getBoundingClientRect() : null;
  }

  function open(li) {
    if (busy) return;
    busy = true;
    card = li;
    trigger = li.querySelector('a');
    fill(li);
    box.classList.remove('is-done');
    box.classList.add('is-open');
    box.setAttribute('aria-hidden', 'false');
    d.documentElement.classList.add('am-pop-zoomed');
    d.getElementById('wrap').inert = true;
    closeButton.focus({ preventScroll: true });
    var start = function () {
      img.onload = img.onerror = null;
      li.classList.add('is-zoomed');
      flip(thumbRect(li), function () { box.classList.add('is-done'); busy = false; });
    };
    if (img.complete && img.naturalWidth) start();
    else { img.onload = start; img.onerror = start; }
  }

  function close() {
    if (!card || busy) return;
    busy = true;
    var li = card;
    box.classList.remove('is-done');
    var r = thumbRect(li);
    var end = function () {
      box.classList.remove('is-open');
      d.documentElement.classList.remove('am-pop-zoomed');
      li.classList.remove('is-zoomed');
      img.style.transition = 'none';
      img.style.transform = '';
      card = null;
      busy = false;
      d.getElementById('wrap').inert = false;
      trigger.focus({ preventScroll: true });
      box.setAttribute('aria-hidden', 'true');
    };
    if (reduce.matches || !r || !r.width) { end(); return; }
    var to = img.getBoundingClientRect();
    img.style.transform = 'translate(' + (r.left - to.left) + 'px,' + (r.top - to.top) + 'px) scale(' + (r.width / to.width) + ')';
    box.classList.add('is-closing');
    setTimeout(function () { box.classList.remove('is-closing'); end(); }, 480);
  }

  function step(dir) {
    if (!card || busy) return;
    var list = cards(), i = list.indexOf(card) + dir;
    if (i < 0 || i >= list.length) return;
    card.classList.remove('is-zoomed');
    card = list[i];
    card.classList.add('is-zoomed');
    fill(card);
  }

  function bindZoom() {
    box = d.querySelector('[data-am-pop-zoom]');
    if (!box) return;
    d.body.appendChild(box); // out of the section, above the menu bar
    img = box.querySelector('.am-pop-zoom__img');
    closeButton = box.querySelector('.am-pop-zoom__btn--close');

    d.querySelector('#portfolio').addEventListener('click', function (e) {
      var link = e.target.closest('.am-card a');
      if (!link || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      open(link.closest('.am-card'));
    });

    var touchStart;
    img.addEventListener('touchstart', function (event) {
      touchStart = event.changedTouches[0];
    }, { passive: true });
    img.addEventListener('touchend', function (event) {
      if (!touchStart) return;
      var end = event.changedTouches[0];
      var dx = end.clientX - touchStart.clientX;
      var dy = end.clientY - touchStart.clientY;
      touchStart = null;
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) {
        event.preventDefault();
        step(dx > 0 ? -1 : 1);
      }
    });
    img.addEventListener('touchcancel', function () { touchStart = null; });
    box.addEventListener('click', function (e) {
      if (e.target.closest('[data-am-pop-prev]')) return step(-1);
      if (e.target.closest('[data-am-pop-next]')) return step(1);
      if (e.target === box || e.target.closest('.am-pop-zoom__btn--close')) close();
    });

    d.addEventListener('keydown', function (e) {
      if (!card) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowRight') step(1);
      else if (e.key === 'ArrowLeft') step(-1);
      else if (e.key === 'Tab') {
        var controls = Array.from(box.querySelectorAll('button')).filter(function (button) {
          return button.getClientRects().length;
        });
        var end = e.shiftKey ? controls[0] : controls[controls.length - 1];
        if (d.activeElement === end) {
          e.preventDefault();
          (e.shiftKey ? controls[controls.length - 1] : controls[0]).focus();
        }
      }
    });
  }

  function init() {
    layout();
    bindZoom();
    w.addEventListener('resize', relayout);
  }

  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', init);
  else init();
})(window, document);
