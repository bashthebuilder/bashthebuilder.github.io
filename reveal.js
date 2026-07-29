/* Shared scroll-animation system.
   Replaces the three divergent per-page implementations (a scroll-listener that
   re-queried the DOM on every event, plus two hand-rolled copies) with one
   IntersectionObserver pass. Opt in from markup:

     class="reveal"                     fade + rise
     class="reveal" data-reveal="left"  slide in from the left
     class="reveal" data-reveal="scale" scale up
     data-reveal-delay="120"            stagger, in ms

     <span class="counter" data-count="1.87" data-pre="£" data-post="M" data-dec="2">
     <div class="bar-fill" data-bar="72">      width animates to 72%

   Everything degrades to the finished state when prefers-reduced-motion is set
   or IntersectionObserver is unavailable. */
(function () {
    'use strict';

    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var hasIO = 'IntersectionObserver' in window;

    function settle(el) { el.classList.add('active'); }

    /* ---------- count-up ---------- */
    function countUp(el) {
        var target = parseFloat(el.dataset.count);
        if (isNaN(target)) return;
        var dec = parseInt(el.dataset.dec || '0', 10);
        var pre = el.dataset.pre || '';
        var post = el.dataset.post || '';
        var group = el.dataset.group === 'true';

        function render(v) {
            var n = v.toFixed(dec);
            if (group) n = Number(n).toLocaleString('en-GB', { minimumFractionDigits: dec, maximumFractionDigits: dec });
            el.textContent = pre + n + post;
        }
        if (reduce) { render(target); return; }

        var dur = 1500, t0 = null;
        function step(now) {
            if (t0 === null) t0 = now;
            var p = Math.min((now - t0) / dur, 1);
            render(target * (1 - Math.pow(1 - p, 3)));
            if (p < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    }

    /* ---------- bars ---------- */
    function fillBar(el) {
        var w = el.dataset.bar;
        if (w == null) return;
        el.style.width = w + '%';
    }

    function activate(el) {
        settle(el);
        var delay = parseInt(el.dataset.revealDelay || '0', 10);
        var run = function () {
            el.querySelectorAll('.counter').forEach(countUp);
            el.querySelectorAll('.bar-fill').forEach(fillBar);
            if (el.classList.contains('counter')) countUp(el);
            if (el.classList.contains('bar-fill')) fillBar(el);
        };
        if (reduce || !delay) run(); else setTimeout(run, delay);
    }

    /* Page-prefixed reveal classes predate this file. They follow the same
       "add .active when scrolled into view" contract and keep their own
       page-scoped CSS, so they are observed here rather than reimplemented
       per page. */
    var SELECTOR = '.reveal, .cm-reveal, .pc-reveal, .ug-reveal, .al-rev, .al-rev-l, .al-rev-scale, .counter, .bar-fill';

    function init() {
        var targets = document.querySelectorAll(SELECTOR);
        if (!targets.length) return;

        if (reduce || !hasIO) { targets.forEach(activate); return; }

        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (!e.isIntersecting) return;
                var el = e.target;
                var delay = parseInt(el.dataset.revealDelay || '0', 10);
                if (delay) setTimeout(function () { activate(el); }, delay);
                else activate(el);
                io.unobserve(el);           // one-shot: no repeated work on scroll
            });
        }, { rootMargin: '0px 0px -80px 0px', threshold: 0.05 });

        targets.forEach(function (el) { io.observe(el); });
    }

    /* ---------- scroll progress bar (opt in with <div class="scroll-progress">) ---------- */
    function progress() {
        var bar = document.querySelector('.scroll-progress');
        if (!bar) return;
        function update() {
            var h = document.documentElement;
            var max = h.scrollHeight - h.clientHeight;
            bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%';
        }
        window.addEventListener('scroll', update, { passive: true });
        window.addEventListener('resize', update);
        update();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () { init(); progress(); });
    } else { init(); progress(); }
})();
