# actualizar_fecundidad.py — Dimensión 4: Salud integral y autocuidado
# Genera fecundidad_adolescente.json desde el CSV del OSB SaludData.
#
# Fuente: osb_saludsr_fecundidad_10-19.csv (SaludData, Observatorio de Salud de Bogotá)
# Uso:    python dim4/actualizar_fecundidad.py

import os
import csv
import json

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
CSV_PATH    = os.path.join(SCRIPT_DIR, 'fuentes', 'natalidad', 'osb_saludsr_fecundidad_10-19.csv')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'data', 'fecundidad_adolescente.json')

FUENTE = 'SaludData – Observatorio de Salud de Bogotá. Corte: 30/04/2026. p: preliminar.'
NOTA   = ('Tasa = nacidos vivos por cada 1.000 mujeres del grupo de edad. '
          'Población: proyecciones DANE-FONDANE-SDP, CNPV 2018. '
          'Nota: Sumapaz presenta tasa elevada por el tamaño muy pequeño de la población.')

EXCLUIR = {'sin información', 'sin informacion', 'sin info'}


def a_float(s):
    if not s or not s.strip() or s.strip().startswith('#'):
        return None
    return float(s.strip().replace(',', '.'))


def a_int(s):
    if not s or not s.strip():
        return None
    try:
        return int(s.strip())
    except ValueError:
        return None


def col(row, *nombres):
    """Busca la primera columna que exista en el diccionario."""
    for n in nombres:
        if n in row:
            return row[n]
    return ''


def main():
    print('=' * 60)
    print('Fecundidad adolescente — actualización')
    print('=' * 60)

    bogota_por_anio = []
    localidades_ultimo_anio = {}
    ultimo_anio_str = None

    with open(CSV_PATH, encoding='latin-1') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            # Año: el encabezado puede venir con o sin tilde según la codificación
            anio_raw = col(row, 'Año', 'A\xf1o', 'Ano', 'AÑO').strip()
            localidad = col(row, 'LOCALIDAD_NOMBRE').strip()

            if not anio_raw or not localidad:
                continue
            if localidad.lower() in EXCLUIR:
                continue

            nv_10_14   = a_int(col(row, 'conteo_10_14'))
            tasa_10_14 = a_float(col(row, 'Tasa10-14'))
            pob_10_14  = a_int(col(row, 'POBLACION_MUJERES_10_14'))
            nv_15_19   = a_int(col(row, 'conteo_15_19'))
            tasa_15_19 = a_float(col(row, 'Tasa15-19'))
            pob_15_19  = a_int(col(row, 'POBLACION_MUJERES_15_19'))

            es_bogota = localidad.lower().startswith('bogot')

            if es_bogota:
                bogota_por_anio.append({
                    'anio':      anio_raw,
                    'nv_10_14':  nv_10_14  or 0,
                    'pob_10_14': pob_10_14 or 0,
                    'tasa_10_14': tasa_10_14,
                    'nv_15_19':  nv_15_19  or 0,
                    'pob_15_19': pob_15_19 or 0,
                    'tasa_15_19': tasa_15_19,
                })
                ultimo_anio_str = anio_raw
            else:
                if anio_raw not in localidades_ultimo_anio:
                    localidades_ultimo_anio[anio_raw] = {}
                localidades_ultimo_anio[anio_raw][localidad] = {
                    'localidad':  localidad,
                    'nv_10_14':   nv_10_14  or 0,
                    'tasa_10_14': tasa_10_14 or 0.0,
                    'nv_15_19':   nv_15_19  or 0,
                    'tasa_15_19': tasa_15_19 or 0.0,
                }

    if not bogota_por_anio:
        print('ERROR: No se encontraron filas de Bogotá en el CSV')
        return

    # Por localidad: último año disponible, ordenado por tasa 15-19 desc
    anio_loc = sorted(localidades_ultimo_anio.keys())[-1]
    por_localidad = list(localidades_ultimo_anio[anio_loc].values())
    por_localidad.sort(key=lambda x: x.get('tasa_15_19') or 0, reverse=True)

    resultado = {
        'por_anio':      bogota_por_anio,
        'por_localidad': por_localidad,
        'ultimo_anio':   ultimo_anio_str or anio_loc,
        'fuente':        FUENTE,
        'nota':          NOTA,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f'Años Bogotá: {[r["anio"] for r in bogota_por_anio]}')
    print(f'Año localidades: {anio_loc} ({len(por_localidad)} localidades)')
    ult = bogota_por_anio[-1]
    print(f'Último año: {ult["anio"]} — 10-14: {ult["nv_10_14"]} NV ({ult["tasa_10_14"]} ‰) | '
          f'15-19: {ult["nv_15_19"]} NV ({ult["tasa_15_19"]} ‰)')
    print(f'\nArchivo: {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
