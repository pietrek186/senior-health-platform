import math
import re
from urllib.parse import quote_plus

import requests
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET

# User-Agent wymagany przez OSM/Nominatim/Overpass
USER_AGENT = getattr(settings, "OSM_USER_AGENT", "ZdrowieApp/1.0 (kontakt@example.com)")
CACHE_TTL = 60 * 10           # 10 min – dane placówek
REVERSE_TTL = 60 * 60 * 24    # 24 h – cache reverse geocode


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p = math.pi / 180
    dlat = (lat2 - lat1) * p
    dlon = (lon2 - lon1) * p
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


@require_GET
def geocode(request):
    q = request.GET.get("query", "").strip()
    if not q:
        return HttpResponseBadRequest("missing query")
    cache_key = f"geocode:{q}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse(cached)

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": q, "format": "jsonv2", "limit": 1, "addressdetails": 1}
    resp = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        result = {"ok": False, "error": "Nie znaleziono adresu."}
        cache.set(cache_key, result, CACHE_TTL)
        return JsonResponse(result)

    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])
    result = {"ok": True, "lat": lat, "lon": lon, "display_name": data[0].get("display_name")}
    cache.set(cache_key, result, CACHE_TTL)
    return JsonResponse(result)


# --------- Specjalności: tłumaczenia i heurystyki ---------

SPECIALITY_PL = {
    # kluczowe:
    "diabetology": "diabetologia",
    "endocrinology": "endokrynologia",
    "cardiology": "kardiologia",
    "hypertension": "hipertensjologia",
    "hypertensiology": "hipertensjologia",
    "internal": "choroby wewnętrzne",
    "internal_medicine": "choroby wewnętrzne",
    # ogólne/częste:
    "family_medicine": "medycyna rodzinna",
    "general": "lekarz ogólny",
    "primary_care": "podstawowa opieka zdrowotna",
    "angiology": "angiologia",
    "nephrology": "nefrologia",
    "pulmonology": "pulmonologia",
    "dermatology": "dermatologia",
    "ophthalmology": "okulistyka",
    "neurology": "neurologia",
    "orthopaedics": "ortopedia",
    "orthopedics": "ortopedia",
    "urology": "urologia",
    "radiology": "radiologia",
    "oncology": "onkologia",
    "immunology": "immunologia",
    "physiotherapy": "fizjoterapia",
    "osteopathy": "osteopatia",
    "gynaecology": "ginekologia",
    "gynecology": "ginekologia",
    "obstetrics": "położnictwo",
    "haematology": "hematologia",
    "hematology": "hematologia",
    "psychiatry": "psychiatria",
    "psychology": "psychologia",
    "dietetics": "dietetyka",
    "dietitian": "dietetyka",
    "paediatrics": "pediatria",
    "pediatrics": "pediatria",
    "allergology": "alergologia",
    "otolaryngology": "laryngologia",
    "otorhinolaryngology": "laryngologia",
    "ent": "laryngologia",
    "laryngology": "laryngologia",
    "gastroenterology": "gastroenterologia",
    "hepatology": "hepatologia",
    "endoscopy": "endoskopia",
    "plastic_surgery": "chirurgia plastyczna",
    "neurosurgery": "neurochirurgia",
    "vascular_surgery": "chirurgia naczyniowa",
    "surgery": "chirurgia",
    "rheumatology": "reumatologia",
    "nutrition counselling": "doradztwo żywieniowe",
    "specialist pediatrician": "specjalista pediatra",
    "dermatovenereology": "dermatowenerologia",
    "birthing_centre": "centrum porodowe",
    "badania_ekg": "badania EKG",
    "badania_usg": "badania USG",
    # czasem ktoś wpisze „clinic” jako speciality – przetłumaczmy sensownie:
    "clinic": "przychodnia",
    "hospital": "szpital",
}

HEALTHCARE_TO_PL = {
    "doctor": "lekarz",
    "doctors": "lekarz",
    "clinic": "przychodnia",
    "hospital": "szpital",
    "centre": "ośrodek medyczny",
}


def translate_speciality_list(raw: str) -> str:
    """Przetłumacz i sformatuj specjalności rozdzielone ; , lub |"""
    if not raw:
        return ""
    tokens = [t.strip().lower() for t in re.split(r"[;,\|]\s*", raw) if t.strip()]
    mapped = [SPECIALITY_PL.get(t, t.replace("_", " ")) for t in tokens]
    unique = list(dict.fromkeys(mapped))
    return ", ".join(unique)


# 3 filtry: diabetolog, kardiolog, wszystkie
FILTER_REGEX = {
    "diabetologist": "diabetology|endocrinology",
    "cardiologist": "cardiology|hypertension|hypertensiology",
    "general": None,
}


def reverse_address(lat: float, lon: float):
    """Reverse geocode (cache). Zwraca dict: {'text': 'ulica nr, miasto, kod', 'city': 'miasto'}."""
    key = f"rev:{lat:.5f}:{lon:.5f}"
    cached = cache.get(key)
    if cached:
        return cached
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "jsonv2", "addressdetails": 1}
    try:
        resp = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        addr = data.get("address", {}) if isinstance(data, dict) else {}
        city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("hamlet") or addr.get("suburb")
        street = " ".join([v for v in [addr.get("road"), addr.get("house_number")] if v])
        parts = []
        if street: parts.append(street)
        if city: parts.append(city)
        if addr.get("postcode"): parts.append(addr.get("postcode"))
        text = ", ".join(parts) or data.get("display_name", "")
        result = {"text": text, "city": city or ""}
        cache.set(key, result, REVERSE_TTL)
        return result
    except Exception:
        return {"text": "", "city": ""}


@require_GET
def reverse_geocode(request):
    """Endpoint używany przez front do dociągnięcia adresu dla rekordów bez addr:*."""
    try:
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("missing lat/lon")
    res = reverse_address(lat, lon)
    return JsonResponse({"ok": bool(res.get("text")), "address": res.get("text", ""), "city": res.get("city", "")})


@require_GET
def clinics(request):
    try:
        lat = float(request.GET.get("lat"))
        lon = float(request.GET.get("lon"))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("missing lat/lon")

    radius_km = float(request.GET.get("radius_km", 20))
    radius_m = int(radius_km * 1000)
    filter_key = (request.GET.get("filter") or "general").strip()

    cache_key = f"clinics:{lat:.5f}:{lon:.5f}:{radius_m}:{filter_key}"
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse(cached)

    if FILTER_REGEX.get(filter_key):
        regex = FILTER_REGEX[filter_key]
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["healthcare"~"clinic|hospital|doctor"]["healthcare:speciality"~"{regex}",i](around:{radius_m},{lat},{lon});
          way["healthcare"~"clinic|hospital|doctor"]["healthcare:speciality"~"{regex}",i](around:{radius_m},{lat},{lon});
          relation["healthcare"~"clinic|hospital|doctor"]["healthcare:speciality"~"{regex}",i](around:{radius_m},{lat},{lon});

          node["healthcare"~"clinic|hospital|doctor"]["speciality"~"{regex}",i](around:{radius_m},{lat},{lon});
          way["healthcare"~"clinic|hospital|doctor"]["speciality"~"{regex}",i](around:{radius_m},{lat},{lon});
          relation["healthcare"~"clinic|hospital|doctor"]["speciality"~"{regex}",i](around:{radius_m},{lat},{lon});

          node["healthcare"~"clinic|hospital|doctor"]["department"~"{regex}",i](around:{radius_m},{lat},{lon});
          way["healthcare"~"clinic|hospital|doctor"]["department"~"{regex}",i](around:{radius_m},{lat},{lon});
          relation["healthcare"~"clinic|hospital|doctor"]["department"~"{regex}",i](around:{radius_m},{lat},{lon});

          node["healthcare"~"clinic|hospital|doctor"]["medical:department"~"{regex}",i](around:{radius_m},{lat},{lon});
          way["healthcare"~"clinic|hospital|doctor"]["medical:department"~"{regex}",i](around:{radius_m},{lat},{lon});
          relation["healthcare"~"clinic|hospital|doctor"]["medical:department"~"{regex}",i](around:{radius_m},{lat},{lon});

          node["amenity"~"doctors|clinic|hospital"]["speciality"~"{regex}",i](around:{radius_m},{lat},{lon});
          way["amenity"~"doctors|clinic|hospital"]["speciality"~"{regex}",i](around:{radius_m},{lat},{lon});
          relation["amenity"~"doctors|clinic|hospital"]["speciality"~"{regex}",i](around:{radius_m},{lat},{lon});
        );
        out center tags;
        """
    else:
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["healthcare"~"clinic|hospital|doctor|centre"](around:{radius_m},{lat},{lon});
          way["healthcare"~"clinic|hospital|doctor|centre"](around:{radius_m},{lat},{lon});
          relation["healthcare"~"clinic|hospital|doctor|centre"](around:{radius_m},{lat},{lon});

          node["amenity"~"doctors|clinic|hospital"](around:{radius_m},{lat},{lon});
          way["amenity"~"doctors|clinic|hospital"](around:{radius_m},{lat},{lon});
          relation["amenity"~"doctors|clinic|hospital"](around:{radius_m},{lat},{lon});
        );
        out center tags;
        """

    resp = requests.post(
        "https://overpass-api.de/api/interpreter",
        data=overpass_query.encode("utf-8"),
        headers={"User-Agent": USER_AGENT, "Content-Type": "text/plain; charset=UTF-8"},
        timeout=60
    )
    resp.raise_for_status()
    data = resp.json()

    features = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name") or tags.get("official_name") or "Placówka medyczna"

        # współrzędne
        if el["type"] == "node":
            clat, clon = el["lat"], el["lon"]
        else:
            center = el.get("center") or {}
            clat, clon = center.get("lat"), center.get("lon")
            if clat is None or clon is None:
                continue

        distance = haversine_km(lat, lon, clat, clon)

        # Adres z tagów
        city = tags.get("addr:city") or tags.get("addr:town") or tags.get("addr:suburb") or tags.get("addr:hamlet") or tags.get("addr:place")
        street = " ".join([v for v in [tags.get("addr:street"), tags.get("addr:housenumber")] if v])
        parts = []
        if street: parts.append(street)
        if city: parts.append(city)
        if tags.get("addr:postcode"): parts.append(tags.get("addr:postcode"))
        addr = ", ".join(parts) or tags.get("addr:full") or ""

        # Specjalności
        spec_raw = (
            tags.get("healthcare:speciality") or tags.get("speciality") or
            tags.get("department") or tags.get("medical:department") or ""
        )
        spec_pl = translate_speciality_list(spec_raw)
        if not spec_pl:
            hc = (tags.get("healthcare") or tags.get("amenity") or "").lower()
            if hc:
                top_token = hc.split(";")[0].strip()
                spec_pl = HEALTHCARE_TO_PL.get(top_token, top_token.replace("_", " "))

        phone = tags.get("phone") or tags.get("contact:phone")
        website = tags.get("website") or tags.get("contact:website")

        # Fallback www -> wyszukiwarka
        search_q = name + (f" {city}" if city else "")
        search_url = f"https://duckduckgo.com/?q={quote_plus(search_q)}"

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [clon, clat]},
            "properties": {
                "name": name,
                "address": addr,                 # UWAGA: jeśli puste, front dociągnie reverse
                "distance_km": round(distance, 2),
                "speciality": spec_pl,
                "phone": phone,
                "website": website,
                "search_url": search_url,
                # (bez OSM – usuwamy z listy/pop-upu)
            }
        })

    features.sort(key=lambda f: f["properties"]["distance_km"])
    result = {"ok": True, "count": len(features), "features": features}
    cache.set(cache_key, result, CACHE_TTL)
    return JsonResponse(result)
