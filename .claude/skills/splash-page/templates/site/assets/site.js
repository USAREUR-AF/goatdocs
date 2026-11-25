// Copy buttons, and the first screen's replay. The replay shows a real artifact
// from the tree (a capture, a vector, a recorded session) in the order it lists
// its records; it decides nothing. Reduced motion: stop on one telling frame.
(function () {
  "use strict";
  document.querySelectorAll("button.copy").forEach(function (b) {
    b.addEventListener("click", function () {
      var text = document.getElementById(b.dataset.copy).textContent;
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(function () {
        b.textContent = "Copied"; setTimeout(function () { b.textContent = "Copy"; }, 1600);
      });
    });
  });

  var stage = document.getElementById("stage-lines");
  if (!stage) return;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  // REPLACE: load the real artifact (fetch("assets/from-tree/<file>")) and build LINES from it.
  // Until then the lines already in the page (the no-JS frame) are revealed one by one.
  var lines = Array.prototype.slice.call(stage.children);
  if (reduce || !lines.length) return;
  var i = 0;
  lines.forEach(function (l) { l.style.visibility = "hidden"; });
  (function tick() {
    if (i >= lines.length) {
      setTimeout(function () { lines.forEach(function (l) { l.style.visibility = "hidden"; }); i = 0; tick(); }, 3000);
      return;
    }
    lines[i++].style.visibility = "visible";
    setTimeout(tick, 650);
  })();
})();
