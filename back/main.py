#!/usr/bin/env python3
"""
Hack4Mobility CDMX — API de accesibilidad urbana en Tlalpan.

Endpoints:
  GET /colonias           → GeoJSON completo (179 colonias)
  GET /colonias/{cve_col} → Detalle + descripción generada por IA
  GET /zonas-riesgo       → Colonias con score >= 4, con centroide
  GET /resumen            → Estadísticas agregadas
"""

from contextlib import asynccontextmanager
import json
import math
import os

import groq
import geopandas as gpd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

GEOJSON_PATH = "tlalpan_accesibilidad.geojson"

# Cargados una vez en memoria al arrancar la app
_gdf: gpd.GeoDataFrame | None = None
_geojson_bytes: bytes | None = None          # GeoJSON pre-serializado
_client: groq.AsyncGroq | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _gdf, _geojson_bytes, _client

    _gdf = gpd.read_file(GEOJSON_PATH)
    _geojson_bytes = _gdf.to_json().encode()

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY no está definida en el entorno")
    _client = groq.AsyncGroq(api_key=api_key)

    print(f"✓ GeoJSON cargado: {len(_gdf)} colonias")
    yield

    await _client.close()


app = FastAPI(
    title="Hack4Mobility CDMX API",
    description="Accesibilidad peatonal y ciclista en Tlalpan, CDMX",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _row_or_404(cve_col: str):
    """Devuelve la fila de la colonia o lanza 404."""
    subset = _gdf[_gdf["cve_col"] == cve_col]
    if subset.empty:
        raise HTTPException(status_code=404, detail=f"Colonia '{cve_col}' no encontrada")
    return subset.iloc[0]


def _safe_int(val) -> int | None:
    """Convierte numpy int32/float a Python int, manejando NaN."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    return int(val)


def _safe_float(val) -> float | None:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    return round(float(val), 2)


_SISTEMA_MOVILIDAD = (
    "Eres un asistente especializado en movilidad urbana inclusiva para la Ciudad de México. "
    "Tu rol es explicar en lenguaje claro y empático, en español, cómo es la experiencia "
    "de moverse por distintas colonias de Tlalpan para personas con movilidad reducida, "
    "adultos mayores o personas con discapacidad. Siempre eres directo, humano y útil. "
    "Nunca usas tecnicismos innecesarios. Nunca uses markdown."
)

_INFRAPEAT_DESCRIPCION = {
    "Alta":  "buena presencia de banquetas, rampas y pasos peatonales",
    "Media": "infraestructura peatonal parcial, con algunas banquetas en buen estado pero sin rampas consistentes",
    "Baja":  "escasa infraestructura peatonal, banquetas deterioradas o inexistentes en varios tramos",
    "Nula":  "sin infraestructura peatonal formal; las personas deben caminar sobre tierra o la vialidad",
}


async def _generar_descripcion_ia(row) -> str:
    colonia = row["colonia"]
    infrapeat = row["INFRAPEAT"]
    score = _safe_float(row["score_accesibilidad"])
    cp_camin = _safe_int(row["Cp_CAMIN"])
    cp_cicl = _safe_int(row["Cp_INFCICL"])

    infra_desc = _INFRAPEAT_DESCRIPCION.get(infrapeat, infrapeat)

    usuario_prompt = (
        f"Describe en 2-3 oraciones cómo es moverse por la colonia {colonia} en Tlalpan "
        f"para una persona con movilidad reducida.\n\n"
        f"Datos disponibles:\n"
        f"- Infraestructura peatonal: {infrapeat} ({infra_desc})\n"
        f"- Score de accesibilidad general: {score}/5 (donde 5 es la peor situación posible)\n"
        f"- Accesibilidad peatonal (cuantil 1-5, 5=peor): {cp_camin}\n"
        f"- Infraestructura ciclista (cuantil 1-5, 5=peor): {cp_cicl}\n\n"
        f"Sé empático y concreto. Menciona qué representa el reto principal en esta colonia."
    )

    response = await _client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=250,
        messages=[
            {"role": "system", "content": _SISTEMA_MOVILIDAD},
            {"role": "user",   "content": usuario_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get(
    "/colonias",
    summary="GeoJSON completo de las 179 colonias de Tlalpan",
    response_class=Response,
)
async def get_colonias():
    """
    Devuelve un FeatureCollection GeoJSON con todas las colonias y sus campos
    de accesibilidad. Listo para consumir desde Mapbox o Kepler.gl.
    """
    return Response(content=_geojson_bytes, media_type="application/geo+json")


@app.get(
    "/colonias/{cve_col}",
    summary="Detalle de una colonia con descripción generada por IA",
)
async def get_colonia(cve_col: str):
    """
    Devuelve nombre, score, nivel INFRAPEAT y una descripción en lenguaje
    natural generada por Claude explicando la transitabilidad de la colonia
    para personas con movilidad reducida.
    """
    row = _row_or_404(cve_col)

    try:
        descripcion = await _generar_descripcion_ia(row)
    except groq.APIError as e:
        raise HTTPException(status_code=502, detail=f"Error en Groq API: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al generar descripción: {str(e)}")

    return {
        "cve_col": row["cve_col"],
        "colonia": row["colonia"],
        "alcaldia": "TLALPAN",
        "pob_2010": _safe_int(row["pob_2010"]),
        "score_accesibilidad": _safe_float(row["score_accesibilidad"]),
        "nivel_acceso": row["nivel_acceso"],
        "INFRAPEAT": row["INFRAPEAT"],
        "Cp_CAMIN": _safe_int(row["Cp_CAMIN"]),
        "Cp_INFCICL": _safe_int(row["Cp_INFCICL"]),
        "C_pEPICCAM": _safe_int(row["C_pEPICCAM"]),
        "descripcion_ia": descripcion,
    }


@app.get(
    "/zonas-riesgo",
    summary="Colonias con peor accesibilidad (score >= 4), con centroide",
)
async def get_zonas_riesgo():
    """
    Devuelve las colonias con score_accesibilidad >= 4 (problemática o muy
    problemática), ordenadas de mayor a menor score. Incluye las coordenadas
    del centroide de cada polígono para marcar puntos en el mapa.
    """
    alto_riesgo = (
        _gdf[_gdf["score_accesibilidad"] >= 4]
        .copy()
        .sort_values("score_accesibilidad", ascending=False)
    )

    result = []
    for _, row in alto_riesgo.iterrows():
        centroid = row.geometry.centroid
        result.append(
            {
                "cve_col": row["cve_col"],
                "colonia": row["colonia"],
                "score_accesibilidad": _safe_float(row["score_accesibilidad"]),
                "nivel_acceso": row["nivel_acceso"],
                "INFRAPEAT": row["INFRAPEAT"],
                "centroide": {
                    "lat": round(centroid.y, 6),
                    "lng": round(centroid.x, 6),
                },
            }
        )

    return {"total": len(result), "colonias": result}


@app.get("/resumen", summary="Estadísticas agregadas de accesibilidad en Tlalpan")
async def get_resumen():
    """
    Devuelve: total de colonias, score promedio, distribución por nivel de
    infraestructura peatonal, distribución por score categorizado, y la colonia
    con la peor situación de accesibilidad.
    """
    peor_idx = _gdf["score_accesibilidad"].idxmax()
    peor = _gdf.loc[peor_idx]

    return {
        "alcaldia": "TLALPAN",
        "total_colonias": len(_gdf),
        "score_promedio": _safe_float(_gdf["score_accesibilidad"].mean()),
        "score_min": _safe_float(_gdf["score_accesibilidad"].min()),
        "score_max": _safe_float(_gdf["score_accesibilidad"].max()),
        "distribucion_infrapeat": (
            _gdf["INFRAPEAT"].value_counts().sort_index().to_dict()
        ),
        "distribucion_nivel_score": (
            _gdf["nivel_acceso"].value_counts().sort_index().to_dict()
        ),
        "colonias_alto_riesgo": int((_gdf["score_accesibilidad"] >= 4).sum()),
        "peor_colonia": {
            "cve_col": peor["cve_col"],
            "colonia": peor["colonia"],
            "score_accesibilidad": _safe_float(peor["score_accesibilidad"]),
            "INFRAPEAT": peor["INFRAPEAT"],
            "nivel_acceso": peor["nivel_acceso"],
        },
    }
