from app import aplicacion, database
from app.models import Usuario


if __name__ == "__main__":
    # Asegurar la creación de tablas y el usuario inicial antes de iniciar el servidor
    with aplicacion.app_context():
        database.create_all()

        if not Usuario.query.filter_by(username="admin").first():
            admin = Usuario(
                username="admin",
                email="admin@hotel.com",
                nombre_completo="Administrador del Hotel"
            )
            admin.set_password("admin123")
            database.session.add(admin)
            database.session.commit()

    aplicacion.run(port=5001)