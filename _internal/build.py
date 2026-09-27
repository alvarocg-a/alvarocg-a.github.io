#!/usr/bin/env python3
"""Generator for the portfolio pages: run `python3 _internal/build.py` from the repo root.
It rewrites every *.html page at the root. Content originally came from the Wix scrape in _internal/output/."""
import html, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (this file lives in _internal/)

# ---------------------------------------------------------------- helpers
I_LINKEDIN = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.75h4V21H3zM9.5 9.75h3.83v1.54h.05c.53-1 1.84-2.06 3.79-2.06 4.05 0 4.8 2.67 4.8 6.13V21h-4v-4.98c0-1.19-.02-2.72-1.66-2.72-1.66 0-1.91 1.3-1.91 2.63V21h-4z"/></svg>'
I_X = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.75 3h3.07l-6.7 7.66L22 21h-6.17l-4.83-6.32L5.47 21H2.4l7.17-8.2L2 3h6.33l4.37 5.77zm-1.08 16.2h1.7L7.4 4.73H5.58z"/></svg>'
I_MAIL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/></svg>'
I_ITCH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 9.5 5.5 4h13L20 9.5M4 9.5c0 1.4 1.1 2.5 2.5 2.5S9 10.9 9 9.5m-5 0h16m-11 0c0 1.4 1.1 2.5 2.5 2.5h1C14.9 12 16 10.9 16 9.5m4 0c0 1.4-1.1 2.5-2.5 2.5S15 10.9 15 9.5M5.5 12v7.5h13V12"/><path d="M10 19.5V16h4v3.5"/></svg>'
I_PIN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'
I_EXT = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5.5 3.5h7v7M12.5 3.5l-9 9"/></svg>'
I_DOC = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M4 1.75h5.5L12.5 4.8v9.45h-8.5zM9.25 1.75V5h3.25"/></svg>'

EXT = 'target="_blank" rel="noopener"'


def yt(vid, title, thumb=None, show_title=False):
    t = f' data-thumb="{thumb}"' if thumb else ""
    st = " data-show-title" if show_title else ""
    return (f'<div class="yt" data-yt="{vid}" data-title="{html.escape(title)}"{t}{st}>'
            f'<a class="yt-fallback" href="https://www.youtube.com/watch?v={vid}" {EXT}>Watch on YouTube</a></div>')


def vimeo(vid, title):
    return (f'<div class="yt" data-vimeo="{vid}" data-title="{html.escape(title)}" data-thumb="assets/img/thumbs/vimeo-{vid}.webp">'
            f'<a class="yt-fallback" href="https://vimeo.com/{vid}" {EXT}>Watch on Vimeo</a></div>')


def notion(url, label):
    return f'<a class="chip" href="{url}" {EXT}>Notion · {label} {I_EXT}</a>'


def doc(url, label):
    return f'<a class="chip" href="{url}" {EXT}>{I_DOC} {label}</a>'


def fig(src, alt, caption=None, link=None, zoom=True):
    cls = ' class="zoomable"' if zoom and not link else ""
    im = f'<img src="{src}" alt="{html.escape(alt)}" loading="lazy" decoding="async"{cls}>'
    if link:
        im = f'<a href="{link}" {EXT}>{im}</a>'
    cap = f'<figcaption class="media-caption">{caption}</figcaption>' if caption else ""
    return f'<figure><div class="media">{im}</div>{cap}</figure>'


SHOW_PLACEHOLDERS = False  # True shows the pending-content boxes listed in PENDIENTES.md


def ph(pid, desc, square=False):
    if not SHOW_PLACEHOLDERS:
        return ""
    sq = " square" if square else ""
    return (f'<div class="ph{sq}" data-placeholder="{pid}"><div class="ph-inner">'
            f'<span class="ph-id">{pid}</span><span>{desc}</span></div></div>')


def phtext(pid, desc):
    if not SHOW_PLACEHOLDERS:
        return ""
    return f'<p class="ph-text" data-placeholder="{pid}">[{pid}] {desc}</p>'


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og}">
<meta property="og:url" content="{url}">
<link rel="canonical" href="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#141a17">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/barlow-condensed-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="css/style.css">
</head>
<body data-section="{section}" data-page="{page}"{hdr}>
<div id="site-header"><noscript><nav class="wrap" style="padding:20px 0;display:flex;gap:16px;flex-wrap:wrap"><a href="index.html">Portfolio</a><a href="index.html#work">Work</a><a href="bugs-n-guns.html">Bugs 'N' Guns</a><a href="personal-projects.html">Personal</a><a href="contact.html">Contact</a></nav></noscript></div>
<main id="main">
"""

FOOT = """
</main>
<div id="site-footer"></div>
<script src="js/site.js"></script>
</body>
</html>
"""


def write(name, title, desc, section, page, body, og="assets/img/thumbs/Yzam-WWlWpI.webp", header=""):
    hdr = f' data-header="{header}"' if header else ""
    base = "https://alvarocg-a.github.io/"
    og_abs = og if og.startswith("http") else base + og.lstrip("/")
    url = base + ("" if name == "index.html" else name)
    out = HEAD.format(title=html.escape(title), desc=html.escape(desc), section=section, page=page, og=og_abs, url=url, hdr=hdr) + body.strip("\n") + FOOT
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
        f.write(out)
    print("wrote", name)


def hero(eyebrow, h1, lead=None, actions="", extra=""):
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    act = f'<div class="actions">{actions}</div>' if actions else ""
    return f"""<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    {lead_html}
    {extra}
    {act}
  </div>
</section>"""


def btn(href, label, primary=False, icon=None, external=True):
    cls = "btn btn-primary" if primary else "btn"
    ic = icon or ""
    ex = f" {EXT}" if external else ""
    return f'<a class="{cls}" href="{href}"{ex}>{ic}{label}</a>'


def facts(rows):
    items = []
    for row in rows:
        k, v = row[0], row[1]
        span = ' class="span-2"' if len(row) > 2 and row[2] else ""
        items.append(f"<div{span}><dt>{k}</dt><dd>{v}</dd></div>")
    return '<dl class="facts">' + "".join(items) + "</dl>"


def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


STEAM_BNG = "https://store.steampowered.com/app/2648130/Bugs_N_Guns/"
NOTION_GDD = "https://sable-sandalwood-dee.notion.site/6b3e2cf0924a4829b68156f894e69264?v=b19f1f11e7794bb48de4bc0fd682faea"
ONE_PAGER = "assets/docs/bugs-n-guns-one-pager.pdf"
CDD = "assets/docs/bugs-n-guns-cdd-es.pdf"
AWARD = "https://www.bilbaogamesconference.com/premios-titanium-2023/"
IMG_STEAM = '<img src="assets/img/logos/steam.webp" alt="" width="18" height="18">'
IMG_ITCH = '<img src="assets/img/logos/itchio.webp" alt="" width="18" height="18">'

SOCIALS = f"""<div class="socials">
      <a class="social" href="https://www.linkedin.com/in/alvarocga/" {EXT}>{I_LINKEDIN}LinkedIn</a>
      <a class="social" href="https://alvarocga.itch.io/" {EXT}>{I_ITCH}Itch.io</a>
      <a class="social" href="https://twitter.com/calvoalvaro12" {EXT}>{I_X}X / Twitter</a>
      <a class="social" href="mailto:Calvoalvaro13@gmail.com">{I_MAIL}Email</a>
    </div>"""

AWARD_HTML = f"""<a class="award" href="{AWARD}" {EXT}>
  <img src="assets/img/logos/big-award.webp" alt="BIG — Bilbao International Games" width="56" height="56">
  <div><strong>Best Student Game</strong><span>Titanium Awards 2023 · Bilbao Games Conference (BIG)</span></div>
</a>"""

CONTACT_CTA = """<section class="section">
  <div class="wrap">
    <div class="cta reveal">
      <div><h2>Let's make games together.</h2><p>Open to Technical Game Design and Combat Design roles.</p></div>
      <div class="actions"><a class="btn btn-primary" href="contact.html">Get in touch</a></div>
    </div>
  </div>
</section>"""

# ================================================================ SHARED (v2)
def case_head(eyebrow, title, lead, actions=""):
    act = f'<div class="actions">{actions}</div>' if actions else ""
    return f"""<section class="wrap proj-head">
  <p class="eyebrow">{eyebrow}</p>
  <h1>{title}</h1>
  <p class="hero-lead">{lead}</p>
  {act}
</section>"""


def sheet(rows, links=(), logo=None, award=False):
    dl = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows)
    lg = f'<img class="sheet-logo" src="{logo[0]}" alt="{logo[1]}">' if logo else ""
    aw = (f'<a class="award" href="{AWARD}" {EXT}><img src="assets/img/logos/big-award.webp" alt="" width="40" height="40">'
          f'<span><strong>Best Student Game</strong>Titanium Awards 2023 · BIG</span></a>') if award else ""
    ext_ic = I_EXT.replace("<svg ", '<svg class="ic" ')
    ln = "".join(f'<li><a href="{u}" {EXT}>{n}{ext_ic}</a></li>' for n, u in links)
    ln = f'<ul class="sheet-links">{ln}</ul>' if links else ""
    return f'<aside class="sheet">{lg}<dl>{dl}</dl>{aw}{ln}</aside>'


def case_grid(sheet_html, main_html, ruled=True):
    return f'<div class="wrap proj-grid{" ruled" if ruled else ""}">{sheet_html}<div class="proj-main">{main_html}</div></div>'


def numbered(items):
    return '<ol class="numbered">' + "".join(f"<li><span>{i}</span></li>" for i in items) + "</ol>"


ARROW_SVG = '<svg class="ic" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg>'

# ================================================================ HOME
PERSONAL = [
    ("you-are-nobody", "You Are Nobody", "img", "assets/img/thumbs/sf2bG8XVwxU.webp", "Global Game Jam · 2025",
     "A stealth game about infiltrating by stealing people's faces with your camera."),
    ("beat-found", "Beat Found", "img", "assets/img/personal/beat-found-cover.webp", "Madrid in Game Hack Jam · 2024",
     "A 3D rhythm platformer: recover all the Heart Beats to make a dystopian Madrid beat again."),
    ("neon-red", "Neon Red", "NoE4qOLrqMI", None, "Com JamOn · 2024",
     "A platformer for speedrunners built around momentum and grappling-hook swings."),
    ("super-transform", "Super Transform", "pPfRK8eXA9U", None, "Madrid in Game Hack Jam · 2023",
     "A first-person puzzle game about transforming objects across the rooftops of a flooded Madrid."),
    ("burger-bros-circus", "Burger Bros Circus", "CI8AUE0d21w", None, "Global Game Jam · 2024",
     "A 1v1 dodgeball-style party game: two gym bros throwing junk food in a circus."),
    ("gea-of-war", "Gea Of War", "SLGUOeP3ZOI", None, "Global Game Jam · 2023",
     "A retro pixel-art arcade shooter: a demigoddess protecting the earth from contamination."),
    ("against-the-clock", "Against The Clock", "EYnCGiVuaXQ", None, "BSc solo project · 2022",
     "Collect every hammer and reach the portal before 00:00. My first Unreal Engine game."),
]


def thumb(vid, override=None):
    return override or f"assets/img/thumbs/{vid}.webp"


def pp_card(s, n, v, t, k, d):
    media = f'<img src="{t if v == "img" else thumb(v, t)}" alt="" loading="lazy" decoding="async">'
    return f"""
      <a class="pp reveal" href="{s}.html"><div class="pp-img">{media}</div>
        <p class="eyebrow">{k}</p><h3>{n}</h3><p>{d}</p></a>"""


def tile(href, img, eyebrow, name, role, tags, cls="", badge=""):
    tg = "".join(f"<li>{x}</li>" for x in tags)
    return f"""
      <a class="tile {cls} reveal" href="{href}">
        <img src="{img}" alt="" loading="lazy" decoding="async">
        <div class="tile-shade"></div>{badge}
        <div class="tile-info"><p class="eyebrow">{eyebrow}</p><h3>{name}</h3><p class="tile-role">{role}</p><ul class="tags">{tg}</ul></div>
        <span class="tile-go">{ARROW_SVG}</span>
      </a>"""


DISCIPLINES = ["Gameplay mechanics &amp; 3Cs", "Combat", "Enemies &amp; AI", "Prototyping", "Level design", "Tools"]
BIG_BADGE = '<span class="tile-badge"><img src="assets/img/logos/big-award.webp" alt="" width="22" height="22">Best Student Game · BIG 2023</span>'

home = f"""
<section class="hero">
  <img class="hero-bg" src="assets/img/thumbs/Yzam-WWlWpI.webp" alt="" fetchpriority="high">
  <div class="hero-shade"></div>
  <div class="wrap hero-in">
    <p class="eyebrow">Technical Game Designer · Madrid</p>
    <h1>Designing how<br>games <span>play.</span></h1>
    <ul class="disc" aria-label="Disciplines">{''.join(f'<li>{d}</li>' for d in DISCIPLINES)}</ul>
    <p class="now"><span class="dot" aria-hidden="true"></span><span>Currently Technical Game Designer at <strong>iBLOXX Studios</strong></span></p>
    <p class="hero-lead">I'm Álvaro Calvo García-Arias. I design, prototype and iterate gameplay in Unreal Engine 5 and Unity, and build the in-engine tools that speed up the team.</p>
    <div class="actions"><a class="btn btn-accent" href="#work">View work</a><a class="btn" href="contact.html">Get in touch</a></div>
  </div>
</section>

<section class="stats"><div class="wrap stats-in">
  <div><strong>4+</strong><span>years in UE5 &amp; Unity</span></div>
  <div><strong>3</strong><span>studio &amp; team titles</span></div>
  <div><strong>7</strong><span>jam &amp; personal games</span></div>
  <a href="{AWARD}" {EXT}><strong>BIG</strong><span>Best Student Game 2023</span></a>
</div></section>

<section class="wrap sec" id="work">
  <div class="sec-head"><p class="eyebrow">01 · Selected work</p><h2>Games I've shaped</h2></div>
  <div class="tiles">{tile("winx.html", "assets/img/thumbs/-eAMfL_nJto.webp", "Iron Frog Studios · 2025 — 2026", "Winx Club", "Game Designer · Combat Designer", ["Core mechanics", "Level blockouts", "Combat arenas", "Enemies &amp; bosses"], "wide")}{tile("macbeth.html", "assets/img/thumbs/5_zhbJUPkPs.webp", "Divertifica · 2023 — 2025", "Macbeth", "Game Designer · Technical Designer", ["3Cs", "Dimension-shift mechanic", "Puzzles", "Level design"])}{tile("bugs-n-guns.html", "assets/img/thumbs/Yzam-WWlWpI.webp", "Blinkshot · 2023", "Bugs 'N' Guns", "Game Designer · Technical Designer", ["Game design", "Prototyping", "Level design", "Enemy AI"], badge=BIG_BADGE)}</div>
</section>

<section class="sec" id="personal">
  <div class="wrap sec-head sec-head-row"><div><p class="eyebrow">02 · Personal projects</p><h2>Jams &amp; experiments</h2></div><a class="link-arrow" href="personal-projects.html">All personal projects</a></div>
  <div class="rail">{''.join(pp_card(*p) for p in PERSONAL)}
  </div>
</section>

<section class="wrap sec" id="about">
  <div class="sec-head"><p class="eyebrow">03 · About</p><h2>Designer who prototypes</h2></div>
  <div class="about-grid">
    <div class="about-text reveal">
      <p>Hi, I'm Álvaro Calvo, a technical designer with over four years of experience working with Unreal Engine 5 and Unity.</p>
      <p>In those four years, I've designed from scratch, prototyped, and iterated on everything from movement and combat mechanics to enemies and AI.</p>
      <p>I also create in-engine tools to streamline the workflow for my fellow designers and myself. I also create levels, combat arenas and puzzles, as well as design and implement world dynamics, systems and interactions.</p>
    </div>
    <div class="reveal">
      <h3 class="mini">Game design skills</h3>
      <ul class="skill-chips">{''.join(f'<li>{s}</li>' for s in ["Mechanics and gameplay design", "Combat system, balance and programming", "Game prototyping", "Level design and enemy encounters", "Enemy design", "Unreal Engine", "Unity"])}</ul>
      <h3 class="mini">Soft skills</h3>
      <ul class="skill-chips ghost">{''.join(f'<li>{s}</li>' for s in ["Fast learner", "Proactive", "Team working", "Good communication", "Adaptability", "Documentation"])}</ul>
    </div>
  </div>
</section>
"""
write("index.html", "Álvaro Calvo García-Arias — Technical Game Designer",
      "Portfolio of Álvaro Calvo García-Arias, Technical Game Designer working with Unreal Engine 5 and Unity: gameplay mechanics, 3Cs, combat, enemies, levels and tools.",
      "", "home", home, header="over")

# ================================================================ WINX
winx = case_head("<a href=\"index.html#work\">Selected work</a> · 01", "Winx Club: The Magic Is Back",
    "Out now on PC, PS5 and Nintendo Switch. An experience that feels both familiar and entirely new: players explore some of the most beloved and iconic locations of the Winx universe and can freely switch between all six fairies, each with their own distinctive magical abilities, to overcome enemies and puzzles in creative new ways.",
    btn("https://store.steampowered.com/app/4007490/", "Get it on Steam", True, IMG_STEAM)) + case_grid(
    sheet([("Role", "Game Designer · Combat Designer"), ("Studio", "Iron Frog Studios"), ("Publisher", "Maximum Entertainment"), ("Genre", "Action-Adventure"),
           ("Platform", "PC · PS5 · Nintendo Switch"), ("Engine", "Unity"), ("Status", "Released"), ("Date", "Feb 2025 — Mar 2026")],
          [("Iron Frog Studios", "https://www.ironfrogstudios.com/")],
          logo=("assets/img/logos/iron-frog.webp", "Iron Frog Studios")),
    f"""{yt("-eAMfL_nJto", "Winx Club: The Magic is Back — Announce Trailer")}
    <p class="me">I worked as Game Designer and Combat Designer on this game at <a href="https://www.ironfrogstudios.com/" {EXT} style="color:var(--accent)">Iron Frog Studios</a>.</p>
    <h2>My contributions</h2>
    <p class="muted" style="margin-bottom:14px">My main contributions to the game:</p>
    {numbered(["Designed and documented the core mechanics (3Cs, interactions, puzzles, combat abilities, etc.).",
               "Designed and blocked out several levels of the game.",
               "Designed and implemented all combat arenas.",
               "Designed and balanced all the enemies, bosses and minibosses."])}""") + """
<section class="wrap section"><nav data-pager="work" aria-label="More projects"></nav></section>
"""
write("winx.html", "Winx Club: The Magic Is Back — Álvaro Calvo García-Arias",
      "Game Designer and Combat Designer on Winx Club: The Magic Is Back at Iron Frog Studios: core mechanics, levels, combat arenas, enemies and bosses.",
      "work", "winx", winx, og="assets/img/thumbs/-eAMfL_nJto.webp")

# ================================================================ MACBETH
ITCH_MACBETH = "https://divertifica.itch.io/macbeth-seeds-of-fate"
macbeth = case_head("<a href=\"index.html#work\">Selected work</a> · 02", "Macbeth: Seeds of Fate",
    "An interactive 3D adventure in which players explore the environment and solve puzzles to unravel the story of Macbeth. You incarnate Shakespeare, who, with the help of some supernatural powers, must travel between two realities to discover and write the incredible play Macbeth.",
    btn(ITCH_MACBETH, "Play on Itch.io", True, IMG_ITCH))+ case_grid(
    sheet([("Role", "Game Designer · Technical Designer"), ("Studio", "Divertifica"),
           ("Team", "1 Creative Director, 3 Game Designers, 3 Programmers, 8 Artists, 2 Sound Designers, 3 Cast"),
           ("Genre", "Puzzle · Narrative"), ("Platform", "PC"), ("Engine", "Unreal Engine 5"), ("Date", "3 Dec 2023 — 10 Jan 2025")],
          [("Divertifica", "https://divertifica.es/")],
          logo=("assets/img/logos/divertifica.webp", "Divertifica")),
    f"""<div class="video-pair">
      <div><p class="video-label">3D vertical slice — final concept</p>{yt("5_zhbJUPkPs", "Macbeth: Seeds of Fate — vertical slice gameplay")}</div>
      <div><p class="video-label">2D minigames — original concept</p>{yt("FyymwatUNNI", "Macbeth — 2D prototype trailer")}</div>
    </div>
    <p class="me">I worked as Game Designer and Technical Designer on this game at <a href="https://divertifica.es/" {EXT} style="color:var(--accent)">Divertifica</a>.</p>
    <h2>About this game</h2>
    <div class="prose">
      <p>This game has been cancelled, but it is playable on <a href="{ITCH_MACBETH}" {EXT}>Itch.io</a>. What you see in the video is the vertical slice we created for funding purposes.</p>
      <p>The game was initially conceived as a 2D minigame-based experience (you can see the trailer for that version above). However, we later shifted our focus toward a more ambitious storytelling approach.</p>
      <p>In the new concept the player controls Shakespeare, who, guided by the three Moirai (Fates), is led to an ancient castle where the events of the play took place. With the ability to travel between the past and the present, the player has to solve puzzles and unravel the story that Shakespeare would eventually write.</p>
    </div>
    <h2>My contributions</h2>
    <p class="muted" style="margin-bottom:14px">Designed and prototyped mechanics and systems, including, among others:</p>
    {numbered(["<strong>Player core mechanics</strong><ul><li>The movement, camera and control mechanics of the player (3Cs).</li><li>The dimensional transition mechanic.</li><li>All the puzzles and interactions.</li></ul>",
               "<strong>Level interactables:</strong> design, programming and implementation of the level interactables (doors, candles, drawers, keys…).",
               "<strong>Level design:</strong> from beat chart to final, going through layout and blocking, I designed the entire level.",
               "<strong>Technical implementation</strong> of shaders and final gameplay elements like puzzles or the transition mechanic.",
               "<strong>Team support:</strong> helped the rest of the design team with Unreal Engine, GitHub and other tools."])}""") + """
<section class="wrap section"><nav data-pager="work" aria-label="More projects"></nav></section>
"""
write("macbeth.html", "Macbeth: Seeds of Fate — Álvaro Calvo García-Arias",
      "Game Designer and Technical Designer on Macbeth: Seeds of Fate at Divertifica: 3Cs, dimensional transition mechanic, puzzles, interactables and level design.",
      "work", "macbeth", macbeth, og="assets/img/thumbs/5_zhbJUPkPs.webp")

# ================================================================ BNG shared
BNG_ACTIONS = (btn(STEAM_BNG, "Steam", True, IMG_STEAM) + btn(NOTION_GDD, "GDD on Notion") +
               btn(ONE_PAGER, "One Pager") + btn(CDD, "CDD (ES)"))


def bng_hero(h1, lead, eyebrow_extra="", actions=""):
    return hero(f"<a href=\"bugs-n-guns.html\">Bugs 'N' Guns</a>{eyebrow_extra}", h1, lead, actions)


SUBNAV = '<nav data-subnav="bng" aria-label="Bugs \'N\' Guns sections"></nav>'
BNG_PAGER = '<section class="section"><div class="wrap"><nav data-pager="bng" aria-label="Bugs \'N\' Guns sections"></nav></div></section>'

# ================================================================ BNG overview
AWARD_INLINE = (f'<a class="award award-inline" href="{AWARD}" {EXT}><img src="assets/img/logos/big-award.webp" alt="" width="32" height="32">'
                f'<span><strong>Best Student Game</strong>Titanium Awards 2023 · BIG</span></a>')
contrib = [
    ("bng-game-design.html", "assets/img/bng/card-game-design.webp", "Game Design",
     "I worked as a game designer on Bugs 'N' Guns from the ideation until the vertical slice."),
    ("bng-prototyping.html", "assets/img/bng/card-prototyping.webp", "Prototyping",
     "Iterating and creating from scratch all the interactables, enemies, weapons and mechanics using Blueprints in UE5."),
    ("bng-level-design.html", "assets/img/bng/card-level-design.webp", "Level Design",
     "From the 2D layout and beat chart to the combat arenas and encounter design."),
    ("bng-tools.html", "assets/img/bng/debug-tool.webp", "Tools 'N' Tech",
     "Tools for a better and faster workflow for my design teammates, plus important programming tasks such as level streaming, checkpoints and saves."),
    ("bng-blinkball.html", "assets/img/bng/card-blinkball.webp", "BlinkBall",
     "In my spare time, I made an easter-egg minigame where both players face each other in a Rocket League-like match."),
]
contrib_list = "".join(f"""
      <li><a href="{h}"><img src="{img}" alt="" loading="lazy" decoding="async"><div><span class="num">{i:02d}</span><h3>{t}</h3><p>{d}</p></div>{ARROW_SVG}</a></li>""" for i, (h, img, t, d) in enumerate(contrib, 1))
phases = "".join(f"<li><strong>{a}</strong><span>{b}</span></li>" for a, b in
                 [("Core design &amp; first playable", "Feb — May 2023"), ("Alpha", "May — Jul 2023"), ("Beta", "Jul — Sep 2023"), ("Gold", "Sep — late Oct 2023")])

bng = case_head("<a href=\"index.html#work\">Selected work</a> · 03", "Bugs 'N' Guns",
    "A third-person co-op shooter where players take on the role of interplanetary garbage disposers. Their task is to escort a train through a hostile alien environment, using elemental weapons and combinations to fight against a mysterious race of insects.",
    btn(STEAM_BNG, "Get it on Steam", True, IMG_STEAM) + AWARD_INLINE) + SUBNAV + case_grid(
    sheet([("Role", "Game Designer · Technical Designer"), ("Studio", "Blinkshot"), ("Context", "Master's Degree final project"),
           ("Team", "6 Game Designers, 6 Programmers, 5 Artists"), ("Genre", "Third-person co-op shooter"), ("Platform", "PC (Steam)"),
           ("Engine", "Unreal Engine 5 · Maya, Substance Painter, ZBrush")],
          [("GDD on Notion", NOTION_GDD), ("One Pager", ONE_PAGER), ("CDD (ES)", CDD), ("@BugsnGuns", "https://twitter.com/BugsnGuns")]),
    f"""{yt("Yzam-WWlWpI", "Bugs 'N' Guns — Trailer")}
    <p class="me">I worked as Game Designer and Technical Designer on this game as my Master's Degree Final Project.</p>
    <h2>What I did</h2>
    <ol class="contrib">{contrib_list}
    </ol>
    <h2>Gameplay</h2>
    {yt("XM_g9x7btv4", "Bugs 'N' Guns — Gameplay Trailer")}
    <h2>Timeline</h2>
    <ol class="phases">{phases}</ol>
    <p class="muted" style="margin-top:16px">During this project I was mentored by industry professionals.</p>""", ruled=False) + """
<section class="wrap section"><nav data-pager="work" aria-label="More projects"></nav></section>
"""
write("bugs-n-guns.html", "Bugs 'N' Guns — Álvaro Calvo García-Arias",
      "Game Designer and Technical Designer on Bugs 'N' Guns, a third-person co-op shooter. Best Student Game at the Titanium Awards 2023.",
      "bng", "bng", bng)

# ================================================================ BNG dossier helpers
def dossier_head(num, title, lead, actions=""):
    return case_head(f'<a href="bugs-n-guns.html">Bugs \'N\' Guns</a> · {num}', title, lead, actions)


def glance(items):
    cells = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in items)
    return f'<section class="wrap glance-wrap"><p class="section-label">At a glance</p><dl class="glance">{cells}</dl></section>'


def side_index(entries, docs=(), title="On this page"):
    items, n = [], 0
    for a, t in entries:
        if t.startswith("· "):
            items.append(f'<li class="sub"><a href="#{a}">{t[2:]}</a></li>')
        else:
            n += 1
            items.append(f'<li><a href="#{a}"><span>{n:02d}</span>{t}</a></li>')
    idx = "".join(items)
    ext_ic = I_EXT.replace("<svg ", '<svg class="ic" ')
    dl = "".join(f'<li><a href="{u}" {EXT}>{n}{ext_ic}</a></li>' for n, u in docs)
    dl = f'<p class="side-title">Documentation</p><ul class="sheet-links">{dl}</ul>' if docs else ""
    return f'<aside class="sheet side-index"><p class="side-title">{title}</p><ol class="toc-side">{idx}</ol>{dl}</aside>'


def dossier(index_html, main_html):
    return f'<div class="wrap proj-grid">{index_html}<div class="proj-main dossier">{main_html}</div></div>'


def chapter_h(anchor, num, title, intro_paras=(), chips=""):
    intro = "".join(f"<p>{p}</p>" for p in intro_paras)
    ch = f'<div class="chips">{chips}</div>' if chips else ""
    return f'<header class="ch-head" id="{anchor}"><span class="ch-num">{num}</span><h2>{title}</h2><div class="prose">{intro}</div>{ch}</header>'


def design_case(title, tags, notion_url, media, challenge, iterations, final, extra=""):
    tg = "".join(f"<li>{t}</li>" for t in tags)
    def col(label, paras, cls=""):
        return f'<div class="cp{cls}"><p class="cp-label">{label}</p><div class="prose">{"".join(f"<p>{p}</p>" for p in paras)}</div></div>'
    return f"""
    <article class="dcase reveal">
      <div class="dcase-head"><div><h3>{title}</h3><ul class="tags">{tg}</ul></div>{notion(notion_url, title) if notion_url else ""}</div>
      {media}
      <div class="cps">{col("Challenge", challenge)}{col("Iterations", iterations)}{col("Final design", final, " final")}</div>{extra}
    </article>"""


# ================================================================ BNG game design
gd_index = side_index([("role", "My role"), ("vision", "Shared vision"), ("in-practice", "Pillars in practice"), ("elements", "Elements &amp; weapons")],
                      [("GDD on Notion", NOTION_GDD), ("One Pager", ONE_PAGER), ("CDD (ES)", CDD)])
gd_main = f"""
    {chapter_h("role", "01", "My role", [
        "As a designer, I have been deeply engaged in shaping the game concept from the start to the vertical slice. I conceptualized the core gameplay loop and established the fundamental design pillars that have influenced all our design decisions.",
        "I have consistently contributed to and participated in all design meetings, playing a crucial role in every decision throughout the game's development.",
        "I also contributed to the documentation of the GDD for Bugs 'N' Guns, focusing primarily on the 3Cs (Character, Camera, Control) and the sections related to combat, encounters, enemies, weapons and interactive elements.",
        "To achieve this, we used Notion to create a comprehensive GDD, and tools like Photoshop and Illustrator to produce detailed documentation for art and programming purposes."])}
    <div class="reveal">{fig("assets/img/bng/one-pager.webp", "Bugs 'N' Guns one pager", "One Pager: click to open the full PDF.", link=ONE_PAGER)}</div>

    {chapter_h("vision", "02", "Shared vision", [
        "One of the most challenging tasks in design is to ensure that everyone shares the same vision for the game.",
        "However, it's also the most important, because otherwise each team member will have a different idea of what is being made, leading to aimless decision-making that can harm the final result.",
        "To tackle this in the design team, we established three pillars and three verbs to build the gameplay upon:"])}
    <dl class="pillars big reveal">
      <div><dt>Core verbs</dt><dd><span>Escort</span><span>Cooperate</span><span>Shoot</span></dd></div>
      <div><dt>Experience pillars</dt><dd><span>Reactivity</span><span>Dependence</span><span>Frenzy</span></dd></div>
    </dl>
    <div class="prose after">
      <p>From these foundations, we designed the entire game, from the core loop to the levels, including weapons, enemies, elemental interactions, and the rest of the mechanics and dynamics present in Bugs 'N' Guns.</p>
      <p>Coming to these conclusions was undoubtedly the most time-consuming part of our discussions and meetings. However, once we established the anchor on which all our decisions pivoted, the rest came much more easily and naturally (not to say there weren't any discussions), as it was no longer about designing based on what each team member believed to be the most fun, but rather on what best supported those anchors.</p>
      <p>That way, when discussing any feature, we always referred back to what aligned best with our pillars to make the decision. Even if another idea seemed more fun to you, ultimately the team would conclude what was best.</p>
    </div>

    {chapter_h("in-practice", "03", "Pillars in practice", ["A very representative example of how we followed our pillars is the element system, one of the central axes on which combat revolves. Each design decision traces back to a verb or a pillar:"])}
    <div class="map reveal">
      <div class="map-row"><p class="map-key"><span>Cooperate</span><span>Dependence</span></p><p>Each player has two elemental weapons, but a player's weapons only combine with those of the other player, never with their own. Without mutual assistance, it is impossible to progress in the adventure.</p></div>
      <div class="map-row"><p class="map-key"><span>Shoot</span></p><p>All the actions and puzzles that players have to solve are done by shooting, including the element puzzles.</p></div>
      <div class="map-row"><p class="map-key"><span>Escort</span></p><p>Besides combat, the element system is used in the puzzles, where players combine their weapons to escort the train through the hostile terrains of Bugs 'N' Guns.</p></div>
      <div class="map-row"><p class="map-key"><span>Frenzy</span></p><p>A very fast-paced combat was established to generate frenzy.</p></div>
      <div class="map-row"><p class="map-key"><span>Reactivity</span></p><p>Dynamically changing environments and situations make players take on-the-fly decisions: we change the environment or add obstacles that players have to deal with while escorting the train.</p></div>
    </div>

    {chapter_h("elements", "04", "Elements &amp; weapons", ["After establishing our pillars, we began to develop the mechanics and dynamics that would make up the game. Each player carries two weapons which, when combined with the other player's, produce powerful interactions either on enemies or on the ground."])}
    <div class="reveal">{fig("assets/img/bng/weapons-elements.webp", "The weapons and the elements of Bugs 'N' Guns and their combinations")}</div>
    <p class="video-label" style="margin-top:36px">Gameplay trailer</p>
    {yt("XM_g9x7btv4", "Bugs 'N' Guns — Gameplay Trailer")}
"""
gd = dossier_head("01", "Game Design", "Shaping the concept of Bugs 'N' Guns from the very start to the vertical slice: core loop, design pillars and documentation.") + SUBNAV + glance([
    ("Scope", "From ideation to the vertical slice"),
    ("Foundations", "Core gameplay loop, 3 core verbs and 3 experience pillars"),
    ("Documentation", "GDD sections on 3Cs, combat, encounters, enemies, weapons and interactables"),
    ("Tools", "Notion, Photoshop and Illustrator")]) + dossier(gd_index, gd_main) + BNG_PAGER
write("bng-game-design.html", "Game Design · Bugs 'N' Guns — Álvaro Calvo García-Arias",
      "Game design of Bugs 'N' Guns: core loop, design pillars, core verbs and how they shaped the elemental weapon combination system.",
      "bng", "bng-game-design", gd)

# ================================================================ BNG prototyping
HYDRO_THUMB = "https://i.ytimg.com/vi/tIn--X-9LRo/hqdefault.jpg"
N = "https://sable-sandalwood-dee.notion.site/"

weapons = [
    ("Fire", "DPS", "Burst rifle, three bullets per burst", "High damage, relatively slow"),
    ("Spore", "CC", "Submachine gun", "Slows enemies down"),
    ("Hydrogel", "CC", "Hose", "Ground bubbles that explode and knock enemies back; direct hits push them back"),
    ("Electroplasm", "DPS", "Charged single projectile", "Piercing damage, reduced by each enemy it passes through"),
]
weapon_cards = "".join(f"""
      <div class="wcard"><div class="wcard-top"><h4>{n}</h4><span class="role role-{r.lower()}">{r}</span></div>
        <dl><div><dt>Final archetype</dt><dd>{a}</dd></div><div><dt>Effect</dt><dd>{e}</dd></div></dl></div>""" for n, r, a, e in weapons)

pr_index = side_index([("prototype", "Pre-Alpha prototype"), ("three-cs", "Player 3Cs"), ("double-jump", "· Double jump"), ("blinkshot", "· Blinkshot"),
                       ("elements", "Elements &amp; weapons"), ("fire", "· Fire"), ("spore", "· Spore"), ("hydrogel", "· Hydrogel"), ("electroplasm", "· Electroplasm"),
                       ("enemies", "Enemies"), ("puckarb", "· Puckarb")],
                      [("3Cs", N + "PLAYER-CCC-2d1cab680b64497980cc05e238e354ce"), ("Elements", N + "ELEMENTS-269e489d38f5446e8d27e38d62bc7960"), ("Enemies", N + "ENEMIES-2a75067c74544431abecd884cc34e9df")])


def anchor(a, html_):
    return html_.replace('<article class="dcase reveal">', f'<article class="dcase reveal" id="{a}">', 1)


pr_main = f"""
    {chapter_h("prototype", "01", "Pre-Alpha prototype", [
        "This was the look of Bugs 'N' Guns in the Pre-Alpha. This prototype was made by the design team to iterate and validate mechanics and level ideas.",
        "Everything in the video was made by a designer, and I made quite a lot of it. On this page I showcase some of the most important and interesting pieces."])}
    {yt("vTBhdAZtNsY", "Bugs 'N' Guns — Pre-Alpha prototype")}

    {chapter_h("three-cs", "02", "Player core mechanics (3Cs)", [
        "One of the key and most important aspects we had to test in-game were the 3Cs. For this, we prototyped a functional character via Blueprints with all the features we wanted to test.",
        "There were many, some of which were completely discarded while others were iterated countless times. Here are two that were especially important and took several iterations and meetings to address."])}
    {anchor("double-jump", design_case("Double jump", ["3Cs", "Movement"], N + "Jumping-cfb2f8fc3ba14e30a5f7f6579502dcd3", yt("N4DxyZoo71Q", "Double jump prototype"),
        ["The first and most troublesome feature was the jump, specifically the double jump.",
         "We needed it because in the game we escort a train through hostile terrain and can be attacked from all directions, so it is essential to be able to move quickly from one side of the train to the other."],
        ["This meant we needed a considerably high double jump, but such a high jump caused the player to move horizontally much more than we intended and, worse, to stay in the air for a very long time."],
        ["After many iterations and meetings, instead of a double jump the player gets a vertical thrust, as if they had two small rockets on their back, providing the height we wanted without the horizontal inertia.",
         "We also added air friction and adjusted the gravity values so that jumps in general felt more natural. It seems obvious now, but at the time it was a serious issue."]))}
    {anchor("blinkshot", design_case("Blinkshot", ["3Cs", "Mobility", "Core mechanic"], N + "Blinkshot-8f6e5fa67ef440c29586d23cf079f8ac", yt("WHnHrLpxWmY", "Blinkshot prototype"),
        ["This mechanic is the most representative of the game's essence and also gives the studio its name. It arises from one of our core verbs, shooting: all interactions with the world and its systems are done by shooting.",
         "In parallel, we needed a mobility tool. Since the game is fast-paced and cooperation is essential, players needed to quickly and dynamically regroup and split up: some type of dash or blink ability."],
        ["Initially, we considered a horizontal dash, but our game is also very vertical, and there are situations where you want to move down or diagonally. We needed an omnidirectional tool."],
        ["After many meetings and iterations, we decided to treat the blink as a shot: you choose the direction by aiming and teleport by shooting. This solved one of the game's mobility problems while reinforcing the idea that everything is done by shooting.",
         "It has many more interactions and functionalities: with enemies and environmental elements, its game-feel peculiarities, and the restrictions that prevent players from breaking the level. What I explain here is just the ideation; the mechanic was adjusted throughout the entire development."]))}

    {chapter_h("elements", "03", "Elements &amp; weapons", [
        "Elements and weapons are the players' tools not only for combat but for all interactions with the world, as in this game everything is done by shooting.",
        "All four weapons were tested and prototyped. They underwent the most iterations and had the most versions, because they needed to work both as combat weapons and as puzzle-solving tools. The two DPS weapons ended up slow and precise but very powerful, while the CC (crowd control) weapons are very fast, with low damage, but excel at “painting” the level with their elements."])}
    <div class="wgrid reveal">{weapon_cards}
    </div>
    <div class="combos reveal">
      <p class="cp-label">Key combinations</p>
      <ul>
        <li><strong>Hydrogel + Electroplasm:</strong> electrified bubbles stun enemies and deal damage.</li>
        <li><strong>Hydrogel + Spore:</strong> a toxic cloud that makes enemies turn against each other, plus a dedicated water–spore interactable for puzzles.</li>
        <li><strong>DPS + CC:</strong> combining the CC areas with the other weapons results in a devastating finale.</li>
      </ul>
    </div>
    {anchor("fire", design_case("Fire", ["DPS"], N + "Fire-DPS-f383ada3dfc14f3b9b0ea630f5473523", yt("uZoiFMmk6YU", "Fire weapon prototype"),
        ["Fire was clear in terms of puzzles: it was fire. The problem arose more on the combat side."],
        ["Initially it was supposed to be like a fire hose, but it left a trail of fire wherever it touched the floor, and that trail caused contact damage. In other words, it was too powerful.",
         "We tried several concepts, ranging from a sniper rifle to a grenade launcher."],
        ["A burst rifle with three bullets per burst: high damage but relatively slow.",
         "This also set the rule for the whole arsenal: DPS weapons slow, precise and powerful; CC weapons fast, low damage and great at creating large CC areas."]))}
    {anchor("spore", design_case("Spore", ["CC"], N + "Spores-CC-f8ff913d5a1c4135b43f3abe776a79fe", yt("VWwqmM7BDx8", "Spore weapon prototype"),
        ["The spore weapon was the closest to its final form from the beginning: conceived as a submachine gun, it kept that archetype and didn't cause problems with its interactions. What changed was its effect on enemies."],
        ["Initially it poisoned them, dealing damage over time, to differentiate it from fire, whose burn would deal damage and disappear.",
         "However, this didn't work out: it was clearly the most powerful weapon of all, and its damage potential conflicted with the idea of a CC weapon."],
        ["We removed the poison and turned it into a slow effect."]))}
    {anchor("hydrogel", design_case("Hydrogel", ["CC"], N + "Water-Hydrogel-CC-c3debd33f909474ca500d1902eb90406", ph("BNG-PROTO-HYDROGEL-VIDEO", "Video: Hydrogel prototype (the Wix video is private on YouTube)"),
        ["The water weapon was problematic, not in its behaviour (we knew from the beginning it would be a hose) but in the effects on enemies, the ground and their interactions."],
        ["Ideas ranged from a vortex that trapped enemies when it touched the ground, to a bubble that lifted the enemy and then exploded, causing fall damage, and many other crazy concepts.",
         "The real challenge was the water–spore interaction, especially since it also needed to work for puzzles. We considered making it grow plants, but this was discarded due to art restrictions."],
        ["When water touches the ground it creates a bubble that explodes and knocks enemies back when they touch it; hitting an enemy directly with the hose pushes them back.",
         "Electrifying the bubbles stuns enemies and deals damage, and water plus spores creates a toxic cloud (similar to what spores used to do) that makes enemies turn against each other. For puzzles, we created a specific water–spore interactable."]))}
    {anchor("electroplasm", design_case("Electroplasm", ["DPS"], N + "Electroplasm-DPS-e1e04b9cf72947e6a8c9ed9a67ea8f02", ph("BNG-PROTO-ELECTROPLASM-VIDEO", "Video: Electroplasm prototype (the Wix video is private on YouTube)"),
        ["The electric weapon was much simpler to design, though it had a few ups and downs. The biggest challenge was deciding what it would do to enemies: we had too many good ideas. It was clear the special effect would only apply when fully charged."],
        ["Initially we wanted it to work like a fusion rifle from Destiny 2. The concept remained similar, but it fires a single projectile instead of multiple ones, with damage varying with how long it is charged.",
         "The most popular effects were chain lightning and a stun, but both were discarded because they provided too much CC for a DPS weapon."],
        ["Piercing damage, where each enemy the projectile passes through reduces its damage."]))}

    {chapter_h("enemies", "04", "Enemies", [
        "Enemies are a key part of the game, so they took a lot of time and resources. We iterated on the enemy concepts countless times to meet the game's needs as well as the restrictions of other departments.",
        "Besides designing the enemy concepts in the design meetings, I was responsible for prototyping them, including their interactions with other mechanics and gameplay elements, and their AI through behaviour trees, iterating until reaching a satisfactory result."])}
    <article class="dcase reveal" id="puckarb">
      <div class="dcase-head"><div><h3>Puckarb</h3><ul class="tags"><li>Smasher</li><li>Horde</li><li>Climber</li></ul></div>{notion(N + "Smasher-Mauricio-4e7735800a354204bb4f943fe9123832", "Puckarb")}</div>
      {yt("YiysNERDmto", "Puckarb (smasher) enemy prototype")}
      <dl class="profile">
        <div><dt>Role</dt><dd>The basic and most common enemy</dd></div>
        <div><dt>Range</dt><dd>Short-range, ground</dd></div>
        <div><dt>Health</dt><dd>Low</dd></div>
        <div><dt>Behaviour</dt><dd>Appears in groups; climbs walls and ceilings</dd></div>
      </dl>
      <div class="cps">
        <div class="cp"><p class="cp-label">Why it climbs</p><div class="prose"><p>Being able to climb creates many moments of surprise, with ambushes from places where players are not used to encountering enemies. At the same time, being always on a surface makes them perfect targets for weapon combinations to eliminate them quickly.</p></div></div>
        <div class="cp final"><p class="cp-label">Design process</p><div class="prose"><p>This enemy was relatively easy to design. It was clear that we needed a “smasher” type enemy and, given the foundations we had established, a “horde” type as well. The climbing ability came naturally, as the train sometimes travels along walls or ceilings, so we needed enemies that could pursue it.</p></div></div>
      </div>
    </article>
    <div class="reveal" style="margin-top:20px">{ph("BNG-PROTO-ENEMIES-MORE", "Pending: the rest of the enemies (on Wix this part was marked as WIP)")}</div>
"""
proto = dossier_head("02", "Prototyping", "Prototype &amp; low-level design: iterating and validating mechanics and level ideas in UE5 Blueprints.") + SUBNAV + glance([
    ("Pre-Alpha", "Prototype built by the design team in UE5 Blueprints"),
    ("3Cs", "Double jump reworked into a vertical thrust; Blinkshot as the core mobility mechanic"),
    ("Weapons", "Four elemental weapons, each both a combat weapon and a puzzle tool"),
    ("Enemies", "Concepts, interactions and AI with behaviour trees")]) + dossier(pr_index, pr_main) + BNG_PAGER
write("bng-prototyping.html", "Prototyping · Bugs 'N' Guns — Álvaro Calvo García-Arias",
      "Prototyping in Bugs 'N' Guns: double jump and Blinkshot 3Cs, the four elemental weapons and the Puckarb enemy, all in UE5 Blueprints.",
      "bng", "bng-prototyping", proto, og="assets/img/thumbs/vTBhdAZtNsY.webp")

# ================================================================ BNG tools


def tool_card(anchor_id, title, media, text):
    return f'<article class="tcard reveal" id="{anchor_id}">{media}<div class="tcard-body"><h3>{title}</h3>{text}</div></article>'


tl_index_full = side_index([("debug", "Debugging tool"), ("streaming", "Level streaming"), ("checkpoints", "Checkpoints &amp; saves"), ("optimization", "Optimization")])
tl_main = f"""
    <div class="tgrid">
      {tool_card("debug", "Debugging tool", fig("assets/img/bng/debug-tool.webp", "In-game debugging tool: train controls, god mode and teleports to every level section"),
                 "<p>In-game debug menu to control the train (spline point, start/stop, speed, immortality), toggle player god-mode options (immortal, infinite jumps, infinite Blinkshot) and teleport the train or the players to any section of the level.</p>" + phtext("BNG-TOOLS-DEBUG-TXT", "Pending text: full description of the Debugging Tool."))}
      {tool_card("streaming", "Level streaming", ph("BNG-TOOLS-STREAMING-MEDIA", "Image or video: level streaming"), phtext("BNG-TOOLS-STREAMING-TXT", "Pending text: how the level streaming was implemented."))}
      {tool_card("checkpoints", "Checkpoints &amp; saves", ph("BNG-TOOLS-CHECKPOINT-MEDIA", "Image or video: checkpoint and save system"), phtext("BNG-TOOLS-CHECKPOINT-TXT", "Pending text: checkpoint and save system."))}
      {tool_card("optimization", "Optimization", ph("BNG-TOOLS-OPTIMIZATION-MEDIA", "Image or video: optimization work"), phtext("BNG-TOOLS-OPTIMIZATION-TXT", "Pending text: optimization tasks."))}
    </div>
"""
if not SHOW_PLACEHOLDERS:
    tl_index = side_index([("debug", "Debugging tool"), ("also", "Other tech work")])
    tl_main = f"""
    <div class="split" id="debug">
      <div>{fig("assets/img/bng/debug-tool.webp", "In-game debugging tool: train controls, god mode and teleports to every level section")}</div>
      <div class="prose"><h2>Debugging tool</h2><p>In-game debug menu to control the train (spline point, start/stop, speed, immortality), toggle player god-mode options (immortal, infinite jumps, infinite Blinkshot) and teleport the train or the players to any section of the level.</p></div>
    </div>
    <div class="prose" id="also" style="margin-top:48px"><h2>Other tech work</h2><p>Besides the tools, I assisted with important programming tasks such as level streaming, checkpoints and saves, and optimization.</p></div>
"""
else:
    tl_index = tl_index_full
tools = dossier_head("03", "Tools 'N' Tech", "I helped my design teammates by creating tools for a better and faster workflow, and also assisted with various important programming tasks such as level streaming, checkpoints and saves, among others.") + SUBNAV + glance([
    ("Workflow", "In-engine tools for a faster design workflow"),
    ("Debugging", "Train controls, god mode and teleports to every section"),
    ("Tech", "Level streaming, checkpoints and saves"),
    ("Performance", "Optimization tasks")]) + dossier(tl_index, tl_main) + BNG_PAGER
write("bng-tools.html", "Tools 'N' Tech · Bugs 'N' Guns — Álvaro Calvo García-Arias",
      "Tools and tech in Bugs 'N' Guns: in-game debugging tool, level streaming, checkpoints and saves, and optimization.",
      "bng", "bng-tools", tools)

# ================================================================ BNG level design
steps = [("rules", "Rules &amp; objectives"), ("beat-chart", "Beat chart"), ("layout", "2D layout"), ("blockout", "Blockout"), ("arenas", "Arenas &amp; encounters")]
stepper = '<ol class="steps reveal">' + "".join(f'<li><a href="#{a}"><span>{i:02d}</span>{t}</a></li>' for i, (a, t) in enumerate(steps, 1)) + "</ol>"


def encounter(anchor_id, title, img, alt, rows):
    dl = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows)
    return f"""
    <article class="enc reveal" id="{anchor_id}">
      <div class="enc-media">{fig(img, alt)}</div>
      <div><h3>{title}</h3><dl class="enc-facts">{dl}</dl></div>
    </article>"""


ld_index = side_index(steps + [("arena-1", "· First arena"), ("arena-4", "· Fourth arena")],
                      [("Level Design", N + "LEVEL-DESIGN-9b41a421d3874e27a6570153073ee32b"), ("Level info", N + "Level-info-c69360a2bd75489696d31a57eb194598"),
                       ("Beat chart", N + "Beat-chart-f3648a0a18444f2abd06e8bf40f4dfbd"), ("Combat Design", N + "Combat-Design-f8c75218f2324956b44007a6a0f4c249")])
ld_main = f"""
    <p class="section-label">The pipeline</p>
    {stepper}

    {chapter_h("rules", "01", "Rules, objectives &amp; general concept", [
        "I was directly involved in making decisions about the general concepts on which the level should be designed, including the feelings and experiences we wanted the player to have and how we planned to deliver them.",
        "I also focused on the technical aspects of the level to make sure our goals were achievable with the team and time we had available.",
        "The objective table outlines what to promote and what to avoid, as we decided to follow it for the creation of the entire level."])}
    <div class="reveal">{fig("assets/img/bng/level-objectives.webp", "Level objectives table: what to promote and what to avoid")}</div>

    {chapter_h("beat-chart", "02", "General path &amp; beat chart", [
        "I was involved in the design and creation of the beat chart for Bugs 'N' Guns, the tool we used to define the rhythm, intensity and duration of all the level phases.",
        "We determined when fights would occur, with which enemies, and how intense they would be. We also established where the puzzles would be, which elements would be used to solve them, and how difficult they would be.",
        "Additionally, we outlined various “WOW” moments where we wanted to leave an impact on the player."])}
    <div class="reveal">{fig("assets/img/bng/beat-chart.webp", "Bugs 'N' Guns beat chart")}</div>

    {chapter_h("layout", "03", "2D layout", [
        "I was involved in designing and creating the 2D layout for all the levels in Bugs 'N' Guns, from the initial whiteboard sketches to the final detailed map.",
        "One of the major challenges was managing the diverse gameplay and multiple biomes, combined with the player's high mobility and vertical exploration, which complicated the task for our art team to visually complete the levels. Consequently, our design strategy emphasized reusing areas efficiently while ensuring varied gameplay with minimal adjustments."])}
    <div class="split layout-split">
      <div class="reveal">{fig("assets/img/bng/layout-2d.webp", "2D layout of the Bugs 'N' Guns levels")}</div>
      <div class="reuse reveal">
        <p class="cp-label">Reuse strategy</p>
        <div class="rcard"><h4>Revisited arenas</h4><p>Two large arenas that players revisit. New elements on re-entry, such as the weapons available at that stage and slight changes in the environment, make each visit a distinctly different experience.</p></div>
        <div class="rcard"><h4>Shared-shell arenas</h4><p>Three smaller arenas for more static combat share identical wall and ceiling designs, so most decoration is reused. Changing the floor layout, enemy placement and train position gives each one a unique feel.</p></div>
        <div class="rcard"><h4>Symmetrical caves</h4><p>The entry and exit of the largest arena are symmetrical caves, avoiding duplicated decoration work. Both focus on platforming with a twist: in one, players chase the train; in the other, they use the train as a platform.</p></div>
      </div>
    </div>

    {chapter_h("blockout", "04", "From layout to blockout", ["This video shows the transition from the 2D layout to the level blocking."])}
    {yt("tICzsxpXogc", "Bugs 'N' Guns — from 2D layout to level blocking")}

    {chapter_h("arenas", "05", "Arenas &amp; encounters", ["During the development of Bugs 'N' Guns, I was in charge of designing all the combat and encounters in the game. These are two of the game's arenas."])}
    {encounter("arena-1", "First game arena", "assets/img/bng/arena-1.webp", "Layout of the first game arena", [
        ("Goal", "Introduce the basic mechanics and dynamics of gameplay (combining weapons) in a controlled and accessible environment."),
        ("Layout", "The train runs alongside a pit from which no enemies can emerge, so players only need to focus on one side of the train. This reduces the intensity and lets them concentrate on learning the mechanics."),
        ("Enemies", "The most basic Smashers, practice targets posing a low, though not nonexistent, threat. Because they arrive in waves, players must learn to combine their weapons, the core gunplay mechanic."),
        ("Teaching moment", "The final spawn climbs down one of the rock walls, teaching that enemies can climb and bypass obstacles, and that players can “paint” the walls to defeat them before they reach the ground.")])}
    {encounter("arena-4", "Fourth game arena", "assets/img/bng/arena-4.webp", "Layout of the fourth game arena", [
        ("Context", "Right after players receive their second weapon kit, the Electroplasm and the Hydrogel."),
        ("Goal", "Let players experiment and have fun with their new weapons. The challenge is intentionally moderate, prioritizing learning and player expression over high pressure."),
        ("Pacing", "The train stays stationary at one end while enemies attack in waves, controlled through the enemy counter and the AI Director."),
        ("Layout", "A bottleneck of narrow, aligned paths lets the Electroplasm's piercing (DPS) hit several enemies at once, while the Hydrogel pushes enemies toward the abyss, an environmental hazard that rewards positioning and weapon combination."),
        ("Outcome", "Reinforces the weapon combination mechanics in a safe, engaging space to understand the new loadout.")])}
"""
ld = dossier_head("04", "Level Design", "The level design of Bugs 'N' Guns: beat chart and level layout, arenas and encounters, and prototyping ideas for every part of the level, from puzzles to the game's final stage.") + SUBNAV + glance([
    ("Pipeline", "Objectives, beat chart, 2D layout, blockout and arenas"),
    ("Combat", "Designed all the combat and encounters in the game"),
    ("Layout", "2D layout for all the levels, from whiteboard to final map"),
    ("Production", "Reuse strategy to deliver varied gameplay with limited art resources")]) + dossier(ld_index, ld_main) + BNG_PAGER
write("bng-level-design.html", "Level Design · Bugs 'N' Guns — Álvaro Calvo García-Arias",
      "Level design of Bugs 'N' Guns: objectives, beat chart, 2D layout built for reuse, blockout, and the design of the first and fourth combat arenas.",
      "bng", "bng-level-design", ld, og="assets/img/thumbs/tICzsxpXogc.webp")

# ================================================================ BNG blinkball
bb_sheet = sheet([("Type", "Easter-egg minigame"), ("Mode", "1v1 soccer between the two players"), ("Access", "Hidden in the game, plus a build that loads it directly"), ("Made", "In my spare time")],
)
bb = dossier_head("05", "BlinkBall", "An easter-egg minigame: a 1v1 soccer match between the two players of Bugs 'N' Guns.",
                  btn("https://alvarocga.itch.io/blinkball", "Play on Itch.io", True, IMG_ITCH)) + SUBNAV + case_grid(bb_sheet, f"""
    {fig("assets/img/bng/card-blinkball.webp", "BlinkBall minigame")}
    <div class="prose" style="margin-top:24px">
      <p>This is a small minigame I created within the game as an easter egg during my brief downtime. It pits the two players of Bugs 'N' Guns against each other in a 1v1 soccer match.</p>
      <p>The main feature of the minigame is the somewhat exaggerated physics of the ball. It not only reacts to the players and the environment but also gains much more force when hit with the Blinkshot.</p>
      <p>There is a modified build of Bugs 'N' Guns that loads the minigame directly, available from the <a href="https://alvarocga.itch.io/blinkball" {EXT}>itch.io link</a>, though there are also hidden ways to access it within the game.</p>
    </div>
    <div style="margin-top:32px">{ph("BNG-BLINKBALL-VIDEO", "Optional: BlinkBall gameplay video (YouTube ID)")}</div>""", ruled=False) + BNG_PAGER
write("bng-blinkball.html", "BlinkBall · Bugs 'N' Guns — Álvaro Calvo García-Arias",
      "BlinkBall: a Rocket League-style 1v1 easter-egg minigame hidden inside Bugs 'N' Guns.",
      "bng", "bng-blinkball", bb)


# ================================================================ PERSONAL list
personal = f"""
<section class="wrap proj-head">
  <p class="eyebrow">Game jams &amp; experiments</p>
  <h1>Personal projects</h1>
  <p class="hero-lead">Apart from larger projects, I've also worked on smaller personal projects such as game jams and experimental prototypes.</p>
  <div class="actions">{btn("https://alvarocga.itch.io/", "All my games on Itch.io", False, IMG_ITCH)}</div>
</section>
<section class="wrap section" style="padding-top:12px">
  <div class="pp-grid">{''.join(pp_card(*p) for p in PERSONAL)}
  </div>
</section>
"""
write("personal-projects.html", "Personal Projects — Álvaro Calvo García-Arias",
      "Game jams and personal projects: You Are Nobody, Beat Found, Neon Red, Super Transform, Burger Bros Circus, Gea Of War and Against The Clock.",
      "personal", "personal", personal, og="assets/img/thumbs/NoE4qOLrqMI.webp")

# ================================================================ PERSONAL detail pages


def project(slug, name, vid, vthumb, eyebrow, lead, rows, links, about_extra, intro, items, desc, other=None):
    main = f"""{yt(vid, name + " — Trailer", vthumb)}
    <h2>About the game</h2>
    <div class="prose">{about_extra}</div>
    <h2>My contributions</h2>
    <p class="muted" style="margin-bottom:14px">{intro}</p>
    {numbered(items)}"""
    if other:
        main += f'<p class="note" style="margin-top:24px">{other}</p>'
    acts = "".join(btn(u, n, k == 0, IMG_ITCH if "itch.io" in u else None) for k, (n, u) in enumerate(links))
    body = case_head(f'<a href="personal-projects.html">Personal projects</a> · {eyebrow}', name, lead, acts) + case_grid(sheet(rows), main) + """
<section class="wrap section"><nav data-pager="personal" aria-label="More personal projects"></nav></section>
"""
    og = vthumb if vthumb else f"assets/img/thumbs/{vid}.webp"
    write(f"{slug}.html", f"{name} — Álvaro Calvo García-Arias", desc, "personal", slug, body, og=og)


project("neon-red", "Neon Red", "NoE4qOLrqMI", None, "Com JamOn · Mar 2024",
        "A platformer for speedrunners. Using the red line connecting your arm and hand, you'll need to use momentum and swings to reach the goal as quickly as possible. Defeat enemies and strive to improve your times.",
        [("Role", "Game Designer &amp; Programmer"), ("Context", "Com JamOn"), ("Team", "Blinkshot · 3 Game Designers"), ("Genre", "Platformer · Speedrun"),
         ("Platform", "PC"), ("Engine", "Unreal Engine 5"), ("Date", "14 — 17 Mar 2024")],
        [("Play on Itch.io", "https://alvarocga.itch.io/neonred")],
        "<p>Are you ready to cross the red line and enter Neon Red? I worked as Game Designer and Programmer on this game at the Com JamOn.</p>",
        "Designed and programmed (all in Blueprints) all the mechanics and systems, including, among others:",
        ["<strong>Player core mechanics</strong><ul><li>The movement and control mechanics of the player.</li><li>The grappling hook swing physics and mechanics.</li><li>The grappling hook retract physics and mechanics.</li></ul>",
         "<strong>Level interactables:</strong> design, programming and implementation of the level interactables (wall-run objects, death areas…).",
         "<strong>Level design:</strong> set the basic principles of the level design with the other designers and designed one of the levels of the game.",
         "<strong>Save system</strong> programming.",
         "<strong>Team support:</strong> helped the rest of the design team with Unreal Engine, GitHub and other tools."],
        "Neon Red, a speedrun platformer with grappling-hook swing physics made at the Com JamOn. Game Designer and Programmer.")

project("super-transform", "Super Transform", "pPfRK8eXA9U", None, "Madrid in Game Hack Jam · Jul 2023",
        "A first-person puzzle game, in the style of Superliminal and inspired by Zelda's Ultrahand, about transforming objects to make your way across the rooftops of a fractured Madrid that has been flooded and is under the vengeful attacks of the squids.",
        [("Role", "Game Designer &amp; Programmer"), ("Context", "Madrid in Game Hack Jam"), ("Team", "Blinkshot · 5 Game Designers"), ("Genre", "Puzzle"),
         ("Platform", "PC"), ("Engine", "Unreal Engine 5"), ("Date", "14 — 16 Jul 2023")],
        [("Play on Itch.io", "https://alvarocga.itch.io/super-transform")],
        "<p>You embody an interdimensional guard whose mission is to save Madrid. I worked as Game Designer and Programmer on this game at the Madrid in Game Hack Jam.</p>",
        "Designed and programmed (all in Blueprints) all the mechanics and systems, including, among others:",
        ["<strong>Player core mechanics</strong><ul><li>The movement and control mechanics of the player.</li><li>The movement, rotation and scale of interactable objects.</li></ul>",
         "<strong>Level interactables:</strong> design, programming and implementation.",
         "<strong>User interface:</strong> programming and implementation of the UI.",
         "<strong>Tools for the level designers</strong>, made to be quick and easy to work with because we only had 48 hours<ul><li>Custom triggers, easy for the level designer to modify and adapt to a variety of circumstances.</li><li>Interactables that are easy to place, with lots of editable variables to adapt to the level designer's work.</li></ul>",
         "<strong>Team support:</strong> helped the rest of the design team with Unreal Engine, GitHub and other tools."],
        "Super Transform, a first-person object-transforming puzzle game made at the Madrid in Game Hack Jam. Game Designer and Programmer.",
        other="During this project the beer was provided for free by the jam organization.")

project("burger-bros-circus", "Burger Bros Circus", "CI8AUE0d21w", None, "Global Game Jam · Jan 2024",
        "A 1 vs 1 multiplayer, dodgeball-style game where two gym bros must throw junk food at each other in a circus setting to make the audience laugh.",
        [("Role", "Game Designer &amp; Programmer"), ("Context", "Global Game Jam 2024"), ("Team", "Blinkshot · 4 Game Designers, 2 Artists, 1 Programmer"),
         ("Genre", "Twin-stick shooter"), ("Platform", "PC"), ("Engine", "Unreal Engine 5"), ("Date", "24 — 28 Jan 2024")],
        [("Play on Itch.io", "https://markelhxc.itch.io/burguer-bros-circus")],
        "<p>Made for the Global Game Jam 2024 with the theme “Make me laugh”, it's a hilarious and chaotic two-player experience. I worked as Game Designer and Programmer on this game.</p>",
        "Designed and programmed multiple mechanics and systems, including, among others:",
        ["<strong>The 3Cs:</strong> the camera, the controls and the character.",
         "<strong>Shooting mechanics</strong><ul><li>Design, programming and implementation of the two types of shooting.</li><li>Design, programming and implementation of the projectile trajectory preview.</li><li>Design, programming and implementation of the different types of ammo and level obstacles.</li></ul>",
         "<strong>User interface:</strong> programming and implementation of the UI.",
         "<strong>Team support:</strong> helped the rest of the design and art team with Unreal Engine, GitHub and other tools."],
        "Burger Bros Circus, a 1v1 dodgeball-style party game made at the Global Game Jam 2024. Game Designer and Programmer.")

project("gea-of-war", "Gea Of War", "SLGUOeP3ZOI", None, "Global Game Jam · Feb 2023",
        "A retro, arcade, 2D pixel-art shooter in which you control a demigoddess trying to keep the earth safe from contamination, managing both your own life and that of the earth by channeling the energy of nature through the roots of your bow.",
        [("Role", "Game Designer &amp; Programmer"), ("Context", "Global Game Jam 2023"), ("Team", "3 Game Designers, 2 Programmers"), ("Genre", "Action · Arcade"),
         ("Platform", "PC · Web"), ("Engine", "Godot"), ("Date", "3 — 5 Feb 2023")],
        [("Play on Itch.io", "https://alvarocga.itch.io/gea-of-war"), ("Play in browser", "https://dcrespo3d.github.io/GGJ2023/build_web/gea_of_war.html")],
        "<p>A frenetic game in which, through some simple mechanics and managing the resources presented, the player has to survive as long as possible to achieve the best score. I worked as Game Designer and Programmer on this game at the Global Game Jam 2023.</p>",
        "Designed and programmed (in GDScript, Godot's own language) most of the mechanics and systems, including, among others:",
        ["The general concept of the game.", "Enemy AI and spawn system: design and programming.", "User interface: design and programming.",
         "Score system: design and programming.", "Player mechanics design.", "Implementation of VFX and SFX."],
        "Gea Of War, a retro pixel-art arcade shooter made in Godot at the Global Game Jam 2023. Game Designer and Programmer.",
        other="It was the first videogame for most of the team.")

project("against-the-clock", "Against The Clock", "EYnCGiVuaXQ", None, "BSc solo project · 2021 — 2022",
        "A simple game where you have to collect all the hammers on the map and go through a portal before the clock hits 00:00.",
        [("Role", "Designer, Programmer &amp; Artist"), ("Context", "BSc Game Design &amp; Development"), ("Team", "Solo developer"), ("Genre", "Action"),
         ("Platform", "PC"), ("Engine", "Unreal Engine 4.27 · Maya, Substance, Audacity"), ("Date", "20 Nov 2021 — 5 May 2022")],
        [("Play on Itch.io", "https://alvarocga.itch.io/against-the-clokc")],
        "<p>This project was my first Unreal Engine game, inspired by Carlos Coronado's Unreal Engine 4 course, and a solo project for my BSc in Game Design and Development.</p>",
        "This project was fully developed by myself, so I was in charge of:",
        ["All the design.", "All the programming.", "All the art."],
        "Against The Clock, my first Unreal Engine game: a solo project for my BSc in Game Design and Development.",
        other="My first videogame in Unreal Engine.")

def gallery(imgs):
    cols = 2 if len(imgs) % 2 == 0 else 3
    return f'<div class="gallery cols-{cols}">' + "".join(f'<figure class="media"><img src="{src}" alt="{alt}" loading="lazy" decoding="async" class="zoomable"></figure>' for src, alt in imgs) + "</div>"


def itch_project(slug, name, eyebrow, lead, rows, itch, media, about, intro, items, desc, og):
    main = f"""{media}
    <h2>About the game</h2>
    <div class="prose">{about}</div>
    <h2>My contributions</h2>
    <p class="muted" style="margin-bottom:14px">{intro}</p>
    {numbered(items)}"""
    body = case_head(f'<a href="personal-projects.html">Personal projects</a> · {eyebrow}', name, lead,
                     btn(itch, "Play on Itch.io", True, IMG_ITCH)) + case_grid(sheet(rows), main) + """
<section class="wrap section"><nav data-pager="personal" aria-label="More personal projects"></nav></section>
"""
    write(f"{slug}.html", f"{name} — Álvaro Calvo García-Arias", desc, "personal", slug, body, og=og)


PEND = lambda pid: f'<span class="ph-inline">[{pid}] pending</span>'
itch_project("beat-found", "Beat Found", "Madrid in Game Hack Jam 6 · Nov 2024",
    "Get back on track! A 3D rhythm platformer where you recover all the Heart Beats to make Madrid beat again.",
    [("Role", "Game Designer &amp; Technical Designer"), ("Context", "Madrid in Game Hack Jam 6"), ("Team", "4 Game Designers"),
     ("Genre", "3D platformer · Rhythm · Exploration"), ("Platform", "Windows"), ("Engine", "Unreal Engine 5"),
     ("Status", "Prototype"), ("Date", "30 Nov — 1 Dec 2024")],
    "https://alvarocga.itch.io/beat-found",
    vimeo("1140096228", "Beat Found — Gameplay") + gallery([(f"assets/img/personal/beat-found-{i}.webp", f"Beat Found screenshot {i}") for i in range(1, 5)]),
    "<p>In a dystopian future, Madrid has lost the most important thing, its people. With them, its music, its color and its essence are forgotten.</p><p>Recover all the Heart Beats to make Madrid beat again.</p>",
    "I worked as Game Designer and Technical Designer. I designed and implemented, among others:",
    ["<strong>Color recovery system:</strong> designed and programmed the system that brings the city's color back, including the shaders, the collectibles and the system that activates the color when they are picked up.",
     "<strong>Player movement:</strong> designed and implemented the character's movement.",
     "<strong>Level progression:</strong> implemented the rewards and missions that move the player around the map.",
     "<strong>Interactables &amp; platforms:</strong> designed and implemented the game's interactables and platforms.",
     "<strong>Team support:</strong> helped the team with the development tools (Unreal Engine, GitHub and others)."],
    "Beat Found, a 3D rhythm platformer made at the Madrid in Game Hack Jam 6 (2024). Game Designer and Technical Designer.", "assets/img/personal/beat-found-cover.webp")

itch_project("you-are-nobody", "You Are Nobody", "Global Game Jam · Jan 2025",
    "A stealth game about infiltrating by stealing people's faces.",
    [("Role", "Game Designer &amp; Technical Designer"), ("Context", "Global Game Jam 2025"), ("Team", "Blinkshot · 3 Game Designers, 1 Artist, 1 Musician"),
     ("Genre", "Action · Stealth"), ("Platform", "Windows"), ("Engine", "Unreal Engine 5"), ("Status", "Released"), ("Date", "Jan 2025")],
    "https://alvarocga.itch.io/you-are-nobody",
    yt("sf2bG8XVwxU", "You Are Nobody — Trailer") + gallery([(f"assets/img/personal/you-are-nobody-{i}.webp", f"You Are Nobody screenshot {i}") for i in (1, 3, 4)]),
    "<p>You will infiltrate their concrete castles and rip them of their identity. Steal civilian faces with your camera and don't get caught by the guards.</p><p>Because remember, <em>you are nobody</em>.</p>",
    "I worked as Game Designer and Technical Designer. I designed and implemented, among others:",
    ["<strong>Core mechanic:</strong> using a camera to steal people's faces and transform into other characters, and the whole stealth system built around it.",
     "<strong>AI:</strong> the enemies' and the NPCs' AI.",
     "<strong>Team support:</strong> helped the team with the development tools (Unreal Engine, GitHub and others)."],
    "You Are Nobody, a stealth game about stealing faces with a camera, made at the Global Game Jam 2025. Game Designer and Technical Designer.", "assets/img/thumbs/sf2bG8XVwxU.webp")

# ================================================================ CONTACT
contact = f"""
<section class="wrap proj-head">
  <p class="eyebrow">Contact</p>
  <h1>Get in touch</h1>
  <p class="hero-lead">Whether it's a role, a collaboration or just to chat about game design, drop me a line.</p>
  <div class="actions"><a class="btn btn-accent" href="mailto:Calvoalvaro13@gmail.com">Calvoalvaro13@gmail.com</a><a class="btn" href="assets/docs/Alvaro-Calvo-Garcia-Arias-CV.pdf" target="_blank" rel="noopener">Download CV</a></div>
</section>
<section class="wrap section">
  <div class="contact-list">
    <a class="contact-item" href="https://www.linkedin.com/in/alvarocga/" {EXT}>{I_LINKEDIN}<div><small>LinkedIn</small><span>alvarocga</span></div></a>
    <a class="contact-item" href="https://alvarocga.itch.io/" {EXT}>{I_ITCH}<div><small>Itch.io</small><span>alvarocga</span></div></a>
    <a class="contact-item" href="https://twitter.com/calvoalvaro12" {EXT}>{I_X}<div><small>X / Twitter</small><span>@calvoalvaro12</span></div></a>
    <div class="contact-item">{I_PIN}<div><small>Location</small><span>Madrid, Spain</span></div></div>
  </div>
</section>
"""
write("contact.html", "Contact — Álvaro Calvo García-Arias",
      "Get in touch with Álvaro Calvo García-Arias, Technical Game Designer based in Madrid, Spain.",
      "contact", "contact", contact)

# ================================================================ 404
nf = """
<section class="wrap proj-head">
  <p class="eyebrow">404</p>
  <h1>Level not found.</h1>
  <p class="hero-lead">This page doesn't exist or has moved.</p>
  <div class="actions"><a class="btn btn-accent" href="index.html">Back to the portfolio</a></div>
</section>
"""
write("404.html", "Page not found — Álvaro Calvo García-Arias", "Page not found.", "", "404", nf)
# 404 is served from any path on GitHub Pages: make its URLs root-absolute.
p404 = os.path.join(ROOT, "404.html")
t = open(p404, encoding="utf-8").read()
for a in ('href="css/', 'src="js/', 'href="assets/', 'content="assets/', 'href="index.html', 'href="bugs-n-guns.html', 'href="personal-projects.html', 'href="contact.html'):
    t = t.replace(a, a.replace('"', '"/', 1))
open(p404, "w", encoding="utf-8").write(t)

# ================================================================ VIDEO REVIEW (hidden, noindex)
VIMEO = [
    ("Beat Found", [("1140085082", "Beatfound Preview", "Blinkshot", 53, "new"), ("1140096228", "Beat_Found", "Markel (personal)", 70, "new")]),
    ("Bugs 'N' Guns", [("879716354", "Launch trailer", "Blinkshot", 100, "YouTube version already on the site"),
                       ("879760611", "Gameplay Trailer", "Blinkshot", 198, "YouTube version already on the site"),
                       ("879765585", "Enemies", "Blinkshot", 17, "new"), ("879767462", "Players", "Blinkshot", 27, "new"),
                       ("879794012", "Cinematics", "Blinkshot", 34, "new"), ("879808236", "Electro Door", "Blinkshot", 8, "new"),
                       ("879808705", "Light plant", "Blinkshot", 8, "new"), ("848917499", "2D to 3D to Art", "Markel (personal)", 29, "new"),
                       ("848917584", "BugsNGuns_FP_02", "Markel (personal)", 81, "new"), ("848937018", "Blocking vertical slice level", "Markel (personal)", 41, "new"),
                       ("848952334", "TFM_Grupo1 Preview", "Markel (personal)", 5, "new")]),
    ("Macbeth", [("921771579", "Macbeth: Seeds of Fate - Announce trailer", "Blinkshot", 86, "new (the site uses other videos)")]),
    ("Personal projects", [("848914254", "Super Transform - Launch Trailer", "Markel (personal)", 60, "YouTube version already on the site"),
                           ("907927703", "Burguer Bros Circus", "Blinkshot", 33, "YouTube trailer already on the site"),
                           ("925678333", "Neon Red - Trailer", "Blinkshot", 59, "YouTube version already on the site"),
                           ("848943216", "GGJ 2023 capture", "Markel (personal)", 113, "new")]),
    ("Other (project unknown)", [("1140069645", "Metroidvania Test", "Blinkshot", 74, "new"), ("1140095331", "Puzzle Test", "Markel (personal)", 360, "new")]),
]
groups = ""
for g, vids in VIMEO:
    cards = "".join(f"""
      <figure class="vcard">
        <div class="vframe"><iframe src="https://player.vimeo.com/video/{vid}?dnt=1&amp;title=0&amp;byline=0&amp;portrait=0" loading="lazy" title="{html.escape(t)}" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></div>
        <figcaption><strong>{html.escape(t)}</strong><span>{acc} · {secs // 60}:{secs % 60:02d} · <code>vimeo {vid}</code></span><em class="{'is-new' if st.startswith('new') else ''}">{st}</em></figcaption>
      </figure>""" for vid, t, acc, secs, st in vids)
    groups += f'<section class="wrap section"><p class="section-label">{g}</p><div class="vgrid">{cards}</div></section>'

review = f"""
<section class="wrap proj-head">
  <p class="eyebrow">Internal · not linked from the menu</p>
  <h1>Video review</h1>
  <p class="hero-lead">Vimeo videos found on markelcuena.com, to decide which ones to use in the portfolio. If a player shows “Because of its privacy settings, this video cannot be played here”, that video is restricted to other domains.</p>
</section>
{groups}
<style>
.vgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px}}
.vcard{{background:var(--s1);border:1px solid var(--line)}}
.vframe{{position:relative;aspect-ratio:16/9;background:#000}}.vframe iframe{{position:absolute;inset:0;width:100%;height:100%;border:0}}
.vcard figcaption{{padding:14px 16px;display:grid;gap:4px}}.vcard strong{{font-weight:600}}
.vcard span{{font-size:.8rem;color:var(--muted)}}.vcard code{{font-family:var(--mono);font-size:.75rem}}
.vcard em{{font-style:normal;font-size:.75rem;color:var(--muted)}}.vcard em.is-new{{color:var(--accent)}}
</style>
"""
write("video-review.html", "Video review — internal", "Internal page to review candidate videos.", "", "video-review", review)
_p = os.path.join(ROOT, "video-review.html")
_t = open(_p, encoding="utf-8").read().replace('<meta name="viewport"', '<meta name="robots" content="noindex, nofollow">\n<meta name="viewport"', 1)
open(_p, "w", encoding="utf-8").write(_t)

# ================================================================ VIDEO REVIEW (hidden, noindex)
# Blinkshot account videos plus Bugs 'N' Guns videos from a teammate's account.
VIMEO = [
    ("Beat Found", [("1140085082", "Beatfound Preview", "Blinkshot", 53, "new"), ("1140096228", "Beat_Found", "Markel Cuena", 70, "new")]),
    ("Bugs 'N' Guns", [("879716354", "Launch trailer", "Blinkshot", 100, "YouTube version already on the site"),
                       ("879760611", "Gameplay Trailer", "Blinkshot", 198, "YouTube version already on the site"),
                       ("879765585", "Enemies", "Blinkshot", 17, "new"), ("879767462", "Players", "Blinkshot", 27, "new"),
                       ("879794012", "Cinematics", "Blinkshot", 34, "new"), ("879808236", "Electro Door", "Blinkshot", 8, "new"),
                       ("879808705", "Light plant", "Blinkshot", 8, "new"), ("848917499", "2D to 3D to Art", "Markel Cuena", 29, "new"),
                       ("848917584", "BugsNGuns_FP_02", "Markel Cuena", 81, "new"), ("848937018", "Blocking vertical slice level", "Markel Cuena", 41, "new"),
                       ("848952334", "TFM_Grupo1 Preview", "Markel Cuena", 5, "new")]),
    ("Macbeth", [("921771579", "Macbeth: Seeds of Fate - Announce trailer", "Blinkshot", 86, "new (the site uses other videos)")]),
    ("Personal projects", [("907927703", "Burguer Bros Circus", "Blinkshot", 33, "YouTube trailer already on the site"),
                           ("925678333", "Neon Red - Trailer", "Blinkshot", 59, "YouTube version already on the site")]),
    ("Other", [("1140069645", "Metroidvania Test", "Blinkshot", 74, "new")]),
]
groups = ""
for g, vids in VIMEO:
    cards = "".join(f"""
      <figure class="vcard">
        <div class="vframe"><iframe src="https://player.vimeo.com/video/{vid}?dnt=1&amp;title=0&amp;byline=0&amp;portrait=0" loading="lazy" title="{html.escape(t)}" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></div>
        <figcaption><strong>{html.escape(t)}</strong><span>{acc} · {secs // 60}:{secs % 60:02d} · <code>vimeo {vid}</code></span><em class="{'is-new' if st.startswith('new') else ''}">{st}</em></figcaption>
      </figure>""" for vid, t, acc, secs, st in vids)
    groups += f'<section class="wrap section"><p class="section-label">{g}</p><div class="vgrid">{cards}</div></section>'

review = f"""
<section class="wrap proj-head">
  <p class="eyebrow">Internal · not linked from the menu</p>
  <h1>Video review</h1>
  <p class="hero-lead">Vimeo videos from the Blinkshot account and Bugs 'N' Guns clips, to decide which ones to use. If a player shows “Because of its privacy settings, this video cannot be played here”, that video is restricted to other domains.</p>
</section>
{groups}
<style>
.vgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:20px}}
.vcard{{background:var(--s1);border:1px solid var(--line)}}
.vframe{{position:relative;aspect-ratio:16/9;background:#000}}.vframe iframe{{position:absolute;inset:0;width:100%;height:100%;border:0}}
.vcard figcaption{{padding:14px 16px;display:grid;gap:4px}}.vcard strong{{font-weight:600}}
.vcard span{{font-size:.8rem;color:var(--muted)}}.vcard code{{font-family:var(--mono);font-size:.75rem}}
.vcard em{{font-style:normal;font-size:.75rem;color:var(--muted)}}.vcard em.is-new{{color:var(--accent)}}
</style>
"""
write("video-review.html", "Video review — internal", "Internal page to review candidate videos.", "", "video-review", review)
_p = os.path.join(ROOT, "video-review.html")
_t = open(_p, encoding="utf-8").read().replace('<meta name="viewport"', '<meta name="robots" content="noindex, nofollow">\n<meta name="viewport"', 1)
open(_p, "w", encoding="utf-8").write(_t)
