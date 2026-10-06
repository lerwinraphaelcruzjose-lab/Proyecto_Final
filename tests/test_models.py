from datetime import date, timedelta
import pytest
from sqlalchemy.exc import IntegrityError
from app import database
from app.models import Usuario, Habitacion, Cliente, Reserva


def test_modelo_usuario(app):
    """Verifica la creación del usuario y el hashing de contraseña."""
    usuario = Usuario(
        username="recepcionista1",
        email="recepcion@hotel.com",
        nombre_completo="Recepcionista Principal"
    )
    usuario.set_password("claveSegura2026")
    database.session.add(usuario)
    database.session.commit()

    assert usuario.id is not None
    assert usuario.username == "recepcionista1"
    assert usuario.check_password("claveSegura2026") is True
    assert usuario.check_password("claveIncorrecta") is False
    assert usuario.is_authenticated is True
    assert repr(usuario) == "<Usuario recepcionista1>"


def test_modelo_habitacion(app):
    """Verifica la creación y propiedades del modelo Habitacion."""
    hab = Habitacion(
        numero_hab=301,
        tipo_hab="Doble",
        precio_noche_hab=75.50,
        estado_hab="Disponible"
    )
    database.session.add(hab)
    database.session.commit()

    assert hab.id is not None
    assert hab.numero_hab == 301
    assert hab.precio_noche_hab == 75.50
    assert repr(hab) == "<Habitacion #301 - Doble>"


def test_modelo_cliente_unicidad(app):
    """Verifica restricciones de unicidad en Cliente (documento y correo)."""
    cli1 = Cliente(
        nombre="Laura",
        apellido="García",
        id_documento="402-0001112-3",
        telefono="809-123-4567",
        correo="laura@example.com",
        ciudad_residencia="Santo Domingo",
        pais_residencia="Rep. Dominicana"
    )
    database.session.add(cli1)
    database.session.commit()

    # Intentar registrar otro cliente con el mismo documento
    cli2 = Cliente(
        nombre="Laura",
        apellido="Pérez",
        id_documento="402-0001112-3",
        telefono="809-999-8888",
        correo="otra_laura@example.com"
    )
    database.session.add(cli2)
    with pytest.raises(IntegrityError):
        database.session.commit()
    database.session.rollback()


def test_modelo_reserva_relaciones(app, sample_data):
    """Verifica que el modelo Reserva se relacione correctamente con Cliente y Habitacion."""
    reserva = sample_data["reserva"]

    assert reserva.id is not None
    assert reserva.cliente.nombre == "Carlos"
    assert reserva.habitacion.numero_hab == 501
    assert reserva.estado == "confirmada"
    assert repr(reserva) == f"<Reserva #{reserva.id} - Hab {reserva.habitacion_id}>"
