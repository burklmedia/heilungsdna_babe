/* Himmel im Browser: Planetenstände für einen Zeitpunkt, Mondphase, Sonnenzeichen
   und die zwölf Tierkreis-Sternbilder als Zeichnung.
   Nur für die Gestaltung der Seite. Der Bauplan selbst wird weiter auf dem Server
   mit der Swiss Ephemeris berechnet.
   Genauigkeit: Sonne und Mond auf wenige Bogenminuten, Planeten über die
   Bahnelemente des JPL (Standish) auf Bruchteile eines Grades. */
(function () {
  "use strict";
  var RAD = Math.PI / 180;
  function norm(x) { x %= 360; return x < 0 ? x + 360 : x; }
  function sin(d) { return Math.sin(d * RAD); }
  function cos(d) { return Math.cos(d * RAD); }

  function jd(date) { return date.getTime() / 86400000 + 2440587.5; }
  function jahrhunderte(date) { return (jd(date) - 2451545.0) / 36525; }

  // Sonne (Meeus, Kap. 25), scheinbare Länge
  function sonne(T) {
    var L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T;
    var M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T;
    var C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * sin(M) + (0.019993 - 0.000101 * T) * sin(2 * M) + 0.000289 * sin(3 * M);
    return norm(L0 + C - 0.00569 - 0.00478 * sin(125.04 - 1934.136 * T));
  }

  // Mond (Meeus, Kap. 47, die größten Glieder)
  var MOND = [
    [0, 0, 1, 0, 6288774], [2, 0, -1, 0, 1274027], [2, 0, 0, 0, 658314], [0, 0, 2, 0, 213618],
    [0, 1, 0, 0, -185116], [0, 0, 0, 2, -114332], [2, 0, -2, 0, 58793], [2, -1, -1, 0, 57066],
    [2, 0, 1, 0, 53322], [2, -1, 0, 0, 45758], [0, 1, -1, 0, -40923], [1, 0, 0, 0, -34720],
    [0, 1, 1, 0, -30383], [2, 0, 0, -2, 15327], [0, 0, 1, 2, -12528], [0, 0, 1, -2, 10980],
    [4, 0, -1, 0, 10675], [0, 0, 3, 0, 10034], [4, 0, -2, 0, 8548], [2, 1, -1, 0, -7888],
    [2, 1, 0, 0, -6766], [1, 0, -1, 0, -5163], [1, 1, 0, 0, 4987], [2, -1, 1, 0, 4036],
    [2, 0, 2, 0, 3994], [4, 0, 0, 0, 3861], [2, 0, -3, 0, 3665], [0, 1, -2, 0, -2689],
    [2, 0, -1, 2, -2602], [2, -1, -2, 0, 2390], [1, 0, 1, 0, -2348], [2, -2, 0, 0, 2236],
    [0, 1, 2, 0, -2120], [0, 2, 0, 0, -2069], [2, -2, -1, 0, 2048], [2, 0, 1, -2, -1773],
    [2, 0, 0, 2, -1595], [4, -1, -1, 0, 1215], [0, 0, 2, 2, -1110], [3, 0, -1, 0, -892],
    [2, 1, 1, 0, -810], [4, -1, -2, 0, 759], [0, 2, -1, 0, -713], [2, 2, -1, 0, -700],
    [2, 1, -2, 0, 691], [2, -1, 0, -2, 596], [4, 0, 1, 0, 549], [0, 0, 4, 0, 537],
    [4, -1, 0, 0, 520], [1, 0, -2, 0, -487], [2, 1, 0, -2, -399], [0, 0, 2, -2, -381],
    [1, 1, 1, 0, 351], [3, 0, -2, 0, -340], [4, 0, -3, 0, 330], [2, -1, 2, 0, 327],
    [0, 2, 1, 0, -323], [1, 1, -1, 0, 299], [2, 0, 3, 0, 294]
  ];
  function mond(T) {
    var Lp = 218.3164477 + 481267.88123421 * T - 0.0015786 * T * T;
    var D = 297.8501921 + 445267.1114034 * T - 0.0018819 * T * T;
    var M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T;
    var Mp = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T;
    var F = 93.2720950 + 483202.0175233 * T - 0.0036539 * T * T;
    var E = 1 - 0.002516 * T - 0.0000074 * T * T;
    var A1 = 119.75 + 131.849 * T, A2 = 53.09 + 479264.290 * T;
    var s = 0;
    for (var i = 0; i < MOND.length; i++) {
      var t = MOND[i], k = t[4];
      if (Math.abs(t[1]) === 1) k *= E; else if (Math.abs(t[1]) === 2) k *= E * E;
      s += k * sin(t[0] * D + t[1] * M + t[2] * Mp + t[3] * F);
    }
    s += 3958 * sin(A1) + 1962 * sin(Lp - F) + 318 * sin(A2);
    var nut = -0.00478 * sin(125.04 - 1934.136 * T);
    return norm(Lp + s / 1e6 + nut);
  }

  // Planeten aus Bahnelementen (JPL, Standish: a, e, I, L, Länge des Perihels, Knoten; je Wert und Änderung pro Jahrhundert)
  var BAHN = {
    erde:    [1.00000261, 0.00000562, 0.01671123, -0.00004392, -0.00001531, -0.01294668, 100.46457166, 35999.37244981, 102.93768193, 0.32327364, 0, 0],
    Merkur:  [0.38709927, 0.00000037, 0.20563593, 0.00001906, 7.00497902, -0.00594749, 252.25032350, 149472.67411175, 77.45779628, 0.16047689, 48.33076593, -0.12534081],
    Venus:   [0.72333566, 0.00000390, 0.00677672, -0.00004107, 3.39467605, -0.00078890, 181.97909950, 58517.81538729, 131.60246718, 0.00268329, 76.67984255, -0.27769418],
    Mars:    [1.52371034, 0.00001847, 0.09339410, 0.00007882, 1.84969142, -0.00813131, -4.55343205, 19140.30268499, -23.94362959, 0.44441088, 49.55953891, -0.29257343],
    Jupiter: [5.20288700, -0.00011607, 0.04838624, -0.00013253, 1.30439695, -0.00183714, 34.39644051, 3034.74612775, 14.72847983, 0.21252668, 100.47390909, 0.20469106],
    Saturn:  [9.53667594, -0.00125060, 0.05386179, -0.00050991, 2.48599187, 0.00193609, 49.95424423, 1222.49362201, 92.59887831, -0.41897216, 113.66242448, -0.28867794],
    Uranus:  [19.18916464, -0.00196176, 0.04725744, -0.00004397, 0.77263783, -0.00242939, 313.23810451, 428.48202785, 170.95427630, 0.40805281, 74.01692503, 0.04240589],
    Neptun:  [30.06992276, 0.00026291, 0.00859048, 0.00005105, 1.77004347, 0.00035372, -55.12002969, 218.45945325, 44.96476227, -0.32241464, 131.78422574, -0.00508664],
    Pluto:   [39.48211675, -0.00031596, 0.24882730, 0.00005170, 17.14001206, 0.00004818, 238.92903833, 145.20780515, 224.06891629, -0.04062942, 110.30393684, -0.01183482]
  };
  function ort(name, T) {
    var b = BAHN[name];
    var a = b[0] + b[1] * T, e = b[2] + b[3] * T, I = b[4] + b[5] * T, L = b[6] + b[7] * T, w = b[8] + b[9] * T, O = b[10] + b[11] * T;
    var M = norm(L - w), om = w - O;
    if (M > 180) M -= 360;
    var E = M + (e / RAD) * sin(M);
    for (var k = 0; k < 8; k++) { var dM = M - (E - (e / RAD) * sin(E)); E += dM / (1 - e * cos(E)); }
    var xs = a * (cos(E) - e), ys = a * Math.sqrt(1 - e * e) * sin(E);
    var co = cos(om), so = sin(om), cO = cos(O), sO = sin(O), cI = cos(I), sI = sin(I);
    return [(co * cO - so * sO * cI) * xs + (-so * cO - co * sO * cI) * ys,
            (co * sO + so * cO * cI) * xs + (-so * sO + co * cO * cI) * ys,
            (so * sI) * xs + (co * sI) * ys];
  }
  function planet(name, T) {
    var p = ort(name, T), e = ort("erde", T);
    // geozentrisch, J2000-Ekliptik, dann Präzession auf das Datum
    return norm(Math.atan2(p[1] - e[1], p[0] - e[0]) / RAD + 1.396971 * T + 0.0003086 * T * T);
  }

  var SYM = { Sonne: "☉", Mond: "☽", Merkur: "☿", Venus: "♀", Mars: "♂", Jupiter: "♃", Saturn: "♄", Uranus: "♅", Neptun: "♆", Pluto: "♇" };
  function planeten(date) {
    var T = jahrhunderte(date || new Date());
    var out = [{ key: "Sonne", sym: SYM.Sonne, lon: sonne(T) }, { key: "Mond", sym: SYM.Mond, lon: mond(T) }];
    ["Merkur", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptun", "Pluto"].forEach(function (n) {
      out.push({ key: n, sym: SYM[n], lon: planet(n, T) });
    });
    return out;
  }

  var ZEICHEN = ["Widder", "Stier", "Zwillinge", "Krebs", "Löwe", "Jungfrau", "Waage", "Skorpion", "Schütze", "Steinbock", "Wassermann", "Fische"];
  // „Sonne in den Zwillingen“, „Mond im Löwen“: Dativ mit Artikel
  var IM = ["im Widder", "im Stier", "in den Zwillingen", "im Krebs", "im Löwen", "in der Jungfrau", "in der Waage", "im Skorpion", "im Schützen", "im Steinbock", "im Wassermann", "in den Fischen"];
  var GLYPH = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"];

  function mondphase(date) {
    var T = jahrhunderte(date || new Date());
    var el = norm(mond(T) - sonne(T));
    var hell = (1 - cos(el)) / 2;
    var name = el < 10 || el > 350 ? "Neumond" : el < 80 ? "zunehmende Mondsichel" : el < 100 ? "zunehmender Halbmond" :
      el < 170 ? "zunehmender Mond" : el < 190 ? "Vollmond" : el < 260 ? "abnehmender Mond" : el < 280 ? "abnehmender Halbmond" : "abnehmende Mondsichel";
    return { winkel: el, hell: hell, name: name };
  }

  // Sonnenzeichen aus Tag und Monat (Jahr optional). Liegt die Sonne an dem Tag
  // auf einer Zeichengrenze, entscheidet erst die genaue Uhrzeit: dann beide Zeichen.
  function sonnenzeichen(tag, monat, jahr) {
    // Tagesanfang und -ende nach mitteleuropäischer Zeit (Sommer- wie Winterzeit abgedeckt)
    var j = jahr || 2000;
    var von = sonne(jahrhunderte(new Date(Date.UTC(j, monat - 1, tag, 0) - 7200000)));
    var bis = sonne(jahrhunderte(new Date(Date.UTC(j, monat - 1, tag, 24) - 3600000)));
    var mitte = sonne(jahrhunderte(new Date(Date.UTC(j, monat - 1, tag, 11))));
    var spanne = jahr ? 0.02 : 0.8;   // ohne Jahr wandert die Grenze je nach Jahr um bis zu einen Tag
    var vor = Math.floor(norm(von - spanne) / 30), nach = Math.floor(norm(bis + spanne) / 30);
    return { index: Math.floor(mitte / 30), grenze: vor !== nach ? [vor, nach] : null };
  }

  /* ── Die zwölf Tierkreis-Sternbilder: Sterne als [Rektaszension in Stunden, Deklination, Helligkeit] ── */
  var STERNBILD = [
    { s: [[2.119, 23.46, 2.0], [1.911, 20.81, 2.6], [1.892, 19.29, 3.9], [2.833, 27.26, 3.6]], l: [[3, 0], [0, 1], [1, 2]] },
    { s: [[4.599, 16.51, .9], [5.438, 28.61, 1.7], [5.627, 21.14, 3.0], [4.330, 15.63, 3.6], [4.382, 17.54, 3.8], [4.477, 19.18, 3.5], [4.478, 15.87, 3.4], [4.011, 12.49, 3.4], [3.791, 24.11, 2.9], [3.452, 9.73, 3.7]],
      l: [[7, 3], [3, 4], [4, 5], [5, 1], [3, 6], [6, 0], [0, 2], [7, 9]] },
    { s: [[7.577, 31.89, 1.6], [7.755, 28.03, 1.1], [6.629, 16.40, 1.9], [6.732, 25.13, 3.0], [6.383, 22.51, 2.9], [6.248, 22.51, 3.3], [7.335, 21.98, 3.5], [7.598, 26.90, 4.1], [7.068, 20.57, 3.9], [7.301, 16.54, 3.6], [7.186, 30.25, 4.4], [6.483, 20.21, 4.1], [6.755, 12.90, 3.4]],
      l: [[0, 10], [10, 3], [3, 4], [4, 5], [3, 11], [1, 7], [7, 6], [6, 8], [8, 2], [6, 9], [9, 12], [10, 7]] },
    { s: [[8.975, 11.86, 4.3], [8.745, 18.15, 3.9], [8.721, 21.47, 4.7], [8.778, 28.76, 4.0], [8.275, 9.19, 3.5]], l: [[4, 1], [1, 0], [1, 2], [2, 3]] },
    { s: [[10.140, 11.97, 1.4], [10.122, 16.76, 3.5], [10.333, 19.84, 2.0], [10.278, 23.42, 3.4], [9.879, 26.01, 3.9], [9.764, 23.77, 3.0], [11.235, 20.52, 2.6], [11.237, 15.43, 3.3], [11.818, 14.57, 2.1]],
      l: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [2, 6], [6, 8], [8, 7], [7, 0], [6, 7]] },
    { s: [[13.420, -11.16, 1.0], [12.694, -1.45, 2.7], [13.036, 10.96, 2.8], [12.927, 3.40, 3.4], [13.578, -.60, 3.4], [11.845, 1.76, 3.6], [12.332, -.67, 3.9], [14.267, -6.00, 4.1], [14.718, -5.66, 3.9], [14.770, 1.89, 3.7], [14.027, 1.54, 4.3], [13.165, -5.54, 4.4]],
      l: [[5, 6], [6, 1], [1, 3], [3, 2], [1, 11], [11, 0], [3, 4], [4, 10], [10, 9], [4, 7], [7, 8]] },
    { s: [[14.848, -16.04, 2.8], [15.283, -9.38, 2.6], [15.592, -14.79, 3.9], [15.068, -25.28, 3.3], [15.617, -28.14, 3.6], [15.645, -29.78, 3.7]],
      l: [[1, 0], [0, 3], [1, 2], [2, 0], [2, 4], [4, 5]] },
    { s: [[16.490, -26.43, 1.0], [16.353, -25.59, 2.9], [16.598, -28.22, 2.8], [16.006, -22.62, 2.3], [16.091, -19.81, 2.6], [15.981, -26.11, 2.9], [16.836, -34.29, 2.3], [16.864, -38.05, 3.0], [16.910, -42.36, 3.6], [17.203, -43.24, 3.3], [17.622, -43.00, 1.9], [17.793, -40.13, 3.0], [17.708, -39.03, 2.4], [17.560, -37.10, 1.6], [17.513, -37.30, 2.7], [15.948, -29.21, 3.9]],
      l: [[4, 3], [3, 5], [5, 15], [3, 1], [1, 0], [0, 2], [2, 6], [6, 7], [7, 8], [8, 9], [9, 10], [10, 11], [11, 12], [12, 13], [13, 14]] },
    { s: [[18.403, -34.38, 1.8], [18.350, -29.83, 2.7], [18.466, -25.42, 2.8], [18.097, -30.42, 3.0], [18.921, -26.30, 2.0], [19.044, -29.88, 2.6], [19.116, -27.67, 3.3], [18.761, -26.99, 3.2], [18.294, -36.76, 3.1]],
      l: [[3, 1], [1, 2], [2, 7], [7, 4], [4, 6], [6, 5], [5, 7], [5, 0], [0, 1], [0, 3], [0, 8], [1, 7]] },
    { s: [[20.300, -12.54, 3.6], [20.350, -14.78, 3.1], [20.768, -25.27, 4.1], [20.864, -26.92, 4.1], [21.444, -22.41, 3.7], [21.668, -16.66, 3.7], [21.784, -16.13, 2.9], [21.099, -17.23, 4.1], [21.371, -16.83, 4.3]],
      l: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 6], [6, 5], [5, 8], [8, 7], [7, 1]] },
    { s: [[21.526, -5.57, 2.9], [22.096, -.32, 3.0], [22.361, -1.39, 3.8], [22.481, -.02, 3.6], [22.589, -.12, 4.0], [22.421, 1.38, 4.7], [22.281, -7.78, 4.2], [22.877, -7.58, 3.7], [22.911, -15.82, 3.3], [20.795, -9.50, 3.8], [23.238, -6.05, 4.2], [23.265, -9.09, 4.2]],
      l: [[9, 0], [0, 1], [1, 2], [2, 3], [3, 4], [3, 5], [1, 6], [6, 7], [7, 10], [7, 8], [10, 11]] },
    { s: [[2.034, 2.76, 3.8], [1.525, 15.35, 3.6], [1.757, 9.16, 4.3], [1.691, 5.49, 4.4], [1.503, 6.14, 4.8], [1.049, 7.89, 4.3], [.811, 7.59, 4.4], [23.989, 6.86, 4.0], [23.666, 5.63, 4.1], [23.466, 6.38, 4.3], [23.286, 3.28, 3.7], [23.449, 1.26, 4.9], [23.700, 1.78, 4.5], [1.194, 30.09, 4.5], [1.325, 27.26, 4.8], [1.229, 24.58, 4.7], [1.191, 21.03, 4.7]],
      l: [[0, 2], [2, 1], [1, 16], [16, 15], [15, 14], [14, 13], [0, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 9], [9, 10], [10, 11], [11, 12], [12, 8]] }
  ];

  // Sternbild in ein Rechteck (Breite b, Höhe h, Rand r) legen: Himmelsnorden oben, Osten links
  function sternbildPunkte(i, b, h, r) {
    var sb = STERNBILD[i], ra0 = 0, dec0 = 0, n = sb.s.length;
    var ref = sb.s[0][0];
    var pts = sb.s.map(function (s) { var d = s[0] - ref; if (d > 12) d -= 24; if (d < -12) d += 24; return [d, s[1], s[2]]; });
    pts.forEach(function (p) { ra0 += p[0]; dec0 += p[1]; }); ra0 /= n; dec0 /= n;
    var xy = pts.map(function (p) { return [-(p[0] - ra0) * 15 * cos(dec0), -(p[1] - dec0), p[2]]; });
    var minx = Infinity, maxx = -Infinity, miny = Infinity, maxy = -Infinity;
    xy.forEach(function (p) { minx = Math.min(minx, p[0]); maxx = Math.max(maxx, p[0]); miny = Math.min(miny, p[1]); maxy = Math.max(maxy, p[1]); });
    r = r || 0;
    var sc = Math.min((b - 2 * r) / Math.max(maxx - minx, 1), (h - 2 * r) / Math.max(maxy - miny, 1));
    var ox = (b - (maxx - minx) * sc) / 2, oy = (h - (maxy - miny) * sc) / 2;
    return { sterne: xy.map(function (p) { return [ox + (p[0] - minx) * sc, oy + (p[1] - miny) * sc, p[2]]; }), linien: sb.l };
  }

  // Fertiges SVG: Linien zeichnen sich nacheinander (Klasse .sb-zeichnen am Eltern-Element startet es)
  function sternbildSVG(i, b, h, opt) {
    opt = opt || {};
    var p = sternbildPunkte(i, b, h, opt.rand || 14), s = "", n = p.linien.length, dauer = opt.dauer || 2.4;
    p.linien.forEach(function (l, k) {
      var a = p.sterne[l[0]], c = p.sterne[l[1]], len = Math.hypot(c[0] - a[0], c[1] - a[1]);
      s += '<line class="sb-l" x1="' + a[0].toFixed(1) + '" y1="' + a[1].toFixed(1) + '" x2="' + c[0].toFixed(1) + '" y2="' + c[1].toFixed(1) +
        '" style="stroke-dasharray:' + len.toFixed(1) + ';stroke-dashoffset:' + len.toFixed(1) + ';--d:' + (k * dauer / n).toFixed(2) + 's"/>';
    });
    p.sterne.forEach(function (st, k) {
      var rr = Math.max(1.1, 3.6 - st[2] * .55) * (opt.gross || 1);
      s += '<circle class="sb-s" cx="' + st[0].toFixed(1) + '" cy="' + st[1].toFixed(1) + '" r="' + rr.toFixed(2) + '" style="--d:' + (k * .12).toFixed(2) + 's"/>';
      if (st[2] < 2.2) s += '<circle class="sb-h" cx="' + st[0].toFixed(1) + '" cy="' + st[1].toFixed(1) + '" r="' + (rr * 3.2).toFixed(1) + '" style="--d:' + (k * .12).toFixed(2) + 's"/>';
    });
    return '<svg class="sternbild" viewBox="0 0 ' + b + ' ' + h + '" aria-hidden="true">' + s + '</svg>';
  }

  window.Himmel = {
    planeten: planeten, mondphase: mondphase, sonnenzeichen: sonnenzeichen,
    zeichen: function (lon) { return Math.floor(norm(lon) / 30); },
    ZEICHEN: ZEICHEN, IM: IM, GLYPH: GLYPH,
    sternbildPunkte: sternbildPunkte, sternbildSVG: sternbildSVG,
    _sonne: sonne, _mond: mond, _T: jahrhunderte
  };
})();
