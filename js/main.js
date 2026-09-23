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

  // Footer year
  var year = q("[data-year]");
  if (year) year.textContent = new Date().getFullYear();

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
      sectionReveals(gsap, ScrollTrigger);
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
  function sectionReveals(gsap, ScrollTrigger) {
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
    reveal(qa(".contact__info"), { x: -24 }, 0);
    reveal(qa(".contact__form"), { x: 24 }, 0);

    var stripes = q(".careers__stripes");
    if (stripes) {
      gsap.fromTo(stripes, { xPercent: -4 }, {
        xPercent: 4, ease: "none",
        scrollTrigger: { trigger: q(".careers"), start: "top bottom", end: "bottom top", scrub: true }
      });
    }
  }
})();
