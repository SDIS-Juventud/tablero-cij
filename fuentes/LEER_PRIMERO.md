# Carpeta de fuentes DANE

Aquí se guardan los archivos Excel del DANE para actualizar el tablero.

## Cómo actualizar

1. Descargar el anexo más reciente de:
   https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/mercado-laboral-de-la-juventud

2. El archivo se llama algo como `anex-GEIHMLJ-oct-dic2025.xlsx`

3. Copiarlo a esta carpeta (`fuentes/`)

4. Subir a GitHub:
   ```
   git add fuentes/
   git commit -m "Nuevo anexo DANE [trimestre]"
   git push
   ```

5. GitHub Actions procesará el archivo automáticamente y actualizará el tablero.
   Verificar en: https://sdis-juventud.github.io/tablero-cij/

## Archivos esperados

- `anex-GEIHMLJ-*.xlsx` — Anexo GEIH Mercado laboral de la juventud (DANE)
