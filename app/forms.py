from flask_wtf import FlaskForm
from wtforms import (
    IntegerField, StringField, FloatField, SubmitField,
    SelectField, DateField, PasswordField, BooleanField
)
from wtforms.validators import (
    DataRequired, Optional, Email, ValidationError,
    NumberRange, Length, EqualTo
)
from datetime import date


# ==============================================================================
# FORMULARIOS DE AUTENTICACIÓN
# ==============================================================================
class LoginForm(FlaskForm):
    """Formulario para inicio de sesión de usuarios."""
    username = StringField(
        "Nombre de Usuario",
        validators=[DataRequired(message="El usuario es requerido.")]
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="La contraseña es requerida.")]
    )
    recordar = BooleanField("Recordar sesión")
    enviar = SubmitField("Iniciar Sesión")


class RegistroForm(FlaskForm):
    """Formulario para el registro de nuevos usuarios en el sistema."""
    nombre_completo = StringField("Nombre Completo", validators=[Optional()])
    username = StringField(
        "Nombre de Usuario",
        validators=[
            DataRequired(message="El nombre de usuario es requerido."),
            Length(min=3, max=30, message="El usuario debe tener entre 3 y 30 caracteres.")
        ]
    )
    email = StringField(
        "Correo Electrónico",
        validators=[
            DataRequired(message="El correo es requerido."),
            Email(message="Introduce un correo electrónico válido.")
        ]
    )
    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es requerida."),
            Length(min=6, message="La contraseña debe contener al menos 6 caracteres.")
        ]
    )
    confirm_password = PasswordField(
        "Confirmar Contraseña",
        validators=[
            DataRequired(message="Por favor confirma tu contraseña."),
            EqualTo("password", message="Las contraseñas no coinciden.")
        ]
    )
    enviar = SubmitField("Crear Cuenta")


# ==============================================================================
# FORMULARIOS DEL CRUD
# ==============================================================================
class HabitacionForm(FlaskForm):
    """Formulario para la creación y edición de habitaciones."""
    numero_hab = IntegerField(
        "Número de Habitación",
        validators=[
            DataRequired(message="El número de habitación es obligatorio."),
            NumberRange(min=1, message="El número de habitación debe ser positivo.")
        ]
    )
    tipo_hab = SelectField(
        "Tipo de Habitación",
        choices=[
            ("Sencilla", "Sencilla"),
            ("Doble", "Doble"),
            ("Suite", "Suite")
        ]
    )
    precio_noche_hab = FloatField(
        "Precio por Noche",
        validators=[
            DataRequired(message="El precio por noche es obligatorio."),
            NumberRange(min=0, message="El precio no puede ser negativo.")
        ],
        render_kw={"min": "0", "step": "0.01"}
    )
    estado_hab = SelectField(
        "Estado de la Habitación",
        choices=[
            ("Disponible", "Disponible"),
            ("Ocupada", "Ocupada"),
            ("Mantenimiento", "Mantenimiento")
        ]
    )
    enviar = SubmitField("Guardar Habitación")


class ClienteForm(FlaskForm):
    """Formulario para el registro y actualización de huéspedes."""
    nombre = StringField("Nombre", validators=[DataRequired(message="El nombre es obligatorio.")])
    apellido = StringField("Apellido", validators=[DataRequired(message="El apellido es obligatorio.")])
    id_documento = StringField("Documento de Identidad / Cédula", validators=[DataRequired(message="El documento es obligatorio.")])
    telefono = StringField("Número de Teléfono", validators=[DataRequired(message="El teléfono es obligatorio.")])
    correo = StringField(
        "Correo Electrónico",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Introduce un correo electrónico válido.")
        ]
    )
    ciudad_residencia = StringField("Ciudad de Residencia", validators=[Optional()])
    pais_residencia = StringField("País de Residencia", validators=[Optional()])
    enviar = SubmitField("Guardar Huésped")


class ReservaForm(FlaskForm):
    """Formulario para la asignación y gestión de reservas."""
    cliente_id = SelectField("Huésped / Cliente", coerce=int, validators=[DataRequired(message="Selecciona un cliente.")])
    habitacion_id = SelectField("Habitación", coerce=int, validators=[DataRequired(message="Selecciona una habitación.")])
    fecha_entrada = DateField("Fecha de Entrada", validators=[DataRequired(message="La fecha de entrada es requerida.")], render_kw={"type": "date"})
    fecha_salida = DateField("Fecha de Salida", validators=[DataRequired(message="La fecha de salida es requerida.")], render_kw={"type": "date"})

    def validate_fecha_entrada(self, field):
        """Valida que la fecha de entrada no sea anterior a hoy."""
        if field.data and field.data < date.today():
            raise ValidationError("La fecha de entrada no puede ser anterior al día de hoy.")

    def validate_fecha_salida(self, field):
        """Valida que la fecha de salida sea posterior a la fecha de entrada."""
        if field.data and self.fecha_entrada.data and field.data <= self.fecha_entrada.data:
            raise ValidationError("La fecha de salida debe ser posterior a la fecha de entrada.")

    estado = SelectField(
        "Estado de la Reserva",
        choices=[
            ("pendiente", "Pendiente"),
            ("confirmada", "Confirmada"),
            ("cancelada", "Cancelada"),
            ("completada", "Completada")
        ],
        validators=[DataRequired(message="Selecciona un estado.")]
    )
    enviar = SubmitField("Guardar Reserva")
