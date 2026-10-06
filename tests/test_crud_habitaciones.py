from app.models import Habitacion
from app import database


def test_listar_habitaciones(auth_client):
    """Prueba que la página de habitaciones responde correctamente para usuarios autenticados."""
    response = auth_client.get("/habitaciones")
    assert response.status_code == 200
    assert b"Habitaciones" in response.data


def test_crear_habitacion_autenticado(auth_client):
    """Prueba crear una habitación estando autenticado."""
    response = auth_client.post(
        "/habitaciones",
        data={
            "numero_hab": 204,
            "tipo_hab": "Doble",
            "precio_noche_hab": 85.0,
            "estado_hab": "Disponible"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"registrada con" in response.data

    hab = Habitacion.query.filter_by(numero_hab=204).first()
    assert hab is not None
    assert hab.tipo_hab == "Doble"


def test_crear_habitacion_duplicada(auth_client, sample_data):
    """Prueba que no se puedan duplicar números de habitación."""
    response = auth_client.post(
        "/habitaciones",
        data={
            "numero_hab": 501,  # ya existe en sample_data
            "tipo_hab": "Sencilla",
            "precio_noche_hab": 50.0,
            "estado_hab": "Disponible"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"ya se encuentra registrada" in response.data


def test_editar_habitacion(auth_client, sample_data):
    """Prueba la edición de datos de una habitación."""
    hab_id = sample_data["habitacion"].id
    response = auth_client.post(
        f"/habitaciones/editar/{hab_id}",
        data={
            "numero_hab": 501,
            "tipo_hab": "Doble",
            "precio_noche_hab": 250.0,
            "estado_hab": "Mantenimiento"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"actualizada con" in response.data

    hab = Habitacion.query.get(hab_id)
    assert hab.tipo_hab == "Doble"
    assert hab.precio_noche_hab == 250.0
    assert hab.estado_hab == "Mantenimiento"


def test_eliminar_habitacion_con_reserva_bloqueada(auth_client, sample_data):
    """Prueba que no se pueda eliminar una habitación vinculada a una reserva."""
    hab_id = sample_data["habitacion"].id
    response = auth_client.post(f"/habitaciones/eliminar/{hab_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"No se puede eliminar" in response.data

    # La habitación debe seguir existiendo
    assert Habitacion.query.get(hab_id) is not None


def test_eliminar_habitacion_sin_reserva(auth_client):
    """Prueba eliminar una habitación libre de reservas."""
    hab = Habitacion(
        numero_hab=999,
        tipo_hab="Sencilla",
        precio_noche_hab=40.0,
        estado_hab="Disponible"
    )
    database.session.add(hab)
    database.session.commit()
    hab_id = hab.id

    response = auth_client.post(f"/habitaciones/eliminar/{hab_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"eliminada correctamente" in response.data
    assert Habitacion.query.get(hab_id) is None
