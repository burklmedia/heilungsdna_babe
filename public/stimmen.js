/* Stimmen als Kartenstapel: vorne eine Rückmeldung, dahinter die nächsten leicht versetzt.
   Blättern über die Pfeile, Wischen zur Seite oder Pfeiltasten. Der Text in der vorderen
   Karte bleibt scrollbar, deshalb blättert ein Antippen der Karte bewusst nicht weiter. */
(function () {
  var stapel = document.querySelector(".st-stapel"); if (!stapel) return;
  var karten = [].slice.call(stapel.querySelectorAll(".stimme")), n = karten.length, akt = 0;
  var nav = document.querySelector(".st-nav"), zahl = nav && nav.querySelector(".st-zahl");
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hinweis = document.querySelector(".st-hinweis");
  if (n < 2) { stapel.classList.add("einzeln"); return; }   // eine einzelne Stimme bleibt eine ruhige Karte
  stapel.classList.add("an");
  if (nav) nav.hidden = false; if (hinweis) hinweis.hidden = false;
  // Lage der Karten hinter der vorderen: x, y in px, Drehung in Grad
  var LAGE = [[0, 0, 0], [16, 12, 2.4], [-14, 22, -2], [8, 30, 1.2]];
  function setzen(weg) {
    karten.forEach(function (k, i) {
      var pos = (i - akt + n) % n, l = LAGE[Math.min(pos, 3)];
      k.style.zIndex = String(n - pos);
      k.style.opacity = pos > 3 ? "0" : "1";
      k.style.transform = "translate(" + l[0] + "px," + l[1] + "px) rotate(" + l[2] + "deg)";
      k.classList.toggle("vorn", pos === 0);
      k.setAttribute("aria-hidden", pos === 0 ? "false" : "true");
      k.inert = pos !== 0;
    });
    if (weg != null) {   // die alte vordere Karte fliegt zur Seite und legt sich hinten an
      var k = karten[weg];
      k.style.zIndex = String(n + 1); k.classList.add("vorn");
      k.style.transform = "translate(-112%, -3%) rotate(-11deg)";
      k.style.opacity = "0";
      setTimeout(function () { setzen(); }, reduce ? 0 : 430);
    }
    if (zahl) zahl.textContent = (akt + 1) + " von " + n;
  }
  function weiter() { var alt = akt; akt = (akt + 1) % n; reduce ? setzen() : setzen(alt); }
  function zurueck() { akt = (akt - 1 + n) % n; setzen(); }
  if (nav) {
    nav.querySelector(".st-weiter").addEventListener("click", weiter);
    nav.querySelector(".st-zurueck").addEventListener("click", zurueck);
  }
  stapel.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight") { e.preventDefault(); weiter(); }
    if (e.key === "ArrowLeft") { e.preventDefault(); zurueck(); }
  });
  // Wischen nur, wenn die Bewegung deutlich waagerecht ist (senkrecht scrollt der Text)
  var x0 = null, y0 = null;
  stapel.addEventListener("pointerdown", function (e) { x0 = e.clientX; y0 = e.clientY; });
  stapel.addEventListener("pointerup", function (e) {
    if (x0 == null) return; var dx = e.clientX - x0, dy = e.clientY - y0; x0 = null;
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.5) { dx < 0 ? weiter() : zurueck(); }
  });
  stapel.addEventListener("pointercancel", function () { x0 = null; });
  setzen();
})();
