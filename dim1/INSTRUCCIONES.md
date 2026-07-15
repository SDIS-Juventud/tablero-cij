# Dimensión 1: Ser joven — instrucciones de actualización

## Datos que usa esta dimensión

| Indicador | Fuente | Frecuencia |
|-----------|--------|------------|
| Población joven (14-28) por localidad, zona, edad y sexo | SDP - DANE (convenio de desagregación post-COVID, base CNPV 2018) | Cuando la SDP publique una nueva actualización |

**Por qué la SDP y no el DANE:** el DANE es la fuente oficial de las
proyecciones de población, pero su página de Bogotá no se ha actualizado.
La SDP, mediante su convenio con el DANE, sí publica las actualizaciones
post-COVID desagregadas por localidad. Por eso desde julio de 2026 esta
dimensión se alimenta de la página de la SDP.

## Cómo funciona (dos pasos)

La SDP cambia el nombre del archivo en cada actualización (el prefijo de
fecha `202503_`, `202511_`, etc.). Para que eso no rompa nada, el flujo
tiene un intermedio con nombre fijo:

```
Archivo de la SDP                    Fuente estándar                 Tablero web
(nombre cambia cada vez)             (nombre fijo)
fuentes/SDP-Dane/*.xlsx  ──paso 2──> fuentes/                ──paso 3──> data/*.json
                                     fuente_dim1_poblacion.xlsx
```

- `generar_fuente.py` toma el archivo más reciente de `fuentes/SDP-Dane/`
  y regenera la **fuente estándar** `fuentes/fuente_dim1_poblacion.xlsx`.
- `actualizar.py` lee solo la fuente estándar y regenera los JSON del tablero.

La fuente estándar trae una hoja `Ficha` que documenta de qué archivo se
generó y cómo actualizarla — quien abra el Excel se orienta sin leer nada más.

## Cómo actualizar (cuando la SDP publique algo nuevo)

### 1. Descargar el archivo nuevo de la SDP

- Ir a: https://sdp.gov.co/gestion-estudios-estrategicos/informacion-estadisticas/censo-2018-post-covid-19/proyecciones-de-poblacion
- En la sección de descargas, bajar **"Proyecciones y retroproyecciones de
  población 2005 a 2035 (Localidad)"**.
- Guardarlo en `dim1/fuentes/SDP-Dane/`. **No borrar el anterior** y no
  importa el nombre que traiga: el script busca el más reciente.

### 2. Regenerar la fuente estándar

```bash
python dim1/generar_fuente.py
```

El script valida el archivo (20 localidades, serie de años sin huecos,
totales que cuadran). Si algo no cuadra, se detiene y dice qué revisar.

### 3. Regenerar los JSON del tablero

```bash
python dim1/actualizar.py
```

Revisar la verificación que imprime (jóvenes 14-28, % de la población,
zonas) contra el boletín de la SDP si hay dudas.

Este paso también reescribe los datos embebidos dentro de `index.html`
(el respaldo que usa la página cuando se abre el archivo local sin
servidor), para que nunca queden con cifras viejas.

### 4. Subir a GitHub

```bash
git add dim1/fuentes/ dim1/data/ dim1/index.html
git commit -m "actualización proyecciones SDP"
git push
```

### 5. Verificar

- Ir a: https://sdis-juventud.github.io/tablero-cij/dim1/
- Revisar que los datos se vean bien.

### 6. Cuadrar contra SaluData (regla del equipo)

El tablero debe dar lo mismo que SaluData, que consume la misma serie del
convenio SDP-DANE:

- Ir al tablero de población de SaluData (Observatorio de Salud de Bogotá).
- Poner el **mismo año** y el filtro de **edad en 14 a 28** (SaluData suele
  estar en otro rango; si no se ajusta, no va a cuadrar).
- Comparar total, hombres y mujeres contra los KPI del tablero CIJ.
  Deben ser idénticos.
- Si no cuadran, lo más probable es que uno de los dos esté en un corte
  distinto: comparar la "Fecha de actualización" de SaluData con la fecha
  del archivo en `fuentes/SDP-Dane/`. Si SaluData va adelante, descargar el
  corte nuevo de la SDP y repetir desde el paso 1; si vamos adelante
  nosotros, dejarlo anotado y avisar a Carolina.

## Qué hacer si el formato cambió

La SDP cambia detalles del formato en cada corte. El script ya tolera las
variantes conocidas:

- **Corte 2025-03:** encabezados en la fila 5, columna `Área`,
  edades como `Total_14`.
- **Corte 2025-12 (ajuste DANE agosto 2025):** encabezados en la fila 6,
  columna `Área Geográfica`, edades como `Total 14 años`, fila de pie de
  página al final.

El script encuentra solo la fila de encabezados y reconoce esas variantes.
Si aun así `generar_fuente.py` falla, es porque llegó una variante nueva:

1. Abrir el archivo nuevo en Excel.
2. Comparar contra el anterior: ¿qué columna cambió de nombre o de lugar?
3. Avisar a Carolina para ajustar `generar_fuente.py` (solo ese script:
   `actualizar.py` no se toca porque lee la fuente estándar).

El script también valida los datos (20 localidades, años sin huecos,
totales que cuadran) y se detiene con un mensaje claro si algo no cuadra —
nunca corrige en silencio.

## Archivos de esta dimensión

```
dim1/
├── index.html                       ← Página web de la dimensión
├── generar_fuente.py                ← Paso 1: archivo SDP → fuente estándar
├── actualizar.py                    ← Paso 2: fuente estándar → JSONs
├── INSTRUCCIONES.md                 ← Este archivo
├── fuentes/
│   ├── fuente_dim1_poblacion.xlsx   ← FUENTE ESTÁNDAR de la dimensión
│   ├── SDP-Dane/                    ← Archivos tal como los publica la SDP
│   │   ├── 2025xx_localidad_proyeccion_retroproyeccion_poblacion_...xlsx  ← el que se usa
│   │   ├── ...upl / hogares y viviendas (referencia, no se usan aún)
│   │   ├── documento_metodologico_proyecciones_pob.pdf
│   │   └── OSB_Demografia-Poblacion-1.pdf
│   └── Dane/
│       └── localidades/             ← Shapefile de localidades (fuente del mapa, no cambia)
└── data/                            ← JSONs generados automáticamente
    ├── resumen_bogota.json
    ├── localidades.json
    └── localidades_geo.json         ← Geometrías del mapa (no se regenera)
```
