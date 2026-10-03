from app import aplicacion, database
from app.models import Habitacion, Cliente, Reserva
from app.forms import HabitacionForm, ClienteForm, ReservaForm
from flask import render_template , redirect



@aplicacion.route("/")
def inicio():
    return"Mi Proyecto Final"

#Ruta_Crear_Habitacion
@aplicacion.route("/habitaciones",methods=["GET", "POST"])
def habitaciones():

    formulario = HabitacionForm()
    if formulario.validate_on_submit():

        habitacion_existente = Habitacion.query.filter_by(
            numero_hab=formulario.numero_hab.data
        ).first()

        if habitacion_existente:
            print("LA HABITACION YA EXISTE")
            return redirect("/habitaciones")

        nueva_habitacion = Habitacion(
            numero_hab=formulario.numero_hab.data,
            tipo_hab=formulario.tipo_hab.data,
            precio_noche_hab=formulario.precio_noche_hab.data,
            estado_hab=formulario.estado_hab.data
        )
        database.session.add(nueva_habitacion)
        database.session.commit()

        return redirect("/habitaciones")
    
    habitaciones = Habitacion.query.all()

    return render_template("habitaciones.html",
                            habitaciones=habitaciones,
                              formulario = formulario
                              )


#Ruta_Editar_Habitacion
@aplicacion.route("/habitaciones/editar/<int:id>", methods=["GET", "POST"])
def editar_habitacion(id):

    # Busca la habitación por su ID.
    # Si no existe, Flask devuelve un error 404.
    habitacion = Habitacion.query.get_or_404(id)

    # Crea el formulario usando los datos actuales
    # de la habitación para rellenar los campos.
    formulario = HabitacionForm(obj=habitacion)

    # Comprueba si el formulario fue enviado mediante POST
    # y si todos sus datos son válidos.
    if formulario.validate_on_submit():
    


        # Actualiza los datos de la habitación existente.
        habitacion.tipo_hab = formulario.tipo_hab.data
        habitacion.precio_noche_hab = formulario.precio_noche_hab.data
        habitacion.estado_hab = formulario.estado_hab.data

        # Confirma los cambios en la base de datos.
        database.session.commit()

        # Regresa a la página de habitaciones.
        return redirect("/habitaciones")

    # Si todavía no se ha enviado el formulario,
    # muestra la página de edición.
    return render_template(
        "editar_habitacion.html",
        formulario=formulario
    )







#Ruta_Eliminar_Habitacion
@aplicacion.route("/habitaciones/eliminar/<int:id>",methods=["POST"])
def eliminar_habitacion(id):
    habitacion = Habitacion.query.get_or_404(id)
    
    database.session.delete(habitacion)
    database.session.commit()

    return redirect("/habitaciones")







#Ruta Clientes
@aplicacion.route("/clientes",methods=["GET", "POST"])
def clientes():
    formulario = ClienteForm()
    clientes = Cliente.query.all()

    if formulario.validate_on_submit():

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

        return redirect("/clientes")

    return render_template("clientes.html", formulario=formulario,clientes=clientes)


@aplicacion.route("/clientes/eliminar/<int:id>", methods=["POST"])
def eliminar_cliente(id):

    cliente = Cliente.query.get_or_404(id)

    database.session.delete(cliente)
    database.session.commit()

    return redirect("/clientes")


@aplicacion.route("/clientes/editar/<int:id>",methods=["GET", "POST"])
def editar_cliente(id):

    cliente = Cliente.query.get_or_404(id)
    formulario=ClienteForm(obj=cliente)


    if formulario.validate_on_submit():
        cliente.nombre = formulario.nombre.data
        cliente.apellido = formulario.apellido.data
        cliente.id_documento = formulario.id_documento.data
        cliente.telefono = formulario.telefono.data
        cliente.correo = formulario.correo.data
        cliente.ciudad_residencia = formulario.ciudad_residencia.data
        cliente.pais_residencia = formulario.pais_residencia.data

        database.session.commit()
        return redirect("/clientes")

    return render_template("editar_cliente.html", formulario=formulario)

@aplicacion.route("/reservas", methods=["GET", "POST"])
def reservas():
    

    formulario = ReservaForm()
    clientes = Cliente.query.all()
    formulario.cliente_id.choices =[
        (cliente.id, f"{cliente.nombre}{cliente.apellido}- {cliente.id_documento}")
        for cliente in clientes
    ]

    habitaciones = Habitacion.query.filter_by(estado_hab="Disponible").all()
    formulario.habitacion_id.choices = [
    (habitacion.id, f"Habitación {habitacion.numero_hab}")
    for habitacion in habitaciones
]

    if formulario.validate_on_submit():
        nueva_reserva = Reserva(
        cliente_id=formulario.cliente_id.data,
        habitacion_id=formulario.habitacion_id.data,
        fecha_entrada=formulario.fecha_entrada.data,
        fecha_salida=formulario.fecha_salida.data,
        estado=formulario.estado.data
        )

        database.session.add(nueva_reserva)
        database.session.commit()

        return redirect("/reservas")

    return render_template("reservas.html", formulario=formulario)

#return f"{habitacion.numero_hab} - {habitacion.tipo_hab} - {habitacion.precio_noche_hab} - {habitacion.estado_hab}"//