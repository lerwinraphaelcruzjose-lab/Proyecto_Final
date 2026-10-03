from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, FloatField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Optional,Email,ValidationError,NumberRange
from datetime import date


class HabitacionForm(FlaskForm):
    numero_hab = IntegerField("Numero de Habitacion", validators=[DataRequired(), NumberRange(min=1)])
    tipo_hab = SelectField("Tipo de Habitacion",
                           choices=[
                               ("Sencilla","Sencilla"),
                               ("Doble","Doble"),
                               ("Suite","Suite")
                           ]
    )
    precio_noche_hab = FloatField("Precio por Noche", validators=[DataRequired(), NumberRange(min=0)],render_kw={"min": "0"})
    def validate_precio_noche_hab(self, field):
        if field.data < 0:
            raise ValidationError("El precio por noche no puede ser negativo")
    estado_hab = SelectField("Estado de la Habitacion",
                               choices=[
                                   ("Disponible","Disponible"),
                                   ("Ocupada","Ocupada"),
                                   ("Mantenimiento","Mantenimiento")
                               ]
    )
    
   

    
    enviar = SubmitField("Guardar")



class ClienteForm(FlaskForm):
    nombre = StringField("Nombre",validators=[DataRequired()])
    apellido = StringField("Apellido",validators=[DataRequired()])
    id_documento = StringField("ID Documento",validators=[DataRequired()])
    telefono = StringField("Numero Telefono",validators=[DataRequired()])
    correo = StringField("Correo",validators=[DataRequired(),Email(message="Introduce un correo válido.")])
    ciudad_residencia = StringField("Ciudad de Residencia",validators=[Optional()])
    pais_residencia = StringField("Pais de Residencia",validators=[Optional()])
    
    enviar=SubmitField("Guardar")




class ReservaForm(FlaskForm):
    cliente_id = SelectField("Cliente",coerce=int)
    habitacion_id = SelectField("Habitacion",coerce=int)
    fecha_entrada = DateField("Fecha de entrada",validators=[DataRequired()],render_kw={"type":"date"} )

    def validate_fecha_entrada(self,field):
        if field.data < date.today():
            raise ValidationError("La fecha de entrada no puede ser anterior a hoy")
    
    
    fecha_salida = DateField("Fecha de salida",validators=[DataRequired()],render_kw={"type":"date"})

    def validate_fecha_salida(self,field):
        if field.data <= self.fecha_entrada.data:
            raise ValidationError("La fecha de salida deber ser posterior a la fecha de entrada")


    estado = SelectField(
        "Estado",
        choices=[
            ("pendiente", "Pendiente"),
            ("confirmada", "Confirmada"),
            ("cancelada", "Cancelada"),
            ("completada", "Completada")
        ],
        validators=[DataRequired()]
    )
        

    enviar = SubmitField("Guardar")  







"""class ReservaForm(FlaskForm):
    cliente_id = SelectField("Cliente", coerce=int)
    habitacion_id = SelectField("Habitacion", coerce=int)
    fecha_entrada = DateField("Fecha de entrada",validators=[DataRequired()],render_kw={"type": "date"})
    def validate_fecha_entrada(self,field):
        if field.data < date.today():
            raise ValidationError("La fecha de entrada no puede ser anterior a hoy")
    fecha_salida = DateField("Fecha de salida",validators=[DataRequired()],render_kw={"type": "date"})
    def validate_fecha_salida(self,field):
        if field.data <= self.fecha_entrada.data:
            raise ValidationError(
                "La fecha de salida debe ser posterior a la fecha de entrada")

    estado = SelectField("Estado",
                         choices=[
                             ("pendiente", "Pendiente"),
                             ("confirmada", "Confirmada"),
                             ("cancelada", "Cancelada"),
                             ("completada", "Completada")
                         ],
                         validators=[DataRequired()]

    )

    enviar = SubmitField("Guardar")"""

