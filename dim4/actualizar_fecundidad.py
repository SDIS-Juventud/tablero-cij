# actualizar_fecundidad.py — Dimensión 4: Salud integral y autocuidado
# Genera fecundidad_adolescente.json desde el CSV del OSB SaludData.
#
# Fuente principal: tasa-de-fecundidad-por-areas.csv (SaludData, OSB)
#   Columnas: ANIO, Localidad, POBLACION_15_49, GRUPO_EDAD, Nacidos vivos, Tasa
#   Codificación: UTF-8-BOM; delimitador: coma
# Uso: python dim4/actualizar_fecundidad.py

import os
import csv
import json
from collections import defaultdict

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
FUENTES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR),
                           'tablero-cij-compartido', 'dim4', 'fuentes', 'natalidad')
CSV_PATH    = os.path.join(FUENTES_DIR, 'tasa-de-fecundidad-por-areas.csv')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'data', 'fecundidad_adolescente.json')

FUENTE = ('SaludData – Observatorio de Salud de Bogotá. '
          'Actualización fuente: 11/06/2026. p: preliminar.')
NOTA   = ('Tasa específica de fecundidad = nacidos vivos de madres del grupo de edad '
          'por cada 1.000 mujeres del mismo grupo. '
          'Numerador: DANE–RUAF–ND (SDS), series finales 2014–2023, 2024 preliminar. '
          'Denominador: proyecciones DANE-FONDANE-SDP, CNPV 2018.')

GRUPOS_OBJETIVO = {'10-14', '15-19', '20-24', '25-29'}
EXCLUIR         = {'sin información', 'sin informacion', 'sin info'}


def a_float(s):
    if not s or not s.strip():
        return None
    return round(float(s.strip().replace(',', '.')), 2)


def a_int(s):
    if not s or not s.strip():
        return 0
    try:
        return int(float(s.strip()))
    except ValueError:
        return 0


def llave_grupo(grupo):
    """Convierte '10-14' → 'tasa_10_14' y 'nv_10_14'."""
    return grupo.replace('-', '_')


def main():
    print('=' * 60)
    print('Fecundidad — actualización (4 grupos: 10-14 a 25-29)')
    print('=' * 60)

    # datos[anio][localidad][grupo] = {'nv': int, 'tasa': float}
    datos = defaultdict(lambda: defaultdict(dict))

    with open(CSV_PATH, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                anio = int(row['ANIO'])
            except (ValueError, KeyError):
                continue
            if anio >= 2026:
                continue

            localidad = row.get('Localidad', '').strip()
            if not localidad or localidad.lower() in EXCLUIR:
                continue

            grupo = row.get('GRUPO_EDAD', '').strip()
            if grupo not in GRUPOS_OBJETIVO:
                continue

            nv   = a_int(row.get('Nacidos vivos', ''))
            tasa = a_float(row.get('Tasa', ''))

            datos[anio][localidad][grupo] = {'nv': nv, 'tasa': tasa}

    if not datos:
        print('ERROR: No se encontraron datos en el CSV')
        return

    # Detectar nombre de Bogotá (total ciudad)
    anios_ordenados = sorted(datos.keys())
    primer_anio = anios_ordenados[0]
    bogota_nombre = next(
        (loc for loc in datos[primer_anio] if loc.lower().startswith('bogot')), None
    )
    if not bogota_nombre:
        print('ERROR: No se encontró fila de Bogotá total en el CSV')
        return
    print(f'Bogotá detectada como: "{bogota_nombre}"')

    # Construir por_anio (Bogotá, todos los años)
    por_anio = []
    for anio in anios_ordenados:
        loc_data = datos[anio].get(bogota_nombre, {})
        anio_str = f'{anio}p' if anio >= 2024 else str(anio)
        fila = {'anio': anio_str}
        for grupo in ['10-14', '15-19', '20-24', '25-29']:
            g = loc_data.get(grupo, {})
            clave = llave_grupo(grupo)
            fila[f'nv_{clave}']   = g.get('nv', 0)
            fila[f'tasa_{clave}'] = g.get('tasa')
        por_anio.append(fila)

    # Construir por_localidad (último año, todas las localidades excepto Bogotá total)
    ultimo_anio = anios_ordenados[-1]
    ultimo_anio_str = f'{ultimo_anio}p' if ultimo_anio >= 2024 else str(ultimo_anio)

    por_localidad = []
    for localidad, grupos in datos[ultimo_anio].items():
        if localidad.lower().startswith('bogot'):
            continue
        fila = {'localidad': localidad}
        for grupo in ['10-14', '15-19', '20-24', '25-29']:
            g = grupos.get(grupo, {})
            clave = llave_grupo(grupo)
            fila[f'nv_{clave}']   = g.get('nv', 0)
            fila[f'tasa_{clave}'] = g.get('tasa') or 0.0
        por_localidad.append(fila)

    por_localidad.sort(key=lambda x: x.get('tasa_15_19') or 0, reverse=True)

    resultado = {
        'por_anio':      por_anio,
        'por_localidad': por_localidad,
        'ultimo_anio':   ultimo_anio_str,
        'fuente':        FUENTE,
        'nota':          NOTA,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f'Años incluidos: {[r["anio"] for r in por_anio]}')
    print(f'Localidades: {len(por_localidad)}')
    ult = por_anio[-1]
    print(
        f'Último año: {ult["anio"]} — '
        f'10-14: {ult["nv_10_14"]} NV ({ult["tasa_10_14"]} ‰) | '
        f'15-19: {ult["nv_15_19"]} NV ({ult["tasa_15_19"]} ‰) | '
        f'20-24: {ult["nv_20_24"]} NV ({ult["tasa_20_24"]} ‰) | '
        f'25-29: {ult["nv_25_29"]} NV ({ult["tasa_25_29"]} ‰)'
    )
    print(f'\nArchivo: {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
