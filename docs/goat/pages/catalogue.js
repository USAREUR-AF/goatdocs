// Copy button; the first screen's slideshow of every page's real first screen; the filter.
// Without JavaScript the first page's capture shows and every entry is listed.
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

  document.querySelectorAll(".filter button").forEach(function (b) {
    b.addEventListener("click", function () {
      var kind = b.dataset.kind;
      document.querySelectorAll(".filter button").forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
      document.querySelectorAll(".plate").forEach(function (p) {
        p.hidden = kind !== "all" && p.dataset.kind !== kind;
      });
    });
  });

  var show = document.getElementById("show"), pic = document.getElementById("show-pic");
  var name = document.getElementById("show-name"), n = document.getElementById("show-n");
  if (!show || typeof PAGES === "undefined") return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  PAGES.forEach(function (p) { new Image().src = "shots/" + p.slug + "-light.jpg"; });
  var i = 0;
  setInterval(function () {
    i = (i + 1) % PAGES.length;
    var p = PAGES[i];
    show.classList.add("fade");
    setTimeout(function () {
      pic.querySelector("source").srcset = "shots/" + p.slug + "-dark.jpg";
      pic.querySelector("img").src = "shots/" + p.slug + "-light.jpg";
      show.href = p.url; name.textContent = p.name; n.textContent = (i + 1) + " / " + PAGES.length;
      show.classList.remove("fade");
    }, 250);
  }, 2600);
})();
