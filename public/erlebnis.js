/* Erlebnis-Schicht „Sternwarte“: alles, was sich bewegt und überrascht.
   1. Astrolabium mit dem echten Himmel von jetzt, Goldfäden zu den sechs Ebenen
   2. Beispiel: Karten fallen nacheinander herein
   3. Vorschau nach dem Klick-Moment
   4. Bericht: Sternbild auf dem Deckblatt, Siegel, Elemente, Zahlensiegel, Reiter-Linie
   Ändert keine Berechnung und keine Abläufe. Bei „Bewegung reduzieren“ steht alles still. */
(function () {
  "use strict";
  var H = window.Himmel;
  if (!H) return;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var NS = "http://www.w3.org/2000/svg";
  function $(id) { return document.getElementById(id); }
  function tp(g) { return g + "︎"; }
  function f1(n) { return n.toFixed(1); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function sichtbar(el, fn, opt) {
    if (!el) return;
    if (!("IntersectionObserver" in window)) { fn(); return; }
    var io = new IntersectionObserver(function (e) { e.forEach(function (x) { if (x.isIntersecting) { fn(); io.disconnect(); } }); }, opt || { threshold: .2 });
    io.observe(el);
  }
  // Sternbild zeichnen lassen: erst einsetzen, im nächsten Bild die Klasse setzen
  function sternbildRein(box, index, b, h, opt, verz) {
    if (!box) return;
    box.innerHTML = H.sternbildSVG(index, b, h, opt);
    box.classList.remove("an");
    void box.offsetWidth;
    setTimeout(function () { box.classList.add("an"); }, verz || 30);
  }

  /* ════════ 1. Astrolabium: der Himmel gerade jetzt ════════ */
  (function astrolab() {
    var rad = $("astrolab-rad"), zeile = $("al-zeile"), buehne = $("ebenen-buehne");
    if (!rad || !buehne) return;
    var C = 200, planGlyphen = [];
    // 0° Widder links, gegen den Uhrzeigersinn wie im Horoskop
    function pt(r, lon) { var a = lon * Math.PI / 180; return [C - r * Math.cos(a), C + r * Math.sin(a)]; }

    function mondPfad(cx, cy, r, ph) {
      var el = ph.winkel, rechts = el < 180, sichel = ph.hell < .5, rx = Math.abs(Math.cos(el * Math.PI / 180)) * r;
      var aussen = rechts ? 1 : 0, innen = rechts ? (sichel ? 0 : 1) : (sichel ? 1 : 0);
      return "M" + cx + " " + (cy - r) + " A" + r + " " + r + " 0 0 " + aussen + " " + cx + " " + (cy + r) +
             " A" + f1(rx) + " " + r + " 0 0 " + innen + " " + cx + " " + (cy - r) + " Z";
    }

    function bauen() {
      var jetzt = new Date(), pl = H.planeten(jetzt), ph = H.mondphase(jetzt), s = "", i, a, b;
      s += '<defs><radialGradient id="alKern" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="rgba(226,196,134,.22)"/><stop offset=".55" stop-color="rgba(140,110,200,.08)"/><stop offset="1" stop-color="rgba(20,14,40,0)"/></radialGradient>' +
           '<filter id="alGlow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>';
      s += '<circle cx="200" cy="200" r="198" fill="url(#alKern)"/>';
      // äußerer Kranz aus Punkten außerhalb der Messingfassung, dreht sich langsam
      s += '<g class="al-kranz"><circle cx="200" cy="200" r="226" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="1 7" stroke-linecap="round" opacity=".5"/>';
      for (i = 0; i < 8; i++) { a = pt(226, i * 45 + 22.5); s += '<path d="M' + f1(a[0]) + ' ' + f1(a[1] - 4) + 'l1.2 2.8 2.8 1.2-2.8 1.2-1.2 2.8-1.2-2.8-2.8-1.2 2.8-1.2z" fill="currentColor" opacity=".8"/>'; }
      s += '</g>';
      // Tierkreisband (die Gradskala trägt die Messingfassung)
      s += '<g class="al-skala" stroke="currentColor">';
      s += '<circle cx="200" cy="200" r="174" fill="rgba(16,11,33,.55)" stroke-width="1.1" opacity=".9"/>';
      for (i = 0; i < 360; i += 10) { a = pt(174, i); b = pt(i % 30 === 0 ? 166 : 170, i);
        s += '<line x1="' + f1(a[0]) + '" y1="' + f1(a[1]) + '" x2="' + f1(b[0]) + '" y2="' + f1(b[1]) + '" stroke-width=".7" opacity=".55"/>'; }
      s += '<circle cx="200" cy="200" r="138" fill="none" stroke-width="1" opacity=".7"/><circle cx="200" cy="200" r="74" fill="none" stroke-width=".7" opacity=".4" stroke-dasharray="2 4"/>';
      for (i = 0; i < 12; i++) { a = pt(174, i * 30); b = pt(138, i * 30); s += '<line x1="' + f1(a[0]) + '" y1="' + f1(a[1]) + '" x2="' + f1(b[0]) + '" y2="' + f1(b[1]) + '" stroke-width=".8" opacity=".55"/>'; }
      s += '</g>';
      // Tierkreis
      s += '<g class="al-zeichen">';
      for (i = 0; i < 12; i++) { a = pt(155, i * 30 + 15); s += '<text x="' + f1(a[0]) + '" y="' + f1(a[1] + 5.5) + '" style="--i:' + i + '">' + tp(H.GLYPH[i]) + '</text>'; }
      s += '</g>';
      // Alhidade (Zeiger) mit Lichtpunkt, dreht sich per Skript
      s += '<g class="al-zeiger" id="al-zeiger"><line x1="30" y1="200" x2="370" y2="200" stroke="currentColor" stroke-width=".9" opacity=".55"/>' +
           '<path d="M30 200l7-3v6z M370 200l-7-3v6z" fill="currentColor" opacity=".8"/><circle cx="200" cy="200" r="4" fill="currentColor"/></g>';
      // Planeten: Striche auf dem Ring, Symbole nach innen versetzt, wenn sie sich drängen
      var platz = [], sort = pl.slice().sort(function (x, y) { return x.lon - y.lon; });
      s += '<g class="al-planeten">';
      sort.forEach(function (p, k) {
        var r = 118, n = 0;
        while (n < 5) { var eng = false;
          for (var j = 0; j < platz.length; j++) { var d = Math.abs(((p.lon - platz[j].lon + 540) % 360) - 180); if (d < 9 && Math.abs(platz[j].r - r) < 14) { eng = true; break; } }
          if (!eng) break; r -= 17; n++; }
        platz.push({ lon: p.lon, r: r });
        var t1 = pt(138, p.lon), t2 = pt(129, p.lon), g = pt(r, p.lon), grad = Math.floor(p.lon % 30);
        var gross = p.key === "Sonne" || p.key === "Mond";
        s += '<g class="al-p' + (gross ? " gross" : "") + '" data-lon="' + p.lon.toFixed(2) + '" style="--i:' + k + '"><title>' + p.key + " " + grad + "° " + H.ZEICHEN[H.zeichen(p.lon)] + '</title>' +
             '<circle class="al-halo" cx="' + f1(g[0]) + '" cy="' + f1(g[1]) + '" r="' + (gross ? 17 : 14) + '"/>' +
             '<line x1="' + f1(t1[0]) + '" y1="' + f1(t1[1]) + '" x2="' + f1(t2[0]) + '" y2="' + f1(t2[1]) + '"/>' +
             '<text x="' + f1(g[0]) + '" y="' + f1(g[1] + 6) + '">' + tp(p.sym) + '</text></g>';
      });
      s += '</g>';
      // Mondphase in der Mitte
      s += '<g class="al-mond" filter="url(#alGlow)"><circle cx="200" cy="200" r="27" class="al-mond-grund"/>' +
           (ph.hell > .015 ? '<path d="' + mondPfad(200, 200, 27, ph) + '" class="al-mond-licht"/>' : '') +
           '<circle cx="200" cy="200" r="27" class="al-mond-rand"/></g>';
      var neu = document.createElement("div");
      neu.innerHTML = '<svg viewBox="0 0 400 400" role="img" aria-label="Der Himmel gerade jetzt">' + s + '</svg>';
      var alt = rad.querySelector(":scope > svg");
      if (alt) rad.replaceChild(neu.firstChild, alt); else rad.appendChild(neu.firstChild);
      planGlyphen = [].slice.call(rad.querySelectorAll(".al-p"));

      var so = pl[0], mo = pl[1];
      var phase = ph.name === "Neumond" || ph.name === "Vollmond" ? ph.name : ph.name + ", " + Math.round(ph.hell * 100) + " % beleuchtet";
      if (zeile) zeile.innerHTML = '<span><b>' + tp("☉") + "</b> Sonne " + H.IM[H.zeichen(so.lon)] + '</span><span><b>' + tp("☽") + "</b> Mond " + H.IM[H.zeichen(mo.lon)] + '</span><span>' + phase + "</span>";
    }
    bauen();
    setInterval(bauen, 5 * 60 * 1000);

    // Zeiger dreht sich langsam; Planeten, die er streift, leuchten kurz auf
    var raf = 0, t0 = 0, aktiv = false, zeiger = null;
    function lauf(t) {
      raf = 0;
      if (!aktiv || document.hidden) return;
      if (!t0) t0 = t;
      var w = ((t - t0) / 1000 * 4) % 360;            // 4 Grad pro Sekunde, eine Runde in 90 s
      zeiger = zeiger || $("al-zeiger");
      if (zeiger && zeiger.isConnected) zeiger.setAttribute("transform", "rotate(" + w.toFixed(2) + " 200 200)"); else zeiger = null;
      var e1 = (360 - w) % 360, e2 = (540 - w) % 360;   // Ekliptiklänge unter beiden Zeigerenden
      planGlyphen.forEach(function (g) {
        var lon = +g.getAttribute("data-lon");
        var d = Math.min(Math.abs(((lon - e1 + 540) % 360) - 180), Math.abs(((lon - e2 + 540) % 360) - 180));
        g.style.setProperty("--hell", Math.max(0, 1 - d / 7).toFixed(2));
      });
      raf = requestAnimationFrame(lauf);
    }
    function los() { if (!raf && !reduce && aktiv) raf = requestAnimationFrame(lauf); }
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (e) { aktiv = e[0].isIntersecting; los(); }, { rootMargin: "60px" }).observe(rad);
    } else { aktiv = true; los(); }
    document.addEventListener("visibilitychange", los);

    /* Goldfäden vom Astrolabium zu den Ebenen */
    var svg = $("faeden"), karten = [].slice.call(buehne.querySelectorAll(".pillar"));
    function faeden() {
      if (!svg) return;
      var br = buehne.getBoundingClientRect();
      if (getComputedStyle(svg).display === "none" || !br.width) { svg.innerHTML = ""; return; }
      // Fäden setzen außen an der Messingfassung an (Außenradius 215 von 400 Einheiten)
      var rr = rad.getBoundingClientRect(), cx = rr.left - br.left + rr.width / 2, cy = rr.top - br.top + rr.height / 2, R = rr.width * 215 / 400;
      svg.setAttribute("viewBox", "0 0 " + f1(br.width) + " " + f1(br.height));
      svg.setAttribute("width", br.width); svg.setAttribute("height", br.height);
      var s = '<defs><linearGradient id="fadenL" x1="1" x2="0" y1="0" y2="0"><stop offset="0" stop-color="#f3dca6" stop-opacity=".9"/><stop offset="1" stop-color="#e2c486" stop-opacity=".25"/></linearGradient>' +
              '<linearGradient id="fadenR" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#f3dca6" stop-opacity=".9"/><stop offset="1" stop-color="#e2c486" stop-opacity=".25"/></linearGradient></defs>';
      karten.forEach(function (k, i) {
        var ic = k.querySelector("svg"), ir = (ic || k).getBoundingClientRect();
        var px = ir.left - br.left + ir.width / 2, py = ir.top - br.top + ir.height / 2;
        var dx = px - cx, dy = py - cy, len = Math.hypot(dx, dy), ux = dx / len, uy = dy / len;
        var sx = cx + ux * (R + 4), sy = cy + uy * (R + 4);
        var links = px < cx, ex = px + (links ? 1 : -1) * (ir.width / 2 + 6), ey = py;
        var qx = sx + (ex - sx) * .55, qy = ey;
        var d = "M" + f1(sx) + " " + f1(sy) + " Q" + f1(qx) + " " + f1(qy) + " " + f1(ex) + " " + f1(ey);
        s += '<path class="faden" data-i="' + i + '" d="' + d + '" stroke="url(#faden' + (links ? "L" : "R") + ')" pathLength="1" style="--d:' + (.2 + i * .16).toFixed(2) + 's"/>' +
             '<path class="faden-puls" d="' + d + '" pathLength="1" style="--d:' + (i * .7).toFixed(2) + 's"/>' +
             '<circle class="faden-knoten" cx="' + f1(sx) + '" cy="' + f1(sy) + '" r="2.4" style="--d:' + (.2 + i * .16).toFixed(2) + 's"/>';
      });
      svg.innerHTML = s;
    }
    faeden();
    if (window.ResizeObserver) new ResizeObserver(faeden).observe(buehne); else window.addEventListener("resize", faeden);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(faeden);
    if (!reduce && "IntersectionObserver" in window) buehne.classList.add("bereit");
    sichtbar(buehne, function () { buehne.classList.add("an"); }, { threshold: .25 });
    karten.forEach(function (k, i) {
      k.style.setProperty("--i", i);
      function an(on) { var f = svg && svg.querySelector('.faden[data-i="' + i + '"]'); if (f) f.classList.toggle("hell", on); buehne.classList.toggle("fokus", on); }
      k.addEventListener("mouseenter", function () { an(true); });
      k.addEventListener("mouseleave", function () { an(false); });
    });
  })();

  /* ════════ Schmuck: Tierkreisband (die Zeichen glimmen nacheinander auf) und Tierkreisrad als Wasserzeichen ════════ */
  [].forEach.call(document.querySelectorAll(".tierkreisband"), function (b) {
    b.innerHTML = '<i></i>' + H.GLYPH.map(function (g, i) { return '<span style="--i:' + i + '">' + tp(g) + '</span>'; }).join("") + '<i></i>';
  });
  [].forEach.call(document.querySelectorAll(".wasserrad"), function (w) {
    var s = '<svg viewBox="0 0 400 400"><g class="wr-dreh">', i, a, b;
    s += '<circle cx="200" cy="200" r="196"/><circle cx="200" cy="200" r="190" class="fein"/><circle cx="200" cy="200" r="150"/><circle cx="200" cy="200" r="96" class="fein"/>';
    for (i = 0; i < 72; i++) { a = i * 5 * Math.PI / 180; b = i % 6 === 0 ? 178 : 184; s += '<line x1="' + f1(200 + Math.cos(a) * 190) + '" y1="' + f1(200 + Math.sin(a) * 190) + '" x2="' + f1(200 + Math.cos(a) * b) + '" y2="' + f1(200 + Math.sin(a) * b) + '" class="fein"/>'; }
    for (i = 0; i < 12; i++) {
      a = i * 30 * Math.PI / 180; s += '<line x1="' + f1(200 + Math.cos(a) * 150) + '" y1="' + f1(200 + Math.sin(a) * 150) + '" x2="' + f1(200 + Math.cos(a) * 178) + '" y2="' + f1(200 + Math.sin(a) * 178) + '"/>';
      b = (i * 30 + 15) * Math.PI / 180; s += '<text x="' + f1(200 + Math.cos(b) * 164) + '" y="' + f1(200 + Math.sin(b) * 164 + 6) + '">' + tp(H.GLYPH[i]) + '</text>';
    }
    w.innerHTML = s + '</g></svg>';
  });

  /* Mitlaufender Knopf: am Seitenende ausblenden (Abschluss und Fuß haben eigene Knöpfe) */
  (function () {
    var enden = [].slice.call(document.querySelectorAll("#step1 .final-band, #step1 footer"));
    if (!enden.length || !("IntersectionObserver" in window)) return;
    var an = new Set();
    var io = new IntersectionObserver(function (e) {
      e.forEach(function (x) { if (x.isIntersecting) an.add(x.target); else an.delete(x.target); });
      document.body.classList.toggle("ende-sichtbar", an.size > 0);
    });
    enden.forEach(function (el) { io.observe(el); });
  })();

  /* ════════ 2. Beispiel: Karten fallen nacheinander herein ════════ */
  (function beispiel() {
    var box = $("mcards");
    if (!box || reduce) return;
    box.classList.add("fall");
    sichtbar(box, function () { box.classList.add("in"); }, { threshold: .3 });
  })();

  // Fünf Siegel aus den berechneten Werten (Vorschau und Bericht)
  function siegelHtml(f) {
    var by = {}; (f.positions || []).forEach(function (p) { by[p.key] = p; });
    var sg = [];
    function astro(k, label, pv) { var p = by[k]; if (p && p.signSymbol) sg.push({ tab: "na", pv: "na", g: tp(p.signSymbol), l: label, v: p.sign, glyph: true }); }
    astro("Sonne", "Sonne"); astro("Mond", "Mond"); astro("AC", "Aszendent");
    if (f.hd) sg.push({ tab: "hd", pv: "hd", g: esc(f.hd.profile || "◈"), l: "Human Design", v: f.hd.type_display || f.hd.type, profil: true });
    if (f.numerology) sg.push({ tab: "nu", pv: "nu", g: esc(String(f.numerology.lifepath)), l: "Lebenszahl", v: f.numerology.title, zahl: true });
    return sg.map(function (x, i) {
      return '<button type="button" class="siegel" data-tab="' + x.tab + '" style="--i:' + i + '">' +
        '<span class="siegel-k"><svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="47"/><circle class="s2" cx="50" cy="50" r="41"/></svg>' +
        '<span class="siegel-g' + (x.glyph ? " zeichen" : "") + (x.zahl ? " zahl" : "") + (x.profil ? " profil" : "") + '">' + x.g + '</span></span>' +
        '<span class="siegel-l">' + esc(x.l) + '</span><span class="siegel-v">' + esc(x.v) + '</span></button>';
    }).join("");
  }

  /* ════════ 3. Vorschau nach dem Moment: Sternbild hinter der Begrüßung, Siegel, die die Vorschau umschalten ════════ */
  function vorschau(d) {
    var f = d && d.full; if (!f) return;
    var box = $("greet-sternbild");
    var so = (f.positions || []).filter(function (p) { return p.key === "Sonne"; })[0], i = so ? H.ZEICHEN.indexOf(so.sign) : -1;
    if (box) { if (i >= 0) sternbildRein(box, i, 900, 420, { rand: 40, dauer: 2.2, gross: 1.4 }, 900); else box.innerHTML = ""; }
    var reihe = $("g-siegel");
    if (reihe) {
      reihe.innerHTML = siegelHtml(f);
      reihe.onclick = function (e) {
        var b = e.target.closest(".siegel"); if (!b) return;
        var pill = document.querySelector('#g-preview-body .pv-pill[data-pv="' + b.getAttribute("data-tab") + '"]');
        if (pill) pill.click();
        var pv = $("g-preview"); if (pv) pv.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
      };
    }
  }

  /* ════════ 5. Bericht ════════ */
  var ELEMENT = {
    Feuer:  '<path d="M20 5 L35 31 H5 Z"/>',
    Erde:   '<path d="M20 35 L35 9 H5 Z"/><path d="M9 18 H31"/>',
    Luft:   '<path d="M20 5 L35 31 H5 Z"/><path d="M9 22 H31"/>',
    Wasser: '<path d="M20 35 L35 9 H5 Z"/>'
  };
  var ELEMENT_WORT = { Feuer: "Antrieb und Begeisterung", Erde: "Halt und Umsetzung", Luft: "Gedanken und Austausch", Wasser: "Gefühl und Tiefe" };

  function bericht(d) {
    var f = d && d.full; if (!f) return;
    var by = {}; (f.positions || []).forEach(function (p) { by[p.key] = p; });
    var sonne = by.Sonne, idx = sonne ? H.ZEICHEN.indexOf(sonne.sign) : -1;

    // Deckblatt: das eigene Sternbild hinter dem Namen
    var cover = $("cover-sternbild"), gravur = $("cover-gravur");
    if (cover) { if (idx >= 0) sternbildRein(cover, idx, 900, 470, { rand: 40, dauer: 2.6, gross: 1.6 }, 1400); else cover.innerHTML = ""; }
    // die Figur des Sonnenzeichens als Gravur aus einem alten Sternatlas
    if (gravur) {
      gravur.classList.remove("an");
      if (idx >= 0) { gravur.style.backgroundImage = "url(/bilder/zeichen-" + idx + "-1600.webp)"; setTimeout(function () { gravur.classList.add("an"); }, 200); }
      else gravur.style.backgroundImage = "none";
    }

    // Siegel: Sonne, Mond, Aszendent, Human Design, Lebenszahl. Ein Klick öffnet den Reiter.
    var reihe = $("siegel-reihe");
    if (reihe) {
      reihe.innerHTML = siegelHtml(f);
      reihe.onclick = function (e) {
        var b = e.target.closest(".siegel"); if (!b) return;
        var t = document.querySelector('.rtab[data-rtab="' + b.getAttribute("data-tab") + '"]'); if (t) t.click();
      };
    }

    // Elemente als alchemistische Zeichen mit Säulen (Natalchart-Reiter)
    var bal = null;
    (f.sections || []).forEach(function (s) { if (/Elemente/.test(s.title || "") && s.facts && s.facts.length) bal = s.facts; });
    var na = $("pane-na");
    if (na && bal) {
      var max = 0; bal.forEach(function (x) { max = Math.max(max, +x[1] || 0); });
      var html = '<div class="elemente"><div class="cap2">Deine Elemente</div><div class="el-reihe">' + bal.map(function (x, i) {
        var n = +x[1] || 0, stark = n === max && max > 0;
        return '<div class="el' + (stark ? " stark" : "") + '" style="--h:' + (max ? n / max : 0).toFixed(3) + ';--i:' + i + '">' +
          '<div class="el-saeule"><span></span></div><svg viewBox="0 0 40 40" aria-hidden="true">' + (ELEMENT[x[0]] || "") + '</svg>' +
          '<div class="el-n">' + n + '</div><div class="el-name">' + esc(x[0]) + '</div><div class="el-wort">' + esc(ELEMENT_WORT[x[0]] || "") + '</div></div>';
      }).join("") + '</div></div>';
      var flank = na.querySelector(".graphic-flank");
      if (flank) flank.insertAdjacentHTML("afterend", html); else na.insertAdjacentHTML("afterbegin", html);
    }

    // Zahlensiegel um die Lebenszahl
    var nu = $("pane-nu"), big = nu && nu.querySelector(".num-big");
    if (big && !big.parentNode.classList.contains("num-siegel")) {
      var w = document.createElement("div"); w.className = "num-siegel";
      var st = "", i, a, pts = [];
      for (i = 0; i < 9; i++) { a = (i * 4 % 9) / 9 * 2 * Math.PI - Math.PI / 2; pts.push(f1(100 + Math.cos(a) * 86) + "," + f1(100 + Math.sin(a) * 86)); }
      for (i = 0; i < 9; i++) { a = i / 9 * 2 * Math.PI - Math.PI / 2; st += '<circle cx="' + f1(100 + Math.cos(a) * 86) + '" cy="' + f1(100 + Math.sin(a) * 86) + '" r="2.6"/>'; }
      w.innerHTML = '<svg viewBox="0 0 200 200" aria-hidden="true"><g class="ns-dreh"><circle cx="100" cy="100" r="97" class="ns-punkte"/><circle cx="100" cy="100" r="86" class="ns-ring"/>' +
        '<polygon points="' + pts.join(" ") + '" class="ns-stern" pathLength="1"/>' + st + '</g><circle cx="100" cy="100" r="52" class="ns-innen"/></svg>';
      big.parentNode.insertBefore(w, big); w.appendChild(big);
      big.setAttribute("data-zahl", big.textContent.trim());
    }

    // Planetenkarten kennen ihr Zeichen (für Sternbild und Gravur beim Aufklappen)
    if (na) {
      var karten = na.querySelectorAll(".pcard");
      (f.positions || []).forEach(function (p, k) { var z = H.ZEICHEN.indexOf(p.sign); if (karten[k] && z >= 0) karten[k].setAttribute("data-zeichen", z); });
    }

    // Breite Ansicht: Grafik links (bleibt beim Lesen stehen), Inhalt rechts
    spalten(na, function (el) { return el.classList.contains("graphic-flank") || (el.tagName === "P" && !el.previousElementSibling && !f.geo); });
    spalten($("pane-hd"), function (el) { return el.classList.contains("graphic-flank") || el.classList.contains("glegend"); });
    spalten(document.querySelector("#pane-in .intu"), function (el) { return /^intu-(sketch|eyebrow|script|tag)$/.test(el.className.split(" ")[0]); });
    spalten(document.querySelector("#pane-nu .intu"), function (el) {
      return el.classList.contains("intu-eyebrow") || el.classList.contains("num-siegel") || el.classList.contains("intu-tag") || !!el.querySelector(".num-calc");
    });

    // Übersicht: sechs Karten, die sich beim Hinscrollen umdrehen
    legung(d);
    // Deutung: jedes Kapitel bekommt seine Gravur, die beim Aufklappen erscheint
    kapitelbilder();
    // Intuitionstyp und Elemente: die Element-Gravuren
    elementbilder(f);
    // „Hier anfangen“: drei Bildkacheln statt Knöpfen
    [].forEach.call(document.querySelectorAll("#pane-ov .ov-start-b"), function (b) {
      var z = b.getAttribute("data-start") || "", bild = "";
      if (z === "in" && f.intuition && ELBILD[f.intuition.key]) bild = "/bilder/element-" + ELBILD[f.intuition.key] + ".webp";
      else if (/Entscheidungsweg/.test(z)) bild = "/bilder/kapitel-5.webp";
      else if (/Schwierigkeiten/.test(z)) bild = "/bilder/kapitel-7.webp";
      if (bild && !b.querySelector(".os-bild")) { b.classList.add("mit-bild"); b.insertAdjacentHTML("afterbegin", '<span class="os-bild" style="background-image:url(' + bild + ')"></span>'); }
    });

    // Schlusswort mit Unterschrift
    var schluss = document.querySelector("#pane-de .closing");
    if (schluss && !schluss.querySelector(".unterschrift")) schluss.insertAdjacentHTML("beforeend", '<span class="unterschrift">Von Herzen, Denise</span>');

    // Reiter: Goldlinie gleitet unter den aktiven Reiter
    var track = document.querySelector("#rtabs .rtabs-track");
    if (track && !track.querySelector(".rtab-linie")) {
      var linie = document.createElement("span"); linie.className = "rtab-linie"; track.appendChild(linie);
      var setz = function () {
        var akt = track.querySelector(".rtab.active"); if (!akt) return;
        linie.style.width = akt.offsetWidth + "px"; linie.style.transform = "translateX(" + akt.offsetLeft + "px)";
        var pane = document.querySelector(".rpane.active"); if (pane) neuImReiter(pane);
      };
      if (window.MutationObserver) new MutationObserver(setz).observe(track, { attributes: true, subtree: true, attributeFilter: ["class"] });
      window.addEventListener("resize", setz);
      setTimeout(setz, 60);
    }

    // Kurz nach dem Erscheinen: Sternbild zeichnen, Zahl zählen, Inhalte einblenden
    neuImReiter(document.querySelector(".rpane.active"));
  }

  var HDBILD = { "Generator": "generator", "Manifestierender Generator": "mg", "Manifestor": "manifestor", "Projektor": "projektor", "Reflektor": "reflektor" };
  var ELBILD = { Feuer: "feuer", Wasser: "wasser", Erde: "erde", Luft: "luft" };

  function legung(d) {
    var f = d.full, t = d.teaser || {}, pane = $("pane-ov");
    if (!pane) return;
    var alt = pane.querySelector(".legung"); if (alt) alt.remove();
    var by = {}; (f.positions || []).forEach(function (p) { by[p.key] = p; });
    var k = [];
    function astro(key, titel) {
      var p = by[key]; if (!p) return;
      var z = H.ZEICHEN.indexOf(p.sign);
      k.push({ tab: "na", karte: p.label || key, titel: titel, wert: '<i class="tk-g">' + tp(p.signSymbol) + "</i> " + esc(p.sign),
        zeile: esc(p.deg) + (p.house ? " · Haus " + p.house : ""), text: p.meaning, bild: z >= 0 ? "/bilder/zeichen-" + z + "-800.webp" : "" });
    }
    astro("Sonne", "Deine Sonne"); astro("Mond", "Dein Mond"); astro("AC", "Dein Aszendent");
    if (f.hd) k.push({ tab: "hd", titel: "Dein Human-Design-Typ", wert: esc(f.hd.type_display || f.hd.type), zeile: "Profil " + esc(f.hd.profile),
      text: t.strategy ? "Strategie: " + t.strategy : f.hd.authority, bild: HDBILD[f.hd.type] ? "/bilder/hd-" + HDBILD[f.hd.type] + ".webp" : "" });
    if (f.numerology) k.push({ tab: "nu", titel: "Deine Lebenszahl", zahl: f.numerology.lifepath, wert: esc(f.numerology.title), text: f.numerology.tagline });
    if (f.intuition) k.push({ tab: "in", titel: "Dein Intuitionstyp", wert: esc(f.intuition.archetype), schrift: true, zeile: esc(f.intuition.tagline),
      text: "Mond in " + f.intuition.moon_sign, bild: ELBILD[f.intuition.key] ? "/bilder/element-" + ELBILD[f.intuition.key] + ".webp" : "" });
    var html = '<section class="legung"><div class="legung-kopf"><div class="script-eyebrow">Dein Bauplan auf einen Blick</div>' +
      '<p class="legung-sub">Gelegt aus dem Moment deiner Geburt. Tippe eine Karte an und sie führt dich in die Tiefe.</p></div><div class="legung-reihe">' +
      k.map(function (x, i) {
        var bild = x.zahl ? '<span class="tk-zahlsiegel"><span>' + esc(String(x.zahl)) + '</span></span>' : (x.bild ? '<span class="tk-bild" style="background-image:url(' + x.bild + ')"></span>' : '');
        return '<button type="button" class="tkarte" data-tab="' + x.tab + '"' + (x.karte ? ' data-karte="' + esc(x.karte) + '"' : '') + ' style="--i:' + i + '">' +
          '<span class="tk-dreh"><span class="tk-seite tk-rueck" aria-hidden="true"></span><span class="tk-seite tk-vorn">' + bild +
          '<span class="tk-titel">' + esc(x.titel) + '</span><span class="tk-wert' + (x.schrift ? " schrift" : "") + '">' + x.wert + '</span>' +
          (x.zeile ? '<span class="tk-zeile">' + x.zeile + '</span>' : '') + (x.text ? '<span class="tk-text">' + esc(x.text) + '</span>' : '') +
          '<span class="tk-mehr">Mehr lesen ✦</span></span></span></button>';
      }).join("") + '</div></section>';
    pane.insertAdjacentHTML("afterbegin", html);
    var leg = pane.querySelector(".legung");
    if (reduce) leg.classList.add("an"); else sichtbar(leg, function () { leg.classList.add("an"); }, { threshold: .25 });
    leg.addEventListener("click", function (e) {
      var b = e.target.closest(".tkarte"); if (!b) return;
      var tab = document.querySelector('.rtab[data-rtab="' + b.getAttribute("data-tab") + '"]'); if (tab) tab.click();
      var name = b.getAttribute("data-karte");
      if (name) setTimeout(function () {
        [].some.call(document.querySelectorAll("#pane-na .pcard"), function (c) {
          var pk = c.querySelector(".pk"); if (pk && pk.textContent.trim() === name) { if (!c.classList.contains("open")) c.querySelector(".ph").click(); return true; }
        });
      }, 380);
    });
    // Karten neigen sich zur Maus
    if (!reduce && window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
      leg.addEventListener("mousemove", function (e) {
        var b = e.target.closest(".tkarte"); if (!b) return;
        var r = b.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        b.style.setProperty("--rx", ((.5 - y) * 12).toFixed(1) + "deg"); b.style.setProperty("--ry", ((x - .5) * 14).toFixed(1) + "deg");
        b.style.setProperty("--mx", (x * 100).toFixed(0) + "%"); b.style.setProperty("--my", (y * 100).toFixed(0) + "%");
      });
      leg.addEventListener("mouseout", function (e) {
        var b = e.target.closest(".tkarte"); if (b && !b.contains(e.relatedTarget)) { b.style.setProperty("--rx", "0deg"); b.style.setProperty("--ry", "0deg"); }
      });
    }
  }

  var KAPITEL = [["innerster Kern", 0], ["Human-Design-Typ", 1], ["innere Autorität", 2], ["Profil", 3], ["Zentren", 4], ["Entscheidungsweg", 5],
    ["Stärken", 6], ["Schwierigkeiten", 7], ["Elemente", 8], ["Lebensschwerpunkt", 9], ["inneren Gespräche", 10], ["Intuitionstyp", 11],
    ["Higher Self", 12], ["Lower Self", 13], ["Lebensaufgabe", 14], ["Chiron", 15], ["Tools", 16]];
  function kapitelbilder() {
    [].forEach.call(document.querySelectorAll("#pane-de details.acc"), function (acc) {
      var t = acc.querySelector(".acc-t"), b = acc.querySelector(".acc-b");
      if (!t || !b || b.querySelector(".kap-bild")) return;
      var titel = (t.firstChild && t.firstChild.textContent) || t.textContent, nr = -1;
      KAPITEL.some(function (k) { if (titel.indexOf(k[0]) >= 0) { nr = k[1]; return true; } });
      if (nr >= 0) b.insertAdjacentHTML("afterbegin", '<div class="kap-bild" aria-hidden="true" style="background-image:url(/bilder/kapitel-' + nr + '.webp)"></div>');
    });
  }

  function elementbilder(f) {
    var it = f.intuition;
    var sk = document.querySelector("#pane-in .intu-sketch");
    if (sk && it && ELBILD[it.key] && !sk.querySelector(".el-gravur")) sk.insertAdjacentHTML("afterbegin", '<span class="el-gravur" style="background-image:url(/bilder/element-' + ELBILD[it.key] + '.webp)"></span>');
    [].forEach.call(document.querySelectorAll("#pane-in .itype"), function (x, i) {
      var a = it && it.all && it.all[i], skx = x.querySelector(".itype-sk");
      if (a && skx && ELBILD[a.key] && !skx.querySelector(".el-gravur")) skx.insertAdjacentHTML("afterbegin", '<span class="el-gravur" style="background-image:url(/bilder/element-' + ELBILD[a.key] + '.webp)"></span>');
    });
    [].forEach.call(document.querySelectorAll("#pane-na .el"), function (x) {
      var n = x.querySelector(".el-name"), key = n && ELBILD[n.textContent.trim()];
      if (key && !x.querySelector(".el-gravur")) x.insertAdjacentHTML("afterbegin", '<span class="el-gravur" style="background-image:url(/bilder/element-' + key + '.webp)"></span>');
    });
  }

  function spalten(root, links) {
    if (!root || root.querySelector(":scope > .spalten")) return;
    var kinder = [].slice.call(root.children), w = document.createElement("div"), l = document.createElement("div"), r = document.createElement("div");
    w.className = "spalten"; l.className = "sp-links"; r.className = "sp-rechts";
    kinder.forEach(function (el) { (links(el) ? l : r).appendChild(el); });
    w.appendChild(l); w.appendChild(r); root.appendChild(w); root.classList.add("gespalten");
  }

  /* Aufklappen mit Wirkung: Karte hebt sich, Medaille dreht sich, Licht fährt darüber.
     Planetenkarten zeigen dazu die Gravur ihres Zeichens und ziehen das Sternbild nach. */
  function aufgeklappt(el) {
    if (!el) return;
    if (!reduce) { el.classList.remove("bam"); void el.offsetWidth; el.classList.add("bam"); }
    var z = el.getAttribute("data-zeichen");
    if (z !== null && !el.querySelector(".pc-himmel")) {
      var box = document.createElement("div");
      box.className = "pc-himmel"; box.setAttribute("aria-hidden", "true");
      box.innerHTML = '<div class="pc-gravur" style="background-image:url(/bilder/zeichen-' + z + '-800.webp)"></div><div class="pc-linien"></div>';
      var pin = el.querySelector(".pin") || el;
      pin.appendChild(box); pin.classList.add("mit-himmel");
      sternbildRein(box.querySelector(".pc-linien"), +z, 300, 220, { rand: 18, dauer: 1.6, gross: 1.1 }, 260);
    }
  }
  var bericht3 = $("step3");
  if (bericht3) {
    bericht3.addEventListener("click", function (e) {
      var h = e.target.closest(".pcard .ph"); if (!h) return;
      var card = h.parentNode;
      setTimeout(function () { if (card.classList.contains("open")) aufgeklappt(card); }, 0);
    });
    bericht3.addEventListener("toggle", function (e) {
      var d = e.target; if (d && d.tagName === "DETAILS" && d.open) aufgeklappt(d);
    }, true);
  }

  // Zählt die Lebenszahl hoch, wenn der Reiter erscheint; Karten blenden nacheinander ein
  function neuImReiter(pane) {
    if (!pane) return;
    var jetzt = Date.now();
    if (pane.__erlebnis && jetzt - pane.__erlebnis < 400) return;   // Klassenwechsel kommen paarweise
    pane.__erlebnis = jetzt;
    var big = pane.querySelector(".num-big[data-zahl]");
    if (big && !reduce) {
      var ziel = +big.getAttribute("data-zahl");
      if (ziel > 0 && ziel < 100) {
        var t0 = performance.now(), dauer = 1100;
        (function zaehl(t) { var q = Math.min(1, (t - t0) / dauer), e = 1 - Math.pow(1 - q, 3);
          big.textContent = Math.max(1, Math.round(e * ziel)); if (q < 1) requestAnimationFrame(zaehl); else big.textContent = ziel; })(t0);
      }
    }
    if (reduce || !("IntersectionObserver" in window)) return;
    var el = pane.querySelectorAll(".panel, .pcard, .acc, .facet2, .itype, .numtile, .el, .kv, .numfact, .ov-start, .factrow .f, .ov-fold, .closing");
    var io = new IntersectionObserver(function (e) {
      e.forEach(function (x) {
        if (!x.isIntersecting) return;
        var t = x.target; t.classList.add("auf"); io.unobserve(t);
        setTimeout(function () { t.classList.remove("einblenden", "auf"); }, 1600);   // danach wirken Hover-Effekte ohne Verzögerung
      });
    }, { threshold: .08 });
    var n = 0;
    el.forEach(function (x) { if (x.classList.contains("auf")) return; x.classList.add("einblenden"); x.style.setProperty("--k", Math.min(n++, 10)); io.observe(x); });
  }

  window.Erlebnis = { vorschau: vorschau, bericht: bericht };
  // Falls der Bericht schon vor diesem Skript fertig war
  if (window.__bauplan) bericht(window.__bauplan);
})();
