from app.models import Usuario


def test_login_exitoso(client, sample_user):
    """Prueba inicio de sesión exitoso con credenciales correctas."""
    response = client.post(
        "/login",
        data={"username": "admin_test", "password": "secreto123"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Bienvenido de nuevo" in response.data or b"admin_test" in response.data


def test_login_credenciales_invalidas(client, sample_user):
    """Prueba intento de inicio de sesión con contraseña errónea."""
    response = client.post(
        "/login",
        data={"username": "admin_test", "password": "clave_falsa"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"incorrectos" in response.data


def test_registro_nuevo_usuario(client):
    """Prueba el registro de una cuenta nueva de usuario."""
    response = client.post(
        "/registro",
        data={
            "nombre_completo": "Ana Torres",
            "username": "atorres",
            "email": "ana@hotel.com",
            "password": "contrasenaSegura1",
            "confirm_password": "contrasenaSegura1"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    usuario = Usuario.query.filter_by(username="atorres").first()
    assert usuario is not None
    assert usuario.email == "ana@hotel.com"


def test_registro_usuario_duplicado(client, sample_user):
    """Prueba que no se permita registrar un usuario con nombre ya existente."""
    response = client.post(
        "/registro",
        data={
            "nombre_completo": "Otro Admin",
            "username": "admin_test",
            "email": "otro@hotel.com",
            "password": "password123",
            "confirm_password": "password123"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"en uso" in response.data


def test_logout(auth_client):
    """Prueba el cierre de sesión."""
    response = auth_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"cerrado" in response.data


def test_proteccion_rutas_sin_autenticacion(client, sample_data):
    """Verifica que las operaciones de edición y eliminación requieran autenticación."""
    hab_id = sample_data["habitacion"].id
    cli_id = sample_data["cliente"].id
    res_id = sample_data["reserva"].id

    # Intentos sin login deben responder con redirección (302) a /login
    assert client.get(f"/habitaciones/editar/{hab_id}").status_code == 302
    assert client.post(f"/habitaciones/eliminar/{hab_id}").status_code == 302
    assert client.get(f"/clientes/editar/{cli_id}").status_code == 302
    assert client.post(f"/clientes/eliminar/{cli_id}").status_code == 302
    assert client.get(f"/reservas/editar/{res_id}").status_code == 302
    assert client.post(f"/reservas/eliminar/{res_id}").status_code == 302
