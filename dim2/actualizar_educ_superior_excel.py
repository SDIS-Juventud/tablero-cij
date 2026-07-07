# actualizar_educ_superior_excel.py — Dimensión 2: Educación Superior
# Lee la hoja "educacion_superior" de datos_dim2.xlsx (mantenida a mano por
# Carolina con cifras oficiales MEN/SNIES) y regenera data/educacion_superior.json.
#
# A diferencia de actualizar_educ_superior.py (que procesa el CSV de datos.gov.co
# por municipios), este script lee directamente el Excel consolidado, que trae
# también las tasas de cobertura y tránsito Bogotá/Nacional que el CSV no tiene.
#
# Uso:
#   1. Actualizar la hoja "educacion_superior" en datos_dim2.xlsx
#   2. Correr: python dim2/actualizar_educ_superior_excel.py
#   3. El archivo data/educacion_superior.json se regenera automáticamente.

import os
import json
import openpyxl

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(SCRIPT_DIR, 'datos_dim2.xlsx')
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')

# Orden fijo de columnas en la hoja "educacion_superior" (se lee por posición
# para evitar problemas de codificación con los encabezados con tilde/ñ)
COLUMNAS = [
    'anio', 'tecnica_profesional', 'tecnologica', 'universitaria',
    'especializacion', 'maestria', 'doctorado', 'total_bogota',
    'total_colombia', 'ies_con_oferta', 'pct_bogota',
    'tasa_cobertura_bogota', 'tasa_cobertura_nacional',
    'tasa_transito_bogota', 'tasa_transito_nacional',
]

# Columnas que a veces vienen como texto ('NA' o 'PENDIENTE') en vez de número
CAMPOS_OPCIONALES = [
    'ies_con_oferta', 'pct_bogota', 'tasa_cobertura_bogota',
    'tasa_cobertura_nacional', 'tasa_transito_bogota', 'tasa_transito_nacional',
]


def limpiar_valor(valor):
    """Convierte 'NA' / 'PENDIENTE' / vacío a None; deja los números tal cual."""
    if isinstance(valor, str) and valor.strip().upper() in ('NA', 'PENDIENTE', ''):
        return None
    return valor


def leer_excel():
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    ws = wb['educacion_superior']

    registros = []
    for fila in ws.iter_rows(min_row=2, values_only=True):
        if fila[0] is None:
            continue
        registro = dict(zip(COLUMNAS, fila))
        registro['anio'] = int(registro['anio'])
        for campo in CAMPOS_OPCIONALES:
            registro[campo] = limpiar_valor(registro[campo])
        registros.append(registro)

    registros.sort(key=lambda r: r['anio'])
    return registros


def generar_json(registros):
    os.makedirs(DATA_DIR, exist_ok=True)
    ruta = os.path.join(DATA_DIR, 'educacion_superior.json')
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)
    return ruta


def main():
    print('=' * 60)
    print('Actualización de datos — Dimensión 2: Educación Superior (Excel)')
    print('=' * 60)

    print(f'\nLeyendo {EXCEL_PATH}...')
    registros = leer_excel()
    print(f'  {len(registros)} años leídos')

    ruta = generar_json(registros)
    print(f'\nArchivo actualizado: {ruta}')

    ultimo = registros[-1]
    print(f'\nVERIFICACIÓN — Año {ultimo["anio"]}:')
    print(f'  Total Bogotá: {ultimo["total_bogota"]:,.0f}'.replace(',', '.'))
    print(f'  Total Colombia: {ultimo["total_colombia"]:,.0f}'.replace(',', '.'))
    print(f'  Tasa cobertura Bogotá: {ultimo["tasa_cobertura_bogota"]}')
    print(f'  Tasa tránsito Bogotá: {ultimo["tasa_transito_bogota"]}')

    anios = [r['anio'] for r in registros]
    print(f'\nAños disponibles: {min(anios)} – {max(anios)}')
    print('\nEl tablero web se actualizará automáticamente al hacer push.')


if __name__ == '__main__':
    main()
