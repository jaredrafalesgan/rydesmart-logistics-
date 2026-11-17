# 5. Roadmap

Complexity: S (days) · M (1–3 weeks) · L (1–2 months) · XL (quarter+). Each phase depends on the previous one.

## Phase 1 — Professional carrier website (delivered, needs company details)
| Item | Status | Dependency |
|---|---|---|
| 8 pages, broker-first navigation, mobile, accessibility | Done | — |
| Carrier snapshot + FMCSA verification links | Done | USDOT/MC from company |
| Fleet directory, coverage map, lane directory | Done | Real equipment, states, lanes, photos |
| Capacity, document, contact forms | Done | Webhook or GHL forms (see `forms-setup.md`) |
| Driver recruitment | Done | Position details |
| Testimonials | Done | Verified reviews with permission |
| SEO: titles, descriptions, canonical, OG, JSON-LD, sitemap | Done | Confirm domain; `show_placeholders: false` |
| Google Business Profile, Search Console, sitemap submission | To do — S | Address, domain |

## Phase 2 — Business automation (GoHighLevel) — M, high value
- Connect forms (webhook workflow or GHL forms), contact creation, tags by inquiry type.
- Internal notifications (email/SMS) and requester confirmation emails.
- Pipeline "Freight inquiries" with stages: New → Quoted → Booked → Lost; owner assignment.
- Follow-up automation: no reply in 24 h → reminder; quoted but not booked in 3 days → check-in.
- Document request workflow: auto-reply with W-9/packet (stored in GHL, not on the website); COI request
  forwarded to the insurance agent template.
- Broker relationship tags (lanes, equipment, volume) for targeted capacity emails.
- Reporting dashboard in GHL: inquiries by source (UTM), by lane, response time, win rate.
*Dependencies:* GHL plan with workflows (Inbound Webhook is premium), a monitored inbox, document files.

## Phase 3 — Broker self-service portal — L, medium value
- Broker accounts (GHL Memberships/Client Portal or a small app with auth).
- Secure document library: current COI, W-9, authority letter, signed packet; expiration reminders when the
  COI renews.
- Inquiry history per broker; direct messaging with dispatch.
- Capacity notices: brokers opt in to lanes/equipment and get alerts when trucks open up.
*Dependencies:* authentication, file storage with access control, a process for keeping documents current.
Consider integrating with MyCarrierPackets/Highway profiles instead of duplicating them.

## Phase 4 — Advanced logistics capabilities — XL, depends on operations systems
- Load status / tracking links from the ELD or TMS (e.g. share-by-link from the ELD provider).
- Real-time truck availability feed (from dispatch/TMS) shown on the Lanes page.
- Lane performance reporting (on-time %, volume) — publish only measured data.
- Digital document management (BOL/POD capture, invoicing) and customer dashboards.
- Operational analytics (deadhead, revenue per mile) for internal use.
*Dependencies:* a TMS and ELD with APIs, data quality, and enough volume to justify it. Nothing here should be
shown publicly until it's connected to real data.

## Ongoing (monthly)
Update lanes/equipment/positions in `content/`, rebuild and re-publish; check SAFER shows current insurance;
add new verified reviews; review GHL inquiry reports.
