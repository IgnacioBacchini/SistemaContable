from sqlalchemy import create_engine, func
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker, aliased
from Models import *
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

# engine = create_engine('sqlite:///C:\\Users\\PETY\\Desktop\\Argenway\\database\\SistemaPRU.db')
# engine = create_engine('sqlite:///C:\\Users\\Argenway\\Documents\\BD_PRU\\database\\SistemaPRU.db')
engine = create_engine('sqlite:///C:\\Users\\ignac\\Desktop\\Argenway\\SistemaContable\\database\\SistemaPRU.db')
# engine = create_engine('sqlite:///C:\\Roberto\\Argenway\\240120 aplicacion\\SistemaContable2\\SistemaContable\\database\\SistemaPRU.db')
# engine = create_engine('sqlite:////home/sanchez/SistemaContable/database/SistemaPRU.db')

Session = sessionmaker(bind=engine)

def generar_id_cuenta_hacia(id_concepto, id_empresa, id_moneda, nombre_cuenta):
    # Realizar la consulta para obtener el id de la cuenta hacia
    cuenta = Cuentas.query.filter_by(
        id_concepto=id_concepto,
        id_empresa=id_empresa,
        id_moneda=id_moneda,
        nombre_cuenta=nombre_cuenta
    ).first()
    
    if cuenta:
        # Si se encuentra una cuenta correspondiente, se retorna su id
        return cuenta.id_cuenta
    else:
        # Si no se encuentra una cuenta correspondiente, se devuelve None
        return None

def consultar_cuentas_inversores():
    # Función para consultar las cuentas de inversores
    try:
        # Creamos una sesión
        session = Session()
        # Obtener la fecha actual sin la hora
        fecha_actual = datetime.now().date()

        # Calcular la fecha del primer día del mes anterior
        ultimo_dia_mes_anterior = fecha_actual.replace(day=1) - timedelta(days=1)
        primer_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)

        # Consulta de cuentas de inversores
        cuentas_query = Cuentas.query.filter(
            Cuentas.inversor_prestamista_deudor_T_F == True,
            Cuentas.tipo_cta == 'B'
        ).with_entities(
            Cuentas.id_cuenta, 
            Cuentas.id_empresa, 
            Cuentas.id_moneda, 
            Cuentas.id_contrato
        )
        
        # Consulta SUM_DESDE_PRIMERO sobre la tabla RELACION_MOVIMIENTOS
        sum_desde_primero_query = RelacionMovimientos.query.filter(
            RelacionMovimientos.fecha <= primer_dia_mes_anterior
        ).with_entities(
            RelacionMovimientos.id_cuenta_desde, 
            RelacionMovimientos.id_empresa,
            RelacionMovimientos.id_moneda_desde, 
            func.sum(RelacionMovimientos.valor_desde).label("suma_valor_desde_primero")
        ).group_by(
            RelacionMovimientos.id_empresa,
            RelacionMovimientos.id_cuenta_desde, 
            RelacionMovimientos.id_moneda_desde
        )
        
        # Consulta SUM_DESDE_ULTIMO sobre la tabla RELACION_MOVIMIENTOS
        sum_desde_ultimo_query = RelacionMovimientos.query.filter(
            RelacionMovimientos.fecha <= ultimo_dia_mes_anterior
        ).with_entities(
            RelacionMovimientos.id_cuenta_desde, 
            RelacionMovimientos.id_empresa,
            RelacionMovimientos.id_moneda_desde, 
            func.sum(RelacionMovimientos.valor_desde).label("suma_valor_desde_ultimo")
        ).group_by(
            RelacionMovimientos.id_empresa,
            RelacionMovimientos.id_cuenta_desde, 
            RelacionMovimientos.id_moneda_desde
        )
        
        # Consulta SUM_HACIA_PRIMERO sobre la tabla RELACION_MOVIMIENTOS
        sum_hacia_primero_query = RelacionMovimientos.query.filter(
            RelacionMovimientos.fecha <= primer_dia_mes_anterior
        ).with_entities(
            RelacionMovimientos.id_cuenta_hacia, 
            RelacionMovimientos.id_empresa,
            RelacionMovimientos.id_moneda_hacia, 
            func.sum(RelacionMovimientos.valor_hacia_calculado).label("suma_valor_hacia_primero")
        ).group_by(
            RelacionMovimientos.id_empresa, 
            RelacionMovimientos.id_cuenta_hacia, 
            RelacionMovimientos.id_moneda_hacia
        )
        
        # Consulta SUM_HACIA_ULTIMO sobre la tabla RELACION_MOVIMIENTOS
        sum_hacia_ultimo_query = RelacionMovimientos.query.filter(
            RelacionMovimientos.fecha <= ultimo_dia_mes_anterior
        ).with_entities(
            RelacionMovimientos.id_cuenta_hacia, 
            RelacionMovimientos.id_empresa,
            RelacionMovimientos.id_moneda_hacia, 
            func.sum(RelacionMovimientos.valor_hacia_calculado).label("suma_valor_hacia_ultimo")
        ).group_by(
            RelacionMovimientos.id_empresa, 
            RelacionMovimientos.id_cuenta_hacia, 
            RelacionMovimientos.id_moneda_hacia
        )    

        # Unir CUENTAS con SUM_DESDE y SUM_HACIA
        sum_desde_primero_alias = aliased(sum_desde_primero_query.subquery())
        sum_hacia_primero_alias = aliased(sum_hacia_primero_query.subquery())
        sum_desde_ultimo_alias = aliased(sum_desde_ultimo_query.subquery())
        sum_hacia_ultimo_alias = aliased(sum_hacia_ultimo_query.subquery())

        integrated_table_query = cuentas_query.outerjoin(
            sum_desde_primero_alias, and_(
                Cuentas.id_cuenta == sum_desde_primero_alias.c.id_cuenta_desde,
                Cuentas.id_empresa == sum_desde_primero_alias.c.id_empresa,
                Cuentas.id_moneda == sum_desde_primero_alias.c.id_moneda_desde
            )
        ).outerjoin(
            sum_hacia_primero_alias, and_(
                Cuentas.id_cuenta == sum_hacia_primero_alias.c.id_cuenta_hacia,
                Cuentas.id_empresa == sum_hacia_primero_alias.c.id_empresa,
                Cuentas.id_moneda == sum_hacia_primero_alias.c.id_moneda_hacia
            )
        ).with_entities(
            Cuentas.id_cuenta, 
            Cuentas.id_empresa, 
            Cuentas.id_moneda,
            sum_desde_primero_alias.c.suma_valor_desde_primero, 
            sum_hacia_primero_alias.c.suma_valor_hacia_primero,
            Cuentas.id_contrato
        )

        integrated_table_query = integrated_table_query.outerjoin(
            sum_desde_ultimo_alias, and_(
                Cuentas.id_cuenta == sum_desde_ultimo_alias.c.id_cuenta_desde,
                Cuentas.id_empresa == sum_desde_ultimo_alias.c.id_empresa,
                Cuentas.id_moneda == sum_desde_ultimo_alias.c.id_moneda_desde
            )
        ).outerjoin(
            sum_hacia_ultimo_alias, and_(
                Cuentas.id_cuenta == sum_hacia_ultimo_alias.c.id_cuenta_hacia,
                Cuentas.id_empresa == sum_hacia_ultimo_alias.c.id_empresa,
                Cuentas.id_moneda == sum_hacia_ultimo_alias.c.id_moneda_hacia
            )
        ).with_entities(
            Cuentas.id_cuenta, 
            Cuentas.id_empresa, 
            Cuentas.id_moneda,
            sum_desde_primero_alias.c.suma_valor_desde_primero, 
            sum_hacia_primero_alias.c.suma_valor_hacia_primero,
            sum_desde_ultimo_alias.c.suma_valor_desde_ultimo, 
            sum_hacia_ultimo_alias.c.suma_valor_hacia_ultimo,
            Cuentas.id_contrato
        )

        contrato_join_query = integrated_table_query.outerjoin(
            Contrato,
            and_(
                Cuentas.id_contrato == Contrato.id_contrato,
                Cuentas.id_empresa == Contrato.id_empresa,
                Cuentas.id_moneda == Contrato.id_moneda
            )
        ).join(Proyecto).filter(Proyecto.fecha_fin_obra >= fecha_actual).with_entities(
            Cuentas.id_cuenta,
            Cuentas.id_empresa,
            Cuentas.id_moneda,
            sum_desde_primero_alias.c.suma_valor_desde_primero,
            sum_hacia_primero_alias.c.suma_valor_hacia_primero,
            sum_desde_ultimo_alias.c.suma_valor_desde_ultimo, 
            sum_hacia_ultimo_alias.c.suma_valor_hacia_ultimo,
            Cuentas.id_contrato,
            Contrato.inversor_o_prestamista_o_deudor,
            Contrato.tasa_anual,
            Contrato.tasa_anual_RE,
            Contrato.aplica_CAC_T_F,
            Contrato.monto_contrato
        )
        
        # Ejecutar la consulta y obtener resultados
        resultados_integrados = contrato_join_query.all()
        
        # Calcular rentas
        rentas = calcular_rentas(resultados_integrados)
    
        # Crear un DataFrame con los resultados
        df = pd.DataFrame(contrato_join_query, columns=[
            'id_cuenta', 
            'id_empresa', 
            'id_moneda', 
            'suma_valor_desde_p', 
            'suma_valor_hacia_p',
            'suma_valor_desde_u', 
            'suma_valor_hacia_u', 
            'id_contrato',
            'inversor_o_prestamista_o_deudor',
            'tasa_anual', 
            'tasa_anual_RE', 
            'aplica_CAC_T_F', 
            'monto_contrato'
        ])

        # Agregar columna de renta calculada
        df['renta'] = rentas

        # Crear movimientos y cargarlos en la base de datos
        for index, row in df.iterrows():
            if row['inversor_o_prestamista_o_deudor'] == 'Inversor':
                id_concepto = 12
                nombre_cuenta = "Renta Espera General"
                id_empresa = row['id_empresa']
                id_moneda = row['id_moneda']
                
                # Obtener id_cuenta_hacia
                id_cuenta_hacia = generar_id_cuenta_hacia(id_concepto, id_empresa, id_moneda, nombre_cuenta)
                
                # Crear un nuevo movimiento
                movimiento = RelacionMovimientos(
                    id_usuario=1,
                    fecha=datetime.now(),  # La fecha del movimiento
                    id_empresa=id_empresa,
                    id_moneda_desde=id_moneda,
                    id_moneda_hacia=id_moneda,
                    tipo_de_cambio=1.0,
                    valor_desde=row['renta'],  # La renta calculada
                    valor_hacia_calculado=row['renta'],  # La renta calculada
                    descripcion="Renta espera cargada de manera automática",
                    id_concepto_desde=10,
                    id_concepto_hacia=12,
                    id_cuenta_desde=row['id_cuenta'],
                    id_cuenta_hacia=id_cuenta_hacia if id_cuenta_hacia is not None else 1  # Renta Espera General predeterminado
                )
                
                # Añadir el movimiento a la sesión
                session.add(movimiento)
        
        # Commit de los cambios a la base de datos
        session.commit()
        
        # Cerrar la sesión
        session.close()
        
        return "Calculo realizado"
    except Exception as e:
        return f"Error al consultar las cuentas de inversores: {e}"

# Puedes definir más funciones para realizar otras consultas
def calcular_rentas(resultados_integrados):
    rentas = []
    for resultado in resultados_integrados:
        # id_contrato = resultado.id_contrato
        inversor_prestamista_o_deudor = resultado.inversor_o_prestamista_o_deudor
        sum_desde_primero = resultado.suma_valor_desde_primero if resultado.suma_valor_desde_primero is not None else 0
        sum_desde_ultimo = resultado.suma_valor_desde_ultimo if resultado.suma_valor_desde_ultimo is not None else 0
        sum_hacia_primero = resultado.suma_valor_hacia_primero if resultado.suma_valor_hacia_primero is not None else 0
        sum_hacia_ultimo = resultado.suma_valor_hacia_ultimo if resultado.suma_valor_hacia_ultimo is not None else 0
        tasa_anual = resultado.tasa_anual
        tasa_anual_RE = resultado.tasa_anual_RE
        monto_contrato = resultado.monto_contrato

        if inversor_prestamista_o_deudor == "Inversor":
            if sum_desde_primero - sum_hacia_primero >= monto_contrato and \
                sum_desde_ultimo - sum_hacia_ultimo >= monto_contrato:
                renta = monto_contrato * ((tasa_anual/12)) + \
                        (sum_desde_ultimo - sum_hacia_ultimo - monto_contrato) * ((tasa_anual_RE/12))
                
            else:
                renta = 0

        rentas.append(renta)

    return rentas