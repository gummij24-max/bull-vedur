import time
from flask import Flask, render_template, request, jsonify
from iceaddr import iceaddr_suggest
from iceweather import (
    observation_for_closest, forecast_for_closest,
    observation_for_stations, observation_for_station,
    forecast_for_station, station_list, station_for_id,
    forecast_text,
)
from collections import defaultdict

app = Flask(__name__)

VINDAETT_FULL = {
    "N":   "Norðanátt",
    "NNA": "Nor-norðaustanátt",
    "NA":  "Norðaustanátt",
    "ANA": "Aus-norðaustanátt",
    "A":   "Austanátt",
    "ASA": "Aus-suðaustanátt",
    "SA":  "Suðaustanátt",
    "SSA": "Suð-suðaustanátt",
    "S":   "Sunnanátt",
    "SSV": "Suð-suðvestanátt",
    "SV":  "Suðvestanátt",
    "VSV": "Ves-suðvestanátt",
    "V":   "Vestanátt",
    "VNV": "Ves-norðvestanátt",
    "NV":  "Norðvestanátt",
    "NNV": "Nor-norðvestanátt",
    "KAL": "Logn",
}

# In-memory cache for station list + observations
_stations_cache = None
_stations_cache_ts = 0.0
_STATIONS_TTL = 300  # 5 mínútur


def parse_num(val):
    if val is None or val == "":
        return None
    try:
        return float(str(val).replace(",", "."))
    except (ValueError, TypeError):
        return None


def format_addr(r):
    gata = r.get("heiti_nf", "")
    if r.get("husnr"):
        gata += f" {r['husnr']}"
    if r.get("bokst"):
        gata += r["bokst"]
    staddr = ""
    if r.get("postnr") and r.get("stadur_nf"):
        staddr = f"{r['postnr']} {r['stadur_nf']}"
    elif r.get("stadur_nf"):
        staddr = r["stadur_nf"]
    return f"{gata}, {staddr}" if staddr else gata


def build_weather_payload(label, lat, lon, stod_nafn, stod_lat, stod_lon, data, spa):
    wind_abbr = data.get("D", "")
    return {
        "heimilisfang": label,
        "lat": lat,
        "lon": lon,
        "stod": {"nafn": stod_nafn, "lat": stod_lat, "lon": stod_lon},
        "vedur": {
            "hitastig":   parse_num(data.get("T")),
            "vindhradi":  parse_num(data.get("F")),
            "vindaett":   VINDAETT_FULL.get(wind_abbr, wind_abbr or "Óþekkt"),
            "rok":        parse_num(data.get("FX")),
            "loftthyngd": parse_num(data.get("P")),
            "vedurlag":   data.get("W", ""),
            "raki":       parse_num(data.get("RH")),
            "timi":       data.get("time", ""),
        },
        "spa": spa,
    }


def group_forecast_by_day(periods):
    days = defaultdict(list)
    for p in periods:
        ftime = p.get("ftime", "")
        if ftime:
            days[ftime[:10]].append(p)

    result = []
    for date_str in sorted(days.keys())[:6]:
        ps = days[date_str]
        temps    = [t for t in (parse_num(p.get("T")) for p in ps) if t is not None]
        winds    = [w for w in (parse_num(p.get("F")) for p in ps) if w is not None]
        precips  = [r for r in (parse_num(p.get("R")) for p in ps) if r is not None]
        dirs     = [p["D"] for p in ps if p.get("D")]
        weathers = [p["W"] for p in ps if p.get("W")]
        top_dir  = max(set(dirs),     key=dirs.count)     if dirs     else None
        top_w    = max(set(weathers), key=weathers.count) if weathers else ""
        result.append({
            "dagur":     date_str,
            "min_hiti":  min(temps) if temps else None,
            "max_hiti":  max(temps) if temps else None,
            "vindhradi": round(sum(winds) / len(winds), 1) if winds else None,
            "vindaett":  VINDAETT_FULL.get(top_dir, top_dir or ""),
            "vedurlag":  top_w,
            "uri":       round(sum(precips), 1) if precips else 0,
        })
    return result


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/suggest")
def suggest():
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    results = iceaddr_suggest(q, limit=10)
    seen, unique = set(), []
    for r in results:
        if not r.get("heiti_nf"):
            continue
        label = format_addr(r)
        if label not in seen:
            seen.add(label)
            unique.append(label)
        if len(unique) >= 8:
            break
    return jsonify(unique)


@app.route("/api/stations")
def stations_endpoint():
    global _stations_cache, _stations_cache_ts
    if _stations_cache is not None and (time.time() - _stations_cache_ts) < _STATIONS_TTL:
        return jsonify(_stations_cache)

    all_s = station_list()
    ids   = [s["id"] for s in all_s]

    # Sækja observations í lotum til að vera viss um að URL verði ekki of langur
    obs_map = {}
    BATCH = 100
    for i in range(0, len(ids), BATCH):
        batch = ids[i:i + BATCH]
        try:
            data = observation_for_stations(batch)
            for r in data.get("results", []):
                obs_map[str(r.get("id", ""))] = r
        except Exception:
            pass

    result = []
    for s in all_s:
        obs = obs_map.get(str(s["id"]), {})
        result.append({
            "id":       s["id"],
            "nafn":     s["name"],
            "lat":      s["lat"],
            "lon":      s["lon"],
            "hitastig": parse_num(obs.get("T")),
            "vedurlag": obs.get("W", ""),
        })

    _stations_cache = result
    _stations_cache_ts = time.time()
    return jsonify(result)


@app.route("/api/weather")
def weather():
    address = request.args.get("address", "").strip()
    if not address:
        return jsonify({"error": "Ekkert heimilisfang gefið upp"}), 400

    results = iceaddr_suggest(address, limit=1)
    if not results:
        return jsonify({"error": "Heimilisfang fannst ekki"}), 404

    loc = results[0]
    lat = loc.get("lat_wgs84")
    lon = loc.get("long_wgs84")
    if not lat or not lon:
        return jsonify({"error": "Ekki tókst að finna GPS hnit"}), 404

    obs, station = observation_for_closest(lat, lon)
    if not obs or not obs.get("results"):
        return jsonify({"error": "Ekki tókst að sækja veðurgögn"}), 503

    try:
        fc, _ = forecast_for_closest(lat, lon)
        fc_periods = (fc.get("results") or [{}])[0].get("forecast", [])
        spa = group_forecast_by_day(fc_periods)
    except Exception:
        spa = []

    return jsonify(build_weather_payload(
        label=format_addr(loc),
        lat=lat, lon=lon,
        stod_nafn=station.get("name", "Óþekkt stöð"),
        stod_lat=station.get("lat"), stod_lon=station.get("lon"),
        data=obs["results"][0], spa=spa,
    ))


@app.route("/api/weather_by_station")
def weather_by_station():
    sid = request.args.get("id", "").strip()
    if not sid:
        return jsonify({"error": "Ekkert stöðvarauðkenni"}), 400

    try:
        s = station_for_id(int(sid))
    except (ValueError, TypeError):
        return jsonify({"error": "Ógilt stöðvarauðkenni"}), 400

    if not s:
        return jsonify({"error": "Stöð fannst ekki"}), 404

    obs = observation_for_station(sid)
    if not obs or not obs.get("results"):
        return jsonify({"error": "Ekki tókst að sækja veðurgögn"}), 503

    try:
        fc = forecast_for_station(sid)
        fc_periods = (fc.get("results") or [{}])[0].get("forecast", [])
        spa = group_forecast_by_day(fc_periods)
    except Exception:
        spa = []

    return jsonify(build_weather_payload(
        label=s["name"],
        lat=s["lat"], lon=s["lon"],
        stod_nafn=s["name"], stod_lat=s["lat"], stod_lon=s["lon"],
        data=obs["results"][0], spa=spa,
    ))


@app.route("/api/forecast_text")
def forecast_text_endpoint():
    try:
        data = forecast_text(5)
        results = data.get("results", [])
        if not results:
            return jsonify({"error": "Engin textaspá til"}), 404
        r = results[0]
        return jsonify({
            "titill":    r.get("title", ""),
            "efni":      r.get("content", ""),
            "gilt_fra":  r.get("valid_from", ""),
            "gilt_til":  r.get("valid_to", ""),
            "buid_til":  r.get("creation", ""),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 503


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
