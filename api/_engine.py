"""
Human Design + Natalchart Engine — Intuition mit Herz
-----------------------------------------------------
Alle astronomischen Werte werden mit der Swiss Ephemeris (Moshier-Modus,
keine Datendateien nötig) exakt berechnet. Die KI textet später auf Basis
dieser korrekten Zahlen — sie rechnet nie selbst.

Validiert gegen reale, handkorrigierte Charts (Denise & Tobias): alle
Planeten, Aszendent, MC und das komplette Human Design stimmen auf die
Bogenminute.
"""
import os
import swisseph as swe
from datetime import datetime
from zoneinfo import ZoneInfo

# Planeten laufen weiter im Moshier-Modus (keine Datendateien). Nur Chiron
# braucht die kleine Asteroiden-Datei seas_18.se1 in api/ephe/.
_EPHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ephe")
swe.set_ephe_path(_EPHE if os.path.isdir(_EPHE) else None)
FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED
CHIRON_FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED

# ── Human-Design-Rad: 64 Tore ab Gate 41 @ 302.0° ekliptikaler Länge ──
GATE_ORDER = [41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3,
              27, 24, 2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56,
              31, 33, 7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50,
              28, 44, 1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60]
GATE_START = 302.0
GATE_SIZE = 360.0 / 64.0
LINE_SIZE = GATE_SIZE / 6.0

CENTERS = {
    "Kopf":        [64, 61, 63],
    "Ajna":        [47, 24, 4, 17, 43, 11],
    "Kehle":       [62, 23, 56, 35, 12, 45, 33, 8, 31, 20, 16],
    "G":           [1, 13, 25, 46, 2, 15, 10, 7],
    "Herz":        [21, 40, 26, 51],
    "Milz":        [48, 57, 44, 50, 32, 28, 18],
    "Sakral":      [5, 14, 29, 59, 9, 3, 42, 27, 34],
    "Solarplexus": [6, 37, 30, 55, 49, 22, 36],
    "Wurzel":      [53, 60, 52, 19, 39, 41, 58, 38, 54],
}
MOTORS = {"Sakral", "Herz", "Solarplexus", "Wurzel"}

# 36 Kanäle: (Tor A, Tor B, Zentrum A, Zentrum B)
CHANNELS = [
    (1, 8, "G", "Kehle"), (2, 14, "G", "Sakral"), (3, 60, "Sakral", "Wurzel"),
    (4, 63, "Ajna", "Kopf"), (5, 15, "Sakral", "G"), (6, 59, "Solarplexus", "Sakral"),
    (7, 31, "G", "Kehle"), (9, 52, "Sakral", "Wurzel"), (10, 20, "G", "Kehle"),
    (10, 34, "G", "Sakral"), (10, 57, "G", "Milz"), (11, 56, "Ajna", "Kehle"),
    (12, 22, "Kehle", "Solarplexus"), (13, 33, "G", "Kehle"), (16, 48, "Kehle", "Milz"),
    (17, 62, "Ajna", "Kehle"), (18, 58, "Milz", "Wurzel"), (19, 49, "Wurzel", "Solarplexus"),
    (20, 34, "Kehle", "Sakral"), (20, 57, "Kehle", "Milz"), (21, 45, "Herz", "Kehle"),
    (23, 43, "Kehle", "Ajna"), (24, 61, "Ajna", "Kopf"), (25, 51, "G", "Herz"),
    (26, 44, "Herz", "Milz"), (27, 50, "Sakral", "Milz"), (28, 38, "Milz", "Wurzel"),
    (29, 46, "Sakral", "G"), (30, 41, "Solarplexus", "Wurzel"), (32, 54, "Milz", "Wurzel"),
    (34, 57, "Sakral", "Milz"), (35, 36, "Kehle", "Solarplexus"), (37, 40, "Solarplexus", "Herz"),
    (39, 55, "Wurzel", "Solarplexus"), (42, 53, "Sakral", "Wurzel"), (47, 64, "Ajna", "Kopf"),
]

# 13 Himmelskörper (Erde & Südknoten werden abgeleitet)
BODIES = [
    ("Sonne", swe.SUN), ("Mond", swe.MOON), ("Merkur", swe.MERCURY),
    ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
    ("Saturn", swe.SATURN), ("Uranus", swe.URANUS), ("Neptun", swe.NEPTUNE),
    ("Pluto", swe.PLUTO), ("Nordknoten", swe.TRUE_NODE),
]
SYMS = {"Sonne": "☉", "Mond": "☽", "Merkur": "☿", "Venus": "♀", "Mars": "♂",
        "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptun": "♆", "Pluto": "♇",
        "Nordknoten": "☊", "Südknoten": "☋", "Erde": "⊕", "Chiron": "⚷"}
SIGNS = ["Widder", "Stier", "Zwillinge", "Krebs", "Löwe", "Jungfrau", "Waage",
         "Skorpion", "Schütze", "Steinbock", "Wassermann", "Fische"]
SIGN_SYMS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]


def ephe_status():
    """Diagnose: Ist die Chiron-Ephemeride auffindbar und rechenbar?"""
    info = {"ephe_dir": _EPHE, "isdir": os.path.isdir(_EPHE)}
    try:
        info["files"] = sorted(os.listdir(_EPHE))
    except Exception as e:  # noqa
        info["files_error"] = repr(e)
    try:
        jd = swe.julday(2000, 1, 1, 12.0)
        info["chiron_lon"] = round(swe.calc_ut(jd, swe.CHIRON, CHIRON_FLAGS)[0][0], 4)
    except Exception as e:  # noqa
        info["chiron_error"] = repr(e)
    return info


def lon_to_gate_line(lon):
    off = (lon - GATE_START) % 360.0
    idx = int(off // GATE_SIZE)
    within = off - idx * GATE_SIZE
    return GATE_ORDER[idx], int(within // LINE_SIZE) + 1


def _sun_lon(jd):
    return swe.calc_ut(jd, swe.SUN, FLAGS)[0][0]


def _design_jd(jd_birth):
    """Moment, in dem die Sonne exakt 88 Bogengrad vor der Geburtssonne stand."""
    target = (_sun_lon(jd_birth) - 88.0) % 360.0
    jd = jd_birth - 88.0
    for _ in range(30):
        d = ((target - _sun_lon(jd) + 180) % 360) - 180
        jd += d / 0.9856
        if abs(d) < 1e-8:
            break
    return jd


def _bodies(jd):
    out = {}
    for name, pid in BODIES:
        out[name] = swe.calc_ut(jd, pid, FLAGS)[0][0]
    out["Erde"] = (out["Sonne"] + 180) % 360
    out["Südknoten"] = (out["Nordknoten"] + 180) % 360
    return out


def _sign(lon):
    i = int(lon // 30)
    d = lon - i * 30
    deg = int(d)
    minute = round((d - deg) * 60)
    if minute == 60:
        deg += 1
        minute = 0
    return {"sign": SIGNS[i], "sym": SIGN_SYMS[i], "deg": deg, "min": minute,
            "text": f"{deg}°{minute:02d}'", "lon": round(lon, 4)}


def _whole_house(lon, asc_lon):
    start = (int(asc_lon // 30)) * 30
    return int((((lon - start) % 360) // 30)) + 1


def _graph(defined, active_ch):
    adj = {c: set() for c in defined}
    for a, b, ca, cb in active_ch:
        if ca in adj and cb in adj:
            adj[ca].add(cb)
            adj[cb].add(ca)
    return adj


def _connected_to_throat(defined, active_ch):
    if "Kehle" not in defined:
        return False
    adj = _graph(defined, active_ch)
    seen, stack = {"Kehle"}, ["Kehle"]
    while stack:
        for m in adj[stack.pop()]:
            if m not in seen:
                seen.add(m)
                stack.append(m)
    return bool(seen & MOTORS)


def _hd_type(defined, active_ch):
    if not defined:
        return "Reflektor"
    sacral = "Sakral" in defined
    motor = _connected_to_throat(defined, active_ch)
    if sacral and motor:
        return "Manifestierender Generator"
    if sacral:
        return "Generator"
    if motor:
        return "Manifestor"
    return "Projektor"


def _authority(defined):
    if "Solarplexus" in defined:
        return "Emotionale Autorität"
    if "Sakral" in defined:
        return "Sakrale Autorität"
    if "Milz" in defined:
        return "Milz-Autorität (Splenisch)"
    if "Herz" in defined:
        return "Ego-/Herz-Autorität"
    if "G" in defined:
        return "Selbst-projizierte Autorität"
    if not defined:
        return "Mond-Autorität (Reflektor)"
    return "Mentale Autorität (Umgebung)"


def _definition(defined, active_ch):
    if not defined:
        return "Keine Definition"
    adj = _graph(defined, active_ch)
    seen, comps = set(), 0
    for c in defined:
        if c not in seen:
            comps += 1
            stack = [c]
            seen.add(c)
            while stack:
                for m in adj[stack.pop()]:
                    if m not in seen:
                        seen.add(m)
                        stack.append(m)
    return {1: "Einfache Definition", 2: "Split-Definition",
            3: "Dreifach-Split", 4: "Vierfach-Split"}.get(comps, f"{comps}-fach")


def compute_chart(name, year, month, day, hour, minute, lat, lon, tz_name,
                  time_known=True):
    """Berechnet Natalchart + Human Design für einen Menschen."""
    tz = ZoneInfo(tz_name)
    local = datetime(year, month, day, hour, minute, tzinfo=tz)
    utc = local.astimezone(ZoneInfo("UTC"))
    jd = swe.julday(utc.year, utc.month, utc.day,
                    utc.hour + utc.minute / 60 + utc.second / 3600)
    jd_des = _design_jd(jd)

    pers_lon = _bodies(jd)
    des_lon = _bodies(jd_des)
    pers = {b: lon_to_gate_line(l) for b, l in pers_lon.items()}
    des = {b: lon_to_gate_line(l) for b, l in des_lon.items()}
    gates_active = {g for g, _ in pers.values()} | {g for g, _ in des.values()}

    active_ch = [(a, b, ca, cb) for a, b, ca, cb in CHANNELS
                 if a in gates_active and b in gates_active]
    defined = set()
    for a, b, ca, cb in active_ch:
        defined.add(ca)
        defined.add(cb)

    hd_type = _hd_type(defined, active_ch)
    authority = _authority(defined)
    profile = f"{pers['Sonne'][1]}/{des['Sonne'][1]}"

    # Natal
    asc_lon = mc_lon = None
    natal = {}
    if time_known:
        cusps, ascmc = swe.houses(jd, lat, lon, b'W')  # W = Whole Sign
        asc_lon, mc_lon = ascmc[0], ascmc[1]
    for b, l in pers_lon.items():
        s = _sign(l)
        if time_known and asc_lon is not None:
            s["house"] = _whole_house(l, asc_lon)
        s["sym_body"] = SYMS.get(b, "")
        natal[b] = s

    # Chiron (nur astrologisch, nicht Teil des Human Design) – braucht seas_18.se1
    try:
        ch_lon = swe.calc_ut(jd, swe.CHIRON, CHIRON_FLAGS)[0][0]
        ch = _sign(ch_lon)
        ch["sym_body"] = "⚷"
        if time_known and asc_lon is not None:
            ch["house"] = _whole_house(ch_lon, asc_lon)
        natal["Chiron"] = ch
    except Exception:
        pass  # ohne Ephemeriden-Datei bleibt Chiron einfach weg

    result = {
        "name": name,
        "hd": {
            "type": hd_type,
            "authority": authority,
            "profile": profile,
            "definition": _definition(defined, active_ch),
            "defined_centers": [c for c in CENTERS if c in defined],
            "open_centers": [c for c in CENTERS if c not in defined],
            "incarnation_cross": {
                "pers_sun": pers["Sonne"][0], "pers_earth": pers["Erde"][0],
                "des_sun": des["Sonne"][0], "des_earth": des["Erde"][0],
            },
            "gates": sorted(gates_active),
            "channels": [f"{a}-{b}" for a, b, _, _ in active_ch],
            "personality": {b: {"gate": g, "line": ln} for b, (g, ln) in pers.items()},
            "design": {b: {"gate": g, "line": ln} for b, (g, ln) in des.items()},
        },
        "natal": natal,
        "time_known": time_known,
    }
    if time_known:
        result["ascendant"] = _sign(asc_lon)
        result["mc"] = _sign(mc_lon)
    return result
