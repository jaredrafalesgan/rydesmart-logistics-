# 3. Website architecture

## Sitemap
```
/                     Home — hero + carrier snapshot, intro, equipment, coverage map, why us (truck journey),
                      process, verification band, testimonials, careers teaser, final CTA
├── /fleet            Fleet & equipment directory (filters by category)
├── /lanes            Coverage map, coverage summary, corridors, lane directory (filter by state)
├── /broker-resources Identification, FMCSA links, insurance, document request form, fraud prevention, reviews
├── /request-capacity Capacity / quote request form (pre-fill from lane & equipment links)
├── /about            Story, mission/vision, values, business approach, leadership, location
├── /careers          Positions, requirements, how to apply, application (inline + pop-up), FAQ
├── /contact          Department cards, contact form, company details, credentials
└── /404
sitemap.xml · robots.txt
```
Header on every page: Fleet · Lanes · Broker Resources · About · Careers · Contact · **Request Capacity**.
Top bar on every page: USDOT · MC · email · phone. Footer: credentials, page links, contact.

## User journeys
**Freight broker (evaluating a new carrier)**
Search "RydeSmart Logistics" → Home: carrier snapshot shows legal name, USDOT, MC, address, phone, email above
the fold → "Verify on FMCSA SAFER" opens the official record → Fleet / Lanes confirm equipment and coverage →
Broker Resources: request carrier packet / COI → Request Capacity with a specific load. Every step is ≤ 2 clicks
from the header.

**Shipper (direct freight)**
Home → "Request Freight Capacity" (or a lane row's "Request capacity", which pre-fills origin, destination,
equipment) → form → reference number and confirmation → follow-up from dispatch.

**Existing business partner**
Header phone/email on every page → Contact: the right department → or Broker Resources for refreshed
documents (COI renewal) → or Request Capacity for a new load.

**CDL applicant**
Home "Drive with RydeSmart" or header "Careers" → positions, requirements, FAQ → "Apply now" opens the
GoHighLevel application in a pop-up (also embedded on the page). Kept separate from freight inquiries.

## How it's built
```
content/*.yml         editable facts: company, equipment, lanes, testimonials, careers
src/templates/        Jinja templates (base layout, macros, one file per page, partials)
src/css, src/js       styles and behavior (one main.js; GSAP vendored for the homepage only)
src/assets, src/data  images, scene art, US state map data
tools/build.py        builds site/ and gohighlevel/
site/                 deployable static website (clean URLs)
gohighlevel/          one paste-in snippet per page + PAGES.md (paths, SEO titles/descriptions)
docs/                 these documents
```
- **Placeholders by design.** Empty facts render as "To be confirmed" while `show_placeholders: true` and
  disappear when it's `false`. Example equipment/lanes and unverified testimonials are dropped automatically at
  launch, and search indexing is turned off until then.
- **No credentials in the frontend.** The only integration value is the GoHighLevel webhook URL (public by
  nature, like any form endpoint) or public GHL form links.
- **Hosting options.** Either paste the GoHighLevel snippets into GHL pages with matching paths, or deploy
  `site/` to any static host (Netlify, Cloudflare Pages, GitHub Pages via Actions). Both use the same paths.
