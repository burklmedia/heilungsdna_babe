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

  // Fünf Siegel aus den berechneten Werten (Vorschau und Bericht).
  // Mit „rueck“ bekommt jedes Siegel eine Rückseite mit einem Satz (nur in der Vorschau).
  function siegelHtml(f, rueck) {
    var by = {}; (f.positions || []).forEach(function (p) { by[p.key] = p; });
    var sg = [];
    function astro(k, label, pv) { var p = by[k]; if (p && p.signSymbol) sg.push({ k: k, tab: "na", pv: "na", g: tp(p.signSymbol), l: label, v: p.sign, glyph: true }); }
    astro("Sonne", "Sonne"); astro("Mond", "Mond"); astro("AC", "Aszendent");
    if (f.hd) sg.push({ k: "hd", tab: "hd", pv: "hd", g: esc(f.hd.profile || "◈"), l: "Human Design", v: f.hd.type_display || f.hd.type, profil: true });
    if (f.numerology) sg.push({ k: "nu", tab: "nu", pv: "nu", g: esc(String(f.numerology.lifepath)), l: "Lebenszahl", v: f.numerology.title, zahl: true });
    return sg.map(function (x, i) {
      var vorn = '<span class="siegel-k"><svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="47"/><circle class="s2" cx="50" cy="50" r="41"/></svg>' +
        '<span class="siegel-g' + (x.glyph ? " zeichen" : "") + (x.zahl ? " zahl" : "") + (x.profil ? " profil" : "") + '">' + x.g + '</span></span>' +
        '<span class="siegel-l">' + esc(x.l) + '</span><span class="siegel-v">' + esc(x.v) + '</span>';
      var r = rueck && rueck[x.k];
      if (r && r.text) vorn = '<span class="siegel-dreh"><span class="siegel-vorn">' + vorn + '</span><span class="siegel-rueck">' +
        (r.kopf ? '<span class="sr-kopf">' + esc(r.kopf) + '</span>' : '') + '<span class="sr-text">' + esc(r.text) + '</span></span></span>';
      return '<button type="button" class="siegel' + (r && r.text ? " mit-rueck" : "") + '" data-tab="' + x.tab + '" style="--i:' + i + '">' + vorn + '</button>';
    }).join("");
  }

  function satz(s) { s = String(s || "").trim(); if (!s) return ""; return /[.!?…]$/.test(s) ? s : s + "."; }
  function ersterSatz(s) { var m = String(s || "").match(/^[^.!?]*[.!?]/); return m ? m[0].trim() : satz(s); }

  /* ════════ 3. Vorschau nach dem Moment: Kuppel öffnet sich, Geburtshimmel, Siegel mit Rückseite ════════ */
  // Name im Browser-Tab: „Maries Himmel“, „Max’ Bauplan“
  function genitiv(n) { n = String(n || "").trim().split(/\s+/)[0]; if (!n) return ""; return /[sßxz]$/i.test(n) ? n + "\u2019" : n + "s"; }
  function tabTitel(was, d) { var g = genitiv(d && d.birth && d.birth.name); if (g) document.title = g + " " + was + " · Intuition mit Herz"; }

  var letzteVorschau = null;
  function vorschau(d) {
    var f = d && d.full; if (!f) return;
    letzteVorschau = d;
    try { mondGeburt(d); spiegel(d); deckImMail(d); duUndSie(d); } catch (e) {}
    tabTitel("Himmel", d);
    kuppelFilm();
    var box = $("greet-sternbild");
    var so = (f.positions || []).filter(function (p) { return p.key === "Sonne"; })[0], i = so ? H.ZEICHEN.indexOf(so.sign) : -1;
    if (box) { if (i >= 0) sternbildRein(box, i, 900, 420, { rand: 40, dauer: 2.2, gross: 1.4 }, 900); else box.innerHTML = ""; }
    var reihe = $("g-siegel");
    if (reihe) {
      var t = d.teaser || {}, res = {};
      (t.resonance || []).forEach(function (r) { res[r[0]] = r[1]; });
      var nu = f.numerology || {};
      reihe.innerHTML = siegelHtml(f, {
        Sonne: { kopf: "Dein Kern", text: satz(res["Darum geht es in deinem Kern"]) },
        Mond: { kopf: "Das brauchst du", text: satz(res["Das brauchst du im Innersten"]) },
        AC: { kopf: "So wirkst du", text: satz(res["So wirkst du nach außen"]) },
        hd: { kopf: t.authority || (f.hd && f.hd.authority), text: ersterSatz(t.authority_desc) },
        nu: { kopf: nu.tagline, text: satz(nu.keyword) }
      });
      // Mit Maus dreht sich ein Siegel beim Darüberfahren um. Auf dem Handy dreht der erste Tipp,
      // der zweite führt zur passenden Karte in der Vorschau.
      var touch = window.matchMedia && window.matchMedia("(hover: none)").matches;
      reihe.onmouseover = function (e) { if (e.target.closest(".siegel.mit-rueck")) zaehl("siegeldreh"); };
      reihe.onclick = function (e) {
        var b = e.target.closest(".siegel"); if (!b) return;
        if (touch && b.classList.contains("mit-rueck") && !b.classList.contains("umgedreht")) {
          [].forEach.call(reihe.querySelectorAll(".umgedreht"), function (x) { x.classList.remove("umgedreht"); });
          b.classList.add("umgedreht"); clearTimeout(b._zurueck); zaehl("siegeldreh");
          b._zurueck = setTimeout(function () { b.classList.remove("umgedreht"); }, 6000);
          return;
        }
        var karte = document.querySelector('#g-preview-body [data-pv="' + b.getAttribute("data-tab") + '"]');
        if (karte) karte.click();
        var pv = $("g-preview"); if (pv) pv.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
      };
    }
    geburtshimmel(d);
  }

  /* ── Kuppel-Film: der Spalt fährt auf, die Milchstraße kommt herein. Nur ab Tablet-Breite,
     nicht bei „Bewegung reduzieren“ oder Datensparen. Geladen wird schon beim Klick auf
     „Meinen Himmel lesen“, gespielt erst, wenn er bis zum Ende laden konnte. ── */
  var film = null, filmBereit = false;
  function filmLaden() {
    if (film || reduce || window.innerWidth < 781) return;
    var c = navigator.connection;
    if (c && (c.saveData || /(^|-)2g$/.test(c.effectiveType || ""))) return;
    var gross = window.innerWidth >= 1101 && window.innerWidth * (window.devicePixelRatio || 1) >= 1600;
    film = document.createElement("video");
    film.className = "kuppel-film";
    film.muted = true; film.playsInline = true; film.preload = "auto";
    film.setAttribute("muted", ""); film.setAttribute("playsinline", ""); film.setAttribute("aria-hidden", "true");
    film.addEventListener("canplaythrough", function () { filmBereit = true; }, { once: true });
    film.src = "/bilder/kuppel-film-" + (gross ? "1080" : "720") + ".mp4";
    film.load();
  }
  if ($("go1")) $("go1").addEventListener("click", filmLaden);
  function kuppelFilm() {
    var bild = document.querySelector("#glimpse .g-bild");
    if (!film || !filmBereit || !bild || bild.querySelector(".kuppel-film")) return;
    bild.appendChild(film);
    try { film.currentTime = 0; } catch (e) {}
    var p = film.play();
    if (p && p.catch) p.catch(function () { if (film.parentNode) film.parentNode.removeChild(film); });
  }

  /* ── Geburtshimmel: ein Bogen über der Kuppel, darauf Sonne, Mond und Planeten an ihrem Platz
     im Moment der Geburt. Mit Geburtszeit nur der Teil, der über dem Horizont stand (links Osten
     mit dem Aszendenten, rechts Westen). Ohne Geburtszeit der ganze Tierkreis, die Sonne oben. ── */
  var PLANETEN = ["Sonne", "Mond", "Merkur", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptun", "Pluto"];
  var PSYM = { Sonne: "☉", Mond: "☽", Merkur: "☿", Venus: "♀", Mars: "♂", Jupiter: "♃", Saturn: "♄", Uranus: "♅", Neptun: "♆", Pluto: "♇" };
  function laengeAus(p) {
    var z = H.ZEICHEN.indexOf(p.sign); if (z < 0) return null;
    var m = String(p.deg || "").match(/(\d+)\D+(\d+)/);
    return z * 30 + (m ? +m[1] + (+m[2]) / 60 : 15);
  }
  var himmel = null;
  function geburtshimmel(d) {
    var f = d.full, buehne = document.querySelector("#glimpse .g-buehne");
    if (!buehne || !f) return;
    var by = {}; (f.positions || []).forEach(function (p) { by[p.key] = p; });
    var geo = f.geo, mitZeit = !!(geo && typeof geo.dc === "number"), sonne = null, pl = [];
    PLANETEN.forEach(function (n) {
      var p = by[n], lon = null, haus = p && p.house;
      if (geo && geo.planets) geo.planets.forEach(function (g) { if (g.name === n) { lon = g.lon; haus = g.house; } });
      if (lon == null && p) lon = laengeAus(p);
      if (lon == null) return;
      var x = { n: n, lon: lon, p: p, haus: haus };
      if (n === "Sonne") sonne = x;
      pl.push(x);
    });
    if (!pl.length) return;
    function lage(lon) {   // 0 = links/Osten, 1 = rechts/Westen, null = unter dem Horizont
      if (mitZeit) { var dd = ((lon - geo.dc) % 360 + 360) % 360; return dd >= 180 ? null : 1 - dd / 180; }
      return ((((lon - (sonne ? sonne.lon : 0)) % 360) + 540) % 360) / 360;
    }
    pl.forEach(function (x) { x.u = lage(x.lon); });
    var ort = ((d.birth && d.birth.place) || "").split(",")[0].trim();
    himmel = { buehne: buehne, lage: lage, mitZeit: mitZeit,
      oben: pl.filter(function (x) { return x.u != null; }).sort(function (a, b) { return a.u - b.u; }),
      zeile: mitZeit ? "So stand der Himmel " + (ort ? "über " + ort + ", " : "") + "als du geboren wurdest."
                     : "So standen Sonne, Mond und Planeten am Tag deiner Geburt." };
    var gr = buehne.querySelector(".g-greeting"), z = buehne.querySelector(".himmel-zeile");
    if (gr && !z) { z = document.createElement("p"); z.className = "himmel-zeile"; gr.insertBefore(z, gr.firstChild); }
    if (z) { z.textContent = himmel.zeile; z.classList.remove("an"); }
    himmelZeichnen(true);
    if (z) setTimeout(function () { z.classList.add("an"); }, reduce ? 0 : 1700 + himmel.oben.length * 320);
  }
  function himmelZeichnen(animiert) {
    var h = himmel; if (!h) return;
    var b = h.buehne, W = b.clientWidth; if (!W) return;
    h.breite = W;
    var alt = b.querySelector(".geburtshimmel"); if (alt) alt.remove();
    var mobil = W < 700, reihe = $("g-siegel");
    var basis = mobil ? 104 : Math.max(380, (reihe ? reihe.offsetTop : 560) - 30), oben = mobil ? 18 : 34;
    var g = { cx: W / 2, base: basis, ry: basis - oben, rx: mobil ? W * .62 : Math.max(W * .56, 560) };
    function pt(u) { var a = Math.PI * u; return [g.cx - g.rx * Math.cos(a), g.base - g.ry * Math.sin(a)]; }
    function nor(u) { var a = Math.PI * u, nx = -g.ry * Math.cos(a), ny = -g.rx * Math.sin(a), l = Math.hypot(nx, ny) || 1; return [nx / l, ny / l]; }
    var p0 = pt(0), p1 = pt(1), s = "", k;
    s += '<defs><radialGradient id="gh-glut"><stop offset="0" stop-color="#fff6dc" stop-opacity=".95"/><stop offset=".3" stop-color="#f3dca6" stop-opacity=".42"/><stop offset="1" stop-color="#e2c486" stop-opacity="0"/></radialGradient></defs>';
    s += '<path class="gh-bogen" d="M' + f1(p0[0]) + ' ' + f1(p0[1]) + ' A' + f1(g.rx) + ' ' + f1(g.ry) + ' 0 0 1 ' + f1(p1[0]) + ' ' + f1(p1[1]) + '"/>';
    for (k = 0; k < 12; k++) {   // Zeichengrenzen als feine Striche, die Zeichen selbst ganz zart dazwischen
      var ug = h.lage(k * 30), um = h.lage(k * 30 + 15);
      if (ug != null) { var q = pt(ug), n = nor(ug); s += '<line class="gh-strich" x1="' + f1(q[0] - n[0] * 5) + '" y1="' + f1(q[1] - n[1] * 5) + '" x2="' + f1(q[0] + n[0] * 5) + '" y2="' + f1(q[1] + n[1] * 5) + '"/>'; }
      if (um != null && !mobil) { var q2 = pt(um), n2 = nor(um); s += '<text class="gh-zeichen" x="' + f1(q2[0] - n2[0] * 17) + '" y="' + f1(q2[1] - n2[1] * 17 + 4) + '">' + tp(H.GLYPH[k]) + '</text>'; }
    }
    var letzt = -1e9, innen = false, bogenlaenge = Math.PI * (g.rx + g.ry) / 2;
    h.oben.forEach(function (x, i) {
      var q = pt(x.u), n = nor(x.u), pos = x.u * bogenlaenge;
      innen = (pos - letzt < (mobil ? 22 : 30)) ? !innen : false; letzt = pos;
      var abst = innen ? -20 : (mobil ? 16 : 21), gross = x.n === "Sonne" ? 1.5 : x.n === "Mond" ? 1.25 : 1;
      var tip = x.n + (x.p ? " in " + x.p.sign + " " + x.p.deg : "") + (h.mitZeit && x.haus ? " · " + x.haus + ". Haus" : "");
      s += '<g class="gh-p' + (x.n === "Sonne" ? " sonne" : "") + '" data-tip="' + esc(tip) + '" style="--d:' + f1(1.5 + i * .32) + 's" transform="translate(' + f1(q[0]) + ' ' + f1(q[1]) + ')">' +
        '<circle class="gh-halo" r="' + f1(17 * gross) + '" fill="url(#gh-glut)"/><circle class="gh-blitz" r="' + f1(8 * gross) + '"/>' +
        '<circle class="gh-kern" r="' + f1(2.6 * gross) + '"/>' +
        '<text class="gh-g" x="' + f1(n[0] * abst) + '" y="' + f1(n[1] * abst + 6) + '">' + tp(PSYM[x.n]) + '</text>' +
        '<circle class="gh-fang" r="20"/></g>';
    });
    var H2 = basis + 30;
    b.insertAdjacentHTML("afterbegin", '<svg class="geburtshimmel' + (animiert && !reduce ? "" : " fertig") + '" width="' + W + '" height="' + H2 + '" viewBox="0 0 ' + W + ' ' + H2 + '" aria-hidden="true">' + s + '</svg>');
    var svg = b.querySelector(".geburtshimmel"), bogen = svg.querySelector(".gh-bogen");
    if (animiert && !reduce && bogen.getTotalLength) {
      var L = bogen.getTotalLength();
      bogen.style.strokeDasharray = L; bogen.style.strokeDashoffset = L;
      requestAnimationFrame(function () { requestAnimationFrame(function () {
        bogen.style.transition = "stroke-dashoffset 2.6s cubic-bezier(.4,.1,.2,1) .5s"; bogen.style.strokeDashoffset = 0; svg.classList.add("an");
      }); });
    }
    // Tipp-Fenster: Planet, Zeichen, Grad und Haus
    var tipp = b.querySelector(".gh-tipp");
    if (!tipp) { tipp = document.createElement("div"); tipp.className = "gh-tipp"; tipp.setAttribute("role", "status"); b.appendChild(tipp); }
    function zeig(el) {
      if (!el) { tipp.classList.remove("an"); return; }
      var r = el.getBoundingClientRect(), rb = b.getBoundingClientRect();
      tipp.textContent = el.getAttribute("data-tip"); zaehl("himmelpunkt");
      tipp.style.left = (r.left + r.width / 2 - rb.left) + "px"; tipp.style.top = (r.top - rb.top - 8) + "px";
      tipp.classList.add("an");
    }
    svg.addEventListener("pointerover", function (e) { var p = e.target.closest(".gh-p"); if (p) zeig(p); });
    svg.addEventListener("pointerout", function (e) { if (e.target.closest(".gh-p")) zeig(null); });
    svg.addEventListener("click", function (e) { var p = e.target.closest(".gh-p"); zeig(p); if (p) { clearTimeout(tipp._t); tipp._t = setTimeout(function () { zeig(null); }, 3500); } });
  }
  var himmelUhr = 0;
  window.addEventListener("resize", function () {
    clearTimeout(himmelUhr);
    himmelUhr = setTimeout(function () { if (himmel && himmel.buehne.clientWidth && himmel.buehne.clientWidth !== himmel.breite) himmelZeichnen(false); }, 200);
  });

  /* ── Am Ende des Berichts: das echte PDF-Deckblatt als Vorschau, schräg gestellt, mit Knopf ── */
  function pdfKarte(d, idx) {
    var f = d.full, note = $("note"), alt = document.querySelector(".pdf-karte");
    if (alt) alt.remove();
    if (!note || !$("pdfbtn")) return;
    var by = {}; (f.positions || []).forEach(function (p) { by[p.key] = p; });
    var ringe = ["Sonne", "Mond", "AC"].map(function (k) { return by[k] && by[k].signSymbol ? tp(by[k].signSymbol) : ""; });
    ringe.push(f.hd ? esc(f.hd.profile || "") : ""); ringe.push(f.numerology ? esc(String(f.numerology.lifepath)) : "");
    var name = (d.birth && d.birth.name) || "", b = d.birth || {}, m = String(b.date || "").match(/^(\d{4})-(\d{2})-(\d{2})/);
    var geburt = m ? [m[3] + "." + m[2] + "." + m[1], b.time && b.time !== "unbekannt" ? b.time + " Uhr" : "", String(b.place || "").split(",")[0]].filter(Boolean).join(" · ") : "";
    var html = '<section class="pdf-karte"><div class="pk-buehne" aria-hidden="true"><div class="pk-deck" style="background-image:url(/bilder/deckblatt-' + (idx >= 0 ? idx : "neutral") + '-480.webp)">' +
      '<div class="pk-titel">Dein kosmischer Bauplan</div>' + (name ? '<div class="pk-name">' + esc(name) + '</div>' : '') + (geburt ? '<div class="pk-geburt">' + esc(geburt) + '</div>' : '') +
      '<div class="pk-ringe">' + ringe.filter(Boolean).map(function (g) { return "<i>" + g + "</i>"; }).join("") + '</div>' +
      '<div class="pk-marke">Intuition mit Herz</div></div></div>' +
      '<div class="pk-text"><div class="script-eyebrow">Dein Bauplan zum Aufheben</div>' +
      '<p>Alle Kapitel in einer PDF, rund 40 Seiten mit deinem Deckblatt. Zum Ausdrucken, Wiederlesen und Weitergeben an dich selbst in ein paar Monaten.</p>' +
      '<div class="pk-knoepfe"><button class="btn pk-pdf" type="button" style="width:auto">Als PDF speichern ↓</button>' +
      '<button class="btn btn-ghost pk-story" type="button" style="width:auto">Als Story teilen ✦</button>' +
      (ersterBesuch ? '' : '<button class="btn btn-ghost pk-hintergrund" type="button" style="width:auto">Als Handy-Hintergrund ✦</button>') + '</div>' +
      '<p class="pk-hinweis">Story-Bild und Hintergrund zeigen deinen Namen und deine Zeichen. Geburtsdatum, Zeit und Ort bleiben bei dir.</p></div></section>';
    note.insertAdjacentHTML("beforebegin", html);
    var karte = document.querySelector(".pdf-karte");
    karte.querySelector(".pk-pdf").addEventListener("click", function () { zaehl("deckblatt"); $("pdfbtn").click(); });
    karte.querySelector(".pk-buehne").addEventListener("click", function () { zaehl("deckblatt"); $("pdfbtn").click(); });
    karte.querySelector(".pk-story").addEventListener("click", function () { storyTeilen(d, this); });
    var hg = karte.querySelector(".pk-hintergrund"); if (hg) hg.addEventListener("click", function () { hintergrundTeilen(d, this); });
    if (reduce) karte.classList.add("an"); else sichtbar(karte, function () { karte.classList.add("an"); }, { threshold: .3 });
  }

  /* ── Anonyme Zähler wie auf der Startseite: je Sitzung einmal, keine Cookies, keine Namen ── */
  function zaehl(ev) {
    try {
      if (sessionStorage.getItem("imh_ev_" + ev)) return;
      sessionStorage.setItem("imh_ev_" + ev, "1");
      var b = JSON.stringify({ e: ev });
      if (navigator.sendBeacon) navigator.sendBeacon("/api/track", b); else fetch("/api/track", { method: "POST", body: b, keepalive: true });
    } catch (e) {}
  }
  // Schlüssel je Bauplan auf diesem Gerät: nur eine Prüfzahl, keine Geburtsdaten im Klartext
  function bauplanSchluessel(d) {
    var b = d.birth || {}, s = [b.date, b.time, b.place, b.name].join("|"), h = 5381;
    for (var i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
    return (h >>> 0).toString(36);
  }
  function mondHeute() {
    var jetzt = new Date(), T = H._T(jetzt), ph = H.mondphase(jetzt);
    return { zeichen: H.zeichen(H._mond(T)), phase: ph.name.charAt(0).toUpperCase() + ph.name.slice(1) };
  }

  /* ── Bericht: Willkommen zurück und der Himmel von heute, bezogen auf den eigenen Bauplan ── */
  function heuteImBericht(d) {
    var f = d.full, kopf = document.querySelector("#step3 .report-head"), gruss = $("a-greeting");
    if (!kopf || !gruss) return;
    var schl = bauplanSchluessel(d), besuche = 0;
    try { besuche = +(localStorage.getItem("imh_besuch_" + schl) || 0); localStorage.setItem("imh_besuch_" + schl, String(besuche + 1)); } catch (e) {}
    var name = (d.birth && d.birth.name) || "";
    if (besuche >= 1) {
      gruss.textContent = (name ? "Schön, dass du wieder da bist, " + name + ". " : "Schön, dass du wieder da bist. ") + "Lies einfach dort weiter, wo es dich gerade hinzieht.";
      zaehl("zurueck");
    }
    var by = {}; (f.positions || []).forEach(function (p) { by[p.key] = p; });
    var m = mondHeute(), zus = "";
    function zi(k) { return by[k] ? H.ZEICHEN.indexOf(by[k].sign) : -1; }
    if (m.zeichen === zi("Sonne")) zus = " Der Mond steht heute in deinem Sonnenzeichen.";
    else if (m.zeichen === zi("Mond")) zus = " Der Mond steht heute im selben Zeichen wie in deiner Geburtsstunde.";
    else if (m.zeichen === zi("AC")) zus = " Der Mond steht heute in deinem Aszendenten.";
    var alt = kopf.querySelector(".report-heute"); if (alt) alt.remove();
    gruss.insertAdjacentHTML("afterend", '<p class="report-heute"><span class="hh-mond">' + tp("☽") + '</span>Der Himmel heute: <b>' + esc(m.phase) + " " + esc(H.IM[m.zeichen]) + "</b>." + esc(zus) + "</p>");
  }

  /* ── Bericht: ein persönlicher Brief von Denise je Sonnenzeichen ganz oben (seit 11.10.2026) ── */
  var BRIEF_ZEICHEN = [
    "Du bist oft die Erste, die losgeht. Die, die anpackt, wenn andere noch überlegen. Das kostet Kraft, und selten fragt jemand, wie es dir dabei geht. Hier darfst du einmal stehen bleiben. Dein Bauplan zeigt dir, wohin dein Feuer wirklich will und wo du es verschenkst, nur weil sonst keiner anfängt. Lies dich in Ruhe. Hier gibt es nichts zu gewinnen.",
    "Du spürst die Welt mit dem Körper. Ein warmes Essen, gute Hände, ein Ort, an dem du ankommen kannst. Und genau deshalb hältst du oft länger fest, als dir guttut, weil Loslassen sich unsicher anfühlt. Dein Bauplan zeigt dir, was dir wirklich Halt gibt. Nimm dir einen Tee und lies langsam. Du bist hier sicher.",
    "In deinem Kopf ist immer etwas los. Gedanken, Ideen, Gespräche, drei Fragen gleichzeitig. Das ist lebendig und manchmal ganz schön laut. Auf den nächsten Seiten darf es einmal still werden. Such dir eine Stelle, die dich ruft, und bleib dort. Dein Bauch kennt die Antwort oft schneller als dein Kopf.",
    "Du merkst sofort, wie es den anderen geht. Oft, bevor sie es selbst wissen. Und während du für alle da bist, wird es bei dir ganz leise. Dieser Bauplan ist nur für dich. Hier geht es einmal ganz um dich. Lies mit der Hand auf dem Herzen, wenn du magst. Alles, was du hier über dich liest, war schon immer da.",
    "Du bringst Licht in einen Raum. Das merken andere sofort, auch wenn du dich selbst oft kleiner machst, damit sich niemand übergangen fühlt. Hier darfst du groß sein. Dein Bauplan zeigt dir, wo dein Leuchten zu Hause ist und wann du es dir selbst verbietest. Lies ihn wie einen Brief an dich. Er ist einer.",
    "Ich weiß, du willst es richtig machen. Auch beim Lesen. Jede Seite gründlich, nichts übersehen. Diesmal darfst du es dir leichter machen. Hier wird nichts bewertet. Nimm dir die Stellen, die sich stimmig anfühlen, den Rest darfst du liegen lassen. Du bist auch ohne Perfektion genug.",
    "Du spürst, was jeder im Raum braucht, und suchst den Weg, der für alle passt. Dabei fragst du dich selten, was eigentlich du willst. Dein Bauplan stellt dir genau diese Frage. Ganz leise, ohne Druck. Lies ihn, als würdest du dir selbst zuhören. Deine Antwort darf auch dann gelten, wenn sie nicht allen gefällt.",
    "Du gehst in die Tiefe. Oberflächliches langweilt dich, halbe Wahrheiten spürst du sofort. Und du zeigst nur wenigen, was wirklich in dir vorgeht. Diese Seiten gehören nur dir, niemand schaut mit. Lies sie mit derselben Ehrlichkeit, mit der du andere durchschaust. Du wirst Dinge finden, die du längst geahnt hast.",
    "Du willst wissen, wohin dein Weg führt. Nach vorne schauen, weiterziehen, Sinn finden. Bevor du losgehst, schau einmal hierher. Dein Bauplan ist eine Landkarte von dir selbst, und die größte Reise beginnt oft genau hier. Lies mit Neugier und offenem Herzen. Was sich nach Freiheit anfühlt, darfst du dir merken.",
    "Du trägst viel. Verantwortung, Pläne, Erwartungen, oft auch die von anderen. Und du machst das so gut, dass kaum jemand sieht, wie schwer es manchmal ist. Für diese Seiten darfst du alles absetzen. Hier gibt es nichts zu leisten. Lies dich, als wärst du jemand, den du sehr gern hast. Du bist es.",
    "Du denkst anders, und das weißt du. Oft fühlst du dich deshalb ein bisschen fremd unter den anderen. Dein Bauplan zeigt dir, dass genau diese Eigenart zu dir gehört. Hier gibt es keine Schublade für dich. Lies frei, spring hin und her, wie es dir gefällt. Dein Weg ist eigen. Er darf es bleiben.",
    "Du fühlst so viel. Stimmungen, Zwischentöne, das, was ungesagt im Raum liegt. Oft weißt du kaum noch, was davon deins ist. Dein Bauplan hilft dir, dich selbst wieder herauszuhören. Lies ihn langsam, vielleicht abends, wenn es ruhig wird. Deine Feinfühligkeit ist eine Gabe. Hier darf sie einfach sein."
    ];
  // Geschlecht aus dem Formular (wie in der PDF): m, f oder n (divers / keine Angabe)
  function geschlecht(d) {
    var g = String((d && d.birth && d.birth.gender) || "").toLowerCase();
    return /^(m|männlich|maennlich|male)$/.test(g) ? "m" : /^(f|w|weiblich|female)$/.test(g) ? "f" : "n";
  }
  function anrede(d) { var g = geschlecht(d); return g === "m" ? "Lieber " : g === "f" ? "Liebe " : "Hallo "; }
  // Die Texte sind für Frauen geschrieben; für Männer und neutral werden die wenigen weiblichen Stellen getauscht
  var GENDERN = {
    m: [["die Erste, die losgeht. Die, die anpackt", "der Erste, der losgeht. Der, der anpackt"], ["als Erste,", "als Erster,"]],
    n: [["Du bist oft die Erste, die losgeht. Die, die anpackt, wenn", "Du gehst oft als Erstes los und packst an, wenn"],
        ["Du spürst oft als Erste, wann", "Du spürst oft früher als andere, wann"]]
  };
  function gendern(text, d) {
    var g = geschlecht(d), t = String(text || "");
    (GENDERN[g] || []).forEach(function (x) { t = t.split(x[0]).join(x[1]); });
    return t;
  }
  function zeichenBrief(d) {
    var f = d.full, kopf = document.querySelector("#step3 .report-head"); if (!kopf || !f) return;
    var alt = document.querySelector(".zeichen-brief"); if (alt) alt.remove();
    var so = (f.positions || []).filter(function (p) { return p.key === "Sonne"; })[0], i = so ? H.ZEICHEN.indexOf(so.sign) : -1;
    if (i < 0) return;
    var name = (d.birth && d.birth.name) || "";
    kopf.insertAdjacentHTML("afterend", '<section class="zeichen-brief"><span class="zb-zeichen" aria-hidden="true">' + tp(H.GLYPH[i]) + '</span>' +
      '<p class="zb-anrede">' + (name ? anrede(d) + esc(name) + "," : "Für dich,") + '</p><p class="zb-text">' + esc(gendern(BRIEF_ZEICHEN[i], d)) + '</p>' +
      '<p class="zb-gruss">Von Herzen, <span>Denise</span></p></section>');
  }

  /* ── Bericht: „Heute für dich“, durch welches Haus der Mond heute wandert (Ganzzeichen ab dem Aszendenten) ── */
  function heuteFuerDich(d) {
    var f = d.full, zeile = document.querySelector("#step3 .report-heute"); if (!zeile || !f) return;
    var ac = (f.positions || []).filter(function (p) { return p.key === "AC"; })[0], ai = ac ? H.ZEICHEN.indexOf(ac.sign) : -1;
    if (ai < 0 || !f.houses) return;
    var m = mondHeute(), haus = ((m.zeichen - ai + 12) % 12) + 1, h = f.houses.filter(function (x) { return x.nr === haus; })[0];
    if (!h) return;
    var alt = document.querySelector(".report-fuer-dich"); if (alt) alt.remove();
    zeile.insertAdjacentHTML("afterend", '<p class="report-fuer-dich">Für dich heute: Der Mond wandert durch dein ' + haus + '. Haus. Das berührt ' + esc(h.meaning) + '.</p>');
  }

  /* ── Bericht als App auf dem Startbildschirm: kurze Anleitung je nach Gerät (nur am Handy, nicht in der App selbst) ── */
  function alsApp() {
    var ua = navigator.userAgent || "", standalone = (window.matchMedia && window.matchMedia("(display-mode: standalone)").matches) || navigator.standalone;
    if (standalone) { zaehl("app_start"); return null; }
    if (ersterBesuch) return null;
    var ios = /iPhone|iPad|iPod/.test(ua), android = /Android/.test(ua), inApp = /Instagram|FBAN|FBAV|FB_IAB/.test(ua);
    if (!ios && !android) return null;
    var schritte = inApp ? "Öffne deinen Bauplan zuerst im Browser: oben rechts auf die drei Punkte tippen und „Im Browser öffnen“ wählen. Dann geht es von dort weiter."
      : ios ? "Tippe unten in Safari auf das Teilen-Symbol (das Quadrat mit dem Pfeil nach oben) und dann auf „Zum Home-Bildschirm“."
      : "Tippe oben rechts auf die drei Punkte und dann auf „Zum Startbildschirm hinzufügen“.";
    return '<div class="wk wk-app"><span class="wk-titel">Dein Bauplan als App</span><span class="wk-text">Leg ihn dir auf deinen Startbildschirm. Dann ist er mit einem Tippen da, und jeden Tag wartet „Heute für dich“ auf dich.</span>' +
      '<details class="app-hilfe"><summary class="wk-mehr">So geht’s ✦</summary><p>' + schritte + '</p></details></div>';
  }

  // Sätze aus einem Text (ohne Lookbehind, alte iPhones); satzAus überspringt verbotene Satzanfänge
  function saetze(text) { return (String(text || "").match(/[^.!?]+[.!?]+(?:\s|$)/g) || []).map(function (x) { return x.trim(); }); }
  function satzAus(text, ab) {
    var s = saetze(text);
    for (var i = ab || 0; i < s.length; i++) if (!/^(Vielleicht|Manchmal|Stell dir vor)\b/.test(s[i])) return s[i];
    return s[0] || "";
  }
  /* ── Bauplan anhören: Lea liest ihn in rund zwei Minuten vor (/api/hoeren). Das Gerät behält die Aufnahme in IndexedDB. ── */
  function audioSpeicher(art, schl, wert) {
    return new Promise(function (ok) {
      try {
        var r = indexedDB.open("imh_bauplan", 1);
        r.onupgradeneeded = function () { r.result.createObjectStore("audio"); };
        r.onerror = function () { ok(null); };
        r.onsuccess = function () {
          try {
            var tx = r.result.transaction("audio", art === "lesen" ? "readonly" : "readwrite"), st = tx.objectStore("audio");
            var q = art === "lesen" ? st.get(schl) : st.put(wert, schl);
            q.onsuccess = function () { ok(art === "lesen" ? q.result || null : true); }; q.onerror = function () { ok(null); };
          } catch (e) { ok(null); }
        };
      } catch (e) { ok(null); }
    });
  }
  function anhoeren(d, knopf) {
    var dParam = ""; try { dParam = new URLSearchParams(location.search).get("d") || ""; } catch (e) {}
    var box = document.querySelector(".hoeren-box"), info = box.querySelector(".hb-info"), audio = box.querySelector("audio");
    if (audio.src) { audio.play(); return; }
    var schl = "lea_" + bauplanSchluessel(d), alt = knopf.innerHTML;
    knopf.disabled = true; knopf.innerHTML = "Lea liest sich ein…"; info.textContent = "";
    audioSpeicher("lesen", schl).then(function (blob) {
      if (blob) return blob;
      return fetch("/api/hoeren", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ d: dParam }) })
        .then(function (r) {
          if (r.ok && /audio/.test(r.headers.get("content-type") || "")) return r.blob().then(function (b) { audioSpeicher("schreiben", schl, b); return b; });
          return r.json().catch(function () { return {}; }).then(function (j) { throw new Error(j.message || "Das Vorlesen klappt gerade nicht. Bitte versuch es später noch einmal."); });
        });
    }).then(function (blob) {
      knopf.disabled = false; knopf.innerHTML = alt;
      audio.src = URL.createObjectURL(blob); audio.hidden = false; box.classList.add("an");
      zaehl("hoeren"); var p = audio.play(); if (p && p.catch) p.catch(function () {});
    }).catch(function (e) { knopf.disabled = false; knopf.innerHTML = alt; info.textContent = e.message; });
  }
  // Bauplan anhören: Knopf oben in der Leiste neben „Als PDF speichern“, Player klappt darunter auf (Story seit 11.10.2026 entfernt)
  function hoerenVorbereiten(d) {
    var leiste = document.querySelector("#step3 .bericht-leiste"), pdf = $("pdfbtn"); if (!leiste || !pdf) return;
    var hatD = false; try { hatD = !!new URLSearchParams(location.search).get("d"); } catch (e) {}
    if (!hatD || document.querySelector(".hoeren-box")) return;
    pdf.insertAdjacentHTML("afterend", '<button class="btn btn-ghost hb-oben" style="width:auto;margin:0" type="button"><span aria-hidden="true">♪</span> Bauplan anhören</button>');
    leiste.insertAdjacentHTML("afterend", '<div class="hoeren-box" hidden><audio controls preload="none" hidden></audio>' +
      '<p class="hb-klein">Lea liest dir das Wichtigste in rund zwei Minuten vor. Eine KI-Stimme.</p><p class="hb-info" aria-live="polite"></p></div>');
    var hk = leiste.querySelector(".hb-oben");
    hk.addEventListener("click", function () { document.querySelector(".hoeren-box").hidden = false; anhoeren(d, hk); });
  }

  /* ── Aha-Momente in der Vorschau (seit 11.10.2026) ── */
  // Mondphase bei der Geburt, als Ortszeit Mitteleuropas gerechnet (die Grenze zwischen zwei Phasen verschiebt sich um Minuten, nicht um Tage)
  var MOND_BEI = { "Neumond": "bei Neumond", "zunehmende Mondsichel": "bei zunehmender Mondsichel", "zunehmender Halbmond": "bei zunehmendem Halbmond",
    "zunehmender Mond": "bei zunehmendem Mond", "Vollmond": "bei Vollmond", "abnehmender Mond": "bei abnehmendem Mond",
    "abnehmender Halbmond": "bei abnehmendem Halbmond", "abnehmende Mondsichel": "bei abnehmender Mondsichel" };
  var MOND_SATZ = { "Neumond": "Ein Anfang wohnt in dir. Du spürst oft als Erste, wann etwas Neues beginnen will.",
    "zunehmende Mondsichel": "Du wächst am liebsten Schritt für Schritt, mit Mut und einer leisen Neugier.",
    "zunehmender Halbmond": "In dir steckt Tatkraft. Wenn dir etwas wichtig ist, gehst du los, auch gegen Widerstand.",
    "zunehmender Mond": "Du feilst gern, bis es stimmt, und gibst den Dingen die Zeit, die sie zum Reifen brauchen.",
    "Vollmond": "Bei dir zeigt sich vieles deutlich. Gefühle, Gedanken, Wahrheiten: Du machst sichtbar, was andere übersehen.",
    "abnehmender Mond": "Du gibst gern weiter, was du verstanden hast. Andere lernen an deiner Erfahrung.",
    "abnehmender Halbmond": "Du spürst, wann etwas zu Ende gehen darf, und schaffst damit Platz für Neues.",
    "abnehmende Mondsichel": "In dir wohnt eine stille Weisheit. Rückzug ist für dich eine Kraftquelle." };
  function mondGeburt(d) {
    var b = d.birth || {}, m = String(b.date || "").match(/^(\d{4})-(\d{2})-(\d{2})/), z = String(b.time || "12:00").match(/^(\d{1,2}):(\d{2})/);
    var lead = $("g-lead"); if (!m || !lead || !H.mondphase) return;
    var utc = Date.UTC(+m[1], +m[2] - 1, +m[3], z ? +z[1] : 12, z ? +z[2] : 0) - 3600000;
    var ph = H.mondphase(new Date(utc)), alt = document.querySelector(".g-mond"); if (alt) alt.remove();
    if (!MOND_BEI[ph.name]) return;
    lead.insertAdjacentHTML("afterend", '<p class="g-mond"><span class="gm-mond" aria-hidden="true" style="--hell:' + ph.hell.toFixed(2) + '"></span>' +
      '<span>Du bist <b>' + esc(MOND_BEI[ph.name]) + '</b> geboren. ' + esc(gendern(MOND_SATZ[ph.name], d)) + '</span></p>');
  }
  // „Erkennst du dich?“: drei Sätze aus „Deine größten Schwierigkeiten“ („Woran du sie erkennst“), zum Antippen
  function spiegel(d) {
    // Unter den Symbolen, vor Vorschau und Mailkarte (nicht im Raster, sonst rutscht die Mailkarte nach unten)
    var f = d.full, ziel = document.querySelector("#glimpse .glimpse-cols"); if (!ziel) return;
    var alt = document.querySelector(".spiegel"); if (alt) alt.remove();
    var sch = (f.sections || []).filter(function (s) { return /Schwierigkeiten/.test(s.title || "") && s.blocks; })[0];
    if (!sch) return;
    var saetze = sch.blocks.slice(0, 3).map(function (b) {
      var teil = (b.parts || []).filter(function (p) { return /erkennst/.test(p[0] || ""); })[0];
      return teil ? satzAus(teil[1], 0) : "";
    }).filter(Boolean);
    if (saetze.length < 2) return;
    ziel.insertAdjacentHTML("beforebegin", '<section class="spiegel"><div class="script-eyebrow">Erkennst du dich?</div>' +
      '<p class="sp-lead">Drei Sätze aus deinem Bauplan. Tippe an, was zu dir passt.</p><div class="sp-reihe">' +
      saetze.map(function (t, i) {
        return '<div class="sp-satz" data-i="' + i + '"><span class="sp-nr" aria-hidden="true">' + ["I", "II", "III"][i] + '</span><p>„' + esc(t) + '“</p>' +
          '<div class="sp-knoepfe"><button type="button" data-a="ja">Das bin ich</button><button type="button" data-a="nein">Eher nicht</button></div></div>';
      }).join("") + '</div><p class="sp-fazit" aria-live="polite"></p></section>');
    var box = document.querySelector(".spiegel"), ja = 0, fertig = 0, n = saetze.length;
    box.addEventListener("click", function (e) {
      var k = e.target.closest("button[data-a]"); if (!k) return;
      var satz = k.closest(".sp-satz"); if (satz.classList.contains("beantwortet")) return;
      satz.classList.add("beantwortet", k.getAttribute("data-a")); k.classList.add("gewaehlt");
      if (k.getAttribute("data-a") === "ja") { ja++; zaehl("spiegel_ja"); } else zaehl("spiegel_nein");
      // Am Handy liegen die Karten nebeneinander zum Wischen: nach der Antwort rückt die nächste ins Bild
      var reihe = box.querySelector(".sp-reihe"), naechste = satz.nextElementSibling;
      if (naechste && reihe && reihe.scrollWidth > reihe.clientWidth + 4) setTimeout(function () {
        reihe.scrollTo({ left: naechste.offsetLeft - (reihe.clientWidth - naechste.offsetWidth) / 2, behavior: reduce ? "auto" : "smooth" });
      }, 450);
      if (++fertig < n) return;
      zaehl("spiegel_fertig");
      box.querySelector(".sp-fazit").textContent = ja >= 2 ? "Dein Bauplan hat noch viele solcher Stellen. Er wartet schon auf dich."
        : ja === 1 ? "Was nicht passt, darfst du liegen lassen. Im ganzen Bauplan findest du noch viel mehr über dich."
        : "Was nicht passt, darfst du liegen lassen. Der ganze Bauplan zeigt dich aus noch vielen anderen Blickwinkeln.";
    });
  }
  // Das eigene Deckblatt liegt schon im E-Mail-Kasten
  function deckImMail(d) {
    var f = d.full, karte = document.querySelector("#glimpse .mailcard"), h = karte && karte.querySelector("h3"); if (!h) return;
    var alt = karte.querySelector(".mail-deck"); if (alt) alt.remove();
    var so = (f.positions || []).filter(function (p) { return p.key === "Sonne"; })[0], i = so ? H.ZEICHEN.indexOf(so.sign) : -1;
    var name = (d.birth && d.birth.name) || "";
    h.insertAdjacentHTML("beforebegin", '<div class="mail-deck" aria-hidden="true" style="background-image:url(/bilder/deckblatt-' + (i >= 0 ? i : "neutral") + '-480.webp)">' +
      '<span class="md-titel">Dein kosmischer Bauplan</span>' + (name ? '<span class="md-name">' + esc(name) + '</span>' : '') + '<span class="md-marke">Intuition mit Herz</span></div>' +
      '<p class="md-text">Dein Deckblatt ist schon fertig.</p>');
  }
  // Du und deine Freundin: kam der Besuch über einen geteilten Himmel (?v=), steht hier der Vergleich (ohne Geburtsdaten)
  var ELEMENT_ZEICHEN = ["Feuer", "Erde", "Luft", "Wasser"];
  function himmelKurz(d) {
    var f = d.full || {}, by = {}; (f.positions || []).forEach(function (p) { by[p.key] = p; });
    function zi(k) { return by[k] ? H.ZEICHEN.indexOf(by[k].sign) : -1; }
    var el = {}; (f.sections || []).forEach(function (s) { if (/Elemente/.test(s.title || "") && s.facts) s.facts.forEach(function (x) { el[x[0]] = +x[1] || 0; }); });
    return { n: ((d.birth && d.birth.name) || "").slice(0, 24), s: zi("Sonne"), m: zi("Mond"), a: zi("AC"), e: el, h: (f.hd && (f.hd.type_display || f.hd.type)) || "" };
  }
  function staerkstes(e) { var best = "", max = -1; Object.keys(e || {}).forEach(function (k) { if (e[k] > max) { max = e[k]; best = k; } }); return best; }
  function duUndSie(d) {
    var roh = ""; try { roh = sessionStorage.getItem("imh_v") || ""; } catch (e) {}
    var ziel = document.querySelector("#glimpse .spiegel") || document.querySelector("#glimpse .glimpse-cols"); if (!roh || !ziel) return;
    var sie; try { sie = JSON.parse(decodeURIComponent(escape(atob(roh.replace(/-/g, "+").replace(/_/g, "/"))))); } catch (e) { return; }
    if (!sie || typeof sie !== "object") return;
    var ich = himmelKurz(d), name = esc(String(sie.n || "Deine Freundin").slice(0, 24)), zeilen = [];
    if (sie.s >= 0 && sie.s === ich.s) zeilen.push("Ihr habt beide die Sonne " + H.IM[ich.s] + ". Kein Wunder, dass ihr euch versteht.");
    else if (sie.s >= 0 && ich.s >= 0) zeilen.push("Deine Sonne steht " + H.IM[ich.s] + ", die von " + name + " " + H.IM[sie.s] + ".");
    var e1 = staerkstes(ich.e), e2 = staerkstes(sie.e);
    if (e1 && e2) zeilen.push(e1 === e2 ? "Bei euch beiden ist " + e1 + " am stärksten. In vielem tickt ihr ähnlich." :
      "Bei dir ist " + e1 + " am stärksten, bei " + name + " " + e2 + ". Ihr ergänzt euch genau dort, wo die andere weniger hat.");
    if (sie.m >= 0 && sie.m === ich.m) zeilen.push("Auch euer Mond steht im selben Zeichen. Ihr fühlt ähnlich.");
    if (sie.h && ich.h) zeilen.push(sie.h === ich.h ? "Im Human Design seid ihr beide " + esc(ich.h) + "." : name + " ist im Human Design " + esc(sie.h) + ", du bist " + esc(ich.h) + ".");
    if (!zeilen.length) return;
    var alt = document.querySelector(".du-und"); if (alt) alt.remove();
    ziel.insertAdjacentHTML("beforebegin", '<section class="du-und"><div class="script-eyebrow">Du und ' + name + '</div>' +
      zeilen.map(function (z) { return "<p>" + z + "</p>"; }).join("") + '</section>');
    zaehl("du_und");
  }

  /* ── Dritte Überraschung: Mondkalender. Die nächsten Neu- und Vollmonde mit dem Lebensbereich (Haus), den sie bei ihr berühren,
        dazu alle Termine als Kalenderdatei mit Link zurück zum Bauplan. Ab dem dritten Öffnen. ── */
  var MONAT = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"];
  var WTAG = ["So.", "Mo.", "Di.", "Mi.", "Do.", "Fr.", "Sa."];
  function mondEreignisse(anzahl) {
    if (!H._mond || !H._sonne || !H._T) return [];
    function el(t) { var T = H._T(new Date(t)); return ((H._mond(T) - H._sonne(T)) % 360 + 360) % 360; }
    var aus = [], t = Date.now(), schritt = 6 * 3600000, vor = el(t);
    for (var i = 0; i < 4 * 75 && aus.length < anzahl; i++) {
      var t2 = t + schritt, jetzt = el(t2);
      [[0, "Neumond"], [180, "Vollmond"]].forEach(function (z) {
        var a1 = (vor - z[0] + 360) % 360, a2 = (jetzt - z[0] + 360) % 360;
        if (a1 > 300 && a2 < 60) {   // Grenze überschritten: auf die Stunde genau eingrenzen
          var lo = t, hi = t2;
          for (var k = 0; k < 12; k++) { var mi = (lo + hi) / 2, am = (el(mi) - z[0] + 360) % 360; if (am > 300) lo = mi; else hi = mi; }
          var T = H._T(new Date(hi));
          aus.push({ art: z[1], zeit: hi, zeichen: H.zeichen(H._mond(T)) });
        }
      });
      vor = jetzt; t = t2;
    }
    return aus.slice(0, anzahl);
  }
  function mondkalender(d) {
    var alt = document.querySelector(".mondkalender"); if (alt) alt.remove();
    if (besuchNr < 2) return;
    var f = d.full, ac = (f.positions || []).filter(function (p) { return p.key === "AC"; })[0], ai = ac ? H.ZEICHEN.indexOf(ac.sign) : -1;
    if (ai < 0 || !f.houses) return;
    var ev = mondEreignisse(4); if (!ev.length) return;
    ev.forEach(function (e) {
      e.haus = ((e.zeichen - ai + 12) % 12) + 1;
      var h = f.houses.filter(function (x) { return x.nr === e.haus; })[0]; e.bedeutung = h ? h.meaning : "";
      var dt = new Date(e.zeit); e.datum = WTAG[dt.getDay()] + ", " + dt.getDate() + ". " + MONAT[dt.getMonth()];
      e.satz = "Er berührt dein " + e.haus + ". Haus: " + e.bedeutung + ". " + (e.art === "Neumond"
        ? "Ein guter Moment, dort etwas Neues zu beginnen." : "Was dort gewachsen ist, darf jetzt sichtbar werden.");
    });
    var ziel = ueNeu ? obenAnker() : (document.querySelector(".roter-faden") || document.querySelector("#siegel-reihe")); if (!ziel) return;
    ziel.insertAdjacentHTML("afterend", '<section class="mondkalender' + (ueNeu ? " neu" : "") + '">' +
      (ueNeu ? '<span class="ue-geschenk" aria-hidden="true"></span><p class="mk-neu">Deine zweite Überraschung</p>' : '') +
      '<p class="mk-titel">Dein Mondkalender</p><ol class="mk-liste">' + ev.map(function (e) {
        return '<li><span class="mk-mond ' + (e.art === "Neumond" ? "neu" : "voll") + '" aria-hidden="true"></span><span class="mk-inhalt"><b>' + esc(e.art) + " " + esc(H.IM[e.zeichen]) +
          '</b><span class="mk-datum">' + esc(e.datum) + '</span><span class="mk-satz">' + esc(e.satz) + '</span></span></li>';
      }).join("") + '</ol><button class="btn btn-ghost mk-ics" type="button" style="width:auto">In meinen Kalender ✦</button></section>');
    if (ueNeu) zaehl("mondkalender");
    document.querySelector(".mk-ics").addEventListener("click", function () {
      var url = location.origin + location.pathname + "?d=" + encodeURIComponent(new URLSearchParams(location.search).get("d") || "");
      function tag(t) { var x = new Date(t); return x.getFullYear() + ("0" + (x.getMonth() + 1)).slice(-2) + ("0" + x.getDate()).slice(-2); }
      function txt(s) { return String(s).replace(/[\\,;]/g, function (c) { return "\\" + c; }); }
      var z = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Intuition mit Herz//Mondkalender//DE", "CALSCALE:GREGORIAN"];
      ev.forEach(function (e, i) {
        z.push("BEGIN:VEVENT", "UID:imh-mond-" + Math.round(e.zeit / 60000) + "-" + i + "@bauplan.intuitionmitherz.de", "DTSTAMP:" + new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+/, ""),
          "DTSTART;VALUE=DATE:" + tag(e.zeit), "SUMMARY:" + txt(e.art + " in deinem " + e.haus + ". Haus"),
          "DESCRIPTION:" + txt(e.satz + " Dein Bauplan: " + url), "URL:" + url,
          "BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:PT9H", "DESCRIPTION:" + txt(e.art + " in deinem " + e.haus + ". Haus"), "END:VALARM", "END:VEVENT");
      });
      z.push("END:VCALENDAR");
      // Zeilen über 75 Zeichen falten (RFC 5545), sonst lehnen strenge Kalender die Datei ab
      z = z.map(function (l) { var o = l.slice(0, 60); for (var p = 60; p < l.length; p += 60) o += "\r\n " + l.slice(p, p + 60); return o; });
      var blob = new Blob([z.join("\r\n") + "\r\n"], { type: "text/calendar" }), a = document.createElement("a");
      a.href = URL.createObjectURL(blob); a.download = "mein-mondkalender.ics"; document.body.appendChild(a); a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
      zaehl("mondkalender_ics");
    });
  }

  /* ── Wiederkommen lohnt sich: beim ersten Lesen der Hinweis auf eine Überraschung, beim zweiten Öffnen die Überraschung selbst ── */
  // Oben unter der Knopfleiste, damit sie beim Öffnen sofort ins Auge fallen
  function obenAnker() { return document.querySelector("#step3 .hoeren-box") || document.querySelector("#step3 .bericht-leiste"); }
  function wannText(ts) {
    var z = new Date(ts), h = new Date(), tage = Math.round((new Date(z.getFullYear(), z.getMonth(), z.getDate()) - new Date(h.getFullYear(), h.getMonth(), h.getDate())) / 864e5);
    var tag = tage <= 0 ? "heute" : tage === 1 ? "morgen" : tage === 2 ? "übermorgen" : WTAG[z.getDay()].replace(".", "") + "., " + z.getDate() + ". " + MONAT[z.getMonth()];
    return tag + " ab " + z.getHours() + ":" + ("0" + z.getMinutes()).slice(-2) + " Uhr";
  }
  function bauplanLink() {
    var dp = ""; try { dp = new URLSearchParams(location.search).get("d") || ""; } catch (e) {}
    return location.origin + location.pathname + (dp ? "?d=" + encodeURIComponent(dp) : "");
  }
  function linkSpeichern(knopf, info) {
    var url = bauplanLink();
    zaehl("link_speichern");
    if (navigator.share && /iPhone|iPad|Android/.test(navigator.userAgent || "")) {
      navigator.share({ title: "Mein Kosmischer Bauplan", url: url }).catch(function () {});
      return;
    }
    var fertig = function () { info.textContent = "Link kopiert. Leg ihn dir als Lesezeichen ab, dann findest du deinen Bauplan sofort wieder."; };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(fertig, function () { info.textContent = url; });
    else info.textContent = url;
  }
  function ueberraschung() {
    var alt = document.querySelectorAll(".ue-hinweis, .ue-karte"); [].forEach.call(alt, function (x) { x.remove(); });
    var anker = obenAnker(); if (!anker) return;
    if (ersterBesuch) {
      var ab = ueFrei ? wannText(ueFrei[0]) : "morgen";
      anker.insertAdjacentHTML("afterend", '<section class="ue-hinweis"><span class="ue-geschenk zu" aria-hidden="true"></span>' +
        '<p class="ue-titel">Hier wartet eine Überraschung auf dich.</p>' +
        '<p class="ue-text">Sie öffnet sich ' + esc(ab) + '. Speicher dir dafür diesen Link, er führt dich direkt zurück zu deinem Bauplan. Du findest ihn auch in deiner E-Mail. Öffne ihn am besten wieder hier auf diesem Gerät.</p>' +
        '<div class="ue-knoepfe"><button class="btn ue-link" type="button" style="width:auto">Link speichern ✦</button></div><p class="ue-info" aria-live="polite"></p></section>');
      var h0 = document.querySelector(".ue-hinweis");
      h0.querySelector(".ue-link").addEventListener("click", function () { linkSpeichern(this, h0.querySelector(".ue-info")); });
      return;
    }
    if (!zweiterBesuch) return;
    var app = !!document.querySelector(".wk-app");
    anker.insertAdjacentHTML("afterend",
      '<section class="ue-karte' + (ueNeu ? " neu" : "") + '"><span class="ue-geschenk" aria-hidden="true"></span><p class="ue-titel">Deine Überraschung</p>' +
      '<p class="ue-text">' + (app ? "Dein Geburtshimmel als Hintergrund für dein Handy und dein Bauplan als App auf deinem Startbildschirm. Beides wartet ab jetzt auf dich."
        : "Dein Geburtshimmel als Hintergrund für dein Handy. Der Himmel über dir in der Minute deiner Geburt, jeden Tag in deiner Hand.") + '</p>' +
      '<div class="ue-knoepfe"><button class="btn ue-himmel" type="button" style="width:auto">Mein Geburtshimmel ✦</button>' +
      (app ? '<button class="btn btn-ghost ue-app" type="button" style="width:auto">Als App speichern</button>' : '') + '</div>' +
      '<p class="ue-naechste">Die nächste Überraschung, dein persönlicher Mondkalender, öffnet sich ' + esc(ueFrei ? wannText(ueFrei[1]) : "beim nächsten Mal") + '.</p></section>');
    if (ueNeu) zaehl("ueberraschung");
    var k = document.querySelector(".ue-karte");
    var h = k.querySelector(".ue-himmel"); if (h) h.addEventListener("click", function () { var b = document.querySelector(".pk-hintergrund"); if (b) { b.scrollIntoView({ behavior: "smooth", block: "center" }); setTimeout(function () { b.click(); }, 500); } });
    var a = k.querySelector(".ue-app"); if (a) a.addEventListener("click", function () { var c = document.querySelector(".wk-app"); if (c) { c.scrollIntoView({ behavior: "smooth", block: "center" }); var det = c.querySelector("details"); if (det) det.open = true; } });
  }


  /* ── Bericht: Lesezeichen „Hier anfangen“ an den drei Stellen aus Mail 2, Lesefortschritt der Kapitel ── */
  var ANFANG = ["Entscheidungsweg", "Schwierigkeiten"];
  function lesezeichen(d) {
    var tab = document.querySelector('.rtab[data-rtab="in"]'); if (tab) tab.classList.add("anfang");
    var kapitel = [].slice.call(document.querySelectorAll("#pane-de details.acc"));
    var schl = "imh_gelesen_" + bauplanSchluessel(d), gelesen = {};
    try { (JSON.parse(localStorage.getItem(schl) || "[]")).forEach(function (t) { gelesen[t] = 1; }); } catch (e) {}
    function titel(acc) { var t = acc.querySelector(".acc-t"); return t ? ((t.firstChild && t.firstChild.textContent) || t.textContent).trim() : ""; }
    kapitel.forEach(function (acc) {
      var t = titel(acc), s = acc.querySelector("summary");
      if (s && !s.querySelector(".lesezeichen") && ANFANG.some(function (a) { return t.indexOf(a) >= 0; })) {
        acc.classList.add("anfang");
        var x = s.querySelector(".acc-x"), lz = '<span class="lesezeichen">Hier anfangen</span>';
        if (x) x.insertAdjacentHTML("beforebegin", lz); else s.insertAdjacentHTML("beforeend", lz);
      }
      if (gelesen[t]) acc.classList.add("gelesen");
    });
    var pane = $("pane-de"); if (!pane || !kapitel.length) return;
    var alt = pane.querySelector(".lesefortschritt"); if (alt) alt.remove();
    pane.insertAdjacentHTML("afterbegin", '<div class="lesefortschritt"><div class="lf-text"></div><div class="lf-balken"><span></span></div></div>');
    var box = pane.querySelector(".lesefortschritt");
    function zeigen() {
      var n = kapitel.filter(function (a) { return a.classList.contains("gelesen"); }).length;
      box.querySelector(".lf-text").textContent = n === 0 ? "Du hast " + kapitel.length + " Kapitel vor dir. Fang an, wo es dich hinzieht."
        : n >= kapitel.length ? "Alle " + kapitel.length + " Kapitel gelesen. Schön, dass du dir die Zeit genommen hast."
        : n + " von " + kapitel.length + " Kapiteln gelesen";
      box.querySelector(".lf-balken span").style.width = (100 * n / kapitel.length).toFixed(1) + "%";
      if (n >= kapitel.length) vollendet();
    }
    // Alle Kapitel gelesen: Wachssiegel und ein Satz von Denise unter dem letzten Kapitel (seit 11.10.2026)
    function vollendet() {
      if (pane.querySelector(".vollendet")) return;
      var vs = "imh_vollendet_" + bauplanSchluessel(d), erstmals = true;
      try { erstmals = !localStorage.getItem(vs); localStorage.setItem(vs, "1"); } catch (e) {}
      kapitel[kapitel.length - 1].insertAdjacentHTML("afterend",
        '<section class="vollendet' + (erstmals && !reduce ? " neu" : "") + '"><span class="vd-siegel" aria-hidden="true"></span>' +
        '<p class="vd-titel">Du hast deinen ganzen Bauplan gelesen.</p>' +
        '<p class="vd-text">Nimm dir mit, was sich stimmig anfühlt. Was nicht passt, darfst du liegen lassen.</p>' +
        '<p class="vd-name">Denise</p></section>');
      if (erstmals) zaehl("vollendet");
    }
    kapitel.forEach(function (acc) {
      acc.addEventListener("toggle", function () {
        if (!acc.open || acc.classList.contains("gelesen")) return;
        acc.classList.add("gelesen"); gelesen[titel(acc)] = 1;
        try { localStorage.setItem(schl, JSON.stringify(Object.keys(gelesen))); } catch (e) {}
        zeigen();
      });
    });
    zeigen();
  }

  /* ── Story-Bild zum Teilen (1080 × 1920): Gravur, Name, Siegel, @intuitionmitherz. Keine Geburtsdaten im Bild. ── */
  function bildLaden(src) { return new Promise(function (ok) { var i = new Image(); i.onload = function () { ok(i); }; i.onerror = function () { ok(null); }; i.src = src; }); }
  function storyBild(d) {
    var f = d.full, by = {}; (f.positions || []).forEach(function (p) { by[p.key] = p; });
    var so = by.Sonne, idx = so ? H.ZEICHEN.indexOf(so.sign) : -1, name = (d.birth && d.birth.name) || "";
    var schriften = document.fonts && document.fonts.load ? Promise.all([
      document.fonts.load('200px "Great Vibes"'), document.fonts.load('500 48px "Cormorant Garamond"'), document.fonts.load('600 30px "Mulish"')
    ]).catch(function () {}) : Promise.resolve();
    return Promise.all([bildLaden("/bilder/kuppel-hoch.webp"), idx >= 0 ? bildLaden("/bilder/zeichen-" + idx + "-1600.webp") : null, bildLaden("/bilder/wachssiegel-440.webp"), schriften]).then(function (r) {
      var W = 1080, Hh = 1920, c = document.createElement("canvas"); c.width = W; c.height = Hh;
      var g = c.getContext("2d");
      g.fillStyle = "#0a0916"; g.fillRect(0, 0, W, Hh);
      if (r[0]) { var s = Math.max(W / r[0].width, 1300 / r[0].height); g.globalAlpha = .62; g.drawImage(r[0], (W - r[0].width * s) / 2, -60, r[0].width * s, r[0].height * s); g.globalAlpha = 1; }
      var v = g.createLinearGradient(0, 0, 0, Hh); v.addColorStop(0, "rgba(10,9,22,.25)"); v.addColorStop(.42, "rgba(10,9,22,.55)"); v.addColorStop(.62, "#0a0916"); v.addColorStop(1, "#0a0916");
      g.fillStyle = v; g.fillRect(0, 0, W, Hh);
      if (r[1]) { var zw = 980, zh = r[1].height * zw / r[1].width; g.globalAlpha = .62; g.globalCompositeOperation = "screen"; g.drawImage(r[1], (W - zw) / 2, 330, zw, zh); g.globalAlpha = 1; g.globalCompositeOperation = "source-over"; }
      g.textAlign = "center"; g.textBaseline = "alphabetic";
      g.fillStyle = "#f6f1e8"; g.font = '500 46px "Cormorant Garamond", Georgia, serif';
      if ("letterSpacing" in g) g.letterSpacing = "10px";
      g.fillText("MEIN KOSMISCHER BAUPLAN", W / 2, 300);
      if ("letterSpacing" in g) g.letterSpacing = "0px";
      if (name) { g.font = '200px "Great Vibes", cursive'; g.fillStyle = "#e2c486"; g.shadowColor = "rgba(226,196,134,.55)"; g.shadowBlur = 40; g.fillText(name, W / 2, 520, W - 120); g.shadowBlur = 0; }
      // fünf Siegel
      var sg = [];
      ["Sonne", "Mond", "AC"].forEach(function (k, i) { var p = by[k]; if (p) sg.push({ g: tp(p.signSymbol), l: ["Sonne", "Mond", "Aszendent"][i], v: p.sign, sym: true }); });
      if (f.hd) sg.push({ g: f.hd.profile || "", l: "Human Design", v: f.hd.type_display || f.hd.type || "" });
      if (f.numerology) sg.push({ g: String(f.numerology.lifepath), l: "Lebenszahl", v: f.numerology.title || "" });
      var y = 1200, schritt = W / (sg.length + 1);
      sg.forEach(function (x, i) {
        var cx = schritt * (i + 1);
        g.beginPath(); g.arc(cx, y, 74, 0, Math.PI * 2); g.fillStyle = "rgba(16,15,36,.82)"; g.fill();
        g.lineWidth = 2; g.strokeStyle = "#e2c486"; g.shadowColor = "rgba(226,196,134,.7)"; g.shadowBlur = 24; g.stroke(); g.shadowBlur = 0;
        g.beginPath(); g.arc(cx, y, 64, 0, Math.PI * 2); g.setLineDash([2, 7]); g.lineWidth = 1.5; g.stroke(); g.setLineDash([]);
        g.fillStyle = "#f3dca6"; g.font = x.sym ? '64px "Apple Symbols", "Segoe UI Symbol", "Noto Sans Symbols 2", serif' : '500 54px "Cormorant Garamond", Georgia, serif';
        // Sichtbares Zeichen genau in die Kreismitte setzen: Symbolschriften haben ungleiche Ränder,
        // deshalb nach der gemessenen Zeichenbox zentrieren statt nach der Schriftbox
        var zeichenText = x.sym ? String(x.g).replace(/\uFE0E/g, "") : x.g;
        g.textAlign = "left"; g.textBaseline = "alphabetic";
        var mz = g.measureText(zeichenText);
        var li = mz.actualBoundingBoxLeft || 0, re = mz.actualBoundingBoxRight || mz.width, ob = mz.actualBoundingBoxAscent || 40, un = mz.actualBoundingBoxDescent || 0;
        g.fillText(zeichenText, cx - (re - li) / 2, y + (ob - un) / 2);
        g.textAlign = "center";
        g.fillStyle = "#e2c486"; g.font = '600 16px "Mulish", sans-serif'; if ("letterSpacing" in g) g.letterSpacing = "2px";
        g.fillText(x.l.toUpperCase(), cx, y + 122, schritt - 10); if ("letterSpacing" in g) g.letterSpacing = "0px";
        // Werte: bei Bedarf auf zwei Zeilen
        g.fillStyle = "#f6f1e8"; g.font = '500 30px "Cormorant Garamond", Georgia, serif';
        var breit = schritt - 14, worte = String(x.v).split(" "), z1 = String(x.v), z2 = "";
        if (g.measureText(z1).width > breit && worte.length > 1) {
          z1 = worte[0]; var k = 1;
          while (k < worte.length && g.measureText(z1 + " " + worte[k]).width <= breit) { z1 += " " + worte[k]; k++; }
          z2 = worte.slice(k).join(" ");
        }
        g.fillText(z1, cx, y + 162, breit); if (z2) g.fillText(z2, cx, y + 196, breit);
      });
      if (r[2]) g.drawImage(r[2], W / 2 - 80, 1480, 160, 160);
      g.fillStyle = "#f6f1e8"; g.font = 'italic 500 44px "Cormorant Garamond", Georgia, serif'; g.fillText("Hol dir deinen eigenen Bauplan", W / 2, 1730);
      g.fillStyle = "#e2c486"; g.font = '600 30px "Mulish", sans-serif'; if ("letterSpacing" in g) g.letterSpacing = "3px";
      g.fillText("@INTUITIONMITHERZ", W / 2, 1790); if ("letterSpacing" in g) g.letterSpacing = "0px";
      return new Promise(function (ok) { c.toBlob(function (b) { ok(b); }, "image/png"); });
    });
  }
  /* ── Geburtshimmel als Handy-Hintergrund (1170 × 2532): Sternenfeld, Tierkreis-Rad mit den Planeten an ihrem Ort,
        Name, Zeichen. Oben bleibt Platz für die Uhr des Sperrbildschirms. Keine Geburtsdaten im Bild. ── */
  function hintergrundBild(d) {
    var f = d.full || {}, by = {}; (f.positions || []).forEach(function (p) { by[p.key] = p; });
    var name = (d.birth && d.birth.name) || "", b = d.birth || {};
    var schriften = document.fonts && document.fonts.load ? Promise.all([
      document.fonts.load('150px "Great Vibes"'), document.fonts.load('500 40px "Cormorant Garamond"'), document.fonts.load('600 24px "Mulish"')
    ]).catch(function () {}) : Promise.resolve();
    return schriften.then(function () {
      var W = 1170, Hh = 2532, c = document.createElement("canvas"); c.width = W; c.height = Hh;
      var g = c.getContext("2d");
      var bg = g.createRadialGradient(W / 2, 1480, 80, W / 2, 1300, 1700);
      bg.addColorStop(0, "#1f1d45"); bg.addColorStop(.45, "#121129"); bg.addColorStop(1, "#07060f");
      g.fillStyle = bg; g.fillRect(0, 0, W, Hh);
      // Sternenfeld, aus den Geburtsdaten gesät: jedes Bild ist anders, und dasselbe Bild entsteht wieder gleich
      var saat = 7; String([b.date, b.time, b.place, name].join("|")).split("").forEach(function (ch) { saat = (saat * 31 + ch.charCodeAt(0)) >>> 0; });
      function zufall() { saat = (saat * 1664525 + 1013904223) >>> 0; return saat / 4294967296; }
      for (var i = 0; i < 900; i++) {
        var x = zufall() * W, y = zufall() * Hh, r = zufall() < .06 ? 1.6 + zufall() * 1.6 : .5 + zufall() * .9, a = .25 + zufall() * .6;
        g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fillStyle = zufall() < .18 ? "rgba(243,220,166," + a + ")" : "rgba(246,241,232," + a + ")";
        if (r > 1.6) { g.shadowColor = "rgba(243,220,166,.8)"; g.shadowBlur = 10; }
        g.fill(); g.shadowBlur = 0;
      }
      // Tierkreis-Rad. Mit Geburtszeit liegt der Aszendent links wie in einem Horoskop, sonst die Sonne.
      var cx = W / 2, cy = 1480, R = 440;
      var bezug = by.AC ? laengeAus(by.AC) : (by.Sonne ? laengeAus(by.Sonne) : 0);
      function winkel(lon) { return Math.PI - (lon - bezug) * Math.PI / 180; }
      function punkt(lon, rr) { var w = winkel(lon); return [cx + Math.cos(w) * rr, cy - Math.sin(w) * rr]; }
      var schein = g.createRadialGradient(cx, cy, 0, cx, cy, R * 1.25);
      schein.addColorStop(0, "rgba(226,196,134,.10)"); schein.addColorStop(1, "rgba(226,196,134,0)");
      g.fillStyle = schein; g.beginPath(); g.arc(cx, cy, R * 1.25, 0, Math.PI * 2); g.fill();
      g.strokeStyle = "rgba(226,196,134,.85)"; g.lineWidth = 2.2; g.shadowColor = "rgba(226,196,134,.6)"; g.shadowBlur = 18;
      g.beginPath(); g.arc(cx, cy, R, 0, Math.PI * 2); g.stroke(); g.shadowBlur = 0;
      g.lineWidth = 1.2; g.strokeStyle = "rgba(226,196,134,.5)";
      g.beginPath(); g.arc(cx, cy, R - 84, 0, Math.PI * 2); g.stroke();
      g.beginPath(); g.arc(cx, cy, R - 250, 0, Math.PI * 2); g.setLineDash([2, 9]); g.stroke(); g.setLineDash([]);
      for (var gr = 0; gr < 360; gr += 5) {   // Gradstriche am äußeren Ring
        var lang = gr % 30 === 0 ? 84 : (gr % 10 === 0 ? 16 : 9), p1 = punkt(gr, R), p2 = punkt(gr, R - lang);
        g.beginPath(); g.moveTo(p1[0], p1[1]); g.lineTo(p2[0], p2[1]); g.strokeStyle = gr % 30 === 0 ? "rgba(226,196,134,.55)" : "rgba(226,196,134,.35)"; g.stroke();
      }
      function zeichenMitte(txt, x, y) {   // sichtbares Zeichen nach gemessener Box mittig setzen (wie beim Story-Bild)
        g.textAlign = "left"; g.textBaseline = "alphabetic";
        var m = g.measureText(txt), li = m.actualBoundingBoxLeft || 0, re = m.actualBoundingBoxRight || m.width, ob = m.actualBoundingBoxAscent || 30, un = m.actualBoundingBoxDescent || 0;
        g.fillText(txt, x - (re - li) / 2, y + (ob - un) / 2);
      }
      var SYMF = '"Apple Symbols", "Segoe UI Symbol", "Noto Sans Symbols 2", serif';
      g.fillStyle = "rgba(226,196,134,.8)"; g.font = "40px " + SYMF;
      H.GLYPH.forEach(function (gl, z) { var q = punkt(z * 30 + 15, R - 42); zeichenMitte(gl, q[0], q[1]); });
      // Planeten: leuchtender Punkt auf dem inneren Ring, Zeichen etwas weiter innen; dicht beieinander wird gestaffelt
      var pl = []; PLANETEN.forEach(function (n) { var p = by[n]; if (p) { var l = laengeAus(p); if (l != null) pl.push({ n: n, lon: l }); } });
      pl.sort(function (a, b) { return a.lon - b.lon; });
      pl.forEach(function (x, k) { var vor = pl[k - 1]; x.stufe = vor && Math.abs(x.lon - vor.lon) < 9 && !vor.stufe ? 1 : 0; });
      pl.forEach(function (x) {
        var gross = x.n === "Sonne" || x.n === "Mond", rp = R - 84, q = punkt(x.lon, rp);
        g.beginPath(); g.arc(q[0], q[1], gross ? 9 : 6, 0, Math.PI * 2); g.fillStyle = "#fff3d2"; g.shadowColor = "rgba(255,240,200,.95)"; g.shadowBlur = gross ? 30 : 18; g.fill(); g.shadowBlur = 0;
        var t = punkt(x.lon, rp - (x.stufe ? 120 : 62));
        g.fillStyle = gross ? "#f3dca6" : "rgba(246,241,232,.92)"; g.font = (gross ? "50px " : "40px ") + SYMF;
        zeichenMitte(tp(PSYM[x.n]).replace(/︎/g, ""), t[0], t[1]);
      });
      if (by.AC) {   // Aszendent als kleine goldene Marke links
        var a1 = punkt(bezug, R + 14), a2 = punkt(bezug, R + 44);
        g.beginPath(); g.moveTo(a1[0], a1[1]); g.lineTo(a2[0], a2[1]); g.strokeStyle = "#e2c486"; g.lineWidth = 3; g.stroke();
      }
      // Mitte: Siegelstern
      g.fillStyle = "#e2c486"; g.font = "60px " + SYMF; g.shadowColor = "rgba(226,196,134,.8)"; g.shadowBlur = 24; zeichenMitte("✦", cx, cy); g.shadowBlur = 0;
      // Name und Zeichen
      g.textAlign = "center"; g.textBaseline = "alphabetic";
      if (name) { g.font = '150px "Great Vibes", cursive'; g.fillStyle = "#e2c486"; g.shadowColor = "rgba(226,196,134,.5)"; g.shadowBlur = 34; g.fillText(name, cx, 2140, W - 160); g.shadowBlur = 0; }
      var zeile = [];
      if (by.Sonne) zeile.push("Sonne " + by.Sonne.sign); if (by.Mond) zeile.push("Mond " + by.Mond.sign); if (by.AC) zeile.push("Aszendent " + by.AC.sign);
      g.fillStyle = "#f6f1e8"; g.font = '500 38px "Cormorant Garamond", Georgia, serif'; if ("letterSpacing" in g) g.letterSpacing = "3px";
      g.fillText(zeile.join("  ·  "), cx, 2232, W - 120); if ("letterSpacing" in g) g.letterSpacing = "0px";
      g.fillStyle = "rgba(226,196,134,.75)"; g.font = '600 22px "Mulish", sans-serif'; if ("letterSpacing" in g) g.letterSpacing = "6px";
      g.fillText("INTUITION MIT HERZ", cx, 2330); if ("letterSpacing" in g) g.letterSpacing = "0px";
      return new Promise(function (ok) { c.toBlob(function (bl) { ok(bl); }, "image/png"); });
    });
  }
  function hintergrundTeilen(d, knopf) {
    var alt = knopf.textContent; knopf.disabled = true; knopf.textContent = "Einen Moment…";
    hintergrundBild(d).then(function (blob) {
      knopf.disabled = false; knopf.textContent = alt;
      if (!blob) return;
      zaehl("hintergrund");
      var datei = null; try { datei = new File([blob], "mein-geburtshimmel.png", { type: "image/png" }); } catch (e) {}
      // Am Handy: Teilen-Menü, darin "Bild sichern", dann in den Fotos als Hintergrund wählen
      if (datei && navigator.canShare && navigator.canShare({ files: [datei] })) { navigator.share({ files: [datei], title: "Mein Geburtshimmel" }).catch(function () {}); return; }
      var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "mein-geburtshimmel.png";
      document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
    }).catch(function () { knopf.disabled = false; knopf.textContent = alt; });
  }
  function storyTeilen(d, knopf) {
    var alt = knopf.textContent; knopf.disabled = true; knopf.textContent = "Einen Moment…";
    storyBild(d).then(function (blob) {
      knopf.disabled = false; knopf.textContent = alt;
      if (!blob) return;
      zaehl("story");
      var datei = null; try { datei = new File([blob], "mein-kosmischer-bauplan.png", { type: "image/png" }); } catch (e) {}
      if (datei && navigator.canShare && navigator.canShare({ files: [datei] })) {
        navigator.share({ files: [datei], title: "Mein Kosmischer Bauplan", text: "Mein Kosmischer Bauplan von @intuitionmitherz" }).catch(function () {});
        return;
      }
      var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "mein-kosmischer-bauplan.png";
      document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
    }).catch(function () { knopf.disabled = false; knopf.textContent = alt; });
  }

  /* ── Bericht: wie es weitergeht (Instagram, Frage an Denise; die Liebesanalyse erscheint erst, wenn sie live ist) ── */
  var LIEBE_LIVE = false;
  function weiter() {
    var note = $("note"); if (!note || document.querySelector(".weiter")) return;
    var karten = [
      '<a class="wk" href="https://www.instagram.com/intuitionmitherz/" target="_blank" rel="noopener" data-ev="folgen"><span class="wk-titel">Folge mir auf Instagram</span><span class="wk-text">Impulse rund um Intuition, Grenzen und das, was in deinem Bauplan steckt.</span><span class="wk-mehr">@intuitionmitherz ✦</span></a>',
      '<a class="wk" href="https://ig.me/m/intuitionmitherz" target="_blank" rel="noopener" data-ev="frage"><span class="wk-titel">Frag mich direkt</span><span class="wk-text">Schreib mir, welche Stelle in deinem Bauplan dich gerade am meisten beschäftigt.</span><span class="wk-mehr">Nachricht schreiben ✦</span></a>'
    ];
    var app = alsApp(); if (app) karten.unshift(app);
    karten.push('<a class="wk wk-teilen" href="https://bauplan.intuitionmitherz.de/geschenk" data-ev="empfehlen"><span class="wk-titel">Schenk ihn einer Freundin</span><span class="wk-text">Kennst du eine Frau, die alle anderen spürt, nur sich selbst kaum? Schick ihr ihren eigenen Bauplan.</span><span class="wk-mehr">Link verschicken ✦</span></a>');
    karten[karten.length - 1] = karten[karten.length - 1].replace('</a>', '</a>').replace('<a class="wk wk-teilen"', '<div class="wk-teilen-box"><a class="wk wk-teilen"') +
      '<label class="mit-himmel"><input type="checkbox" id="mit-himmel"> Meinen Himmel mitschicken, damit sie sieht, wie ihr zusammenpasst (Vorname, Zeichen, Elemente, ohne Geburtsdaten)</label></div>';
    if (!LIEBE_LIVE) karten.push('<div class="wk wk-warte"><span class="wk-titel">Wenn dein Himmel auf einen anderen trifft</span><span class="wk-text">Die Kosmische Liebesanalyse für dich und einen Menschen, der dir nah ist. Sie entsteht gerade. Magst du sie als Erste bekommen?</span>' +
      '<form class="wl-form" novalidate><input class="wl-mail" type="email" placeholder="Deine E-Mail-Adresse" autocomplete="email" hidden aria-label="E-Mail-Adresse"><button class="wk-mehr wl-knopf" type="submit">Auf die Warteliste ✦</button></form><span class="wl-info" aria-live="polite"></span></div>');
    if (LIEBE_LIVE) karten.push('<a class="wk" href="https://liebe.intuitionmitherz.de/?q=bauplan-bericht" data-ev="liebe"><span class="wk-titel">Wenn dein Himmel auf einen anderen trifft</span><span class="wk-text">Die Kosmische Liebesanalyse für dich und einen Menschen, der dir nah ist.</span><span class="wk-mehr">Ansehen ✦</span></a>');
    note.insertAdjacentHTML("beforebegin", '<section class="weiter"><div class="script-eyebrow">Wie geht es für dich weiter?</div><div class="wk-reihe">' + karten.join("") + '</div></section>');
    note.insertAdjacentHTML("beforebegin", '<section class="fragebox"><div class="script-eyebrow">Eine Frage an dich</div>' +
      '<p class="fb-lead">Welche Frage hat dein Bauplan bei dir ausgelöst? Schreib sie mir, ganz ohne Namen und ohne E-Mail.</p>' +
      '<form class="fb-form" novalidate><textarea class="fb-text" maxlength="800" rows="3" placeholder="Zum Beispiel: Wie merke ich im Alltag, ob mein Bauch Ja sagt?" aria-label="Deine Frage"></textarea>' +
      '<button class="btn fb-knopf" type="submit" style="width:auto">Frage abschicken ✦</button></form><p class="fb-info" aria-live="polite"></p></section>');
    fragebox(); warteliste();
    document.querySelector(".weiter").addEventListener("click", function (e) { var a = e.target.closest("[data-ev]"); if (a) zaehl(a.getAttribute("data-ev")); });
    // Weiterempfehlung: am Handy das Teilen-Menü, sonst Link kopieren. Herkunft ?q=freundin landet in AC-Feld 8.
    var teilen = document.querySelector(".wk-teilen");
    if (teilen) teilen.addEventListener("click", function (e) {
      e.preventDefault();
      var url = teilen.href, mehr = teilen.querySelector(".wk-mehr"), mit = document.getElementById("mit-himmel");
      if (mit && mit.checked && letzterBericht) {
        try { url += "?v=" + btoa(unescape(encodeURIComponent(JSON.stringify(himmelKurz(letzterBericht))))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""); zaehl("himmel_mit"); } catch (x) {}
      }
      var text = "Ich habe gerade meinen Kosmischen Bauplan von Denise gelesen. Hol dir deinen auch, er ist ein Geschenk:";
      function fertig(t) { if (mehr) { mehr.textContent = t; setTimeout(function () { mehr.textContent = "Link verschicken ✦"; }, 2600); } }
      if (navigator.share) { navigator.share({ title: "Dein Kosmischer Bauplan", text: text, url: url }).catch(function () {}); return; }
      function whatsapp() { window.open("https://wa.me/?text=" + encodeURIComponent(text + " " + url), "_blank", "noopener"); }
      if (navigator.clipboard) { navigator.clipboard.writeText(text + " " + url).then(function () { fertig("Link kopiert ✦"); }, whatsapp); return; }
      whatsapp();
    });
  }

  /* ── Bericht: Warteliste Liebesanalyse und Frage an Denise, beides über /api/bericht ── */
  function berichtAktion(daten) {
    return fetch("/api/bericht", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(daten) })
      .then(function (r) { return r.json().catch(function () { return {}; }); });
  }
  function warteliste() {
    var karte = document.querySelector(".wk-warte"); if (!karte) return;
    var form = karte.querySelector(".wl-form"), mail = karte.querySelector(".wl-mail"), knopf = karte.querySelector(".wl-knopf"), info = karte.querySelector(".wl-info");
    function drauf() { form.hidden = true; info.textContent = "Du stehst auf der Liste ✦ Ich sag dir Bescheid, sobald sie fertig ist."; karte.classList.add("drauf"); }
    try { if (localStorage.getItem("imh_warteliste")) { drauf(); return; } } catch (e) {}
    var t = ""; try { t = sessionStorage.getItem("imh_t") || ""; } catch (e) {}
    if (!t) mail.hidden = false;
    form.addEventListener("submit", function (e) {
      e.preventDefault(); info.textContent = "";
      var daten = { aktion: "warteliste" };
      if (t) daten.t = t; else daten.email = mail.value.trim();
      if (!t && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(daten.email)) { info.textContent = "Bitte gib die E-Mail-Adresse ein, mit der du deinen Bauplan bekommen hast."; return; }
      knopf.disabled = true;
      berichtAktion(daten).then(function (d) {
        knopf.disabled = false;
        if (d && d.ok) { try { localStorage.setItem("imh_warteliste", "1"); } catch (x) {} zaehl("warteliste"); drauf(); return; }
        if (d && d.error === "need_email") { t = ""; mail.hidden = false; }
        info.textContent = (d && d.message) || "Das hat gerade nicht geklappt. Bitte versuch es gleich noch einmal.";
      }).catch(function () { knopf.disabled = false; info.textContent = "Keine Verbindung. Bitte versuch es gleich noch einmal."; });
    });
  }
  function fragebox() {
    var box = document.querySelector(".fragebox"); if (!box) return;
    var form = box.querySelector(".fb-form"), feld = box.querySelector(".fb-text"), knopf = box.querySelector(".fb-knopf"), info = box.querySelector(".fb-info");
    form.addEventListener("submit", function (e) {
      e.preventDefault(); info.textContent = "";
      var text = feld.value.trim();
      if (text.length < 3) { info.textContent = "Schreib mir gern ein paar Worte."; return; }
      knopf.disabled = true;
      berichtAktion({ aktion: "frage", text: text }).then(function (d) {
        knopf.disabled = false;
        if (d && d.ok) { zaehl("fragebox"); form.hidden = true; info.textContent = "Danke. Deine Frage ist bei mir angekommen. 🤍"; box.classList.add("gesendet"); return; }
        info.textContent = (d && d.message) || "Das hat gerade nicht geklappt. Bitte versuch es gleich noch einmal.";
      }).catch(function () { knopf.disabled = false; info.textContent = "Keine Verbindung. Bitte versuch es gleich noch einmal."; });
    });
  }

  /* ── Startseite: Goldfolie auf den Schmuckwörtern glänzt einmal auf, wenn sie ins Bild kommen ── */
  (function goldfolie() {
    var w = [].slice.call(document.querySelectorAll("#step1 h2 .script, .ebenen-pointe .script"));
    if (!w.length) return;
    if (reduce || !("IntersectionObserver" in window)) { w.forEach(function (x) { x.classList.add("glanz"); }); return; }
    var io = new IntersectionObserver(function (e) {
      e.forEach(function (x) { if (x.isIntersecting) { var el = x.target; setTimeout(function () { el.classList.add("glanz"); }, 700); io.unobserve(el); } });
    }, { threshold: .6 });
    w.forEach(function (x) { io.observe(x); });
  })();

  /* ── Startseite: ein feiner Lichtschein folgt der Maus über den dunklen Abschnitten (nur mit Maus) ── */
  (function lichtschein() {
    if (reduce || !window.matchMedia || !window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
    [].forEach.call(document.querySelectorAll("#step1 header.hero, #step1 .ebenen, #step1 .final-band"), function (sec) {
      var l = document.createElement("div"); l.className = "lichtschein"; l.setAttribute("aria-hidden", "true");
      sec.appendChild(l);
      var raf = 0, x = 0, y = 0;
      sec.addEventListener("pointermove", function (e) {
        var r = sec.getBoundingClientRect(); x = e.clientX - r.left; y = e.clientY - r.top;
        if (!raf) raf = requestAnimationFrame(function () { raf = 0; l.style.setProperty("--mx", x + "px"); l.style.setProperty("--my", y + "px"); l.classList.add("an"); });
      });
      sec.addEventListener("pointerleave", function () { l.classList.remove("an"); });
    });
  })();

  /* ── Startseite: der Himmel von heute in einer Zeile (Mondphase und Zeichen des Mondes) ── */
  (function himmelHeute() {
    var el = $("hero-heute"); if (!el || !H._mond) return;
    var jetzt = new Date(), T = H._T(jetzt), z = H.zeichen(H._mond(T)), ph = H.mondphase(jetzt);
    var name = ph.name.charAt(0).toUpperCase() + ph.name.slice(1);
    el.innerHTML = '<span class="hh-mond">' + tp("☽") + '</span>Der Himmel heute: <b>' + esc(name) + ' ' + esc(H.IM[z]) + '</b>';
    el.hidden = false;
  })();

  /* ── Nach dem Absenden: das Wachssiegel bricht, Licht fällt heraus, eine Sternschnuppe fliegt
     vom Knopf in den Himmel. Gibt zurück, wie lange das Bestätigungsfenster warten soll. ── */
  function gesendet(knopf) {
    // Für die Bestätigungsseite: nur das Sonnenzeichen als Zahl 0 bis 11, kein Name, keine Geburtsdaten
    try {
      var so = letzteVorschau && (letzteVorschau.full.positions || []).filter(function (p) { return p.key === "Sonne"; })[0];
      var zi = so ? H.ZEICHEN.indexOf(so.sign) : -1;
      if (zi >= 0) localStorage.setItem("imh_zeichen", String(zi));
    } catch (e) {}
    var lock = document.querySelector("#g-preview .preview-seal .lock");
    // Am Handy steht das Siegel über dem Formular und ist beim Absenden aus dem Bild gescrollt.
    // Dann erst sanft hinscrollen, danach bricht es sichtbar (seit 11.10.2026).
    var vorlauf = 0, lr = lock && lock.getBoundingClientRect();
    if (lock && !reduce && lr.height && (lr.top < 70 || lr.bottom > window.innerHeight - 40)) {
      lock.scrollIntoView({ behavior: "smooth", block: "center" }); vorlauf = 750; knopf = lock;
    }
    function brechen() {
      if (lock) {
        lock.classList.add("gebrochen");
        var st = document.querySelector("#g-preview .seal-text"), ss = document.querySelector("#g-preview .seal-sub");
        if (st) st.textContent = "Dein Siegel ist gebrochen.";
        if (ss) ss.textContent = "Bestätige kurz deine E-Mail-Adresse, dann kommt deine vollständige Deutung zu dir.";
      }
      if (reduce || !knopf || !knopf.getBoundingClientRect || !document.body.animate) return;
      try { if (navigator.vibrate) navigator.vibrate(18); } catch (e) {}
      var r = knopf.getBoundingClientRect(), x0 = r.left + r.width / 2, y0 = r.top + r.height / 2;
      var x1 = Math.max(30, x0 - window.innerWidth * .38), y1 = -80, dx = x1 - x0, dy = y1 - y0;
      var winkel = Math.atan2(dy, dx) * 180 / Math.PI;
      var el = document.createElement("div"); el.className = "schnuppe";
      el.style.left = x0 + "px"; el.style.top = y0 + "px";
      document.body.appendChild(el);
      var rot = " rotate(" + f1(winkel) + "deg)";
      el.animate([
        { transform: "translate(0,0)" + rot + " scaleX(.15)", opacity: 0 },
        { offset: .12, transform: "translate(" + f1(dx * .06) + "px," + f1(dy * .06) + "px)" + rot + " scaleX(1)", opacity: 1 },
        { transform: "translate(" + f1(dx) + "px," + f1(dy) + "px)" + rot + " scaleX(.7)", opacity: 0 }
      ], { duration: 1500, easing: "cubic-bezier(.45,.05,.2,1)", fill: "forwards" }).onfinish = function () { el.remove(); };
      for (var i = 0; i < 16; i++) {   // Funken am Knopf
        var fu = document.createElement("div"); fu.className = "funke";
        fu.style.left = x0 + "px"; fu.style.top = y0 + "px"; document.body.appendChild(fu);
        var a = Math.random() * Math.PI * 2, w = 30 + Math.random() * 70;
        fu.animate([{ transform: "translate(0,0) scale(1)", opacity: 1 },
                    { transform: "translate(" + f1(Math.cos(a) * w) + "px," + f1(Math.sin(a) * w - 20) + "px) scale(.2)", opacity: 0 }],
                   { duration: 700 + Math.random() * 600, easing: "cubic-bezier(.2,.7,.3,1)", fill: "forwards" }).onfinish = (function (x) { return function () { x.remove(); }; })(fu);
      }
    }
    if (vorlauf) setTimeout(brechen, vorlauf); else brechen();
    if (reduce || !document.body.animate) return 0;
    return vorlauf ? vorlauf + 2000 : 1500;
  }

  /* ════════ 5. Bericht ════════ */
  var ELEMENT = {
    Feuer:  '<path d="M20 5 L35 31 H5 Z"/>',
    Erde:   '<path d="M20 35 L35 9 H5 Z"/><path d="M9 18 H31"/>',
    Luft:   '<path d="M20 5 L35 31 H5 Z"/><path d="M9 22 H31"/>',
    Wasser: '<path d="M20 35 L35 9 H5 Z"/>'
  };
  var ELEMENT_WORT = { Feuer: "Antrieb und Begeisterung", Erde: "Halt und Umsetzung", Luft: "Gedanken und Austausch", Wasser: "Gefühl und Tiefe" };

  var letzterBericht = null, ersterBesuch = true, zweiterBesuch = false, besuchNr = 0, ueNeu = false, ueFrei = null;
  function bericht(d) {
    var f = d && d.full; if (!f) return;
    letzterBericht = d;
    // Beim ersten Lesen nur das Wesentliche: Story, Brief, Kapitel. App und Handy-Hintergrund kommen ab dem zweiten Besuch dazu.
    /* Überraschungen nach Stunden seit dem ersten Öffnen auf diesem Gerät: ab 24 h die erste, ab 48 h die zweite (seit 11.10.2026).
       Ältere Zählung (imh_tage, imh_besuch) wird übernommen, damit niemand zurückfällt. */
    try {
      var schl0 = bauplanSchluessel(d), jetzt = Date.now(), erst = +(localStorage.getItem("imh_erst_" + schl0) || 0);
      if (!erst) {
        var bn = +(localStorage.getItem("imh_besuch_" + schl0) || 0), tg = JSON.parse(localStorage.getItem("imh_tage_" + schl0) || "null");
        erst = tg && tg.n >= 1 ? jetzt - (tg.n - 1) * 864e5 : bn >= 1 ? jetzt - 864e5 : jetzt;
        localStorage.setItem("imh_erst_" + schl0, String(erst));
      }
      var std = (jetzt - erst) / 36e5, gesehen = +(localStorage.getItem("imh_ue_" + schl0) || 0);
      besuchNr = std >= 48 ? 2 : std >= 24 ? 1 : 0;
      ueNeu = besuchNr > gesehen; if (ueNeu) localStorage.setItem("imh_ue_" + schl0, String(besuchNr));
      ueFrei = [erst + 864e5, erst + 2 * 864e5];
      ersterBesuch = besuchNr < 1; zweiterBesuch = besuchNr === 1;
    } catch (e) { ersterBesuch = true; zweiterBesuch = false; besuchNr = 0; ueNeu = false; ueFrei = null; }
    tabTitel("Bauplan", d);
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

    // Das Wachssiegel aus der Vorschau, jetzt als Stempel auf dem fertigen Bauplan
    var kopf = document.querySelector("#step3 .report-head");
    if (kopf && !kopf.querySelector(".cover-wachs")) kopf.insertAdjacentHTML("beforeend", '<div class="cover-wachs" aria-hidden="true"></div>');
    pdfKarte(d, idx);

    // Siegel: Sonne, Mond, Aszendent, Human Design, Lebenszahl. Ein Klick öffnet den Reiter.
    var reihe = $("siegel-reihe");
    if (reihe) {
      reihe.innerHTML = siegelHtml(f);
      reihe.onclick = function (e) {
        var b = e.target.closest(".siegel"); if (!b) return;
        var t = document.querySelector('.rtab[data-rtab="' + b.getAttribute("data-tab") + '"]'); if (t) t.click();
      };
    }

    // Dein roter Faden: der Satz aus dem Entscheidungsweg, unter den Siegeln mit einer goldenen Linie verbunden
    var weg = (f.sections || []).filter(function (x) { return /Entscheidungsweg/.test(x.title || "") && x.takeaway; })[0];
    var altFaden = document.querySelector(".roter-faden"); if (altFaden) altFaden.remove();
    if (reihe && weg) {
      var satz = String(weg.takeaway).replace(/^Dein roter Faden:\s*/, "");
      reihe.insertAdjacentHTML("afterend", '<div class="roter-faden"><span class="rf-linie" aria-hidden="true"></span><p class="rf-titel">Dein roter Faden</p><p class="rf-text">' + esc(satz) + '</p></div>');
      var faden = document.querySelector(".roter-faden");
      if (reduce) faden.classList.add("an"); else sichtbar(faden, function () { faden.classList.add("an"); }, { threshold: .4 });
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
      var st = "", i, a, pts = [], lp = +f.numerology.lifepath, eigene = lp > 9 ? ({ 11: 2, 22: 4, 33: 6 }[lp] || 0) : lp;
      for (i = 0; i < 9; i++) { a = (i * 4 % 9) / 9 * 2 * Math.PI - Math.PI / 2; pts.push(f1(100 + Math.cos(a) * 82) + "," + f1(100 + Math.sin(a) * 82)); }
      for (i = 0; i < 9; i++) {
        a = i / 9 * 2 * Math.PI - Math.PI / 2;
        var x = f1(100 + Math.cos(a) * 82), y = f1(100 + Math.sin(a) * 82);
        st += '<g class="ns-zahl' + (i + 1 === eigene ? " an" : "") + '" style="--i:' + i + '"><circle cx="' + x + '" cy="' + y + '" r="9.5"/><text x="' + x + '" y="' + (+y + 3.6).toFixed(1) + '">' + (i + 1) + '</text></g>';
      }
      w.innerHTML = '<svg viewBox="0 0 200 200" aria-hidden="true"><g class="ns-dreh"><circle cx="100" cy="100" r="98" class="ns-punkte"/></g><circle cx="100" cy="100" r="82" class="ns-ring"/>' +
        '<polygon points="' + pts.join(" ") + '" class="ns-stern" pathLength="1"/><circle cx="100" cy="100" r="52" class="ns-innen"/>' + st + '</svg>';
      big.parentNode.insertBefore(w, big); w.appendChild(big);
      big.setAttribute("data-zahl", big.textContent.trim());
    }

    var calc = document.querySelector("#pane-nu .num-calc");
    if (calc && !calc.querySelector("span")) {
      calc.innerHTML = Array.from(calc.textContent).map(function (ch, i) { return ch === " " ? " " : '<span style="--i:' + i + '">' + esc(ch) + "</span>"; }).join("");
    }
    var py = f.numerology && f.numerology.personal_year;
    if (py && py.number && !document.querySelector("#pane-nu .jahreszyklus")) {
      var kap = [].filter.call(document.querySelectorAll("#pane-nu .cap2"), function (c) { return /persönliches Jahr/i.test(c.textContent); })[0];
      var ziel = kap && kap.nextElementSibling;
      if (ziel) {
        var html = '<div class="jahreszyklus" aria-label="Dein Neun-Jahres-Zyklus"><div class="jz-titel">Dein Neun-Jahres-Zyklus</div><div class="jz-bahn">';
        for (var j = 1; j <= 9; j++) {
          var jahr = py.year + (j - py.number);
          html += '<div class="jz-punkt' + (j < py.number ? " war" : "") + (j === py.number ? " jetzt" : "") + '" style="--i:' + j + '"><span>' + j + '</span><small>' + jahr + '</small></div>';
        }
        ziel.insertAdjacentHTML("afterend", html + '</div></div>');
      }
    }

    // Planetenkarten kennen ihr Zeichen (für Sternbild und Gravur beim Aufklappen)
    // und zeigen die klassische Planetenfigur als Medaillon, das Symbol klein als Abzeichen
    if (na) {
      var karten = na.querySelectorAll(".pcard");
      (f.positions || []).forEach(function (p, k) {
        var c = karten[k]; if (!c) return;
        var z = H.ZEICHEN.indexOf(p.sign); if (z >= 0) c.setAttribute("data-zeichen", z);
        var bild = PLANETBILD[p.key], pico = c.querySelector(".pico");
        if (bild && pico && !pico.querySelector(".pico-figur")) {
          var g = pico.innerHTML;
          pico.classList.add("mit-figur");
          pico.innerHTML = '<span class="pico-figur" style="background-image:url(' + bild + ')"></span><span class="pico-g">' + g + '</span>';
        }
      });
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
    lesezeichen(d);
    heuteImBericht(d);
    heuteFuerDich(d);
    zeichenBrief(d);
    hoerenVorbereiten(d);
    weiter();
    mondkalender(d);
    ueberraschung();
    // Intuitionstyp und Elemente: die Element-Gravuren
    elementbilder(f);
    elementfunken(document.querySelector("#pane-in .intu-sketch"), f.intuition && ELBILD[f.intuition.key]);
    hdBuehne(d);
    natalGruppen(f);
    himmelskarten(f);
    deutungsbuehne();
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

  var PLANETBILD = { Sonne: "/bilder/planet-sonne.webp", Mond: "/bilder/planet-mond.webp", Merkur: "/bilder/planet-merkur.webp", Venus: "/bilder/planet-venus.webp",
    Mars: "/bilder/planet-mars.webp", Jupiter: "/bilder/planet-jupiter.webp", Saturn: "/bilder/planet-saturn.webp", Uranus: "/bilder/planet-uranus.webp",
    Neptun: "/bilder/planet-neptun.webp", Pluto: "/bilder/planet-pluto.webp", Chiron: "/bilder/kapitel-15.webp" };
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

  // Bewegung passend zum Element: Funken steigen, Tropfen fallen, Staub sinkt, Wind zieht
  function elementfunken(box, art) {
    if (!box || reduce || box.querySelector(".intu-funken")) return;
    var c = document.createElement("canvas"); c.className = "intu-funken"; c.setAttribute("aria-hidden", "true"); box.appendChild(c);
    var ctx = c.getContext("2d"), dpr = Math.min(window.devicePixelRatio || 1, 2), W = 0, H = 0, teile = [], raf = 0, an = false, t0 = 0;
    function neu(start) {
      var p = { x: Math.random() * W, y: Math.random() * H, a: Math.random(), s: .4 + Math.random() * 1.2, r: .6 + Math.random() * 1.8, w: Math.random() * 6.28 };
      if (art === "feuer") { p.x = W * (.38 + Math.random() * .24); p.y = start ? Math.random() * H : H * (.62 + Math.random() * .1); p.vy = -(18 + Math.random() * 34); }
      if (art === "wasser") { p.y = start ? Math.random() * H : -6; p.vy = 26 + Math.random() * 30; p.r = 1 + Math.random() * 1.6; }
      if (art === "erde") { p.vy = 4 + Math.random() * 7; }
      if (art === "luft") { p.vx = 30 + Math.random() * 40; p.x = start ? Math.random() * W : -40; p.len = 18 + Math.random() * 40; }
      return p;
    }
    function groesse() { var r = c.getBoundingClientRect(); W = r.width; H = r.height; if (!W) return; c.width = W * dpr; c.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      teile = []; for (var i = 0; i < (art === "luft" ? 14 : 46); i++) teile.push(neu(true)); }
    function lauf(t) {
      raf = 0; if (!an || document.hidden || !c.offsetParent) return;
      var dt = t0 ? Math.min(.05, (t - t0) / 1000) : 0; t0 = t; ctx.clearRect(0, 0, W, H);
      teile.forEach(function (p, i) {
        var sek = t / 1000;
        if (art === "feuer") { p.y += p.vy * dt; p.x += Math.sin(sek * 2 + p.w) * 12 * dt; if (p.y < H * .05) teile[i] = neu(false);
          var al = Math.max(0, Math.min(1, (p.y / H - .05) * 2.2)) * (.5 + .5 * Math.sin(sek * 9 * p.s + p.w));
          ctx.fillStyle = "rgba(255," + (190 + Math.round(50 * p.a)) + ",120," + al.toFixed(3) + ")"; ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 6.283); ctx.fill(); }
        if (art === "wasser") { p.y += p.vy * dt; if (p.y > H + 6) teile[i] = neu(false);
          ctx.strokeStyle = "rgba(205,225,255," + (.25 + .45 * p.a).toFixed(3) + ")"; ctx.lineWidth = p.r * .7; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p.x, p.y - 6 - p.r * 4); ctx.stroke(); }
        if (art === "erde") { p.y += p.vy * dt; p.x += Math.sin(sek * .7 + p.w) * 4 * dt; if (p.y > H + 4) { p.y = -4; p.x = Math.random() * W; }
          ctx.fillStyle = "rgba(236,214,160," + ((.2 + .5 * p.a) * (.6 + .4 * Math.sin(sek * p.s + p.w))).toFixed(3) + ")"; ctx.beginPath(); ctx.arc(p.x, p.y, p.r * .9, 0, 6.283); ctx.fill(); }
        if (art === "luft") { p.x += p.vx * dt; if (p.x > W + 60) teile[i] = neu(false);
          var yy = p.y + Math.sin(p.x / 40 + p.w) * 10, g = ctx.createLinearGradient(p.x - p.len, 0, p.x, 0);
          g.addColorStop(0, "rgba(243,220,166,0)"); g.addColorStop(1, "rgba(243,220,166," + (.25 + .35 * p.a).toFixed(3) + ")");
          ctx.strokeStyle = g; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(p.x - p.len, yy + 3); ctx.quadraticCurveTo(p.x - p.len / 2, yy - 5, p.x, yy); ctx.stroke(); }
      });
      raf = requestAnimationFrame(lauf);
    }
    function los() { if (!raf && an) { t0 = 0; raf = requestAnimationFrame(lauf); } }
    groesse();
    if (window.ResizeObserver) new ResizeObserver(function () { groesse(); los(); }).observe(c);
    if ("IntersectionObserver" in window) new IntersectionObserver(function (e) { an = e[0].isIntersecting; los(); }).observe(c); else { an = true; los(); }
  }

  // Deutung: die alte Himmelskarte steht ruhig hinter den Kapiteln, eine Goldlinie verbindet die Kapitel und füllt sich beim Lesen
  function deutungsbuehne() {
    var de = $("pane-de"); if (!de) return;
    if (!de.querySelector(".de-himmel")) de.insertAdjacentHTML("afterbegin", '<div class="de-himmel" aria-hidden="true"><div></div></div>');
    var story = de.querySelector(".story"); if (!story || story.__linie) return;
    story.__linie = true;
    function fortschritt() {
      if (!de.classList.contains("active")) return;
      var r = story.getBoundingClientRect(), mitte = window.innerHeight * .55;
      story.style.setProperty("--weg", Math.max(0, Math.min(1, (mitte - r.top) / Math.max(1, r.height))).toFixed(4));
    }
    window.addEventListener("scroll", fortschritt, { passive: true });
    window.addEventListener("resize", fortschritt);
    de.addEventListener("toggle", function () { setTimeout(fortschritt, 60); }, true);
    fortschritt();
  }

  var ZENTRUMBILD = { Kopf: "kopf", Ajna: "ajna", Kehle: "kehle", G: "g", Herz: "herz", Milz: "milz", Sakral: "sakral", Solarplexus: "solarplexus", Wurzel: "wurzel" };

  // Human Design: Auftakt mit der Typ-Gravur, drei Schlüssel als Bildkarten, Zentren als Medaillons
  function hdBuehne(d) {
    var f = d.full, t = d.teaser || {}, hd = f.hd, pane = $("pane-hd");
    if (!pane || !hd || pane.querySelector(".hd-buehne")) return;
    var bild = HDBILD[hd.type] ? "/bilder/hd-" + HDBILD[hd.type] + ".webp" : "";
    var flow = (t.signature ? '<span class="gut"><b>Signatur im Flow</b>' + esc(t.signature) + '</span>' : "") +
               (t.not_self ? '<span class="warn"><b>Nicht-Selbst-Thema</b>' + esc(t.not_self) + '</span>' : "");
    var keys = [
      { bild: "/bilder/kapitel-5.webp", l: "Deine Strategie", v: t.strategy || "", d: "" },
      { bild: "/bilder/kapitel-2.webp", l: "Deine innere Autorität", v: hd.authority || "", d: t.authority_desc || "" },
      { bild: "/bilder/kapitel-3.webp", l: "Dein Profil", v: (hd.profile || "") + (t.profile_name ? " · " + t.profile_name : ""), d: t.profile_desc || "" }
    ].filter(function (k) { return k.v; });
    var html = '<section class="hd-buehne"><div class="hd-bild" style="background-image:url(' + bild + ')"></div><div class="hd-text">' +
      '<div class="script-eyebrow">Dein Human-Design-Typ</div><div class="hd-typ">' + esc(hd.type_display || hd.type) + '</div>' +
      (t.type_short ? '<p class="hd-kurz">' + esc(t.type_short) + '</p>' : '') + (flow ? '<div class="hd-flow">' + flow + '</div>' : '') + '</div></section>' +
      '<div class="hd-schluessel">' + keys.map(function (k, i) {
        return '<div class="hd-key" style="--i:' + i + '"><span class="hk-bild" style="background-image:url(' + k.bild + ')"></span><span class="hk-l">' + esc(k.l) + '</span>' +
          '<span class="hk-v">' + esc(k.v) + '</span>' + (k.d ? '<span class="hk-d">' + esc(k.d) + '</span>' : '') + '</div>';
      }).join("") + '</div>';
    pane.insertAdjacentHTML("afterbegin", html);
    // Typ, Strategie, Autorität und Profil stehen jetzt oben; in der Liste bleiben Definition und Inkarnationskreuz
    [].forEach.call(pane.querySelectorAll(".kv"), function (kv) {
      var k = kv.querySelector(".k"); if (k && /^(Typ|Strategie|Autorität|Profil)$/.test(k.textContent.trim())) kv.classList.add("doppelt");
    });
    // Zentren als Medaillons, definiert oder offen als Abzeichen
    [].forEach.call(pane.querySelectorAll(".pcard"), function (c) {
      var pk = c.querySelector(".pk"), pico = c.querySelector(".pico"), name = pk && pk.textContent.trim();
      if (!name || !ZENTRUMBILD[name] || !pico || pico.querySelector(".pico-figur")) return;
      c.setAttribute("data-zentrum", name);
      var def = pico.textContent.indexOf("●") >= 0;
      pico.classList.add("mit-figur", def ? "definiert" : "offen");
      pico.innerHTML = '<span class="pico-figur" style="background-image:url(/bilder/zentrum-' + ZENTRUMBILD[name] + '.webp)"></span><span class="pico-g">' + (def ? "●" : "○") + '</span>';
    });
  }

  // Natalchart: Planeten in Gruppen mit kurzer Einordnung
  var GRUPPEN = [
    { t: "Deine großen Drei", d: "Wer du im Kern bist, was du fühlst und wie du auf andere wirkst.", k: ["Sonne", "Mond", "AC"] },
    { t: "Deine persönlichen Planeten", d: "Wie du denkst, wie du liebst und wie du handelst.", k: ["Merkur", "Venus", "Mars"] },
    { t: "Die großen Lehrer", d: "Wo du wächst und wo du reifst.", k: ["Jupiter", "Saturn"] },
    { t: "Die tiefen Kräfte", d: "Langsame Planeten, die ganze Generationen prägen. In deinem Chart zeigen sie, in welchem Lebensfeld sie bei dir wirken.", k: ["Uranus", "Neptun", "Pluto"] },
    { t: "Achsen und Heilpunkt", d: "Deine Beziehungsachse, deine Berufung, deine Wurzeln und deine Wunde mit ihrer Heilkraft.", k: ["DC", "MC", "IC", "Chiron"] }
  ];
  function natalGruppen(f) {
    var rechts = document.querySelector("#pane-na .sp-rechts") || $("pane-na");
    if (!rechts || rechts.querySelector(".pgruppe")) return;
    var karten = [].slice.call(rechts.querySelectorAll(":scope > .pcard")); if (!karten.length) return;
    var nachKey = {};
    (f.positions || []).forEach(function (p, i) { if (karten[i]) { nachKey[p.key] = karten[i]; karten[i].setAttribute("data-k", p.label === "Aszendent" ? "AC" : p.key); } });
    var vorher = karten[0].previousSibling, rest = karten.slice(), frag = document.createDocumentFragment();
    GRUPPEN.forEach(function (g, gi) {
      var ks = g.k.map(function (k) { return nachKey[k]; }).filter(Boolean); if (!ks.length) return;
      var box = document.createElement("div"); box.className = "pgruppe"; box.style.setProperty("--i", gi);
      box.innerHTML = '<div class="pg-kopf"><span class="pg-nr">' + ("0" + (gi + 1)).slice(-2) + '</span><div><div class="pg-t">' + g.t + '</div><div class="pg-d">' + g.d + '</div></div></div>';
      ks.forEach(function (c) { box.appendChild(c); rest.splice(rest.indexOf(c), 1); });
      frag.appendChild(box);
    });
    if (rest.length) { var sonst = document.createElement("div"); sonst.className = "pgruppe"; rest.forEach(function (c) { sonst.appendChild(c); }); frag.appendChild(sonst); }
    rechts.insertBefore(frag, vorher ? vorher.nextSibling : rechts.firstChild);
  }

  // Rad und Bodygraph sprechen: beim Darüberfahren steht da, was es ist; ein Klick öffnet die passende Karte
  function himmelskarten(f) {
    var by = {}; (f.positions || []).forEach(function (p) { by[p.key] = p; });
    var zen = {}; (f.hd_centers || []).forEach(function (c) { zen[c.name] = c; });
    // Übersicht: Überschrift und Unterschriften für die beiden Karten
    var grid = document.querySelector("#pane-ov .grid2");
    if (grid && !(grid.previousElementSibling && grid.previousElementSibling.classList.contains("karten-kopf"))) {
      var fein = window.matchMedia && window.matchMedia("(hover: hover)").matches;
      grid.insertAdjacentHTML("beforebegin", '<div class="karten-kopf"><div class="script-eyebrow">Zwei Karten deines Himmels</div><p>Links dein Geburtshimmel, rechts dein Energiekörper. ' +
        (fein ? "Fahre über einen Planeten oder ein Zentrum, um zu sehen, was es bei dir bedeutet. Ein Klick öffnet die ganze Erklärung." : "Tippe auf einen Planeten oder ein Zentrum und du landest bei seiner Erklärung.") + '</p></div>');
      var panels = grid.querySelectorAll(".panel");
      if (panels[0]) panels[0].insertAdjacentHTML("beforeend", '<p class="karte-unterschrift">Wo Sonne, Mond und Planeten im Moment deiner Geburt standen.</p>');
      if (panels[1]) panels[1].insertAdjacentHTML("beforeend", '<p class="karte-unterschrift">Welche deiner neun Energiezentren fest sind (gold) und welche offen.</p>');
    }
    var tip = $("himmel-tip");
    if (!tip) { tip = document.createElement("div"); tip.id = "himmel-tip"; tip.className = "himmel-tip"; tip.setAttribute("role", "tooltip"); document.body.appendChild(tip); }
    var step = $("step3"); if (!step || step.__karten) { if (step) step.__daten = { by: by, zen: zen }; return; }
    step.__karten = true; step.__daten = { by: by, zen: zen };
    function inhalt(el) {
      var dd = step.__daten, k = el.getAttribute("data-k"), z = el.getAttribute("data-z");
      if (k && dd.by[k]) { var p = dd.by[k]; return '<b>' + tp(p.sym) + " " + esc(p.label) + " " + tp(p.signSymbol) + " " + esc(p.sign) + '</b><span>' + esc(p.deg) + (p.house ? " · Haus " + p.house : "") + '</span><i>' + esc(p.meaning) + '</i><em>Antippen für mehr</em>'; }
      if (z && dd.zen[z]) { var c = dd.zen[z]; return '<b>' + esc(c.name) + (c.defined ? " · definiert" : " · offen") + '</b><i>' + esc(c.meaning || "") + '</i><em>Antippen für mehr</em>'; }
      return "";
    }
    step.addEventListener("mouseover", function (e) {
      var el = e.target.closest(".gwheel [data-k], .gbody [data-z]"); if (!el) return;
      var h = inhalt(el); if (!h) return;
      tip.innerHTML = h; tip.classList.add("an");
      var hk = el.getAttribute("data-k"); if (hk) [].forEach.call(document.querySelectorAll('.gwheel [data-k="' + hk + '"]'), function (x) { x.classList.add("hl"); });
    });
    function weg() { tip.classList.remove("an"); }
    window.addEventListener("scroll", weg, { passive: true });
    document.addEventListener("click", function (e) { if (e.target.closest(".rtab")) weg(); });
    step.addEventListener("mousemove", function (e) { if (tip.classList.contains("an")) { tip.style.left = Math.min(window.innerWidth - 270, e.clientX + 18) + "px"; tip.style.top = (e.clientY + 18) + "px"; } });
    step.addEventListener("mouseout", function (e) {
      var el = e.target.closest(".gwheel [data-k], .gbody [data-z]"); if (!el) return;
      tip.classList.remove("an"); [].forEach.call(document.querySelectorAll(".gwheel .hl"), function (x) { x.classList.remove("hl"); });
    });
    step.addEventListener("click", function (e) {
      var el = e.target.closest(".gwheel [data-k], .gbody [data-z]"); if (!el) return;
      tip.classList.remove("an");
      var k = el.getAttribute("data-k"), z = el.getAttribute("data-z");
      var tab = k ? "na" : "hd", sel = k ? '#pane-na .pcard[data-k="' + (k === "Aszendent" ? "AC" : k) + '"]' : '#pane-hd .pcard[data-zentrum="' + z + '"]';
      var pane = $("pane-" + tab);
      if (!pane.classList.contains("active")) { var r = document.querySelector('.rtab[data-rtab="' + tab + '"]'); if (r) r.click(); }
      setTimeout(function () { var c = document.querySelector(sel); if (c && !c.classList.contains("open")) c.querySelector(".ph").click(); else if (c) c.scrollIntoView({ behavior: "smooth", block: "center" }); }, 380);
    });
    // Karte im Natalchart hervorheben → Planet im Rad leuchtet
    step.addEventListener("mouseover", function (e) {
      var c = e.target.closest("#pane-na .pcard[data-k]"); if (!c) return;
      var k = c.getAttribute("data-k"); [].forEach.call(document.querySelectorAll('#pane-na .gwheel [data-k="' + k + '"]'), function (x) { x.classList.add("hl"); });
    });
    step.addEventListener("mouseout", function (e) {
      var c = e.target.closest("#pane-na .pcard[data-k]"); if (!c || c.contains(e.relatedTarget)) return;
      [].forEach.call(document.querySelectorAll("#pane-na .gwheel .hl"), function (x) { x.classList.remove("hl"); });
    });
  }

  function elementbilder(f) {
    var it = f.intuition;
    var intu = document.querySelector("#pane-in .intu");
    if (intu && it && ELBILD[it.key]) intu.style.setProperty("--el-bild", "url(/bilder/element-" + ELBILD[it.key] + ".webp)");
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

  /* Symmetrie (Wunsch Denise, 11.10.2026): Zentrierte Texte brechen ausgeglichen um, damit nie ein einzelnes Wort
     allein unter dem Satz steht. Linksbündige Absätze regelt text-wrap: pretty in design.css. Ohne Unterstützung bleibt alles wie vorher. */
  function symmetrie() {
    if (!window.CSS || !CSS.supports || !CSS.supports("text-wrap", "balance")) return;
    [].forEach.call(document.querySelectorAll("p, li, figcaption, .seal-text, .seal-sub, .mail-sub, .wk-text, .wk-titel, .bl-hinweis"), function (el) {
      if (el.style.textWrap || (el.textContent || "").length > 480) return;
      if (getComputedStyle(el).textAlign === "center") el.style.textWrap = "balance";
    });
  }
  function symmetrieGleichUndSpaeter() { symmetrie(); setTimeout(symmetrie, 1600); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", symmetrie); else symmetrie();

  window.Erlebnis = {
    vorschau: function (d) { var r = vorschau(d); symmetrieGleichUndSpaeter(); return r; },
    bericht: function (d) { var r = bericht(d); symmetrieGleichUndSpaeter(); return r; },
    gesendet: function (k) { var r = gesendet(k); setTimeout(symmetrie, 900); return r; }
  };
  // Falls der Bericht schon vor diesem Skript fertig war
  if (window.__bauplan) bericht(window.__bauplan);
})();
