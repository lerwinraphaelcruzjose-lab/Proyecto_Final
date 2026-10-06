from datetime import date, timedelta
from app.models import Reserva, Habitacion
from app import database


def test_listar_reservas(auth_client):
    """Prueba que el listado de reservas cargue correctamente para usuarios autenticados."""
    response = auth_client.get("/reservas")
    assert response.status_code == 200
    assert b"Reservas" in response.data


def test_crear_reserva_confirmada(auth_client, sample_data):
    """Prueba crear una nueva reserva y que actualice el estado de la habitación a Ocupada."""
    # Crear una nueva habitación disponible
    hab2 = Habitacion(
        numero_hab=601,
        tipo_hab="Doble",
        precio_noche_hab=90.0,
        estado_hab="Disponible"
    )
    database.session.add(hab2)
    database.session.commit()

    cli_id = sample_data["cliente"].id
    entrada = date.today() + timedelta(days=5)
    salida = date.today() + timedelta(days=8)

    response = auth_client.post(
        "/reservas",
        data={
            "cliente_id": cli_id,
            "habitacion_id": hab2.id,
            "fecha_entrada": entrada.strftime("%Y-%m-%d"),
            "fecha_salida": salida.strftime("%Y-%m-%d"),
            "estado": "confirmada"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"creada exitosamente" in response.data

    # Verificar estado de la habitación
    hab_actualizada = Habitacion.query.get(hab2.id)
    assert hab_actualizada.estado_hab == "Ocupada"


def test_editar_reserva(auth_client, sample_data):
    """Prueba la edición de fechas y estado de una reserva."""
    res_id = sample_data["reserva"].id
    cli_id = sample_data["cliente"].id
    hab_id = sample_data["habitacion"].id

    nueva_entrada = date.today() + timedelta(days=1)
    nueva_salida = date.today() + timedelta(days=4)

    response = auth_client.post(
        f"/reservas/editar/{res_id}",
        data={
            "cliente_id": cli_id,
            "habitacion_id": hab_id,
            "fecha_entrada": nueva_entrada.strftime("%Y-%m-%d"),
            "fecha_salida": nueva_salida.strftime("%Y-%m-%d"),
            "estado": "cancelada"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"actualizada correctamente" in response.data

    reserva = Reserva.query.get(res_id)
    assert reserva.estado == "cancelada"

    # Al cancelarse, la habitación debe volver a estar disponible
    hab = Habitacion.query.get(hab_id)
    assert hab.estado_hab == "Disponible"


def test_eliminar_reserva(auth_client, sample_data):
    """Prueba eliminar una reserva y liberar la habitación."""
    res_id = sample_data["reserva"].id
    hab_id = sample_data["habitacion"].id

    response = auth_client.post(f"/reservas/eliminar/{res_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"eliminada correctamente" in response.data

    assert Reserva.query.get(res_id) is None
    hab = Habitacion.query.get(hab_id)
    assert hab.estado_hab == "Disponible"
