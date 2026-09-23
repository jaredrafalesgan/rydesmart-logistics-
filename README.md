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
- `js/main.js` — mobile menu, quote forms, scroll effects
- `assets/` — logo variants (`logo.png`, white-text `logo-light.png` for dark backgrounds) and favicon

## Placeholder info to replace before going live
- Phone: `(555) 123-4567` / `tel:+15551234567`
- Emails: `dispatch@rydesmartlogistics.com`, `careers@rydesmartlogistics.com` (also `QUOTE_EMAIL` in `js/main.js`)
- USDOT / MC numbers in the footer
- Stats (98% on-time, 48 states, 1 hr quote response), office hours and service list — confirm they're accurate

The quote forms currently open the visitor's email app with the request filled in. To receive
submissions directly, point the forms at a form service (e.g. Formspree or Netlify Forms).

## GoHighLevel version
`gohighlevel/rydesmart-ghl.html` is the whole site as a single paste-in snippet for a GoHighLevel
**Custom JS/HTML** element. Its classes and ids are prefixed with `rs-` and its CSS only applies inside
`<div id="rs-site">`, so it won't clash with the page builder. After editing `index.html`, `css/` or `js/`,
rebuild it with `python3 tools/build_ghl.py` (needs Pillow).
