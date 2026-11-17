# 1. Audit of the previous website

Audited before this rebuild (commit `5ba605d`): a single static page (`index.html` + `css/` + `js/`),
GSAP scroll animation, a testimonial carousel, and a GoHighLevel paste-in version.

## What was already good (kept)
- **Brand system** — logo-derived navy/royal blue, Saira + Inter type, slanted buttons. Kept, with an amber
  action accent added for primary buttons.
- **"Why RydeSmart" truck journey** — scroll-driven, pinned, reduced-motion safe. Kept on the homepage; panel
  copy rewritten to remove unconfirmed claims.
- **Testimonial carousel** — smooth, accessible, pause/drag/keyboard. Kept; now data-driven with sample labeling.
- **Driver application pop-up** — GoHighLevel form in a native `<dialog>`. Kept and reused on the new Careers page.
- **GoHighLevel build pipeline** — CSS scoping, `rs-` prefixing, full-width breakout. Kept and extended to every page.
- Responsive layout, sticky header, tap-to-call button, phone/email in the top bar.

## What was missing
| Gap | Why it matters to a broker |
|---|---|
| No USDOT / MC numbers (only `#0000000` placeholders) | The first thing a broker checks; without them the site can't be matched to FMCSA |
| No link to FMCSA SAFER / L&I | Verification takes extra searching |
| No equipment information | Can't tell if you fit the load |
| No lanes or service area | Can't tell if you run their lanes |
| No broker resources / document process | Carrier setup needs W-9, COI and a packet |
| Single page — no About, Fleet, Lanes, Careers, Contact pages | Thin presence; nothing to link or index per topic |
| No SEO basics: canonical, Open Graph, structured data, sitemap, robots | Weak search/social presence |

## What was inaccurate or unsupported (removed or made placeholders)
| Previous content | Problem | Now |
|---|---|---|
| "98% on-time", "48 states covered", "24/7 live dispatch", "1 hr quote response" | Invented statistics | Removed; replaced by a credentials snapshot |
| "Serving all 48 contiguous states" | Unconfirmed coverage | Coverage comes from `content/lanes.yml` |
| "Fully insured & DOT compliant", "Fully Insured Cargo" | Unconfirmed insurance/compliance claims | Insurance limits are placeholders; certificate requests go through a form |
| "Real-time GPS tracking", "Live Shipment Tracking" | Implies a tracking system that isn't connected | "Proactive shipment updates" (a communication commitment) |
| Six services (FTL, LTL, expedited, dedicated, power only, final mile), "53' dry van and reefer capacity" | Unconfirmed services/equipment | Equipment from `content/equipment.yml`; examples clearly labeled |
| Industries list | Unconfirmed | Removed |
| Six testimonials shown as real (label removed) | Fictional reviews presented as genuine | Labeled "Sample review" in preview mode; removed automatically at launch |
| "Mon–Fri 7am–7pm", "Competitive weekly pay" | Unconfirmed | Placeholders |

## What didn't function well
- **Forms** only opened the visitor's email client (`mailto:`): nothing stored, no confirmation, no CRM.
- **Hero "Quick Quote"** collected four fields into the same mailto flow.
- GSAP (117 KB) loaded on every page view, though only one section needed it.
- In the GoHighLevel version, `aria-labelledby` references broke after id prefixing.
- Accessibility: some low-contrast text and heading-order issues (fixed — see testing report).

## Improvement plan (implemented)
1. Split into eight pages sharing one layout: Home, Fleet, Lanes, Broker Resources, Request Capacity, About,
   Careers, Contact (+ 404).
2. Move company facts, equipment, lanes, testimonials and careers into editable `content/*.yml`, with a
   preview/launch switch for placeholders.
3. Build broker-first features: carrier snapshot, FMCSA verification links, document requests, fraud-prevention
   guidance, coverage map, lane directory with "Request capacity on this lane".
4. Replace mailto forms with validated inquiry forms that post to GoHighLevel (webhook) or embed GHL forms, with
   email fallback.
5. SEO: per-page titles/descriptions, canonical URLs, Open Graph, JSON-LD (confirmed facts only), sitemap, robots.
6. Generate GoHighLevel paste-in snippets for every page.
