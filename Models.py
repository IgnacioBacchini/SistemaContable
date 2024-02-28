from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from flask import Flask

db = SQLAlchemy()

class Empresa(db.Model):
    id_empresa = db.Column(db.Integer, unique=True, primary_key=True)
    nombre_empresa = db.Column(db.Text, unique=True)
    
    def serialize(self):
        return {
            'id_empresa': self.id_empresa,
            'nombre_empresa': self.nombre_empresa
        }

class Moneda(db.Model):
    id_moneda = db.Column(db.Integer, unique=True, primary_key=True)
    descr_moneda = db.Column(db.Text, unique=True)
    
    def serialize(self):
        return {
            'id_moneda': self.id_moneda,
            'descr_moneda': self.descr_moneda
        }

class Usuario(db.Model, UserMixin):
    id_usuario = db.Column(db.Integer, unique=True, primary_key=True)
    nombre_usuario = db.Column(db.Text)
    mail_usuario = db.Column(db.Text)
    contrasenia_usuario = db.Column(db.Text)
    
    def get_id(self):
        return str(self.id)
    
    def serialize(self):
        return {
            'id_usuario': self.id_usuario,
            'nombre_usuario': self.nombre_usuario,
            'mail_usuario': self.mail_usuario,
            'contrasenia_usuario': self.contrasenia_usuario
        }

class Concepto(db.Model):
    id_concepto = db.Column(db.Integer, unique=True, primary_key=True)
    nombre_concepto = db.Column(db.Text, unique=True)
    
    def serialize(self):
        return {
            'id_concepto': self.id_concepto,
            'nombre_concepto': self.nombre_concepto
        }
class Inversor_prestamista_deudor(db.Model):
    id_inversor_prestamista_deudor = db.Column(db.Integer, unique=True, primary_key=True)
    nombre_inversor_prestamista_deudor = db.Column(db.Text)
    inversor_o_prestamista_o_deudor = db.Column(db.Text)
    
    def serialize(self):
        return {
            'id_inversor_prestamista_deudor': self.id_inversor_prestamista_deudor,
            'nombre_inversor_prestamista_deudor': self.nombre_inversor_prestamista_deudor,
            'inversor_o_prestamista_o_deudor': self.inversor_o_prestamista_o_deudor
        }

class Proyecto(db.Model):
    id_proyecto = db.Column(db.Integer, unique=True, primary_key=True)
    nombre_proyecto = db.Column(db.Text)
    fecha_fin_obra = db.Column(db.Date)
    
    def serialize(self):
        return {
            'id_proyecto': self.id_proyecto,
            'nombre_proyecto': self.nombre_proyecto,
            'fecha_fin_obra': self.fecha_fin_obra,
        }

class Contrato(db.Model):
    id_contrato = db.Column(db.Integer, unique=True, primary_key=True)
    nombre_contrato = db.Column(db.Text)    
    id_inversor_prestamista_deudor = db.Column(db.Integer, db.ForeignKey('inversor_prestamista_deudor.id_inversor_prestamista_deudor'))
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresa.id_empresa'))
    id_proyecto = db.Column(db.Integer, db.ForeignKey('proyecto.id_proyecto'))
    id_moneda = db.Column(db.Integer, db.ForeignKey('moneda.id_moneda'))
    inversor_o_prestamista_o_deudor = db.Column(db.Text)
    tasa_anual = db.Column(db.Float)
    aplica_CAC_T_F = db.Column(db.Boolean)
    monto_contrato = db.Column(db.Float)
    
    # Define las relaciones
    inversor_prestamista_deudor = db.relationship('Inversor_prestamista_deudor', foreign_keys=[id_inversor_prestamista_deudor])
    empresa = db.relationship('Empresa', foreign_keys=[id_empresa])
    moneda = db.relationship('Moneda', foreign_keys=[id_moneda])
    proyecto = db.relationship('Proyecto',foreign_keys=[id_proyecto])
    
    def serialize(self):
        return {
            'id_contrato': self.id_contrato,
            'nombre_contrato': self.nombre_contrato,
            'id_inversor_prestamista_deudor': self.id_inversor_prestamista_deudor,
            'id_empresa': self.id_empresa,
            'id_proyecto': self.id_proyecto,
            'id_moneda': self.id_moneda,
            'inversor_o_prestamista_o_deudor': self.inversor_o_prestamista_o_deudor,
            'tasa_anual': self.tasa_anual,
            'aplica_CAC_T_F': self.aplica_CAC_T_F,
            'monto_contrato': self.monto_contrato,
        }

class Cuentas(db.Model):
    id_cuenta = db.Column(db.Integer, primary_key=True)
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresa.id_empresa'))
    id_concepto = db.Column(db.Integer, db.ForeignKey('concepto.id_concepto'))
    id_moneda = db.Column(db.Integer, db.ForeignKey('moneda.id_moneda'))
    nombre_cuenta = db.Column(db.Text)
    inversor_prestamista_deudor_T_F = db.Column(db.Boolean)
    id_inversor_prestamista_deudor = db.Column(db.Integer, db.ForeignKey('inversor_prestamista_deudor.id_inversor_prestamista_deudor'))
    tipo_cta = db.Column(db.Text)
    id_contrato = db.Column(db.Integer, db.ForeignKey('contrato.id_contrato'))

    # Define las relaciones
    empresa = db.relationship('Empresa', foreign_keys=[id_empresa])
    concepto = db.relationship('Concepto', foreign_keys=[id_concepto])
    moneda = db.relationship('Moneda', foreign_keys=[id_moneda])
    inversor_prestamista_deudor = db.relationship('Inversor_prestamista_deudor', foreign_keys=[id_inversor_prestamista_deudor])
    contrato = db.relationship('Contrato', foreign_keys=[id_contrato])
    
    def serialize(self):
        return {
            'id_cuenta': self.id_cuenta,
            'id_empresa': self.id_empresa,
            'id_concepto': self.id_concepto,
            'id_moneda': self.id_moneda,
            'nombre_cuenta': self.nombre_cuenta,
            'inversor_prestamista_deudor_T_F': self.inversor_prestamista_deudor_T_F,
            'id_inversor_prestamista_deudor': self.id_inversor_prestamista_deudor,
            'tipo_cta': self.tipo_cta,
            'id_contrato': self.id_contrato
        }

class RelacionMovimientos(db.Model):
    id_movimiento = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    fecha = db.Column(db.Date)
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresa.id_empresa'))
    id_moneda_hacia = db.Column(db.Integer, db.ForeignKey('moneda.id_moneda'))
    id_moneda_desde = db.Column(db.Integer, db.ForeignKey('moneda.id_moneda'))
    id_concepto_hacia = db.Column(db.Integer, db.ForeignKey('concepto.id_concepto'))
    id_concepto_desde = db.Column(db.Integer, db.ForeignKey('concepto.id_concepto'))
    id_cuenta_hacia = db.Column(db.Integer, db.ForeignKey('cuentas.id_cuenta'))
    id_cuenta_desde = db.Column(db.Integer, db.ForeignKey('cuentas.id_cuenta'))
    tipo_de_cambio = db.Column(db.Float)
    valor_desde = db.Column(db.Float)
    valor_hacia_calculado = db.Column(db.Float)
    descripcion = db.Column(db.Text)
    
    # Define las relaciones
    usuario = db.relationship('Usuario', foreign_keys=[id_usuario])
    empresa = db.relationship('Empresa', foreign_keys=[id_empresa])
    moneda_hacia = db.relationship('Moneda', foreign_keys=[id_moneda_hacia])
    moneda_desde = db.relationship('Moneda', foreign_keys=[id_moneda_desde])
    concepto_hacia = db.relationship('Concepto', foreign_keys=[id_concepto_hacia])
    concepto_desde = db.relationship('Concepto', foreign_keys=[id_concepto_desde])
    cuenta_hacia = db.relationship('Cuentas', foreign_keys=[id_cuenta_hacia])
    cuenta_desde = db.relationship('Cuentas', foreign_keys=[id_cuenta_desde])

    def serialize(self):
        return {
            'id_movimiento': self.id_movimiento,
            'fecha': self.fecha,
            'id_empresa': self.id_empresa,
            'id_moneda_hacia': self.id_moneda_hacia,
            'id_moneda_desde': self.id_moneda_desde,
            'id_concepto_hacia': self.id_concepto_hacia,
            'id_concepto_desde': self.id_concepto_desde,
            'id_cuenta_hacia': self.id_cuenta_hacia,
            'id_cuenta_desde': self.id_cuenta_desde,
            'tipo_de_cambio': self.tipo_de_cambio,
            'valor_desde': self.valor_desde,
            'valor_hacia_calculado': self.valor_hacia_calculado,
            'descripcion': self.descripcion,
        }
    
class Indice_cac(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uno_mes_anio = db.Column(db.Date)
    indice = db.Column(db.Float)

    def serialize(self):
        return {
            'id': self.id,
            'uno_mes_anio': self.uno_mes_anio,
            'indice': self.indice
        }

