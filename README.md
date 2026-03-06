# Visualización Centro de Información de Juventud

Tablero interactivo de indicadores de juventud para la Subdirección para la Juventud (SDIS Bogotá). Replica y complementa el tablero de Power BI del Centro de Información de Juventud.

**URL del tablero:** https://sdis-juventud.github.io/tablero-cij/

---

## Estructura del proyecto

```
├── index.html                 # Página principal (7 dimensiones)
├── dimension3.html            # Dimensión 3: Inclusión Productiva
├── actualizar_datos.py        # Script que procesa los datos del DANE
├── fuentes/                   # Aquí se suben los archivos Excel del DANE
│   └── LEER_PRIMERO.md
├── data/                      # JSONs generados automáticamente
│   ├── mercado_laboral.json
│   └── mercado_laboral_ciudades.json
├── .github/workflows/         # Automatización
│   └── actualizar_datos.yml
└── README.md
```

---

## Cómo actualizar los datos (para cualquier analista)

Solo hay que hacer 3 cosas: **descargar, copiar y subir**.

### Paso 1: Descargar el anexo del DANE

1. Ir a: https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/mercado-laboral-de-la-juventud
2. En "Anexos", descargar el archivo más reciente
   - Se llama algo como `anex-GEIHMLJ-oct-dic2025.xlsx`
   - El nombre indica el trimestre: `oct-dic2025` = octubre-diciembre 2025

### Paso 2: Copiar el archivo a la carpeta `fuentes/`

Copiar el archivo descargado a la carpeta `fuentes/` de este proyecto.

### Paso 3: Subir a GitHub

Desde la terminal (en la carpeta del proyecto):

```bash
git add fuentes/
git commit -m "Nuevo anexo DANE oct-dic 2025"
git push
```

**O desde GitHub.com directamente:**
1. Ir al repo → carpeta `fuentes/`
2. "Add file" → "Upload files"
3. Arrastrar el archivo Excel
4. Escribir mensaje de commit (ej: "Nuevo anexo DANE oct-dic 2025")
5. Click en "Commit changes"

### Qué pasa después

GitHub Actions automáticamente:
1. Detecta el nuevo archivo en `fuentes/`
2. Ejecuta `actualizar_datos.py`
3. Genera los JSONs actualizados en `data/`
4. Hace commit de los nuevos datos
5. GitHub Pages publica la versión actualizada

El tablero se actualiza solo en ~2 minutos.

---

## Dimensiones del tablero

| Dimensión | Estado | Página |
|-----------|--------|--------|
| 1. Ser joven | Próximamente | — |
| 2. Educación | Próximamente | — |
| **3. Inclusión Productiva** | **Activa** | `dimension3.html` |
| 4. Salud Integral y Autocuidado | Próximamente | — |
| 5. Cultura, Recreación y Deporte | Próximamente | — |
| 6. Paz, Convivencia y Justicia | Próximamente | — |
| 7. Hábitat | Próximamente | — |

---

## Dimensión 3: Inclusión Productiva

### Datos y fuentes

| Archivo | Fuente | Cobertura | Actualización |
|---------|--------|-----------|---------------|
| `mercado_laboral.json` | DANE, GEIH Mercado laboral juvenil | Bogotá D.C., 2014-presente | Trimestral |
| `mercado_laboral_ciudades.json` | DANE, GEIH Mercado laboral juvenil | 7 entidades, 2018-presente | Trimestral |

### Indicadores

- **TGP** — Tasa global de participación
- **TO** — Tasa de ocupación
- **TD** — Tasa de desocupación
- **PET** — Población en edad de trabajar (15-28 años)
- **Fuerza de trabajo** — Ocupados + Desocupados
- **Fuera de la fuerza de trabajo** — Población que no busca empleo

### Ciudades de comparación

Bogotá D.C., Medellín A.M., Cali A.M., Barranquilla A.M., Bucaramanga A.M., Total 13 ciudades, Total nacional.

### Notas metodológicas

**Total nacional:** excluye de la cobertura de los departamentos de la Amazonía y Orinoquía las cabeceras municipales que no son capitales de departamento, así como los centros poblados y rural disperso. También se excluye la población de Providencia y el centro poblado y rural disperso de San Andrés.

**13 ciudades y áreas metropolitanas:** Bogotá D.C., Medellín A.M., Cali A.M., Barranquilla A.M., Bucaramanga A.M., Manizales A.M., Pereira A.M., Cúcuta A.M., Pasto, Ibagué, Montería, Cartagena y Villavicencio.

---

## Notas técnicas (para quien mantenga el código)

### Sobre los trimestres

El DANE publica trimestres **móviles** (Ene-Mar, Feb-Abr, Mar-May...) y **fijos** (Ene-Mar, Abr-Jun, Jul-Sep, Oct-Dic). El tablero solo muestra los 4 trimestres fijos.

### Si el DANE cambia el formato del anexo Excel

1. Abrir el nuevo anexo en Excel
2. Buscar la hoja `23 ciudades trim móvil`
3. Encontrar la fila donde empieza la sección de Bogotá (buscar "Bogotá" o "% Población en edad de trabajar")
4. Actualizar la variable `CIUDADES_EXTRAER` en `actualizar_datos.py` con el nuevo número de fila

### Requisitos para correr localmente

- Python 3.8+ con `openpyxl` (`pip install openpyxl`)
- Para ver el tablero local: `python -m http.server 8080` → abrir http://localhost:8080

---

## Contacto

Subdirección para la Juventud – SDIS Bogotá
