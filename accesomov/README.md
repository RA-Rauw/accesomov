# AccesoMov — Hack4Mobility CDMX

Dashboard de accesibilidad peatonal y ciclista para las 179 colonias de Tlalpan, CDMX.
Construido para el hackathon Hack4Mobility CDMX.

## Stack

- React 18 + Vite
- react-map-gl v7 + Mapbox GL JS v2
- Tailwind CSS v3
- FastAPI (backend en `/back`)

## Instalación

```bash
cd accesomov
npm install
```

## Correr en desarrollo

Primero asegúrate de que el backend esté corriendo en `http://localhost:8000`:

```bash
# Terminal 1 — backend
cd back
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn main:app --reload --port 8000

# Terminal 2 — frontend
cd accesomov
npm run dev
```

La app queda disponible en http://localhost:5173

## Build de producción

```bash
npm run build
npm run preview
```

## Funcionalidades

| Feature | Descripción |
|---|---|
| Mapa coropléticо | 179 colonias coloreadas por score de accesibilidad (verde→rojo) |
| Panel de stats | Score promedio, distribución por nivel, colonia con peor situación |
| Click en colonia | Detalle + descripción empática generada por IA (Claude) |
| Zonas de riesgo | Lista colapsable de 108 colonias con score ≥ 4, con flyTo al mapa |
| Loading skeletons | Placeholder animado mientras carga cada sección |
| Toast de error | Aviso si el backend no responde |

## Estructura

```
accesomov/
├── src/
│   ├── App.jsx               # Estado global, fetching, layout
│   ├── components/
│   │   ├── MapView.jsx       # Mapa Mapbox con capas GeoJSON
│   │   ├── SidebarStats.jsx  # Panel de estadísticas (izquierda)
│   │   ├── ZonasRiesgo.jsx   # Lista colapsable de alto riesgo
│   │   ├── ColoniaDetail.jsx # Panel inferior con descripción IA
│   │   └── Toast.jsx         # Notificaciones de error
│   ├── index.css
│   └── main.jsx
├── index.html
├── package.json
├── tailwind.config.js
└── vite.config.js
```

## Datos

Los datos provienen de dos datasets abiertos de CDMX procesados con GeoPandas:
- `esppub_ciclis_peat` — infraestructura ciclista y accesibilidad peatonal por colonia
- `Dist_acce_infra` — nivel de infraestructura peatonal (Alta/Media/Baja/Nula)

Score de accesibilidad = promedio(INFRAPEAT_numérico, C_pEPICCAM), escala 1-5 donde 5 = mayor problemática.
