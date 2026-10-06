from app import database
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from sqlalchemy import ForeignKey, String
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(database.Model, UserMixin):
    """
    Modelo para la autenticación y gestión de usuarios del sistema.
    Hereda de UserMixin para compatibilidad con Flask-Login.
    """
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    nombre_completo: Mapped[str | None] = mapped_column(String(100), default=None)
    rol: Mapped[str] = mapped_column(String(20), default="admin")
    fecha_creacion: Mapped[date] = mapped_column(default=date.today)

    def set_password(self, password: str) -> None:
        """Genera el hash seguro de la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña ingresada coincide con el hash almacenado."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<Usuario {self.username}>"


class Habitacion(database.Model):
    """
    Modelo que representa una habitación física dentro del hotel.
    """
    __tablename__ = "habitaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero_hab: Mapped[int] = mapped_column(unique=True)
    tipo_hab: Mapped[str] = mapped_column(String(50))
    precio_noche_hab: Mapped[float] = mapped_column()
    estado_hab: Mapped[str] = mapped_column(String(30), default="Disponible")

    def __repr__(self) -> str:
        return f"<Habitacion #{self.numero_hab} - {self.tipo_hab}>"


class Cliente(database.Model):
    """
    Modelo que almacena la información de huéspedes y clientes registrados.
    """
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60))
    apellido: Mapped[str] = mapped_column(String(60))
    id_documento: Mapped[str] = mapped_column(String(30), unique=True)
    telefono: Mapped[str] = mapped_column(String(25))
    correo: Mapped[str] = mapped_column(String(120), unique=True)
    ciudad_residencia: Mapped[str | None] = mapped_column(String(80), nullable=True)
    pais_residencia: Mapped[str | None] = mapped_column(String(80), nullable=True)
    fecha_registro: Mapped[date] = mapped_column(default=date.today)

    def __repr__(self) -> str:
        return f"<Cliente {self.nombre} {self.apellido}>"


class Reserva(database.Model):
    """
    Modelo que vincula a un huésped con una habitación durante un período de fechas.
    """
    __tablename__ = "reservas"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    cliente: Mapped["Cliente"] = relationship("Cliente")
    habitacion_id: Mapped[int] = mapped_column(ForeignKey("habitaciones.id"))
    habitacion: Mapped["Habitacion"] = relationship("Habitacion")
    fecha_entrada: Mapped[date] = mapped_column()
    fecha_salida: Mapped[date] = mapped_column()
    estado: Mapped[str] = mapped_column(String(30), default="pendiente")

    def __repr__(self) -> str:
        return f"<Reserva #{self.id} - Hab {self.habitacion_id}>"