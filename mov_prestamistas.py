
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from Models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# engine = create_engine('sqlite:///C:\\Users\\PETY\\Desktop\\Argenway\\database\\SistemaPRU.db')
# engine = create_engine('sqlite:///C:\\Users\\Argenway\\Documents\\BD_PRU\\database\\SistemaPRU.db')
engine = create_engine('sqlite:///C:\\Users\\ignac\\Desktop\\Argenway\\SistemaContable\\database\\SistemaPRU.db')
# engine = create_engine('sqlite:///C:\\Roberto\\Argenway\\240120 aplicacion\\SistemaContable2\\SistemaContable\\database\\SistemaPRU.db')
# engine = create_engine('sqlite:////home/sanchez/SistemaContable/database/SistemaPRU.db')

Session = sessionmaker(bind=engine)

def movimientos_prestamistas(id_concepto):
    # Consulta principal para obtener los detalles de las cuentas asociadas al concepto de prestamistas
    movimientos = RelacionMovimientos.query.filter(
        (RelacionMovimientos.id_concepto_hacia == id_concepto) | 
        (RelacionMovimientos.id_concepto_desde == id_concepto)
    ).all()

    return movimientos