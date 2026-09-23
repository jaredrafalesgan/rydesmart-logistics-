"""Build single-file versions of the site.

1. gohighlevel/rydesmart-ghl.html — a snippet for a GoHighLevel "Custom JS/HTML"
   element. That element drops code into the middle of GHL's own page, so the snippet
   has no <html>/<head>/<body>, and its CSS must not leak into (or be overridden by)
   the builder's styles. So it:
     - wraps the page body in <div id="rs-site">
     - prefixes every class and id with "rs-" and scopes every CSS rule to #rs-site
     - inlines the CSS, JS, scene art and (downsized) logos; GSAP is loaded from
       jsDelivr by js/main.js at runtime to keep the paste small
2. dist/rydesmart-logistics.html — the full page with every asset (GSAP included)
   inlined, for opening directly or uploading anywhere.

Run from the repo root:  python3 tools/build.py   (needs Pillow)
"""
import base64
import io
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "gohighlevel" / "rydesmart-ghl.html"
STANDALONE = ROOT / "dist" / "rydesmart-logistics.html"
P = "rs-"
SCOPE = "#rs-site"


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
    return SCOPE + " " + prefix_classes(sel)


def scope_css(css):
    out, i = [], 0
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    while i < len(css):
        brace = css.find("{", i)
        if brace == -1:
            break
        head = css[i:brace].strip()
        # find the matching closing brace
        depth, j = 1, brace + 1
        while depth:
            depth += {"{": 1, "}": -1}.get(css[j], 0)
            j += 1
        body = css[brace + 1:j - 1]
        if head.startswith("@media"):
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
    html = re.sub(r'\b(id|aria-controls)="([^"]+)"', lambda m: m.group(1) + '="' + P + m.group(2) + '"', html)
    html = re.sub(r'href="#([^"]+)"', lambda m: 'href="#' + P + m.group(1) + '"', html)
    html = html.replace("url(#", "url(#" + P)
    return html


def prefix_js(js):
    # main.js builds every class/id selector from P (see sel()/cls() there).
    assert 'var P = "";' in js
    return js.replace('var P = "";', 'var P = "' + P + '";', 1)


def inline_css_urls(css):
    """Swap url("../assets/...svg") references for data URIs."""
    def repl(m):
        data = (ROOT / m.group(1)).read_bytes()
        return 'url("data:image/svg+xml;base64,' + base64.b64encode(data).decode() + '")'
    return re.sub(r'url\("\.\./(assets/[^"]+\.svg)"\)', repl, css)


def file_uri(path):
    return "data:image/png;base64," + base64.b64encode((ROOT / path).read_bytes()).decode()


def data_uri(path, width):
    im = Image.open(path).convert("RGBA")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.quantize(colors=96, method=Image.Quantize.FASTOCTREE).save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def build_ghl(page):
    body = page.split("<body>", 1)[1].split("</body>", 1)[0]
    body = re.sub(r'\s*<script src="[^"]+"></script>', "", body).strip()
    body = prefix_html(body)
    body = body.replace('"assets/logo.png"', '"' + data_uri(ROOT / "assets/logo.png", 520) + '"')
    body = body.replace('"assets/logo-light.png"', '"' + data_uri(ROOT / "assets/logo-light.png", 520) + '"')
    body = body.replace('width="722" height="139"', 'width="520" height="100"')

    fonts = re.search(r'<link href="https://fonts.googleapis.com[^>]+>', page).group(0)
    css = inline_css_urls(scope_css((ROOT / "css/styles.css").read_text()))
    # Break out of the builder's centred row so there are no white gaps at the sides
    # (main.js then aligns it to the exact pixel); clip stops any sideways scroll.
    css += (
        SCOPE + " { position: relative; width: 100vw; max-width: none; margin-left: calc(50% - 50vw); margin-right: 0; }\n"
        "body { overflow-x: clip; }\n"
    )
    js = prefix_js((ROOT / "js/main.js").read_text())

    snippet = (
        "<!-- RydeSmart Logistics site: paste into a GoHighLevel Custom JS/HTML element -->\n"
        + fonts + "\n<style>\n" + css + "</style>\n"
        + '<div id="rs-site">\n' + body + "\n</div>\n"
        + "<script>\n" + js + "</script>\n"
    )
    assert "assets/" not in snippet
    return snippet


def build_standalone(page):
    css = inline_css_urls((ROOT / "css/styles.css").read_text())
    page = page.replace('<link rel="stylesheet" href="css/styles.css">', "<style>\n" + css + "</style>")

    def script(m):
        code = (ROOT / m.group(1)).read_text()
        assert "</script" not in code
        return "<script>\n" + code + "\n</script>"
    page = re.sub(r'<script src="([^"]+)"></script>', script, page)
    for img in ("assets/logo.png", "assets/logo-light.png", "assets/favicon.png"):
        page = page.replace('"' + img + '"', '"' + file_uri(img) + '"')
    assert "assets/" not in page
    return page


def main():
    page = (ROOT / "index.html").read_text()
    for out, text in ((OUT, build_ghl(page)), (STANDALONE, build_standalone(page))):
        out.parent.mkdir(exist_ok=True)
        out.write_text(text)
        print(out.relative_to(ROOT), f"{len(text) // 1024} KB")


if __name__ == "__main__":
    main()
