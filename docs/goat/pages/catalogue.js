// Copy button; the first screen's slideshow of every page's real first screen.
// Without JavaScript the first page's capture shows; every entry is listed either way.
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

  var show = document.getElementById("show"), pic = document.getElementById("show-pic");
  var name = document.getElementById("show-name"), n = document.getElementById("show-n");
  if (!show || typeof PAGES === "undefined") return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  // The name, number and link change only once the new capture has loaded, so the
  // window never shows one page's capture under another page's name.
  var dark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)");
  function shot(p) { return "shots/" + p.slug + (dark && dark.matches ? "-dark" : "-light") + ".jpg"; }
  var i = 0, busy = false;
  setInterval(function () {
    if (busy) return;
    busy = true;
    var next = (i + 1) % PAGES.length, p = PAGES[next], img = new Image();
    img.onload = function () {
      show.classList.add("fade");
      setTimeout(function () {
        // A new <source> and <img>, not new attributes on the old ones: a browser
        // need not choose again between sources whose srcset changed in place.
        pic.innerHTML = '<source media="(prefers-color-scheme: dark)" srcset="shots/' + p.slug +
          '-dark.jpg"><img src="shots/' + p.slug + '-light.jpg" width="1080" height="675" alt="">';
        show.href = p.url; name.textContent = p.name; n.textContent = (next + 1) + " / " + PAGES.length;
        i = next; busy = false;
        show.classList.remove("fade");
      }, 250);
    };
    img.onerror = function () { i = next; busy = false; };
    img.src = shot(p);
  }, 2600);
})();
