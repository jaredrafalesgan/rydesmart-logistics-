"""Build a GoHighLevel-ready snippet of the site.

GoHighLevel's "Custom JS/HTML" element drops code into the middle of its own page,
so the snippet can't carry <html>/<head>/<body> and its CSS must not leak into (or
be overridden by) the builder's styles. This script:
  - wraps the page body in <div id="rs-site">
  - prefixes every class and id with "rs-" and scopes every CSS rule to #rs-site
  - inlines the CSS, JS and (downsized) logos so it's one paste

Run from the repo root:  python3 tools/build_ghl.py
Output: gohighlevel/rydesmart-ghl.html
"""
import base64
import io
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "gohighlevel" / "rydesmart-ghl.html"
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
    # Class names and selectors inside string literals ("..." only in main.js).
    def fix(m):
        s = m.group(1)
        if s.startswith(("aria-", "mailto:", "?", "&", "Thanks", "Freight", "Open", "Close", "\\n", "IntersectionObserver")) or " - " in s:
            return m.group(0)
        if s in ("true", "false", "scroll", "click", "submit", "a", "[data-quote-form]", "[data-year]"):
            return m.group(0)
        if s.startswith("."):
            return '"' + prefix_classes(s) + '"'
        if re.fullmatch(r"[a-z][\w-]*", s):  # bare class name for classList
            return '"' + P + s + '"'
        return m.group(0)
    js = re.sub(r'"([^"\n]*)"', fix, js)
    js = js.replace("(function () {", '(function () {\n  var root = document.getElementById("rs-site");\n  if (!root) return;', 1)
    js = js.replace("document.querySelector(", "root.querySelector(").replace("document.querySelectorAll(", "root.querySelectorAll(")
    return js


def data_uri(path, width):
    im = Image.open(path).convert("RGBA")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.quantize(colors=96, method=Image.Quantize.FASTOCTREE).save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    page = (ROOT / "index.html").read_text()
    body = page.split("<body>", 1)[1].split("</body>", 1)[0]
    body = body.replace('<script src="js/main.js"></script>', "").strip()
    body = prefix_html(body)
    body = body.replace('"assets/logo.png"', '"' + data_uri(ROOT / "assets/logo.png", 520) + '"')
    body = body.replace('"assets/logo-light.png"', '"' + data_uri(ROOT / "assets/logo-light.png", 520) + '"')
    body = body.replace('width="722" height="139"', 'width="520" height="100"')

    fonts = re.search(r'<link href="https://fonts.googleapis.com[^>]+>', page).group(0)
    css = scope_css((ROOT / "css/styles.css").read_text())
    js = prefix_js((ROOT / "js/main.js").read_text())

    snippet = (
        "<!-- RydeSmart Logistics site: paste into a GoHighLevel Custom JS/HTML element -->\n"
        + fonts + "\n<style>\n" + css + "</style>\n"
        + '<div id="rs-site">\n' + body + "\n</div>\n"
        + "<script>\n" + js + "</script>\n"
    )
    assert "assets/" not in snippet
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(snippet)
    print(OUT.relative_to(ROOT), f"{len(snippet) // 1024} KB")


if __name__ == "__main__":
    main()
