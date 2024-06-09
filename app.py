from flask import Flask, jsonify, request, render_template, redirect, url_for, send_file, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate
from logging import exception
from datetime import date, datetime
from pathlib import Path
import os
from calculadora_RE import *
from Models import *
from pantalla_prestamistas import obtener_prestamistas
from mov_prestamistas import movimientos_prestamistas
from tabla_caja import obtener_reportes, obtener_reportes_agentes
from crear_zip import crear_zip_en_memoria
# Configuración de la aplicación Flask
app = Flask(__name__, template_folder='templates', static_folder='static')

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:\\Users\\PETY\\Desktop\\Argenway\\database\\SistemaPRU.db"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:\\Users\\Argenway\\Documents\\BD_PRU\\database\\SistemaPRU.db"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:\\Users\\ignac\\Desktop\\Argenway\\SistemaContable\\database\\SistemaPRU.db"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:\\Roberto\\Argenway\\240120 aplicacion\\SistemaContable2\\SistemaContable\\database\\SistemaPRU.db"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/sanchez/SistemaContable/database/SistemaPRU.db"
app.config['SECRET_KEY'] = 'password'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Corregido: "SQLALCHEMY_TRACK_MODIFICATIONES"
db.init_app(app)

#login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ordeno las tablas
tablas_ordenadas = [Empresa, Moneda, Usuario, Concepto, Inversor_prestamista_deudor, Proyecto, Contrato, Cuentas]
tablas_ordenadas = sorted(tablas_ordenadas, key=lambda tabla: tabla.__tablename__)

# Aquí empiezan las rutas

# Ruta para servir los archivos estáticos del frontend
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route("/index", methods=["GET", "POST"])
def home():
    return render_template("index.html")

def pagina_no_encontrada(error):
    return "<h1>La página que intentas buscar no existe...</h1>"

@app.route("/api/base")
@login_required
def show_main():
    return render_template("base.html")

@app.route("/api/inversor")
@login_required
def show_inversor():
    #Conceptos a filtrar
    conceptos = [10,15,16]
    # print (conceptos)
    # Llama a la función para obtener los resultados de las tres consultas
    datos_peso, datos_euro, datos_dolar = obtener_reportes_agentes(conceptos)
    # Renderiza los resultados en una plantilla HTML
    return render_template('inversor.html',datos_peso=datos_peso, datos_euro=datos_euro, datos_dolar=datos_dolar)

@app.route("/api/saldo")
@login_required
def show_saldos():
    ids_conceptos = db.session.query(Concepto.id_concepto).all()
    # print(ids_conceptos)
    todos_los_ids = [id_concepto[0] for id_concepto in ids_conceptos]
    # print(todos_los_ids)
    conceptos_excluidos = [1, 10, 15, 16]
    # print(conceptos_excluidos)
    conceptos_a_pasar = [id_concepto for id_concepto in todos_los_ids if id_concepto not in conceptos_excluidos]
    # print(conceptos_a_pasar)
    # Llama a la función para obtener los resultados de las tres consultas
    datos_peso, datos_euro, datos_dolar = obtener_reportes(conceptos_a_pasar)
    # Renderiza los resultados en una plantilla HTML
    return render_template('saldo.html',datos_peso=datos_peso, datos_euro=datos_euro, datos_dolar=datos_dolar)

@app.route("/api/showmovement")
@login_required
def show_movement():
    movimientos = RelacionMovimientos.query.all()
    # Renderiza los resultados en una plantilla HTML
    return render_template('showmovement.html', movimientos=movimientos)

@app.route("/api/caja")
@login_required
def show_caja():
    #Conceptos a filtrar
    conceptos = [1]
    # Llama a la función para obtener los resultados de las tres consultas
    datos_peso, datos_euro, datos_dolar = obtener_reportes(conceptos)
    # Renderiza los resultados en una plantilla HTML
    return render_template('caja.html',datos_peso=datos_peso, datos_euro=datos_euro, datos_dolar=datos_dolar)

@login_manager.user_loader
def load_user(id_usuario):
    # Carga y devuelve el usuario a partir del ID de usuario almacenado en la sesión
    session = Session()
    return session.get(Usuario, int(id_usuario))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        contrasenia = request.form['contrasenia']
        
        # Consultar la base de datos para verificar las credenciales
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        
        if usuario and check_password_hash(usuario.contrasenia_usuario, contrasenia):
            # Autenticación exitosa, loguear al usuario
            login_user(usuario)
            # Redirigir al usuario a la página principal
            return redirect(url_for('home'))
        
    # Si es un GET request o si hubo un error de autenticación, renderiza la página de inicio de sesión
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/api/rent", methods=["GET", "POST"])
@login_required
def calcular_renta():
    if request.method == "POST":
        try:
            # Verificar si el botón ya se ha presionado este mes
            today = datetime.now().date()
            last_button_press = UltimaPresion.query.order_by(UltimaPresion.id.desc()).first()
            if last_button_press and last_button_press.fecha.month == today.month and last_button_press.fecha.year == today.year:
                return render_template("resultado_renta.html", resultado="El botón ya ha sido presionado este mes.")

            # Guardar la fecha actual como la última presión del botón
            nueva_presion = UltimaPresion(fecha=datetime.now().date())
            db.session.add(nueva_presion)
            db.session.commit()
            
            # Realizar la consulta SQL sobre la tabla CUENTAS
            resultado = consultar_cuentas_inversores()  # Por ejemplo, la cantidad de cuentas obtenidas
            return render_template("resultado_renta.html", resultado=resultado)
        except Exception as e:
            print(f"\n[SERVER]: Error en la ruta /api/rent. Log: {str(e)}\n")
            return jsonify({"error": "¡Algo salió mal al realizar la consulta!"}), 500
    else:
        # Aquí se muestra el formulario para ingresar los datos
        return render_template("rent.html")
parent_directory = os.path.dirname(os.path.abspath(__file__))

# Ruta para descargar el archivo ZIP
@app.route('/download_zip')
@login_required
def download_csv():
    # Crear el archivo ZIP en memoria
    archivo_zip = crear_zip_en_memoria()

    # Enviar el archivo ZIP como respuesta HTTP para su descarga
    return send_file(
        archivo_zip,
        as_attachment=True,
        download_name='Sistema_PRU.zip'
    )

#----Muestro el formulario para agregar CAC----#
@app.route("/api/addcac")
@login_required
def show_cac():
    opciones_cac = sorted(Indice_cac.query.all(), key=lambda cac: cac.indice)
    return render_template("addcac.html",opciones_cac=opciones_cac)

#----Obtengo datos del formulario tasa----#
@app.route("/api/addcac", methods=["POST"])
@login_required
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
@login_required
def show_movement_form():
    opciones_moneda = sorted(Moneda.query.all(), key=lambda moneda: moneda.descr_moneda)
    opciones_empresa = sorted(Empresa.query.all(), key=lambda empresa: empresa.nombre_empresa)
    opciones_concepto = sorted(Concepto.query.all(), key=lambda concepto: concepto.nombre_concepto)
    opciones_cuenta = sorted(Cuentas.query.all(), key=lambda cuenta: cuenta.nombre_cuenta)
    # Obtener la fecha actual
    fecha_actual = date.today().strftime("%Y-%m-%d")
    fecha_minima = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    fecha_maxima = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    return render_template("movimientos.html",fecha_minima=fecha_minima,fecha_maxima=fecha_maxima,fecha_actual=fecha_actual,opciones_cuenta=opciones_cuenta, opciones_concepto=opciones_concepto, opciones_moneda=opciones_moneda, opciones_empresa=opciones_empresa)

#----Obtengo datos del formulario movimientos----#
@app.route("/api/get_cuentas_desde", methods=["POST"])
@login_required
def get_cuentas_desde():
    try:
        data = request.get_json()
        id_concepto_desde = data.get("id_concepto_desde")
        id_empresa_desde = data.get("id_empresa_desde")
        id_moneda_desde = data.get("id_moneda_desde")

        # Iniciar la consulta filtrando por concepto
        cuentas_desde_query = Cuentas.query.filter_by(id_concepto=id_concepto_desde)

        # Aplicar filtros adicionales si los parámetros están presentes
        if id_empresa_desde:
            cuentas_desde_query = cuentas_desde_query.filter_by(id_empresa=id_empresa_desde)
        if id_moneda_desde:
            cuentas_desde_query = cuentas_desde_query.filter_by(id_moneda=id_moneda_desde)

        # Ordenar las cuentas por un campo específico, por ejemplo, nombre_cuenta
        cuentas_desde_query = cuentas_desde_query.order_by(Cuentas.nombre_cuenta.asc())

        # Obtener el resultado final de la consulta
        cuentas_desde = cuentas_desde_query.all()

        # Serializar y devolver las cuentas en formato JSON
        return jsonify([cuenta.serialize() for cuenta in cuentas_desde]), 200
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/get_cuentas_desde. Log: {str(e)}\n")
        return jsonify({"msg": "Algo ha salido mal"}), 500

@app.route("/api/get_cuentas_hacia", methods=["POST"])
@login_required
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

        # Ordenar las cuentas por un campo específico, por ejemplo, nombre_cuenta
        cuentas_hacia_query = cuentas_hacia_query.order_by(Cuentas.nombre_cuenta.asc())

        # Obtener el resultado final de la consulta hacia
        cuentas_hacia = cuentas_hacia_query.all()

        # Serializar y devolver las cuentas en formato JSON
        return jsonify([cuenta.serialize() for cuenta in cuentas_hacia]), 200
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/get_cuentas_hacia. Log: {str(e)}\n")
        return jsonify({"msg": "Algo ha salido mal"}), 500

# Modificar la función add_movement para recibir concepto_desde y concepto_hacia
@app.route("/api/addmovement", methods=["POST"])
@login_required
def add_movement():
    try:
        # Obtener el usuario logueado
        usuario = current_user
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
            id_usuario=usuario.id_usuario,  # Asigna el ID del usuario al nuevo movimiento
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
@login_required
def show_company_form():
    opciones_empresa = sorted(Empresa.query.all(), key=lambda empresa: empresa.nombre_empresa)
    return render_template("addcompany.html", opciones_empresa=opciones_empresa)

#----Obtengo datos del formulario para agregar empresa----#
@app.route("/api/addcompany", methods=["POST"])
@login_required
def add_company():
    try:
        nombre_empresa = request.form["nombre_empresa"]

        # # Verificar si la empresa ya existe
        # if Empresa.query.filter_by(nombre_empresa=nombre_empresa).first():
        #     error = "La empresa ya existe"
        #     return render_template("addcompany.html", empresas=Empresa.query.all(), error=error)        
        
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
@login_required
def show_investor_form():
    opciones_inversor_prestamista_deudor = sorted(Inversor_prestamista_deudor.query.all(), key=lambda inversor_prestamista_deudor: inversor_prestamista_deudor.nombre_inversor_prestamista_deudor)
    return render_template("addinvestor.html", opciones_inversor_prestamista_deudor=opciones_inversor_prestamista_deudor)

#----Obtengo datos del formulario para agregar inversor_prestamista_deudor----#
@app.route("/api/addinvestor", methods=["POST"])
@login_required
def add_investor():
    try:
        nombre_inversor_prestamista_deudor = request.form["nombre_inversor_prestamista_deudor"]
        inversor_o_prestamista_o_deudor = request.form["inversor_o_prestamista_o_deudor"]
                
        # Verificar si el inversor ya existe
        inversor_existente = Inversor_prestamista_deudor.query.filter_by(nombre_inversor_prestamista_deudor=nombre_inversor_prestamista_deudor).first()
        if inversor_existente:
            flash("El inversor ya existe. Por favor, ingresa un nombre diferente.", "error")
            return redirect(url_for('show_investor_form'))

        # Crear un nuevo objeto inversor_prestamista_deudor
        nuevo_inversor_prestamista_deudor = Inversor_prestamista_deudor(
            nombre_inversor_prestamista_deudor=nombre_inversor_prestamista_deudor,
            inversor_o_prestamista_o_deudor=inversor_o_prestamista_o_deudor
            )
        db.session.add(nuevo_inversor_prestamista_deudor)
        db.session.commit()
        
        flash("Inversor agregado exitosamente.", "success")
        return redirect(url_for('show_investor_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addinvestor. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        flash("Algo ha salido mal. Por favor, inténtalo nuevamente.", "error")
        return redirect(url_for('show_investor_form'))

#----Muestro el formulario para proyecto----#
@app.route("/api/addproyect", methods=["GET"])
@login_required
def show_proyect_form():
    opciones_proyecto = sorted(Proyecto.query.all(), key=lambda proyecto: proyecto.nombre_proyecto)
    for proyecto in opciones_proyecto:
            proyecto.fecha_inicio_obra = proyecto.fecha_inicio_obra.strftime("%d-%m-%Y")
            proyecto.fecha_fin_obra = proyecto.fecha_fin_obra.strftime("%d-%m-%Y")
    return render_template("addproyect.html", opciones_proyecto=opciones_proyecto)

#----Obtengo datos del formulario para agregar proyecto----#
@app.route("/api/addproyect", methods=["POST"])
@login_required
def add_proyect():
    try:
        nombre_proyecto = request.form["nombre_proyecto"]
        fecha_inicio_obra_str = request.form["fecha_inicio_obra"]
        fecha_fin_obra_str = request.form["fecha_fin_obra"]
        
        fecha_inicio_obra = datetime.strptime(fecha_inicio_obra_str, "%Y-%m-%d")       
        fecha_fin_obra = datetime.strptime(fecha_fin_obra_str, "%Y-%m-%d")

        # Verificar si el proyecto ya existe
        proyecto_existente = Proyecto.query.filter_by(nombre_proyecto=nombre_proyecto).first()
        if proyecto_existente:
            flash("El proyecto ya existe. Por favor, ingresa un nombre diferente.", "error")
            return redirect(url_for('show_proyect_form'))

        # Crear un nuevo objeto proyecto
        nuevo_proyecto = Proyecto(
            nombre_proyecto=nombre_proyecto,
            fecha_inicio_obra=fecha_inicio_obra,
            fecha_fin_obra=fecha_fin_obra
            )
        db.session.add(nuevo_proyecto)
        db.session.commit()
        
        flash("Proyecto agregado exitosamente.", "success")
        return redirect(url_for('show_proyect_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addproyect. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        flash("Algo ha salido mal. Por favor, inténtalo nuevamente.", "error")
        return redirect(url_for('show_proyect_form'))

#----Muestro el formulario para moneda----#
@app.route("/api/addcoin", methods=["GET"])
@login_required
def show_coin_form():
    opciones_moneda = sorted(Moneda.query.all(), key=lambda moneda: moneda.descr_moneda)
    return render_template("addcoin.html", opciones_moneda=opciones_moneda)

#----Obtengo datos del formulario para agregar moneda----#
@app.route("/api/addcoin", methods=["POST"])
@login_required
def add_coin():
    try:
        descr_moneda = request.form["descr_moneda"]
        
        # Verificar si la moneda ya existe en la base de datos
        moneda_existente = Moneda.query.filter_by(descr_moneda=descr_moneda).first()
        if moneda_existente:
            # Si la moneda ya existe, mostrar un mensaje de error al usuario
            flash("La moneda ya existe", "error")
            return redirect(url_for('show_coin_form'))

        nueva_moneda = Moneda(descr_moneda=descr_moneda)
        db.session.add(nueva_moneda)
        db.session.commit()
        
        return redirect(url_for('show_coin_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addcoin. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        flash("Algo ha salido mal", "error")
        return redirect(url_for('show_coin_form'))

#----Muestro el formulario para conceptos----#
@app.route("/api/addconcept", methods=["GET"])
@login_required
def show_concept_form():
    opciones_concepto = sorted(Concepto.query.all(), key=lambda concepto: concepto.nombre_concepto)
    return render_template("addconcept.html", opciones_concepto=opciones_concepto)

#----Obtengo datos del formulario para agregar concepto----#
@app.route("/api/addconcept", methods=["POST"])
@login_required
def add_concept():
    try:
        nombre_concepto = request.form["nombre_concepto"]

        # Verificar si el concepto ya existe
        concepto_existente = Concepto.query.filter_by(nombre_concepto=nombre_concepto).first()
        if concepto_existente:
            flash("El concepto ya existe. Por favor, ingresa un nombre diferente.", "error")
            return redirect(url_for('show_concept_form'))

        # Crear un nuevo objeto Concepto
        nuevo_concepto = Concepto(nombre_concepto=nombre_concepto)
        db.session.add(nuevo_concepto)
        db.session.commit()
        
        flash("Concepto agregado exitosamente.", "success")
        return redirect(url_for('show_concept_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addconcept. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        flash("Algo ha salido mal. Por favor, inténtalo nuevamente.", "error")
        return redirect(url_for('show_concept_form'))
    
#----Muestro el formulario para usuarios----#
@app.route("/api/adduser", methods=["GET"])
@login_required
def show_user_form():
    opciones_usuario = sorted(Usuario.query.all(), key=lambda usuario: usuario.nombre_usuario)
    return render_template("adduser.html", opciones_usuario=opciones_usuario)

#----Obtengo datos del formulario para agregar usuario----#
@app.route("/api/adduser", methods=["POST"])
@login_required
def add_user():
    try:
        nombre_usuario = request.form["nombre_usuario"]
        contrasenia_usuario = request.form["contrasenia_usuario"]
        contrasenia_hash = generate_password_hash(contrasenia_usuario)
        
        # Crear un nuevo objeto Usuario
        nuevo_usuario = Usuario(
            nombre_usuario=nombre_usuario,
            contrasenia_usuario=contrasenia_hash
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        

        return redirect(url_for('show_user_form'))
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/adduser. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500

# Ruta para obtener los contratos según el agente seleccionado
@app.route("/api/get_contratos", methods=["POST"])
@login_required
def get_contratos():
    try:
        data = request.get_json()
        id_inversor_prestamista_deudor = data.get("id_inversor_prestamista_deudor")

        # Filtrar y ordenar los contratos por el agente seleccionado
        contratos = Contrato.query.filter_by(id_inversor_prestamista_deudor=id_inversor_prestamista_deudor).order_by(Contrato.nombre_contrato.asc()).all()


        # Serializar y devolver los contratos en formato JSON
        contratos_data = []
        for contrato in contratos:
            contrato_info = contrato.serialize()
            contrato_info['proyecto'] = contrato.proyecto.serialize()  # Incluir información del proyecto asociado al contrato
            contratos_data.append(contrato_info)

        return jsonify(contratos_data), 200
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/get_contratos. Log: {str(e)}\n")
        return jsonify({"msg": "Algo ha salido mal"}), 500

#----Muestro el formulario para agregar cuenta----#
@app.route("/api/addaccount", methods=["GET"])
@login_required
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
@login_required
def add_account():
    try:
        id_empresa = request.form["id_empresa"]
        id_concepto = request.form["id_concepto"]
        id_moneda = request.form["id_moneda"]
        nombre_cuenta = request.form["nombre_cuenta"]
        resultado = request.form.get("resultado") == "on"
        inversor_prestamista_deudor_T_F = request.form.get("inversor_prestamista_deudor_T_F") == "on"  # Utiliza request.form.get para manejar el caso de que la casilla no esté marcada
        # Obtener los valores relacionados con el agente financiero si el checkbox está marcado
        if inversor_prestamista_deudor_T_F:
            id_inversor_prestamista_deudor = request.form["id_inversor_prestamista_deudor"]
            tipo_cta = request.form["tipo_cta"]
            id_contrato = request.form["id_contrato"]
        else:
            id_inversor_prestamista_deudor = None
            tipo_cta = None
            id_contrato = None
        # Crear un nuevo objeto Cuentas
        nueva_cuenta = Cuentas(
            id_empresa=id_empresa,
            id_concepto=id_concepto,
            id_moneda=id_moneda,
            nombre_cuenta=nombre_cuenta,
            resultado=resultado,
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

#----Obtengo datos del formulario movimientos----#
@app.route("/api/get_investor", methods=["POST"])
@login_required
def get_investor():
    try:
        data = request.get_json()
        inversor_o_prestamista_o_deudor = data.get("inversor_o_prestamista_o_deudor")

        # print(f"\n[SERVER]: Received role: {inversor_o_prestamista_o_deudor}\n")

        # Filtrar y ordenar los inversores por el rol seleccionado
        agente_query = Inversor_prestamista_deudor.query.filter_by(inversor_o_prestamista_o_deudor=inversor_o_prestamista_o_deudor).order_by(Inversor_prestamista_deudor.nombre_inversor_prestamista_deudor.asc()).all()
        # print(f"\n[SERVER]: Query result: {agente_query}\n")

        # Serializar y devolver las cuentas en formato JSON
        return jsonify([Inversor_prestamista_deudor.serialize() for Inversor_prestamista_deudor in agente_query]), 200
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/get_investor. Log: {str(e)}\n")
        return jsonify({"msg": "Algo ha salido mal"}), 500

#----Muestro el formulario para agregar contrato----#
@app.route("/api/addcontract", methods=["GET"])
@login_required
def show_contract_form():    
    opciones_contrato = sorted(Contrato.query.all(), key=lambda contrato: contrato.nombre_contrato)
    opciones_inversor_prestamista_deudor = sorted(Inversor_prestamista_deudor.query.all(), key=lambda inversor_prestamista_deudor: inversor_prestamista_deudor.nombre_inversor_prestamista_deudor)
    opciones_empresa = sorted(Empresa.query.all(), key=lambda empresa: empresa.nombre_empresa)
    opciones_proyecto = sorted(Proyecto.query.all(), key=lambda proyecto: proyecto.nombre_proyecto)
    opciones_moneda = sorted(Moneda.query.all(), key=lambda moneda: moneda.descr_moneda)
    # Formatear la fecha de fin de obra
    for proyecto in opciones_proyecto:
        if proyecto.fecha_fin_obra:
            proyecto.fecha_fin_obra_formateada = proyecto.fecha_fin_obra.strftime('%d-%m-%Y')
        else:
            proyecto.fecha_fin_obra_formateada = 'Fecha no disponible'

    return render_template("addcontract.html",opciones_contrato=opciones_contrato, opciones_proyecto=opciones_proyecto, opciones_inversor_prestamista_deudor=opciones_inversor_prestamista_deudor, opciones_moneda=opciones_moneda, opciones_empresa=opciones_empresa)

#----Obtengo datos del formulario contrato----#
@app.route("/api/addcontract", methods=["POST"])
@login_required
def add_contract():
    try:
        nombre_contrato = request.form["nombre_contrato"]
        id_inversor_prestamista_deudor = request.form["id_inversor_prestamista_deudor"]
        id_empresa = request.form["id_empresa"]
        id_proyecto = request.form["id_proyecto"]
        id_moneda = request.form["id_moneda"]
        inversor_o_prestamista_o_deudor = request.form["inversor_o_prestamista_o_deudor"]
        tasa_anual = request.form["tasa_anual"]
        tasa_anual_RE = request.form["tasa_anual_RE"]
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
            tasa_anual_RE=tasa_anual_RE,
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

@app.route("/api/lender")
@login_required
def show_lender():
    # Llama a la función para obtener los resultados de las tres consultas
    datos_prestamistas = obtener_prestamistas(15)
    # print(datos_prestamistas)
    # opciones_moneda = sorted(Moneda.query.all(), key=lambda moneda: moneda.descr_moneda)
    # opciones_empresa = sorted(Empresa.query.all(), key=lambda empresa: empresa.nombre_empresa)
    # opciones_concepto = sorted(Concepto.query.all(), key=lambda concepto: concepto.nombre_concepto)
    # opciones_cuenta = sorted(Cuentas.query.all(), key=lambda cuenta: cuenta.nombre_cuenta)
    movimientos_data = movimientos_prestamistas(15)
    # print(movimientos_data)
    # Renderiza los resultados en una plantilla HTML
    return render_template('lender.html',movimientos_data=movimientos_data, datos_prestamistas=datos_prestamistas)

# #----Muestro el formulario para inversor_prestamista_deudor----#
# @app.route("/api/get_investor_account", methods=["GET"])
# @login_required
# def show_investor_form():
#     opciones_inversor_prestamista_deudor = sorted(Inversor_prestamista_deudor.query.all(), key=lambda inversor_prestamista_deudor: inversor_prestamista_deudor.nombre_inversor_prestamista_deudor)
#     return render_template("addinvestor.html", opciones_inversor_prestamista_deudor=opciones_inversor_prestamista_deudor)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(host='0.0.0.0', debug=True, port=80)