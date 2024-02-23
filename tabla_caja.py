import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from Models import *

# Importa la instancia de la aplicación Flask


def obtener_reportes(conceptos):
    consulta_original = db.session.query(
        Cuentas.id_cuenta,
        Cuentas.id_empresa,
        Empresa.nombre_empresa,
        Cuentas.id_moneda,
        Moneda.descr_moneda,
        Cuentas.nombre_cuenta
    ).filter(
        Cuentas.id_concepto.in_(conceptos)
    ).join(
        Empresa, Cuentas.id_empresa == Empresa.id_empresa
    ).join(
        Moneda, Cuentas.id_moneda == Moneda.id_moneda
    ).all()

    tabla_suma_desde = db.session.query(
        RelacionMovimientos.id_cuenta_desde,
        func.sum(RelacionMovimientos.valor_desde).label('total_valor_desde')
    ).filter(
        RelacionMovimientos.id_concepto_desde.in_(conceptos)
    ).group_by(
        RelacionMovimientos.id_cuenta_desde
    ).all()

    tabla_suma_hacia = db.session.query(
        RelacionMovimientos.id_cuenta_hacia,
        func.sum(RelacionMovimientos.valor_hacia_calculado).label('total_valor_hacia')
    ).filter(
        RelacionMovimientos.id_concepto_hacia.in_(conceptos)
    ).group_by(
        RelacionMovimientos.id_cuenta_hacia
    ).all()

    df_consulta_original = pd.DataFrame(consulta_original, columns=[
        'id_cuenta', 'id_empresa', 'nombre_empresa', 'id_moneda', 'descr_moneda', 'nombre_cuenta'
    ])

    df_tabla_suma_desde = pd.DataFrame(tabla_suma_desde, columns=['id_cuenta_desde', 'total_valor_desde'])
    df_tabla_suma_hacia = pd.DataFrame(tabla_suma_hacia, columns=['id_cuenta_hacia', 'total_valor_hacia'])
    
    df_merged = df_consulta_original.merge(df_tabla_suma_desde, how='left', left_on='id_cuenta', right_on='id_cuenta_desde')
    df_merged = df_merged.merge(df_tabla_suma_hacia, how='left', left_on='id_cuenta', right_on='id_cuenta_hacia')

    df_merged.loc[:, 'total_valor_hacia'] = df_merged['total_valor_hacia'].fillna(0)
    df_merged.loc[:, 'total_valor_desde'] = df_merged['total_valor_desde'].fillna(0)
    
    df_merged['diferencia'] = df_merged['total_valor_hacia'] - df_merged['total_valor_desde']

    df_merged['total_valor_hacia'] = df_merged['total_valor_hacia'].apply(lambda x: '{:,.0f}'.format(x))
    df_merged['total_valor_desde'] = df_merged['total_valor_desde'].apply(lambda x: '{:,.0f}'.format(x))
    df_merged['diferencia'] = df_merged['diferencia'].apply(lambda x: '{:,.0f}'.format(x))
    
    df_merged.drop(['id_cuenta_desde', 'id_cuenta_hacia'], axis=1, inplace=True)

    datos_peso = df_merged[df_merged['descr_moneda'] == 'Peso'].to_dict(orient='records')
    datos_euro = df_merged[df_merged['descr_moneda'] == 'Euro'].to_dict(orient='records')
    datos_dolar = df_merged[df_merged['descr_moneda'] == 'Dolar'].to_dict(orient='records')

    return datos_peso, datos_euro, datos_dolar
