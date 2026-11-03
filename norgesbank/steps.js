// Generic stepper for simple build slides: count visible .gstep fragments on the slide, then
// [data-show=n] is visible from step n, [data-hide=n] disappears at step n, titles via data-title-n.
(() => {
  // leaf slides only: with # chapters, Quarto wraps slides in vertical stacks
  const slides = [...document.querySelectorAll(".reveal .slides section")].filter(s => !s.querySelector("section") && s.querySelector(".fragment.gstep"));
  const render = slide => {
    const step = slide.querySelectorAll(".fragment.gstep.visible").length;
    slide.querySelectorAll("[data-show]").forEach(el => el.classList.toggle("on", step >= +el.dataset.show));
    slide.querySelectorAll("[data-hide]").forEach(el => el.classList.toggle("off", step >= +el.dataset.hide));
    slide.querySelectorAll(".stage-title").forEach(el => {
      let best = null;
      for (const a of el.getAttributeNames()) {
        const m = a.match(/^data-title-(\d+)$/);
        if (m && +m[1] <= step && (best === null || +m[1] > best)) best = +m[1];
      }
      if (best !== null) el.textContent = el.getAttribute(`data-title-${best}`);
    });
    slide.querySelectorAll("[data-zoom]").forEach(el => el.classList.toggle("zoom", step >= +el.dataset.zoom));
    const stage = slide.querySelector(".stage");
    if (stage) {
      stage.classList.toggle("zooming", !!slide.querySelector("[data-zoom].zoom"));
      for (let i = 0; i <= 20; i++) stage.classList.toggle("s" + i, step >= i);
    }
    slide.dataset.step = step;
  };
  const update = () => { const s = Reveal.getCurrentSlide(); if (slides.includes(s)) render(s); };
  Reveal.on("ready", update);
  Reveal.on("slidechanged", update);
  Reveal.on("fragmentshown", update);
  Reveal.on("fragmenthidden", update);
  slides.forEach(render);
})();
