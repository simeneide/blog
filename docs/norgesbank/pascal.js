// Pascal slide: one state per fragment step, so the clicker drives it and going back works.
(() => {
  const slide = document.getElementById("pascal");
  const stage = slide.querySelector(".stage");
  const pot = stage.querySelector(".pot");
  const flipper = stage.querySelector(".flipper");
  const result = stage.querySelector(".toss-result");
  const toss = stage.querySelector(".toss");
  const point = stage.querySelector(".point");

  // Steps: 0 portraits, 1 bubble, 2 coins in, 3 rules, 4-6 tosses, 7 stop, 8 question,
  // 9-12 poll rows A-D appear one by one (all stay visible)
  const TOSSES = { 4: "kron", 5: "mynt", 6: "kron" };
  // small coin piles for each poll row: de Méré's share left, Pascal's right
  stage.querySelectorAll(".row[data-split]").forEach(row => {
    const piles = row.querySelector(".piles");
    row.dataset.split.split(",").map(Number).forEach((n, side) => {
      const cx = side === 0 ? 100 : 300;
      let k = 1;
      while ((k * (k + 1)) / 2 < n) k++;
      let placed = 0;
      for (let r = 0, w = k; placed < n; r++, w--) {
        for (let i = 0; i < w && placed < n; i++, placed++) {
          const img = document.createElement("img");
          img.className = "mc";
          img.src = "img/coin.png";
          img.style.left = cx - 13 + (i - (w - 1) / 2) * 17 + "px";
          img.style.top = 50 - r * Math.min(8, 50 / (k - 1)) + "px";
          img.style.zIndex = r;
          img.style.animationDelay = placed * 12 + "ms";
          piles.appendChild(img);
        }
      }
      const num = document.createElement("div");
      num.className = "num";
      num.style.left = cx - 100 + "px";
      num.textContent = side === 0 && n === 43 ? "≈ 43" : side === 1 && n === 21 ? "≈ 21" : n;
      piles.appendChild(num);
    });
  });

  // 64 coins in a pile: rows of 11,10,...,3 and a top coin. Even index from A, odd from B.
  const rows = [11, 10, 9, 8, 7, 6, 5, 4, 3, 1];
  const coins = [];
  rows.forEach((n, r) => {
    for (let i = 0; i < n; i++) {
      const x = 640 - 23 + (i - (n - 1) / 2) * 44;
      const y = 600 - 23 - r * 26;
      coins.push({ x, y, r });
    }
  });
  coins.forEach((c, i) => {
    const img = document.createElement("img");
    img.className = "c";
    img.src = "img/coin.png";
    img.style.left = c.x + "px";
    img.style.top = c.y + "px";
    img.style.zIndex = 2000 + c.r;
    img.style.transitionDelay = (i % 32) * 18 + "ms";
    c.from = i % 2 === 0 ? { x: 220 - c.x, y: 360 - c.y } : { x: 1060 - c.x, y: 360 - c.y };
    c.el = img;
    pot.appendChild(img);
  });

  const posIn = el => {
    let x = 0, y = 0;
    for (let e = el; e && e !== stage; e = e.offsetParent) { x += e.offsetLeft; y += e.offsetTop; }
    return { x, y };
  };

  const setText = (attr, el, step) => {
    let best = null;
    for (const a of el.getAttributeNames()) {
      const m = a.match(new RegExp(`^data-${attr}-(\\d+)$`));
      if (m && +m[1] <= step && (best === null || +m[1] > best)) best = +m[1];
    }
    if (best !== null) el.textContent = el.getAttribute(`data-${attr}-${best}`);
  };

  const score = step => {
    const s = { A: 0, B: 0 };
    for (let k = 4; k <= Math.min(step, 6); k++) s[TOSSES[k] === "kron" ? "A" : "B"]++;
    return s;
  };

  let last = -1;
  const render = step => {
    const forward = step === last + 1;
    stage.classList.toggle("show-bubble", step === 1);
    stage.classList.toggle("coins-in", step >= 2);
    stage.classList.toggle("show-rule", step >= 3);
    stage.classList.toggle("tossing", step >= 4 && step <= 6);
    stage.classList.toggle("stopped", step >= 7);
    stage.classList.toggle("asking", step >= 8);

    setText("title", stage.querySelector(".stage-title"), step);

    coins.forEach(c => {
      c.el.style.opacity = step >= 2 ? 1 : 0;
      c.el.style.transform = step >= 2 ? "none" : `translate(${c.from.x}px, ${c.from.y}px) scale(0.6)`;
    });

    stage.classList.toggle("polling", step >= 9);
    stage.querySelectorAll(".row").forEach(r => r.classList.toggle("shown", step >= +r.dataset.row));

    const face = TOSSES[step];
    const animate = Boolean(face) && forward;
    const s = score(step);
    const winner = face === "kron" ? "A" : "B";
    // Final state is set immediately; CSS delays only control when it becomes visible,
    // so nothing depends on animation events (which pause in hidden tabs).
    stage.querySelectorAll(".pips").forEach(p => {
      [...p.children].forEach((pip, i) => {
        pip.classList.toggle("on", i < s[p.dataset.player]);
        pip.classList.toggle("late", animate && p.dataset.player === winner && i === s[winner] - 1);
      });
    });

    flipper.className = "flipper";
    toss.classList.remove("spinning");
    point.classList.remove("fly");
    result.classList.remove("late");
    result.textContent = "";
    if (face) {
      flipper.classList.toggle("face-mynt", face === "mynt");
      flipper.style.setProperty("--end", face === "mynt" ? 1 : 0);
      result.textContent = face === "kron" ? "Kron: poeng til de Méré" : "Mynt: poeng til Pascal";
      if (animate) {
        void flipper.offsetWidth; // restart animations
        flipper.classList.add("spin");
        toss.classList.add("spinning");
        result.classList.add("late");
        const from = posIn(flipper), to = posIn(stage.querySelector(`.pips[data-player="${winner}"]`).children[s[winner] - 1]);
        point.style.left = from.x + 63 + "px";
        point.style.top = from.y + 63 + "px";
        point.style.setProperty("--dx", to.x - from.x - 63 + "px");
        point.style.setProperty("--dy", to.y - from.y - 63 + "px");
        point.classList.add("fly");
      }
    }
    last = step;
  };

  const currentStep = () => slide.querySelectorAll(".fragment.step.visible").length;
  const update = () => { if (Reveal.getCurrentSlide() === slide) render(currentStep()); };
  Reveal.on("ready", update);
  Reveal.on("slidechanged", update);
  Reveal.on("fragmentshown", update);
  Reveal.on("fragmenthidden", update);
  render(0);
})();
