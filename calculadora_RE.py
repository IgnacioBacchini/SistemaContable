from sqlalchemy import create_engine, func
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker, aliased
from Models import *
from datetime import datetime, timedelta
import pandas as pd


# Configura la conexión a la base de datos
engine = create_engine('sqlite:///C:\\Users\\ignac\\Desktop\\Argenway\\SistemaContable\\database\\SistemaPRU.db')
#engine = create_engine('sqlite:///C:\\Roberto\\Argenway\\240120 aplicacion\\SistemaContable2\\SistemaContable\\database\\SistemaPRU.db')
#engine = create_engine('sqlite:////home/sanchez/SistemaContable/database/SistemaPRU.db')

Session = sessionmaker(bind=engine)

def consultar_cuentas_inversores():
    # Función para consultar las cuentas de inversores
    try:
        # Creamos una sesión
        session = Session()
        # Consulta de cuentas de inversores
        # Obtener la fecha actual sin la hora
        fecha_actual = datetime.now().date()

        # Calcular la fecha del primer día del mes anterior
        ultimo_dia_mes_anterior = fecha_actual.replace(day=1) - timedelta(days=1)
        primer_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)

        # Verificar la fecha obtenida
        print("Primer día del mes anterior:", primer_dia_mes_anterior)
        print("Ultimo día del mes anterior:", ultimo_dia_mes_anterior)
        
        cuentas_query = Cuentas.query.filter(
            Cuentas.inversor_prestamista_deudor_T_F == True,
            Cuentas.tipo_cta == 'B'
        ).with_entities(
            Cuentas.id_cuenta, 
            Cuentas.id_empresa, 
            Cuentas.id_moneda, 
            Cuentas.id_contrato
        )
        # print("Resultados de la consulta 1:")
        # for resultado in cuentas_query:
        #     print(resultado)
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
        
        # print("Resultados de la consulta 2:")
        # for resultado in sum_desde_primero_query:
        #     print(resultado)
        
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

        # print("Resultados de la consulta 3:")
        # for resultado in sum_hacia_primero_query:
        #     print(resultado)
        
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
        
        # print("Resultados de la consulta 4:")
        # for resultado in integrated_table_query:
        #     print(resultado)
            
        contrato_join_query = integrated_table_query.outerjoin(
            Contrato,
            and_(
                Cuentas.id_contrato == Contrato.id_contrato,
                Cuentas.id_empresa == Contrato.id_empresa,
                Cuentas.id_moneda == Contrato.id_moneda
            )
        ).with_entities(
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
            Contrato.aplica_CAC_T_F,
            Contrato.monto_contrato
        )
        print("Resultados de la consulta 5:")
        for resultado in contrato_join_query:
            print(resultado)
        # Ejecutar las consultas
        # resultados_cuentas = cuentas_query.all()
        resultados_integrados = contrato_join_query.all()
        
        # Calcular rentas
        rentas = calcular_rentas(resultados_integrados)
    
        df = pd.DataFrame(contrato_join_query, columns=[
            'id_cuenta', 
            'id_empresa', 
            'id_moneda', 
            'suma_valor_desde_u', 
            'suma_valor_hacia_u',
            'suma_valor_desde_p', 
            'suma_valor_hacia_p',
            'id_contrato', 
            'inversor_o_prestamista_o_deudor', 
            'tasa_anual', 
            'aplica_CAC_T_F',
            'monto_contrato'
        ])
        # Convertir la columna 'aplica_CAC_T_F' a tipo booleano
        df['aplica_CAC_T_F'] = df['aplica_CAC_T_F'].astype(bool)

        # Convertir la columna 'inversor_o_prestamista_o_deudor' a tipo cadena
        df['inversor_o_prestamista_o_deudor'] = df['inversor_o_prestamista_o_deudor'].astype(str)
        
        # Agrega la columna de rentas al DataFrame
        df['renta'] = rentas
        
        # df = df.dropna(subset=['tasa_anual'])
        print(df)
        # Iterar sobre cada fila del DataFrame
        for index, row in df.iterrows():
            movimiento = RelacionMovimientos(
                id_usuario=1,
                fecha=datetime.now(),  # La fecha del movimiento
                id_empresa=row['id_empresa'],
                id_moneda_desde=row['id_moneda'],
                id_moneda_hacia=row['id_moneda'],
                tipo_de_cambio=1.0,
                valor_desde=row['renta'],  # La renta calculada
                valor_hacia_calculado=row['renta'],  # La renta calculada
                descripcion="Renta espera cargada de manera automática"
            )

            # Dependiendo del tipo de inversor, prestamista o deudor
            if row['inversor_o_prestamista_o_deudor'] == 'Inversor':
                movimiento.id_concepto_desde = 10
                movimiento.id_concepto_hacia = 12
                movimiento.id_cuenta_desde = row['id_cuenta']
                movimiento.id_cuenta_hacia = 1 #Renta Espera General
            elif row['inversor_o_prestamista_o_deudor'] == 'Prestamista':
                movimiento.id_concepto_desde = 15
                movimiento.id_concepto_hacia = 16
                movimiento.id_cuenta_desde = row['id_cuenta']
                movimiento.id_cuenta_hacia = 2 #Intereses por Prestamos Recibidos
            elif row['inversor_o_prestamista_o_deudor'] == 'Deudor':
                movimiento.id_concepto_desde = 18
                movimiento.id_concepto_hacia = 17
                movimiento.id_cuenta_desde = 3 #Intereses por prestamos brindados
                movimiento.id_cuenta_hacia = row['id_cuenta']
            
            # Añadir el movimiento a la sesión
            session.add(movimiento)
        
        # Commit de los cambios a la base de datos
        session.commit()
        
        # Cerramos la sesión
        session.close()

        return "Calculo realizado"
    except Exception as e:
        print(f"Error al consultar las cuentas de inversores: {e}")
        return None

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
        monto_contrato = resultado.monto_contrato

        if inversor_prestamista_o_deudor == "Inversor":
            if sum_desde_primero - sum_hacia_primero >= monto_contrato and \
                sum_desde_ultimo - sum_hacia_ultimo >= monto_contrato:
                renta = (sum_desde_ultimo - sum_hacia_ultimo) * ((1 + tasa_anual) ** (1/12) - 1)
            else:
                renta = 0
        elif inversor_prestamista_o_deudor == "Prestamista":
            if sum_desde_ultimo - sum_hacia_ultimo <= sum_desde_primero - sum_hacia_primero:
                renta = (sum_desde_ultimo - sum_hacia_ultimo) * ((1 + tasa_anual) ** (1/12) - 1)
            else:
                renta = (sum_desde_primero - sum_hacia_primero) * ((1 + tasa_anual) ** (1/12) - 1)
        elif inversor_prestamista_o_deudor == "Deudor":
            if sum_hacia_ultimo - sum_desde_ultimo <= sum_hacia_primero - sum_desde_primero:
                renta = (sum_hacia_ultimo - sum_desde_ultimo) * ((1 + tasa_anual) ** (1/12) - 1)
            else:
                renta = (sum_hacia_primero - sum_desde_primero) * ((1 + tasa_anual) ** (1/12) - 1)
        else:
            renta = None

        rentas.append(renta)

    return rentas