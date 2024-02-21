import tempfile, os, zipfile, sqlite3
import pandas as pd

def crear_zip_en_memoria():
    # Conectar a la base de datos
    conexion = sqlite3.connect('database/SistemaPRU.db')

    # Obtener una lista de todas las tablas en la base de datos
    cursor = conexion.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()

    # Crear un archivo ZIP temporal
    archivo_zip = tempfile.NamedTemporaryFile(delete=False)

    # Agregar cada tabla como un archivo CSV al archivo ZIP temporal
    with zipfile.ZipFile(archivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for tabla in tablas:
            nombre_tabla = tabla[0]
            df = pd.read_sql_query(f"SELECT * FROM {nombre_tabla};", conexion)
            csv_buffer = os.path.join(tempfile.gettempdir(), f'{nombre_tabla}.csv')
            df.to_csv(csv_buffer, index=False)
            zipf.write(csv_buffer, arcname=f'{nombre_tabla}.csv')
            os.remove(csv_buffer)

    # Cerrar la conexión a la base de datos
    conexion.close()

    return archivo_zip.name
