// RydeSmart Logistics — site interactions
(function () {
  // Class/id prefix. Empty on the main site; tools/build.py sets it to "rs-" for GoHighLevel.
  var P = "";
  var root = document.getElementById(P + "site") || document;

  // Where quote requests are sent (swap for a form service endpoint to collect them directly).
  var QUOTE_EMAIL = "Admin@rydesmartlogistics.com";

  // Used only when GSAP isn't already on the page (e.g. the GoHighLevel snippet).
  var GSAP_CDN = "https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/";

  function sel(s) { return P ? s.replace(/([.#])([a-zA-Z_][\w-]*)/g, "$1" + P + "$2") : s; }
  function cls(name) { return P + name; }
  function q(s, ctx) { return (ctx || root).querySelector(sel(s)); }
  function qa(s, ctx) { return Array.prototype.slice.call((ctx || root).querySelectorAll(sel(s))); }

  // Page builders (GoHighLevel) put this inside their own section/row/column, which have a
  // max width and padding. Stretch the site back out to the full window width.
  if (root !== document) {
    var fitWidth = function () {
      root.style.marginLeft = "0px";
      root.style.width = document.documentElement.clientWidth + "px";
      root.style.marginLeft = -root.getBoundingClientRect().left + "px";
    };
    fitWidth();
    window.addEventListener("resize", fitWidth);
  }

  // Mobile navigation
  var toggle = q(".nav-toggle");
  var nav = q("#nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle(cls("is-open"));
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        nav.classList.remove(cls("is-open"));
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open menu");
      }
    });
  }

  // Header shadow once the page scrolls
  var header = q(".header");
  var onScroll = function () { header.classList.toggle(cls("is-scrolled"), window.scrollY > 10); };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Quote forms: open the visitor's email app with the request filled in
  qa("[data-quote-form]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var lines = [];
      new FormData(form).forEach(function (value, key) {
        if (String(value).trim()) {
          lines.push(key.charAt(0).toUpperCase() + key.slice(1) + ": " + value);
        }
      });
      var subject = "Freight Quote Request - " + (form.elements.service ? form.elements.service.value : "");
      window.location.href = "mailto:" + QUOTE_EMAIL +
        "?subject=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(lines.join("\n"));
      var note = q(".form-note", form);
      if (note) note.textContent = "Thanks! Your email app should open with your request. Prefer to talk? Call (678) 315-8285.";
    });
  });

  // CDL driver application: open the GoHighLevel form in a pop-up instead of a new tab.
  // The link still works as a normal new-tab link if JS or <dialog> isn't available.
  var applyModal = q(".apply-modal");
  if (applyModal && typeof applyModal.showModal === "function") {
    var applyFrame = q("iframe", applyModal);
    var applyTrigger = null;
    var loadForm = function (link) { if (!applyFrame.getAttribute("src")) applyFrame.src = link.href; };
    applyFrame.addEventListener("load", function () { applyModal.classList.add(cls("is-loaded")); });
    qa("[data-driver-form]").forEach(function (link) {
      // Start loading as soon as the visitor shows intent, so the form is ready on open.
      link.addEventListener("pointerenter", function () { loadForm(link); });
      link.addEventListener("focus", function () { loadForm(link); });
      link.addEventListener("click", function (e) {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return; // let "open in new tab" work
        e.preventDefault();
        loadForm(link);
        applyTrigger = link;
        var docEl = document.documentElement;
        docEl.style.paddingRight = (window.innerWidth - docEl.clientWidth) + "px";
        docEl.style.overflow = "hidden";
        applyModal.showModal();
      });
    });
    q(".apply-modal__close", applyModal).addEventListener("click", function () { applyModal.close(); });
    applyModal.addEventListener("click", function (e) { if (e.target === applyModal) applyModal.close(); }); // backdrop
    applyModal.addEventListener("close", function () {
      document.documentElement.style.overflow = "";
      document.documentElement.style.paddingRight = "";
      if (applyTrigger) applyTrigger.focus({ preventScroll: true });
    });
  }

  // Footer year
  var year = q("[data-year]");
  if (year) year.textContent = new Date().getFullYear();

  // ---------- Testimonials carousel ----------
  // A slow, endless conveyor: the track is translated every frame and wraps by one full
  // set of cards (cloned to cover the screen), so there's never a visible jump. Hover,
  // focus or the pause button ease it to a stop; drag/swipe, arrows, dots and arrow keys
  // move it by hand. With reduced motion it never moves on its own.
  (function reviewsCarousel() {
    var wrap = q(".reviews");
    if (!wrap) return;
    var viewport = q(".reviews__viewport", wrap);
    var track = q(".reviews__track", wrap);
    var originals = qa(".review", track);
    var count = originals.length;
    if (!count) return;

    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
    var playBtn = q(".reviews__play", wrap);
    var cards = [], dots = [];
    var step = 0, setW = 0, half = 0, centerX = 0;
    var x = 0, speed = 0, fling = 0, active = -1;
    var paused = false, hover = false, focused = false;
    var drag = null, glide = null, raf = 0, last = 0, visible = true;

    function baseSpeed() { return window.innerWidth < 700 ? 20 : 26; } // px per second
    function wrapX(v) { return ((v % setW) - setW) % setW; }           // keep within (-setW, 0]

    wrap.classList.add(cls("is-live"));

    originals.forEach(function (_, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = cls("reviews__dot");
      b.setAttribute("aria-label", "Show testimonial " + (i + 1) + " of " + count);
      b.addEventListener("click", function () { goTo(i); });
      q(".reviews__dots", wrap).appendChild(b);
      dots.push(b);
    });

    function layout() {
      var index = step ? (centerX - x) / step : 0;
      qa(".is-clone", track).forEach(function (c) { track.removeChild(c); });
      step = originals[0].offsetWidth + (parseFloat(getComputedStyle(track).columnGap) || 0);
      setW = step * count;
      var copies = Math.ceil((viewport.clientWidth + setW) / setW);
      for (var k = 0; k < copies; k++) {
        originals.forEach(function (o) {
          var c = o.cloneNode(true);
          c.classList.add(cls("is-clone"));
          c.setAttribute("aria-hidden", "true");
          track.appendChild(c);
        });
      }
      cards = qa(".review", track).map(function (el) {
        return { card: el.firstElementChild, mid: el.offsetLeft + el.offsetWidth / 2 };
      });
      half = viewport.clientWidth / 2;
      centerX = half - originals[0].offsetWidth / 2; // track offset that centres card 0
      x = centerX - index * step;
      render();
    }

    function render() {
      var rx = wrapX(x);
      track.style.transform = "translate3d(" + rx.toFixed(2) + "px,0,0)";
      // Cards ease up to full size/opacity as they reach the centre.
      for (var i = 0; i < cards.length; i++) {
        var d = Math.abs(rx + cards[i].mid - half);
        if (d > half + step) continue;
        var f = Math.min(1, d / (step * 1.15));
        cards[i].card.style.transform = "scale(" + (1 - 0.05 * f).toFixed(4) + ")";
        cards[i].card.style.opacity = (1 - 0.45 * f).toFixed(3);
      }
      var a = ((Math.round((centerX - rx) / step) % count) + count) % count;
      if (a !== active) {
        if (active > -1) dots[active].classList.remove(cls("is-active"));
        dots[a].classList.add(cls("is-active"));
        dots[a].setAttribute("aria-current", "true");
        if (active > -1) dots[active].removeAttribute("aria-current");
        active = a;
      }
    }

    function glideTo(target) {
      glide = { from: x, to: target, t0: performance.now(), dur: reduce.matches ? 1 : 750 };
      fling = 0;
      speed = 0;
      start();
    }
    function shift(dir) { glideTo(centerX - (Math.round((centerX - x) / step) + dir) * step); }
    function goTo(i) {
      var cur = Math.round((centerX - x) / step);
      var diff = ((i - cur) % count + count) % count;
      if (diff > count / 2) diff -= count;
      glideTo(centerX - (cur + diff) * step);
    }

    function frame(t) {
      raf = requestAnimationFrame(frame);
      var dt = Math.min(0.05, (t - (last || t)) / 1000);
      last = t;
      if (glide) {
        var p = Math.max(0, Math.min(1, (t - glide.t0) / glide.dur));
        x = glide.from + (glide.to - glide.from) * (1 - Math.pow(1 - p, 3));
        if (p === 1) glide = null;
      } else if (!drag) {
        var stopped = paused || hover || focused || reduce.matches;
        speed += ((stopped ? 0 : baseSpeed()) - speed) * Math.min(1, dt * 2.5); // soft start/stop
        if (fling) {
          x += fling * dt;
          fling *= Math.pow(0.03, dt);
          if (Math.abs(fling) < 5) fling = 0;
        }
        x -= speed * dt;
      }
      if (!glide) x = wrapX(x);
      render();
      // Nothing left to animate: stop the loop until something changes.
      if (!glide && !drag && !fling && speed < 0.05 && (paused || hover || focused || reduce.matches)) stop();
    }
    function start() { if (!raf && visible) { last = 0; raf = requestAnimationFrame(frame); } }
    function stop() { cancelAnimationFrame(raf); raf = 0; }

    // Hover (mouse only) and keyboard focus pause; leaving resumes.
    viewport.addEventListener("pointerenter", function (e) { if (e.pointerType === "mouse") { hover = true; } });
    viewport.addEventListener("pointerleave", function (e) { if (e.pointerType === "mouse") { hover = false; start(); } });
    wrap.addEventListener("focusin", function (e) { focused = e.target.matches(":focus-visible"); });
    wrap.addEventListener("focusout", function (e) { if (!wrap.contains(e.relatedTarget)) { focused = false; start(); } });

    // Drag / swipe. touch-action: pan-y leaves vertical page scrolling to the browser.
    viewport.addEventListener("pointerdown", function (e) {
      if (e.button !== 0) return;
      drag = { id: e.pointerId, x0: e.clientX, last: e.clientX, t: e.timeStamp, v: 0, moved: false };
      glide = null;
      fling = 0;
      start();
    });
    viewport.addEventListener("pointermove", function (e) {
      if (!drag || e.pointerId !== drag.id) return;
      if (!drag.moved) {
        if (Math.abs(e.clientX - drag.x0) < 6) return;
        drag.moved = true;
        drag.last = e.clientX;
        viewport.setPointerCapture(drag.id);
        wrap.classList.add(cls("is-dragging"));
      }
      var dx = e.clientX - drag.last;
      var ms = Math.max(8, e.timeStamp - drag.t);
      x += dx;
      drag.v = 0.7 * (dx / ms * 1000) + 0.3 * drag.v;
      drag.last = e.clientX;
      drag.t = e.timeStamp;
    });
    function endDrag(e) {
      if (!drag || e.pointerId !== drag.id) return;
      if (drag.moved) {
        fling = Math.max(-1800, Math.min(1800, drag.v));
        speed = 0;
      }
      wrap.classList.remove(cls("is-dragging"));
      drag = null;
      start();
    }
    viewport.addEventListener("pointerup", endDrag);
    viewport.addEventListener("pointercancel", endDrag);

    q(".reviews__prev", wrap).addEventListener("click", function () { shift(-1); });
    q(".reviews__next", wrap).addEventListener("click", function () { shift(1); });
    viewport.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { e.preventDefault(); shift(-1); }
      if (e.key === "ArrowRight") { e.preventDefault(); shift(1); }
    });
    playBtn.addEventListener("click", function () {
      paused = !paused;
      playBtn.setAttribute("aria-pressed", String(paused));
      playBtn.setAttribute("aria-label", paused ? "Play testimonials" : "Pause testimonials");
      start();
    });

    function motionPref() {
      wrap.classList.toggle(cls("is-static"), reduce.matches);
      start();
    }
    if (reduce.addEventListener) reduce.addEventListener("change", motionPref);

    // Only animate while the section is on screen.
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        if (visible) start(); else stop();
      }).observe(wrap);
    }

    var resizeTimer;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(layout, 150);
    });

    layout();
    motionPref();
  })();

  // ---------- Scroll animation ----------
  // Everything below is progressive: if GSAP fails to load, or the visitor prefers
  // reduced motion, the page keeps its static layout with all content visible.

  function loadScript(src, done) {
    var s = document.createElement("script");
    s.src = src;
    s.onload = done;
    document.head.appendChild(s);
  }

  function withGsap(cb) {
    var files = [];
    if (!window.gsap) files.push("gsap.min.js");
    if (!window.ScrollTrigger) files.push("ScrollTrigger.min.js");
    (function next() {
      if (!files.length) return cb(window.gsap, window.ScrollTrigger);
      loadScript(GSAP_CDN + files.shift(), next);
    })();
  }

  withGsap(function (gsap, ScrollTrigger) {
    gsap.registerPlugin(ScrollTrigger);
    ScrollTrigger.config({ ignoreMobileResize: true });

    var mm = gsap.matchMedia();
    mm.add({
      desktop: "(min-width: 900px) and (prefers-reduced-motion: no-preference)",
      mobile: "(max-width: 899.98px) and (prefers-reduced-motion: no-preference)"
    }, function (ctx) {
      var undo = truckJourney(gsap, ctx.conditions.desktop);
      sectionReveals(gsap, ScrollTrigger, ctx.conditions.desktop);
      return undo;
    });

    // Web fonts change text heights, which moves every trigger point.
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
    }
  });

  // "Why RydeSmart": the section pins while scrolling moves a truck through four stages.
  function truckJourney(gsap, desktop) {
    var section = q(".journey");
    if (!section) return;
    var stage = q(".journey__stage", section);
    var truck = q(".journey__truck", section);
    var panels = qa(".journey__panel", section);
    var headerH = function () { return header ? header.offsetHeight : 0; };
    var W = function () { return stage.clientWidth; };

    section.classList.add(cls("is-cinematic"));
    section.style.setProperty("--header-h", headerH() + "px");

    var D = 12; // timeline length; the numbers below are positions on it
    // Where the truck's centre sits (fraction of screen width) at each timeline mark.
    var marks = [0, 1.4, 3.2, 4.4, 6.0, 7.0, 8.4, 9.4, 10.6, D];
    var stops = desktop
      ? [-0.32, 0.18, 0.24, 0.5, 0.55, 0.7, 0.74, 0.85, 0.88, 1.4]
      : [-0.6, 0.4, 0.43, 0.47, 0.5, 0.53, 0.56, 0.58, 0.6, 1.7];
    // Slow drifts between the moves keep the truck rolling while a panel is read.
    var eases = ["power2.out", "none", "power2.inOut", "none", "power2.inOut", "none", "power2.inOut", "none", "power2.in"];
    // How far each layer slides left over the whole scroll, as a fraction of screen width.
    var travel = desktop
      ? { clouds: 0.04, far: 0.14, roadside: 1.5, lanes: 3.0, verge: 3.6 }
      : { clouds: 0.03, far: 0.1, roadside: 0.9, lanes: 1.8, verge: 2.2 };
    // Panel [in, out] positions on the timeline.
    var slots = [[1.0, 3.2], [3.9, 6.0], [6.6, 8.4], [9.0, 10.9]];

    var tl = gsap.timeline({
      defaults: { ease: "power2.out" },
      scrollTrigger: {
        trigger: section,
        start: function () { return "top " + headerH() + "px"; },
        end: function () { return "+=" + Math.round(window.innerHeight * (desktop ? 3.2 : 1.9)); },
        pin: true,
        scrub: desktop ? 0.9 : 0.6,
        anticipatePin: 1,
        invalidateOnRefresh: true,
        onRefreshInit: function () { section.style.setProperty("--header-h", headerH() + "px"); }
      }
    });

    // Parallax: far layers barely move, the road and near shoulder move fastest.
    Object.keys(travel).forEach(function (name) {
      tl.fromTo(q(".journey__" + name, section), { x: 0 },
        { x: function () { return -W() * travel[name]; }, ease: "none", duration: D }, 0);
    });

    // Truck position, with the GPS route line filling up behind it.
    var fill = q(".journey__route-fill", section);
    var truckX = function (f) { return function () { return W() * f - truck.offsetWidth / 2; }; };
    var routeAt = function (f) { return Math.min(1, Math.max(0, (f - 0.08) / 0.84)); };
    gsap.set(truck, { x: truckX(stops[0]) });
    if (fill) gsap.set(fill, { scaleX: 0 });
    for (var i = 1; i < marks.length; i++) {
      var seg = { duration: marks[i] - marks[i - 1], ease: eases[i - 1] };
      tl.to(truck, Object.assign({ x: truckX(stops[i]) }, seg), marks[i - 1]);
      if (fill) tl.to(fill, Object.assign({ scaleX: routeAt(stops[i]) }, seg), marks[i - 1]);
    }

    // Wheels turn in step with how far the truck travels over the road.
    var wheels = qa(".truck__wheel", section);
    gsap.set(wheels, { transformOrigin: "50% 50%" });
    tl.to(wheels, {
      rotation: function () {
        var ground = W() * (travel.lanes + stops[stops.length - 1] - stops[0]);
        var tire = truck.offsetWidth * 41 / 900; // tire diameter in the 900-wide drawing
        return ground / (Math.PI * tire) * 360;
      },
      ease: "none", duration: D
    }, 0);

    // Passing highway lights sweep across the body; a slight suspension float.
    tl.fromTo(q(".truck__sheen", section), { x: -120 }, { x: 1150, ease: "none", duration: D / 5, repeat: 4 }, 0);
    tl.to(q(".truck__body", section), { y: -0.6, ease: "sine.inOut", duration: D / 24, repeat: 23, yoyo: true }, 0);

    // Copy: the intro gives way to four panels, one per stage of the trip.
    tl.to(q(".journey__hint", section), { autoAlpha: 0, y: 8, duration: 0.4 }, 0.05);
    tl.to(q(".journey__lead", section), { autoAlpha: 0, y: -12, duration: 0.5, ease: "power1.in" }, 0.5);
    panels.forEach(function (panel, n) {
      var shift = desktop ? { x: 24 } : { y: 14 };
      gsap.set(panel, Object.assign({ autoAlpha: 0 }, shift));
      gsap.set(panel.children, { autoAlpha: 0, y: 12 });
      tl.to(panel, { autoAlpha: 1, x: 0, y: 0, duration: 0.45 }, slots[n][0]);
      tl.to(panel.children, { autoAlpha: 1, y: 0, duration: 0.4, stagger: 0.18 }, slots[n][0] + 0.1);
      tl.to(panel, Object.assign({ autoAlpha: 0, duration: 0.45, ease: "power1.in" },
        desktop ? { x: -24 } : { y: -14 }), slots[n][1]);
    });

    // Tracking stage: location pin over the cab and the pickup-to-delivery route.
    var pin = q(".journey__pin", section);
    var route = q(".journey__route", section);
    gsap.set([pin, route], { autoAlpha: 0 });
    gsap.set(pin, { scale: 0.6, transformOrigin: "50% 100%" });
    tl.to(route, { autoAlpha: 1, duration: 0.5 }, 3.3);
    tl.to(pin, { autoAlpha: 1, scale: 1, duration: 0.4 }, 3.7);
    tl.to([pin, route], { autoAlpha: 0, duration: 0.5, ease: "power1.in" }, 8.5);

    // Exit: headline lifts away and the road fades into the next (white) section.
    tl.to(q(".journey__intro", section), { autoAlpha: 0, y: -16, duration: 0.6, ease: "power1.in" }, 11.0);
    tl.to(q(".journey__fade", section), { opacity: 1, duration: 1, ease: "none" }, 11.0);

    return function () {
      section.classList.remove(cls("is-cinematic"));
      section.style.removeProperty("--header-h");
    };
  }

  // Light entrance animations for the rest of the page.
  function sectionReveals(gsap, ScrollTrigger, desktop) {
    function reveal(targets, from, stagger) {
      if (!targets.length) return;
      gsap.set(targets, Object.assign({ autoAlpha: 0, transition: "none" }, from));
      ScrollTrigger.batch(targets, {
        start: "top 88%",
        once: true,
        onEnter: function (batch) {
          gsap.to(batch, {
            autoAlpha: 1, x: 0, y: 0, duration: 0.7, ease: "power2.out", stagger: stagger, overwrite: true,
            clearProps: "transition,transform,opacity,visibility"
          });
        }
      });
    }
    reveal(qa(".section__head"), { y: 18 }, 0);
    reveal(qa(".service"), { y: 28 }, 0.08);
    reveal(qa(".step"), { y: 22 }, 0.15);
    reveal(qa(".industries li"), { y: 14 }, 0.05);
    // Side slides only where there's room; on phones they'd push past the screen edge.
    reveal(qa(".contact__info"), desktop ? { x: -24 } : { y: 18 }, 0);
    reveal(qa(".contact__form"), desktop ? { x: 16 } : { y: 18 }, 0.1);

    var stripes = q(".careers__stripes");
    if (stripes) {
      gsap.fromTo(stripes, { xPercent: -4 }, {
        xPercent: 4, ease: "none",
        scrollTrigger: { trigger: q(".careers"), start: "top bottom", end: "bottom top", scrub: true }
      });
    }
  }
})();
