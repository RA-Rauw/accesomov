#!/usr/bin/env python3
"""
Hack4Mobility CDMX — Análisis de accesibilidad peatonal y ciclista en Tlalpan.
Produce tlalpan_accesibilidad.geojson listo para Mapbox/Kepler.gl.
"""

import warnings
warnings.filterwarnings("ignore")

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
CICLIS_PATH = "datos/esppub_ciclis_peat/esppub_ciclis_peat.shp"
INFRA_PATH  = "datos/Nivel de presencia de infraestructura peatonal por colonia/Dist_acce_infra.shp"
OUTPUT_GEOJSON = "tlalpan_accesibilidad.geojson"
OUTPUT_PNG     = "tlalpan_accesibilidad.png"

# ---------------------------------------------------------------------------
# 1. Cargar shapefiles (encoding CP1252)
# ---------------------------------------------------------------------------
print("Cargando shapefiles...")
gdf_ciclis = gpd.read_file(CICLIS_PATH, encoding="cp1252")
gdf_infra  = gpd.read_file(INFRA_PATH,  encoding="cp1252")
print(f"  esppub_ciclis_peat : {len(gdf_ciclis):>4} colonias — CRS: {gdf_ciclis.crs}")
print(f"  Dist_acce_infra    : {len(gdf_infra):>4} colonias — CRS: {gdf_infra.crs}")

# ---------------------------------------------------------------------------
# 2. Filtrar Tlalpan
# ---------------------------------------------------------------------------
ciclis_tl = gdf_ciclis[gdf_ciclis["alcaldia"] == "TLALPAN"].copy()
infra_tl  = gdf_infra[ gdf_infra["alcaldia"]  == "TLALPAN"].copy()
print(f"\nTlalpan — ciclis: {len(ciclis_tl)} colonias | infra: {len(infra_tl)} colonias")

# ---------------------------------------------------------------------------
# 3. Merge por cve_col (geometry viene de ciclis)
# ---------------------------------------------------------------------------
merged = ciclis_tl.merge(
    infra_tl[["cve_col", "INFRAPEAT"]],
    on="cve_col",
    how="left",
)
print(f"Merge resultado    : {len(merged)} colonias | INFRAPEAT nulos: {merged['INFRAPEAT'].isna().sum()}")

# ---------------------------------------------------------------------------
# 4. Convertir a EPSG:4326 (WGS84)
# ---------------------------------------------------------------------------
merged = merged.to_crs(epsg=4326)
print(f"CRS convertido     : {merged.crs}")

# ---------------------------------------------------------------------------
# 5. Calcular score_accesibilidad (1=bueno … 5=problemático)
#    INFRAPEAT (cualitativo)  → numérico:
#      Nula=5  Baja=4  Media=3  Alta=2  Muy Alta=1
#    C_pEPICCAM ya está en escala 1-5 (5=mayor problemática)
#    score = promedio(infrapeat_score, C_pEPICCAM)
# ---------------------------------------------------------------------------
INFRAPEAT_MAP = {
    "Nula":     5,
    "Muy baja": 5,
    "Baja":     4,
    "Media":    3,
    "Alta":     2,
    "Muy Alta": 1,
}

merged["infrapeat_score"]   = merged["INFRAPEAT"].map(INFRAPEAT_MAP)
merged["score_accesibilidad"] = (
    (merged["infrapeat_score"] + merged["C_pEPICCAM"]) / 2
).round(2)

# Etiqueta legible
NIVEL_BINS   = [0, 1.5, 2.5, 3.5, 4.5, 5.1]
NIVEL_LABELS = ["1-Muy buena", "2-Buena", "3-Media", "4-Mala", "5-Muy mala"]
merged["nivel_acceso"] = pd.cut(
    merged["score_accesibilidad"], bins=NIVEL_BINS, labels=NIVEL_LABELS
)

# ---------------------------------------------------------------------------
# 6. Resumen en consola
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("COLONIAS POR NIVEL DE ACCESIBILIDAD (score 1=mejor, 5=peor)")
print("=" * 60)
resumen = merged["nivel_acceso"].value_counts().sort_index()
for nivel, n in resumen.items():
    print(f"  {nivel:<20} : {n:>3} colonias")

print("\n" + "=" * 60)
print("TOP 10 COLONIAS CON PEOR SCORE DE ACCESIBILIDAD")
print("=" * 60)
cols_display = ["colonia", "INFRAPEAT", "infrapeat_score", "C_pEPICCAM", "score_accesibilidad"]
worst10 = (
    merged[cols_display]
    .nlargest(10, "score_accesibilidad")
    .reset_index(drop=True)
)
worst10.index += 1
print(worst10.to_string())

# ---------------------------------------------------------------------------
# 7. Exportar GeoJSON
# ---------------------------------------------------------------------------
export_cols = [
    "cve_col", "colonia", "pob_2010",
    "INFRAPEAT", "infrapeat_score",
    "Cp_CAMIN", "Cp_INFCICL", "C_pEPICCAM",
    "score_accesibilidad", "nivel_acceso",
    "geometry",
]
merged[export_cols].to_file(OUTPUT_GEOJSON, driver="GeoJSON")
print(f"\nGeoJSON exportado  : {OUTPUT_GEOJSON}")
print(f"  Propiedades      : {[c for c in export_cols if c != 'geometry']}")

# ---------------------------------------------------------------------------
# 8. Plot de verificación
# ---------------------------------------------------------------------------
COLORS = {
    "1-Muy buena": "#1a9641",
    "2-Buena":     "#a6d96a",
    "3-Media":     "#ffffbf",
    "4-Mala":      "#fdae61",
    "5-Muy mala":  "#d7191c",
}

fig, ax = plt.subplots(1, 1, figsize=(10, 13))
ax.set_facecolor("#f0f0f0")

for nivel, color in COLORS.items():
    subset = merged[merged["nivel_acceso"] == nivel]
    if len(subset) > 0:
        subset.plot(ax=ax, color=color, edgecolor="white", linewidth=0.3)

# Leyenda manual
patches = [mpatches.Patch(color=c, label=l) for l, c in COLORS.items()]
ax.legend(
    handles=patches,
    title="Score accesibilidad\n(1=mejor, 5=peor)",
    loc="lower left",
    fontsize=9,
    title_fontsize=9,
    framealpha=0.9,
)

ax.set_title(
    "Tlalpan CDMX — Accesibilidad Peatonal y Ciclista por Colonia\n"
    "Hack4Mobility CDMX · Fuente: Datos Abiertos CDMX",
    fontsize=13,
    pad=15,
)
ax.set_axis_off()
plt.tight_layout()
plt.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight")
plt.show()
print(f"Plot guardado      : {OUTPUT_PNG}")
