"""
Reiknar veðurfarsskor fyrir hvert póstnúmer:
  40% meðalhitastig (hærra = betra)
  35% meðalvindhraði (lægri = betra)
  25% meðalúrkoma (minni = betra)

Reiknar einnig veðurverð = fermetraverð / veðurfarsskor (lægra = betra deal).

Keyra: python3 build_scores.py
Skilar: static/scores.json
"""

import csv
import json
import math
import statistics
from collections import defaultdict

KAUPSKRA_PATH   = "static/kaupskra.csv"
CLIMATE_PATH    = "static/climate_averages.json"
OUTPUT_PATH     = "static/scores.json"

# Nota sölu frá þessum árum
YEARS_INCLUDE   = {"2022", "2023", "2024", "2025"}
MIN_SALES       = 4       # Lágmark fjöldi samninga í póstnúmeri

# Aðeins íbúðarhúsnæði
IBUDATEGUND = {"Fjölbýli", "Einbýli", "Sérbýli", "Raðhús", "Parhús"}

# ── Haul kaupskrá ─────────────────────────────────────────────────────────────
print("Les kaupskrá…")
pn_sales = defaultdict(list)   # postnr -> list of (price_per_m2)

with open(KAUPSKRA_PATH, encoding="iso-8859-1") as f:
    reader = csv.DictReader(f, delimiter=";")
    for row in reader:
        # Aðeins íbúðarhúsnæði
        if row.get("TEGUND", "").strip() not in IBUDATEGUND:
            continue
        # Sía út ógilda samninga
        if row.get("ONOTHAEFUR_SAMNINGUR", "").strip() == "1":
            continue
        year = row["UTGDAG"][:4]
        if year not in YEARS_INCLUDE:
            continue
        try:
            price_thous = float(row["KAUPVERD"].replace(",", "."))
            area_m2     = float(row["EINFLM"].replace(",", "."))
        except (ValueError, AttributeError):
            continue
        if price_thous <= 0 or area_m2 <= 0:
            continue
        price_isk   = price_thous * 1000
        price_per_m2 = price_isk / area_m2
        # Sía út óraunhæf gildi (< 50k/m² eða > 2M/m²)
        if price_per_m2 < 50_000 or price_per_m2 > 2_000_000:
            continue
        postnr = row["POSTNR"].strip()
        if postnr:
            pn_sales[postnr].append(price_per_m2)

print(f"  {len(pn_sales)} póstnúmer með gögn")

# Reikna miðgildi fermetraverðs per póstnúmer
pn_price = {}
for pn, prices in pn_sales.items():
    if len(prices) >= MIN_SALES:
        pn_price[pn] = statistics.median(prices)

print(f"  {len(pn_price)} póstnúmer með ≥{MIN_SALES} samninga")

# ── Sækja hnit póstnúmera úr iceaddr ─────────────────────────────────────────
print("Sæki hnit póstnúmera úr iceaddr…")
from iceaddr.db import shared_db

conn = shared_db.connection()
pn_coords = {}

for pn in pn_price:
    try:
        pn_int = int(pn)
    except ValueError:
        continue
    cur = conn.execute(
        "SELECT AVG(lat_wgs84) as lat, AVG(long_wgs84) as lon, COUNT(*) as n "
        "FROM stadfong WHERE postnr=? AND lat_wgs84 IS NOT NULL AND long_wgs84 IS NOT NULL",
        (str(pn_int),)
    )
    row = cur.fetchone()
    if row and row["n"] and row["n"] > 0:
        pn_coords[pn] = (row["lat"], row["lon"])

print(f"  {len(pn_coords)} póstnúmer með hnit")

# ── Hlaða loftlagsgögnum ──────────────────────────────────────────────────────
print("Hleð climate_averages.json…")
with open(CLIMATE_PATH, encoding="utf-8") as f:
    climate = json.load(f)

stations = []
for s in climate["stations"]:
    # Þurfum hitastig, vindhraða og úrkomu – sá stöð sem hefur allt þrjú
    # getur verið notaður með öðrum stöðvum sem vantar einstaka mæligildi
    stations.append(s)

def haversine(lat1, lon1, lat2, lon2):
    """Km milli tveggja GPS hnita."""
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat/2)**2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(d_lon/2)**2)
    return 2 * R * math.asin(math.sqrt(a))

def nearest_station_value(lat, lon, key):
    """Finn næstu stöð sem hefur gildi fyrir 'key' og skilar gildinu."""
    best_val  = None
    best_dist = float("inf")
    for s in stations:
        val = s.get(key)
        if val is None:
            continue
        if s.get("lat") is None:
            continue  # Þessir stöðvar hafa ekki hnit í JSON – sjá neðar
        dist = haversine(lat, lon, s["lat"], s["lon"])
        if dist < best_dist:
            best_dist = dist
            best_val  = val
    return best_val, best_dist

# Við þurfum hnit stöðvanna — þær eru EKKI í climate_averages.json
# Sækjum þær úr iceweather station_list
print("Sæki hnit veðurstöðva úr iceweather…")
from iceweather import station_list
import unicodedata, re

def norm_name(s):
    """Lowercase, strip accents, keep only alphanumeric."""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)

iw_by_id   = {s["id"]:          s for s in station_list()}
iw_by_name = {norm_name(s["name"]): s for s in station_list()}

station_map = []
matched = 0
for s in stations:
    sid  = s.get("id")
    iw   = iw_by_id.get(sid)
    if not iw:
        iw = iw_by_name.get(norm_name(s.get("nafn", "")))
    if iw:
        station_map.append({**s, "lat": iw["lat"], "lon": iw["lon"]})
        matched += 1
    else:
        station_map.append(s)   # lat/lon verður None

print(f"  {matched} stöðvar með hnit (af {len(stations)})")

def nearest_climate(lat, lon):
    """Skilar dict með t, f, r úr næstu hæfum stöðvum."""
    result = {"t": None, "f": None, "r": None, "stod_nafn": None, "stod_dist_km": None}
    best_dist = float("inf")
    for s in station_map:
        if not s.get("lat") or not s.get("lon"):
            continue
        dist = haversine(lat, lon, s["lat"], s["lon"])
        # Velja stöð sem er næst og hefur a.m.k. hitastig eða úrkomu
        if dist < best_dist and (s.get("t") is not None or s.get("r") is not None):
            best_dist = dist
            result = {
                "t":         s.get("t"),
                "f":         s.get("f"),
                "r":         s.get("r"),
                "stod_nafn": s.get("nafn"),
                "stod_dist_km": round(dist, 1),
            }
    return result

# Ef stöð vantar t eða f: finna nærstu stöð sem hefur þær mæligerð
def best_climate(lat, lon):
    """Sameinar gögn úr næstu stöðvum per mæligerð."""
    result = {}
    for key in ("t", "f", "r"):
        best_val  = None
        best_dist = float("inf")
        for s in station_map:
            if not s.get("lat"):
                continue
            val = s.get(key)
            if val is None:
                continue
            dist = haversine(lat, lon, s["lat"], s["lon"])
            if dist < best_dist:
                best_dist = dist
                best_val  = val
        result[key] = best_val
    # Nearest station (any key) for label
    nc = nearest_climate(lat, lon)
    result["stod_nafn"]     = nc["stod_nafn"]
    result["stod_dist_km"] = nc["stod_dist_km"]
    return result

# ── Búa til gögn per póstnúmer ───────────────────────────────────────────────
print("Reikna loftlagsgögn per póstnúmer…")
from iceaddr.postcodes import POSTCODES

records = []
for pn, price_per_m2 in pn_price.items():
    coords = pn_coords.get(pn)
    if not coords:
        continue
    lat, lon = coords
    climate_data = best_climate(lat, lon)

    pc_info = POSTCODES.get(int(pn), {})
    records.append({
        "postnr":      int(pn),
        "stadur":      pc_info.get("stadur_nf", ""),
        "lysing":      pc_info.get("lysing", ""),
        "lat":         round(lat, 5),
        "lon":         round(lon, 5),
        "fmverd":      round(price_per_m2),
        "n_samninga":  len(pn_sales[pn]),
        "t":           climate_data["t"],
        "f":           climate_data["f"],
        "r":           climate_data["r"],
        "stod_nafn":   climate_data["stod_nafn"],
        "stod_dist_km": climate_data["stod_dist_km"],
    })

print(f"  {len(records)} póstnúmer tilbúin til skora")

# ── Normalísering og skor ─────────────────────────────────────────────────────
def normalize_inverse(values, low_is_good=True):
    """Normalísera á 0-100. Ef low_is_good=True: lægra gildi fær hærra skor."""
    valid = [v for v in values if v is not None]
    if not valid:
        return [None] * len(values)
    mn, mx = min(valid), max(valid)
    result = []
    for v in values:
        if v is None:
            result.append(None)
            continue
        if mx == mn:
            result.append(50.0)
            continue
        norm = (v - mn) / (mx - mn) * 100
        result.append(100 - norm if low_is_good else norm)
    return result

# Safna gildum til normalíseringar
t_vals = [r["t"] for r in records]
f_vals = [r["f"] for r in records]
r_vals = [r["r"] for r in records]

t_norm = normalize_inverse(t_vals, low_is_good=False)   # hærra = betra
f_norm = normalize_inverse(f_vals, low_is_good=True)    # lægra = betra
r_norm = normalize_inverse(r_vals, low_is_good=True)    # minni = betra

W_TEMP = 0.40
W_WIND = 0.35
W_RAIN = 0.25

scored = []
for i, rec in enumerate(records):
    components = {
        "t": t_norm[i],
        "f": f_norm[i],
        "r": r_norm[i],
    }
    climate_keys = [("t", W_TEMP), ("f", W_WIND), ("r", W_RAIN)]
    available    = [(k, w) for k, w in climate_keys if components[k] is not None]
    if not available:
        continue
    total_w      = sum(w for _, w in available)
    weights_used = {k: w / total_w for k, w in available}

    skor = sum(components[k] * w for k, w in weights_used.items())
    skor = round(skor, 1)

    fmverd = rec["fmverd"]
    vedursverd = round(fmverd / skor) if skor > 0 else None

    scored.append({
        **rec,
        "skor":       skor,
        "vedursverd": vedursverd,
        "norm_t":     round(t_norm[i], 1) if t_norm[i] is not None else None,
        "norm_f":     round(f_norm[i], 1) if f_norm[i] is not None else None,
        "norm_r":     round(r_norm[i], 1) if r_norm[i] is not None else None,
    })

# Raða eftir skori
scored.sort(key=lambda x: x["skor"], reverse=True)
for rank, rec in enumerate(scored, 1):
    rec["rod"] = rank

# ── Fallback: póstnúmer án gagna → næsta póstnúmer með skor ──────────────────
# Sækja hnit fyrir öll póstnúmer í iceaddr (líka þau sem hafa ekki gögn)
print("Reikna fallback-vörpun fyrir póstnúmer án gagna…")
scored_pn = {rec["postnr"]: rec for rec in scored}

# Búa til lookup: öll gild póstnúmer með hnit
all_pn_coords = {}
for pn_str, coords in pn_coords.items():
    try:
        all_pn_coords[int(pn_str)] = coords
    except ValueError:
        pass

# Finna öll póstnúmer í POSTCODES sem eru ekki í scored
fallback_map = {}   # postnr_without_score -> nearest postnr with score
for pn_int, info in POSTCODES.items():
    if pn_int in scored_pn:
        continue
    coords = all_pn_coords.get(pn_int)
    if not coords:
        # Reyna að sækja úr iceaddr
        try:
            cur = conn.execute(
                "SELECT AVG(lat_wgs84) as lat, AVG(long_wgs84) as lon FROM stadfong "
                "WHERE postnr=? AND lat_wgs84 IS NOT NULL", (str(pn_int),)
            )
            row2 = cur.fetchone()
            if row2 and row2["lat"]:
                coords = (row2["lat"], row2["lon"])
        except Exception:
            pass
    if not coords:
        continue
    lat, lon = coords
    best_dist = float("inf")
    best_pn   = None
    for sp in scored:
        dist = haversine(lat, lon, sp["lat"], sp["lon"])
        if dist < best_dist:
            best_dist = dist
            best_pn   = sp["postnr"]
    if best_pn is not None:
        fallback_map[pn_int] = {
            "postnr_fallback": best_pn,
            "dist_km": round(best_dist, 1),
        }

print(f"  {len(fallback_map)} fallback-varpanir búnar til")

# ── Vista ─────────────────────────────────────────────────────────────────────
output = {
    "updated":     __import__("datetime").date.today().isoformat(),
    "years":       sorted(YEARS_INCLUDE),
    "weights": {
        "t": W_TEMP,
        "f": W_WIND,
        "r": W_RAIN,
    },
    "scores":   scored,
    "fallback": fallback_map,
}

with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
    json.dump(output, out, ensure_ascii=False, separators=(",", ":"))

print(f"\nVistað í {OUTPUT_PATH}")
print(f"Fjöldi póstnúmera: {len(scored)}")
print("\nTop 10 (veðurfarsskor):")
for r in scored[:10]:
    vv = r['vedursverd']
    print(f"  #{r['rod']:3} {r['postnr']} {r['stadur']:20} skor={r['skor']:5.1f}  "
          f"vedursverd={vv}  fm={r['fmverd']/1000:.0f}k/m²  t={r['t']}°C  f={r['f']}m/s  r={r['r']}mm")

print("\nBest veðurverð (lægst):")
by_vv = sorted([r for r in scored if r['vedursverd']], key=lambda x: x['vedursverd'])
for r in by_vv[:5]:
    print(f"  {r['postnr']} {r['stadur']:20} skor={r['skor']:5.1f}  vedursverd={r['vedursverd']:,}")
