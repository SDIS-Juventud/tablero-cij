# Visualización Centro de Información de Juventud

Tablero interactivo de indicadores de juventud para la Subdirección para la Juventud (SDIS Bogotá). Replica y complementa el tablero de Power BI del Centro de Información de Juventud.

**URL del tablero:** https://sdis-juventud.github.io/tablero-cij/

---

## Estructura del proyecto

```
tablero-cij/
├── index.html                          # Página principal (7 dimensiones)
├── guia.html                           # Guía de navegación
├── img/                                # Imágenes e iconos
├── dim1/                               # Dimensión 1: Ser joven
│   ├── fuentes/
│   └── data/
├── dim2/                               # Dimensión 2: Educación
├── dim3/                               # Dimensión 3: Inclusión Productiva ✔
│   ├── index.html                      #   Página de la dimensión
│   ├── actualizar.py                   #   Script de procesamiento
│   ├── fuentes/                        #   Excel del DANE
│   ├── data/                           #   JSONs generados
│   └── INSTRUCCIONES.md                #   Cómo actualizar esta dimensión
├── dim4/                               # Dimensión 4: Salud Integral y Autocuidado
├── dim5/                               # Dimensión 5: Cultura, Recreación y Deporte
├── dim6/                               # Dimensión 6: Paz, Convivencia y Justicia
├── dim7/                               # Dimensión 7: Hábitat
├── .github/workflows/                  # Automatización (GitHub Actions)
│   └── actualizar_datos.yml
└── README.md
```

Cada dimensión es una carpeta autocontenida (`dim1/` a `dim7/`). Las instrucciones de actualización están dentro de cada una.

---

## Dimensiones del tablero

| Dimensión | Estado | Carpeta | Instrucciones |
|-----------|--------|---------|---------------|
| 1. Ser joven | Próximamente | `dim1/` | — |
| 2. Educación | Próximamente | `dim2/` | — |
| 4. Salud Integral y Autocuidado | Próximamente | `dim4/` | — |
| **3. Inclusión Productiva** | **Activa** | `dim3/` |  |
| 4. Salud Integral y Autocuidado | Próximamente | `dim4/` | — |
| 5. Cultura, Recreación y Deporte | Próximamente | `dim5/` | — |
| 6. Paz, Convivencia y Justicia | Próximamente | — | — |
| 7. Hábitat | Próximamente | `dim7/` | — |

---

## Cómo actualizar datos

Cada dimensión tiene sus propias fuentes y su propio script. Las instrucciones específicas están en `dimX/INSTRUCCIONES.md`.

**Flujo general:**

1. Descargar los datos de la fuente oficial
2. Copiar el archivo a `dimX/fuentes/`
3. Subir a GitHub (push o por la web)
4. GitHub Actions procesa automáticamente y publica (~2 min)

---

