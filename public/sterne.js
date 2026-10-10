/* Bewegte Sterne für die Nachtbänder: jedes Element mit data-sterne bekommt ein
   eigenes Sternenfeld. Sterne funkeln einzeln, das Feld driftet langsam, selten
   zieht eine Sternschnuppe vorbei. Läuft nur, solange das Band sichtbar ist.
   Bei „Bewegung reduzieren“ steht das Feld still. */
(function () {
  "use strict";
  var bands = document.querySelectorAll("[data-sterne]");
  if (!bands.length || !window.HTMLCanvasElement) return;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var GOLD = "243,217,164", WEISS = "255,244,220";

  function rand(a, b) { return a + Math.random() * (b - a); }

  function feld(el) {
    var c = document.createElement("canvas");
    c.className = "sternfeld";
    c.setAttribute("aria-hidden", "true");
    el.insertBefore(c, el.firstChild);
    el.classList.add("sterne-live");
    var ctx = c.getContext("2d"), dpr = Math.min(window.devicePixelRatio || 1, 2);
    var W = 0, H = 0, sterne = [], funkler = [], schnuppe = null, naechste = 0, sichtbar = false, raf = 0, zuletzt = 0;

    function saeen() {
      sterne = []; funkler = [];
      var n = Math.round(W * H / 3600);
      for (var i = 0; i < n; i++) {
        var r = Math.random() < .8 ? rand(.55, 1.05) : rand(1.05, 1.7);
        sterne.push({ x: rand(0, W), y: rand(0, H), r: r, a: rand(.4, 1), s: rand(.5, 1.8), p: rand(0, 6.283),
                      v: 1.5 + r * 3, gold: Math.random() < .14 });
      }
      for (var k = 0; k < Math.max(3, Math.round(n / 45)); k++) {
        funkler.push({ x: rand(0, W), y: rand(0, H), g: rand(3, 5.5), s: rand(.25, .6), p: rand(0, 6.283) });
      }
    }
    function groesse() {
      var r = el.getBoundingClientRect();
      if (!r.width || !r.height) return;
      W = r.width; H = r.height;
      c.width = Math.round(W * dpr); c.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      saeen();
      bild(performance.now(), 0);           // sofort ein erstes Bild, auch ohne Animation
    }
    function stern4(x, y, g, a) {
      ctx.fillStyle = "rgba(" + GOLD + "," + a + ")";
      ctx.beginPath();
      ctx.moveTo(x, y - g); ctx.lineTo(x + g * .22, y - g * .22); ctx.lineTo(x + g, y); ctx.lineTo(x + g * .22, y + g * .22);
      ctx.lineTo(x, y + g); ctx.lineTo(x - g * .22, y + g * .22); ctx.lineTo(x - g, y); ctx.lineTo(x - g * .22, y - g * .22);
      ctx.closePath(); ctx.fill();
    }
    function bild(t, dt) {
      ctx.clearRect(0, 0, W, H);
      var sek = t / 1000;
      for (var i = 0; i < sterne.length; i++) {
        var s = sterne[i];
        s.x -= s.v * dt; s.y -= s.v * .22 * dt;
        if (s.x < -2) s.x += W + 4;
        if (s.y < -2) s.y += H + 4;
        var a = s.a * (.68 + .32 * Math.sin(sek * s.s + s.p));
        ctx.fillStyle = "rgba(" + (s.gold ? GOLD : WEISS) + "," + a.toFixed(3) + ")";
        ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, 6.283); ctx.fill();
      }
      for (var k = 0; k < funkler.length; k++) {
        var f = funkler[k], puls = .5 + .5 * Math.sin(sek * f.s * 2 + f.p);
        f.x -= 3 * dt; if (f.x < -8) f.x += W + 16;
        stern4(f.x, f.y, f.g * (.7 + .3 * puls), (.25 + .55 * puls).toFixed(3));
      }
      if (schnuppe) {
        var q = schnuppe; q.x += q.vx * dt; q.y += q.vy * dt; q.leben -= dt;
        var alpha = Math.max(0, Math.min(1, q.leben / .35));
        var gr = ctx.createLinearGradient(q.x, q.y, q.x - q.vx * .22, q.y - q.vy * .22);
        gr.addColorStop(0, "rgba(" + WEISS + "," + (.9 * alpha).toFixed(3) + ")");
        gr.addColorStop(1, "rgba(" + GOLD + ",0)");
        ctx.strokeStyle = gr; ctx.lineWidth = 1.2; ctx.lineCap = "round";
        ctx.beginPath(); ctx.moveTo(q.x, q.y); ctx.lineTo(q.x - q.vx * .22, q.y - q.vy * .22); ctx.stroke();
        if (q.leben <= 0) schnuppe = null;
      }
    }
    function lauf(t) {
      raf = 0;
      if (!sichtbar || document.hidden) return;
      if (!zuletzt) zuletzt = t;
      var dt = (t - zuletzt) / 1000;
      if (dt >= 1 / 30) {                       // etwa 30 Bilder pro Sekunde reichen
        zuletzt = t;
        if (!schnuppe && t > naechste) {
          var tempo = rand(420, 560);
          schnuppe = { x: rand(W * .35, W), y: rand(0, H * .35), vx: -tempo, vy: tempo * .32, leben: rand(.7, 1.1) };
          naechste = t + rand(7000, 14000);
        }
        bild(t, Math.min(dt, .1));
      }
      raf = requestAnimationFrame(lauf);
    }
    function start() { if (!raf && !reduce) { zuletzt = 0; raf = requestAnimationFrame(lauf); } }

    groesse();
    naechste = performance.now() + rand(3000, 8000);
    if (window.ResizeObserver) new ResizeObserver(groesse).observe(el);
    else window.addEventListener("resize", groesse);
    if (window.IntersectionObserver) {
      new IntersectionObserver(function (e) { sichtbar = e[0].isIntersecting; if (sichtbar) start(); }, { rootMargin: "100px" }).observe(el);
    } else { sichtbar = true; start(); }
    document.addEventListener("visibilitychange", function () { if (!document.hidden && sichtbar) start(); });
  }

  bands.forEach(feld);
})();
