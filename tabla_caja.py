import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, case
from sqlalchemy.orm import aliased, sessionmaker
from Models import *
from sqlalchemy import create_engine


def obtener_reportes(conceptos):
    # Aliases for the tables involved
    cuenta_hacia = aliased(Cuentas)
    cuenta_desde = aliased(Cuentas)

    # Building the base query
    base_query = db.session.query(
        Cuentas.id_cuenta,
        Concepto.nombre_concepto,
        Cuentas.nombre_cuenta,
        Empresa.nombre_empresa,
        Moneda.descr_moneda,
        func.coalesce( 
            func.sum(
                case(
                    (RelacionMovimientos.id_cuenta_hacia == Cuentas.id_cuenta, RelacionMovimientos.valor_hacia_calculado),
                    else_=0
                )
                - case(
                    (RelacionMovimientos.id_cuenta_desde == Cuentas.id_cuenta, RelacionMovimientos.valor_desde),
                    else_=0
                )
            ), 0
        ).label('saldo')
    ).join(
        Empresa, Cuentas.id_empresa == Empresa.id_empresa
    ).join(
        Concepto, Cuentas.id_concepto == Concepto.id_concepto
    ).join(
        Moneda, Cuentas.id_moneda == Moneda.id_moneda
    ).outerjoin(
        RelacionMovimientos, (RelacionMovimientos.id_cuenta_hacia == Cuentas.id_cuenta) | (RelacionMovimientos.id_cuenta_desde == Cuentas.id_cuenta)
    ).filter(
        Cuentas.id_concepto.in_(conceptos)
    ).group_by(
        Cuentas.id_cuenta,
        Concepto.nombre_concepto,
        Cuentas.nombre_cuenta,
        Empresa.nombre_empresa,
        Moneda.descr_moneda
    )

    # Execute the base query and fetch all results
    results = base_query.all()
    
    # Convert results to a DataFrame
    df = pd.DataFrame(results, columns=['id_cuenta', 
                                        'nombre_concepto',
                                        'nombre_cuenta',
                                        'nombre_empresa', 
                                        'descr_moneda', 
                                        'saldo'])
    # Redondear el saldo a 2 decimales
    df['saldo'] = df['saldo'].round(2)
    
    datos_peso = df[df['descr_moneda'] == 'Peso']
    datos_euro = df[df['descr_moneda'] == 'Euro']
    datos_dolar = df[df['descr_moneda'] == 'Dolar']
    # print("Datos Peso:")
    # print(datos_peso)

    # print("Datos Euro:")
    # print(datos_euro)

    # print("Datos Dolar:")
    # print(datos_dolar)
    # Convertir DataFrame a lista de diccionarios
    datos_peso = datos_peso.to_dict(orient='records')
    datos_euro = datos_euro.to_dict(orient='records')
    datos_dolar = datos_dolar.to_dict(orient='records')
    
    return datos_peso, datos_euro, datos_dolar

def obtener_reportes_agentes(conceptos):
    # Aliases for the tables involved
    cuenta_hacia = aliased(Cuentas)
    cuenta_desde = aliased(Cuentas)

    # Building the base query
    base_query = db.session.query(
        Cuentas.id_cuenta,
        Contrato.id_contrato,
        Concepto.nombre_concepto,
        Cuentas.nombre_cuenta,
        Empresa.nombre_empresa,
        Moneda.descr_moneda,
        func.coalesce( 
            func.sum(
                case(
                    (RelacionMovimientos.id_cuenta_hacia == Cuentas.id_cuenta, RelacionMovimientos.valor_hacia_calculado),
                    else_=0
                )
                - case(
                    (RelacionMovimientos.id_cuenta_desde == Cuentas.id_cuenta, RelacionMovimientos.valor_desde),
                    else_=0
                )
            ), 0
        ).label('saldo')
    ).join(
        Empresa, Cuentas.id_empresa == Empresa.id_empresa
    ).join(
        Concepto, Cuentas.id_concepto == Concepto.id_concepto
    ).join(
        Moneda, Cuentas.id_moneda == Moneda.id_moneda
    ).join(
        Contrato, Cuentas.id_contrato == Contrato.id_contrato
    ).outerjoin(
        RelacionMovimientos, (RelacionMovimientos.id_cuenta_hacia == Cuentas.id_cuenta) | (RelacionMovimientos.id_cuenta_desde == Cuentas.id_cuenta)
    ).filter(
        Cuentas.id_concepto.in_(conceptos)
    ).filter(
        Cuentas.tipo_cta == 'B'
    ).group_by(
        Cuentas.id_cuenta,
        Concepto.nombre_concepto,
        Cuentas.nombre_cuenta,
        Empresa.nombre_empresa,
        Moneda.descr_moneda,
    )

    # Execute the base query and fetch all results
    results = base_query.all()
    
    # Convert results to a DataFrame
    df = pd.DataFrame(results, columns=['id_cuenta',
                                        'id_contrato', 
                                        'nombre_concepto',
                                        'nombre_cuenta',
                                        'nombre_empresa', 
                                        'descr_moneda', 
                                        'saldo'])
    
    # Obtener el monto del contrato y restarlo al saldo
    contratos = {contrato.id_contrato: contrato.monto_contrato for contrato in db.session.query(Contrato).all()}
    df['saldo'] = df.apply(lambda row: row['saldo'] + contratos.get(row['id_contrato'], 0), axis=1)
    
    # Condición para establecer el saldo como cero si la suma es positiva
    df.loc[df['saldo'] > 0, 'saldo'] = 0
    
    # Redondear el saldo a 2 decimales
    df['saldo'] = df['saldo'].round(2)
    
    datos_peso = df[df['descr_moneda'] == 'Peso']
    datos_euro = df[df['descr_moneda'] == 'Euro']
    datos_dolar = df[df['descr_moneda'] == 'Dolar']
    # print("Datos Peso:")
    # print(datos_peso)

    # print("Datos Euro:")
    # print(datos_euro)

    # print("Datos Dolar:")
    # print(datos_dolar)
    # Convertir DataFrame a lista de diccionarios
    datos_peso = datos_peso.to_dict(orient='records')
    datos_euro = datos_euro.to_dict(orient='records')
    datos_dolar = datos_dolar.to_dict(orient='records')
    
    return datos_peso, datos_euro, datos_dolar