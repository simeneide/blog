// Probability tree for the problem of points. One state per fragment step, like pascal.js.
(() => {
  const slide = document.getElementById("tree");
  const stage = slide.querySelector(".stage");

  // Steps: 0 root, 1 first toss, 2 de Méré wins at once (1/2), 3 second toss (1/4 each),
  // 4 sum per player, 5 split the pot 48 / 16, 6 insight, 7 = expected value
  const STATES = ["s-toss1", "s-n1", "s-toss2", "s-sum", "s-split", "s-insight", "s-ev"];

  // small coin piles in the summary rows
  stage.querySelectorAll(".sp").forEach(box => {
    const n = +box.dataset.n;
    let k = 1;
    while ((k * (k + 1)) / 2 < n) k++;
    let placed = 0;
    for (let r = 0, w = k; placed < n; r++, w--) {
      for (let i = 0; i < w && placed < n; i++, placed++) {
        const img = document.createElement("img");
        img.className = "mc";
        img.src = "img/coin.png";
        img.style.left = 100 - 13 + (i - (w - 1) / 2) * 17 + "px";
        img.style.top = 70 - r * Math.min(8, 62 / Math.max(k - 1, 1)) + "px";
        img.style.zIndex = r;
        img.style.animationDelay = placed * 15 + "ms";
        box.appendChild(img);
      }
    }
  });

  const setTitle = step => {
    const el = stage.querySelector(".stage-title");
    let best = 0;
    for (const a of el.getAttributeNames()) {
      const m = a.match(/^data-title-(\d+)$/);
      if (m && +m[1] <= step && +m[1] >= best) best = +m[1];
    }
    el.textContent = el.getAttribute(`data-title-${best}`);
  };

  const render = step => {
    STATES.forEach((cls, i) => stage.classList.toggle(cls, step >= i + 1));
    setTitle(step);
  };

  const currentStep = () => slide.querySelectorAll(".fragment.tstep.visible").length;
  const update = () => { if (Reveal.getCurrentSlide() === slide) render(currentStep()); };
  Reveal.on("ready", update);
  Reveal.on("slidechanged", update);
  Reveal.on("fragmentshown", update);
  Reveal.on("fragmenthidden", update);
  render(0);
})();
