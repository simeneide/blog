// Next-word slide: the sentence grows one word per click. For each prediction, attention arcs
// show the transformer looking at every earlier word, then the distribution for the next word.
// On the next click the most likely word flies up into the sentence.
(() => {
  const slide = document.getElementById("neste-ord");
  if (!slide) return;
  const stage = slide.querySelector(".lm2-stage");

  const START = "Styringsrenten";
  // One entry per prediction: attention weight per earlier word, and the next-word distribution
  const STEPS = [
    { att: [1], dist: [["vil", 41], ["er", 22], ["ble", 14], ["kan", 9], ["holdes", 6]] },
    { att: [0.65, 0.35], dist: [["holdes", 47], ["settes ned", 31], ["økes", 9], ["trolig", 6], ["ligge", 4]] },
    { att: [0.3, 0.1, 0.6], dist: [["uendret", 83], ["på", 9], ["i ro", 4], ["fast", 2]] },
  ];

  const row = document.createElement("div");
  row.className = "lm2-row";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "lm2-arcs");
  const dist = document.createElement("div");
  dist.className = "lm2-dist";
  stage.append(svg, row, dist);

  // position of an element in stage coordinates (unscaled layout pixels)
  const pos = el => {
    let x = 0, y = 0;
    for (let e = el; e && e !== stage; e = e.offsetParent) { x += e.offsetLeft; y += e.offsetTop; }
    return { x, y, w: el.offsetWidth, h: el.offsetHeight };
  };

  const words = step => [START, ...STEPS.slice(0, step).map(s => s.dist[0][0])];

  const render = step => {
    row.innerHTML = "";
    for (const w of words(step)) {
      const t = document.createElement("span");
      t.className = "lm2-tok";
      t.textContent = w;
      row.append(t);
    }
    const s = STEPS[step];
    svg.innerHTML = "";
    dist.innerHTML = "";
    if (!s) return;
    const slot = document.createElement("span");
    slot.className = "lm2-tok slot";
    slot.textContent = "?";
    row.append(slot);

    // attention arcs from every earlier word to the slot
    const toks = [...row.querySelectorAll(".lm2-tok:not(.slot)")];
    const b = pos(slot), bx = b.x + b.w / 2, by = b.y;
    toks.forEach((t, i) => {
      const a = pos(t), ax = a.x + a.w / 2, ay = a.y;
      const lift = 40 + 0.18 * (bx - ax);
      const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
      p.setAttribute("d", `M ${ax} ${ay - 6} C ${ax} ${ay - lift}, ${bx} ${by - lift}, ${bx} ${by - 6}`);
      p.setAttribute("stroke-width", 2 + 14 * s.att[i]);
      p.style.opacity = 0.3 + 0.7 * s.att[i];
      svg.append(p);
      const len = p.getTotalLength();
      p.style.strokeDasharray = len;
      p.animate([{ strokeDashoffset: len }, { strokeDashoffset: 0 }], { duration: 700, delay: 120 * i, fill: "backwards", easing: "ease-out" });
    });

    s.dist.forEach(([w, pct], j) => {
      const r = document.createElement("div");
      r.className = "lm2-bar" + (j === 0 ? " top" : "");
      r.innerHTML = `<span class="w">${w}</span><span class="b" style="width:${pct * 6}px"></span><span class="p">${pct} %</span>`;
      r.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 400, delay: 700 + 60 * j, fill: "backwards" });
      dist.append(r);
    });
  };

  let shown = -1;
  const update = () => {
    if (Reveal.getCurrentSlide() !== slide) return;
    const step = slide.querySelectorAll(".fragment.gstep.visible").length;
    if (step === shown + 1 && shown >= 0) {
      // forward one click: fly the chosen word from its bar up into the slot
      const from = dist.querySelector(".lm2-bar.top .w");
      const slot = row.querySelector(".slot");
      if (from && slot) {
        const a = pos(from), b = pos(slot);
        const fly = document.createElement("span");
        fly.className = "lm2-fly";
        fly.textContent = from.textContent;
        fly.style.left = a.x + "px";
        fly.style.top = a.y + "px";
        stage.append(fly);
        from.style.visibility = "hidden";
        const scale = 46 / 38;
        fly.animate(
          [{ transform: "translate(0, 0) scale(1)" }, { transform: `translate(${b.x - a.x}px, ${b.y - a.y}px) scale(${scale})` }],
          { duration: 650, easing: "cubic-bezier(.3,.7,.4,1)" },
        ).finished.then(() => { fly.remove(); render(step); });
        shown = step;
        return;
      }
    }
    render(step);
    shown = step;
  };
  Reveal.on("ready", update);
  Reveal.on("slidechanged", update);
  Reveal.on("fragmentshown", update);
  Reveal.on("fragmenthidden", update);
})();
