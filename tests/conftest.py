import os

# Configurar variables de entorno antes de importar la aplicación
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["WTF_CSRF_ENABLED"] = "False"
os.environ["FLASK_DEBUG"] = "False"

import pytest
from datetime import date, timedelta
from app import aplicacion, database
from app.models import Usuario, Habitacion, Cliente, Reserva
from config import TestingConfig


@pytest.fixture
def app():
    """Configura la aplicación en modo de pruebas con base de datos en memoria."""
    aplicacion.config.from_object(TestingConfig)

    with aplicacion.app_context():
        database.create_all()
        yield aplicacion
        database.session.rollback()
        database.drop_all()


@pytest.fixture
def client(app):
    """Cliente HTTP sin autenticar."""
    return app.test_client()


@pytest.fixture
def sample_user(app):
    """Crea un usuario administrador de prueba."""
    usuario = Usuario(
        username="admin_test",
        email="admintest@hotel.com",
        nombre_completo="Admin Test"
    )
    usuario.set_password("secreto123")
    database.session.add(usuario)
    database.session.commit()
    return usuario


@pytest.fixture
def auth_client(client, sample_user):
    """Cliente HTTP con sesión activa del usuario administrador de prueba."""
    client.post(
        "/login",
        data={"username": "admin_test", "password": "secreto123"},
        follow_redirects=True
    )
    return client


@pytest.fixture
def sample_data(app):
    """Crea registros base de habitación, cliente y reserva."""
    hab = Habitacion(
        numero_hab=501,
        tipo_hab="Suite",
        precio_noche_hab=120.0,
        estado_hab="Disponible"
    )
    cli = Cliente(
        nombre="Carlos",
        apellido="Mendoza",
        id_documento="001-998877-1",
        telefono="809-555-9988",
        correo="carlos@test.com",
        ciudad_residencia="Santiago",
        pais_residencia="República Dominicana",
        fecha_registro=date.today()
    )
    database.session.add_all([hab, cli])
    database.session.commit()

    res = Reserva(
        cliente_id=cli.id,
        habitacion_id=hab.id,
        fecha_entrada=date.today(),
        fecha_salida=date.today() + timedelta(days=2),
        estado="confirmada"
    )
    database.session.add(res)
    database.session.commit()

    return {"habitacion": hab, "cliente": cli, "reserva": res}
