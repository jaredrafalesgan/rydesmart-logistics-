# 4. Functional testing report

Tested November 2026 with Playwright (Chromium) against the built `site/` served locally, at 1440×900 and
390×844, plus each GoHighLevel snippet inside a page that mimics GoHighLevel's centered rows and conflicting
global styles. GoHighLevel's servers, FMCSA sites and Google Fonts aren't reachable from the build environment,
so those endpoints were stubbed; see "Not verifiable here".

## Results
| Area | Check | Result |
|---|---|---|
| Pages | All 8 pages + 404 render; no JavaScript errors; no horizontal scroll at 1440 / 390 px | Pass |
| Links | 14 internal links and in-page anchors resolve (incl. `/broker-resources#documents`) | Pass |
| Navigation | Current page marked (`aria-current`); mobile menu opens and navigates | Pass |
| Capacity form | Empty submit flags all 10 required fields and focuses the first | Pass |
| | Invalid email and past pickup date rejected with messages | Pass |
| | Without webhook: success panel with reference (`RSL-YYMMDD-XXXX`), timestamp, email-app fallback | Pass |
| | With webhook: one JSON POST containing type, reference, timestamp, page, fields, contact keys | Pass |
| | Lead source (UTM tags, referrer, landing page) included | Pass |
| | Spam-trap field never sent; identical re-submission blocked (no 2nd POST); double-click sends once | Pass |
| | Webhook failure: error message + "Send by email instead", button re-enabled, form kept | Pass |
| | Lane/equipment links pre-fill origin, destination and equipment | Pass |
| Document request | Requires at least one document; validation; same submission pipeline | Pass |
| Contact form | Department select; same pipeline | Pass |
| Fleet | Category filter shows matching cards, `aria-pressed` updated | Pass |
| Lanes | State filter; hovering a lane highlights its arc; state tooltip | Pass |
| Careers | "Apply now" opens the driver application pop-up; inline embed present | Pass |
| Home animation | Truck journey pins and scrubs; with reduced motion it renders static with all panels visible | Pass |
| Accessibility | axe-core (WCAG 2 A/AA + best practice) on all 9 pages | 0 violations |
| Preview vs launch | Launch build has no "To be confirmed", examples, sample reviews, preview bar or `noindex`; robots allows | Pass |
| SEO | Unique title/description, canonical, Open Graph, JSON-LD (confirmed facts only), sitemap (8 URLs), robots | Pass |
| GoHighLevel | All 8 snippets: full width, prefixed classes, host styles don't leak, labels intact, features work | Pass |

## Performance notes
- Home HTML 127 KB uncompressed (includes the map and truck artwork inline; ~30 KB gzipped); other pages 11–90 KB.
- Shared CSS 56 KB, JS 33 KB. GSAP (114 KB) now loads **only on the homepage** (previously every page).
- No large photos yet. When adding fleet photos, export ~1600 px wide JPG/WebP under 250 KB; they lazy-load.

## Not verifiable here (needs the live accounts)
- **GoHighLevel webhook delivery and CORS** — test with one submission after adding the URL (`forms-setup.md`, step 4).
- **GoHighLevel form embeds** — the driver form URL is configured; it renders in GHL/production only.
- **FMCSA links** — SAFER/SMS deep links activate once a USDOT number is entered; confirm they open your record.
- **Fonts** — Google Fonts load in production; tests used a local copy.
- **Confirmation emails, notifications, CRM records** — configured inside GoHighLevel workflows.

## Re-running the tests
`python3 tools/build.py`, serve `site/` (`python3 -m http.server -d site 8765`), then repeat the checks above.
