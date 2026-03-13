# actualizar_habitat.py — Dimensión 7: Hábitat
# Procesa los microdatos SPSS de la Encuesta de Percepción Ciudadana
# (Bogotá Cómo Vamos) y genera el JSON de hábitat en jóvenes.
#
# Variables disponibles:
#   AMB_2: Satisfacción calidad del agua (ríos, quebradas, humedales...)
#   AMB_3: Satisfacción ruido de la ciudad
#   GOB_3: Satisfacción con Bogotá como lugar para vivir
#
# Variables NO disponibles en microdatos (pendientes):
#   - Acciones para cuidar el medio ambiente (ahorrar agua, reciclar, etc.)
#   - Satisfacción con la vivienda que habita
#
# Uso:
#   python dim7/actualizar_habitat.py
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


# ============================================================
# Funciones
# ============================================================

def encontrar_spss(carpeta):
    """Busca el archivo SPSS de microdatos."""
    for f in os.listdir(carpeta):
        if f.lower().startswith('microdatos') and not f.endswith('.xlsx'):
            return os.path.join(carpeta, f)
        if f.lower().endswith('.sav'):
            return os.path.join(carpeta, f)
    return None


def calcular_satisfaccion(serie):
    """Calcula porcentajes de satisfacción agrupados en 3 categorías.
    Escala: 1-2 insatisfecho, 3 ni/ni, 4-5 satisfecho. Excluye 90 (No sabe).
    """
    datos = serie.dropna()
    datos = datos[datos <= 5]  # Excluir "No sabe" (90)
    n = len(datos)
    if n == 0:
        return {'satisfecho': 0, 'ni_satisfecho_ni_insatisfecho': 0, 'insatisfecho': 0, 'n': 0}

    satisfecho = (datos >= 4).sum()
    ni = (datos == 3).sum()
    insatisfecho = (datos <= 2).sum()

    return {
        'satisfecho': round(satisfecho / n * 100, 2),
        'ni_satisfecho_ni_insatisfecho': round(ni / n * 100, 2),
        'insatisfecho': round(insatisfecho / n * 100, 2),
        'n': n,
    }


def procesar(ruta_spss):
    """Lee el SPSS, filtra jóvenes y calcula indicadores de hábitat."""
    df, meta = pyreadstat.read_sav(ruta_spss)

    # Filtrar jóvenes 18-25
    jovenes = df[(df['DMO_3_1'] >= EDAD_MIN) & (df['DMO_3_1'] <= EDAD_MAX)].copy()
    n = len(jovenes)
    print(f'  Jóvenes 18-25: {n} de {len(df)} encuestados')

    # --- 1. Satisfacción calidad del agua (AMB_2) ---
    agua = calcular_satisfaccion(jovenes['AMB_2'])

    # --- 2. Satisfacción ruido de la ciudad (AMB_3) ---
    ruido = calcular_satisfaccion(jovenes['AMB_3'])

    # --- 3. Satisfacción con Bogotá como lugar para vivir (GOB_3) ---
    vivienda = calcular_satisfaccion(jovenes['GOB_3'])

    return {
        'fuente': 'Encuesta de Percepción Ciudadana - Bogotá Cómo Vamos - 2025',
        'poblacion': f'Jóvenes de {EDAD_MIN} a {EDAD_MAX} años de Bogotá',
        'n_jovenes': n,
        'satisfaccion_agua': agua,
        'satisfaccion_ruido': ruido,
        'satisfaccion_vivienda': vivienda,
        'notas': 'La variable de acciones ambientales y satisfacción con vivienda específica no están disponibles en los microdatos. Se usa GOB_3 (satisfacción con Bogotá como lugar para vivir) como proxy.',
    }


def guardar_json(datos):
    os.makedirs(DATA_DIR, exist_ok=True)
    ruta = os.path.join(DATA_DIR, 'habitat.json')
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f'  habitat.json generado')
    return ruta


def main():
    print('=' * 60)
    print('Actualización — Dimensión 7: Hábitat')
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
    for key, label in [('satisfaccion_agua', 'Calidad del agua'), ('satisfaccion_ruido', 'Ruido'), ('satisfaccion_vivienda', 'Bogotá como lugar para vivir')]:
        d = datos[key]
        print(f'\n  {label}:')
        print(f'    Satisfecho {d["satisfecho"]}% / Ni {d["ni_satisfecho_ni_insatisfecho"]}% / Insatisfecho {d["insatisfecho"]}%  (n={d["n"]})')

    print(f'\nArchivo: {ruta}')


if __name__ == '__main__':
    main()
