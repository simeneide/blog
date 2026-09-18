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

  // Fit the whole recording, including wider activity edits, without cropping.
  var PHONE_MAX_H = 900;
  var PHONE_MAX_W = 760;

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
    // A clip already moves. Ken Burns is for stills only, so every kb* class
    // is dropped here rather than at every call site.
    if (media.type === "video") {
      var keep = (cls || "")
        .split(/\s+/)
        .filter(function (c) {
          return c && c.indexOf("kb") !== 0;
        })
        .join(" ");
      return videoEl(media, keep);
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


  // Only stills move artificially; app recordings keep their captured camera.
  function bleed(sec, s) {
    var node = mediaEl(s.media, "media-bleed kb kb-" + (s.kb || "in"));
    sec.appendChild(node);
    return node;
  }

  function titleCard(sec, s) {
    var card = el("div", "title-card card-" + s.card, sec);
    if (s.card === "none") card.style.display = "none";
    el("h2", null, card).textContent = s.title;
    if (s.lines.length) el("p", null, card).textContent = s.lines.join(" ");
    return card;
  }

  function buildWide(sec, s) {
    sec.classList.add("wide-slide");
    bleed(sec, s);
    // Default to an unobscured app, with contrast only behind the title.
    if (s.scrim !== false) el("div", "scrim", sec);
    titleCard(sec, s);
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

    var still = el("img", "bg-blur kb-bg kb", sec);
    still.src = s.media.poster || s.media.src;
    still.alt = "";
    el("div", "bg-tint", sec);

    var grid = el("div", "phone-grid", sec);
    var frame = el("div", "phone-frame", grid);
    var screen = el("div", "phone-screen", frame);

    var ratio = (s.media.w || 1080) / (s.media.h || 1920);
    var sh = Math.min(PHONE_MAX_H, PHONE_MAX_W / ratio);
    screen.style.width = Math.round(sh * ratio) + "px";
    screen.style.height = Math.round(sh) + "px";
    grid.style.gridTemplateColumns =
      Math.max(700, Math.round(sh * ratio) + 180) + "px 1fr";
    var inner = mediaEl(
      s.media,
      s.media.type === "image" ? "kb kb-" + (s.kb || "in") : null,
    );
    screen.appendChild(inner);

    var copy = el("div", "phone-copy", grid);
    el("h2", null, copy).textContent = s.title;
    lines(copy, s.lines);
    if (s.qr) {
      qrBlock(
        copy,
        s.qr,
        s.qr === "coupe" ? "pgpilot.app/coupe" : "pgpilot.app",
        s.qr === "coupe" ? "Join this week's contest" : "iOS and Android",
      );
    }
  }


  // Two stills on one slide, one after the other: the first pushes in on
  // what the second is a close-up of, then hands over. Used where a wide
  // figure and its detail are the same thought.
  function buildSeq(sec, s) {
    sec.classList.add("wide-slide", "seq-slide");
    s.images.forEach(function (im, i) {
      var cell = el("div", "seq-cell anim " + (i ? "seq-b" : "seq-a"), sec);
      var img = el("img", "kb kb-" + ((s.kbSeq && s.kbSeq[i]) || "in"), cell);
      img.src = im.src;
      img.alt = "";
      // The second one spends its first ten seconds at opacity 0, so Chromium
      // is in no hurry to decode it and the cross-fade can land on a
      // half-painted picture. Decode it up front and paint it in one go.
      img.decoding = "sync";
      img.loading = "eager";
      if (img.decode) img.decode().catch(function () {});
      if (s.kbOriginSeq && s.kbOriginSeq[i]) {
        img.style.transformOrigin = s.kbOriginSeq[i];
      }
    });
    if (s.scrim !== false) el("div", "scrim", sec);
    titleCard(sec, s);
  }


  var BUILDERS = {
    wide: buildWide,
    seq: buildSeq,
    phone: buildPhone,
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
  var chipFor = []; // slide index -> chip index

  SLIDES.forEach(function (s, i) {
    // A slide with no label shares the previous slide's chip. That is how a
    // run of slides on one theme stays one entry in the strip: the strip has
    // 1920 px and no second row, so every entry has to earn its width.
    if (!s.label) {
      chipFor.push(chips.length - 1);
      return;
    }
    // A real button: this monitor gets touched, and someone at the stand
    // should be able to put a finger on a feature and land on it.
    var a = el("button", "hk", strip);
    a.type = "button";
    if (s.key) el("b", null, a).textContent = s.key;
    a.appendChild(document.createTextNode(s.label));
    a.dataset.index = String(i);
    a.setAttribute("aria-label", s.title);
    a.addEventListener("click", function () {
      a.blur(); // or the next space bar would press it again
      jump(i);
    });
    chipFor.push(chips.length);
    chips.push(a);
  });

  // -------------------------------------------------------------- edge taps
  // The stand screen gets touched, and a hand goes to the edge of a picture
  // before it goes to a 64 px strip. Two tall zones down the sides step the
  // deck, with a chevron that stays nearly invisible until something is on it.
  function edge(side) {
    var z = el("button", "edge edge-" + side, document.body);
    z.type = "button";
    z.setAttribute(
      "aria-label",
      side === "left" ? "Previous slide" : "Next slide",
    );
    el("span", "chev", z);
    z.addEventListener("click", function () {
      z.blur();
      step(side === "right");
    });
  }
  edge("left");
  edge("right");

  function markStrip(i) {
    var on = chipFor[i];
    chips.forEach(function (c, n) {
      c.classList.toggle("on", n === on);
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
    var cq = SLIDES[i] ? SLIDES[i].cornerQr : "top";
    document.body.classList.toggle("no-corner-qr", cq === false);
    document.body.classList.toggle("corner-qr-low", cq === "low");
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

  // Reveal cues the auto-advance timer when it decides to, not when we move
  // the deck by hand: after a jump the new slide inherits whatever was left of
  // the old slide's countdown, so a slide someone just pressed could be gone
  // in two seconds. Pausing and resuming re-cues it from now, with the new
  // slide's own data-autoslide. autoSlideStoppable stays false, so the deck
  // still carries on by itself afterwards.
  function recue() {
    if (!Reveal.toggleAutoSlide) return;
    Reveal.toggleAutoSlide(false);
    Reveal.toggleAutoSlide(true);
  }

  function jump(i) {
    if (i == null || i < 0 || i >= SLIDES.length) return;
    Reveal.slide(i, 0);
    recue();
  }

  function step(forward) {
    if (forward) Reveal.next();
    else Reveal.prev();
    recue();
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
      step(true);
      e.preventDefault();
      return;
    }
    if (k === "ArrowLeft" || k === "PageUp") {
      step(false);
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
