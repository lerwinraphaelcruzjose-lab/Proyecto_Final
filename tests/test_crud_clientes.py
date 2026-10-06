from app.models import Cliente
from app import database


def test_listar_clientes(auth_client):
    """Prueba que el listado de clientes carga con éxito para usuarios autenticados."""
    response = auth_client.get("/clientes")
    assert response.status_code == 200
    assert b"Clientes" in response.data or b"Directorio" in response.data


def test_crear_cliente_autenticado(auth_client):
    """Prueba registrar un huésped en el sistema."""
    response = auth_client.post(
        "/clientes",
        data={
            "nombre": "Mariana",
            "apellido": "López",
            "id_documento": "001-1234567-9",
            "telefono": "809-555-4321",
            "correo": "mariana@correo.com",
            "ciudad_residencia": "La Vega",
            "pais_residencia": "Rep. Dominicana"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"registrado con" in response.data

    cliente = Cliente.query.filter_by(id_documento="001-1234567-9").first()
    assert cliente is not None
    assert cliente.nombre == "Mariana"


def test_crear_cliente_documento_duplicado(auth_client, sample_data):
    """Prueba que no se permita duplicar documento de identidad de cliente."""
    response = auth_client.post(
        "/clientes",
        data={
            "nombre": "Carlos Segundo",
            "apellido": "Mendoza",
            "id_documento": "001-998877-1",  # ya existe en sample_data
            "telefono": "809-000-0000",
            "correo": "otro_carlos@test.com",
            "ciudad_residencia": "Santiago",
            "pais_residencia": "RD"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Ya existe un hu" in response.data or b"documento" in response.data


def test_editar_cliente(auth_client, sample_data):
    """Prueba modificar la información de un cliente."""
    cli_id = sample_data["cliente"].id
    response = auth_client.post(
        f"/clientes/editar/{cli_id}",
        data={
            "nombre": "Carlos Modificado",
            "apellido": "Mendoza Díaz",
            "id_documento": "001-998877-1",
            "telefono": "809-777-6655",
            "correo": "carlos_nuevo@test.com",
            "ciudad_residencia": "Puerto Plata",
            "pais_residencia": "Rep. Dominicana"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"actualizados" in response.data

    cli = Cliente.query.get(cli_id)
    assert cli.nombre == "Carlos Modificado"
    assert cli.telefono == "809-777-6655"


def test_eliminar_cliente_con_reserva_bloqueado(auth_client, sample_data):
    """Prueba que no se elimine un cliente con reservas activas."""
    cli_id = sample_data["cliente"].id
    response = auth_client.post(f"/clientes/eliminar/{cli_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"No se puede eliminar" in response.data
    assert Cliente.query.get(cli_id) is not None


def test_eliminar_cliente_sin_reserva(auth_client):
    """Prueba eliminar un cliente sin reservas asociadas."""
    cli = Cliente(
        nombre="Temporal",
        apellido="Prueba",
        id_documento="999-9999999-9",
        telefono="809-999-9999",
        correo="temp@prueba.com"
    )
    database.session.add(cli)
    database.session.commit()
    cli_id = cli.id

    response = auth_client.post(f"/clientes/eliminar/{cli_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"eliminado correctamente" in response.data
    assert Cliente.query.get(cli_id) is None
