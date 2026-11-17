# RydeSmart Logistics Website

Carrier website for **RydeSmart Logistics** — *Driven by safety. Focused on delivery.*
Built for freight brokers and shippers to verify the company, review equipment and lanes, and request
capacity, plus CDL driver recruiting.

**Status: preview.** Company facts that aren't confirmed yet show as *To be confirmed*. See
[`docs/INFO-NEEDED.md`](docs/INFO-NEEDED.md) for the exact list.

## Pages
Home · Fleet & equipment · Lanes & service areas · Broker & shipper resources · Request capacity · About ·
Careers · Contact (+ 404). Paths: `/`, `/fleet`, `/lanes`, `/broker-resources`, `/request-capacity`,
`/about`, `/careers`, `/contact`.

## Updating content (no design work needed)
Edit the plain-text files in `content/`, then rebuild:

| File | What's in it |
|---|---|
| `content/company.yml` | Name, legal name, USDOT, MC, phone, email, address, hours, insurance limits, departments, leadership, form/CRM settings, **preview/launch switch** |
| `content/equipment.yml` | Equipment cards (type, specs, freight, status, photo) |
| `content/lanes.yml` | States served, corridors, preferred lanes (drawn on the map) |
| `content/testimonials.yml` | Reviews — `verified: true` only for genuine, approved reviews |
| `content/careers.yml` | Open positions, requirements, FAQ |

```bash
pip install jinja2 pyyaml pillow     # once
python3 tools/build.py               # rebuilds site/ and gohighlevel/
```
Set `show_placeholders: false` in `content/company.yml` to launch: placeholders, examples, sample reviews and
the preview banner disappear, and search indexing turns on.

## Publishing
- **GoHighLevel:** `gohighlevel/` has one file per page. Create a GHL page with the matching path, add a
  Custom JS/HTML element, paste the file, set the section/row to full width with 0 padding, and copy the SEO
  title/description from `gohighlevel/PAGES.md`.
- **Any static host:** deploy the `site/` folder (Netlify, Cloudflare Pages, GitHub Pages via Actions).

## Forms
Capacity requests, document requests and contact messages validate input, show sending/success/error states,
prevent duplicates and include a reference number, timestamp and lead source. Connect them to GoHighLevel with
an Inbound Webhook or GHL forms — see [`docs/forms-setup.md`](docs/forms-setup.md). Until then they open the
visitor's email app addressed to Admin@rydesmartlogistics.com. The CDL application uses the existing
GoHighLevel form.

## Project layout
```
content/         editable company data (YAML)
src/templates/   page templates          src/css/  styles      src/js/  main.js + vendor/GSAP
src/assets/      logos, scene art        src/data/ US map data
tools/build.py   build script            tools/cities.py  map coordinates for lane cities
site/            built website (deploy)  gohighlevel/     paste-in snippets per page
docs/            audit, research, architecture, testing, roadmap, forms setup, info needed
```

## Documents
1. [Audit of the previous site](docs/01-audit.md)
2. [Research summary](docs/02-research.md)
3. [Architecture & user journeys](docs/03-architecture.md)
4. [Testing report](docs/04-testing.md)
5. [Roadmap](docs/05-roadmap.md)
- [Forms setup](docs/forms-setup.md) · [Company details needed](docs/INFO-NEEDED.md)

Third-party: GSAP 3.15.0 (GreenSock standard no-charge license), US state outlines from us-atlas (public domain,
US Census data).
