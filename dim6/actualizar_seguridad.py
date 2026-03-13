# actualizar_seguridad.py — Dimensión 6: Paz, Justicia y Convivencia
# Procesa los microdatos SPSS de la Encuesta de Percepción Ciudadana
# (Bogotá Cómo Vamos) y genera el JSON de seguridad en jóvenes.
#
# Uso:
#   1. El archivo SPSS debe estar en dim6/fuentes/Bogota como vamos/Microdatos
#   2. Correr: python dim6/actualizar_seguridad.py
#
# Dependencia: pyreadstat (pip install pyreadstat)

import os
import json
import pyreadstat

# ============================================================
# Configuración
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FUENTES_DIR = os.path.join(SCRIPT_DIR, 'fuentes', 'Bogota como vamos')
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')

# Filtro de edad (jóvenes)
EDAD_MIN = 18
EDAD_MAX = 25

# Problemas de seguridad (SEG_3) — labels del SPSS
PROBLEMAS_LABELS = {
    1.0: 'Las pandillas',
    2.0: 'Se presentan atracos callejeros',
    3.0: 'Se roban muchos carros o partes',
    4.0: 'Asaltos a casas o apartamentos',
    5.0: 'Atracos a tiendas o negocios del barrio',
    6.0: 'Se presentan casos de homicidio',
    7.0: 'Tráfico de drogas',
    8.0: 'Se presentan casos de violaciones',
    9.0: 'Vandalismo contra edificaciones, parques y otros',
    10.0: 'Presencia de paramilitarismo y milicias (guerrilla)',
    13.0: 'Drogadicción',
    89.0: 'Otra',
    90.0: 'No se presenta ningún problema grave de seguridad en mi barrio',
    141.0: 'Extorsión',
}


# ============================================================
# Funciones
# ============================================================

def encontrar_spss(carpeta):
    """Busca el archivo SPSS de microdatos."""
    for f in os.listdir(carpeta):
        if f.lower().startswith('microdatos') or f.lower().endswith('.sav'):
            return os.path.join(carpeta, f)
    return None


def procesar(ruta_spss):
    """Lee el SPSS, filtra jóvenes y calcula indicadores de seguridad."""
    df, meta = pyreadstat.read_sav(ruta_spss)

    # Filtrar jóvenes 18-25
    jovenes = df[(df['DMO_3_1'] >= EDAD_MIN) & (df['DMO_3_1'] <= EDAD_MAX)].copy()
    n = len(jovenes)
    print(f'  Jóvenes 18-25: {n} de {len(df)} encuestados')

    # --- 1. Problemas de seguridad en el barrio (SEG_3_1, SEG_3_2, SEG_3_3) ---
    # Cada persona menciona hasta 3 problemas (respuesta múltiple)
    conteo_problemas = {}
    for col in ['SEG_3_1', 'SEG_3_2', 'SEG_3_3']:
        for val in jovenes[col].dropna():
            label = PROBLEMAS_LABELS.get(val, f'Código {int(val)}')
            conteo_problemas[label] = conteo_problemas.get(label, 0) + 1

    # Porcentaje sobre total de jóvenes (respuesta múltiple)
    problemas = []
    for label, count in conteo_problemas.items():
        problemas.append({
            'problema': label,
            'porcentaje': round(count / n * 100, 2),
            'respuestas': count,
        })
    problemas.sort(key=lambda x: x['porcentaje'], reverse=True)

    # --- 2. Víctima de delito (SEG_4) ---
    victima = jovenes['SEG_4'].dropna()
    n_victima = len(victima)
    si = (victima == 1.0).sum()
    no = (victima == 2.0).sum()
    pct_si = round(si / n_victima * 100, 2) if n_victima > 0 else 0
    pct_no = round(no / n_victima * 100, 2) if n_victima > 0 else 0

    victima_delito = {
        'si': pct_si,
        'no': pct_no,
        'n': n_victima,
    }

    # --- 3. Percepción de seguridad en el barrio (SEG_2) ---
    seg_barrio = jovenes['SEG_2'].dropna()
    seg_barrio = seg_barrio[seg_barrio <= 5]  # Excluir "No sabe" si hay
    n_barrio = len(seg_barrio)
    seguro_b = ((seg_barrio >= 4)).sum()
    ni_b = (seg_barrio == 3).sum()
    inseguro_b = (seg_barrio <= 2).sum()

    percepcion_barrio = {
        'seguro': round(seguro_b / n_barrio * 100, 2) if n_barrio > 0 else 0,
        'ni_seguro_ni_inseguro': round(ni_b / n_barrio * 100, 2) if n_barrio > 0 else 0,
        'inseguro': round(inseguro_b / n_barrio * 100, 2) if n_barrio > 0 else 0,
        'n': n_barrio,
    }

    # --- 4. Percepción de seguridad en la ciudad (SEG_1) ---
    seg_ciudad = jovenes['SEG_1'].dropna()
    seg_ciudad = seg_ciudad[seg_ciudad <= 5]
    n_ciudad = len(seg_ciudad)
    seguro_c = (seg_ciudad >= 4).sum()
    ni_c = (seg_ciudad == 3).sum()
    inseguro_c = (seg_ciudad <= 2).sum()

    percepcion_ciudad = {
        'seguro': round(seguro_c / n_ciudad * 100, 2) if n_ciudad > 0 else 0,
        'ni_seguro_ni_inseguro': round(ni_c / n_ciudad * 100, 2) if n_ciudad > 0 else 0,
        'inseguro': round(inseguro_c / n_ciudad * 100, 2) if n_ciudad > 0 else 0,
        'n': n_ciudad,
    }

    return {
        'fuente': 'Encuesta de Percepción Ciudadana - Bogotá Cómo Vamos - 2025',
        'poblacion': f'Jóvenes de {EDAD_MIN} a {EDAD_MAX} años de Bogotá',
        'n_jovenes': n,
        'problemas_barrio': problemas,
        'victima_delito': victima_delito,
        'percepcion_barrio': percepcion_barrio,
        'percepcion_ciudad': percepcion_ciudad,
    }


def guardar_json(datos):
    os.makedirs(DATA_DIR, exist_ok=True)
    ruta = os.path.join(DATA_DIR, 'seguridad.json')
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f'  seguridad.json generado')
    return ruta


def main():
    print('=' * 60)
    print('Actualización — Dimensión 6: Seguridad')
    print('=' * 60)

    archivo = encontrar_spss(FUENTES_DIR)
    if not archivo:
        print('ERROR: No se encontró archivo SPSS de microdatos')
        return
    print(f'  Archivo: {os.path.basename(archivo)}')

    print('\nProcesando...')
    datos = procesar(archivo)

    print('\nGenerando JSON...')
    ruta = guardar_json(datos)

    # Verificación
    print(f'\n{"=" * 60}')
    print('VERIFICACIÓN:')
    print(f'{"=" * 60}')
    print(f'  Jóvenes encuestados: {datos["n_jovenes"]}')
    print(f'\n  Problemas de seguridad (top 5):')
    for p in datos['problemas_barrio'][:5]:
        print(f'    {p["problema"]}: {p["porcentaje"]}%')
    print(f'\n  Víctima de delito: Sí {datos["victima_delito"]["si"]}% / No {datos["victima_delito"]["no"]}%')
    print(f'  Seguridad barrio: Seguro {datos["percepcion_barrio"]["seguro"]}% / Ni {datos["percepcion_barrio"]["ni_seguro_ni_inseguro"]}% / Inseguro {datos["percepcion_barrio"]["inseguro"]}%')
    print(f'  Seguridad ciudad: Seguro {datos["percepcion_ciudad"]["seguro"]}% / Ni {datos["percepcion_ciudad"]["ni_seguro_ni_inseguro"]}% / Inseguro {datos["percepcion_ciudad"]["inseguro"]}%')

    print(f'\nArchivo: {ruta}')


if __name__ == '__main__':
    main()
