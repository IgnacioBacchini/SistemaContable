import tempfile, os, zipfile
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from Models import *  
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# engine = create_engine('sqlite:///C:\\Users\\PETY\\Desktop\\Argenway\\database\\SistemaPRU.db')
# engine = create_engine('sqlite:///C:\\Users\\Argenway\\Documents\\BD_PRU\\database\\SistemaPRU.db')
engine = create_engine('sqlite:///C:\\Users\\ignac\\Desktop\\Argenway\\SistemaContable\\database\\SistemaPRU.db')
# engine = create_engine('sqlite:///C:\\Roberto\\Argenway\\240120 aplicacion\\SistemaContable2\\SistemaContable\\database\\SistemaPRU.db')
# engine = create_engine('sqlite:////home/sanchez/SistemaContable/database/SistemaPRU.db')
# Crear un objeto inspector
inspector = inspect(engine)

Session = sessionmaker(bind=engine)

def get_table_names(engine):
    inspector = inspect(engine)
    return inspector.get_table_names()

def crear_zip_en_memoria():
    # Obtener la ruta absoluta del directorio actual
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    
    # Crear un archivo ZIP temporal
    archivo_zip = tempfile.NamedTemporaryFile(delete=False)

    # Agregar cada tabla como un archivo CSV al archivo ZIP temporal
    with zipfile.ZipFile(archivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for nombre_tabla in inspector.get_table_names():
            df = pd.read_sql_table(nombre_tabla, engine)
            csv_buffer = os.path.join(tempfile.gettempdir(), f'{nombre_tabla}.csv')
            df.to_csv(csv_buffer, index=False)
            zipf.write(csv_buffer, arcname=f'{nombre_tabla}.csv')
            os.remove(csv_buffer)

    return archivo_zip.name
