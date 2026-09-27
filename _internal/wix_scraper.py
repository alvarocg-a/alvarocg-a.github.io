"""
Wix site scraper — extracts content, structure, design tokens and media from a
published Wix site so it can be rebuilt elsewhere (e.g. GitHub Pages).

Usage:
    python wix_scraper.py https://calvoalvaro12.wixsite.com/-lvarocg-a
    python wix_scraper.py <url> --out output --max-pages 100 --no-mobile --no-download

Output (in --out):
    README.md                 overview: sitemap, nav, design tokens, asset inventory
    site.json                 everything, machine-readable
    pages/<slug>/content.md   ordered content of each page (text, images, videos, links)
    pages/<slug>/page.json    raw blocks with positions/styles
    pages/<slug>/desktop.png  full-page screenshot (1440px)
    pages/<slug>/mobile.png   full-page screenshot (390px)
    pages/<slug>/rendered.html
    assets/images/            original-resolution images
    assets/videos/            Wix-hosted videos (mp4)
    assets/thumbnails/        YouTube/Vimeo thumbnails
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse, urljoin, parse_qs

import requests
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

WIX_MEDIA_RE = re.compile(r"https?://static\.wixstatic\.com/(media|shapes)/([^/?#\"'\s)]+)")
WIX_MEDIA_ID_RE = re.compile(r"\b([0-9a-f]{6}_[0-9a-f]{32}(?:~mv2(?:_d_\d+_\d+_s_\d+)?)?\.(?:jpe?g|png|gif|webp|svg))\b", re.I)
WIX_VIDEO_RE = re.compile(r"https?://video\.wixstatic\.com/video/([^/]+)/(\d+p)/mp4/file\.mp4")
YOUTUBE_RE = re.compile(r"(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=|shorts/)|youtu\.be/)([\w-]{11})")
VIMEO_RE = re.compile(r"vimeo\.com/(?:video/)?(\d+)")

# --------------------------------------------------------------------------- #
# In-page extraction (runs inside the browser)
# --------------------------------------------------------------------------- #
EXTRACT_JS = r"""
() => {
  const root = document.querySelector('#PAGES_CONTAINER') || document.querySelector('main') || document.body;
  const clean = s => (s || '').replace(/[\u200b\u200c\u200d\ufeff]/g, '').replace(/\u00a0/g, ' ')
                              .replace(/[ \t]+/g, ' ').replace(/ *\n */g, '\n').replace(/\n{3,}/g, '\n\n').trim();
  const rect = el => { const r = el.getBoundingClientRect();
    return {x: Math.round(r.left + scrollX), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height)}; };
  const visible = el => { const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && parseFloat(s.opacity) > 0.01 && r.width > 1 && r.height > 1; };
  const style = el => { const s = getComputedStyle(el);
    return {font: s.fontFamily, size: s.fontSize, weight: s.fontWeight, color: s.color, align: s.textAlign,
            lineHeight: s.lineHeight, letterSpacing: s.letterSpacing, transform: s.textTransform, italic: s.fontStyle === 'italic'}; };
  const inAds = el => !!el.closest('#WIX_ADS, [data-testid="wix-ads"], #wix-ads');
  const jsonAttr = (el, attr) => { try { return JSON.parse(el.getAttribute(attr)); } catch (e) { return null; } };

  // ---- sections (top-level blocks of the page) ----
  let sections = [...root.querySelectorAll('section')].filter(s => !s.parentElement.closest('section') && visible(s));
  if (!sections.length) sections = [...root.children].filter(visible);
  sections.sort((a, b) => rect(a).y - rect(b).y);
  const sectionOf = el => { for (let i = 0; i < sections.length; i++) if (sections[i].contains(el)) return i; return -1; };
  const sectionInfo = sections.map((s, i) => {
    const bgLayer = s.querySelector('[data-testid="bgLayers"], [id^="bgLayers"]') || s;
    const cs = getComputedStyle(s), bs = getComputedStyle(bgLayer);
    const colorLayer = s.querySelector('[data-testid="colorUnderlay"]');
    return {index: i, id: s.id, rect: rect(s),
            background: (colorLayer && getComputedStyle(colorLayer).backgroundColor) || bs.backgroundColor || cs.backgroundColor};
  });

  // ---- ordered content blocks ----
  const blocks = [];
  const TEXT = 'h1,h2,h3,h4,h5,h6,p,li,blockquote';
  const sel = TEXT + ',img,video,iframe,a[href],button,[data-video-info]';
  for (const el of root.querySelectorAll(sel)) {
    const tag = el.tagName.toLowerCase();
    if (inAds(el) || (tag !== 'img' && !visible(el))) continue;
    const base = {section: sectionOf(el), rect: rect(el)};

    if (el.matches(TEXT)) {
      if (tag === 'li' && el.querySelector('p,h1,h2,h3,h4,h5,h6')) continue;
      if (tag !== 'li' && el.parentElement.closest('p,h1,h2,h3,h4,h5,h6,blockquote')) continue;
      const text = clean(el.innerText);
      if (!text) continue;
      const links = [...el.querySelectorAll('a[href]')].map(a => ({text: clean(a.innerText), href: a.href}));
      blocks.push({...base, type: /^h\d$/.test(tag) ? 'heading' : (tag === 'li' ? 'list-item' : 'text'),
                   tag, level: /^h\d$/.test(tag) ? +tag[1] : null, text, links, style: style(el)});
    } else if (tag === 'img') {
      const wow = el.closest('wow-image, [data-image-info]');
      const info = wow ? jsonAttr(wow, 'data-image-info') : null;
      const isBg = !!el.closest('[data-testid="bgLayers"], [id^="bgLayers"], [data-testid="bgImage"]');
      const link = el.closest('a[href]');
      blocks.push({...base, type: 'image', src: el.currentSrc || el.src, srcset: el.srcset || null,
                   alt: el.alt || (info && info.imageData && info.imageData.alt) || '',
                   name: (info && info.imageData && info.imageData.name) || null,
                   original: info && info.imageData ? {uri: info.imageData.uri, width: info.imageData.width, height: info.imageData.height} : null,
                   natural: {w: el.naturalWidth, h: el.naturalHeight}, background: isBg, link: link ? link.href : null,
                   hidden: !visible(el)});
    } else if (tag === 'video') {
      blocks.push({...base, type: 'video', src: el.currentSrc || el.src,
                   sources: [...el.querySelectorAll('source')].map(s => s.src), poster: el.poster || null,
                   background: !!el.closest('[data-testid="bgLayers"], [id^="bgLayers"]'),
                   autoplay: el.autoplay, loop: el.loop, muted: el.muted});
    } else if (el.hasAttribute('data-video-info')) {
      blocks.push({...base, type: 'wix-video', info: jsonAttr(el, 'data-video-info')});
    } else if (tag === 'iframe') {
      blocks.push({...base, type: 'embed', src: el.src, title: el.title || ''});
    } else if (tag === 'a' || tag === 'button') {
      if (el.closest(TEXT) || el.querySelector(TEXT + ',img')) continue;   // inline link or image link: handled elsewhere
      const text = clean(el.innerText || el.getAttribute('aria-label'));
      if (!text && tag === 'button') continue;
      blocks.push({...base, type: 'button', text, href: el.href || null, style: style(el)});
    }
  }

  // ---- CSS background images anywhere on the page ----
  const cssBackgrounds = [];
  for (const el of document.querySelectorAll('body *')) {
    const bg = getComputedStyle(el).backgroundImage;
    if (bg && bg !== 'none' && bg.includes('url(') && visible(el))
      for (const m of bg.matchAll(/url\(["']?([^"')]+)["']?\)/g))
        cssBackgrounds.push({url: m[1], section: sectionOf(el), rect: rect(el)});
  }

  // ---- header / footer / navigation ----
  const region = sel => { const r = document.querySelector(sel); if (!r) return null;
    return {text: clean(r.innerText),
            links: [...r.querySelectorAll('a[href]')].filter(a => !inAds(a)).map(a => ({
              text: clean(a.innerText || a.getAttribute('aria-label')), href: a.href,
              depth: (() => { let d = 0, p = a.parentElement; while (p && p !== r) { if (p.tagName === 'UL') d++; p = p.parentElement; } return Math.max(0, d - 1); })(),
              visible: visible(a)})),
            images: [...r.querySelectorAll('img')].map(i => ({src: i.currentSrc || i.src, alt: i.alt}))}; };

  const meta = n => (document.querySelector(`meta[name="${n}"], meta[property="${n}"]`) || {}).content || null;
  return {
    title: document.title, lang: document.documentElement.lang,
    meta: {description: meta('description'), ogTitle: meta('og:title'), ogDescription: meta('og:description'),
           ogImage: meta('og:image'), keywords: meta('keywords'), robots: meta('robots')},
    favicon: (document.querySelector('link[rel~="icon"]') || {}).href || null,
    canonical: (document.querySelector('link[rel="canonical"]') || {}).href || null,
    pageBackground: getComputedStyle(document.body).backgroundColor,
    pageHeight: document.documentElement.scrollHeight,
    header: region('#SITE_HEADER, header'), footer: region('#SITE_FOOTER, footer'),
    sections: sectionInfo, blocks, cssBackgrounds,
    fonts: [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/["']/g, '')))],
    allLinks: [...document.querySelectorAll('a[href]')].filter(a => !inAds(a)).map(a => a.href),
  };
}
"""


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def norm_url(u):
    p = urlparse(u)
    path = p.path.rstrip("/") or "/"
    return f"{p.scheme}://{p.netloc}{path}"


def slug_for(url, base):
    rest = norm_url(url)[len(norm_url(base)):].strip("/")
    return re.sub(r"[^\w.-]+", "_", rest) or "home"


def wix_original(url):
    """static.wixstatic.com/media/<id>/v1/fill/... -> static.wixstatic.com/media/<id>"""
    m = WIX_MEDIA_RE.search(url or "")
    return f"https://static.wixstatic.com/{m.group(1)}/{m.group(2)}" if m else None


def safe_name(s):
    return re.sub(r"[^\w.-]+", "_", s)


def discover_sitemap(base, session):
    """Wix publishes /sitemap.xml (an index pointing to pages-sitemap.xml etc.)."""
    found, todo, seen = set(), [urljoin(norm_url(base) + "/", "sitemap.xml")], set()
    while todo:
        sm = todo.pop()
        if sm in seen:
            continue
        seen.add(sm)
        try:
            r = session.get(sm, timeout=20)
            if r.status_code != 200 or "<" not in r.text[:100]:
                continue
            tree = ET.fromstring(r.content)
        except Exception:
            continue
        for loc in tree.iter():
            if loc.tag.endswith("loc") and loc.text:
                u = loc.text.strip()
                (todo.append(u) if u.endswith(".xml") else found.add(norm_url(u)))
    return found


def auto_scroll(page):
    """Scroll slowly to the bottom so lazy images / galleries / animations load."""
    last = 0
    for _ in range(80):
        h = page.evaluate("document.documentElement.scrollHeight")
        y = page.evaluate("window.scrollY + window.innerHeight")
        if y >= h and h == last:
            break
        last = h
        page.mouse.wheel(0, 700)
        page.wait_for_timeout(250)
    page.wait_for_timeout(1500)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(500)


def open_page(page, url):
    page.goto(url, wait_until="load", timeout=90000)
    page.wait_for_timeout(3000)
    # Hide the Wix free-plan ad banner so it doesn't pollute screenshots
    page.add_style_tag(content="#WIX_ADS, [data-testid='wix-ads'] {display:none !important}")
    auto_scroll(page)


# --------------------------------------------------------------------------- #
# Scraping
# --------------------------------------------------------------------------- #
def scrape(base, out, max_pages, mobile, session):
    base_n = norm_url(base)
    in_scope = lambda u: norm_url(u) == base_n or norm_url(u).startswith(base_n + "/")

    queue = [base_n]
    sm = discover_sitemap(base, session)
    print(f"[sitemap] {len(sm)} URLs found")
    queue += sorted(u for u in sm if in_scope(u))
    seen, pages = set(), []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, user_agent=UA, locale="es-ES")
        mctx = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2,
                                   is_mobile=True, has_touch=True, locale="es-ES",
                                   user_agent=UA.replace("Windows NT 10.0; Win64; x64", "Linux; Android 14; Pixel 8") + " Mobile") if mobile else None

        while queue and len(pages) < max_pages:
            url = norm_url(queue.pop(0))
            if url in seen or not in_scope(url):
                continue
            seen.add(url)
            slug = slug_for(url, base)
            pdir = out / "pages" / slug
            pdir.mkdir(parents=True, exist_ok=True)
            print(f"[page {len(pages)+1}] {url}  ->  pages/{slug}")

            page = ctx.new_page()
            net_media, data_resps = set(), []
            def on_resp(r):
                if "wixstatic.com" in r.url:
                    net_media.add(r.url)
                elif "parastorage.com" in r.url and ("pages" in r.url or "thunderbolt" in r.url):
                    data_resps.append(r)
            page.on("response", on_resp)
            try:
                open_page(page, url)
                data = page.evaluate(EXTRACT_JS)
                page_data_media = set()
                for r in data_resps:
                    try:
                        page_data_media |= set(WIX_MEDIA_ID_RE.findall(r.text()))
                    except Exception:
                        pass
                page.screenshot(path=str(pdir / "desktop.png"), full_page=True)
                (pdir / "rendered.html").write_text(page.content(), encoding="utf-8")
            except Exception as e:
                print(f"   !! failed: {e}")
                page.close()
                continue
            page.close()

            if mctx:
                mp = mctx.new_page()
                try:
                    open_page(mp, url)
                    mp.screenshot(path=str(pdir / "mobile.png"), full_page=True)
                except Exception as e:
                    print(f"   !! mobile screenshot failed: {e}")
                mp.close()

            data.update(url=url, slug=slug, networkMedia=sorted(net_media),
                        pageDataMedia=sorted(f"https://static.wixstatic.com/media/{m}" for m in page_data_media))
            pages.append(data)
            for link in data["allLinks"]:
                if in_scope(link) and norm_url(link) not in seen:
                    queue.append(norm_url(link))

        browser.close()
    return pages


# --------------------------------------------------------------------------- #
# Media inventory + download
# --------------------------------------------------------------------------- #
def collect_media(pages):
    images, videos, embeds = {}, {}, {}
    by_file = {}   # same Wix file can appear under /media/ and /shapes/: keep the first URL seen

    def add_img(url, slug, **extra):
        orig = wix_original(url)
        key = orig or url
        if not key or key.startswith("data:"):
            return
        fname = key.rsplit("/", 1)[-1]
        key = by_file.setdefault(fname, key)
        it = images.setdefault(key, {"url": key, "pages": set(), "alt": "", "name": None, "width": None, "height": None,
                                     "background": False})
        it["pages"].add(slug)
        for k, v in extra.items():
            if v and not it.get(k):
                it[k] = v

    for pg in pages:
        s = pg["slug"]
        for b in pg["blocks"]:
            if b["type"] == "image":
                o = b.get("original") or {}
                add_img(b["src"], s, alt=b.get("alt"), name=b.get("name"), width=o.get("width"),
                        height=o.get("height"), background=b.get("background"))
            elif b["type"] == "video":
                for v in [b.get("src")] + b.get("sources", []):
                    if v:
                        videos.setdefault(v, {"url": v, "pages": set(), "poster": b.get("poster")})["pages"].add(s)
                if b.get("poster"):
                    add_img(b["poster"], s)
            elif b["type"] == "wix-video" and b.get("info"):
                # Wix video box: metadata lists every encoded quality -> take the best one
                q = max(b["info"].get("qualities") or [], key=lambda x: int(x["quality"].rstrip("p") or 0), default=None)
                if q and q.get("url"):
                    v = "https://video.wixstatic.com/" + q["url"].lstrip("/")
                    videos.setdefault(v, {"url": v, "pages": set(), "poster": None})["pages"].add(s)
            elif b["type"] == "embed":
                src = b["src"]
                yt, vm = YOUTUBE_RE.search(src), VIMEO_RE.search(src)
                key = f"youtube:{yt.group(1)}" if yt else f"vimeo:{vm.group(1)}" if vm else src
                embeds.setdefault(key, {"key": key, "src": src, "pages": set(), "title": b.get("title")})["pages"].add(s)
        for bg in pg["cssBackgrounds"]:
            add_img(bg["url"], s, background=True)
        for region in ("header", "footer"):
            for im in (pg.get(region) or {}).get("images", []):
                add_img(im["src"], s, alt=im.get("alt"))
        for u in [pg["meta"].get("ogImage"), pg.get("favicon")]:
            if u and "wixstatic" in u:
                add_img(u, s)
        for u in pg["networkMedia"]:
            if WIX_MEDIA_RE.search(u):
                add_img(u, s)
        for u in pg.get("pageDataMedia", []):
            if u.endswith(".svg"):   # vector art lives under /shapes/, not /media/
                u = u.replace("/media/", "/shapes/")
            add_img(u, s, fromPageData=True)
            m = WIX_VIDEO_RE.search(u)
            if m:
                videos.setdefault(u, {"url": u, "pages": set(), "poster": None})["pages"].add(s)
        # External video links (e.g. "watch on YouTube" buttons)
        for b in pg["blocks"]:
            for href in [b.get("href")] + [l["href"] for l in b.get("links", [])]:
                if href and (YOUTUBE_RE.search(href) or VIMEO_RE.search(href)):
                    yt, vm = YOUTUBE_RE.search(href), VIMEO_RE.search(href)
                    key = f"youtube:{yt.group(1)}" if yt else f"vimeo:{vm.group(1)}"
                    embeds.setdefault(key, {"key": key, "src": href, "pages": set(), "title": b.get("text")})["pages"].add(s)

    # Wix videos: keep only the best quality per video id
    best = {}
    for u, v in videos.items():
        m = WIX_VIDEO_RE.search(u)
        vid, q = (m.group(1), int(m.group(2)[:-1])) if m else (u, 0)
        if vid not in best or q > best[vid][0]:
            if vid in best:
                v["pages"] |= best[vid][1]["pages"]
            best[vid] = (q, v)
    videos = {v["url"]: v for _, v in best.values()}
    return images, videos, embeds


def download(url, dest, session):
    if dest.exists() and dest.stat().st_size > 0:
        return True
    try:
        with session.get(url, stream=True, timeout=60) as r:
            if r.status_code != 200:
                return r.status_code
            ct = r.headers.get("content-type", "")
            if not dest.suffix:
                ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif",
                       "image/svg+xml": ".svg", "video/mp4": ".mp4"}.get(ct.split(";")[0], "")
                dest = dest.with_suffix(ext)
            with open(dest, "wb") as f:
                for chunk in r.iter_content(1 << 16):
                    f.write(chunk)
        return dest
    except Exception as e:
        print(f"   !! download failed {url}: {e}")
        return False


def download_all(images, videos, embeds, out, session):
    (out / "assets/images").mkdir(parents=True, exist_ok=True)
    (out / "assets/videos").mkdir(parents=True, exist_ok=True)
    (out / "assets/thumbnails").mkdir(parents=True, exist_ok=True)
    jobs = []

    for it in images.values():
        m = WIX_MEDIA_RE.search(it["url"])
        fname = safe_name(m.group(2).replace("~mv2", "")) if m else safe_name(Path(urlparse(it["url"]).path).name or "img")
        it["local"] = f"assets/images/{fname}"
        jobs.append((it, it["url"], out / it["local"]))

    for it in videos.values():
        m = WIX_VIDEO_RE.search(it["url"])
        fname = f"{safe_name(m.group(1))}_{m.group(2)}.mp4" if m else safe_name(Path(urlparse(it["url"]).path).name)
        it["local"] = f"assets/videos/{fname}"
        jobs.append((it, it["url"], out / it["local"]))

    for it in embeds.values():
        if it["key"].startswith("youtube:"):
            vid = it["key"].split(":")[1]
            it["watch"] = f"https://www.youtube.com/watch?v={vid}"
            it["embed"] = f"https://www.youtube.com/embed/{vid}"
            it["local"] = f"assets/thumbnails/youtube_{vid}.jpg"
            it["_thumbs"] = [f"https://img.youtube.com/vi/{vid}/{q}.jpg" for q in ("maxresdefault", "hqdefault")]
        elif it["key"].startswith("vimeo:"):
            vid = it["key"].split(":")[1]
            it["watch"] = f"https://vimeo.com/{vid}"
            it["embed"] = f"https://player.vimeo.com/video/{vid}"

    def run(job):
        it, url, dest = job
        res = download(url, dest, session)
        if isinstance(res, Path):
            it["local"] = res.relative_to(out).as_posix()
        elif res is not True:
            it["local"] = None
            it["error"] = f"HTTP {res}" if isinstance(res, int) else "download error"
            if res in (403, 404, 410):
                it["broken"] = True   # deleted from Wix Media Manager: also broken on the live site

    def run_thumb(it):
        for t in it.pop("_thumbs", []):
            if download(t, out / it["local"], session):
                return
        it["local"] = None

    with ThreadPoolExecutor(8) as ex:
        list(ex.map(run, jobs))
        list(ex.map(run_thumb, [e for e in embeds.values() if "_thumbs" in e]))
    ok = sum(1 for it, _, _ in jobs if it.get("local"))
    broken = sum(1 for it, _, _ in jobs if it.get("broken"))
    print(f"[download] {ok}/{len(jobs)} files ({broken} already broken on the live site), {sum(1 for e in embeds.values() if e.get('local'))} video thumbnails")


# --------------------------------------------------------------------------- #
# Reports
# --------------------------------------------------------------------------- #
def design_tokens(pages):
    fonts, sizes, colors, bgs = Counter(), defaultdict(Counter), Counter(), Counter()
    for pg in pages:
        for b in pg["blocks"]:
            st = b.get("style")
            if not st:
                continue
            w = len(b.get("text", "")) or 1
            role = f"h{b['level']}" if b["type"] == "heading" else ("button" if b["type"] == "button" else "text")
            fam = st["font"].split(",")[0].strip().strip('"\'')
            fonts[fam] += w
            sizes[role][f"{st['size']} / {st['weight']} / {fam}"] += w
            colors[st["color"]] += w
        for s in pg["sections"]:
            if s["background"] and s["background"] not in ("rgba(0, 0, 0, 0)", "transparent"):
                bgs[s["background"]] += 1
        bgs[pg["pageBackground"]] += 1
    loaded = sorted({f for pg in pages for f in pg["fonts"]})
    return {"fonts": fonts.most_common(), "loadedFonts": loaded,
            "typeScale": {k: v.most_common(3) for k, v in sorted(sizes.items())},
            "textColors": colors.most_common(10), "backgroundColors": bgs.most_common(10)}


def rgb_to_hex(c):
    m = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)", c or "")
    if not m:
        return c
    hx = "#{:02x}{:02x}{:02x}".format(*map(int, m.groups()[:3]))
    return hx + (f" (alpha {m.group(4)})" if m.group(4) and float(m.group(4)) < 1 else "")


def md_escape(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def write_page_md(pg, images, videos, embeds, out):
    pdir = out / "pages" / pg["slug"]
    rel = "../../"
    L = [f"# {pg['title']}", "", f"- **URL:** {pg['url']}"]
    if pg["meta"].get("description"):
        L.append(f"- **Meta description:** {pg['meta']['description']}")
    L += ["- **Screenshots:** [desktop](desktop.png) · [mobile](mobile.png)", ""]

    cur = None
    # DOM order within each section keeps multi-column layouts grouped by column
    for b in sorted(pg["blocks"], key=lambda b: b["section"]):
        if b["section"] != cur:
            cur = b["section"]
            sec = pg["sections"][cur] if 0 <= cur < len(pg["sections"]) else None
            bg = f" — fondo {rgb_to_hex(sec['background'])}" if sec and sec.get("background") else ""
            L += ["", "---", f"<!-- section {cur}{(' #' + sec['id']) if sec and sec['id'] else ''}{bg} -->", ""]
        t = b["type"]
        if t == "heading":
            L += [f"{'#' * min(6, b['level'] + 1)} {b['text']}", ""]
        elif t in ("text", "list-item"):
            txt = b["text"]
            for l in b["links"]:
                if l["text"] and l["text"] in txt:
                    txt = txt.replace(l["text"], f"[{l['text']}]({l['href']})", 1)
            L += [("- " if t == "list-item" else "") + txt.replace("\n", "  \n"), "" if t == "text" else None]
        elif t == "image":
            key = wix_original(b["src"]) or b["src"]
            it = images.get(key, {})
            src = rel + it["local"] if it.get("local") else key
            tag = (" *(fondo)*" if b.get("background") else "") + (" *(oculta: carrusel/galería)*" if b.get("hidden") else "")                   + (" ⚠️ ROTA en la web actual" if it.get("broken") else "")
            img = f"![{md_escape(b.get('alt'))}]({src})"
            L += [f"[{img}]({b['link']})" if b.get("link") else img,
                  f"<sub>{b['rect']['w']}×{b['rect']['h']} en pantalla · original: {key}{tag}</sub>", ""]
        elif t == "embed":
            yt, vm = YOUTUBE_RE.search(b["src"]), VIMEO_RE.search(b["src"])
            key = f"youtube:{yt.group(1)}" if yt else f"vimeo:{vm.group(1)}" if vm else b["src"]
            e = embeds.get(key, {})
            if e.get("watch"):
                thumb = f"![thumbnail]({rel + e['local']})\n" if e.get("local") else ""
                L += [f"🎬 **Vídeo {key.split(':')[0]}:** {e['watch']}  ", f"{thumb}<sub>embed: {e['embed']}</sub>", ""]
            else:
                L += [f"🧩 **Embed:** {b['src']}", ""]
        elif t == "video":
            L += [f"🎬 **Vídeo:** {b.get('src')}", ""]
        elif t == "wix-video":
            vid = (b.get("info") or {}).get("videoId", "")
            v = next((v for u, v in videos.items() if vid and vid in u), {})
            state = f"[{Path(v['local']).name}]({rel + v['local']})" if v.get("local") else \
                    ("⚠️ ROTO en la web actual" if v.get("broken") else v.get("url", vid))
            L += [f"🎬 **Vídeo Wix** ({vid}): {state}", ""]
        elif t == "button":
            L += [f"🔘 **[{b['text'] or '(sin texto)'}]({b['href']})**", ""]
    (pdir / "content.md").write_text("\n".join(x for x in L if x is not None), encoding="utf-8")


def write_readme(base, pages, images, videos, embeds, tokens, out):
    L = [f"# Export de {base}", "",
         f"{len(pages)} páginas · {len(images)} imágenes · {len(videos)} vídeos Wix · {len(embeds)} vídeos/embeds externos", ""]

    home = pages[0] if pages else {}
    nav = (home.get("header") or {}).get("links", [])
    if nav:
        L += ["## Navegación (header)", ""]
        seen = set()
        for l in nav:
            if (l["text"], l["href"]) in seen or not l["text"]:
                continue
            seen.add((l["text"], l["href"]))
            L.append(f"{'  ' * l['depth']}- [{l['text']}]({l['href']})")
        L.append("")

    L += ["## Páginas", "", "| Página | Título | Bloques | Contenido | Captura |", "|---|---|---|---|---|"]
    for pg in pages:
        L.append(f"| `{pg['slug']}` | {md_escape(pg['title'])} | {len(pg['blocks'])} | "
                 f"[content.md](pages/{pg['slug']}/content.md) | [desktop](pages/{pg['slug']}/desktop.png) |")

    L += ["", "## Diseño (tokens detectados)", "", "**Fuentes usadas (por cantidad de texto):**", ""]
    L += [f"- {f} ({n} caracteres)" for f, n in tokens["fonts"]]
    L += ["", f"**Fuentes cargadas:** {', '.join(tokens['loadedFonts']) or '—'}", "", "**Escala tipográfica (tamaño / peso / fuente):**", ""]
    for role, vals in tokens["typeScale"].items():
        L.append(f"- **{role}:** " + "; ".join(v for v, _ in vals))
    L += ["", "**Colores de texto:** " + ", ".join(f"`{rgb_to_hex(c)}`" for c, _ in tokens["textColors"]),
          "", "**Colores de fondo:** " + ", ".join(f"`{rgb_to_hex(c)}`" for c, _ in tokens["backgroundColors"]), ""]

    L += ["## Imágenes", "", "| Archivo | Alt | Tamaño original | Páginas |", "|---|---|---|---|"]
    for it in sorted(images.values(), key=lambda i: (sorted(i["pages"])[0], i["url"])):
        size = f"{it['width']}×{it['height']}" if it.get("width") else ""
        f = f"[{Path(it['local']).name}]({it['local']})" if it.get("local") else f"⚠️ {it['url']} ({it.get('error', '')})"
        L.append(f"| {f} | {md_escape(it.get('alt'))} | {size} | {', '.join(sorted(it['pages']))} |")

    broken = [x for x in list(images.values()) + list(videos.values()) if x.get("broken")]
    if broken:
        L += ["", "## ⚠️ Recursos rotos en la web actual", "",
              "Wix devuelve 403/404: se borraron del gestor de medios y ya no se ven en la web publicada.",
              "Tendrás que recuperarlos de tus archivos originales.", ""]
        L += [f"- {x['url']} — {md_escape(x.get('alt') or x.get('name') or '')} — {', '.join(sorted(x['pages']))}" for x in broken]
    if videos:
        L += ["", "## Vídeos alojados en Wix", ""]
        L += [f"- [{Path(v['local']).name if v.get('local') else v['url']}]({v.get('local') or v['url']}) — {', '.join(sorted(v['pages']))}"
              for v in videos.values()]
    if embeds:
        L += ["", "## Vídeos y embeds externos", ""]
        L += [f"- **{e['key']}** {e.get('watch') or e['src']} — {md_escape(e.get('title'))} — {', '.join(sorted(e['pages']))}"
              for e in embeds.values()]

    ext = Counter()
    for pg in pages:
        for l in pg["allLinks"]:
            host = urlparse(l).netloc
            if host and host not in urlparse(base).netloc and "wix.com" not in host:
                ext[l] += 1
    if ext:
        L += ["", "## Enlaces externos", ""] + [f"- {u}" for u in sorted(ext)]
    (out / "README.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def to_jsonable(o):
    if isinstance(o, set):
        return sorted(o)
    raise TypeError(type(o))


def main():
    ap = argparse.ArgumentParser(description="Extract all content and media from a Wix site")
    ap.add_argument("url")
    ap.add_argument("--out", default="output")
    ap.add_argument("--max-pages", type=int, default=200)
    ap.add_argument("--no-mobile", action="store_true", help="skip mobile screenshots")
    ap.add_argument("--no-download", action="store_true", help="don't download media files")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = UA

    pages = scrape(a.url, out, a.max_pages, not a.no_mobile, session)
    images, videos, embeds = collect_media(pages)
    print(f"[media] {len(images)} images, {len(videos)} Wix videos, {len(embeds)} external embeds")
    if not a.no_download:
        download_all(images, videos, embeds, out, session)

    tokens = design_tokens(pages)
    for pg in pages:
        write_page_md(pg, images, videos, embeds, out)
        (out / "pages" / pg["slug"] / "page.json").write_text(
            json.dumps(pg, ensure_ascii=False, indent=2, default=to_jsonable), encoding="utf-8")
    write_readme(a.url, pages, images, videos, embeds, tokens, out)
    site = {"base": a.url, "designTokens": tokens, "images": list(images.values()), "videos": list(videos.values()),
            "embeds": list(embeds.values()),
            "pages": [{k: v for k, v in pg.items() if k not in ("allLinks", "networkMedia", "pageDataMedia")} for pg in pages]}
    (out / "site.json").write_text(json.dumps(site, ensure_ascii=False, indent=2, default=to_jsonable), encoding="utf-8")
    print(f"\nDone. Open {out / 'README.md'}")


if __name__ == "__main__":
    main()
