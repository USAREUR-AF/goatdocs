// Copy buttons, and the first screen's replay: one command builds a whole site, each stage
// adding its part to the drawing on one clock; one command takes the site down; the same
// command builds it again. The times are the JSON block that build.py writes from
// run.json. With reduced motion, or without JavaScript, the page shows the finished site.
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

  var src = document.getElementById("run-data"), fig = document.getElementById("fig-site");
  if (!src || !fig) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var R = JSON.parse(src.textContent), parts = fig.querySelectorAll(".st"), N = R.ends.length;
  var clk = document.getElementById("clk"), of = document.getElementById("clk-of"), step = document.getElementById("step");
  var phase = document.getElementById("phase"), bar = document.getElementById("pbar");
  function clock(s) { var m = Math.floor(s / 60), r = Math.floor(s % 60); return m + ":" + (r < 10 ? "0" : "") + r; }
  function show(n) { for (var i = 0; i < parts.length; i++) parts[i].classList.toggle("off", +parts[i].dataset.stage > n); }

  var n = 0;
  function build() {
    n += 1; show(n);
    var t = R.ends[n - 1];
    clk.textContent = clock(n < N ? t : R.total);
    bar.style.width = (100 * (n < N ? t : R.total) / R.total) + "%";
    step.textContent = n < N ? R.names[n - 1] : "The whole site is built and checked";
    phase.textContent = n < N ? "stage " + n + " of " + N : "built";
    if (n < N) { setTimeout(build, 650 + 2600 * (R.ends[n] - t) / R.total); return; }
    setTimeout(down, 4600);
  }
  function down() {
    phase.textContent = "taking it down"; step.textContent = "One command takes the site down";
    of.textContent = "minutes:seconds to take it down";
    var t0 = Date.now(), ms = 1700;
    (function fall() {
      var f = Math.min(1, (Date.now() - t0) / ms);
      show(Math.round(N * (1 - f)));
      bar.style.width = (100 * (1 - f)) + "%";
      clk.textContent = clock(R.down * f);
      if (f < 1) { requestAnimationFrame(fall); return; }
      phase.textContent = "taken down"; step.textContent = "Nothing is left running";
      setTimeout(start, 2400);
    })();
  }
  function start() {
    n = 0; show(0); clk.textContent = "0:00"; bar.style.width = "0";
    of.textContent = "minutes:seconds of machine time";
    phase.textContent = "building"; step.textContent = "The same command builds it again";
    setTimeout(build, 900);
  }
  show(0); clk.textContent = "0:00"; bar.style.width = "0"; phase.textContent = "building"; step.textContent = "One command, from the declaration";
  setTimeout(build, 900);
})();
