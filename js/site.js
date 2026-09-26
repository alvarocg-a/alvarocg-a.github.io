/* Shared header, footer, section navigation and small interactions.
   Each page sets <body data-section="…" data-page="…"> (and data-header="over"
   when the header floats over a full-bleed image). The arrays below are the
   single source of truth for menus and prev/next links. */
(function () {
  "use strict";

  var MENU = [
    { id: "work", label: "Work", href: "index.html#work" },
    { id: "bng", label: "Bugs 'N' Guns", href: "bugs-n-guns.html" },
    { id: "personal", label: "Personal", href: "personal-projects.html" },
    { id: "about", label: "About", href: "index.html#about" }
  ];

  var GROUPS = {
    work: [
      { id: "winx", label: "Winx Club", href: "winx.html" },
      { id: "macbeth", label: "Macbeth", href: "macbeth.html" },
      { id: "bng", label: "Bugs 'N' Guns", href: "bugs-n-guns.html" }
    ],
    bng: [
      { id: "bng", label: "Overview", href: "bugs-n-guns.html" },
      { id: "bng-game-design", label: "Game Design", href: "bng-game-design.html" },
      { id: "bng-prototyping", label: "Prototyping", href: "bng-prototyping.html" },
      { id: "bng-tools", label: "Tools 'N' Tech", href: "bng-tools.html" },
      { id: "bng-level-design", label: "Level Design", href: "bng-level-design.html" },
      { id: "bng-blinkball", label: "BlinkBall", href: "bng-blinkball.html" }
    ],
    personal: [
      { id: "neon-red", label: "Neon Red", href: "neon-red.html" },
      { id: "super-transform", label: "Super Transform", href: "super-transform.html" },
      { id: "burger-bros-circus", label: "Burger Bros Circus", href: "burger-bros-circus.html" },
      { id: "gea-of-war", label: "Gea Of War", href: "gea-of-war.html" },
      { id: "against-the-clock", label: "Against The Clock", href: "against-the-clock.html" },
      { id: "beat-found", label: "Beat Found", href: "beat-found.html" },
      { id: "you-are-nobody", label: "You Are Nobody", href: "you-are-nobody.html" }
    ]
  };

  var SOCIAL = [
    { label: "LinkedIn", href: "https://www.linkedin.com/in/alvarocga/" },
    { label: "Itch.io", href: "https://alvarocga.itch.io/" },
    { label: "X / Twitter", href: "https://twitter.com/calvoalvaro12" }
  ];
  var MAIL = "Calvoalvaro13@gmail.com";

  var ICON = {
    arrow: '<svg class="ic" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg>',
    play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>',
    close: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m3 3 10 10M13 3 3 13"/></svg>'
  };

  var body = document.body;
  var section = body.getAttribute("data-section") || "";
  var page = body.getAttribute("data-page") || "";
  document.documentElement.classList.add("js");

  /* ---------- Header ---------- */
  function renderHeader() {
    var mount = document.getElementById("site-header");
    if (!mount) return;
    var links = MENU.map(function (m) {
      return '<a href="' + m.href + '"' + (m.id === section ? ' aria-current="page"' : "") + ">" + m.label + "</a>";
    }).join("") + '<a class="menu-cta" href="contact.html"' + (section === "contact" ? ' aria-current="page"' : "") + ">Contact</a>";

    mount.innerHTML =
      '<a class="skip" href="#main">Skip to content</a>' +
      '<header class="hdr"><div class="wrap hdr-in">' +
      '<a class="logo" href="index.html" aria-label="Álvaro Calvo García-Arias, home">Álvaro Calvo</a>' +
      '<nav class="menu" id="menu" aria-label="Main">' + links + "</nav>" +
      '<button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu" aria-label="Open menu"><span></span><span></span></button>' +
      "</div></header>";

    var btn = mount.querySelector(".menu-btn");
    function setMenu(open) {
      body.classList.toggle("nav-open", open);
      btn.setAttribute("aria-expanded", String(open));
      btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    }
    btn.addEventListener("click", function () { setMenu(!body.classList.contains("nav-open")); });
    mount.querySelectorAll(".menu a").forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
    window.addEventListener("resize", function () { if (window.innerWidth > 820) setMenu(false); });

    function onScroll() { body.classList.toggle("scrolled", window.scrollY > 24); }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Section tabs and prev/next ---------- */
  function renderSectionNav() {
    var sub = document.querySelector("[data-subnav]");
    if (sub) {
      var list = GROUPS[sub.getAttribute("data-subnav")] || [];
      sub.className = "subnav";
      sub.innerHTML = '<div class="wrap"><div class="subnav-list">' + list.map(function (c) {
        return '<a href="' + c.href + '"' + (c.id === page ? ' aria-current="page"' : "") + ">" + c.label + "</a>";
      }).join("") + "</div></div>";
      var cur = sub.querySelector('[aria-current="page"]');
      if (cur) {
        var row = sub.querySelector(".subnav-list");
        var anchor = cur.previousElementSibling || cur; // keep the previous tab fully visible
        row.scrollLeft += anchor.getBoundingClientRect().left - row.getBoundingClientRect().left;
      }
    }

    document.querySelectorAll("[data-pager]").forEach(function (pager) {
      var items = GROUPS[pager.getAttribute("data-pager")] || [];
      var idx = items.map(function (c) { return c.id; }).indexOf(page);
      if (idx === -1) return;
      var prev = items[idx - 1], next = items[idx + 1];
      pager.className = "pager";
      pager.innerHTML =
        (prev ? '<a class="prev" href="' + prev.href + '"><small>Previous</small><span>' + prev.label + "</span></a>" : "") +
        (next ? '<a class="next" href="' + next.href + '"><small>Next</small><span>' + next.label + "</span></a>" : "");
    });
  }

  /* ---------- Footer: contact block on every page ---------- */
  function renderFooter() {
    var mount = document.getElementById("site-footer");
    if (!mount) return;
    mount.innerHTML =
      '<footer class="ftr" id="contact"><div class="wrap">' +
      '<p class="eyebrow">Contact</p>' +
      "<h2>Let's build<br>something fun.</h2>" +
      '<p class="ftr-sub">Open to Technical Game Design and Combat Design roles.</p>' +
      '<div class="ftr-row"><a class="btn btn-accent" href="mailto:' + MAIL + '">' + MAIL + "</a>" +
      '<div class="ftr-soc">' + SOCIAL.map(function (s) { return '<a href="' + s.href + '" target="_blank" rel="noopener">' + s.label + "</a>"; }).join("") + "</div></div>" +
      '<p class="ftr-copy">© ' + new Date().getFullYear() + " Álvaro Calvo García-Arias · Technical Game Designer · Madrid, Spain</p>" +
      "</div></footer>";
  }

  /* ---------- YouTube: thumbnail first, iframe on click ---------- */
  function initVideos() {
    document.querySelectorAll(".yt[data-yt]").forEach(function (el) {
      var id = el.getAttribute("data-yt");
      var title = (el.getAttribute("data-title") || "Video").replace(/"/g, "&quot;");
      var thumb = el.getAttribute("data-thumb") || ("assets/img/thumbs/" + id + ".webp");
      el.innerHTML = '<img src="' + thumb + '" alt="" loading="lazy" decoding="async">' +
        '<button class="yt-play" type="button" aria-label="Play video: ' + title + '"><span>' + ICON.play + "</span></button>";
      var img = el.querySelector("img");
      img.addEventListener("error", function () { img.src = "https://i.ytimg.com/vi/" + id + "/hqdefault.jpg"; }, { once: true });
      el.querySelector(".yt-play").addEventListener("click", function () {
        var f = document.createElement("iframe");
        f.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0&modestbranding=1";
        f.title = el.getAttribute("data-title") || "Video";
        f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
        f.allowFullscreen = true;
        el.innerHTML = "";
        el.appendChild(f);
      });
    });
  }

  /* ---------- Lightbox for documentation images ---------- */
  function initLightbox() {
    var imgs = document.querySelectorAll("img.zoomable");
    if (!imgs.length) return;
    var box = document.createElement("div");
    box.className = "lightbox";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", "Image viewer");
    box.innerHTML = '<img alt=""><button class="lightbox-close" type="button" aria-label="Close">' + ICON.close + "</button>";
    body.appendChild(box);
    var big = box.querySelector("img"), closeBtn = box.querySelector(".lightbox-close"), last = null;
    function close() { box.classList.remove("is-open"); body.style.overflow = ""; if (last) last.focus(); }
    imgs.forEach(function (img) {
      img.setAttribute("tabindex", "0");
      img.setAttribute("role", "button");
      function open() { last = img; big.src = img.currentSrc || img.src; big.alt = img.alt; box.classList.add("is-open"); body.style.overflow = "hidden"; closeBtn.focus(); }
      img.addEventListener("click", open);
      img.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } });
    });
    box.addEventListener("click", close);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && box.classList.contains("is-open")) close(); });
  }

  /* ---------- Reveal on scroll ---------- */
  function initReveal() {
    var els = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window)) { els.forEach(function (e) { e.classList.add("is-visible"); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("is-visible"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    els.forEach(function (e) { io.observe(e); });
  }

  function initIcons() {
    document.querySelectorAll(".link-arrow:not(.has-icon)").forEach(function (a) { a.insertAdjacentHTML("beforeend", ICON.arrow); a.classList.add("has-icon"); });
  }

  /* ---------- Side index: highlight the section in view ---------- */
  function initScrollSpy() {
    var links = [].slice.call(document.querySelectorAll(".toc-side a[href^='#']"));
    if (!links.length || !("IntersectionObserver" in window)) return;
    var targets = links.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
    function update() {
      var line = window.innerHeight * 0.3, current = 0;
      targets.forEach(function (t, i) { if (t && t.getBoundingClientRect().top < line) current = i; });
      links.forEach(function (a, i) { a.classList.toggle("is-active", i === current); });
    }
    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  /* ---------- Sticky sheets only when they fit in the viewport ---------- */
  function initSheets() {
    var sheets = document.querySelectorAll(".sheet");
    if (!sheets.length) return;
    function fit() {
      sheets.forEach(function (el) {
        el.classList.remove("no-stick");
        var top = parseFloat(getComputedStyle(el).top) || 0;
        if (el.offsetHeight + top + 24 > window.innerHeight) el.classList.add("no-stick");
      });
    }
    window.addEventListener("resize", fit);
    window.addEventListener("load", fit);
    fit();
  }

  renderHeader();
  renderSectionNav();
  renderFooter();
  initIcons();
  initVideos();
  initLightbox();
  initReveal();
  initScrollSpy();
  initSheets();
})();
