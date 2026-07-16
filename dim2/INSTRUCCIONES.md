# Dimensión 2: Educación — instrucciones de actualización

## Datos que usa esta dimensión

| Sección | Indicador | Fuente | Archivo | Frecuencia |
|---------|-----------|--------|---------|------------|
| 2.1 Educación media | Cobertura, deserción, aprobación, reprobación y repitencia | MEN – Estadísticas en educación por departamento (datos.gov.co) | CSV en `fuentes/` | Anual |
| 2.2 Educación superior | Matrículas por nivel de formación (técnica, tecnológica, universitaria, posgrado) | MEN – Estadísticas de matrícula por municipio (datos.gov.co) | CSV en `fuentes/Educ superior/` | Anual |

---

## 2.1 Educación media

**Dataset:** [MEN_ESTADISTICAS_EN_EDUCACION_EN_PREESCOLAR-BÁSICA_Y_MEDIA_POR_DEPARTAMENTO](https://www.datos.gov.co/Educaci-n/MEN_ESTADISTICAS_EN_EDUCACION_EN_PREESCOLAR-B-SICA/ji8i-4anb/about_data)

**Nota:** Se filtra por Bogotá D.C. Los datos disponibles actualmente van de 2011 a 2024.

### Indicadores disponibles

- **Cobertura neta y bruta:** total, transición, primaria, secundaria, media
- **Deserción, aprobación, reprobación, repitencia:** total, transición, primaria, secundaria, media

### Cómo actualizar

1. Ir al dataset → **Exportar** → **CSV**
2. Pegar el archivo en `dim2/fuentes/` (no borrar el anterior)
3. Ejecutar:
   ```bash
   python dim2/actualizar.py
   ```
4. Subir a GitHub:
   ```bash
   git add dim2/fuentes/ dim2/data/
   git commit -m "Actualizar datos de educación media"
   git push
   ```

---

## 2.2 Educación superior

**Fuentes oficiales (MEN):**

- [SNIES – Resumen de indicadores de educación superior](https://snies.mineducacion.gov.co/portal/Informes-e-indicadores/Resumen-indicadores-Educacion-Superior/) — tasas de cobertura y de tránsito inmediato, Bogotá y Colombia.
- [HECAA – Tablero de matrícula](https://hecaa.mineducacion.gov.co/consultaspublicas/tableros/matricula) — matrículas por nivel de formación.

**Cómo funciona desde julio de 2026:** los datos se mantienen a mano en la
hoja `educacion_superior` de `dim2/datos_dim2.xlsx` (Carolina los toma de
las dos fuentes de arriba). Ya **no** se usa el CSV de datos.gov.co
(MEN_ESTADISTICAS-MATRICULA-POR-MUNICIPIOS, llegaba solo hasta 2021); el
script viejo `actualizar_educ_superior.py` queda solo como referencia.

### Indicadores

- **Matrículas por nivel:** técnica profesional, tecnológica, universitaria, especialización, maestría, doctorado
- **Total Bogotá vs. total Colombia** (con porcentaje de participación)
- **Tasas de cobertura y de tránsito inmediato**, Bogotá y Colombia
- **IES con oferta** en Bogotá

### Cómo actualizar

1. Consultar las dos fuentes del MEN y completar la hoja `educacion_superior` de `dim2/datos_dim2.xlsx` (los años sin dato se marcan "PENDIENTE")
2. Ejecutar:
   ```bash
   python dim2/actualizar_educ_superior_excel.py
   ```
3. Subir a GitHub:
   ```bash
   git add dim2/datos_dim2.xlsx dim2/data/
   git commit -m "Actualizar datos de educación superior"
   git push
   ```

---

## Verificar después de actualizar

- Ir a: https://sdis-juventud.github.io/tablero-cij/dim2/
- Revisar que las dos secciones (2.1 y 2.2) muestren datos correctos
- Verificar que el último año disponible aparezca en cada selector

## Qué hacer si el formato cambió

Si algún script falla porque el MEN cambió el formato del CSV:

1. Abrir el nuevo archivo en Excel o un editor de texto
2. Verificar que las columnas sigan teniendo los mismos nombres
3. Verificar que Bogotá aparezca (buscar "BOGOT" en el archivo)
4. Avisar a Carolina para ajustar el script

## Archivos de esta dimensión

```
dim2/
├── index.html                    ← Página web (secciones 2.1 y 2.2)
├── actualizar.py                 ← Script para educación media
├── actualizar_educ_superior.py   ← Script para educación superior
├── fuentes/                      ← CSVs de educación media
│   └── Educ superior/            ← CSVs de educación superior
├── data/                         ← JSONs generados automáticamente
│   ├── educacion_media.json
│   └── educacion_superior.json
└── INSTRUCCIONES.md              ← Este archivo
```
