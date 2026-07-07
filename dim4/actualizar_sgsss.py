# actualizar_sgsss.py — Dimensión 4: Salud integral y autocuidado
# Lee la pestaña "1 SGSSS" de dim4/datos_dim4.xlsx y genera el JSON
# de afiliación al Sistema General de Seguridad Social en Salud (SGSSS).
#
# Uso:
#   1. Actualizar la pestaña "1 SGSSS" del Excel con el nuevo corte
#      (agregar filas nuevas, sin borrar los cortes anteriores)
#   2. Correr: python dim4/actualizar_sgsss.py

import os
import json
import openpyxl

# ============================================================
# Configuración
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(SCRIPT_DIR, 'datos_dim4.xlsx')
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')

MESES = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO',
         'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

# Orden de despliegue de los regímenes en el gráfico (mayor a menor típico)
ORDEN_REGIMEN = ['CONTRIBUTIVO', 'SUBSIDIADO', 'EXCEPCION', 'INPEC INTRAMURAL']
ORDEN_QUINQUENIO = ['15-19', '20-24', '25-29']


def clave_corte(corte):
    """Convierte 'MAYO-2026' en (2026, 5) para poder ordenar cronológicamente."""
    mes, anio = corte.split('-')
    return (int(anio), MESES.index(mes.upper()) + 1)


def es_fila_de_corte(valor):
    """Una fila de datos válida empieza con un corte tipo 'MAYO-2026'."""
    if not isinstance(valor, str) or '-' not in valor:
        return False
    _, anio = valor.rsplit('-', 1)
    return anio.strip().isdigit()


def leer_excel():
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    ws = wb['1 SGSSS']
    filas = [r for r in ws.iter_rows(values_only=True) if es_fila_de_corte(r[0])]
    return filas


def procesar(filas):
    """Se queda solo con el corte más reciente y arma el detalle por cohorte y régimen."""
    cortes = sorted({f[0] for f in filas}, key=clave_corte)
    ultimo_corte = cortes[-1]

    detalle = {}  # {quinquenio: {regimen: cantidad}}
    for corte, regimen, quinquenio, cantidad in filas:
        if corte != ultimo_corte:
            continue
        detalle.setdefault(quinquenio, {})[regimen] = cantidad

    por_cohorte = []
    totales_regimen = {r: 0 for r in ORDEN_REGIMEN}
    total_general = 0

    for q in ORDEN_QUINQUENIO:
        regimenes = detalle.get(q, {})
        total_q = sum(regimenes.values())
        por_cohorte.append({
            'quinquenio': q,
            'total': total_q,
            'regimen': {r: regimenes.get(r, 0) for r in ORDEN_REGIMEN},
        })
        for r in ORDEN_REGIMEN:
            totales_regimen[r] += regimenes.get(r, 0)
        total_general += total_q

    return {
        'corte': ultimo_corte,
        'fuente': 'MinSalud – Caracterización de afiliados (PISIS/BDUA)',
        'nota': ('Bogotá D.C., jóvenes de 15 a 29 años (no incluye 14 años por límite de la fuente). '
                 'La categoría "No sabe" no está disponible en esta fuente.'),
        'regimenes': ORDEN_REGIMEN,
        'por_cohorte': por_cohorte,
        'totales_regimen': totales_regimen,
        'total_general': total_general,
    }


def guardar_json(datos):
    os.makedirs(DATA_DIR, exist_ok=True)
    ruta = os.path.join(DATA_DIR, 'sgsss.json')
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print('  sgsss.json generado')
    return ruta


def main():
    print('=' * 60)
    print('Actualización — Dimensión 4: SGSSS (4.1)')
    print('=' * 60)

    filas = leer_excel()
    datos = procesar(filas)

    print(f'  Corte: {datos["corte"]}')
    print(f'  Total jóvenes 15-29: {datos["total_general"]:,}'.replace(',', '.'))
    for r in ORDEN_REGIMEN:
        print(f'  {r}: {datos["totales_regimen"][r]:,}'.replace(',', '.'))

    ruta = guardar_json(datos)
    print(f'\nArchivo: {ruta}')


if __name__ == '__main__':
    main()
