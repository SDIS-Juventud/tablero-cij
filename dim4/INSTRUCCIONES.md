# Dimensión 4: Salud integral y autocuidado — instrucciones de actualización

## Datos que usa esta dimensión

| Sección | Indicador | Fuente | Carpeta fuentes | Frecuencia |
|---------|-----------|--------|-----------------|------------|
| 4.1 SGSSS | Afiliación por régimen | Pendiente — datos no disponibles aún | – | – |
| 4.2 Discapacidad | Jóvenes con discapacidad certificada por tipo | OSB – SaludData | `fuentes/discapacidad/` | Por definir |
| 4.3 Natalidad | Tasa de natalidad por cada mil en jóvenes | OSB – SaludData + DANE proyecciones | `fuentes/natalidad/` | Anual |

---

## 4.2 Discapacidad

**Fuente:** Observatorio de Salud de Bogotá – SaludData (Discapacidad certificada)

**Nota:** Los datos no tienen columna de año. Es un corte único (acumulado). Se filtra por Grupo de Edad = Juventud + Adolescencia como proxy de 14-28 años.

### Cómo actualizar

1. Descargar el CSV actualizado de SaludData
2. Guardarlo en `dim4/fuentes/discapacidad/` (no borrar el anterior)
3. Ejecutar:
   ```bash
   python dim4/actualizar_discapacidad.py
   ```
4. Subir a GitHub:
   ```bash
   git add dim4/fuentes/ dim4/data/
   git commit -m "Actualizar datos de discapacidad"
   git push
   ```

### Nota sobre los datos

- El CSV usa separador `;` y codificación latin-1
- Las categorías de discapacidad NO son mutuamente excluyentes (una persona puede tener más de un tipo)
- El total de jóvenes es el número de personas, no la suma de categorías

---

## 4.3 Natalidad

**Fuente nacimientos:** Observatorio de Salud de Bogotá – SaludData (Natalidad)
**Fuente población:** DANE – Proyecciones CNPV 2018 por localidad y grupo quinquenal

**Nota:** La tasa se calcula como: nacidos vivos de madres 15-28 / mujeres 15-29 × 1.000. Se usa el grupo quinquenal 25-29 del DANE como proxy del rango 25-28 de la política.

### Cómo actualizar

1. Descargar el CSV de natalidad actualizado de SaludData
2. Guardarlo en `dim4/fuentes/natalidad/` (no borrar el anterior)
3. El Excel de proyecciones DANE ya debe estar en la misma carpeta
4. Ejecutar:
   ```bash
   python dim4/actualizar_natalidad.py
   ```
5. Subir a GitHub:
   ```bash
   git add dim4/fuentes/ dim4/data/
   git commit -m "Actualizar datos de natalidad"
   git push
   ```

### Notas sobre los datos

- El CSV usa separador `;` y codificación UTF-8 con BOM
- La primera columna tiene un carácter BOM invisible (el script lo maneja con `utf-8-sig`)
- Hay filas para "00 - Bogotá" (total agregado) y para cada localidad individual. El script usa solo las localidades individuales para evitar doble conteo
- Datos disponibles: 2009-2024, pero se filtran desde 2018 (corte de la política)

### Dependencia

El script de natalidad requiere `openpyxl` para leer el Excel de proyecciones:
```bash
pip install openpyxl
```

---

## Verificar después de actualizar

- Ir a: https://sdis-juventud.github.io/tablero-cij/dim4/
- Revisar que las dos secciones (4.2 y 4.3) muestren datos correctos
- Verificar que las tasas de natalidad sean coherentes (tendencia a la baja)

## Archivos de esta dimensión

```
dim4/
├── index.html                    ← Página web (secciones 4.1, 4.2 y 4.3)
├── actualizar_discapacidad.py    ← Script para discapacidad
├── actualizar_natalidad.py       ← Script para natalidad
├── fuentes/
│   ├── discapacidad/             ← CSV del OSB + PDF de referencia
│   ├── natalidad/                ← CSV del OSB + Excel proyecciones DANE
│   └── localidades/              ← Shapefiles (para uso futuro con mapas)
├── data/                         ← JSONs generados automáticamente
│   ├── discapacidad.json
│   └── natalidad.json
└── INSTRUCCIONES.md              ← Este archivo
```
