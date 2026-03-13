# actualizar_discapacidad.py — Dimensión 4: Salud integral y autocuidado
# Script para procesar el CSV del Observatorio de Salud de Bogotá (OSB)
# y generar el JSON de discapacidad certificada en jóvenes.
#
# Uso:
#   1. Descargar el CSV de SaludData / OSB
#   2. Guardar en dim4/fuentes/discapacidad/
#   3. Correr: python dim4/actualizar_discapacidad.py

import os
import csv
import json

# ============================================================
# Configuración
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FUENTES_DIR = os.path.join(SCRIPT_DIR, 'fuentes', 'discapacidad')
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')

# Grupos de edad que corresponden a jóvenes (14-28 aprox.)
GRUPOS_JUVENTUD = {'Juventud', 'Adolescencia'}

# Categorías de discapacidad en el CSV y nombres para el JSON
CATEGORIAS = [
    ('Cat_Multiple', 'Discapacidad múltiple'),
    ('Cat_Intelectual', 'Discapacidad intelectual'),
    ('Cat_Fisica', 'Discapacidad física'),
    ('Cat_Psicosocial', 'Discapacidad psicosocial'),
    ('Cat_Auditiva', 'Discapacidad auditiva'),
    ('Cat_Visual', 'Discapacidad visual'),
    ('Cat_Sordoceguera', 'Sordoceguera'),
]


# ============================================================
# Funciones
# ============================================================

def encontrar_csv(carpeta):
    """Busca el archivo CSV más reciente en la carpeta."""
    if not os.path.exists(carpeta):
        print(f'ERROR: No existe la carpeta {carpeta}')
        return None
    archivos = [f for f in os.listdir(carpeta)
                if f.endswith('.csv') and not f.startswith('~$')]
    if not archivos:
        print(f'ERROR: No se encontró CSV en {carpeta}')
        return None
    archivos.sort()
    return os.path.join(carpeta, archivos[-1])


def procesar(ruta_csv):
    """Lee el CSV y cuenta jóvenes por tipo de discapacidad y localidad."""
    conteo_tipo = {col: 0 for col, _ in CATEGORIAS}
    conteo_localidad = {}
    total = 0

    with open(ruta_csv, 'r', encoding='latin-1') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            grupo = row.get('Grupo de Edad', '').strip()
            if grupo not in GRUPOS_JUVENTUD:
                continue

            total += 1
            localidad = row.get('Localidad', '').strip()
            if localidad and localidad not in ('Sin Dato', 'Fuera de Bogota'):
                conteo_localidad[localidad] = conteo_localidad.get(localidad, 0) + 1

            for col, _ in CATEGORIAS:
                if row.get(col, '').strip().upper() == 'SI':
                    conteo_tipo[col] += 1

    # Ordenar tipos de mayor a menor
    por_tipo = []
    for col, nombre in CATEGORIAS:
        por_tipo.append({
            'tipo': col.replace('Cat_', '').lower(),
            'nombre': nombre,
            'cantidad': conteo_tipo[col],
        })
    por_tipo.sort(key=lambda x: x['cantidad'], reverse=True)

    # Ordenar localidades de mayor a menor
    por_localidad = [{'localidad': k, 'cantidad': v}
                     for k, v in conteo_localidad.items()]
    por_localidad.sort(key=lambda x: x['cantidad'], reverse=True)

    return {
        'total_jovenes_discapacidad': total,
        'nota': 'Incluye grupos Juventud y Adolescencia como proxy de 14-28 años. Una persona puede tener más de un tipo de discapacidad.',
        'por_tipo': por_tipo,
        'por_localidad': por_localidad,
    }


def guardar_json(datos):
    os.makedirs(DATA_DIR, exist_ok=True)
    ruta = os.path.join(DATA_DIR, 'discapacidad.json')
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f'  discapacidad.json generado')
    return ruta


def main():
    print('=' * 60)
    print('Actualización — Dimensión 4: Discapacidad')
    print('=' * 60)

    archivo = encontrar_csv(FUENTES_DIR)
    if not archivo:
        return
    print(f'  Archivo: {os.path.basename(archivo)}')

    print('\nProcesando...')
    datos = procesar(archivo)
    print(f'  Total jóvenes con discapacidad: {datos["total_jovenes_discapacidad"]:,}'.replace(',', '.'))

    print('\nPor tipo de discapacidad:')
    for t in datos['por_tipo']:
        print(f'  {t["nombre"]}: {t["cantidad"]:,}'.replace(',', '.'))

    print('\nGenerando JSON...')
    ruta = guardar_json(datos)
    print(f'\nArchivo: {ruta}')


if __name__ == '__main__':
    main()
