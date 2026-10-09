from datetime import date
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import aplicacion, database
from app.models import Habitacion, Cliente, Reserva, Usuario
from app.forms import (
    HabitacionForm, ClienteForm, ReservaForm,
    LoginForm, RegistroForm
)


# ==============================================================================
# AUTENTICACIÓN Y CONTROL DE ACCESO
# ==============================================================================
@aplicacion.route("/login", methods=["GET", "POST"])
def login():
    """
    Gestiona el inicio de sesión para el personal administrativo del hotel.
    """
    if current_user.is_authenticated:
        return redirect(url_for("inicio"))

    formulario = LoginForm()
    if formulario.validate_on_submit():
        usuario = Usuario.query.filter_by(username=formulario.username.data.strip()).first()

        if usuario and usuario.check_password(formulario.password.data):
            login_user(usuario, remember=formulario.recordar.data)
            flash(f"¡Bienvenido de nuevo, {usuario.nombre_completo or usuario.username}!", "success")

            next_page = request.args.get("next")
            # Validación de seguridad para redirecciones abiertas
            if not next_page or urlparse(next_page).netloc != "":
                next_page = url_for("inicio")
            return redirect(next_page)
        else:
            flash("Nombre de usuario o contraseña incorrectos.", "danger")

    return render_template("login.html", formulario=formulario)


@aplicacion.route("/registro", methods=["GET", "POST"])
def registro():
    """
    Permite registrar un nuevo usuario con permisos de administración.
    """
    if current_user.is_authenticated:
        return redirect(url_for("inicio"))

    formulario = RegistroForm()
    if formulario.validate_on_submit():
        # Validar si el usuario ya existe
        if Usuario.query.filter_by(username=formulario.username.data.strip()).first():
            flash("El nombre de usuario ingresado ya está en uso.", "danger")
            return render_template("registro.html", formulario=formulario)

        # Validar si el correo ya existe
        if Usuario.query.filter_by(email=formulario.email.data.strip().lower()).first():
            flash("Ya existe una cuenta vinculada a este correo electrónico.", "danger")
            return render_template("registro.html", formulario=formulario)

        nuevo_usuario = Usuario(
            username=formulario.username.data.strip(),
            email=formulario.email.data.strip().lower(),
            nombre_completo=formulario.nombre_completo.data.strip() if formulario.nombre_completo.data else None
        )
        nuevo_usuario.set_password(formulario.password.data)

        database.session.add(nuevo_usuario)
        database.session.commit()

        login_user(nuevo_usuario)
        flash(f"Cuenta creada exitosamente. ¡Bienvenido al sistema, {nuevo_usuario.username}!", "success")
        return redirect(url_for("inicio"))

    return render_template("registro.html", formulario=formulario)


@aplicacion.route("/logout")
@login_required
def logout():
    """
    Cierra la sesión del usuario activo.
    """
    logout_user()
    flash("Has cerrado sesión exitosamente.", "info")
    return redirect(url_for("login"))


# ==============================================================================
# RUTA PRINCIPAL - DASHBOARD
# ==============================================================================
@aplicacion.route("/")
@login_required
def inicio():
    """
    Vista principal del sistema. Muestra un dashboard con estadísticas clave,
    habitaciones disponibles y las reservas más recientes. Requiere autenticación.
    """
    total_habitaciones = Habitacion.query.count()
    habitaciones_disponibles = Habitacion.query.filter_by(estado_hab="Disponible").count()
    total_clientes = Cliente.query.count()
    total_reservas = Reserva.query.count()

    lista_disponibles = Habitacion.query.filter_by(estado_hab="Disponible").limit(5).all()
    ultimas_reservas = Reserva.query.order_by(Reserva.id.desc()).limit(5).all()

    return render_template(
        "index.html",
        total_habitaciones=total_habitaciones,
        habitaciones_disponibles=habitaciones_disponibles,
        total_clientes=total_clientes,
        total_reservas=total_reservas,
        lista_disponibles=lista_disponibles,
        ultimas_reservas=ultimas_reservas
    )


# ==============================================================================
# CRUD HABITACIONES
# ==============================================================================
@aplicacion.route("/habitaciones", methods=["GET", "POST"])
@login_required
def habitaciones():
    """
    Muestra la lista de todas las habitaciones y permite registrar nuevas.
    """
    formulario = HabitacionForm()

    if formulario.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión para registrar habitaciones.", "warning")
            return redirect(url_for("login", next=request.url))

        habitacion_existente = Habitacion.query.filter_by(
            numero_hab=formulario.numero_hab.data
        ).first()

        if habitacion_existente:
            flash(f"La habitación #{formulario.numero_hab.data} ya se encuentra registrada.", "danger")
            return redirect(url_for("habitaciones"))

        nueva_habitacion = Habitacion(
            numero_hab=formulario.numero_hab.data,
            tipo_hab=formulario.tipo_hab.data,
            precio_noche_hab=formulario.precio_noche_hab.data,
            estado_hab=formulario.estado_hab.data
        )
        database.session.add(nueva_habitacion)
        database.session.commit()

        flash(f"Habitación #{nueva_habitacion.numero_hab} registrada con éxito.", "success")
        return redirect(url_for("habitaciones"))

    lista_habitaciones = Habitacion.query.order_by(Habitacion.numero_hab.asc()).all()
    return render_template(
        "habitaciones.html",
        habitaciones=lista_habitaciones,
        formulario=formulario
    )


@aplicacion.route("/habitaciones/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_habitacion(id):
    """
    Permite modificar los datos de una habitación existente. Protegida con autenticación.
    """
    habitacion = Habitacion.query.get_or_404(id)
    formulario = HabitacionForm(obj=habitacion)

    if formulario.validate_on_submit():
        hab_repetida = Habitacion.query.filter(
            Habitacion.numero_hab == formulario.numero_hab.data,
            Habitacion.id != id
        ).first()

        if hab_repetida:
            flash(f"El número #{formulario.numero_hab.data} ya está asignado a otra habitación.", "danger")
            return render_template("editar_habitacion.html", formulario=formulario, habitacion=habitacion)

        habitacion.numero_hab = formulario.numero_hab.data
        habitacion.tipo_hab = formulario.tipo_hab.data
        habitacion.precio_noche_hab = formulario.precio_noche_hab.data
        habitacion.estado_hab = formulario.estado_hab.data

        database.session.commit()
        flash(f"Habitación #{habitacion.numero_hab} actualizada con éxito.", "success")
        return redirect(url_for("habitaciones"))

    return render_template("editar_habitacion.html", formulario=formulario, habitacion=habitacion)


@aplicacion.route("/habitaciones/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_habitacion(id):
    """
    Elimina una habitación del sistema si no tiene reservas activas. Protegida con autenticación.
    """
    habitacion = Habitacion.query.get_or_404(id)

    reservas_asociadas = Reserva.query.filter_by(habitacion_id=id).count()
    if reservas_asociadas > 0:
        flash(f"No se puede eliminar la habitación #{habitacion.numero_hab} porque tiene {reservas_asociadas} reserva(s) asociada(s).", "warning")
        return redirect(url_for("habitaciones"))

    database.session.delete(habitacion)
    database.session.commit()
    flash(f"Habitación #{habitacion.numero_hab} eliminada correctamente.", "info")
    return redirect(url_for("habitaciones"))


# ==============================================================================
# CRUD CLIENTES
# ==============================================================================
@aplicacion.route("/clientes", methods=["GET", "POST"])
@login_required
def clientes():
    """
    Muestra la lista de clientes y permite registrar uno nuevo
    (creación restringida a usuarios autenticados).
    """
    formulario = ClienteForm()

    if formulario.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión para registrar nuevos huéspedes.", "warning")
            return redirect(url_for("login", next=request.url))

        if Cliente.query.filter_by(id_documento=formulario.id_documento.data).first():
            flash(f"Ya existe un huésped con el documento '{formulario.id_documento.data}'.", "danger")
            return redirect(url_for("clientes"))

        if Cliente.query.filter_by(correo=formulario.correo.data).first():
            flash(f"Ya existe un huésped con el correo '{formulario.correo.data}'.", "danger")
            return redirect(url_for("clientes"))

        nuevo_cliente = Cliente(
            nombre=formulario.nombre.data,
            apellido=formulario.apellido.data,
            id_documento=formulario.id_documento.data,
            telefono=formulario.telefono.data,
            correo=formulario.correo.data,
            ciudad_residencia=formulario.ciudad_residencia.data,
            pais_residencia=formulario.pais_residencia.data
        )

        database.session.add(nuevo_cliente)
        database.session.commit()
        flash(f"Cliente '{nuevo_cliente.nombre} {nuevo_cliente.apellido}' registrado con éxito.", "success")
        return redirect(url_for("clientes"))

    lista_clientes = Cliente.query.order_by(Cliente.id.desc()).all()
    return render_template("clientes.html", formulario=formulario, clientes=lista_clientes)


@aplicacion.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_cliente(id):
    """
    Permite modificar los datos de un cliente existente. Protegida con autenticación.
    """
    cliente = Cliente.query.get_or_404(id)
    formulario = ClienteForm(obj=cliente)

    if formulario.validate_on_submit():
        doc_duplicado = Cliente.query.filter(
            Cliente.id_documento == formulario.id_documento.data,
            Cliente.id != id
        ).first()
        if doc_duplicado:
            flash(f"El documento '{formulario.id_documento.data}' ya está registrado con otro cliente.", "danger")
            return render_template("editar_cliente.html", formulario=formulario, cliente=cliente)

        correo_duplicado = Cliente.query.filter(
            Cliente.correo == formulario.correo.data,
            Cliente.id != id
        ).first()
        if correo_duplicado:
            flash(f"El correo '{formulario.correo.data}' ya está registrado con otro cliente.", "danger")
            return render_template("editar_cliente.html", formulario=formulario, cliente=cliente)

        cliente.nombre = formulario.nombre.data
        cliente.apellido = formulario.apellido.data
        cliente.id_documento = formulario.id_documento.data
        cliente.telefono = formulario.telefono.data
        cliente.correo = formulario.correo.data
        cliente.ciudad_residencia = formulario.ciudad_residencia.data
        cliente.pais_residencia = formulario.pais_residencia.data

        database.session.commit()
        flash(f"Datos del cliente '{cliente.nombre} {cliente.apellido}' actualizados.", "success")
        return redirect(url_for("clientes"))

    return render_template("editar_cliente.html", formulario=formulario, cliente=cliente)


@aplicacion.route("/clientes/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_cliente(id):
    """
    Elimina un cliente si no tiene reservas vinculadas. Protegida con autenticación.
    """
    cliente = Cliente.query.get_or_404(id)

    reservas_vinculadas = Reserva.query.filter_by(cliente_id=id).count()
    if reservas_vinculadas > 0:
        flash(f"No se puede eliminar a '{cliente.nombre} {cliente.apellido}' porque tiene {reservas_vinculadas} reserva(s) registradas.", "warning")
        return redirect(url_for("clientes"))

    database.session.delete(cliente)
    database.session.commit()
    flash(f"Cliente '{cliente.nombre} {cliente.apellido}' eliminado correctamente.", "info")
    return redirect(url_for("clientes"))


# ==============================================================================
# CRUD RESERVAS
# ==============================================================================
@aplicacion.route("/reservas", methods=["GET", "POST"])
@login_required
def reservas():
    """
    Muestra la lista de reservas y permite crear nuevas
    (creación restringida a usuarios autenticados).
    """
    formulario = ReservaForm()
    clientes = Cliente.query.order_by(Cliente.nombre.asc()).all()
    formulario.cliente_id.choices = [
        (cliente.id, f"{cliente.nombre} {cliente.apellido} - Doc: {cliente.id_documento}")
        for cliente in clientes
    ]

    habitaciones = Habitacion.query.filter(Habitacion.estado_hab.in_(["Disponible","Ocupada"])).order_by(Habitacion.numero_hab.asc()).all()
    formulario.habitacion_id.choices = [
        (hab.id, f"Hab. #{hab.numero_hab} ({hab.tipo_hab}) - ${hab.precio_noche_hab:.2f}/noche")
        for hab in habitaciones
    ]

    if formulario.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión para generar reservaciones.", "warning")
            return redirect(url_for("login", next=request.url))


        reserva_existente = Reserva.query.filter(
            Reserva.habitacion_id == formulario.habitacion_id.data,
            Reserva.estado.in_(["pendiente", "confirmada"]),
            Reserva.fecha_entrada < formulario.fecha_salida.data,
            Reserva.fecha_salida > formulario.fecha_entrada.data
        ).first()

        if reserva_existente is not None:
            flash(
                "La habitación ya está reservada para esas fechas.",
                "danger"
            )
            return redirect(url_for("reservas"))

        nueva_reserva = Reserva(
            cliente_id=formulario.cliente_id.data,
            habitacion_id=formulario.habitacion_id.data,
            fecha_entrada=formulario.fecha_entrada.data,
            fecha_salida=formulario.fecha_salida.data,
            estado=formulario.estado.data
        )

        if formulario.estado.data == "confirmada":
            hab = Habitacion.query.get(formulario.habitacion_id.data)
            if hab:
                hab.estado_hab = "Ocupada"

        database.session.add(nueva_reserva)
        database.session.commit()

        flash(f"Reserva #{nueva_reserva.id} creada exitosamente.", "success")
        return redirect(url_for("reservas"))

    lista_reservas = Reserva.query.order_by(Reserva.id.desc()).all()
    return render_template("reservas.html", formulario=formulario, reservas=lista_reservas)



@aplicacion.route("/reservas/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_reserva(id):
    """
    Permite modificar una reserva existente,
    evitando fechas pasadas y conflictos de fechas.
    """
    reserva = Reserva.query.get_or_404(id)
    formulario = ReservaForm(obj=reserva)

    clientes = Cliente.query.order_by(Cliente.nombre.asc()).all()
    formulario.cliente_id.choices = [
        (
            cliente.id,
            f"{cliente.nombre} {cliente.apellido} - Doc: {cliente.id_documento}"
        )
        for cliente in clientes
    ]

    habitaciones = Habitacion.query.filter(
        Habitacion.estado_hab.in_(["Disponible", "Ocupada"]),
        Habitacion.id != None
    ).order_by(Habitacion.numero_hab.asc()).all()

    formulario.habitacion_id.choices = [
        (
            hab.id,
            f"Hab. #{hab.numero_hab} ({hab.tipo_hab}) - "
            f"${hab.precio_noche_hab:.2f}/noche"
        )
        for hab in habitaciones
    ]

    if formulario.validate_on_submit():

        # 1. Impedir fechas de entrada anteriores a hoy
        if formulario.fecha_entrada.data < date.today():
            flash(
                "La fecha de entrada no puede ser anterior a hoy.",
                "danger"
            )
            return render_template(
                "editar_reserva.html",
                formulario=formulario,
                reserva=reserva
            )

        # 2. La salida debe ser posterior a la entrada
        if formulario.fecha_salida.data <= formulario.fecha_entrada.data:
            flash(
                "La fecha de salida debe ser posterior a la fecha de entrada.",
                "danger"
            )
            return render_template(
                "editar_reserva.html",
                formulario=formulario,
                reserva=reserva
            )

        # 3. Buscar conflictos con otras reservas
        reserva_existente = Reserva.query.filter(
            Reserva.habitacion_id == formulario.habitacion_id.data,
            Reserva.id != reserva.id,
            Reserva.estado.in_(["pendiente", "confirmada"]),
            Reserva.fecha_entrada < formulario.fecha_salida.data,
            Reserva.fecha_salida > formulario.fecha_entrada.data
        ).first()

        if reserva_existente is not None:
            flash(
                "La habitación ya está reservada para esas fechas.",
                "danger"
            )
            return render_template(
                "editar_reserva.html",
                formulario=formulario,
                reserva=reserva
            )

        # 4. Actualizar los datos de la reserva
        reserva.cliente_id = formulario.cliente_id.data
        reserva.habitacion_id = formulario.habitacion_id.data
        reserva.fecha_entrada = formulario.fecha_entrada.data
        reserva.fecha_salida = formulario.fecha_salida.data
        reserva.estado = formulario.estado.data

        # 5. Guardar los cambios
        database.session.commit()

        flash(
            f"Reserva #{reserva.id} actualizada correctamente.",
            "success"
        )
        return redirect(url_for("reservas"))

    return render_template(
        "editar_reserva.html",
        formulario=formulario,
        reserva=reserva
    )



@aplicacion.route("/reservas/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_reserva(id):
    """
    Elimina una reserva y libera la habitación si estaba ocupada. Protegida con autenticación.
    """
    reserva = Reserva.query.get_or_404(id)
    if reserva.habitacion and reserva.estado == "confirmada":
        reserva.habitacion.estado_hab = "Disponible"

    database.session.delete(reserva)
    database.session.commit()
    flash(f"Reserva #{id} eliminada correctamente.", "info")
    return redirect(url_for("reservas"))


# ==============================================================================
# MANEJADORES DE ERROR PERSONALIZADOS (404, 500)
# ==============================================================================
@aplicacion.errorhandler(404)
def error_404(error):
    return render_template("errors/404.html"), 404


@aplicacion.errorhandler(500)
def error_500(error):
    database.session.rollback()
    return render_template("errors/500.html"), 500