# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional

# forms.py
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('staff','Staff'), ('manager','Manager'), ('admin','Admin')])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2)])
    password = PasswordField('Password', validators=[DataRequired()])

class ProductForm(FlaskForm):
    code = StringField('Product Code', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    category = StringField('Category', validators=[Optional()])
    stock = IntegerField('Stock', validators=[Optional()])
    reorder_point = IntegerField('Reorder Point', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()])
    supplier_id = SelectField('Supplier', coerce=int, validators=[Optional()])

class SupplierForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    contact = StringField('Contact', validators=[Optional()])
    email = StringField('Email', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
