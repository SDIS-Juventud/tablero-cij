# actualizar_bienal.py — Dimensión 5: Cultura, Recreación y Deporte
# Lee datos-dim5.xlsx (generado por extraer_bienal_microdatos.py) y genera
# bienal_culturas.json, que es lo que consume dim5/index.html.
#
# Flujo de actualización (cada dos años — encuesta bienal):
#   1. Conseguir los microdatos nuevos y guardarlos en dim5/fuentes/
#   2. Correr: python dim5/extraer_bienal_microdatos.py
#   3. Correr: python dim5/actualizar_bienal.py
#
# Si la fuente cambia de formato en el futuro, solo hay que reescribir
# extraer_bienal_microdatos.py — este script y el esquema del Excel
# intermedio se mantienen iguales.
#
# Requiere: pip install openpyxl

import os
import json
import openpyxl

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(os.path.dirname(SCRIPT_DIR),
                          'tablero-cij-compartido', 'dim5', 'datos-dim5.xlsx')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'data', 'bienal_culturas.json')


def leer_pares(ws):
    """Lee una hoja de dos columnas (etiqueta, valor) y la devuelve como lista."""
    filas = []
    for etiqueta, valor in ws.iter_rows(min_row=2, values_only=True):
        if etiqueta is None:
            continue
        filas.append({'nombre': etiqueta, 'pct': valor})
    return filas


def leer_info(ws):
    return {fila[0]: fila[1] for fila in ws.iter_rows(min_row=2, values_only=True) if fila[0]}


def main():
    print('=' * 60)
    print('Generación de bienal_culturas.json desde datos-dim5.xlsx')
    print('=' * 60)

    if not os.path.exists(EXCEL_PATH):
        print('ERROR: No se encontró datos-dim5.xlsx')
        print('  → Correr primero: python dim5/extraer_bienal_microdatos.py')
        return

    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)

    info = leer_info(wb['Info'])

    kpis = {fila[0]: fila[1] for fila in wb['KPIs'].iter_rows(min_row=2, values_only=True) if fila[0]}

    ws_sat = wb['Satisfaccion']
    niveles_clave = {
        'Nada satisfecho/a': 'nada',
        'Poco satisfecho/a': 'poco',
        'Satisfecho/a': 'satisfecho',
        'Muy satisfecho/a': 'muy_satisfecho',
    }
    sat_cultura, sat_deporte = {}, {}
    for nivel, cultura, deporte in ws_sat.iter_rows(min_row=2, values_only=True):
        clave = niveles_clave.get(nivel, nivel)
        sat_cultura[clave] = cultura
        sat_deporte[clave] = deporte

    resultado = {
        'fuente_cultura': info.get('Fuente Cultura'),
        'fuente_deportes': info.get('Fuente Deportes'),
        'corte_edad': info.get('Corte edad jóvenes'),
        'nota_categorias_descontinuadas': info.get('Categorías de participación cultural descontinuadas'),
        'kpis': {
            'practica_cultural_actual': kpis.get('practica_cultural_actual'),
            'practica_deportiva_actual': kpis.get('practica_deportiva_actual'),
        },
        'satisfaccion': {
            'cultura_distrito': sat_cultura,
            'deporte_distrito': sat_deporte,
        },
        'practica_cultural': leer_pares(wb['Practica_Cultural']),
        'asistencia_cultural': leer_pares(wb['Asistencia_Cultural']),
        'razon_no_deporte': leer_pares(wb['Razon_No_Deporte']),
        'donde_actividad_fisica': leer_pares(wb['Donde_Actividad_Fisica']),
        'etapas_cambio': leer_pares(wb['Etapas_Cambio']),
    }

    wb.close()

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f'Práctica cultural actual: {resultado["kpis"]["practica_cultural_actual"]}%')
    print(f'Práctica deportiva actual: {resultado["kpis"]["practica_deportiva_actual"]}%')
    print(f'Actividades culturales (práctica): {len(resultado["practica_cultural"])}')
    print(f'Actividades culturales (asistencia): {len(resultado["asistencia_cultural"])}')
    print(f'\nArchivo: {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
