/* Hero „Sternwarte“: Beim Ankommen geht der Lichtkegel aus der Kuppel an, darin schwebt
   goldener Sternenstaub, in der Kuppelöffnung funkeln Sterne.
   Alle Orte stehen in Anteilen des Fotos (0 bis 1). Das Skript rechnet sie auf den
   sichtbaren Ausschnitt um (object-fit: cover samt object-position).
   Läuft nur, solange der Hero sichtbar ist; bei „Bewegung reduzieren“ ein ruhiges Standbild. */
(function () {
  "use strict";
  var hero = document.querySelector("header.hero");
  var img = hero && hero.querySelector(".scene img");
  if (!hero || !img || !window.HTMLCanvasElement) return;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Lichtkegel als Viereck (oben links, oben rechts, unten rechts, unten links) und Kuppelöffnung als Ellipse
  var ORTE = {
    quer: { kegel: [[0.182, 0.083], [0.302, 0.083], [0.352, 0.883], [0.192, 0.883]], kuppel: [0.26, 0.013, 0.085, 0.075] },
    hoch: { kegel: [[0.42, 0.13], [0.66, 0.13], [0.63, 0.90], [0.37, 0.90]], kuppel: [0.575, 0.04, 0.21, 0.06] }
  };

  var c = document.createElement("canvas");
  c.id = "lichtfeld";
  c.setAttribute("aria-hidden", "true");
  hero.querySelector(".scene").appendChild(c);
  var ctx = c.getContext("2d"), dpr = Math.min(window.devicePixelRatio || 1, 2);
  var W = 0, H = 0, bild = null, staub = [], sterne = [], start = 0, raf = 0, sichtbar = true;

  function rand(a, b) { return a + Math.random() * (b - a); }
  function art() { return /hoch/.test(img.currentSrc || img.src) ? "hoch" : "quer"; }

  // Wo liegt das Foto gerade? (object-fit: cover)
  function ausschnitt() {
    var nw = img.naturalWidth || 2688, nh = img.naturalHeight || 1520;
    var r = img.getBoundingClientRect(), s = Math.max(r.width / nw, r.height / nh);
    var dw = nw * s, dh = nh * s, pos = (getComputedStyle(img).objectPosition || "50% 50%").split(" ");
    var px = parseFloat(pos[0]) / 100, py = parseFloat(pos[1] || "50%") / 100;
    var hr = hero.getBoundingClientRect();
    return { x: r.left - hr.left + (r.width - dw) * (isNaN(px) ? .5 : px), y: r.top - hr.top + (r.height - dh) * (isNaN(py) ? .5 : py), w: dw, h: dh };
  }
  function punkt(u, v) { return [bild.x + u * bild.w, bild.y + v * bild.h]; }
  // Punkt im Kegel: u quer (0 links bis 1 rechts), v längs (0 oben bis 1 unten)
  function imKegel(u, v) {
    var k = ORTE[art()].kegel;
    var lx = k[0][0] + (k[3][0] - k[0][0]) * v, rx = k[1][0] + (k[2][0] - k[1][0]) * v;
    var y = k[0][1] + (k[3][1] - k[0][1]) * v;
    return punkt(lx + (rx - lx) * u, y);
  }

  function saeen() {
    var mobil = W < 760;
    staub = [];
    for (var i = 0; i < (mobil ? 45 : 80); i++) {
      staub.push({ u: Math.random(), v: Math.random(), r: rand(.5, 1.7), a: rand(.25, .85), s: rand(.4, 1.4), p: rand(0, 6.28),
                   dv: rand(.006, .02), gold: Math.random() < .55 });
    }
    sterne = [];
    for (var k = 0; k < (mobil ? 12 : 22); k++) {
      var w = Math.random() * 6.283, d = Math.sqrt(Math.random()) * .92;
      sterne.push({ w: w, d: d, r: rand(.5, 1.4), s: rand(.6, 2.2), p: rand(0, 6.28), funkel: Math.random() < .25 });
    }
  }
  function groesse() {
    var r = hero.getBoundingClientRect();
    W = r.width; H = r.height;
    c.width = Math.round(W * dpr); c.height = Math.round(H * dpr);
    c.style.width = W + "px"; c.style.height = H + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    bild = ausschnitt();
    saeen();
    if (reduce) zeichne(99999);
  }

  function kegelLicht(staerke) {
    var k = ORTE[art()].kegel, a = punkt(k[0][0], k[0][1]), b = punkt(k[1][0], k[1][1]), cc = punkt(k[2][0], k[2][1]), d = punkt(k[3][0], k[3][1]);
    var g = ctx.createLinearGradient(0, a[1], 0, d[1]);
    g.addColorStop(0, "rgba(205,215,255," + (staerke * .55).toFixed(3) + ")");
    g.addColorStop(.55, "rgba(205,215,255," + (staerke * .22).toFixed(3) + ")");
    g.addColorStop(1, "rgba(235,215,170," + (staerke * .08).toFixed(3) + ")");
    ctx.save();
    ctx.globalCompositeOperation = "screen";
    ctx.filter = "blur(" + Math.round(bild.w * .006) + "px)";
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.lineTo(cc[0], cc[1]); ctx.lineTo(d[0], d[1]); ctx.closePath(); ctx.fill();
    ctx.restore();
  }

  function zeichne(t) {
    ctx.clearRect(0, 0, W, H);
    var sek = t / 1000;
    // Licht geht an: kurz kräftiger, dann ruhiges Atmen
    var an = reduce ? 1 : Math.min(1, sek / 1.6);
    var spitze = reduce ? 0 : Math.max(0, 1 - Math.abs(sek - 1.7) / 1.3);
    kegelLicht(.28 * an + .3 * spitze + .05 * Math.sin(sek * .9));
    // Staub sinkt langsam durch den Kegel
    var sicht = reduce ? 1 : Math.min(1, Math.max(0, (sek - .6) / 1.8));
    ctx.save(); ctx.globalCompositeOperation = "screen";
    for (var i = 0; i < staub.length; i++) {
      var s = staub[i];
      if (!reduce) { s.v += s.dv / 60; if (s.v > 1) { s.v = 0; s.u = Math.random(); } }
      var u = s.u + .04 * Math.sin(sek * .4 + s.p);
      var q = imKegel(Math.min(1, Math.max(0, u)), s.v);
      var rand0 = Math.min(1, s.v * 6, (1 - s.v) * 6);
      var a = s.a * sicht * rand0 * (.55 + .45 * Math.sin(sek * s.s + s.p));
      ctx.fillStyle = s.gold ? "rgba(246,222,170," + a.toFixed(3) + ")" : "rgba(225,232,255," + a.toFixed(3) + ")";
      ctx.beginPath(); ctx.arc(q[0], q[1], s.r * (bild.w / 1600 + .4), 0, 6.283); ctx.fill();
    }
    // Sterne in der Kuppelöffnung
    var ku = ORTE[art()].kuppel;
    for (var k = 0; k < sterne.length; k++) {
      var st = sterne[k], p = punkt(ku[0] + Math.cos(st.w) * st.d * ku[2], ku[1] + Math.sin(st.w) * st.d * ku[3]);
      var al = (.35 + .65 * Math.max(0, Math.sin(sek * st.s + st.p))) * an;
      if (p[1] < 0) continue;
      ctx.fillStyle = "rgba(255,246,225," + (al * .9).toFixed(3) + ")";
      ctx.beginPath(); ctx.arc(p[0], p[1], st.r, 0, 6.283); ctx.fill();
      if (st.funkel && al > .75) {
        var g = 4 + 3 * al;
        ctx.strokeStyle = "rgba(255,240,205," + ((al - .75) * 2.4).toFixed(3) + ")"; ctx.lineWidth = .7;
        ctx.beginPath(); ctx.moveTo(p[0] - g, p[1]); ctx.lineTo(p[0] + g, p[1]); ctx.moveTo(p[0], p[1] - g); ctx.lineTo(p[0], p[1] + g); ctx.stroke();
      }
    }
    ctx.restore();
  }

  function lauf(t) {
    raf = 0;
    if (!sichtbar || document.hidden) return;
    if (!start) start = t;
    zeichne(t - start);
    raf = requestAnimationFrame(lauf);
  }
  function los() { if (!raf && !reduce) raf = requestAnimationFrame(lauf); }

  function bereit() {
    groesse();
    if (window.ResizeObserver) new ResizeObserver(groesse).observe(hero); else window.addEventListener("resize", groesse);
    if (window.IntersectionObserver) new IntersectionObserver(function (e) { sichtbar = e[0].isIntersecting; if (sichtbar) los(); }).observe(hero);
    document.addEventListener("visibilitychange", function () { if (!document.hidden) los(); });
    los();
  }
  if (img.complete && img.naturalWidth) bereit(); else img.addEventListener("load", bereit, { once: true });

  /* Film: auf dem Desktop dreht sich die Armillarsphäre (Seedance 2.5, nahtlose Schleife).
     Lädt erst nach dem Lichtauftakt, nicht bei „Bewegung reduzieren“ oder Datensparen, pausiert außer Sicht. */
  var film = hero.querySelector(".hero-film");
  var spar = navigator.connection && (navigator.connection.saveData || /2g/.test(navigator.connection.effectiveType || ""));
  if (film && !reduce && !spar && window.innerWidth > 1100) {
    var starten = function () {
      film.src = (window.innerWidth * (window.devicePixelRatio || 1) >= 1600) ? film.getAttribute("data-src") : film.getAttribute("data-src-klein");
      film.addEventListener("playing", function () { film.classList.add("an"); hero.classList.add("mit-film"); }, { once: true });
      var p = film.play(); if (p && p.catch) p.catch(function () {});
      if (window.IntersectionObserver) new IntersectionObserver(function (e) {
        if (e[0].isIntersecting) { var q = film.play(); if (q && q.catch) q.catch(function () {}); } else film.pause();
      }).observe(hero);
    };
    var spaeter = function () { setTimeout(starten, 2600); };
    if (document.readyState === "complete") spaeter(); else window.addEventListener("load", spaeter, { once: true });
  }
  img.addEventListener("load", function () { if (bild) groesse(); });   // anderes Bild nach Größenwechsel
})();
