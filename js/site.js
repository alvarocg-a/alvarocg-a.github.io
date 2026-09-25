/* Shared header, footer, navigation and small interactions.
   Every page sets <body data-section="…" data-page="…">; the menu below is the
   single source of truth, so adding a page only means adding an entry here. */
(function () {
  "use strict";

  var NAV = [
    { id: "portfolio", label: "Portfolio", href: "index.html#work", children: [
      { id: "winx", label: "Winx Club", href: "winx.html" },
      { id: "macbeth", label: "Macbeth", href: "macbeth.html" },
      { id: "bng", label: "Bugs 'N' Guns", href: "bugs-n-guns.html" }
    ] },
    { id: "bng", label: "Bugs 'N' Guns", href: "bugs-n-guns.html", children: [
      { id: "bng", label: "Overview", href: "bugs-n-guns.html" },
      { id: "bng-game-design", label: "Game Design", href: "bng-game-design.html" },
      { id: "bng-prototyping", label: "Prototyping", href: "bng-prototyping.html" },
      { id: "bng-tools", label: "Tools 'N' Tech", href: "bng-tools.html" },
      { id: "bng-level-design", label: "Level Design", href: "bng-level-design.html" },
      { id: "bng-blinkball", label: "BlinkBall", href: "bng-blinkball.html" }
    ] },
    { id: "personal", label: "Personal Projects", href: "personal-projects.html", children: [
      { id: "neon-red", label: "Neon Red", href: "neon-red.html" },
      { id: "super-transform", label: "Super Transform", href: "super-transform.html" },
      { id: "burger-bros-circus", label: "Burger Bros Circus", href: "burger-bros-circus.html" },
      { id: "gea-of-war", label: "Gea Of War", href: "gea-of-war.html" },
      { id: "against-the-clock", label: "Against The Clock", href: "against-the-clock.html" }
    ] },
    { id: "contact", label: "Contact", href: "contact.html" }
  ];

  var ICON = {
    chevron: '<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M2 4.5 6 8l4-3.5"/></svg>',
    arrow: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4"/></svg>',
    arrowLeft: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M13 8H3M7 4 3 8l4 4"/></svg>',
    play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>',
    close: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="m3 3 10 10M13 3 3 13"/></svg>'
  };

  var body = document.body;
  var section = body.getAttribute("data-section") || "";
  var page = body.getAttribute("data-page") || "";
  document.documentElement.classList.add("js");

  /* ---------- Header ---------- */
  function renderHeader() {
    var mount = document.getElementById("site-header");
    if (!mount) return;
    var items = NAV.map(function (item, i) {
      var active = item.id === section ? " is-active" : "";
      var html = '<li class="nav-item' + (item.children ? " has-sub" : "") + active + '">' +
        '<a class="nav-link" href="' + item.href + '">' + item.label + "</a>";
      if (item.children) {
        html += '<button class="sub-toggle" type="button" aria-expanded="false" aria-controls="sub-' + i + '" aria-label="Show ' + item.label + ' pages">' + ICON.chevron + "</button>" +
          '<ul class="sub" id="sub-' + i + '">' + item.children.map(function (c) {
            return '<li><a href="' + c.href + '"' + (c.id === page ? ' aria-current="page"' : "") + ">" + c.label + "</a></li>";
          }).join("") + "</ul>";
      }
      return html + "</li>";
    }).join("");

    mount.innerHTML =
      '<a class="skip" href="#main">Skip to content</a>' +
      '<header class="site-header"><div class="wrap header-inner">' +
      '<a class="brand" href="index.html" aria-label="Álvaro Calvo García-Arias — home">' +
      '<span class="brand-name">Álvaro Calvo</span><span class="brand-role">Technical Game Designer</span></a>' +
      '<nav class="nav" id="site-nav" aria-label="Main"><ul class="nav-list">' + items + "</ul></nav>" +
      '<button class="burger" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu"><span></span><span></span><span></span></button>' +
      "</div></header>";

    var header = mount.querySelector(".site-header");
    var nav = mount.querySelector(".nav");
    var burger = mount.querySelector(".burger");

    function setMenu(open) {
      nav.classList.toggle("is-open", open);
      burger.setAttribute("aria-expanded", String(open));
      burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      body.classList.toggle("nav-open", open);
    }
    burger.addEventListener("click", function () { setMenu(!nav.classList.contains("is-open")); });

    mount.querySelectorAll(".sub-toggle").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var li = btn.parentElement;
        var open = !li.classList.contains("is-open");
        mount.querySelectorAll(".nav-item.is-open").forEach(function (o) {
          if (o !== li) { o.classList.remove("is-open"); o.querySelector(".sub-toggle").setAttribute("aria-expanded", "false"); }
        });
        li.classList.toggle("is-open", open);
        btn.setAttribute("aria-expanded", String(open));
      });
    });

    // On mobile, open the current section's submenu by default.
    if (window.matchMedia("(max-width: 900px)").matches) {
      var current = mount.querySelector(".nav-item.is-active.has-sub");
      if (current) { current.classList.add("is-open"); current.querySelector(".sub-toggle").setAttribute("aria-expanded", "true"); }
    }

    nav.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      setMenu(false);
      mount.querySelectorAll(".nav-item.is-open").forEach(function (o) { o.classList.remove("is-open"); });
    });
    document.addEventListener("click", function (e) {
      if (!e.target.closest(".nav-item") && window.matchMedia("(min-width: 901px)").matches) {
        mount.querySelectorAll(".nav-item.is-open").forEach(function (o) { o.classList.remove("is-open"); });
      }
    });
    window.addEventListener("resize", function () { if (window.innerWidth > 900) setMenu(false); });

    function onScroll() { header.classList.toggle("is-scrolled", window.scrollY > 8); }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Bugs 'N' Guns sub-navigation and prev/next ---------- */
  function renderSubnav() {
    var bng = NAV[1].children;
    var sub = document.querySelector("[data-subnav]");
    if (sub) {
      sub.className = "subnav";
      sub.setAttribute("aria-label", "Bugs 'N' Guns sections");
      sub.innerHTML = '<div class="wrap"><div class="subnav-list">' + bng.map(function (c) {
        return '<a href="' + c.href + '"' + (c.id === page ? ' aria-current="page"' : "") + ">" + c.label + "</a>";
      }).join("") + "</div></div>";
      var cur = sub.querySelector('[aria-current="page"]');
      if (cur) {
        var list = sub.querySelector(".subnav-list");
        list.scrollLeft += cur.getBoundingClientRect().left - list.getBoundingClientRect().left - 56;
      }
    }

    var pager = document.querySelector("[data-pager]");
    if (pager) {
      var group = NAV.filter(function (n) { return n.id === pager.getAttribute("data-pager"); })[0];
      var list = group ? group.children : [];
      var idx = list.map(function (c) { return c.id; }).indexOf(page);
      if (idx === -1) return;
      var prev = list[idx - 1], next = list[idx + 1];
      pager.className = "pager";
      pager.innerHTML =
        (prev ? '<a class="prev" href="' + prev.href + '"><small>Previous</small><span>' + prev.label + "</span></a>" : "") +
        (next ? '<a class="next" href="' + next.href + '"><small>Next</small><span>' + next.label + "</span></a>" : "");
    }
  }

  /* ---------- Footer ---------- */
  function renderFooter() {
    var mount = document.getElementById("site-footer");
    if (!mount) return;
    mount.innerHTML =
      '<footer class="site-footer"><div class="wrap footer-inner">' +
      "<p>© " + new Date().getFullYear() + " Álvaro Calvo García-Arias · Technical Game Designer · Madrid, Spain</p>" +
      '<div class="footer-links">' +
      '<a href="https://www.linkedin.com/in/alvarocga/" target="_blank" rel="noopener">LinkedIn</a>' +
      '<a href="https://alvarocga.itch.io/" target="_blank" rel="noopener">Itch.io</a>' +
      '<a href="https://twitter.com/calvoalvaro12" target="_blank" rel="noopener">X / Twitter</a>' +
      '<a href="mailto:Calvoalvaro13@gmail.com">Email</a>' +
      "</div></div></footer>";
  }

  /* ---------- YouTube: thumbnail first, iframe on click ---------- */
  function initVideos() {
    document.querySelectorAll(".yt[data-yt]").forEach(function (el) {
      var id = el.getAttribute("data-yt");
      var title = el.getAttribute("data-title") || "Video";
      var thumb = el.getAttribute("data-thumb") || ("assets/img/thumbs/" + id + ".webp");
      el.innerHTML =
        '<img src="' + thumb + '" alt="" loading="lazy" decoding="async">' +
        '<button class="yt-play" type="button" aria-label="Play video: ' + title.replace(/"/g, "&quot;") + '"><span>' + ICON.play + "</span></button>" +
        (el.hasAttribute("data-show-title") ? '<span class="yt-title">' + title + "</span>" : "");
      var img = el.querySelector("img");
      img.addEventListener("error", function () { img.src = "https://i.ytimg.com/vi/" + id + "/hqdefault.jpg"; }, { once: true });
      el.querySelector(".yt-play").addEventListener("click", function () {
        var f = document.createElement("iframe");
        f.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0&modestbranding=1";
        f.title = title;
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
    var big = box.querySelector("img");
    var closeBtn = box.querySelector(".lightbox-close");
    var lastFocus = null;

    function close() { box.classList.remove("is-open"); body.style.overflow = ""; if (lastFocus) lastFocus.focus(); }
    imgs.forEach(function (img) {
      img.setAttribute("tabindex", "0");
      img.setAttribute("role", "button");
      function open() {
        lastFocus = img;
        big.src = img.currentSrc || img.src;
        big.alt = img.alt;
        box.classList.add("is-open");
        body.style.overflow = "hidden";
        closeBtn.focus();
      }
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
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    els.forEach(function (e) { io.observe(e); });
  }

  /* Arrow icons for .link-arrow / .back-link placeholders */
  function initIcons() {
    document.querySelectorAll(".link-arrow:not(.has-icon)").forEach(function (a) { a.insertAdjacentHTML("beforeend", ICON.arrow); a.classList.add("has-icon"); });
    document.querySelectorAll(".back-link:not(.has-icon)").forEach(function (a) { a.insertAdjacentHTML("afterbegin", ICON.arrowLeft); a.classList.add("has-icon"); });
  }

  renderHeader();
  renderSubnav();
  renderFooter();
  initIcons();
  initVideos();
  initLightbox();
  initReveal();
})();
