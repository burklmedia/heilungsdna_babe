/* Feedback zum Kosmischen Bauplan (Entwurf 29.10.2026, Zweig feedback-bericht)
   1. Knopf „Feedback“ oben rechts in der Leiste, beim Scrollen angedockt. Sein Goldring füllt sich beim Lesen.
   2. Am Ende jedes Themas eine Frage: „Erkennst du dich hier wieder?“ (erst, wenn das Thema gelesen ist)
   3. Unter dem Bericht die Sterne, danach der Fragebogen im Fenster, eine Frage je Schritt.
   Alles wird erst frei, wenn der Bauplan gelesen ist: LESEZEIT Sekunden aktive Lesezeit und THEMEN_MIN Themen
   bis zum Ende gelesen. Aktiv heißt: Seite sichtbar und in den letzten 45 s gescrollt, getippt oder Bauplan angehört.
   Das Gerät merkt sich den Stand je Bauplan (localStorage imh_rm_<Schlüssel>), angefangene Antworten in
   imh_rm_entwurf_<Schlüssel>. Der Server prüft die Lesezeit noch einmal (/api/feedback, art "bauplan" und "kapitel"). */
(function () {
  "use strict";
  var LESEZEIT = 300, THEMEN_MIN = 3, AKTIV_PAUSE = 45000;
  var THEMEN = [
    { id: "hd", name: "Human Design", min: 40 },
    { id: "na", name: "Natalchart", min: 40 },
    { id: "in", name: "Intuitionstyp", min: 30 },
    { id: "nu", name: "Numerologie", min: 30 },
    { id: "de", name: "Deutung", min: 90 }
  ];
  var STERN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.6l2.83 6.06 6.63.8-4.9 4.55 1.28 6.56L12 17.3l-5.84 3.27 1.28-6.56-4.9-4.55 6.63-.8z"/></svg>';
  var SCHRITTE = [
    { id: "wiedererkannt", art: "sterne", pflicht: true, frage: "Wie sehr hast du dich in deinem Bauplan wiedererkannt?", enden: ["kaum", "total"] },
    { id: "beruehrt", art: "mehr", frage: "Welcher Teil hat dich am meisten berührt?", hinweis: "Du kannst mehrere antippen.",
      optionen: ["Human Design", "Natalchart", "Intuitionstyp", "Numerologie", "Deutung", "Deine größte Stärke", "Deine Schwierigkeiten", "Der Brief zu deinem Sternzeichen"] },
    { id: "verstaendlich", art: "eins", frage: "Wie leicht war dein Bauplan zu lesen?",
      optionen: ["Klar und leicht", "Manches musste ich zweimal lesen", "Oft zu kompliziert für mich"] },
    { id: "aha", art: "text", frage: "Gab es einen Satz, bei dem du kurz innegehalten hast?",
      platzhalter: "Schreib ihn mir gern hier hinein, auch in deinen eigenen Worten." },
    { id: "hilfe", art: "mehr", frage: "Was würde dir jetzt am meisten helfen?", hinweis: "Du kannst mehrere antippen.", anderes: true,
      optionen: ["Ein persönliches Gespräch über meinen Bauplan", "Eine Analyse für mich und einen Menschen, der mir nah ist", "Ein Blick auf mein kommendes Jahr",
        "Kleine Übungen, um meinem Bauchgefühl im Alltag zu folgen", "Erst mal nichts, ich lasse ihn wirken"] },
    { id: "empfehlen", art: "skala", frage: "Würdest du deinen Bauplan einer Freundin zeigen?", enden: ["auf keinen Fall", "auf jeden Fall"],
      nachfrage: "Was hätte gefehlt, damit du ihn weitergibst?" },
    { id: "stimme", art: "stimme", frage: "Magst du erzählen, wie es dir beim Lesen ging?" }
  ];

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function $(s, r) { return (r || document).querySelector(s); }
  function alle(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function lies(k, std) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : std; } catch (e) { return std; } }
  function merk(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  // Anonyme Zähler wie in erlebnis.js: je Sitzung einmal, keine Cookies, keine Namen
  function zaehl(ev) {
    try {
      if (sessionStorage.getItem("imh_ev_" + ev)) return;
      sessionStorage.setItem("imh_ev_" + ev, "1");
      var b = JSON.stringify({ e: ev });
      if (navigator.sendBeacon) navigator.sendBeacon("/api/track", b); else fetch("/api/track", { method: "POST", body: b, keepalive: true });
    } catch (e) {}
  }
  // derselbe Schlüssel je Bauplan wie in erlebnis.js (bauplanSchluessel), damit imh_gelesen_<schl> passt
  function schluessel(d) {
    var b = d.birth || {}, s = [b.date, b.time, b.place, b.name].join("|"), h = 5381;
    for (var i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
    return (h >>> 0).toString(36);
  }

  var d0 = null, schl = "", stand = null, antworten = {}, knoepfe = [], letzteAktivitaet = Date.now(), uhr = null, schritt = -1, opener = null;

  /* ════════ Lesen messen ════════ */
  function s3aktiv() { var s = document.getElementById("step3"); return !!(s && s.classList.contains("active")); }
  function aktiverTab() { var a = $(".rtab.active"); return a ? a.getAttribute("data-rtab") : ""; }
  function geoeffnet() { var g = lies("imh_gelesen_" + schl, []); return g && g.length ? g.length : 0; }
  function themaGelesen(t) {
    if ((stand.tab[t.id] || 0) < t.min) return false;
    return t.id === "de" ? geoeffnet() >= 2 : !!stand.ende[t.id];
  }
  function gelesenListe() { return THEMEN.filter(themaGelesen).map(function (t) { return t.id; }); }
  function istFrei() { return stand.frei || (stand.sek >= LESEZEIT && gelesenListe().length >= THEMEN_MIN); }
  function fortschritt() { return (Math.min(1, stand.sek / LESEZEIT) + Math.min(1, gelesenListe().length / THEMEN_MIN)) / 2; }
  function speichern() { if (schl) merk("imh_rm_" + schl, stand); }

  function tick() {
    if (!stand || document.hidden || !s3aktiv()) return;
    var au = $(".hoeren-box audio"), hoert = au && !au.paused;
    if (!hoert && Date.now() - letzteAktivitaet > AKTIV_PAUSE) return;
    stand.sek++;
    var t = aktiverTab(); if (t && t !== "ov") stand.tab[t] = (stand.tab[t] || 0) + 1;
    if (stand.sek % 5 === 0) speichern();
    aktualisieren();
  }
  function aktiv() { letzteAktivitaet = Date.now(); }

  function aktualisieren() {
    var p = (istFrei() || stand.gesendet) ? 1 : fortschritt();
    knoepfe.forEach(function (k) { var c = k.querySelector(".rm-voll"); if (c) c.style.strokeDashoffset = (100 * (1 - p)).toFixed(2); });
    THEMEN.forEach(function (t) {
      var b = document.querySelector('.rm-kapitel[data-thema="' + t.id + '"]');
      if (b && b.hidden && themaGelesen(t)) { b.hidden = false; if (!reduce) b.classList.add("auf"); }
    });
    if (!stand.frei && istFrei()) freischalten(true);
  }

  /* ════════ Knopf oben rechts ════════ */
  function knopfHtml(extra) {
    return '<button class="rm-knopf' + extra + '" type="button" aria-haspopup="dialog">' +
      '<span class="rm-ring" aria-hidden="true"><svg viewBox="0 0 36 36"><circle class="rm-spur" cx="18" cy="18" r="16" pathLength="100"/>' +
      '<circle class="rm-voll" cx="18" cy="18" r="16" pathLength="100"/></svg><span class="rm-stern">✦</span></span>' +
      '<span class="rm-wort">Feedback</span></button>';
  }
  function knopfZustand() {
    knoepfe.forEach(function (k) {
      k.classList.toggle("rm-frei", istFrei());
      k.classList.toggle("rm-gesendet", !!stand.gesendet);
      k.querySelector(".rm-wort").textContent = stand.gesendet ? "Danke" : "Feedback";
      k.setAttribute("aria-label", stand.gesendet ? "Feedback gesendet" : istFrei() ? "Feedback geben" : "Feedback, wird frei, wenn du deinen Bauplan gelesen hast");
    });
  }
  function knoepfeEinsetzen() {
    alle(".rm-knopf").forEach(function (k) { k.remove(); });
    var leiste = $("#step3 .bericht-leiste");
    if (leiste) leiste.insertAdjacentHTML("beforeend", knopfHtml(" rm-in-leiste"));
    document.body.insertAdjacentHTML("beforeend", knopfHtml(" rm-schwebend"));
    knoepfe = alle(".rm-knopf");
    knoepfe.forEach(function (k) { k.addEventListener("click", function (e) { e.stopPropagation(); knopfKlick(k); }); });
    var schwebend = $(".rm-schwebend");
    // angedockt, sobald die Leiste aus dem Bild ist; nur solange der Bericht offen ist
    if (leiste && "IntersectionObserver" in window) {
      new IntersectionObserver(function (e) { schwebend.classList.toggle("da", !e[0].isIntersecting && s3aktiv()); }).observe(leiste);
    }
    // Klebt die Reiterleiste oben, sitzt der Knopf darunter statt darauf
    function platz() {
      var rt = document.getElementById("rtabs"), top = 10;
      if (rt && s3aktiv()) { var r = rt.getBoundingClientRect(); if (r.top < 24 && r.bottom > 0) top = Math.round(r.bottom + 8); }
      schwebend.style.top = top + "px";
    }
    // Handy: beim Weiterlesen nach unten weg, beim Hochscrollen wieder da
    var y0 = window.scrollY;
    window.addEventListener("scroll", function () {
      platz();
      var y = window.scrollY; if (Math.abs(y - y0) < 10) return;
      if (!s3aktiv()) schwebend.classList.remove("da");
      schwebend.classList.toggle("weg", y > y0 && window.innerWidth <= 900 && !schwebend.classList.contains("halten"));
      y0 = y;
      // Fenster am mitscrollenden Leistenknopf schließen, am angedockten Knopf bleiben sie stehen
      alle('.rm-pop[data-an="leiste"], .rm-blase[data-an="leiste"]').forEach(function (p) { p.remove(); });
    }, { passive: true });
    window.addEventListener("resize", platz);
    platz();
    knopfZustand();
  }
  function knopfKlick(k) {
    if (stand.gesendet) { oeffnen("danke", k); return; }
    if (istFrei()) { oeffnen(antworten._schritt != null ? antworten._schritt : "start", k); return; }
    pop(k);
  }

  // Noch nicht frei: kleines Fenster unter dem Knopf mit dem Lesestand
  function popZu() { alle(".rm-pop, .rm-blase").forEach(function (p) { p.remove(); }); var s = $(".rm-schwebend"); if (s) s.classList.remove("halten"); }
  function anKnopf(el, k) {
    var r = k.getBoundingClientRect();
    el.setAttribute("data-an", k.classList.contains("rm-schwebend") ? "schwebend" : "leiste");
    el.style.top = Math.round(r.bottom + 12) + "px";
    el.style.right = Math.max(12, Math.round(window.innerWidth - r.right)) + "px";
  }
  function pop(k) {
    popZu();
    var gl = gelesenListe(), min = Math.min(LESEZEIT / 60, Math.floor(stand.sek / 60));
    function zeile(name, wert, anteil) {
      return '<div class="rm-pop-zeile"><span>' + name + '</span><b>' + wert + '</b></div><div class="rm-pop-balken"><span style="width:' + (100 * anteil).toFixed(1) + '%"></span></div>';
    }
    document.body.insertAdjacentHTML("beforeend", '<div class="rm-pop" role="dialog" aria-label="Feedback nach dem Lesen">' +
      '<button class="rm-pop-zu" type="button" aria-label="Schließen">×</button>' +
      '<p class="rm-pop-titel">Nimm dir erst Zeit für deinen Bauplan</p>' +
      '<p class="rm-pop-text">Sobald du ein paar Minuten darin gelesen hast, öffnet sich hier dein Feedback. Dann kannst du mir wirklich erzählen, wie er sich für dich anfühlt.</p>' +
      zeile("Lesezeit", min + " von " + (LESEZEIT / 60) + " Minuten", Math.min(1, stand.sek / LESEZEIT)) +
      zeile("Themen", Math.min(gl.length, THEMEN_MIN) + " von " + THEMEN_MIN + " gelesen", Math.min(1, gl.length / THEMEN_MIN)) +
      '<div class="rm-pop-themen">' + THEMEN.map(function (t) { var ja = gl.indexOf(t.id) >= 0; return '<span' + (ja ? ' class="ja"' : '') + '>' + (ja ? "✓ " : "") + t.name + '</span>'; }).join("") + '</div></div>');
    var p = $(".rm-pop"); anKnopf(p, k);
    p.querySelector(".rm-pop-zu").addEventListener("click", popZu);
    if (k.classList.contains("rm-schwebend")) k.classList.add("halten");
    zaehl("rm_gesperrt");
  }

  // Frei geworden: Knopf leuchtet auf, ein Satz von Denise erscheint am Knopf
  function freischalten(jetzt) {
    stand.frei = true; speichern(); knopfZustand();
    untenEinsetzen();
    if (!jetzt) return;
    zaehl("rm_frei");
    knoepfe.forEach(function (k) { if (!reduce) { k.classList.add("rm-blitz"); setTimeout(function () { k.classList.remove("rm-blitz"); }, 4400); } });
    var leisteK = $(".rm-in-leiste"), schwebend = $(".rm-schwebend"), k = leisteK;
    var r = leisteK && leisteK.getBoundingClientRect();
    if (!r || r.bottom < 0 || r.top > window.innerHeight || !s3aktiv()) { k = schwebend; schwebend.classList.add("da", "halten"); schwebend.classList.remove("weg"); }
    popZu(); if (k === schwebend) schwebend.classList.add("halten");
    document.body.insertAdjacentHTML("beforeend", '<button class="rm-blase" type="button">' +
      '<span class="rm-blase-text">Danke, dass du dir Zeit für deinen Bauplan genommen hast. Magst du mir erzählen, wie er für dich war?</span>' +
      '<span class="rm-blase-los">Feedback geben ✦</span></button>');
    var b = $(".rm-blase"); anKnopf(b, k);
    b.addEventListener("click", function () { popZu(); oeffnen("start", k); });
    setTimeout(function () { if (b.parentNode) { b.classList.add("geht"); setTimeout(popZu, 500); } }, 9000);
  }

  /* ════════ Frage am Ende jedes Themas ════════ */
  var KAPITEL_DANKE = { ja: "Schön, das freut mich. 🤍", teils: "Danke dir. Nimm mit, was für dich passt.", nein: "Danke für deine Ehrlichkeit." };
  function kapitelEinsetzen() {
    THEMEN.forEach(function (t) {
      var pane = document.getElementById("pane-" + t.id); if (!pane) return;
      alle(".rm-ende, .rm-kapitel", pane).forEach(function (x) { x.remove(); });
      pane.insertAdjacentHTML("beforeend", '<div class="rm-ende" aria-hidden="true"></div>' +
        '<section class="rm-kapitel" data-thema="' + t.id + '" hidden>' +
        '<p class="rm-k-frage">Erkennst du dich hier wieder?</p>' +
        '<div class="rm-k-wahl" role="group" aria-label="Erkennst du dich in ' + esc(t.name) + ' wieder?">' +
          '<button class="rm-wahl" type="button" data-wert="ja">Ja, total</button>' +
          '<button class="rm-wahl" type="button" data-wert="teils">Teils</button>' +
          '<button class="rm-wahl" type="button" data-wert="nein">Eher nicht</button></div>' +
        '<form class="rm-k-mehr" hidden><input class="rm-feld" maxlength="600" placeholder="Was hat nicht zu dir gepasst? Ein paar Worte reichen." aria-label="Was hat nicht zu dir gepasst?">' +
          '<button class="rm-rund" type="submit" aria-label="Absenden">→</button></form>' +
        '<p class="rm-k-danke" aria-live="polite"></p></section>');
      var block = pane.querySelector(".rm-kapitel");
      kapitelZustand(block, t);
      block.querySelector(".rm-k-wahl").addEventListener("click", function (e) {
        var b = e.target.closest("[data-wert]"); if (!b || stand.stimmen[t.id]) return;
        var w = b.getAttribute("data-wert");
        stand.stimmen[t.id] = w; speichern(); kapitelZustand(block, t, true);
        senden({ art: "kapitel", thema: t.id, wert: w, sek: stand.tab[t.id] || 0 });
        zaehl("rm_kapitel");
      });
      block.querySelector(".rm-k-mehr").addEventListener("submit", function (e) {
        e.preventDefault();
        var text = block.querySelector(".rm-feld").value.trim(); if (text.length < 2) return;
        senden({ art: "kapitel", thema: t.id, wert: "nein", sek: stand.tab[t.id] || 0, text: text, nur_text: true });
        stand.stimmen[t.id + "_text"] = 1; speichern(); kapitelZustand(block, t);
        block.querySelector(".rm-k-danke").textContent = "Danke, das hilft mir sehr. 🤍";
      });
      if ("IntersectionObserver" in window) {
        var ende = pane.querySelector(".rm-ende");
        new IntersectionObserver(function (e) {
          if (e[0].isIntersecting && pane.classList.contains("active") && !stand.ende[t.id]) { stand.ende[t.id] = 1; speichern(); aktualisieren(); }
        }).observe(ende);
      }
    });
  }
  function kapitelZustand(block, t, frisch) {
    var w = stand.stimmen[t.id];
    alle(".rm-wahl", block).forEach(function (b) { b.classList.toggle("an", b.getAttribute("data-wert") === w); b.disabled = !!w; });
    var mehr = block.querySelector(".rm-k-mehr");
    mehr.hidden = !(w === "nein" && !stand.stimmen[t.id + "_text"]);
    block.querySelector(".rm-k-danke").textContent = w ? (stand.stimmen[t.id + "_text"] ? "Danke, das hilft mir sehr. 🤍" : KAPITEL_DANKE[w]) : "";
    if (frisch && w === "nein") setTimeout(function () { var f = mehr.querySelector(".rm-feld"); if (f) f.focus({ preventScroll: true }); }, 60);
  }

  /* ════════ Sterne unter dem Bericht ════════ */
  function sterneHtml(wert, klasse) {
    var s = "";
    for (var i = 1; i <= 5; i++) s += '<button class="rm-stern-k' + (wert >= i ? " an" : "") + '" type="button" role="radio" aria-checked="' + (wert === i) + '" aria-label="' + i + ' von 5" data-wert="' + i + '">' + STERN + '</button>';
    return '<div class="rm-sterne ' + (klasse || "") + '" role="radiogroup" aria-label="Wie sehr hast du dich wiedererkannt?">' + s + '</div>';
  }
  function sterneVorschau(box) {
    function zeig(n) { alle(".rm-stern-k", box).forEach(function (b, i) { b.classList.toggle("vor", i < n); }); }
    box.addEventListener("pointerover", function (e) { var b = e.target.closest(".rm-stern-k"); if (b) zeig(+b.getAttribute("data-wert")); });
    box.addEventListener("pointerleave", function () { zeig(0); });
  }
  function untenEinsetzen() {
    var alt = $(".rm-unten"); if (alt) alt.remove();
    if (!istFrei()) return;
    var ziel = $("#step3 .weiter") || document.getElementById("note"); if (!ziel) return;
    if (stand.gesendet) {
      ziel.insertAdjacentHTML("beforebegin", '<section class="rm-unten fertig"><span class="rm-u-siegel" aria-hidden="true"></span><div class="script-eyebrow">Danke für dein Feedback</div><p class="rm-u-lead">Es ist bei mir angekommen. 🤍</p></section>');
      return;
    }
    ziel.insertAdjacentHTML("beforebegin", '<section class="rm-unten"><div class="script-eyebrow">Wie war dein Bauplan für dich?</div>' +
      '<p class="rm-u-lead">Tipp an, wie sehr du dich darin wiedererkannt hast. Danach frage ich dich noch ein paar kurze Dinge, das dauert etwa eine Minute.</p>' +
      sterneHtml(antworten.wiedererkannt || 0) + '<div class="rm-enden"><span>kaum</span><span>total</span></div></section>');
    var box = $(".rm-unten .rm-sterne"); sterneVorschau(box);
    box.addEventListener("click", function (e) {
      var b = e.target.closest(".rm-stern-k"); if (!b) return;
      antworten.wiedererkannt = +b.getAttribute("data-wert"); entwurf();
      alle(".rm-stern-k", box).forEach(function (x, i) { x.classList.toggle("an", i < antworten.wiedererkannt); });
      zaehl("rm_sterne");
      setTimeout(function () { oeffnen(1, b); }, reduce ? 0 : 320);
    });
  }

  /* ════════ Fragebogen im Fenster ════════ */
  function entwurf() { if (schl) merk("imh_rm_entwurf_" + schl, antworten); }
  function oeffnen(wohin, von) {
    popZu();
    opener = von || null;
    var f = $(".rm-fenster");
    if (!f) {
      document.body.insertAdjacentHTML("beforeend", '<div class="rm-fenster" role="dialog" aria-modal="true" aria-labelledby="rm-titel">' +
        '<div class="rm-schleier"></div><div class="rm-karte"><div class="rm-griff" aria-hidden="true"></div>' +
        '<header class="rm-kopf"><button class="rm-rund rm-zurueck" type="button" aria-label="Zurück">←</button>' +
        '<div class="rm-segmente" aria-hidden="true">' + SCHRITTE.map(function () { return "<span></span>"; }).join("") + '</div>' +
        '<button class="rm-rund rm-zu" type="button" aria-label="Schließen">×</button></header>' +
        '<div class="rm-inhalt"></div></div></div>');
      f = $(".rm-fenster");
      f.querySelector(".rm-schleier").addEventListener("click", schliessen);
      f.querySelector(".rm-zu").addEventListener("click", schliessen);
      f.querySelector(".rm-zurueck").addEventListener("click", function () { zeige(schritt <= 0 ? "start" : schritt - 1); });
      f.addEventListener("keydown", tasten);
      document.documentElement.classList.add("rm-offen");
      setTimeout(function () { f.classList.add("auf"); }, 20);
      zaehl("rm_offen");
    }
    zeige(wohin);
  }
  function schliessen() {
    var f = $(".rm-fenster"); if (!f) return;
    if (typeof schritt === "number" && schritt >= 0 && schritt < SCHRITTE.length) { antworten._schritt = schritt; entwurf(); }
    f.classList.remove("auf");
    document.documentElement.classList.remove("rm-offen");
    setTimeout(function () { f.remove(); }, reduce ? 0 : 450);
    if (opener && document.contains(opener)) opener.focus({ preventScroll: true });
  }
  function tasten(e) {
    if (e.key === "Escape") { schliessen(); return; }
    if (e.key !== "Tab") return;
    var f = alle(".rm-karte button:not([disabled]), .rm-karte input, .rm-karte textarea", $(".rm-fenster")).filter(function (x) { return x.offsetParent !== null; });
    if (!f.length) return;
    if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
    else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
  }

  function zeige(wohin) {
    var f = $(".rm-fenster"), inhalt = f.querySelector(".rm-inhalt");
    schritt = wohin;
    var frage = typeof wohin === "number";
    f.querySelector(".rm-segmente").style.visibility = frage ? "visible" : "hidden";
    f.querySelector(".rm-zurueck").style.visibility = frage ? "visible" : "hidden";
    alle(".rm-segmente span", f).forEach(function (s, i) { s.className = !frage ? "" : i < wohin ? "fertig" : i === wohin ? "jetzt" : ""; });
    if (wohin === "start") inhalt.innerHTML = startHtml();
    else if (wohin === "danke") inhalt.innerHTML = dankeHtml();
    else inhalt.innerHTML = frageHtml(SCHRITTE[wohin], wohin);
    var erstes = inhalt.querySelector(".rm-cta, .rm-option, .rm-chip, .rm-stern-k, .rm-text");
    if (erstes && !("ontouchstart" in window)) erstes.focus({ preventScroll: true });
    inhalt.parentNode.scrollTop = 0;
    verdrahten(wohin, inhalt);
  }

  function startHtml() {
    return '<div class="rm-schritt rm-mitte"><img class="rm-bild" src="/bilder/denise-ki-rund-220.webp" srcset="/bilder/denise-ki-rund-440.webp 2x" alt="" width="92" height="92">' +
      '<h2 class="rm-frage" id="rm-titel">Darf ich dich kurz etwas fragen?</h2>' +
      '<p class="rm-lead">Sieben kurze Fragen, fast alles zum Antippen. Deine ehrliche Antwort hilft mir, den Kosmischen Bauplan für dich und andere Frauen besser zu machen.</p>' +
      '<div class="rm-fuss"><button class="rm-cta" type="button" data-los>Los geht\'s ✦</button></div><p class="rm-klein">Dauert etwa eine Minute</p></div>';
  }
  function dankeHtml() {
    var freundin = antworten.empfehlen >= 9 && $(".wk-teilen");
    var schon = stand.gesendet && !antworten._frisch;
    return '<div class="rm-schritt rm-mitte"><span class="rm-siegel" aria-hidden="true"></span>' +
      '<h2 class="rm-frage" id="rm-titel">' + (schon ? "Danke für dein Feedback." : "Danke, das bedeutet mir viel.") + '</h2>' +
      '<p class="rm-lead">' + (schon ? "Du hast mir schon geantwortet. 🤍" : "Deine Rückmeldung ist bei mir angekommen. 🤍") + '</p>' +
      (freundin && !schon ? '<p class="rm-lead leise">Wenn du magst, schenk deinen Bauplan einer Freundin. Sie bekommt dann ihren eigenen.</p>' +
        '<div class="rm-fuss"><button class="rm-cta" type="button" data-freundin>Einer Freundin schenken ✦</button></div>' : "") +
      '<div class="rm-fuss"><button class="rm-cta' + (freundin && !schon ? " leise" : "") + '" type="button" data-zurueck>Zurück zu deinem Bauplan</button></div></div>';
  }
  function frageHtml(s, i) {
    var w = antworten[s.id], h = '<div class="rm-schritt"><p class="rm-zaehler">' + (i + 1) + ' von ' + SCHRITTE.length + '</p>' +
      '<h2 class="rm-frage" id="rm-titel">' + esc(s.frage) + '</h2>';
    if (s.id === "beruehrt" && w === undefined) {
      w = antworten.beruehrt = THEMEN.filter(function (t) { return stand.stimmen[t.id] === "ja"; }).map(function (t) { return t.name; });
      if (w.length) h += '<p class="rm-hinweis">Deine Ja-Antworten aus den Themen habe ich schon markiert. Du kannst mehrere antippen.</p>';
      else if (s.hinweis) h += '<p class="rm-hinweis">' + s.hinweis + '</p>';
    } else if (s.hinweis) h += '<p class="rm-hinweis">' + s.hinweis + '</p>';
    if (s.art === "sterne") h += sterneHtml(w || 0, "gross") + '<div class="rm-enden">' + s.enden.map(function (x) { return "<span>" + x + "</span>"; }).join("") + '</div>';
    if (s.art === "mehr") {
      h += '<div class="rm-chips">' + s.optionen.map(function (o) { return '<button class="rm-chip' + ((w || []).indexOf(o) >= 0 ? " an" : "") + '" type="button" aria-pressed="' + ((w || []).indexOf(o) >= 0) + '" data-wert="' + esc(o) + '">' + esc(o) + '</button>'; }).join("") + '</div>';
      if (s.anderes) h += '<input class="rm-feld rm-anderes" maxlength="200" placeholder="Etwas anderes? Schreib es hier hinein." aria-label="Etwas anderes" value="' + esc(antworten[s.id + "_anderes"] || "") + '">';
    }
    if (s.art === "eins") h += '<div class="rm-optionen">' + s.optionen.map(function (o) { return '<button class="rm-option' + (w === o ? " an" : "") + '" type="button" data-wert="' + esc(o) + '">' + esc(o) + '</button>'; }).join("") + '</div>';
    if (s.art === "text") h += '<textarea class="rm-text" maxlength="1000" rows="4" placeholder="' + esc(s.platzhalter) + '" aria-label="' + esc(s.frage) + '">' + esc(w || "") + '</textarea>';
    if (s.art === "skala") {
      var z = ""; for (var n = 0; n <= 10; n++) z += '<button class="rm-zahl' + (w === n ? " an" : "") + '" type="button" data-wert="' + n + '" aria-label="' + n + ' von 10">' + n + '</button>';
      h += '<div class="rm-skala">' + z + '</div><div class="rm-enden">' + s.enden.map(function (x) { return "<span>" + x + "</span>"; }).join("") + '</div>' +
        '<div class="rm-nachfrage"' + (typeof w === "number" && w <= 6 ? "" : " hidden") + '><p class="rm-hinweis">' + esc(s.nachfrage) + '</p>' +
        '<textarea class="rm-text klein" maxlength="800" rows="2" placeholder="Ein paar Worte reichen." aria-label="' + esc(s.nachfrage) + '">' + esc(antworten.empfehlen_fehlt || "") + '</textarea></div>';
    }
    if (s.art === "stimme") {
      var name = antworten.vorname != null ? antworten.vorname : ((d0 && d0.birth && d0.birth.name) || "");
      h += '<p class="rm-hinweis">Zwei, drei Sätze reichen. Mit deinem Okay zeige ich sie mit deinem Vornamen auf meiner Seite, damit andere Frauen einen ehrlichen Eindruck bekommen.</p>' +
        '<textarea class="rm-text" maxlength="1200" rows="4" placeholder="Wie ging es dir beim Lesen?" aria-label="Wie ging es dir beim Lesen?">' + esc(antworten.stimme_text || "") + '</textarea>' +
        '<label class="rm-haken"><input type="checkbox" class="rm-ok"' + (antworten.stimme_ok ? " checked" : "") + '><span>Ja, du darfst das mit meinem Vornamen auf deiner Seite zeigen.</span></label>' +
        '<input class="rm-feld rm-vorname" maxlength="40" placeholder="Dein Vorname" aria-label="Dein Vorname" value="' + esc(name) + '"' + (antworten.stimme_ok ? "" : " hidden") + '>' +
        '<p class="rm-fehler" aria-live="polite"></p>';
    }
    return h + '<div class="rm-fuss"><button class="rm-cta" type="button" data-weiter></button></div></div>';
  }

  function beantwortet(s) {
    var w = antworten[s.id];
    if (s.art === "mehr") return (w && w.length) || !!(antworten[s.id + "_anderes"] || "").trim();
    if (s.art === "text") return !!(w || "").trim();
    if (s.art === "stimme") return !!(antworten.stimme_text || "").trim();
    return w !== undefined && w !== null && w !== "";
  }
  function verdrahten(wohin, inhalt) {
    var los = inhalt.querySelector("[data-los]"); if (los) los.addEventListener("click", function () { zaehl("rm_start"); zeige(0); });
    var zur = inhalt.querySelector("[data-zurueck]"); if (zur) zur.addEventListener("click", schliessen);
    var fr = inhalt.querySelector("[data-freundin]");
    if (fr) fr.addEventListener("click", function () { schliessen(); var t = $(".wk-teilen"); if (t) setTimeout(function () { t.click(); }, reduce ? 0 : 460); });
    if (typeof wohin !== "number") return;
    var s = SCHRITTE[wohin], weiter = inhalt.querySelector("[data-weiter]"), letzte = wohin === SCHRITTE.length - 1;
    function knopf() {
      var ok = beantwortet(s);
      weiter.textContent = letzte ? "Absenden ✦" : ok || s.pflicht ? "Weiter ✦" : "Überspringen";
      weiter.classList.toggle("leise", !ok && !s.pflicht && !letzte);
      weiter.disabled = !!s.pflicht && !ok;
    }
    function vor(nach) { entwurf(); setTimeout(function () { zeige(wohin + 1); }, reduce ? 0 : (nach || 0)); }
    weiter.addEventListener("click", function () { if (letzte) abschicken(weiter); else vor(); });
    if (s.art === "sterne") {
      var box = inhalt.querySelector(".rm-sterne"); sterneVorschau(box);
      box.addEventListener("click", function (e) {
        var b = e.target.closest(".rm-stern-k"); if (!b) return;
        antworten[s.id] = +b.getAttribute("data-wert");
        alle(".rm-stern-k", box).forEach(function (x, i) { x.classList.toggle("an", i < antworten[s.id]); x.setAttribute("aria-checked", String(i + 1 === antworten[s.id])); });
        knopf(); vor(380);
      });
    }
    if (s.art === "mehr") {
      inhalt.querySelector(".rm-chips").addEventListener("click", function (e) {
        var b = e.target.closest(".rm-chip"); if (!b) return;
        var o = b.getAttribute("data-wert"), l = antworten[s.id] || [], i = l.indexOf(o);
        if (i >= 0) l.splice(i, 1); else l.push(o);
        antworten[s.id] = l; b.classList.toggle("an", i < 0); b.setAttribute("aria-pressed", String(i < 0)); entwurf(); knopf();
      });
      var an = inhalt.querySelector(".rm-anderes");
      if (an) an.addEventListener("input", function () { antworten[s.id + "_anderes"] = an.value; entwurf(); knopf(); });
    }
    if (s.art === "eins") {
      inhalt.querySelector(".rm-optionen").addEventListener("click", function (e) {
        var b = e.target.closest(".rm-option"); if (!b) return;
        antworten[s.id] = b.getAttribute("data-wert");
        alle(".rm-option", inhalt).forEach(function (x) { x.classList.toggle("an", x === b); });
        knopf(); vor(380);
      });
    }
    if (s.art === "text") {
      var ta = inhalt.querySelector(".rm-text");
      ta.addEventListener("input", function () { antworten[s.id] = ta.value; entwurf(); knopf(); });
    }
    if (s.art === "skala") {
      var nf = inhalt.querySelector(".rm-nachfrage"), nt = nf.querySelector(".rm-text");
      inhalt.querySelector(".rm-skala").addEventListener("click", function (e) {
        var b = e.target.closest(".rm-zahl"); if (!b) return;
        antworten[s.id] = +b.getAttribute("data-wert");
        alle(".rm-zahl", inhalt).forEach(function (x) { x.classList.toggle("an", x === b); });
        knopf();
        if (antworten[s.id] <= 6) { nf.hidden = false; setTimeout(function () { nt.focus({ preventScroll: true }); nf.scrollIntoView({ block: "nearest" }); }, 60); }
        else { nf.hidden = true; vor(380); }
      });
      nt.addEventListener("input", function () { antworten.empfehlen_fehlt = nt.value; entwurf(); });
    }
    if (s.art === "stimme") {
      var st = inhalt.querySelector(".rm-text"), ok = inhalt.querySelector(".rm-ok"), vn = inhalt.querySelector(".rm-vorname");
      if (antworten.vorname == null) antworten.vorname = vn.value;
      st.addEventListener("input", function () { antworten.stimme_text = st.value; entwurf(); knopf(); });
      ok.addEventListener("change", function () { antworten.stimme_ok = ok.checked; vn.hidden = !ok.checked; if (ok.checked) vn.focus({ preventScroll: true }); entwurf(); });
      vn.addEventListener("input", function () { antworten.vorname = vn.value; entwurf(); });
    }
    knopf();
  }

  function profil(d) {
    var f = (d && d.full) || {}, hd = f.hd || {}, so = (f.positions || []).filter(function (p) { return p.key === "Sonne"; })[0];
    return { typ: hd.type || "", autoritaet: hd.authority || "", profil: hd.profile || "", intuition: (f.intuition || {}).archetype || "",
      sonne: so ? so.sign : "", lebenszahl: (f.numerology || {}).lifepath || "" };
  }
  function senden(daten) {
    var t = ""; try { t = sessionStorage.getItem("imh_t") || ""; } catch (e) {}
    if (t) daten.t = t;
    daten.profil = profil(d0);
    return fetch("/api/feedback", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(daten) })
      .then(function (r) { return r.json().catch(function () { return {}; }); });
  }
  function abschicken(knopfEl) {
    var fehler = $(".rm-fenster .rm-fehler");
    if (antworten.stimme_ok && !(antworten.vorname || "").trim()) { fehler.textContent = "Schreib mir noch deinen Vornamen dazu, oder nimm das Häkchen weg."; return; }
    var a = {}; Object.keys(antworten).forEach(function (k) { if (k.charAt(0) !== "_") a[k] = antworten[k]; });
    if (!a.stimme_ok) delete a.vorname;
    knopfEl.disabled = true; knopfEl.textContent = "Wird gesendet …"; fehler.textContent = "";
    senden({ art: "bauplan", antworten: a, kapitel: stand.stimmen, lesen: { sek: stand.sek, themen: gelesenListe(), geoeffnet: geoeffnet() } })
      .then(function (d) {
        if (d && d.ok) {
          stand.gesendet = true; speichern(); antworten._frisch = true;
          zaehl("rm_gesendet"); knopfZustand(); aktualisieren(); untenEinsetzen(); zeige("danke");
          merk("imh_rm_entwurf_" + schl, { empfehlen: antworten.empfehlen });
          return;
        }
        fehler.textContent = (d && d.message) || "Das hat gerade nicht geklappt. Bitte versuch es gleich noch einmal.";
        knopfEl.disabled = false; knopfEl.textContent = "Absenden ✦";
      })
      .catch(function () { fehler.textContent = "Keine Verbindung. Bitte versuch es gleich noch einmal."; knopfEl.disabled = false; knopfEl.textContent = "Absenden ✦"; });
  }

  /* ════════ Start, wenn der Bericht steht ════════ */
  function start(d) {
    if (!d || !d.full) return;
    d0 = d; schl = schluessel(d);
    var alt = lies("imh_rm_" + schl, {}) || {}, leer = { sek: 0, tab: {}, ende: {}, frei: false, gesendet: false, stimmen: {} };
    Object.keys(leer).forEach(function (k) { if (alt[k] === undefined) alt[k] = leer[k]; });
    stand = alt; antworten = lies("imh_rm_entwurf_" + schl, {}) || {};
    popZu();
    knoepfeEinsetzen(); kapitelEinsetzen();
    if (istFrei()) freischalten(false);
    aktualisieren();
    if (!uhr) {
      uhr = setInterval(tick, 1000);
      ["scroll", "wheel", "touchstart", "pointerdown", "keydown", "mousemove"].forEach(function (ev) { window.addEventListener(ev, aktiv, { passive: true }); });
      document.addEventListener("click", function (e) { if (!e.target.closest(".rm-pop, .rm-knopf, .rm-blase")) popZu(); });
      document.addEventListener("keydown", function (e) { if (e.key === "Escape") popZu(); });
      window.addEventListener("pagehide", speichern);
    }
  }
  window.Rueckmeldung = { start: start };
  if (window.__bauplan && s3aktiv()) start(window.__bauplan);
})();
