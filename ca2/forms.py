from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import InputRequired

class NameForm(FlaskForm):
    name=StringField('Name:', validators=[InputRequired()])
    submit=SubmitField('Play')