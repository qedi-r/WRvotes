#!/usr/bin/env python3
import json
import glob
import os
from shapely.geometry import shape, mapping, MultiPolygon

# requires shapely and dependencies. running:
# pip install shapely
# should be sufficient


# Sources:
# Kitchener: https://open-kitchenergis.opendata.arcgis.com/datasets/KitchenerGIS::wards
# Waterloo: https://rowopendata-rmw.opendata.arcgis.com/maps/71fb5d53368e4936b4309d88deb86549
# Cambridge: https://geohub.cambridge.ca/datasets/cityofcambridge::wards-2/explore?location=43.402300%2C-80.331400%2C12
# Wellesley**: https://www.wellesley.ca/media/f40h5ood/townshipofwellesley_wardmap_2026.pdf
# Woolwich**: https://woolwich-geohub-woolwich.hub.arcgis.com/documents/c68bc6d2268e497e98263fd26a147c04/about
# North Dumfries**: https://experience.arcgis.com/experience/b8f663f04cd8471fb5cc8a0fbe56527a
# Wilmot**: https://www.wilmot.ca/media/ra5pfa5y/allwards.pdf
# ** denotes old shapefile used from 2022 election, visual inspection with boundaries done via links above

DIR = os.path.dirname(os.path.abspath(__file__))

STYLE = {
    "stroke-opacity": 1,
    "stroke-width": 2.5,
    "fill": "#fff",
    "fill-opacity": 0.4,
}

OVERLAP_STYLE = {
    "stroke": "#e74c3c",
    "stroke-opacity": 1,
    "stroke-width": 2,
    "fill": "#e74c3c",
    "fill-opacity": 0.55,
}


def info_link(slug, num):
    return f'<a href="by-ward/{slug}-Ward-{num:02d}">Positions and Candidates</a>'


def normalize_cambridge(feature):
    n = feature["properties"]["WARD_ID"]
    return {
        **feature,
        "properties": {
            "Name": f"Cambridge Ward {n}",
            "stroke": "#FA6800",
            "information-link": info_link("Cambridge", n),
            **STYLE,
        },
    }


def normalize_kitchener(feature):
    n = feature["properties"]["WARDID"]
    return {
        **feature,
        "properties": {
            "Name": f"Kitchener Ward {n}",
            "stroke": "#aa00ff",
            "information-link": info_link("Kitchener", n),
            **STYLE,
        },
    }


def normalize_waterloo(feature):
    n = feature["properties"]["WARD_NO"]
    return {
        **feature,
        "properties": {
            "Name": f"Waterloo Ward {n}",
            "stroke": "#f1c40f",
            "information-link": info_link("Waterloo", n),
            **STYLE,
        },
    }


def load(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


sources = [
    ("Cambridge-Wards.geojson", normalize_cambridge),
    ("Kitchener-Wards_4671744091772333670.geojson", normalize_kitchener),
    ("Waterloo-Wards2022.geojson", normalize_waterloo),
    ("Townships.geojson", lambda f: f),
]

# Kitchener and Waterloo share a boundary where some properties can vote in
# either ward. Other inter-municipal overlaps are shapefile precision artifacts.
KITCHENER = 1
WATERLOO = 2

# Only these specific ward pairs have confirmed genuine dual-ward areas.
# Value is the number of discrete overlap shapes to keep (largest first);
EXPECTED_OVERLAPS = {
    frozenset({"Kitchener Ward 9", "Waterloo Ward 7"}): 3,
    frozenset({"Kitchener Ward 10", "Waterloo Ward 7"}): 3,
    frozenset({"Kitchener Ward 8", "Waterloo Ward 7"}): 3,
    frozenset({"Kitchener Ward 10", "Waterloo Ward 5"}): 1,
}


def top_n_polygons(geom, n):
    """Return the n largest polygon components of geom as a single geometry."""
    if geom.geom_type == "Polygon":
        parts = [geom]
    elif geom.geom_type == "MultiPolygon":
        parts = list(geom.geoms)
    elif geom.geom_type == "GeometryCollection":
        parts = [g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")]
    else:
        return geom
    parts.sort(key=lambda g: g.area, reverse=True)
    kept = parts[:n]
    return kept[0] if len(kept) == 1 else MultiPolygon(kept)


def load_features_with_sources():
    # Load all features, tracking which source each came from
    indexed = []  # list of (source_idx, feature)
    for source_idx, (path, normalize) in enumerate(sources):
        if not os.path.isabs(path):
            path = os.path.join(DIR, path)
        data = load(path)
        for feature in data["features"]:
            if feature["type"] == "Feature":
                indexed.append((source_idx, normalize(feature)))
    return indexed


def convert_to_shapely_geo(indexed):
    return [shape(f["geometry"]) for _, f in indexed]


def find_and_clip_overlaps(indexed):
    # Find inter-source overlaps, clip them out of both polygons, collect as zones
    geometries = convert_to_shapely_geo(indexed)
    overlap_zones = []
    for i, (src_i, feat_i) in enumerate(indexed):
        for j, (src_j, feat_j) in enumerate(indexed[i + 1 :], i + 1):
            if {src_i, src_j} != {KITCHENER, WATERLOO}:
                continue
            name_pair = frozenset(
                {feat_i["properties"]["Name"], feat_j["properties"]["Name"]}
            )
            if name_pair not in EXPECTED_OVERLAPS:
                continue
            try:
                inter = geometries[i].intersection(geometries[j])
            except Exception:
                continue
            if inter.is_empty or inter.area < 1e-10:
                continue
            inter = top_n_polygons(inter, EXPECTED_OVERLAPS[name_pair])

            name_a = feat_i["properties"]["Name"]
            name_b = feat_j["properties"]["Name"]
            link_a = feat_i["properties"].get("information-link", "")
            link_b = feat_j["properties"].get("information-link", "")

            geometries[i] = geometries[i].difference(inter)
            geometries[j] = geometries[j].difference(inter)

            overlap_zones.append(
                {
                    "type": "Feature",
                    "geometry": mapping(inter),
                    "properties": {
                        "Name": "Overlapping Boundary",
                        "information-link": (
                            f"Properties in this area may be eligible to vote in "
                            f"<strong>{name_a}</strong> and/or <strong>{name_b}</strong>. "
                            f"Contact your municipality to confirm which ward applies to your address. "
                            f"{link_a} &mdash; {link_b}"
                        ),
                        **OVERLAP_STYLE,
                    },
                }
            )
    return overlap_zones, list(zip(indexed, geometries))


def rebuild_features(indexed_geometries, overlap_zones):
    # Rebuild features with corrected (non-overlapping) geometries
    features = []
    for (_, feat), geom in indexed_geometries:
        features.append({**feat, "geometry": mapping(geom)})

    features.extend(overlap_zones)
    return features


def output_features(features, overlap_zone_len):
    output = {"type": "FeatureCollection", "features": features}
    out_path = os.path.join(DIR, "WardBoundaries.geojson")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f)

    print(
        f"Wrote {len(features)} features to {out_path} ({overlap_zone_len} overlap zones)"
    )


indexed = load_features_with_sources()
overlap_zones, indexed_geometries = find_and_clip_overlaps(indexed)
features = rebuild_features(indexed_geometries, overlap_zones)
output_features(features, len(overlap_zones))
