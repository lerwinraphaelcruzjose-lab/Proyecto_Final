from app import database
from sqlalchemy.orm import Mapped,mapped_column, relationship
from datetime import date
from sqlalchemy import ForeignKey


class Habitacion(database.Model):
    __tablename__="habitaciones"

    id:Mapped[int]= mapped_column(primary_key=True)
    numero_hab: Mapped[int] = mapped_column()
    tipo_hab: Mapped[str] = mapped_column()
    precio_noche_hab:Mapped[float] = mapped_column()
    estado_hab: Mapped[int] = mapped_column()


class Cliente(database.Model):
    __tablename__="clientes"

    id:Mapped[int] = mapped_column(primary_key=True)
    nombre:Mapped[str] = mapped_column()
    apellido:Mapped[str] = mapped_column()
    id_documento:Mapped[str] = mapped_column(unique=True)
    telefono:Mapped[str] = mapped_column()
    correo:Mapped[str] = mapped_column(unique=True)
    ciudad_residencia:Mapped[str | None] = mapped_column()
    pais_residencia:Mapped[str | None] = mapped_column()
    fecha_registro:Mapped[date] = mapped_column(default=date.today)
    

class Reserva(database.Model):
    __tablename__ = "reservas"

    id: Mapped[int]=mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"))
    cliente: Mapped["Cliente"] = relationship("Cliente")
    habitacion_id: Mapped[int] = mapped_column(ForeignKey("habitaciones.id"))
    habitacion: Mapped["Habitacion"] = relationship("Habitacion")
    fecha_entrada: Mapped[date] = mapped_column()
    fecha_salida: Mapped[date] = mapped_column()
    estado: Mapped[str] = mapped_column()