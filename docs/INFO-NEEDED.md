# Company details needed before launch

The website never invents company facts. Everything below is currently shown as
**"To be confirmed"** (preview mode) or hidden (launch mode). Send these, or enter them in
the `content/` files, then run `python3 tools/build.py`.

## Must have (brokers look for these first)
| Item | Where it goes | Notes |
|---|---|---|
| Legal company name (exactly as on FMCSA) | `content/company.yml` → `legal_name` | e.g. "RydeSmart Logistics LLC" |
| USDOT number | `company.yml` → `usdot` | Turns on the direct SAFER / SMS verification links |
| MC (docket) number | `company.yml` → `mc` | MC numbers are still in use; FMCSA's proposal to drop them is not final |
| Business address | `company.yml` → `address` | Should match FMCSA registration. Enables the map on the Contact page |
| Equipment you actually run | `content/equipment.yml` | Type, count, specs, photos. Delete the two `example: true` entries |
| States served + preferred lanes | `content/lanes.yml` | Delete the three `example: true` lanes |
| GoHighLevel inbound webhook URL (or GHL form links) | `company.yml` → `integrations` | See `docs/forms-setup.md` — until then forms fall back to email |

## Should have
| Item | Where |
|---|---|
| Home base (e.g. "Atlanta, GA") | `company.yml` → `home_base`, `lanes.yml` → `coverage.home_base` |
| Business hours / after-hours dispatch | `company.yml` → `hours`, `after_hours` |
| Primary business contact (name, title) | `company.yml` → `primary_contact` |
| Insurance limits as shown on your COI, insurance agent | `company.yml` → `insurance` |
| Department emails (if different from Admin@) | `company.yml` → `departments` |
| Year established | `company.yml` → `founded` |
| Confirm the live domain | `company.yml` → `site.url` (currently www.rydesmartlogistics.com) |
| Your own fleet photos | `src/assets/fleet/…`, referenced from `equipment.yml` |
| Verified testimonials **with permission** | `content/testimonials.yml` (`verified: true`). The six current ones are samples |

## Careers
| Item | Where |
|---|---|
| Open positions: type, route, equipment, home time, pay | `content/careers.yml` → `positions` |
| Hiring requirements (experience, MVR, screening) | `careers.yml` → `requirements` |
| What drivers can expect (equipment, settlements, benefits) | `careers.yml` → `what_to_expect` |
| Owner-operators: yes / no | `careers.yml` → FAQ |

## Please confirm the wording
- Brand spelling: the logo reads **RydeSmart Logistics**; the brief says "Ride Smart Logistics". The site uses **RydeSmart**.
- Mission and vision statements on the About page are drafts for approval.
- Homepage intro describes the company as a truckload carrier for brokers and shippers — confirm that's accurate.

## Launch switch
When the details above are in, set `show_placeholders: false` in `content/company.yml`. That removes every
"To be confirmed" marker, example equipment/lanes, sample reviews and the preview banner, and allows search
engines to index the site.
