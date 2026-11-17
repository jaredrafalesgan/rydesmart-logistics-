"""Build the RydeSmart Logistics website.

    python3 tools/build.py            (needs: pip install jinja2 pyyaml pillow)

Reads   content/*.yml          company details, equipment, lanes, testimonials, careers
        src/templates/         page templates (Jinja)
        src/css, src/js, src/assets, src/data
Writes  site/                  the complete static website — deploy this folder
                               (clean URLs: /fleet, /lanes, … as folder/index.html)
        gohighlevel/<page>.html one paste-in snippet per page for GoHighLevel
                               "Custom JS/HTML" elements, plus gohighlevel/PAGES.md

GoHighLevel snippets: GHL drops custom code into the middle of its own page, so each
snippet has no <html>/<head>/<body>, every class and id is prefixed "rs-", all CSS is
scoped to #rs-site, and the CSS, JS, scene art and logos are inlined. GSAP (home page
only) is loaded from jsDelivr at runtime.
"""
import base64
import datetime as dt
import io
import json
import math
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from cities import CITIES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
SITE = ROOT / "site"
GHL = ROOT / "gohighlevel"
P = "rs-"
SCOPE = "#rs-site"

# slug, template, nav label, <title>, meta description
PAGES = [
    ("", "home", None,
     "{name} | Reliable Freight Transportation & Trucking",
     "{name} provides dependable truckload freight transportation with professional communication. "
     "Request capacity, review our fleet and lanes, and verify our credentials."),
    ("fleet", "fleet", "Fleet",
     "Fleet & Equipment | {name}",
     "Equipment {name} runs: trailer types, specifications, freight capabilities and availability."),
    ("lanes", "lanes", "Lanes",
     "Lanes & Service Areas | {name}",
     "Preferred lanes, states served and freight corridors for {name}. Request capacity on a lane."),
    ("broker-resources", "resources", "Broker Resources",
     "Broker & Shipper Resources | {name}",
     "USDOT and MC numbers, FMCSA verification links, insurance certificate and carrier packet requests for {name}."),
    ("about", "about", "About",
     "About Us | {name}",
     "{name} is a freight transportation carrier focused on safety, clear communication and long-term partnerships."),
    ("careers", "careers", "Careers",
     "CDL-A Driver Jobs | {name}",
     "Drive with {name}. Open CDL-A positions, requirements, and our online driver application."),
    ("contact", "contact", "Contact",
     "Contact | {name}",
     "Contact {name}: freight and capacity, broker setup and documents, driver recruiting."),
    ("request-capacity", "request", None,
     "Request Freight Capacity or a Quote | {name}",
     "Request truckload capacity or a freight quote from {name}. Send lane, dates, equipment and commodity."),
]
NOT_FOUND = ("404", "404", None, "Page not found | {name}", "The page you were looking for could not be found.")


# ---------------------------------------------------------------- content
def load_content():
    c = {}
    for name in ("company", "equipment", "lanes", "testimonials", "careers"):
        c[name] = yaml.safe_load((ROOT / "content" / f"{name}.yml").read_text()) or {}
    return c


def blank(v):
    return "" if v is None else v


def albers(lon, lat, proj):
    """d3.geoAlbers() with the scale/translate fitted in src/data/us-states.json."""
    p0, p1 = math.radians(29.5), math.radians(45.5)
    n = (math.sin(p0) + math.sin(p1)) / 2
    c = 1 + math.sin(p0) * (2 * n - math.sin(p0))
    r0 = math.sqrt(c) / n

    def raw(lam, phi):
        r = math.sqrt(c - 2 * n * math.sin(phi)) / n
        return r * math.sin(lam * n), r0 - r * math.cos(lam * n)

    cx, cy = raw(math.radians(-0.6), math.radians(38.7))
    x, y = raw(math.radians(lon + 96), math.radians(lat))
    k, (tx, ty) = proj["scale"], proj["translate"]
    return round(tx + k * (x - cx), 1), round(ty - k * (y - cy), 1)


def city_point(name, coords, proj):
    if coords:
        lat, lon = coords
    elif name in CITIES:
        lat, lon = CITIES[name]
    else:
        sys.exit(f"content/lanes.yml: no map location for '{name}'. Add coords, e.g. origin_coords: [33.75, -84.39]")
    return albers(lon, lat, proj)


def arc(a, b):
    """Gentle curve between two map points (bulging to the left of travel)."""
    (x1, y1), (x2, y2) = a, b
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    bend = 0.18
    return f"M{x1} {y1}Q{round(mx - dy * bend, 1)} {round(my + dx * bend, 1)} {x2} {y2}"


def build_context(c):
    company_file = c["company"]
    show = bool(company_file.get("show_placeholders"))
    company = company_file["company"]
    company["primary_contact"] = {k: str(blank(v)) for k, v in (company.get("primary_contact") or {}).items()}
    for k in ("name", "title", "email", "phone"):
        company["primary_contact"].setdefault(k, "")
    for k in ("legal_name", "dba", "usdot", "mc", "home_base", "hours", "after_hours", "founded"):
        company[k] = str(blank(company.get(k))).strip()
    addr = company.get("address") or {}
    street, city, state, zp = (str(blank(addr.get(k))).strip() for k in ("street", "city", "state", "zip"))
    address_line = ", ".join(x for x in (street, city, " ".join(x for x in (state, zp) if x)) if x)
    site = company_file["site"]
    integrations = company_file.get("integrations") or {}
    integrations.setdefault("ghl_forms", {})
    for k in ("capacity", "documents", "contact", "driver_application"):
        integrations["ghl_forms"][k] = blank(integrations["ghl_forms"].get(k))
    integrations["inquiry_webhook_url"] = blank(integrations.get("inquiry_webhook_url"))
    insurance = {k: str(blank((company_file.get("insurance") or {}).get(k))) for k in ("auto_liability", "cargo", "agent")}

    depts = []
    for d in company_file.get("departments") or []:
        d = {k: blank(v) for k, v in d.items()}
        d["phone_e164"] = "+1" + re.sub(r"\D", "", d["phone"])[-10:] if d["phone"] else ""
        depts.append(d)

    def dept_email(key):
        for d in depts:
            if d["key"] == key and d["email"]:
                return d["email"]
        return company["email"]

    # equipment
    equipment = []
    for e in c["equipment"].get("equipment") or []:
        if e.get("example") and not show:
            continue
        e["specs"] = {k: str(blank(v)) for k, v in (e.get("specs") or {}).items()}
        for k in ("photo", "status", "units", "category"):
            e[k] = str(blank(e.get(k)))
        e["freight"], e["features"] = e.get("freight") or [], e.get("features") or []
        equipment.append(e)
    eq_names = {e["id"]: e["name"] for e in equipment}
    categories = sorted({e["category"] for e in equipment if e["category"]})

    # lanes + map
    usmap = json.loads((SRC / "data" / "us-states.json").read_text())
    proj = usmap["projection"]
    lanes_file = c["lanes"]
    coverage = lanes_file.get("coverage") or {}
    coverage = {k: blank(coverage.get(k)) for k in ("scope", "summary", "home_base", "states")}
    coverage["states"] = [s.upper() for s in coverage["states"] or []]
    lanes, cities = [], {}
    for lane in lanes_file.get("lanes") or []:
        if lane.get("example") and not show:
            continue
        a = city_point(lane["origin"], lane.get("origin_coords"), proj)
        b = city_point(lane["destination"], lane.get("destination_coords"), proj)
        lane["arc"] = arc(a, b)
        lane["frequency"] = str(blank(lane.get("frequency")))
        lane["notes"] = str(blank(lane.get("notes")))
        lane["equipment"] = lane.get("equipment") or []
        lane["equipment_names"] = [eq_names.get(x, x) for x in lane["equipment"]]
        lane["states"] = [x.split(",")[-1].strip() for x in (lane["origin"], lane["destination"])]
        for name, pt in ((lane["origin"], a), (lane["destination"], b)):
            prev = cities.get(name)
            cities[name] = {"x": pt[0], "y": pt[1], "label": name.split(",")[0],
                            "example": bool(lane.get("example")) and (prev is None or prev["example"])}
        lanes.append(lane)
    home = coverage["home_base"] or company["home_base"]
    home_state = home.split(",")[-1].strip().upper() if "," in home else ""
    lane_states = sorted({s for lane in lanes for s in lane["states"]})

    # testimonials: verified always; samples only in preview
    testimonials = []
    for t in c["testimonials"].get("testimonials") or []:
        if not t.get("verified") and not show:
            continue
        t = {**{k: str(blank(t.get(k))) for k in ("quote", "name", "title", "company", "location")},
             "verified": bool(t.get("verified"))}
        t["initials"] = "".join(w[0] for w in t["name"].split()[:2]).upper()
        testimonials.append(t)

    careers = c["careers"]
    positions = [p for p in careers.get("positions") or []
                 if (p.get("status") or "open") == "open" and (show or not p.get("example"))]
    for p in positions:
        for k in ("type", "route", "equipment", "pay", "home_time"):
            p[k] = str(blank(p.get(k)))
    careers["requirements"] = careers.get("requirements") or []
    careers["what_to_expect"] = careers.get("what_to_expect") or []
    faqs = [f for f in careers.get("faqs") or [] if f.get("a")]

    base = (site.get("base_path") or "").rstrip("/")

    def url(slug):
        return f"{base}/{slug}" if slug else f"{base}/"

    def asset(path):
        return f"{base}/{path}"

    def abs_url(path):
        return site["url"].rstrip("/") + asset(path) if not path.startswith("http") else path

    usdot, mc = company["usdot"], company["mc"]
    fmcsa = {
        "safer_home": "https://safer.fmcsa.dot.gov/CompanySnapshot.aspx",
        "safer_dot": f"https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string={usdot}",
        "safer_mc": f"https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=MC_MX&query_string={mc}",
        "sms": f"https://ai.fmcsa.dot.gov/SMS/Carrier/{usdot}/CarrierOverview.aspx",
        "li": "https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist",
    }
    map_embed = ("https://www.google.com/maps?output=embed&q=" + quote(address_line)) if street and city else ""

    return dict(
        show_placeholders=show, company=company, site=site, integrations=integrations, insurance=insurance,
        address_line=address_line, departments=depts, dept_email=dept_email,
        email_domain=company["email"].split("@")[-1].lower(),
        equipment=equipment, categories=categories,
        equipment_options=[e["name"] for e in equipment if not e.get("example")] + (
            ["53' Dry Van"] if show and not any(not e.get("example") for e in equipment) else []) + ["Other / not sure"],
        usmap=usmap, coverage=coverage, lanes=lanes, lane_cities=list(cities.values()),
        real_lanes=[x for x in lanes if not x.get("example")], example_lanes=[x for x in lanes if x.get("example")],
        home_state=home_state, lane_states=lane_states, corridors=lanes_file.get("corridors") or [],
        testimonials=testimonials, sample_testimonials=any(not t.get("verified") for t in testimonials),
        careers=careers, positions=positions, faqs=faqs,
        leadership=[{k: str(blank(v)) for k, v in x.items()} for x in company_file.get("leadership") or [] if x.get("name")],
        fmcsa=fmcsa, map_embed=map_embed, url=url, asset=asset, abs_url=abs_url,
        year=dt.date.today().year,
        nav=[(slug, label) for slug, _, label, _, _ in PAGES if label],
    )


def jsonld(ctx, slug):
    """Structured data using confirmed details only."""
    co, site = ctx["company"], ctx["site"]
    org = {
        "@context": "https://schema.org", "@type": "Organization",
        "name": co["name"], "url": site["url"], "logo": ctx["abs_url"]("assets/logo.png"),
        "email": co["email"], "telephone": co["phone_e164"],
        "slogan": co["tagline"],
    }
    if co["legal_name"]:
        org["legalName"] = co["legal_name"]
    if co["usdot"]:
        org["identifier"] = [{"@type": "PropertyValue", "propertyID": "USDOT", "value": co["usdot"]}]
        if co["mc"]:
            org["identifier"].append({"@type": "PropertyValue", "propertyID": "MC", "value": co["mc"]})
    addr = co.get("address") or {}
    if addr.get("street") and addr.get("city"):
        org["address"] = {"@type": "PostalAddress", "streetAddress": addr["street"], "addressLocality": addr["city"],
                          "addressRegion": addr.get("state") or "", "postalCode": str(addr.get("zip") or ""),
                          "addressCountry": "US"}
    if ctx["coverage"]["states"]:
        org["areaServed"] = [{"@type": "State", "name": ctx["usmap"]["states"][s]["name"]}
                             for s in ctx["coverage"]["states"] if s in ctx["usmap"]["states"]]
    blocks = [org] if slug in ("", "about", "contact", "broker-resources") else []
    if slug == "careers" and ctx["faqs"]:
        blocks.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in ctx["faqs"]]})
    return blocks


# ---------------------------------------------------------------- static site
def render_site(ctx):
    env = Environment(loader=FileSystemLoader(SRC / "templates"), undefined=StrictUndefined,
                      autoescape=True, trim_blocks=False, lstrip_blocks=False)
    env.globals.update(ctx)
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    pages = {}
    name = ctx["company"]["name"]
    for slug, tpl, _label, title, desc in PAGES + [NOT_FOUND]:
        path = "" if slug in ("", "404") else slug
        page = dict(
            slug="" if slug == "404" else slug, title=title.format(name=name),
            og_title=title.format(name=name).split(" | ")[0] if slug else name,
            description=desc.format(name=name),
            canonical=ctx["site"]["url"].rstrip("/") + ctx["url"](path),
            gsap=(slug == ""), jsonld=jsonld(ctx, slug),
        )
        html = env.get_template(f"pages/{tpl}.html").render(page=page)
        html = re.sub(r"\n\s*\n+", "\n", html)  # tidy blank lines left by template tags
        out = SITE / (f"{slug}/index.html" if slug and slug != "404" else ("404.html" if slug == "404" else "index.html"))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html)
        pages[slug] = (page, html)
    for d in ("css", "js", "assets"):
        shutil.copytree(SRC / d, SITE / d)
    make_og_image(ctx)

    urls = [p["canonical"] for s, (p, _) in pages.items() if s != "404"]
    today = dt.date.today().isoformat()
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    (SITE / "robots.txt").write_text(
        ("User-agent: *\nDisallow: /\n# Preview mode (show_placeholders: true) — indexing disabled until launch.\n"
         if ctx["show_placeholders"] else "User-agent: *\nAllow: /\n")
        + f"Sitemap: {ctx['site']['url'].rstrip('/')}/sitemap.xml\n")
    return pages


def make_og_image(ctx):
    """1200x630 social share image from the logo, if one doesn't exist."""
    src = SRC / ctx["site"]["og_image"]
    if not src.exists():
        img = Image.new("RGB", (1200, 630), (10, 22, 54))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 600, 1200, 630], fill=(10, 90, 224))
        logo = Image.open(SRC / "assets/logo-light.png").convert("RGBA")
        logo = logo.resize((900, round(logo.height * 900 / logo.width)), Image.LANCZOS)
        img.paste(logo, ((1200 - logo.width) // 2, 200), logo)
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
        except OSError:
            font = ImageFont.load_default()
        text = "Reliable freight. Professional service."
        w = d.textlength(text, font=font)
        d.text(((1200 - w) / 2, 420), text, fill=(200, 212, 240), font=font)
        img.save(src, optimize=True)
    shutil.copy(src, SITE / ctx["site"]["og_image"])


# ---------------------------------------------------------------- GoHighLevel snippets
def prefix_classes(selector):
    return re.sub(r"\.([a-zA-Z_][\w-]*)", lambda m: "." + P + m.group(1), selector)


def scope_selector(sel):
    sel = sel.strip()
    if sel in (":root", "body"):
        return SCOPE
    if sel == "*":
        return SCOPE + ", " + SCOPE + " *"
    if sel.startswith("*::"):
        return SCOPE + " " + sel
    if sel.startswith("body."):  # page-specific body class -> same class on the wrapper
        return SCOPE + prefix_classes(sel[4:])
    return SCOPE + " " + prefix_classes(sel)


def scope_css(css):
    out, i = [], 0
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    while i < len(css):
        brace = css.find("{", i)
        if brace == -1:
            break
        head = css[i:brace].strip()
        depth, j = 1, brace + 1
        while depth:
            depth += {"{": 1, "}": -1}.get(css[j], 0)
            j += 1
        body = css[brace + 1:j - 1]
        if head.startswith("@media") or head.startswith("@supports"):
            out.append(head + " {\n" + scope_css(body) + "}")
        elif head.startswith("@keyframes"):
            out.append(head.replace("lane", P + "lane") + " {" + body + "}")
        elif head == "html":
            out.append("html {" + body + "}")
        else:
            sels = ", ".join(scope_selector(s) for s in head.split(","))
            out.append(sels + " {" + body.replace("animation: lane", "animation: " + P + "lane") + "}")
        i = j
    return "\n".join(out) + "\n"


def prefix_html(html):
    html = re.sub(r'class="([^"]*)"', lambda m: 'class="' + " ".join(P + c for c in m.group(1).split()) + '"', html)
    html = re.sub(r'\b(id|aria-controls|aria-labelledby|aria-describedby|for)="([^"]+)"',
                  lambda m: m.group(1) + '="' + " ".join(P + x for x in m.group(2).split()) + '"', html)
    html = re.sub(r'href="#([^"]+)"', lambda m: 'href="#' + P + m.group(1) + '"', html)
    html = re.sub(r'href="(/[^"#]*)#([^"]+)"', lambda m: f'href="{m.group(1)}#{P}{m.group(2)}"', html)
    html = html.replace("url(#", "url(#" + P)
    return html


def inline_css_urls(css):
    def repl(m):
        data = (SRC / m.group(1)).read_bytes()
        return 'url("data:image/svg+xml;base64,' + base64.b64encode(data).decode() + '")'
    return re.sub(r'url\("\.\./(assets/[^"]+\.svg)"\)', repl, css)


def data_uri(path, width):
    im = Image.open(path).convert("RGBA")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.quantize(colors=96, method=Image.Quantize.FASTOCTREE).save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def build_ghl(ctx, pages):
    if GHL.exists():
        shutil.rmtree(GHL)
    GHL.mkdir()
    css = scope_css((SRC / "css/styles.css").read_text())
    css = inline_css_urls(css)
    css += (SCOPE + " { position: relative; width: 100vw; max-width: none; margin-left: calc(50% - 50vw); margin-right: 0; }\n"
            "body { overflow-x: clip; }\n")
    js = (SRC / "js/main.js").read_text()
    assert 'var P = "";' in js
    js = js.replace('var P = "";', 'var P = "' + P + '";', 1)
    logo = data_uri(SRC / "assets/logo.png", 520)
    logo_light = data_uri(SRC / "assets/logo-light.png", 520)
    base = ctx["url"]("").rstrip("/")
    fonts = re.search(r'<link href="https://fonts.googleapis.com[^>]+>', pages[""][1]).group(0)
    rows = []
    for slug, (page, html) in pages.items():
        if slug == "404":
            continue
        body = html.split("<body", 1)[1].split(">", 1)[1].split("</body>", 1)[0]
        body = re.sub(r'\s*<script src="[^"]+"></script>', "", body).strip()
        body = prefix_html(body)
        body = body.replace(f'"{base}/assets/logo.png"', f'"{logo}"').replace(f'"{base}/assets/logo-light.png"', f'"{logo_light}"')
        body = body.replace('width="722" height="139"', 'width="520" height="100"')
        ld = "".join(f'<script type="application/ld+json">{json.dumps(b)}</script>\n' for b in page["jsonld"])
        cls = P + "page-" + (slug or "home")
        snippet = (
            f"<!-- {ctx['company']['name']} — {page['title']} — paste into a GoHighLevel Custom JS/HTML element -->\n"
            + fonts + "\n<style>\n" + css + "</style>\n" + ld
            + f'<div id="rs-site" class="{cls}">\n' + body + "\n</div>\n"
            + "<script>\n" + js + "</script>\n")
        leftover = re.findall(rf'(?:src|href)="{re.escape(base)}/assets/[^"]+"', snippet)
        assert not [x for x in leftover if not x.endswith('.jpg"') and not x.endswith('.png"')], leftover
        name = (slug or "home") + ".html"
        (GHL / name).write_text(snippet)
        rows.append((slug, name, page, len(snippet) // 1024))
    lines = [
        "# GoHighLevel pages", "",
        "Create one page per row in your GoHighLevel website/funnel with the **exact path** shown,",
        "add a **Custom JS/HTML** element to it, and paste the whole file into the element.",
        "Set the section and row to full width with 0 padding. Copy the title and description into the",
        "page's SEO settings.", "",
        "Images you add to `src/assets/` (e.g. fleet photos) must also be uploaded to GoHighLevel Media",
        "or hosted at the same paths on your domain.", "",
        "| Path | File | SEO title | SEO description | Size |", "|---|---|---|---|---|",
    ]
    for slug, name, page, kb in rows:
        lines.append(f"| `/{slug}` | `{name}` | {page['title']} | {page['description']} | {kb} KB |")
    (GHL / "PAGES.md").write_text("\n".join(lines) + "\n")
    return rows


def main():
    ctx = build_context(load_content())
    pages = render_site(ctx)
    rows = build_ghl(ctx, pages)
    mode = "PREVIEW (placeholders shown, indexing off)" if ctx["show_placeholders"] else "LIVE"
    print(f"site/: {len(pages)} pages · gohighlevel/: {len(rows)} snippets · mode: {mode}")
    for slug, name, _, kb in rows:
        print(f"  /{slug:<18} gohighlevel/{name:<24} {kb} KB")


if __name__ == "__main__":
    main()
