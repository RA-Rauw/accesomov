# AccesoMov · Hack4Mobility CDMX

Dashboard de accesibilidad peatonal y ciclista en Tlalpan, Ciudad de México, con descripciones generadas por IA para personas con movilidad reducida.

Desarrollado para el hackathon **Hack4Mobility CDMX — IA para una movilidad universitaria inteligente y segura**.

---

## Equipo

| Nombre | Rol |
|--------|-----|
|        |     |
|        |     |
|        |     |

---

## Tecnologías

| Capa | Stack |
|------|-------|
| Backend | FastAPI · GeoPandas · Shapely · Uvicorn |
| IA | Groq API · `llama-3.1-8b-instant` |
| Frontend | React 18 · Vite · react-map-gl · Mapbox GL JS |
| Estilos | Tailwind CSS v3 |
| Análisis de datos | Python · GeoPandas · Pandas |

---

## Arquitectura

Monorepo con dos carpetas independientes:

```
hackKS/
├── back/               # API REST (FastAPI)
│   ├── main.py         # Endpoints + llamada a Groq
│   ├── analysis.py     # Procesamiento de shapefiles → GeoJSON
│   ├── requirements.txt
│   ├── .env.example
│   └── tlalpan_accesibilidad.geojson   # Generado por analysis.py
└── accesomov/          # Dashboard (React + Vite)
    └── src/
        ├── App.jsx
        └── components/
            ├── MapView.jsx       # Mapa Mapbox con polígonos
            ├── SidebarStats.jsx  # Estadísticas agregadas
            ├── ZonasRiesgo.jsx   # Lista colapsable de alto riesgo
            ├── ColoniaDetail.jsx # Panel con descripción IA
            └── Toast.jsx
```

El frontend consume la API en `http://localhost:8000`. No hay base de datos: los datos se cargan en memoria al iniciar el servidor desde el GeoJSON pre-procesado.

---

## Cómo correr el backend

```bash
cd back
pip install -r requirements.txt

# Copia el ejemplo y agrega tu key de Groq
cp .env.example .env
# Edita .env: GROQ_API_KEY=gsk_...

set -a && source .env && set +a
uvicorn main:app --reload --port 8000
```

La API queda disponible en `http://localhost:8000`.  
Documentación interactiva: `http://localhost:8000/docs`

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/colonias` | GeoJSON completo (179 colonias de Tlalpan) |
| GET | `/colonias/{cve_col}` | Detalle + descripción empática generada por IA |
| GET | `/zonas-riesgo` | 108 colonias con score ≥ 4, con centroides |
| GET | `/resumen` | Estadísticas agregadas |

---

## Cómo correr el frontend

```bash
cd accesomov
npm install
npm run dev
```

La app queda disponible en `http://localhost:5173`.  
Requiere que el backend esté corriendo en el puerto 8000.

---

## Datos utilizados

| Dataset | Fuente | Descripción |
|---------|--------|-------------|
| `esppub_ciclis_peat.shp` | Instituto de Planeación Democrática y Prospectiva (CDMX) | Infraestructura ciclista y accesibilidad peatonal por colonia |
| `Dist_acce_infra.shp` | Instituto de Planeación Democrática y Prospectiva (CDMX) | Nivel de presencia de infraestructura peatonal por colonia (Alta/Media/Baja/Nula) |

Ambos datasets cubren las 1,815 colonias de CDMX. El análisis filtra las **179 colonias de Tlalpan** y genera un score de accesibilidad del 1 al 5 combinando `INFRAPEAT` y `C_pEPICCAM`.

Los datos crudos (shapefiles) no se incluyen en este repositorio por su tamaño. Están disponibles en el Portal de Datos Abiertos de la CDMX.

---

## Consideraciones éticas

- **Anonimización**: todos los datos están agregados por colonia, nunca por individuo. No se procesa ni almacena información personal.
- **Sin recolección de datos de usuarios**: la aplicación no registra ubicaciones, identidades ni comportamiento de quienes la consultan.
- **Fuentes gubernamentales públicas**: los datasets provienen del Portal de Datos Abiertos de la CDMX bajo licencia de uso libre.
- **Sesgos identificados**: la cobertura de los datos es desigual — las zonas periféricas de Tlalpan (áreas rurales y pueblos originarios) tienen menor densidad de medición, lo que puede subestimar la problemática real en esas colonias. El score debe interpretarse como una aproximación, no como una verdad absoluta.
- **Uso de IA**: las descripciones generadas por `llama-3.1-8b-instant` son orientativas y pueden contener imprecisiones. No sustituyen un diagnóstico técnico de infraestructura urbana.
