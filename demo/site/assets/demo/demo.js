/* Chronopoli clickable demo layer: navigator, map, click-through rules, offline AI Tutor answers.
 * Works offline from the local folder: all data comes from the script files loaded before this one. */
(function () {
  'use strict';

  var MAP = window.CPXD_MAP || { pages: [], chapters: [], personas: {} };
  var RULES = window.CPXD_RULES || { global: [], pages: {}, forms: {}, scroll: {} };
  var KB = window.CPXD_KB || { qa: [], suggest: [] };
  var SLUG = window.CPXD_SLUG || '';
  var PAGES = MAP.pages || [];
  var IDX = -1;
  for (var i = 0; i < PAGES.length; i++) { if (PAGES[i].slug === SLUG) { IDX = i; break; } }
  var PAGE = PAGES[IDX] || null;
  var DEST = (PAGE && PAGE.destinations) || {};

  /* ---------------------------------------------------------------- storage (optional) */
  function sget(k) { try { return window.localStorage.getItem('cpxd.' + k); } catch (e) { return null; } }
  function sset(k, v) { try { window.localStorage.setItem('cpxd.' + k, v); } catch (e) { /* private mode */ } }
  function ssget(k) { try { return window.sessionStorage.getItem('cpxd.' + k); } catch (e) { return null; } }
  function ssset(k, v) { try { window.sessionStorage.setItem('cpxd.' + k, v); } catch (e) { /* ignore */ } }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function resolve(go) {
    if (!go) return '';
    if (go.charAt(0) === '@') return DEST[go.slice(1)] || 'index.html';
    return go;
  }
  function goTo(href) { if (href) window.location.href = href; }

  /* ---------------------------------------------------------------- fit to window
   * The windows were designed at 1600 px. In a narrower browser window the page body is zoomed so the layout stays
   * exactly as designed. The demo's own controls live outside <body> and are never zoomed. */
  var DESIGN_W = 1600, MIN_ZOOM = 0.72, ZOOM = 1;
  function fitOn() { return sget('fit') !== '0'; }
  function applyFit() {
    if (!document.body) return;
    var w = window.innerWidth || DESIGN_W;
    var z = (fitOn() && w < DESIGN_W - 10) ? Math.max(MIN_ZOOM, w / DESIGN_W) : 1;
    z = Math.round(z * 1000) / 1000;
    if (z === ZOOM && (document.body.style.zoom || '1') === String(z === 1 ? '1' : z)) return;
    ZOOM = z;
    document.body.style.zoom = z === 1 ? '' : String(z);
  }
  if (PAGE) applyFit();
  function uiRoot() { return document.documentElement; }

  /* ---------------------------------------------------------------- offline AI Tutor */
  var STOP = ('the and for with are our you your this that what which how does can should would could about from into than then there their them they '
    + 'not yes will just more most some any all have has had was were been being its it’s i’m we’re me my we us do did if or of to in on at as by be is an a so up out').split(' ');
  function stem(w) { return w.length > 4 ? w.replace(/(ings|ing|ies|ied|es|ed|s)$/, '') : w; }
  function toks(s) {
    var m = String(s || '').toLowerCase().match(/[a-z0-9][a-z0-9.'’-]*/g) || [];
    var out = [];
    m.forEach(function (w) { w = w.replace(/[.'’-]+$/, ''); if (w.length > 1 && STOP.indexOf(w) < 0) out.push(stem(w)); });
    return out;
  }
  KB.qa.forEach(function (e) { e._t = toks(e.q + ' ' + (e.k || '')); e._q = toks(e.q); });

  function answerFor(question) {
    var qt = toks(question);
    var best = null, bestScore = 0;
    KB.qa.forEach(function (e) {
      var hit = 0, seen = {};
      qt.forEach(function (w) { if (!seen[w] && e._t.indexOf(w) >= 0) { hit += (e._q.indexOf(w) >= 0 ? 1 : 0.6); seen[w] = 1; } });
      var score = hit / Math.sqrt(e._t.length + 2);
      if (hit >= Math.min(2, qt.length) && score > bestScore) { best = e; bestScore = score; }
    });
    if (best) return { text: best.a, sources: best.src };
    var sug = (KB.suggest || []).map(function (s) { return '• ' + s; }).join('\n');
    return {
      text: 'I could not find that in the course material available to me here. This demo AI Tutor answers from a small '
        + 'sample of Chronopoli content, so try one of these:\n' + sug,
      sources: ['Chronopoli demo library']
    };
  }

  function sseStream(events) {
    var enc = window.TextEncoder ? new TextEncoder() : null;
    var i = 0;
    function encode(s) {
      if (enc) return enc.encode(s);
      var u = unescape(encodeURIComponent(s)), a = new Uint8Array(u.length);
      for (var k = 0; k < u.length; k++) a[k] = u.charCodeAt(k);
      return a;
    }
    var reader = {
      read: function () {
        return new Promise(function (res) {
          var delay = i === 0 ? 380 : (i === 1 ? 260 : 24 + Math.random() * 46);
          setTimeout(function () {
            if (i >= events.length) { res({ done: true, value: undefined }); return; }
            res({ done: false, value: encode('data: ' + JSON.stringify(events[i++]) + '\n\n') });
          }, delay);
        });
      },
      cancel: function () { return Promise.resolve(); },
      releaseLock: function () { }
    };
    return {
      ok: true, status: 200, headers: { get: function () { return 'text/event-stream'; } },
      body: { getReader: function () { return reader; } },
      json: function () { return Promise.reject(new Error('stream')); },
      text: function () { return Promise.resolve(''); }
    };
  }

  function tutorResponse(init) {
    var q = '';
    try { q = JSON.parse((init && init.body) || '{}').question || ''; } catch (e) { q = ''; }
    var ans = answerFor(q);
    var events = [{ type: 'session', session_id: 'demo-' + (SLUG || 'page') }];
    var parts = ans.text.match(/\S+\s*/g) || [ans.text];
    for (var k = 0; k < parts.length; k += 3) events.push({ type: 'chunk', text: parts.slice(k, k + 3).join('') });
    events.push({ type: 'done', sources: ans.sources.map(function (t) { return { uri: 'library/' + t, score: 0.9 }; }) });
    return Promise.resolve(sseStream(events));
  }

  function jsonResponse(obj) {
    return Promise.resolve({
      ok: true, status: 200, headers: { get: function () { return 'application/json'; } },
      json: function () { return Promise.resolve(obj); }, text: function () { return Promise.resolve(JSON.stringify(obj)); }
    });
  }

  function approveResponse(url, init) {
    var m = /output\/(\d+)\/approve/.exec(url);
    var id = m ? m[1] : '';
    var action = 'approve';
    try { action = JSON.parse((init && init.body) || '{}').action || 'approve'; } catch (e) { /* default */ }
    var card = document.getElementById('output-' + id);
    var type = 'draft';
    if (card) {
      var spans = card.querySelectorAll('span');
      for (var k = 0; k < spans.length; k++) {
        var t = (spans[k].textContent || '').trim();
        if (t && t.length < 30 && !/Generated/.test(t)) { type = t; break; }
      }
    }
    var status = action === 'approve' ? 'approved' : 'rejected';
    setTimeout(function () { toast(type + ' ' + status + ' (demo only, nothing is sent).'); }, 60);
    return jsonResponse({ output_type: type, status: status });
  }

  var realFetch = window.fetch ? window.fetch.bind(window) : null;
  window.fetch = function (input, init) {
    var url = typeof input === 'string' ? input : (input && input.url) || String(input);
    if (/\/ai-tutor\/chat\/?/.test(url)) return tutorResponse(init);
    if (/\/ai-tutor\/history\/?/.test(url)) return jsonResponse({ sessions: [] });
    if (/\/symposia\/api\/symposia\/output\/\d+\/approve/.test(url)) return approveResponse(url, init);
    if (/^\//.test(url) || /chronopoli\.io/.test(url)) return jsonResponse({ ok: true });
    if (realFetch) return realFetch(input, init);
    return Promise.reject(new Error('offline'));
  };

  function openTutor(q) {
    var w = document.getElementById('cp-tutor-widget');
    if (!w) { toast('The AI Tutor opens from the gold button at the bottom right of most windows.'); return; }
    w.style.setProperty('display', 'block', 'important');
    var panel = document.getElementById('cp-tutor-panel');
    var tg = document.getElementById('cp-tutor-toggle');
    if (panel && panel.classList.contains('cp-tutor-hidden') && tg) tg.click();
    var input = document.getElementById('cp-tutor-input');
    if (input) {
      if (q) input.value = q;
      try { input.focus({ preventScroll: true }); } catch (e) { input.focus(); }
    }
    layoutNav();
  }

  /* ---------------------------------------------------------------- toast */
  var toastEl = null, toastTimer = null;
  function toast(msg, href, label, ms) {
    if (!document.body) return;
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className = 'cpxd-toast';
      toastEl.setAttribute('role', 'status');
      uiRoot().appendChild(toastEl);
    }
    toastEl.innerHTML = '<span>' + esc(msg) + '</span>' + (href ? '<a href="' + esc(href) + '">' + esc(label || 'Open') + ' →</a>' : '');
    var nb = nav && !nav.classList.contains('is-collapsed') ? nav.getBoundingClientRect() : null;
    toastEl.style.bottom = nb && nb.height ? Math.round(window.innerHeight - nb.top + 10) + 'px' : '';
    toastEl.classList.add('is-on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('is-on'); }, ms || (href ? 5200 : 3200));
  }

  window.CPXD_TOAST = toast; // shared with the in-page wiring of each window

  /* ---------------------------------------------------------------- click rules */
  var DEF_SEL = 'a, button, .btn, [class*="btn"], .cpx-tab, .cpx-chip, .cpx-card__action, .cpx-sidenav__item, '
    + '[class*="__cta"], [class*="__action"], .hx-now__a, .cpx-link, [role="tab"], .cpx-iconbtn, .cv-iconbtn, .pv-btn';
  var UI_SEL = '.cp-header, #cp-tutor-widget, .cpxd-nav, .cpxd-map, .cpxd-toast';
  var LIST = [];

  function norm(s) { return String(s || '').replace(/\s+/g, ' ').replace(/[\s→↓↑↗›»]+$/, '').trim(); }
  function inUI(el) { return !!(el.closest && el.closest(UI_SEL)); }
  // [class*="__action"] in DEF_SEL also matches button rows such as .cpx-pagehead__actions: a row is never a control
  function isRow(el) { return /(^|\s)[\w-]+__actions(\s|$)/.test(typeof el.className === 'string' ? el.className : ''); }
  function control(t) {
    var c = t.closest(DEF_SEL);
    while (c && isRow(c)) c = c.parentElement ? c.parentElement.closest(DEF_SEL) : null;
    return c;
  }

  function applyRule(r) {
    var nodes;
    try { nodes = document.querySelectorAll(r.s || DEF_SEL); } catch (e) { return; }
    var hits = [];
    for (var k = 0; k < nodes.length; k++) {
      var el = nodes[k];
      if (inUI(el)) continue;
      if (!r.s && isRow(el)) continue;
      if (r['in'] && !el.closest(r['in'])) continue;
      if (r.t != null || r.p != null || r.has != null || r.re) {
        var txt = norm(el.innerText || el.textContent);
        if (r.t != null && txt !== r.t) continue;
        if (r.p != null && txt.indexOf(r.p) !== 0) continue;
        if (r.has != null && txt.indexOf(r.has) < 0) continue;
        if (r.re && !(new RegExp(r.re)).test(txt)) continue;
      }
      hits.push(el);
    }
    // innermost matches only (a container and its single button share the same text)
    hits = hits.filter(function (el) { return !hits.some(function (o) { return o !== el && el.contains(o); }); });
    if (r.nth != null) hits = hits.slice(r.nth, r.nth + 1);
    hits.forEach(function (el) {
      if (el.hasAttribute('data-cpxd-r')) return; // first rule wins
      el.setAttribute('data-cpxd-r', String(LIST.length));
      el.classList.add('cpxd-hot');
      LIST.push(r);
    });
  }

  function runRule(r) {
    if (r.act === 'tutor') { openTutor(r.q); return; }
    if (r.act === 'toast') { toast(r.msg || 'Not part of this demo.', r.ex, r.exl); return; }
    var href = resolve(r.go);
    if (href) goTo(href);
  }

  function wireAll() {
    (RULES.pages[SLUG] || []).forEach(applyRule);
    (RULES.global || []).forEach(applyRule);
    // links that already lead to a demo window count as hotspots too
    var links = document.querySelectorAll('a[href]');
    for (var k = 0; k < links.length; k++) {
      var h = links[k].getAttribute('href') || '';
      if (/\.html(#|$)/.test(h) && !inUI(links[k])) links[k].classList.add('cpxd-hot');
    }
  }

  function isRealControl(c) {
    if (c.hasAttribute('onclick')) return true;
    if (c.closest('form') && (c.tagName === 'BUTTON' || c.tagName === 'INPUT' || c.tagName === 'SELECT')) return true;
    if (c.tagName === 'A') {
      var h = c.getAttribute('href');
      if (h && h !== '#' && !c.hasAttribute('data-cpxd-msg')) return true; // real link or in-page anchor
    }
    return false;
  }

  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || !t.closest || e.defaultPrevented || e.button !== 0) return;
    if (t.closest('.cpxd-nav, .cpxd-map, .cpxd-toast')) return;
    var w = t.closest('[data-cpxd-r]');
    if (w) {
      e.preventDefault(); e.stopPropagation();
      runRule(LIST[+w.getAttribute('data-cpxd-r')] || {});
      return;
    }
    var m = t.closest('[data-cpxd-msg]');
    if (m && !inUI(m)) {
      e.preventDefault(); e.stopPropagation();
      toast(m.getAttribute('data-cpxd-msg'), m.getAttribute('data-cpxd-ex'), m.getAttribute('data-cpxd-exl'));
      return;
    }
    if (inUI(t)) return;
    var c = control(t);
    if (!c || isRealControl(c)) return;
    e.preventDefault();
    toast('Demo: not wired in this preview');
  }, true);

  // the account menu closes on any click outside it. The theme listens on document, which never hears clicks that
  // a window's in-page wiring has already handled (toasts, tabs), so close it here as well.
  window.addEventListener('click', function (e) {
    var dd = document.getElementById('cp-user-dropdown');
    if (!dd || !dd.classList.contains('is-open')) return;
    var t = e.target;
    if (t && t.closest && (t.closest('#cp-user-dropdown') || t.closest('.cp-header__user-toggle'))) return;
    dd.classList.remove('is-open');
    var tg = document.querySelector('.cp-header__user-toggle');
    if (tg) { tg.setAttribute('aria-expanded', 'false'); tg.classList.remove('is-open'); }
  }, true);

  document.addEventListener('submit', function (e) {
    e.preventDefault();
    var to = (RULES.forms || {})[SLUG];
    if (to) goTo(to);
    else toast('Filters are shown for illustration in this demo.');
  }, true);

  /* ---------------------------------------------------------------- navigator */
  var ICON = {
    prev: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>',
    next: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>',
    map: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M4 6h16M4 12h16M4 18h16"/></svg>',
    min: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M6 12h12"/></svg>',
    gem: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 3l8 9-8 9-8-9z"/></svg>'
  };
  var nav = null, mapEl = null;

  function personaHTML() {
    var key = PAGE ? PAGE.persona : 'visitor';
    var p = (MAP.personas || {})[key] || { name: 'Visitor', role: 'not signed in', initials: '?' };
    var isVisitor = key === 'visitor';
    return '<span class="cpxd-persona" title="' + esc(isVisitor ? 'Not signed in' : 'Signed in as ' + p.name + ' · ' + p.role) + '">'
      + '<i class="' + (isVisitor ? 'is-visitor' : '') + '">' + esc(p.initials) + '</i>'
      + '<span>' + esc(isVisitor ? 'Visitor' : p.name) + ' <em>· ' + esc(p.role) + '</em></span></span>';
  }

  function buildNav() {
    if (!PAGE) return;
    var total = MAP.count || PAGES.length;
    var prev = PAGE.prev || 'index.html', next = PAGE.next || 'index.html';
    var path = String(PAGE.menu_path || '').replace(/\s*>\s*/g, ' › ');
    nav = document.createElement('div');
    nav.className = 'cpxd-nav';
    nav.setAttribute('role', 'navigation');
    nav.setAttribute('aria-label', 'Demo navigator');
    nav.innerHTML =
      '<a class="cpxd-prev" href="' + esc(prev) + '" title="Previous window (←)">' + ICON.prev + (PAGE.prev ? 'Prev' : 'Start') + '</a>'
      + '<span class="cpxd-count" title="Window ' + PAGE.index + ' of ' + total + '">' + PAGE.index + ' / ' + total + '</span>'
      + '<span class="cpxd-sep"></span>'
      + '<div class="cpxd-where" title="' + esc(path + ' (' + PAGE.title + ')') + '"><b>' + esc(PAGE.title) + '</b><span>' + esc(path) + '</span></div>'
      + '<span class="cpxd-kind ' + (PAGE.kind === 'built' ? 'is-built">Built' : 'is-preview">Design preview') + '</span>'
      + '<a class="cpxd-next" href="' + esc(next) + '" title="Next window (→)">' + (PAGE.next ? 'Next' : 'Finish') + ICON.next + '</a>'
      + '<span class="cpxd-sep"></span>'
      + '<button type="button" class="cpxd-mapbtn" title="All windows (M)">' + ICON.map + 'Map</button>'
      + personaHTML()
      + '<button type="button" class="cpxd-icon cpxd-min" title="Collapse the navigator">' + ICON.min + '</button>'
      + '<button type="button" class="cpxd-pill" title="Show the demo navigator">' + ICON.gem + 'Demo <b>' + PAGE.index + ' / ' + total + '</b></button>';
    uiRoot().appendChild(nav);
    nav.querySelector('.cpxd-mapbtn').addEventListener('click', function () { toggleMap(); });
    nav.querySelector('.cpxd-min').addEventListener('click', function () { setCollapsed(true); });
    nav.querySelector('.cpxd-pill').addEventListener('click', function () { setCollapsed(false); });
    if (sget('collapsed') === '1') nav.classList.add('is-collapsed');
  }

  function setCollapsed(on) {
    if (!nav) return;
    nav.classList.toggle('is-collapsed', on);
    sset('collapsed', on ? '1' : '0');
    layoutNav();
  }

  // keep the navigator clear of the AI Tutor panel when it is open
  function tutorOpen() {
    var panel = document.getElementById('cp-tutor-panel');
    var widget = document.getElementById('cp-tutor-widget');
    return !!(panel && widget && !panel.classList.contains('cp-tutor-hidden') && getComputedStyle(widget).display !== 'none');
  }
  function layoutNav() {
    if (!nav) return;
    var open = tutorOpen();
    nav.classList.toggle('is-left', open);
    nav.classList.toggle('is-compact', open);
    var marker = document.querySelector('.cpx-demo-marker');
    var markerShown = marker && getComputedStyle(marker).display !== 'none' && marker.getBoundingClientRect().bottom > window.innerHeight - 60;
    nav.style.left = open ? '12px' : '';
    nav.style.bottom = open && markerShown ? '54px' : '';
    if (spacer) placeSpacer(); // the navigator may now sit higher: keep the end of the page above it
  }

  // room below the last content so the navigator never hides it (works even when content overflows its box)
  var spacer = null;
  function placeSpacer() {
    if (!document.body) return;
    if (!spacer) { spacer = document.createElement('div'); spacer.className = 'cpxd-spacer'; spacer.setAttribute('aria-hidden', 'true'); }
    var y0 = window.pageYOffset;
    if (spacer.parentNode) spacer.parentNode.removeChild(spacer);
    var h = document.documentElement.scrollHeight;
    // room = the navigator's height plus its distance from the bottom edge (it moves up when the AI Tutor is open)
    var nb = nav && !nav.classList.contains('is-collapsed') ? nav.getBoundingClientRect() : null;
    var room = nb && nb.height ? Math.max(64, Math.round(window.innerHeight - nb.top + 18)) : 64;
    spacer.style.top = (h + room) + 'px';
    uiRoot().appendChild(spacer);
    if (window.pageYOffset !== y0) { // measuring without the spacer can clamp the scroll position: put it back
      try { window.scrollTo({ top: y0, left: window.pageXOffset, behavior: 'instant' }); } catch (e) { window.scrollTo(window.pageXOffset, y0); }
    }
  }

  /* ---------------------------------------------------------------- map overlay */
  function buildMap() {
    mapEl = document.createElement('div');
    mapEl.className = 'cpxd-map';
    mapEl.setAttribute('role', 'dialog');
    mapEl.setAttribute('aria-label', 'Demo map');
    var groups = {};
    PAGES.forEach(function (p) { (groups[p.chapter] = groups[p.chapter] || []).push(p); });
    var body = (MAP.chapters || []).map(function (ch, n) {
      var list = groups[ch] || [];
      return '<section class="cpxd-map__ch"><h3>' + (n + 1) + ' · ' + esc(ch) + ' <em>' + list.length + '</em></h3><ol>'
        + list.map(function (p) {
          return '<li><a href="' + esc(p.file) + '" class="' + (p.slug === SLUG ? 'is-current' : '') + '" title="' + esc(p.menu_path) + '">'
            + '<b>' + p.index + '</b><span>' + esc(p.title) + '</span>'
            + '<i class="' + (p.kind === 'built' ? 'is-built">BUILT' : 'is-preview">PREVIEW') + '</i></a></li>';
        }).join('') + '</ol></section>';
    }).join('');
    mapEl.innerHTML =
      '<div class="cpxd-map__box">'
      + '<div class="cpxd-map__head"><div class="cpxd-grow"><h2>Chronopoli <span>· Clickable Demo</span></h2>'
      + '<p>' + PAGES.length + ' windows in tour order · ' + esc(MAP.disclaimer || '') + '</p></div>'
      + '<button type="button" class="cpxd-map__btn cpxd-hotbtn" title="Highlight what you can click (H)">Show clickable areas</button>'
      + '<button type="button" class="cpxd-map__btn cpxd-fitbtn" title="Scale windows to the browser width (F)">Fit to window</button>'
      + '<a class="cpxd-map__btn" href="index.html">Start page</a>'
      + '<button type="button" class="cpxd-map__btn cpxd-map__btn--gold cpxd-close">Close</button></div>'
      + '<div class="cpxd-map__body">' + body + '</div>'
      + '<div class="cpxd-map__foot"><span><kbd>←</kbd> <kbd>→</kbd> previous / next window</span><span><kbd>M</kbd> map</span>'
      + '<span><kbd>H</kbd> highlight clickable areas</span><span><kbd>F</kbd> fit to window</span><span><kbd>Esc</kbd> close</span>'
      + '<span>BUILT = real screen template with demo data · PREVIEW = design preview of a planned screen</span></div></div>';
    uiRoot().appendChild(mapEl);
    mapEl.addEventListener('click', function (e) { if (e.target === mapEl) toggleMap(false); });
    mapEl.querySelector('.cpxd-close').addEventListener('click', function () { toggleMap(false); });
    mapEl.querySelector('.cpxd-hotbtn').addEventListener('click', function () { toggleHot(); });
    mapEl.querySelector('.cpxd-fitbtn').addEventListener('click', function () { toggleFit(); });
    syncHotBtn();
    syncFitBtn();
  }

  function toggleMap(force) {
    if (!mapEl) buildMap();
    var on = force == null ? !mapEl.classList.contains('is-open') : force;
    mapEl.classList.toggle('is-open', on);
    if (on) {
      var cur = mapEl.querySelector('a.is-current');
      if (cur && cur.scrollIntoView) cur.scrollIntoView({ block: 'center' });
    }
  }

  function syncHotBtn() {
    var b = mapEl && mapEl.querySelector('.cpxd-hotbtn');
    var on = document.documentElement.classList.contains('cpxd-show-hot');
    if (b) { b.classList.toggle('is-on', on); b.textContent = on ? 'Hide clickable areas' : 'Show clickable areas'; }
  }
  function syncFitBtn() {
    var b = mapEl && mapEl.querySelector('.cpxd-fitbtn');
    if (b) { b.classList.toggle('is-on', fitOn()); b.textContent = fitOn() ? 'Fit to window: on' : 'Fit to window: off'; }
  }
  function toggleFit() {
    sset('fit', fitOn() ? '0' : '1');
    applyFit(); layoutNav(); placeSpacer(); syncFitBtn();
    toast(fitOn() ? 'Windows are scaled to fit the browser width, as designed.' : 'Windows now use the browser width without scaling.');
  }
  function toggleHot(force) {
    var root = document.documentElement;
    var on = force == null ? !root.classList.contains('cpxd-show-hot') : force;
    root.classList.toggle('cpxd-show-hot', on);
    ssset('hot', on ? '1' : '0');
    syncHotBtn();
    if (on) toast('Dashed outlines show what you can click in this window.');
  }

  /* ---------------------------------------------------------------- keyboard */
  document.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    if (!PAGE) return;
    if (e.key === 'ArrowRight') { e.preventDefault(); goTo(PAGE.next || 'index.html'); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); goTo(PAGE.prev || 'index.html'); }
    else if (e.key === 'm' || e.key === 'M') { e.preventDefault(); toggleMap(); }
    else if (e.key === 'h' || e.key === 'H') { e.preventDefault(); toggleHot(); }
    else if (e.key === 'f' || e.key === 'F') { e.preventDefault(); toggleFit(); }
    else if (e.key === 'Escape' && mapEl && mapEl.classList.contains('is-open')) { toggleMap(false); }
  });

  /* ---------------------------------------------------------------- start */
  function start() {
    document.body.classList.add('cpxd-on');
    applyFit();
    if (SLUG) sset('last', SLUG);
    buildNav();
    wireAll();
    if (ssget('hot') === '1') document.documentElement.classList.add('cpxd-show-hot');
    var panel = document.getElementById('cp-tutor-panel');
    if (panel && window.MutationObserver) {
      new MutationObserver(function () { layoutNav(); }).observe(panel, { attributes: true, attributeFilter: ['class', 'style'] });
    }
    window.addEventListener('resize', function () { applyFit(); layoutNav(); placeSpacer(); });
    layoutNav();
    if (!ssget('tip')) {
      ssset('tip', '1');
      setTimeout(function () { toast('Tip: click through the window like a real product. ← → step through the tour, M opens the map, H shows what you can click.', null, null, 6500); }, 700);
    }
  }

  // the AI Tutor widget is added on DOMContentLoaded; wire after it exists, then once more after page scripts ran
  function onLoad() {
    layoutNav();
    wireAll();
    placeSpacer();
    var y = (RULES.scroll || {})[SLUG];
    if (y && !window.location.hash) window.scrollTo(0, Math.round(y * ZOOM));
    setTimeout(function () { layoutNav(); placeSpacer(); }, 600);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
  if (document.readyState === 'complete') onLoad(); else window.addEventListener('load', onLoad);
})();
