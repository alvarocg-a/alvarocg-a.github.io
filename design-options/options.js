/* Shared behaviour for the design prototypes: menu toggle, header state, lazy YouTube. */
(function () {
  var b = document.body, btn = document.querySelector("[data-menu]");
  if (btn) {
    btn.addEventListener("click", function () {
      var open = b.classList.toggle("menu-open");
      btn.setAttribute("aria-expanded", String(open));
    });
    document.querySelectorAll("#menu a").forEach(function (a) {
      a.addEventListener("click", function () { b.classList.remove("menu-open"); btn.setAttribute("aria-expanded", "false"); });
    });
  }
  function onScroll() { b.classList.toggle("scrolled", window.scrollY > 24); }
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  var PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>';
  document.querySelectorAll("[data-yt]").forEach(function (el) {
    var id = el.getAttribute("data-yt"), t = el.getAttribute("data-title") || "Video";
    el.innerHTML = '<img src="../../assets/img/thumbs/' + id + '.webp" alt="" loading="lazy">' +
      '<button class="yt-btn" type="button" aria-label="Play: ' + t.replace(/"/g, "&quot;") + '"><span>' + PLAY + ' Play</span></button>';
    el.querySelector(".yt-btn").addEventListener("click", function () {
      el.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0" title="' + t.replace(/"/g, "&quot;") +
        '" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
    });
  });
})();
