// Copy buttons, and the first screen's replay: the skill's two scripts run in a new
// repository, their output copied from the run and shown line by line in order.
// With reduced motion, or without JavaScript, the page shows the last frame.
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

  var LINES = [
    ["in", "$ python3 -I scaffold.py site . --name example-repo --repo USAREUR-AF/example-repo"],
    ["", "wrote site/build.py"], ["", "wrote site/index.html"], ["", "wrote site/fitcheck.py"],
    ["", "wrote site/README.md"], ["", "wrote site/.gitignore"], ["", "wrote site/assets/icon.svg"],
    ["", "wrote site/assets/site.css"], ["", "wrote site/assets/site.js"],
    ["", "wrote .github/workflows/pages.yml"],
    ["in", "$ python3 -I site/build.py"],
    ["", "site/index.html: placeholders on lines 7, 24, 25, 28, 30 (and 23 more)"],
    ["", "site/assets/icon.svg: placeholders on line 1"],
    ["", "site/assets/site.css: placeholders on lines 1, 5"],
    ["", "site/assets/site.js: placeholders on line 18"],
    ["no", "site/index.html: example-count says 0, the tree gives 1"],
    ["cm", "# the page is written"],
    ["in", "$ python3 -I site/build.py"],
    ["ok", "fitcheck: index.html: every box fits at 1440 and 390 px"],
    ["ev", "site: numbers match the tree: example-count=1"]
  ];
  var RUNS = { 0: "1/3 scaffold", 10: "2/3 build fails", 17: "3/3 build passes" };
  var box = document.getElementById("stage-lines"), step = document.getElementById("step");
  if (!box) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var SHOW = 12, i = 0;
  function esc(s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;"); }
  function draw() {
    var from = Math.max(0, i - SHOW);
    box.innerHTML = LINES.slice(from, i).map(function (l) {
      return '<span class="' + l[0] + '">' + esc(l[1]) + "</span>";
    }).join("");
  }
  (function tick() {
    if (i in RUNS) step.textContent = RUNS[i];
    i += 1; draw();
    if (i < LINES.length) { setTimeout(tick, LINES[i][0] === "in" || LINES[i][0] === "cm" ? 1300 : 380); return; }
    setTimeout(function () { i = 0; tick(); }, 5000);
  })();
})();
