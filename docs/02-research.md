# 2. Research summary

Research was done in November 2026. Direct page fetches of the large carriers' sites were blocked from the
build environment, so competitor findings come from search results describing those sites. Practitioner
sources on carrier vetting are mostly vendor blogs; they're cited as industry practice, not regulation.

## A. Established carriers' websites — what they do well
| Finding | Source | How it shaped this site |
|---|---|---|
| Navigation split by audience: **Shippers / Carriers / Drivers** | [Werner](https://werner.com/), [J.B. Hunt](https://www.jbhunt.com/) | Separate paths: brokers & shippers (Fleet, Lanes, Broker Resources, Request Capacity) vs drivers (Careers) |
| Quote CTA from the hero and from every service page ("Get Freight Quote", "Request an FTL quote") | [Werner quote page](https://werner.com/shippers/logistics), [Schneider truckload](https://schneider.com/freight-shipping-solutions/truckload) | "Request Capacity" in the header on every page; equipment cards and lane rows deep-link to a pre-filled request |
| Quote forms explain that more detail = more accurate quote; enterprise vs single-shipment paths | [Werner](https://werner.com/shippers/logistics), [J.B. Hunt quote](https://www.jbhunt.com/freight-shipping-solutions/request_quote/) | Request form grouped into contact / freight details with helpful placeholders |
| Contact pages route by audience (drivers, carriers, shippers, investors) | [Werner contact](https://werner.com/contact/), [Schneider contact](https://schneider.com/contact-us) | Contact page has department cards (freight, broker setup, drivers, general) |
| Driver recruiting kept separate from shipper content, often its own site | [Werner jobs](https://jobs.werner.com/), [Prime drivers](https://primeincdrivers.com/) | Dedicated Careers page with its own application flow (existing GHL form) |
| Fleet presented by mode with concrete counts and trailer types | [Prime transportation solutions](https://www.primeinc.com/transportation-solutions/) | Fleet page with type, specs, freight, availability and optional unit count — **only confirmed data** |
| Safety framed through practices and training, not just slogans | [Schneider dedicated](https://schneider.com/freight-shipping-solutions/dedicated) | Values/approach describe concrete practices; no unearned awards or ratings |

**Avoided:** large-carrier scale claims (fleet sizes, "largest"), portals/load boards a small carrier doesn't run,
and stock imagery of other companies' trucks.

## B. How brokers verify carriers
- Brokers confirm **active authority** and **MC/DOT** on SAFER, review **insurance** (limits, dates, cargo fit),
  check **safety** data (inspections, OOS rates, crashes), verify **identity** (phone/email match FMCSA records)
  and collect **W-9, COI and a broker-carrier agreement** before tendering
  ([LoadConnect](https://loadconnect.io/blog/carrier-vetting-checklist-10-checks-brokers-should-make),
  [Longmile](https://longmile.io/blog/carrier-verification-checklist-for-freight-brokers-before-dispatch),
  [Super Dispatch](https://superdispatch.com/blog/carrier-vetting-process/),
  [JustTracking](https://justtracking.net/blog/how-freight-brokers-find-and-vet-reliable-carriers),
  [Kingpost](https://kingpost.us/carrier-vetting/)).
- Certificates are best obtained **from the carrier's insurance agent**, not the carrier
  ([JustTracking](https://justtracking.net/blog/how-freight-brokers-find-and-vet-reliable-carriers)).
- New authority gets extra scrutiny; references help
  ([Direct Fleet Dispatch](https://directfleetdispatch.com/guides/carrier-vetting-checklist/)).
- **SAFER Company Snapshot** accepts direct query links by USDOT
  (`query.asp?query_type=queryCarrierSnapshot&query_param=USDOT&query_string=…`) or MC (`query_param=MC_MX`)
  ([SAFER example](https://safer.fmcsa.dot.gov/query.asp?query_type=queryCarrierSnapshot&query_param=USDOT&query_string=1364191),
  [data.gov](https://catalog.data.gov/dataset/safer-company-snapshot-safer-company-snapshot)).
- **L&I** carrier search is at [li-public.fmcsa.dot.gov](https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist);
  a stable deep-link parameter couldn't be confirmed, so the site links to the search page and shows the
  number to enter.
- **MC numbers still exist.** FMCSA has *proposed* moving to USDOT-only identification, but it's not final and
  wasn't part of Motus Phase II ([FMCSA Registration Modernization FAQ](https://www.fmcsa.dot.gov/registration/modernization-faqs)).
  Several blogs wrongly say MC numbers were eliminated.
- Small-carrier website guidance consistently says to show **USDOT/MC prominently (header and footer)**,
  equipment, lanes/states, a quote form and a real dispatch number — and to keep them current
  ([WebStackRank](https://webstackrank.com/blog/logistics-trucking-shipping-website-design),
  [Trucker Web Pro](https://truckerwebpro.com/best-website-for-owner-operators.html)).
- Carrier onboarding platforms (MyCarrierPackets, Highway, RMIS) are how many brokers collect packets
  ([CarrierAtlas overview](https://carrieratlas.com/carrier-packets.php)).

**Applied:** USDOT/MC in the top bar, hero snapshot, footer and Broker Resources; one-click SAFER and SMS links once
the USDOT is entered; L&I link; a "match our contact details" fraud-prevention section; document requests sent
privately (never public files); a note inviting onboarding-platform invitations; no badges implying FMCSA endorsement.

## C. Modern carrier-website functionality — now vs later
| Feature | Practical now? | Status |
|---|---|---|
| Carrier profile / credentials page | Yes | **Built** (Broker & Shipper Resources) |
| Capacity / quote request with CRM routing | Yes | **Built** (webhook or GHL form; email fallback) |
| Document request workflow | Yes | **Built** (request form → team/GHL workflow) |
| Equipment directory with filters | Yes | **Built** (data-driven, filters appear with 2+ categories) |
| Service-area map + lane directory | Yes | **Built** (states + lane arcs from `lanes.yml`) |
| Driver recruitment | Yes | **Built** (Careers + existing GHL application) |
| Testimonials | Yes, once verified | **Built** (samples hidden at launch) |
| Lead source tracking | Yes | **Built** (UTM/referrer in each submission) |
| Self-service document portal, broker accounts | Later | Roadmap phase 3 |
| Real-time capacity, tracking, load status | Only with a TMS/ELD integration | Roadmap phase 4 |

## D. GoHighLevel integration
- Inbound Webhook triggers accept JSON POSTs, need a sample request to map fields, and are a **premium**
  trigger; the URL acts as the only credential
  ([GHL help](https://help.gohighlevel.com/support/solutions/articles/155000003147-workflow-trigger-inbound-webhook),
  [WP Webhooks](https://wpwebhooks.org/blog/wordpress-gohighlevel-integration/)).
- Browser (CORS) behavior of the webhook isn't documented, so the site supports both the webhook and native
  GHL form embeds, plus an email fallback. See `forms-setup.md`.

## E. Search terms
Only use terms that match confirmed services and areas. Once confirmed, target combinations of:
company name ("RydeSmart Logistics", "RydeSmart Logistics USDOT"), service + equipment ("dry van carrier",
"truckload carrier", "53 ft dry van trucking") and confirmed geography ("[home city] trucking company",
"[state] dry van carrier", lane pairs such as "Atlanta to Charlotte freight"). Page titles and descriptions
are set per page; geographic terms are added automatically through the coverage data, not hard-coded.
