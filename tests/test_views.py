def test_dashboard_redirige_a_login_sin_autenticacion(client):
    """Verifica que al entrar a la raíz sin iniciar sesión redirija a /login."""
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_dashboard_principal_autenticado(auth_client, sample_data):
    """Verifica que el dashboard responda con status 200 y métricas para usuarios autenticados."""
    response = auth_client.get("/")
    assert response.status_code == 200
    assert b"Panel de Control" in response.data
    assert b"Habitaciones" in response.data
    assert b"Carlos" in response.data


def test_pagina_error_404(client):
    """Verifica que rutas inexistentes rendericen la página 404 personalizada."""
    response = client.get("/esta-ruta-no-existe-12345")
    assert response.status_code == 404
    assert b"404" in response.data
    assert b"encontrada" in response.data
