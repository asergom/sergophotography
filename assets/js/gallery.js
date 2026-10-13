/* SerGo Photography — gallery behaviour (no dependencies) */
(function () {
  "use strict";

  var tiles = Array.prototype.slice.call(document.querySelectorAll(".tile a"));

  /* Fade each thumbnail in once it has loaded */
  tiles.forEach(function (a) {
    var img = a.querySelector("img");
    var done = function () { a.parentNode.classList.add("loaded"); };
    if (img.complete && img.naturalWidth) done();
    else {
      img.addEventListener("load", done, { once: true });
      img.addEventListener("error", done, { once: true });
    }
  });

  var dlg = document.querySelector(".lb");
  if (!dlg || !tiles.length || typeof dlg.showModal !== "function") return;

  var stage = dlg.querySelector(".lb-stage");
  var img = dlg.querySelector(".lb-img");
  var bar = dlg.querySelector(".lb-bar");
  var countEl = dlg.querySelector(".lb-count");
  var exifEl = dlg.querySelector(".lb-exif");
  var rawBtn = dlg.querySelector(".lb-raw");
  var fullLink = dlg.querySelector(".lb-full");
  var root = document.documentElement;

  var index = -1;
  var showRaw = false;
  var pushedHistory = false;
  var closingFromHistory = false;
  var token = 0;
  var preloads = {};

  function measureBar() {
    dlg.style.setProperty("--bar-h", bar.offsetHeight + "px");
  }

  /* CSS width the photo will occupy, so the browser picks the right file */
  function sizesFor(w, h) {
    var sw = stage.clientWidth || window.innerWidth;
    var sh = stage.clientHeight || window.innerHeight;
    var cs = getComputedStyle(stage);
    sw -= parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
    sh -= parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);
    return Math.max(1, Math.ceil(Math.min(sw, sh * (w / h)))) + "px";
  }

  function sourceFor(a, raw) {
    var d = a.dataset;
    if (raw && d.rawSrcset) return { set: d.rawSrcset, w: +d.rawW, h: +d.rawH };
    return { set: d.srcset, w: +d.w, h: +d.h };
  }

  function load(src, cb) {
    var im = new Image();
    im.decoding = "async";
    im.sizes = sizesFor(src.w, src.h);
    im.srcset = src.set;
    if (cb) {
      im.onload = function () { cb(im.currentSrc || im.src); };
      im.onerror = function () { cb(null); };
    }
    return im;
  }

  function preload(i) {
    var a = tiles[(i + tiles.length) % tiles.length];
    if (!preloads[a.id]) preloads[a.id] = load(sourceFor(a, false));
  }

  function exifText(d) {
    return [d.camera, d.exposure, d.aperture, d.focal, d.iso ? "ISO " + d.iso : ""]
      .filter(Boolean).join("  ·  ");
  }

  function render(i, keepImage) {
    index = (i + tiles.length) % tiles.length;
    var a = tiles[index];
    var d = a.dataset;
    var useRaw = showRaw && !!d.rawSrcset;
    var src = sourceFor(a, useRaw);
    var my = ++token;

    countEl.textContent = (index + 1) + " / " + tiles.length;
    exifEl.textContent = exifText(d);
    fullLink.href = a.href;
    rawBtn.hidden = !d.rawSrcset;
    rawBtn.textContent = useRaw ? "developed_view" : "raw_view";
    rawBtn.setAttribute("aria-pressed", useRaw ? "true" : "false");
    img.alt = a.querySelector("img").alt + (useRaw ? " (unprocessed)" : "");
    measureBar();

    if (keepImage) {
      stage.classList.add("switching");
    } else {
      // show the already-loaded thumbnail straight away, then swap in the sharp version
      var thumb = a.querySelector("img");
      img.removeAttribute("srcset");
      img.src = thumb.currentSrc || thumb.src;
    }
    img.width = src.w;
    img.height = src.h;
    stage.classList.add("loading");

    load(src, function (url) {
      if (my !== token) return;
      if (url) img.src = url;
      stage.classList.remove("loading", "switching");
      preload(index + 1);
      preload(index - 1);
    });

    var hash = "#" + a.id;
    if (location.hash !== hash) history.replaceState(history.state, "", hash);
  }

  function open(i, fromHistory) {
    if (!dlg.open) {
      root.classList.add("lb-open");
      dlg.showModal();
      if (!fromHistory) {
        history.pushState({ lb: true }, "", "#" + tiles[i].id);
        pushedHistory = true;
      }
    }
    render(i);
  }

  function close() {
    if (dlg.open) dlg.close();
  }

  dlg.addEventListener("close", function () {
    root.classList.remove("lb-open");
    token++;
    var a = tiles[index];
    if (!closingFromHistory) {
      if (pushedHistory && history.state && history.state.lb) {
        history.back();
      } else {
        history.replaceState(null, "", location.pathname + location.search);
      }
    }
    pushedHistory = false;
    closingFromHistory = false;
    if (a) {
      a.focus({ preventScroll: true });
      a.scrollIntoView({ block: "nearest" });
    }
  });

  window.addEventListener("popstate", function () {
    var id = location.hash.slice(1);
    var i = id ? tiles.findIndex(function (t) { return t.id === id; }) : -1;
    if (i >= 0) {
      open(i, true);
    } else if (dlg.open) {
      closingFromHistory = true;
      close();
    }
  });

  tiles.forEach(function (a, i) {
    a.addEventListener("click", function (e) {
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      open(i);
    });
  });

  dlg.querySelector(".lb-prev").addEventListener("click", function () { render(index - 1); });
  dlg.querySelector(".lb-next").addEventListener("click", function () { render(index + 1); });
  dlg.querySelector(".lb-close").addEventListener("click", close);
  rawBtn.addEventListener("click", function () { showRaw = !showRaw; render(index, true); });

  // click on the empty area around the photo closes the viewer
  stage.addEventListener("click", function (e) { if (e.target === stage) close(); });

  dlg.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight") { e.preventDefault(); render(index + 1); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); render(index - 1); }
  });

  // swipe left/right to change photo, swipe down to close (ignored while pinch-zoomed)
  var sx = 0, sy = 0, st = 0, tracking = false;
  stage.addEventListener("touchstart", function (e) {
    tracking = e.touches.length === 1;
    if (!tracking) return;
    sx = e.touches[0].clientX; sy = e.touches[0].clientY; st = Date.now();
  }, { passive: true });
  stage.addEventListener("touchend", function (e) {
    if (!tracking) return;
    tracking = false;
    if (window.visualViewport && window.visualViewport.scale > 1.01) return;
    var t = e.changedTouches[0];
    var dx = t.clientX - sx, dy = t.clientY - sy;
    if (Date.now() - st > 800) return;
    if (Math.abs(dx) > 50 && Math.abs(dx) > 1.5 * Math.abs(dy)) render(index + (dx < 0 ? 1 : -1));
    else if (dy > 90 && dy > 1.5 * Math.abs(dx)) close();
  }, { passive: true });

  window.addEventListener("resize", function () { if (dlg.open) measureBar(); });

  // deep link: gallery.html#P9100910 opens that photo directly (old links keep working)
  var start = location.hash.slice(1);
  if (start) {
    var si = tiles.findIndex(function (t) { return t.id === start; });
    if (si >= 0) open(si, true);
  }
})();
