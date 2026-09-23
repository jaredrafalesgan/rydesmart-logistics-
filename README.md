# RydeSmart Logistics Website

Marketing website for **RydeSmart Logistics** — *Driven by safety. Focused on delivery.*

A static, one-page site (HTML + CSS + a little JavaScript, no build step). The layout follows the
service-business style of the Smart Decision Truck Repair site (contact top bar, bold hero with a call-to-action,
services grid, "why choose us", stats, and a quote/contact form). The colors and type come from the
RydeSmart logo: royal blue, deep navy, black and white, with bold italic headings and slanted buttons.

## View it
Open `index.html` in a browser, or host the folder on GitHub Pages
(Settings → Pages → Deploy from branch → root).

## Files
- `index.html` — page content
- `css/styles.css` — styling (brand colors are at the top in `:root`)
- `js/main.js` — mobile menu, quote forms, scroll animation
- `js/vendor/` — GSAP 3.15.0 + ScrollTrigger (GSAP's free standard license)
- `assets/` — logo variants (`logo.png`, white-text `logo-light.png` for dark backgrounds) and favicon
- `assets/journey/` — background art for the truck scene (clouds, mountains, skyline, roadside, asphalt, shoulder)
- `tools/build.py` — builds the single-file versions (see below)

## Scroll animation
The **Why RydeSmart** section is a pinned, scroll-driven scene: while the visitor scrolls, a
RydeSmart truck drives across a layered highway scene (parallax sky, mountains, roadside, road),
and four panels appear in turn — Safety-First Drivers, Live Shipment Tracking (with a GPS route
and location pin), Fully Insured Cargo and One Point of Contact — before the scene fades into
**How It Works**. Everything is driven by scroll position (GSAP ScrollTrigger `pin` + `scrub`);
nothing plays on its own.

- Timeline positions, truck stops and layer speeds are at the top of `truckJourney()` in `js/main.js`.
- Phones get a shorter pin, a smaller truck with less travel, and stacked panels.
- With *reduce motion* turned on (or if JavaScript/GSAP doesn't load) the section shows as a normal
  static layout: headline, all four panels, and the truck parked on the road.
- Other sections only get light entrance reveals and a slow drift on the careers banner.

## Testimonials carousel
The **What Our Customers Say** section (between Industries and Drive With RydeSmart) is a slow,
continuous right-to-left conveyor of review cards (`reviewsCarousel()` in `js/main.js`, no library).
It loops without a visible jump, eases to a stop on hover or keyboard focus, and can be dragged or
swiped; arrows, dots, arrow keys and a pause button give manual control. The centre card is full
size and opacity, neighbours are slightly smaller and dimmer. With reduced motion it doesn't move
on its own; without JavaScript it's a plain swipeable row.

**The six testimonials are fictional placeholders.** Each card is marked `data-sample`. Replace
them with verified customer testimonials (same markup: quote, name, title, city) before the site
goes live.

The truck is an inline SVG illustration (so the wheels can turn and the lights can move). To use a
real photo instead, replace the `<svg class="truck">` inside `.journey__truck` with a side-profile,
transparent-background PNG/WebP of the truck facing right; the wheel-turn and light-sweep effects
simply won't apply to a flat photo.

## Contact info
- Phone: (678) 315-8285
- Email: Admin@rydesmartlogistics.com (quote forms and driver applications go here; set in `QUOTE_EMAIL` in `js/main.js`)

## Placeholder info to replace before going live
- USDOT / MC numbers in the footer
- Stats (98% on-time, 48 states, 1 hr quote response), office hours and service list — confirm they're accurate
- Testimonials — all six are samples (see below)

The quote forms currently open the visitor's email app with the request filled in. To receive
submissions directly, point the forms at a form service (e.g. Formspree or Netlify Forms).

## Single-file versions
After editing `index.html`, `css/` or `js/`, rebuild both with `python3 tools/build.py` (needs Pillow):

- `gohighlevel/rydesmart-ghl.html` — paste-in snippet for a GoHighLevel **Custom JS/HTML** element.
  Classes and ids are prefixed with `rs-` and the CSS only applies inside `<div id="rs-site">`, so it
  won't clash with the page builder. It loads GSAP from jsDelivr at runtime, and stretches itself to
  the full window width even inside a builder's centred row. In GoHighLevel, also set the section's
  top/bottom padding to 0 so there's no white strip above or below the site.
- `dist/rydesmart-logistics.html` — the full page with every asset (GSAP included) inlined.
