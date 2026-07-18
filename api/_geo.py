"""
Offline-Geocoding als Sicherheitsnetz.
Der Hauptweg ist das Städte-Autocomplete im Frontend (liefert lat/lon/tz
direkt mit). Falls jemand keinen Vorschlag auswählt, lösen wir den Ortsnamen
hier serverseitig auf – ohne externen Dienst, ohne Rate-Limits.
"""
import unicodedata

# gängige deutschsprachige Namen -> internationaler Name in geonamescache
ALIASES = {
    "wien": "Vienna", "muenchen": "Munich", "münchen": "Munich",
    "koeln": "Cologne", "köln": "Cologne", "nuernberg": "Nuremberg",
    "nürnberg": "Nuremberg", "zuerich": "Zurich", "zürich": "Zurich",
    "genf": "Geneva", "prag": "Prague", "warschau": "Warsaw",
    "mailand": "Milan", "rom": "Rome", "athen": "Athens",
    "lissabon": "Lisbon", "kopenhagen": "Copenhagen", "moskau": "Moscow",
    "bruessel": "Brussels", "brüssel": "Brussels",
}

_TF = None
_CITIES = None


def _norm(s):
    s = s.strip().lower()
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(c))


def _load():
    global _TF, _CITIES
    if _CITIES is None:
        from geonamescache import GeonamesCache
        _CITIES = list(GeonamesCache().get_cities().values())
    if _TF is None:
        from timezonefinder import TimezoneFinder
        _TF = TimezoneFinder()


def tz_for(lat, lon):
    _load()
    return _TF.timezone_at(lat=lat, lng=lon) or "UTC"


def resolve_place(place):
    """place -> (lat, lon, tz_name, display) oder None."""
    if not place:
        return None
    _load()
    raw = place.split(",")[0].strip()
    key = _norm(raw)
    target = _norm(ALIASES.get(key, raw))

    exact, prefix = [], []
    for c in _CITIES:
        n = _norm(c["name"])
        if n == target:
            exact.append(c)
        elif n.startswith(target) or target in n:
            prefix.append(c)
    pool = exact or prefix
    if not pool:
        return None
    best = max(pool, key=lambda c: c.get("population", 0))
    lat, lon = float(best["latitude"]), float(best["longitude"])
    display = f"{best['name']}, {best['countrycode']}"
    return lat, lon, tz_for(lat, lon), display
