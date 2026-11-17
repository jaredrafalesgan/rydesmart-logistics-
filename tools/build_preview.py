"""Bundle the built site into ONE self-contained HTML preview file.

    python3 tools/build.py && python3 tools/build_preview.py [output.html]

All eight pages go into a single file; the menu switches between them with #page links
(e.g. #fleet, #lanes). CSS, JS, GSAP and images are inlined, so the file works on its own
(opened locally or published as a hosted preview). For review only — publish the real site
from site/ or gohighlevel/.
"""
import base64
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build  # noqa: E402

ROOT = build.ROOT
SITE = ROOT / "site"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "preview" / "rydesmart-preview.html"
ORDER = ["", "fleet", "lanes", "broker-resources", "request-capacity", "about", "careers", "contact"]


def page_file(slug):
    return SITE / (f"{slug}/index.html" if slug else "index.html")


def main_inner(html):
    return html.split('<main id="main" tabindex="-1">', 1)[1].split("</main>", 1)[0]


def rewrite_links(html):
    def repl(m):
        path, frag = m.group(1), m.group(2)
        if frag:
            return f'href="#{frag}"'
        slug = path.strip("/").split("?")[0]
        return f'href="#{slug or "home"}"'
    return re.sub(r'href="(/[^"#]*)(?:#([^"]*))?"', repl, html)


def img_uri(path):
    return "data:image/png;base64," + base64.b64encode((SITE / path).read_bytes()).decode()


def main():
    pages = {s: page_file(s).read_text() for s in ORDER}
    home = pages[""]
    head = home.split("<head>", 1)[1].split("</head>", 1)[0]
    fonts = re.search(r'<link href="https://fonts.googleapis.com[^>]+>', head).group(0)
    css = build.inline_css_urls((ROOT / "src/css/styles.css").read_text())
    body = home.split("<body", 1)[1].split(">", 1)[1].split("</body>", 1)[0]
    before, after = body.split('<main id="main" tabindex="-1">', 1)
    after = after.split("</main>", 1)[1]
    after = re.sub(r'\s*<script src="[^"]+"></script>', "", after)

    views = []
    for slug in ORDER:
        title = re.search(r"<title>(.*?)</title>", pages[slug]).group(1)
        views.append(f'<div data-view="{slug or "home"}" data-title="{title}"{"" if not slug else " hidden"}>'
                     f'{main_inner(pages[slug])}</div>')
    doc = before + '<main id="main" tabindex="-1">' + "\n".join(views) + "</main>" + after
    doc = doc.replace(' aria-current="page"', "")
    doc = rewrite_links(doc)
    # Embedded third-party forms can't load in a sandboxed preview: open them in a new tab instead.
    doc = doc.replace(" data-driver-form", "")
    doc = re.sub(r'<div class="ghl-form"[^>]*>\s*<iframe src="([^"]+)"[^>]*></iframe>\s*</div>',
                 r'<p class="empty-note">The GoHighLevel form appears here on the live site. '
                 r'<a href="\1" target="_blank" rel="noopener">Open the form in a new tab</a>.</p>', doc)
    for img in ("assets/logo.png", "assets/logo-light.png"):
        doc = doc.replace(f'"/{img}"', f'"{img_uri(img)}"')
    assert '"/assets/' not in doc, re.findall(r'"/assets/[^"]+"', doc)[:3]

    gsap = "".join((ROOT / f"src/js/vendor/{f}").read_text() + "\n" for f in ("gsap.min.js", "ScrollTrigger.min.js"))
    js = (ROOT / "src/js/main.js").read_text()
    router = """
(function () {
  // Preview router: show one page at a time from the #hash.
  var views = Array.prototype.slice.call(document.querySelectorAll("[data-view]"));
  function show() {
    var h = decodeURIComponent(location.hash.slice(1)) || "home";
    var view = document.querySelector('[data-view="' + h + '"]'), target = null;
    if (!view) { target = document.getElementById(h); view = target && target.closest("[data-view]"); }
    if (!view) view = views[0];
    views.forEach(function (v) { v.hidden = v !== view; });
    var name = view.getAttribute("data-view");
    document.querySelectorAll(".nav a").forEach(function (a) {
      if (a.getAttribute("href") === "#" + name) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    document.title = view.getAttribute("data-title");
    if (target) target.scrollIntoView(); else window.scrollTo(0, 0);
    window.dispatchEvent(new Event("resize"));
    if (window.ScrollTrigger) setTimeout(function () { window.ScrollTrigger.refresh(); }, 60);
  }
  window.addEventListener("hashchange", show);
  show();
})();
"""
    title = "RydeSmart Logistics Website"
    out = (f"<title>{title}</title>\n"
           '<meta name="description" content="Preview of the RydeSmart Logistics carrier website.">\n'
           f"{fonts}\n<style>\n{css}\n</style>\n{doc}\n"
           f"<script>\n{gsap}</script>\n<script>\n{router}</script>\n<script>\n{js}</script>\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(out)
    print(OUT, f"{len(out) // 1024} KB")


if __name__ == "__main__":
    main()
