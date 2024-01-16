from flask import Flask, jsonify, request, render_template
from Models import db, RelacionMovimientos, Cuentas, Usuario, Empresa, Moneda, Concepto, Tasa, Inversor
from logging import exception


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:\\Users\\ignac\\Desktop\\Argenway\\APP_PRU\\database\\SistemaPRU.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Corregido: "SQLALCHEMY_TRACK_MODIFICATIONES"
db.init_app(app)

# Aquí empiezan las rutas
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/base")
def show_main():
    return render_template("base.html")

@app.route("/api/balances")
def show_balances():
    return render_template("saldos.html")

@app.route("/api/reports")
def show_reports():
    return render_template("reportes.html")

@app.route("/api/addrate")
def show_rates():
    return render_template("addrate.html")

#----Muestro el formulario para agregar movimiento----#
@app.route("/api/addmovement", methods=["GET"])
def show_movement_form():
    opciones_moneda = Moneda.query.all()
    opciones_empresa = Empresa.query.all()
    opciones_concepto = Concepto.query.all()
    opciones_cuenta = Cuentas.query.all()
    return render_template("movimientos.html",opciones_cuenta=opciones_cuenta, opciones_concepto=opciones_concepto, opciones_moneda=opciones_moneda, opciones_empresa=opciones_empresa)

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
        fecha = request.form["fecha"]
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

        # Obtener las cuentas asociadas a los conceptos desde y hacia
        cuentas_desde = Cuentas.query.filter_by(id_concepto=id_concepto_desde).all()
        cuentas_hacia = Cuentas.query.filter_by(id_concepto=id_concepto_hacia).all()

        # Serializar y enviar información filtrada al cliente
        cuentas_desde_serialized = [cuenta.serialize() for cuenta in cuentas_desde]
        cuentas_hacia_serialized = [cuenta.serialize() for cuenta in cuentas_hacia]

        return jsonify({
            "movimiento": nuevo_movimiento.serialize(),
            "cuentas_desde": cuentas_desde_serialized,
            "cuentas_hacia": cuentas_hacia_serialized
        }), 200
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addmovement. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500

#----Muestro el formulario para empresa----#
@app.route("/api/addcompany", methods=["GET"])
def show_company_form():
    empresas = Empresa.query.all()
    return render_template("addcompany.html", empresas=empresas)

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

        return jsonify(nueva_empresa.serialize()), 200
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addcompany. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500
    
#----Muestro el formulario para inversor----#
@app.route("/api/addinvestor", methods=["GET"])
def show_investor_form():
    inversores = Inversor.query.all()
    return render_template("addinvestor.html", inversores=inversores)

#----Obtengo datos del formulario para agregar inversor----#
@app.route("/api/addinvestor", methods=["POST"])
def add_investor():
    try:
        nombre_inversor = request.form["nombre_inversor"]

        # Verificar si el inversor ya existe
        if Inversor.query.filter_by(nombre_inversor=nombre_inversor).first():
            error = "El inversor ya existe"
            return render_template("addinvestor.html", inversores=Inversor.query.all(), error=error)        
        
        # Crear un nuevo objeto Inversor
        nuevo_inversor = Inversor(nombre_inversor=nombre_inversor)
        db.session.add(nuevo_inversor)
        db.session.commit()
        
        # Agregar el nuevo inversor a la base de datos
        db.session.add(nuevo_inversor)
        db.session.commit()

        return jsonify(nuevo_inversor.serialize()), 200
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addinvestor. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500
    
#----Muestro el formulario para moneda----#
@app.route("/api/addcoin", methods=["GET"])
def show_coin_form():
    monedas = Moneda.query.all()
    return render_template("addcoin.html", monedas=monedas)

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
        
        # Agregar la nueva moneda a la base de datos
        db.session.add(nueva_moneda)
        db.session.commit()

        return jsonify(nueva_moneda.serialize()), 200
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addcoin. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500

#----Muestro el formulario para conceptos----#
@app.route("/api/addconcept", methods=["GET"])
def show_concept_form():
    conceptos = Concepto.query.all()
    return render_template("addconcept.html", conceptos=conceptos)

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
        
        # Agregar el nuevo movimiento a la base de datos
        db.session.add(nuevo_concepto)
        db.session.commit()

        return jsonify(nuevo_concepto.serialize()), 200
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addconcept. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500
        
#----Muestro el formulario para usuarios----#
@app.route("/api/adduser", methods=["GET"])
def show_user_form():
    usuarios = Usuario.query.all()
    return render_template("adduser.html", usuarios=usuarios)

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
        
        # Agregar el nuevo movimiento a la base de datos
        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify(nuevo_usuario.serialize()), 200
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/adduser. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500

#----Muestro el formulario para agregar cuenta----#
@app.route("/api/addaccount", methods=["GET"])
def show_account_form():
    opciones_moneda = Moneda.query.all()
    opciones_empresa = Empresa.query.all()
    opciones_concepto = Concepto.query.all()
    opciones_inversor = Inversor.query.all()
    cuentas = Cuentas.query.all()
    return render_template("addaccount.html",opciones_inversor=opciones_inversor,cuentas=cuentas, opciones_moneda=opciones_moneda, opciones_empresa=opciones_empresa, opciones_concepto=opciones_concepto)

#----Obtengo datos del formulario cuenta----#
@app.route("/api/addaccount", methods=["POST"])
def add_account():
    try:
        # id_usuario = request.form["id_usuario"]
        id_empresa = request.form["id_empresa"]
        id_concepto = request.form["id_concepto"]
        id_moneda = request.form["id_moneda"]
        nombre_cuenta = request.form["nombre_cuenta"]
        inversor_T_F = request.form.get("inversor_T_F", "off")  # Utiliza request.form.get para manejar el caso de que la casilla no esté marcada
        nombre_inversor = request.form["id_inversor"]
        tasa_T_F = request.form.get("tasa_T_F","off")

        # Verificar si la cuenta ya existe
        if Cuentas.query.filter_by(nombre_cuenta=nombre_cuenta).first():
            error = "La cuenta ya existe"
            return render_template("addaccount.html", cuentas=Cuentas.query.all(), error=error)

        
        # Buscar el ID del inversor
        id_inversor = None if inversor_T_F == "off" else None  # Valor por defecto

        if inversor_T_F == "on":
            inversor_existente = Inversor.query.filter_by(nombre_inversor=nombre_inversor).first()

            if not inversor_existente:
                # Si el inversor no existe y se marcó como inversor, muestra un mensaje de alerta
                mensaje_alerta = "Debe cargar en primer lugar dicho inversor"
                return render_template("addaccount.html", cuentas=Cuentas.query.all(), mensaje_alerta=mensaje_alerta)

            id_inversor = inversor_existente.id_inversor

        # Crear un nuevo objeto Cuentas
        nueva_cuenta = Cuentas(
            # id_usuario=id_usuario,
            id_empresa=id_empresa,
            id_concepto=id_concepto,
            id_moneda=id_moneda,
            nombre_cuenta=nombre_cuenta,
            inversor_T_F=inversor_T_F,
            id_inversor=id_inversor,
            tasa_T_F=tasa_T_F
        )

        # Agregar el nuevo movimiento a la base de datos
        db.session.add(nueva_cuenta)
        db.session.commit()

        return jsonify(nueva_cuenta.serialize()), 200
    except Exception as e:
        print(f"\n[SERVER]: Error in route /api/addaccount. Log: {str(e)}\n")
        print(f"Request data: {request.form}")
        db.session.rollback()
        return jsonify({"msg": "Algo ha salido mal"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=4000)
