from flask import Flask, jsonify, request, render_template, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logging import exception
from datetime import date, datetime
# Importa tus modelos SQLAlchemy
from Models import *
from tabla_caja import obtener_resultados_tabla_caja

# Configuración de la aplicación Flask
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:\\Users\\ignac\\Desktop\\Argenway\\SistemaContable\\database\\SistemaPRU.db"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:\\Roberto\\Argenway\\240120 aplicacion\\SistemaContable\\database\\SistemaPRU.db"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/sanchez/SistemaContable/database/SistemaPRU.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Corregido: "SQLALCHEMY_TRACK_MODIFICATIONES"
db.init_app(app)

# Ordeno las tablas
tablas_ordenadas = [Empresa, Moneda, Usuario, Concepto, Inversor_prestamista_deudor, Cuentas]
tablas_ordenadas = sorted(tablas_ordenadas, key=lambda tabla: tabla.__tablename__)

#Calculo RENTA ESPERA
from calculadora_RE import *

# Aquí empiezan las rutas

@app.route("/index", methods=["GET", "POST"])
def home():
    return render_template("index.html")

def pagina_no_encontrada(error):
    return "<h1>La página que intentas buscar no existe...</h1>"

@app.route("/api/base")
def show_main():
    return render_template("base.html")

@app.route("/api/inversor")
def show_inversor():
    return render_template("inversor.html")

@app.route("/api/saldo")
def show_saldos():
    return render_template("saldo.html")

@app.route("/api/showmovement")
def show_movement():
    movimientos = RelacionMovimientos.query.all()
    # Renderiza los resultados en una plantilla HTML
    return render_template('showmovement.html', movimientos=movimientos)


@app.route("/api/caja")
def show_caja():
    # Llama a la función para obtener los resultados de las tres consultas
    datos_peso, datos_euro, datos_dolar = obtener_resultados_tabla_caja()
    # Renderiza los resultados en una plantilla HTML
    return render_template('caja.html',datos_peso=datos_peso, datos_euro=datos_euro, datos_dolar=datos_dolar)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        contrasenia = request.form['contrasenia']
        
        # Consultar la base de datos para verificar las credenciales
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario, contrasenia_usuario=contrasenia).first()
        
        if usuario:
            # Autenticación exitosa, redirigir al usuario a la página principal
            return redirect(url_for('home'))
        else:
            # Si las credenciales son incorrectas, muestra un mensaje de error
            error = 'Nombre de usuario o contraseña incorrectos. Inténtalo de nuevo.'

    # Si es un GET request, renderiza la página de inicio de sesión
    return render_template('login.html', error=error)

@app.route("/api/rent", methods=["GET", "POST"])
def calcular_renta():
    if request.method == "POST":
        try:
            # Realizar la consulta SQL sobre la tabla CUENTAS
            resultado = consultar_cuentas_inversores()  # Por ejemplo, la cantidad de cuentas obtenidas
            return render_template("resultado_renta.html", resultado=resultado)
        except Exception as e:
            print(f"\n[SERVER]: Error en la ruta /api/rent. Log: {str(e)}\n")
            return jsonify({"error": "¡Algo salió mal al realizar la consulta!"}), 500
    else:
        # Aquí se muestra el formulario para ingresar los datos
        return render_template("rent.html")


#----Muestro el formulario para agregar CAC----#
@app.route("/api/addcac")
def show_cac():
    opciones_cac = sorted(Indice_cac.query.all(), key=lambda cac: cac.indice)
    return render_template("addcac.html",opciones_cac=opciones_cac)

#----Obtengo datos del formulario tasa----#
@app.route("/api/addcac", methods=["POST"])
def add_cac():
    try:
        uno_mes_anio_str = request.form["uno_mes_anio"]
        indice = request.form["indice"]

        uno_mes_anio = datetime.strptime(uno_mes_anio_str, "%Y-%m-%d")
        
        # Crear un nuevo objeto Indice CAC
        nuevo_cac = Indice_cac(
            uno_mes_anio=uno_mes_anio,
            indice=indice        
        )
        db.session.add(nuevo_cac)
        db.session.commit()
        

        return redirect(url_for('show_cac'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addcac. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500

#----Muestro el formulario para agregar movimiento----#
@app.route("/api/addmovement", methods=["GET"])
def show_movement_form():
    opciones_moneda = sorted(Moneda.query.all(), key=lambda moneda: moneda.descr_moneda)
    opciones_empresa = sorted(Empresa.query.all(), key=lambda empresa: empresa.nombre_empresa)
    opciones_concepto = sorted(Concepto.query.all(), key=lambda concepto: concepto.nombre_concepto)
    opciones_cuenta = sorted(Cuentas.query.all(), key=lambda cuenta: cuenta.nombre_cuenta)
    # Obtener la fecha actual
    fecha_actual = date.today().strftime("%Y-%m-%d")
    
    return render_template("movimientos.html",fecha_actual=fecha_actual,opciones_cuenta=opciones_cuenta, opciones_concepto=opciones_concepto, opciones_moneda=opciones_moneda, opciones_empresa=opciones_empresa)

#----Obtengo datos del formulario movimientos----#
@app.route("/api/get_cuentas", methods=["POST"])
def get_cuentas():
    try:
        data = request.get_json()
        id_concepto = data.get("id_concepto")
        id_empresa = data.get("id_empresa")
        id_moneda = data.get("id_moneda")

        # Iniciar la consulta filtrando por concepto
        cuentas_query = Cuentas.query.filter_by(id_concepto=id_concepto)

        # Aplicar filtros adicionales si los parámetros están presentes
        if id_empresa:
            cuentas_query = cuentas_query.filter_by(id_empresa=id_empresa)
        if id_moneda:
            cuentas_query = cuentas_query.filter_by(id_moneda=id_moneda)

        # Obtener el resultado final de la consulta
        cuentas = cuentas_query.all()

        # Serializar y devolver las cuentas en formato JSON
        return jsonify([cuenta.serialize() for cuenta in cuentas]), 200
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/get_cuentas. Log: {str(e)}\n")
        return jsonify({"msg": "Algo ha salido mal"}), 500

@app.route("/api/get_cuentas_hacia", methods=["POST"])
def get_cuentas_hacia():
    try:
        data = request.get_json()
        id_concepto_hacia = data.get("id_concepto_hacia")
        id_empresa_hacia = data.get("id_empresa_hacia")
        id_moneda_hacia = data.get("id_moneda_hacia")

        # Iniciar la consulta filtrando por concepto hacia
        cuentas_hacia_query = Cuentas.query.filter_by(id_concepto=id_concepto_hacia)

        # Aplicar filtros adicionales si los parámetros están presentes
        if id_empresa_hacia:
            cuentas_hacia_query = cuentas_hacia_query.filter_by(id_empresa=id_empresa_hacia)
        if id_moneda_hacia:
            cuentas_hacia_query = cuentas_hacia_query.filter_by(id_moneda=id_moneda_hacia)

        # Obtener el resultado final de la consulta hacia
        cuentas_hacia = cuentas_hacia_query.all()

        # Serializar y devolver las cuentas en formato JSON
        return jsonify([cuenta.serialize() for cuenta in cuentas_hacia]), 200
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/get_cuentas_hacia. Log: {str(e)}\n")
        return jsonify({"msg": "Algo ha salido mal"}), 500

# Modificar la función add_movement para recibir concepto_desde y concepto_hacia
@app.route("/api/addmovement", methods=["POST"])
def add_movement():
    
    try:
        # Obtener los datos del formulario
        fecha_str = request.form["fecha"]
        id_empresa = request.form["id_empresa"]
        tipo_de_cambio = request.form["tipo_de_cambio"]
        id_moneda_desde = request.form["id_moneda_desde"]
        id_concepto_desde = request.form["id_concepto_desde"]
        id_cuenta_desde = request.form["id_cuenta_desde"]
        id_moneda_hacia = request.form["id_moneda_hacia"]
        id_concepto_hacia = request.form["id_concepto_hacia"]
        id_cuenta_hacia = request.form["id_cuenta_hacia"]
        valor_desde = request.form["valor_desde"]
        valor_hacia_calculado = request.form["valor_hacia_calculado"]
        descripcion = request.form["descripcion"]

        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")

        # Crear un nuevo objeto RelacionMovimientos
        nuevo_movimiento = RelacionMovimientos(
            fecha=fecha,
            id_empresa=id_empresa,
            tipo_de_cambio=tipo_de_cambio,
            id_moneda_desde=id_moneda_desde,
            id_concepto_desde=id_concepto_desde,
            id_cuenta_desde=id_cuenta_desde,
            id_moneda_hacia=id_moneda_hacia,
            id_concepto_hacia=id_concepto_hacia,
            id_cuenta_hacia=id_cuenta_hacia,
            valor_desde=valor_desde,
            valor_hacia_calculado=valor_hacia_calculado,
            descripcion=descripcion
        )

        # Agregar el nuevo movimiento a la base de datos
        db.session.add(nuevo_movimiento)
        
        # Confirmar los cambios en la base de datos
        db.session.commit()

        return redirect(url_for('show_movement_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addmovement. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500

#----Muestro el formulario para empresa----#
@app.route("/api/addcompany", methods=["GET"])
def show_company_form():
    opciones_empresa = sorted(Empresa.query.all(), key=lambda empresa: empresa.nombre_empresa)
    return render_template("addcompany.html", opciones_empresa=opciones_empresa)

#----Obtengo datos del formulario para agregar empresa----#
@app.route("/api/addcompany", methods=["POST"])
def add_company():
    try:
        nombre_empresa = request.form["nombre_empresa"]

        # Verificar si la empresa ya existe
        if Empresa.query.filter_by(nombre_empresa=nombre_empresa).first():
            error = "La empresa ya existe"
            return render_template("addcompany.html", empresas=Empresa.query.all(), error=error)        
        
        # Crear un nuevo objeto Empresa
        nueva_empresa = Empresa(nombre_empresa=nombre_empresa)
        db.session.add(nueva_empresa)
        db.session.commit()
        
        # Agregar el nuevo movimiento a la base de datos
        db.session.add(nueva_empresa)
        db.session.commit()

        return redirect(url_for('show_company_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addcompany. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500
    
#----Muestro el formulario para inversor_prestamista_deudor----#
@app.route("/api/addinvestor", methods=["GET"])
def show_investor_form():
    opciones_inversor_prestamista_deudor = sorted(Inversor_prestamista_deudor.query.all(), key=lambda inversor_prestamista_deudor: inversor_prestamista_deudor.nombre_inversor_prestamista_deudor)
    return render_template("addinvestor.html", opciones_inversor_prestamista_deudor=opciones_inversor_prestamista_deudor)

#----Obtengo datos del formulario para agregar inversor_prestamista_deudor----#
@app.route("/api/addinvestor", methods=["POST"])
def add_investor():
    try:
        nombre_inversor_prestamista_deudor = request.form["nombre_inversor_prestamista_deudor"]
        inversor_o_prestamista_o_deudor = request.form["inversor_o_prestamista_o_deudor"]
        
        # Verificar si el inversor_prestamista_deudor ya existe
        if Inversor_prestamista_deudor.query.filter_by(nombre_inversor_prestamista_deudor=nombre_inversor_prestamista_deudor).first():
            error = "El inversor_prestamista_deudor ya existe"
            return render_template("addinvestor.html", inversor_prestamista_deudor=Inversor_prestamista_deudor.query.all(), error=error)        
        
        # Crear un nuevo objeto inversor_prestamista_deudor
        nuevo_inversor_prestamista_deudor = Inversor_prestamista_deudor(
            nombre_inversor_prestamista_deudor=nombre_inversor_prestamista_deudor,
            inversor_o_prestamista_o_deudor=inversor_o_prestamista_o_deudor
            )
        db.session.add(nuevo_inversor_prestamista_deudor)
        db.session.commit()
        
        return redirect(url_for('show_investor_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addinvestor. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500

#----Muestro el formulario para proyecto----#
@app.route("/api/addproyect", methods=["GET"])
def show_proyect_form():
    opciones_proyecto = sorted(Proyecto.query.all(), key=lambda proyecto: proyecto.nombre_proyecto)
    return render_template("addproyect.html", opciones_proyecto=opciones_proyecto)

#----Obtengo datos del formulario para agregar proyecto----#
@app.route("/api/addproyect", methods=["POST"])
def add_proyect():
    try:
        nombre_proyecto = request.form["nombre_proyecto"]
        fecha_fin_obra_str = request.form["fecha_fin_obra"]        
                
        fecha_fin_obra = datetime.strptime(fecha_fin_obra_str, "%Y-%m-%d")

    
        # Verificar si el proyecto ya existe
        if Proyecto.query.filter_by(nombre_proyecto=nombre_proyecto).first():
            error = "El proyecto ya existe"
            return render_template("addproyect.html", nombre_proyecto=Proyecto.query.all(), error=error)        
        
        # Crear un nuevo objeto proyecto
        nuevo_proyecto = Proyecto(
            nombre_proyecto=nombre_proyecto,
            fecha_fin_obra=fecha_fin_obra
            )
        db.session.add(nuevo_proyecto)
        db.session.commit()
        
        return redirect(url_for('show_proyect_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addproyect. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500


#----Muestro el formulario para moneda----#
@app.route("/api/addcoin", methods=["GET"])
def show_coin_form():
    opciones_moneda = sorted(Moneda.query.all(), key=lambda moneda: moneda.descr_moneda)
    return render_template("addcoin.html", opciones_moneda=opciones_moneda)

#----Obtengo datos del formulario para agregar moneda----#
@app.route("/api/addcoin", methods=["POST"])
def add_coin():
    try:
        descr_moneda = request.form["descr_moneda"]

        # Verificar si la moneda ya existe
        if Moneda.query.filter_by(descr_moneda=descr_moneda).first():
            error = "La Moneda ya existe"
            return render_template("addcoin.html", monedas=Moneda.query.all(), error=error)        
        
        # Crear un nuevo objeto Moneda
        nueva_moneda = Moneda(descr_moneda=descr_moneda)
        db.session.add(nueva_moneda)
        db.session.commit()
        

        return redirect(url_for('show_coin_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addcoin. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500

#----Muestro el formulario para conceptos----#
@app.route("/api/addconcept", methods=["GET"])
def show_concept_form():
    opciones_concepto = sorted(Concepto.query.all(), key=lambda concepto: concepto.nombre_concepto)
    return render_template("addconcept.html", opciones_concepto=opciones_concepto)

#----Obtengo datos del formulario para agregar concepto----#
@app.route("/api/addconcept", methods=["POST"])
def add_concept():
    try:
        nombre_concepto = request.form["nombre_concepto"]

        # Verificar si el concepto ya existe
        if Concepto.query.filter_by(nombre_concepto=nombre_concepto).first():
            error = "El concepto ya existe"
            return render_template("addconcept.html", conceptos=Concepto.query.all(), error=error)        
        
        # Crear un nuevo objeto Concepto
        nuevo_concepto = Concepto(nombre_concepto=nombre_concepto)
        db.session.add(nuevo_concepto)
        db.session.commit()
        
        return redirect(url_for('show_concept_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addconcept. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500
        
#----Muestro el formulario para usuarios----#
@app.route("/api/adduser", methods=["GET"])
def show_user_form():
    opciones_usuario = sorted(Usuario.query.all(), key=lambda usuario: usuario.nombre_usuario)
    return render_template("adduser.html", opciones_usuario=opciones_usuario)

#----Obtengo datos del formulario para agregar usuario----#
@app.route("/api/adduser", methods=["POST"])
def add_user():
    try:
        nombre_usuario = request.form["nombre_usuario"]
        mail_usuario = request.form["mail_usuario"]
        contrasenia_usuario = request.form["contrasenia_usuario"]

        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
            error = "El usuario ya existe"
            return render_template("adduser.html", usuarios=Usuario.query.all(), error=error)        
        
        # Crear un nuevo objeto Usuario
        nuevo_usuario = Usuario(
            nombre_usuario=nombre_usuario,
            mail_usuario=mail_usuario,
            contrasenia_usuario=contrasenia_usuario
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        

        return redirect(url_for('show_user_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/adduser. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500

#----Muestro el formulario para agregar cuenta----#
@app.route("/api/addaccount", methods=["GET"])
def show_account_form():
    opciones_moneda = sorted(Moneda.query.all(), key=lambda moneda: moneda.descr_moneda)
    opciones_empresa = sorted(Empresa.query.all(), key=lambda empresa: empresa.nombre_empresa)
    opciones_concepto = sorted(Concepto.query.all(), key=lambda concepto: concepto.nombre_concepto)
    opciones_cuenta = sorted(Cuentas.query.all(), key=lambda cuenta: cuenta.nombre_cuenta)
    opciones_contrato = sorted(Contrato.query.all(), key=lambda contrato: contrato.nombre_contrato)
    opciones_inversor_prestamista_deudor = sorted(Inversor_prestamista_deudor.query.all(), key=lambda inversor_prestamista_deudor: inversor_prestamista_deudor.nombre_inversor_prestamista_deudor)
    
    return render_template("addaccount.html",opciones_contrato=opciones_contrato, opciones_inversor_prestamista_deudor=opciones_inversor_prestamista_deudor,opciones_cuenta=opciones_cuenta, opciones_moneda=opciones_moneda, opciones_empresa=opciones_empresa, opciones_concepto=opciones_concepto)

#----Obtengo datos del formulario cuenta----#
@app.route("/api/addaccount", methods=["POST"])
def add_account():
    try:
        id_empresa = request.form["id_empresa"]
        id_concepto = request.form["id_concepto"]
        id_moneda = request.form["id_moneda"]
        nombre_cuenta = request.form["nombre_cuenta"]
        inversor_prestamista_deudor_T_F = request.form.get("inversor_prestamista_deudor_T_F") == "on"  # Utiliza request.form.get para manejar el caso de que la casilla no esté marcada
        # Obtener los valores relacionados con el agente financiero si el checkbox está marcado
        if inversor_prestamista_deudor_T_F:
            id_inversor_prestamista_deudor = request.form["id_inversor_prestamista_deudor"]
            tipo_cta = request.form["tipo_cta"]
            id_contrato = request.form["id_contrato"]
        else:
            # Establecer los valores como nulos si el checkbox no está marcado
            id_inversor_prestamista_deudor = None
            tipo_cta = None
            id_contrato = None

        # Crear un nuevo objeto Cuentas
        nueva_cuenta = Cuentas(
            id_empresa=id_empresa,
            id_concepto=id_concepto,
            id_moneda=id_moneda,
            nombre_cuenta=nombre_cuenta,
            inversor_prestamista_deudor_T_F=inversor_prestamista_deudor_T_F,
            id_inversor_prestamista_deudor=id_inversor_prestamista_deudor,
            tipo_cta=tipo_cta,
            id_contrato=id_contrato
        )

        # Agregar el nuevo movimiento a la base de datos
        db.session.add(nueva_cuenta)
        db.session.commit()

        return redirect(url_for('show_account_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addaccount. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500

#----Muestro el formulario para agregar contrato----#
@app.route("/api/addcontract", methods=["GET"])
def show_contract_form():    
    opciones_contrato = sorted(Contrato.query.all(), key=lambda contrato: contrato.nombre_contrato)
    opciones_inversor_prestamista_deudor = sorted(Inversor_prestamista_deudor.query.all(), key=lambda inversor_prestamista_deudor: inversor_prestamista_deudor.nombre_inversor_prestamista_deudor)
    opciones_empresa = sorted(Empresa.query.all(), key=lambda empresa: empresa.nombre_empresa)
    opciones_proyecto = sorted(Proyecto.query.all(), key=lambda proyecto: proyecto.nombre_proyecto)
    opciones_moneda = sorted(Moneda.query.all(), key=lambda moneda: moneda.descr_moneda)
    
    return render_template("addcontract.html",opciones_contrato=opciones_contrato, opciones_proyecto=opciones_proyecto, opciones_inversor_prestamista_deudor=opciones_inversor_prestamista_deudor, opciones_moneda=opciones_moneda, opciones_empresa=opciones_empresa)

#----Obtengo datos del formulario contrato----#
@app.route("/api/addcontract", methods=["POST"])
def add_contract():
    try:
        nombre_contrato = request.form["nombre_contrato"]
        id_inversor_prestamista_deudor = request.form["id_inversor_prestamista_deudor"]
        id_empresa = request.form["id_empresa"]
        id_proyecto = request.form["id_proyecto"]
        id_moneda = request.form["id_moneda"]
        inversor_o_prestamista_o_deudor = request.form["inversor_o_prestamista_o_deudor"]
        tasa_anual = request.form["tasa_anual"]
        aplica_CAC_T_F = request.form.get("act_cac") == "on"  # True if checkbox is checked, False otherwise
        monto_contrato = request.form["monto_contrato"]

        
        # Crear un nuevo objeto Cuentas
        nuevo_contrato = Contrato(
            nombre_contrato=nombre_contrato,
            id_inversor_prestamista_deudor=id_inversor_prestamista_deudor,
            id_empresa=id_empresa,
            id_proyecto=id_proyecto,
            id_moneda=id_moneda,
            inversor_o_prestamista_o_deudor=inversor_o_prestamista_o_deudor,
            tasa_anual=tasa_anual,
            aplica_CAC_T_F=aplica_CAC_T_F,
            monto_contrato=monto_contrato
        )

        # Agregar el nuevo movimiento a la base de datos
        db.session.add(nuevo_contrato)
        db.session.commit()

        return redirect(url_for('show_contract_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addcontract. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True, port=4000)