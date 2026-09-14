/* Coupe Icare stand kiosk.
 *
 * Builds the deck from window.KIOSK_SLIDES (written by build.py), starts
 * Reveal in auto-play, and adds the two things a stand screen needs that a
 * normal deck does not: a hotkey strip so anyone can jump straight to the
 * feature a visitor just asked about, and a hard guarantee that nothing on
 * screen is ever still.
 *
 * Keyboard handling is ours, not Reveal's (keyboard: false below). Reveal's
 * defaults would eat the letters we want: s opens the speaker window, n steps
 * forward, f goes fullscreen, o toggles the overview. We still reimplement the
 * two bindings that are worth keeping, Escape for the overview and
 * number+Enter for a direct jump.
 */

(function () {
  "use strict";

  var SLIDES = window.KIOSK_SLIDES || [];

  // The phone frame. The screen is fitted inside this box, so a 9:16 reel and
  // a taller 780x1688 screen recording both sit in a believable phone instead
  // of being cropped to a common shape.
  var PHONE_MAX_H = 900;
  var PHONE_MAX_W = 520;
  // ...but only down to a point. klipp-knapp.mp4 is 1080x1714, and a frame cut
  // to that shape is a stubby tablet sitting next to four proper phones. The
  // clamp is 0.60 rather than a true 9:16 on purpose: at 9:16 the crop ate the
  // leading digit of the altitude, and a cut-off number reads as a bug.
  var PHONE_MIN_RATIO = 0.42;
  var PHONE_MAX_RATIO = 0.6;

  // ---------------------------------------------------------------- helpers

  function el(tag, cls, parent) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (parent) parent.appendChild(n);
    return n;
  }

  function videoEl(media, cls) {
    var v = document.createElement("video");
    if (cls) v.className = cls;
    v.src = media.src;
    if (media.poster) v.poster = media.poster;
    v.muted = true;
    v.defaultMuted = true;
    v.loop = true;
    v.playsInline = true;
    v.setAttribute("muted", "");
    v.setAttribute("loop", "");
    v.setAttribute("playsinline", "");
    v.setAttribute("data-autoplay", "");
    v.preload = "metadata";
    return v;
  }

  function mediaEl(media, cls) {
    // A clip already moves. Ken Burns is for stills only, so the class is
    // dropped here rather than at every call site.
    if (media.type === "video") {
      return videoEl(media, (cls || "").replace(/\bkb\b/g, "").trim());
    }
    var img = document.createElement("img");
    img.className = cls;
    img.src = media.src;
    img.alt = "";
    return img;
  }

  function lines(parent, arr) {
    var box = el("div", "lines", parent);
    arr.forEach(function (t) {
      el("p", null, box).textContent = t;
    });
    return box;
  }

  function qrBlock(parent, which, label, sub) {
    var wrap = el("div", "slide-qr", parent);
    var card = el("div", "qr-card", wrap);
    var img = el("img", null, card);
    img.src = which === "coupe" ? "img/qr-coupe.svg" : "img/qr-pgpilot.svg";
    img.alt = "";
    var txt = el("div", "qr-label", wrap);
    el("strong", null, txt).textContent = label;
    txt.appendChild(document.createTextNode(sub));
    return wrap;
  }

  // ----------------------------------------------------------- slide builds

  function buildTitle(sec, s) {
    sec.classList.add("title-slide");
    sec.appendChild(mediaEl(s.media, "media-bleed kb"));
    el("div", "scrim", sec);
    var c = el("div", "center", sec);
    var mark = el("img", "wordmark", c);
    mark.src = "img/pgpilot-wordmark.png";
    mark.alt = "pgpilot";
    el("h1", null, c).textContent = s.title;
    el("div", "sub", c).textContent = s.lines.join(" ");
  }

  function buildWide(sec, s) {
    sec.classList.add("wide-slide");
    sec.appendChild(mediaEl(s.media, "media-bleed kb" + (s.dim ? " media-dim" : "")));
    el("div", "scrim", sec);
    var card = el("div", "title-card" + (s.card === "top" ? " card-top" : ""), sec);
    el("h2", null, card).textContent = s.title;
    el("p", null, card).textContent = s.lines.join(" ");
    if (s.qr) {
      qrBlock(
        sec,
        s.qr,
        s.qr === "coupe" ? "pgpilot.app/coupe" : "pgpilot.app",
        s.qr === "coupe" ? "Join this week's contest" : "iOS and Android",
      );
    }
  }

  function buildPhone(sec, s) {
    sec.classList.add("phone-slide");

    // Backdrop: the landscape recording if we have one, otherwise a blurred,
    // slowly zooming frame of the same clip. Either way the slide moves even
    // where there is no content.
    if (s.bg) {
      sec.appendChild(mediaEl(s.bg, "bg-blur"));
    } else {
      var still = el("img", "bg-blur kb-bg kb", null);
      still.src = s.media.poster || s.media.src;
      still.alt = "";
      sec.appendChild(still);
    }
    el("div", "bg-tint", sec);

    var grid = el("div", "phone-grid", sec);
    var frame = el("div", "phone-frame", grid);
    var screen = el("div", "phone-screen", frame);

    var ratio = (s.media.w || 1080) / (s.media.h || 1920);
    ratio = Math.min(PHONE_MAX_RATIO, Math.max(PHONE_MIN_RATIO, ratio));
    var sh = Math.min(PHONE_MAX_H, PHONE_MAX_W / ratio);
    screen.style.width = Math.round(sh * ratio) + "px";
    screen.style.height = Math.round(sh) + "px";
    var inner = mediaEl(s.media, s.media.type === "image" ? "kb" : null);
    screen.appendChild(inner);

    var copy = el("div", "phone-copy", grid);
    el("h2", null, copy).textContent = s.title;
    lines(copy, s.lines);
    if (s.footnote) el("div", "footnote", copy).textContent = s.footnote;
    if (s.qr) {
      qrBlock(
        copy,
        s.qr,
        s.qr === "coupe" ? "pgpilot.app/coupe" : "pgpilot.app",
        s.qr === "coupe" ? "Join this week's contest" : "iOS and Android",
      );
    }
  }

  function buildDuo(sec, s) {
    sec.classList.add("duo-slide");
    var wrap = el("div", "duo-wrap", sec);
    s.images.forEach(function (im, i) {
      var cell = el("div", "duo-cell", wrap);
      var img = el("img", "kb", cell);
      img.src = im.src;
      img.alt = "";
      // Opposite drift, so the two halves do not read as one sliding block.
      img.style.transformOrigin = i === 0 ? "30% 30%" : "70% 60%";
    });
    var card = el("div", "title-card", sec);
    el("h2", null, card).textContent = s.title;
    el("p", null, card).textContent = s.lines.join(" ");
  }

  function buildClosing(sec, s) {
    sec.classList.add("closing-slide");
    sec.appendChild(mediaEl(s.media, "media-bleed kb"));
    el("div", "scrim", sec);
    var c = el("div", "center", sec);
    el("h2", null, c).textContent = s.title;
    var card = el("div", "qr-card", c);
    var img = el("img", null, card);
    img.src = "img/qr-pgpilot.svg";
    img.alt = "QR code for pgpilot.app";
    el("div", "url", c).textContent = "pgpilot.app";
    el("div", "ask", c).textContent = s.lines.join(" ");
  }

  var BUILDERS = {
    title: buildTitle,
    wide: buildWide,
    phone: buildPhone,
    duo: buildDuo,
    closing: buildClosing,
  };

  var slidesRoot = document.querySelector(".slides");

  SLIDES.forEach(function (s) {
    var sec = document.createElement("section");
    sec.dataset.id = s.id;
    sec.dataset.autoslide = String(s.dur * 1000);
    sec.style.setProperty("--dur", s.dur + "s");
    (BUILDERS[s.layout] || buildWide)(sec, s);
    slidesRoot.appendChild(sec);
  });

  // ------------------------------------------------------------ hotkey strip

  var strip = document.querySelector(".hotkeys");
  var chips = [];

  SLIDES.forEach(function (s, i) {
    var a = el("div", "hk", strip);
    if (s.key) el("b", null, a).textContent = s.key;
    a.appendChild(document.createTextNode(s.label));
    chips.push(a);
    a.dataset.index = String(i);
  });

  function markStrip(i) {
    chips.forEach(function (c, n) {
      c.classList.toggle("on", n === i);
    });
  }

  var byKey = {};
  SLIDES.forEach(function (s, i) {
    if (s.key) byKey[s.key.toUpperCase()] = i;
  });

  // ------------------------------------------------------------------ Reveal

  Reveal.initialize({
    width: 1920,
    height: 1080,
    margin: 0,
    controls: false,
    progress: false,
    slideNumber: false,
    hash: false,
    transition: "fade",
    transitionSpeed: "fast",
    backgroundTransition: "fade",
    loop: true,
    autoSlide: 20000, // per-slide data-autoslide overrides this
    autoSlideStoppable: false, // keep cycling after someone jumps
    keyboard: false, // we handle keys ourselves, see below
    touch: false,
    overview: true,
    disableLayout: false,
    display: "block",
  });

  // ----------------------------------------------------- motion bookkeeping

  function restart(sec) {
    if (!sec) return;

    // Ken Burns: strip the class, force a reflow, add it back. Without the
    // reflow the browser coalesces the two changes and the animation never
    // restarts, which is how a "moving" kiosk quietly goes static.
    sec.querySelectorAll(".kb").forEach(function (n) {
      n.classList.remove("kb-run");
      void n.offsetWidth;
      n.classList.add("kb-run");
    });

    // Video: always from the top. Reveal plays it for us, but it resumes
    // wherever the last visit left off, so on the second lap a 5 s clip would
    // start two thirds in.
    sec.querySelectorAll("video").forEach(function (v) {
      try {
        v.currentTime = 0;
      } catch (e) {
        /* not seekable yet, it will start at 0 anyway */
      }
      var p = v.play();
      if (p && p.catch) p.catch(function () {});
    });
  }

  function pause(sec) {
    if (!sec) return;
    sec.querySelectorAll("video").forEach(function (v) {
      v.pause();
    });
    sec.querySelectorAll(".kb").forEach(function (n) {
      n.classList.remove("kb-run");
    });
  }

  // Pull the next slide's clips in early so the cut is clean. Everything is
  // local, but the first lap still has to read it off disk.
  function warm(i) {
    var all = slidesRoot.children;
    var next = all[(i + 1) % all.length];
    if (!next) return;
    next.querySelectorAll("video").forEach(function (v) {
      if (v.preload !== "auto") {
        v.preload = "auto";
        if (v.readyState === 0) v.load();
      }
    });
  }

  function onSlide(ev) {
    var i = ev && typeof ev.indexh === "number" ? ev.indexh : Reveal.getIndices().h;
    if (ev && ev.previousSlide) pause(ev.previousSlide);
    var cur = (ev && ev.currentSlide) || Reveal.getCurrentSlide();
    restart(cur);
    markStrip(i);
    warm(i);
    document.body.classList.toggle("no-corner-qr", SLIDES[i] && SLIDES[i].cornerQr === false);
  }

  Reveal.on("ready", onSlide);
  Reveal.on("slidechanged", onSlide);

  // Chrome refuses the first play() often enough that it is worth a retry:
  // any clip that is on screen and not running gets nudged once a second.
  setInterval(function () {
    var cur = Reveal.getCurrentSlide();
    if (!cur) return;
    cur.querySelectorAll("video").forEach(function (v) {
      if (v.paused) {
        var p = v.play();
        if (p && p.catch) p.catch(function () {});
      }
    });
  }, 1000);

  // ---------------------------------------------------------------- keyboard

  var numBuf = "";
  var numTimer = null;
  var threeTimer = null;

  function clearNum() {
    numBuf = "";
    clearTimeout(numTimer);
    numTimer = null;
  }

  function cancelThree() {
    if (threeTimer) {
      clearTimeout(threeTimer);
      threeTimer = null;
    }
  }

  function jump(i) {
    if (i == null || i < 0 || i >= SLIDES.length) return;
    Reveal.slide(i, 0);
  }

  document.addEventListener("keydown", function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var k = e.key;

    if (k === "Escape") {
      cancelThree();
      clearNum();
      Reveal.toggleOverview();
      return;
    }

    if (k === "Enter") {
      cancelThree();
      if (numBuf) {
        var n = parseInt(numBuf, 10);
        clearNum();
        jump(n - 1);
      }
      e.preventDefault();
      return;
    }

    if (/^[0-9]$/.test(k)) {
      // A digit is ambiguous: "3" is the 3D replay hotkey, but it is also the
      // first half of "13" + Enter. So a lone 3 arms a short timer, and any
      // second digit or an Enter disarms it and makes it a number again.
      cancelThree();
      numBuf += k;
      clearTimeout(numTimer);
      numTimer = setTimeout(clearNum, 2000);
      if (numBuf === "3") {
        threeTimer = setTimeout(function () {
          threeTimer = null;
          clearNum();
          jump(byKey["3"]);
        }, 600);
      }
      e.preventDefault();
      return;
    }

    if (k === "Home") {
      cancelThree();
      clearNum();
      jump(byKey["HOME"] != null ? byKey["HOME"] : 0);
      e.preventDefault();
      return;
    }
    if (k === "End") {
      cancelThree();
      clearNum();
      jump(SLIDES.length - 1);
      e.preventDefault();
      return;
    }
    if (k === "ArrowRight" || k === "PageDown" || k === " ") {
      Reveal.next();
      e.preventDefault();
      return;
    }
    if (k === "ArrowLeft" || k === "PageUp") {
      Reveal.prev();
      e.preventDefault();
      return;
    }

    if (/^[a-zA-Z]$/.test(k)) {
      var target = byKey[k.toUpperCase()];
      if (target != null) {
        cancelThree();
        clearNum();
        jump(target);
        e.preventDefault();
      }
    }
  });

  // Handy for the Playwright check and for anyone debugging on the stand.
  window.KIOSK = {
    jump: jump,
    slides: SLIDES,
    index: function () {
      return Reveal.getIndices().h;
    },
  };
})();
