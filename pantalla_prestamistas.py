import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from Models import *
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# engine = create_engine('sqlite:///C:\\Users\\PETY\\Desktop\\Argenway\\database\\SistemaPRU.db')
# engine = create_engine('sqlite:///C:\\Users\\Argenway\\Documents\\BD_PRU\\database\\SistemaPRU.db')
engine = create_engine('sqlite:///C:\\Users\\ignac\\Desktop\\Argenway\\SistemaContable\\database\\SistemaPRU.db')
# engine = create_engine('sqlite:///C:\\Roberto\\Argenway\\240120 aplicacion\\SistemaContable2\\SistemaContable\\database\\SistemaPRU.db')
# engine = create_engine('sqlite:////home/sanchez/SistemaContable/database/SistemaPRU.db')

Session = sessionmaker(bind=engine)

def obtener_prestamistas(id_concepto):
    # Consulta principal para obtener los detalles de las cuentas asociadas al concepto de prestamistas
    consulta = db.session.query(
        Cuentas.id_cuenta,
        Inversor_prestamista_deudor.nombre_inversor_prestamista_deudor,
        Empresa.nombre_empresa,
        Proyecto.nombre_proyecto,
        Moneda.descr_moneda,
        Proyecto.fecha_fin_obra,
        Proyecto.fecha_inicio_obra,
        Contrato.tasa_anual,
        Contrato.monto_contrato
    ).filter(
        Cuentas.id_concepto == id_concepto
    ).join(
        Contrato, Cuentas.id_inversor_prestamista_deudor == Contrato.id_inversor_prestamista_deudor
    ).join(
        Proyecto, Contrato.id_proyecto == Proyecto.id_proyecto
    ).join(
        Empresa, Contrato.id_empresa == Empresa.id_empresa
    ).join(
        Moneda, Contrato.id_moneda == Moneda.id_moneda
    ).join(
        Inversor_prestamista_deudor, Cuentas.id_inversor_prestamista_deudor == Inversor_prestamista_deudor.id_inversor_prestamista_deudor
    ).filter(
        Contrato.id_contrato == Cuentas.id_contrato
    ).all()

    # Convertir resultados a DataFrame para manipulación adicional si es necesario
    df_consulta = pd.DataFrame(consulta, columns=[
        'id_cuenta', 
        'nombre_inversor_prestamista_deudor', 
        'nombre_empresa', 
        'nombre_proyecto', 
        'descr_moneda', 
        'fecha_fin_obra',
        'fecha_inicio_obra', 
        'tasa_anual', 
        'monto_contrato'
    ])
    # Asegurar que las columnas de fecha están en formato de fecha sin horas, minutos y segundos
    df_consulta['fecha_inicio_obra_temp'] = pd.to_datetime(df_consulta['fecha_inicio_obra'])
    df_consulta['fecha_fin_obra_temp'] = pd.to_datetime(df_consulta['fecha_fin_obra'])

    # Calcular la diferencia en días entre fecha_fin_obra y fecha_inicio_obra
    df_consulta['dias_diferencia'] = (df_consulta['fecha_fin_obra_temp'] - df_consulta['fecha_inicio_obra_temp']).dt.days

    # Calcular la diferencia en meses entre fecha_fin_obra y fecha_inicio_obra
    df_consulta['plazo'] = (df_consulta['fecha_fin_obra_temp'].dt.year - df_consulta['fecha_inicio_obra_temp'].dt.year) * 12 + (df_consulta['fecha_fin_obra_temp'].dt.month - df_consulta['fecha_inicio_obra_temp'].dt.month)

    # Calcular el total
    df_consulta['total'] = df_consulta['monto_contrato'] * (1 + df_consulta['tasa_anual'] / 365 * df_consulta['dias_diferencia'])

    # Formatear las fechas en formato dd-mm-aaaa
    df_consulta['fecha_inicio_obra'] = df_consulta['fecha_inicio_obra_temp'].dt.strftime('%d-%m-%Y')
    df_consulta['fecha_fin_obra'] = df_consulta['fecha_fin_obra_temp'].dt.strftime('%d-%m-%Y')

    # Convertir el DataFrame a una lista de diccionarios para facilitar la manipulación y el retorno de los datos
    datos = df_consulta.to_dict(orient='records')
    return datos