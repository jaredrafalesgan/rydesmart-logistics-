// RydeSmart Logistics — site interactions
(function () {
  // Where quote requests are sent. Replace with the real inbox (or a form service endpoint).
  var QUOTE_EMAIL = "dispatch@rydesmartlogistics.com";

  // Mobile navigation
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open menu");
      }
    });
  }

  // Header shadow once the page scrolls
  var header = document.querySelector(".header");
  var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 10); };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Quote forms: open the visitor's email app with the request filled in
  document.querySelectorAll("[data-quote-form]").forEach(function (form) {
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
      var note = form.querySelector(".form-note");
      if (note) note.textContent = "Thanks! Your email app should open with your request. Prefer to talk? Call (555) 123-4567.";
    });
  });

  // Fade sections in as they scroll into view
  var targets = document.querySelectorAll(".service, .why__list li, .step, .industries li, .section__head");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    targets.forEach(function (el) { el.classList.add("reveal"); io.observe(el); });
  }

  // Footer year
  var year = document.querySelector("[data-year]");
  if (year) year.textContent = new Date().getFullYear();
})();
