// Copy buttons, and the first screen's replay of one timed run. The data is the JSON block
// written into the page by build.py from run.json. With reduced motion, or without
// JavaScript, the page shows the last frame, which build.py wrote.
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

  var src = document.getElementById("run-data"), box = document.getElementById("stage-lines");
  if (!src || !box) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var R = JSON.parse(src.textContent);
  var $ = function (id) { return document.getElementById(id); };
  var clk = $("clk"), step = $("step"), b1 = $("b1"), b1l = $("b1l"), b2 = $("b2"), b3 = $("b3");
  var v1 = $("v1"), v2 = $("v2"), v3 = $("v3");
  var ticks = Array.prototype.slice.call(document.querySelectorAll(".trk .tick"));
  function two(n) { return (n < 10 ? "0" : "") + n; }
  function clock(s) { return Math.floor(s / 60) + ":" + two(Math.floor(s % 60)); }
  function dur(s) { var m = Math.floor(s / 60), r = Math.floor(s % 60); return m + " min" + (r ? " " + r + " s" : ""); }
  function pct(s) { return (100 * s / R.scale).toFixed(2) + "%"; }
  function verdict(ok) { return ok ? "met" : "not met"; }

  // the frames, in order: [clock seconds, line class, line text, label for the stage head]
  var F = [], t = 0, i;
  for (i = 0; i < R.steps.length; i++) {
    t += R.steps[i].seconds;
    F.push([t, "", two(R.steps[i].phase) + "  " + R.steps[i].name + "  " + clock(R.steps[i].seconds), "phase " + R.steps[i].phase]);
  }
  F.push([R.unattended_end, "ev", "phases 1 to 10: " + R.steps.length + " steps, no stop", "phase 10"]);
  var late = R.stops.slice().sort(function (a, b) { return a.at_s - b.at_s; }), signed = false;
  function signin() {
    F.push([R.person.done_at_s, "", R.person.phase + "  " + R.person.name + ", done", "phase " + R.person.phase]);
    signed = true;
  }
  for (i = 0; i < late.length; i++) {
    if (late[i].at_s > R.acceptance.at_s) break;
    if (!signed && late[i].at_s >= R.person.done_at_s) signin();
    F.push([late[i].at_s, "st", "stop " + late[i].n + "  phase " + late[i].phase + ": " + late[i].reason, "stop " + late[i].n]);
  }
  if (!signed) signin();
  var A = R.acceptance;
  F.push([A.at_s, "ev", "acceptance: " + A.pass + " passed, " + A.fail + " failed, " + A.unknown + " undecided", "acceptance"]);
  F.push([A.at_s, R.met ? "ok" : "st", "first site: " + dur(A.at_s) + "; target " + dur(R.target) + ": " + verdict(R.met), "verdict"]);
  var END1 = F.length;
  F.push([A.at_s, "", "the same steps with no stop: " + dur(R.clean), "steps only"]);
  F.push([A.at_s, R.down_met ? "ok" : "st", "site taken down: " + dur(R.teardown.seconds) + "; target " + dur(R.teardown.target_s) + ": " + verdict(R.down_met), "teardown"]);

  var SHOW = 9, n = 0;
  function esc(s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;"); }
  function draw() {
    var now = n ? F[n - 1][0] : 0, signedAt = R.person.done_at_s;
    clk.textContent = clock(now);
    step.textContent = n ? F[n - 1][3] : "start";
    b1.style.width = pct(Math.min(now, signedAt));
    b1l.style.left = pct(signedAt);
    b1l.style.width = pct(Math.max(0, now - signedAt));
    v1.textContent = n >= END1 ? dur(A.at_s) : clock(now);
    b2.style.width = n > END1 ? pct(R.clean) : "0";
    v2.textContent = n > END1 ? dur(R.clean) : "";
    b3.style.width = n > END1 + 1 ? pct(R.teardown.seconds) : "0";
    v3.textContent = n > END1 + 1 ? dur(R.teardown.seconds) : "";
    ticks.forEach(function (k) { k.style.visibility = n >= END1 || +k.dataset.at <= now ? "" : "hidden"; });
    box.innerHTML = F.slice(Math.max(0, n - SHOW), n).map(function (l) {
      return "<span" + (l[1] ? ' class="' + l[1] + '"' : "") + ">" + esc(l[2]) + "</span>";
    }).join("");
  }
  (function tick() {
    n += 1; draw();
    if (n < F.length) {
      var cls = F[n][1];
      setTimeout(tick, cls === "st" ? 1500 : cls === "ev" || cls === "ok" ? 1300 : n >= END1 ? 1600 : 330);
      return;
    }
    setTimeout(function () { n = 0; draw(); setTimeout(tick, 700); }, 9000);
  })();
})();
