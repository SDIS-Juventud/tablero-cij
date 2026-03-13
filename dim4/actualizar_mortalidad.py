# actualizar_mortalidad.py — Dimensión 4: Salud integral y autocuidado
# Script para procesar el CSV de mortalidad del OSB y generar
# el JSON de causas de muerte en jóvenes (15-29 años).
# Calcula tasa de mortalidad por cada 100.000 usando proyecciones DANE.
#
# Uso:
#   1. Descargar CSV de mortalidad de SaludData / OSB
#   2. Guardar en dim4/fuentes/mortalidad/
#   3. Correr: python dim4/actualizar_mortalidad.py
#
# Dependencia: openpyxl (pip install openpyxl)

import os
import csv
import json
import unicodedata
import openpyxl

# ============================================================
# Configuración
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FUENTES_DIR = os.path.join(SCRIPT_DIR, 'fuentes', 'mortalidad')
NATALIDAD_DIR = os.path.join(SCRIPT_DIR, 'fuentes', 'natalidad')
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')

# Grupos de edad de jóvenes
GRUPOS_JUVENTUD = {'15 a 19', '20 a 24', '25 a 29'}

# Solo datos desde 2018 (corte de la política)
ANIO_MIN = 2018


def normalizar(nombre):
    """Quita tildes y pasa a minúsculas para comparar nombres de localidad."""
    s = unicodedata.normalize('NFD', nombre)
    return s.encode('ascii', 'ignore').decode().lower().strip()


# ============================================================
# Funciones — Población (Excel DANE)
# ============================================================

def encontrar_excel(carpeta):
    """Busca el Excel de proyecciones de población."""
    for f in os.listdir(carpeta):
        if f.endswith('.xlsx') and 'proyecciones' in f.lower() and not f.startswith('~$'):
            return os.path.join(carpeta, f)
    return None


def cargar_poblacion(ruta_excel):
    """
    Lee el Excel de proyecciones DANE y extrae población total de jóvenes
    (15-29 años, hombres + mujeres) por localidad y año.
    Retorna: dict[anio][localidad_normalizada] = población total 15-29
    """
    wb = openpyxl.load_workbook(ruta_excel, data_only=True)
    ws = wb['Localidades_edad_quinquenal']

    # Encontrar fila de encabezados
    headers = None
    header_row = None
    for i, row in enumerate(ws.iter_rows(min_row=1, max_row=20, values_only=False), 1):
        vals = [cell.value for cell in row]
        if 'COD_LOC' in vals:
            headers = vals
            header_row = i
            break

    if not headers:
        print('ERROR: No se encontró encabezado en el Excel')
        return {}, {}

    # Índices de columnas Total_15-19, Total_20-24, Total_25-29
    col_indices = {}
    for idx, h in enumerate(headers):
        if h and isinstance(h, str):
            if h == 'Total_15-19':
                col_indices['15-19'] = idx
            elif h == 'Total_20-24':
                col_indices['20-24'] = idx
            elif h == 'Total_25-29':
                col_indices['25-29'] = idx

    # dict[anio][nombre_normalizado] = población total 15-29
    poblacion = {}
    # dict para nombre original
    nombres_loc = {}

    for row in ws.iter_rows(min_row=header_row + 1, values_only=True):
        area = row[2]  # AREA
        if area != 'Total':
            continue

        anio = row[3]  # AÑO
        if not isinstance(anio, (int, float)) or int(anio) < ANIO_MIN:
            continue
        anio = int(anio)

        localidad = str(row[1] or '').strip()  # NOM_LOC
        if not localidad:
            continue

        t15 = row[col_indices.get('15-19', 0)] or 0
        t20 = row[col_indices.get('20-24', 0)] or 0
        t25 = row[col_indices.get('25-29', 0)] or 0
        total = int(t15) + int(t20) + int(t25)

        if anio not in poblacion:
            poblacion[anio] = {}
        loc_norm = normalizar(localidad)
        poblacion[anio][loc_norm] = total
        nombres_loc[loc_norm] = localidad

    # Total Bogotá por año
    for anio in poblacion:
        poblacion[anio]['bogota'] = sum(poblacion[anio].values())

    wb.close()
    return poblacion, nombres_loc


# ============================================================
# Funciones — Mortalidad (CSV OSB)
# ============================================================

def encontrar_csv(carpeta):
    """Busca el CSV principal de mortalidad (no el de metadatos)."""
    archivos = [f for f in os.listdir(carpeta)
                if f.endswith('.csv') and 'metadato' not in f.lower()
                and not f.startswith('~$')]
    if not archivos:
        return None
    archivos.sort()
    return os.path.join(carpeta, archivos[-1])


def procesar(ruta_csv):
    """Lee el CSV y extrae datos de mortalidad de jóvenes."""
    por_anio = {}

    with open(ruta_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            edad_q = row.get('EDAD_QUINQUENAL', '').strip()
            if edad_q not in GRUPOS_JUVENTUD:
                continue

            try:
                anio = int(row.get('ANO', '0'))
                casos = int(row.get('TOTAL_CASOS', '0'))
            except (ValueError, TypeError):
                continue

            if anio < ANIO_MIN:
                continue

            sexo = row.get('SEXO', '').strip()
            causa = row.get('CAUSAS_667', '').strip()
            localidad = row.get('LOCALIDAD', '').strip()

            if anio not in por_anio:
                por_anio[anio] = {
                    'total': 0,
                    'hombres': 0,
                    'mujeres': 0,
                    'causas': {},
                    'localidades': {},
                }

            a = por_anio[anio]
            a['total'] += casos

            if sexo == 'Hombres':
                a['hombres'] += casos
            elif sexo == 'Mujeres':
                a['mujeres'] += casos

            if causa:
                a['causas'][causa] = a['causas'].get(causa, 0) + casos

            if localidad and localidad != 'Sin Dato':
                a['localidades'][localidad] = a['localidades'].get(localidad, 0) + casos

    return por_anio


def generar_json(por_anio, poblacion):
    """Genera el JSON de mortalidad con tasa por cada 100.000."""
    os.makedirs(DATA_DIR, exist_ok=True)

    anios = sorted(por_anio.keys())
    registros = []

    for anio in anios:
        a = por_anio[anio]

        # Tasa total Bogotá
        pob_bog = poblacion.get(anio, {}).get('bogota', 0)
        tasa_total = round(a['total'] / pob_bog * 100000, 1) if pob_bog > 0 else None

        # Top 10 causas
        causas_sorted = sorted(a['causas'].items(), key=lambda x: x[1], reverse=True)
        top_causas = [{'causa': c, 'casos': n} for c, n in causas_sorted[:10]]

        # Localidades con tasa
        pob_anio = poblacion.get(anio, {})
        locs_con_tasa = []
        for loc, casos in a['localidades'].items():
            loc_norm = normalizar(loc)
            pob_loc = pob_anio.get(loc_norm, 0)
            tasa = round(casos / pob_loc * 100000, 1) if pob_loc > 0 else None
            locs_con_tasa.append({
                'localidad': loc,
                'casos': casos,
                'tasa_100k': tasa,
            })
        locs_con_tasa.sort(key=lambda x: x.get('tasa_100k') or 0, reverse=True)

        registros.append({
            'anio': anio,
            'total': a['total'],
            'hombres': a['hombres'],
            'mujeres': a['mujeres'],
            'tasa_100k': tasa_total,
            'top_causas': top_causas,
            'por_localidad': locs_con_tasa,
        })

    resultado = {
        'por_anio': registros,
        'nota': 'Defunciones de jóvenes 15-29 años residentes en Bogotá. Tasa por cada 100.000 jóvenes. Fuente: DANE-RUAF-ND / OSB SaludData.',
    }

    ruta = os.path.join(DATA_DIR, 'mortalidad.json')
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    print(f'  mortalidad.json generado')
    return ruta


def main():
    print('=' * 60)
    print('Actualización — Dimensión 4: Mortalidad')
    print('=' * 60)

    # 1. Cargar población del Excel DANE (en carpeta de natalidad)
    excel = encontrar_excel(NATALIDAD_DIR)
    if not excel:
        print('AVISO: No se encontró Excel de proyecciones — no se calcularán tasas')
        poblacion = {}
    else:
        print(f'  Proyecciones: {os.path.basename(excel)}')
        poblacion, _ = cargar_poblacion(excel)
        print(f'  Años de población: {sorted(poblacion.keys())}')

    # 2. Procesar CSV mortalidad
    archivo = encontrar_csv(FUENTES_DIR)
    if not archivo:
        print('ERROR: No se encontró CSV de mortalidad')
        return
    print(f'  Archivo: {os.path.basename(archivo)}')

    print('\nProcesando...')
    por_anio = procesar(archivo)
    print(f'  Años: {sorted(por_anio.keys())}')

    print('\nGenerando JSON...')
    ruta = generar_json(por_anio, poblacion)

    # Verificación
    with open(ruta, 'r', encoding='utf-8') as f:
        datos = json.load(f)

    print(f'\n{"=" * 60}')
    print('VERIFICACIÓN:')
    print(f'{"=" * 60}')
    for r in datos['por_anio']:
        tasa = f'{r["tasa_100k"]}' if r.get('tasa_100k') else 'N/D'
        print(f'  {r["anio"]}: {r["total"]:,} muertes (H:{r["hombres"]:,} M:{r["mujeres"]:,}) — tasa {tasa}/100k'.replace(',', '.'))
        if r['top_causas']:
            print(f'    #1: {r["top_causas"][0]["causa"]} ({r["top_causas"][0]["casos"]})')

    # Verificar tasa por localidad del último año
    ultimo = datos['por_anio'][-1]
    print(f'\nTasa por localidad ({ultimo["anio"]}):')
    for loc in ultimo['por_localidad'][:5]:
        tasa = loc.get('tasa_100k', 'N/D')
        print(f'  {loc["localidad"]}: {tasa}/100k ({loc["casos"]} muertes)')

    print(f'\nArchivo: {ruta}')


if __name__ == '__main__':
    main()
