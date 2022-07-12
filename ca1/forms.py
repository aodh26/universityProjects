from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, DecimalField, SelectField, RadioField, IntegerField, FloatField
from wtforms.validators import InputRequired, EqualTo, NumberRange
from wtforms.fields.html5 import DateField

class PatientRegistrationForm(FlaskForm):
    pps=StringField('PPS Number: ', validators=[InputRequired()])
    name=StringField('Full Name: ', validators=[InputRequired()])
    gender=RadioField('Gender:',
        choices=[('Male','Male'),
                ('Female','Female'),
                ('Other','Other')],
                validators=[InputRequired()])
    dob=DateField('Date Of Birth: ', format='%Y-%m-%d',validators=[InputRequired()])
    weight=FloatField('Weight (kg): ', validators=[InputRequired(), NumberRange(0,200)] )
    height=FloatField('Height (m): ', validators=[InputRequired(), NumberRange(0.3,2.5)] )
    smoker=SelectField('Do you smoke:',
        choices=[('yes','Yes'),
                ('no','No')],
                default='no',
                validators=[InputRequired()])
    email=StringField('email: ', validators=[InputRequired()])
    number=IntegerField('number: ', validators=[InputRequired()])
    doctor=StringField('Doctors first and last name: ', validators=[InputRequired()])
    password=PasswordField('Password:', validators=[InputRequired()])
    password2=PasswordField('Confirm password:', validators=[InputRequired(), EqualTo('password')])
    submit=SubmitField('Register')

class LoginForm(FlaskForm):
    pps=StringField('PPS Number:', validators=[InputRequired()])
    password=PasswordField('Password:', validators=[InputRequired()])
    submit=SubmitField('Login')

class AppointmentForm(FlaskForm):
    appointment=DateField('Choose a date: ',format='%Y-%m-%d',validators=[InputRequired()])
    submit=SubmitField('Submit Date')

class CancelForm(FlaskForm):
    cancel=SelectField('Cancel Appointment:',
        choices=[('yes','Yes'),
                ('no','No')],
                default='no',
                validators=[InputRequired()])
    submit=SubmitField('Submit')

class UpdateProfileForm(FlaskForm):
    name=StringField('Full Name: ', validators=[InputRequired()])
    gender=RadioField('Gender:',
        choices=[('Male','Male'),
                ('Female','Female'),
                ('Other','Other')],
                validators=[InputRequired()])
    weight=FloatField('Weight (kg): ', validators=[InputRequired(), NumberRange(0,200)] )
    height=FloatField('Height (m): ', validators=[InputRequired(), NumberRange(0.3,2.5)] )
    smoker=SelectField('Do you smoke:',
        choices=[('yes','Yes'),
                ('no','No')],
                default='no',
                validators=[InputRequired()])
    email=StringField('email: ', validators=[InputRequired()])
    number=IntegerField('number: ', validators=[InputRequired()])
    password=PasswordField('Password:', validators=[InputRequired()])
    password2=PasswordField('Confirm password:', validators=[InputRequired(), EqualTo('password')])
    submit=SubmitField('Update')


class NewStaffForm(FlaskForm):
    pps=StringField('PPS Number: ', validators=[InputRequired()])
    name=StringField('Full Name: ', validators=[InputRequired()])
    role=SelectField('Role:',
        choices=[('doctor','Doctor'),
                ('admin','Admin')],
                validators=[InputRequired()])
    password=PasswordField('Password:', validators=[InputRequired()])
    password2=PasswordField('Confirm password:', validators=[InputRequired(), EqualTo('password')])
    submit=SubmitField('Register Staff Member')

class RemoveStaffForm(FlaskForm):
    pps=StringField('PPS Number of staff to be removed: ', validators=[InputRequired()])
    submit=SubmitField('Remove Staff Member')

class MoneyowedForm(FlaskForm):
    pps=StringField('PPS Number of patient: ', validators=[InputRequired()])
    amount=FloatField('Change in money owed: ')
    operator=RadioField('Add or Subtract:',
        choices=[('add','Add'),
                ('subtract','Subtract')],
                validators=[InputRequired()])
    submit=SubmitField('Submit')

class DaysoffForm(FlaskForm):
    pps=StringField('PPS Number of staff member: ', validators=[InputRequired()])
    startdate=DateField('Choose a start date: ',format='%Y-%m-%d',validators=[InputRequired()])
    enddate=DateField('Choose an end date: ',format='%Y-%m-%d',validators=[InputRequired()])
    submit=SubmitField('Submit')

class UpdateDeleteForm(FlaskForm):
    updateordelete=RadioField('Are you Updating or Deleting existing days off:',
        choices=[('update','Update'),
                ('delete','Delete')],
                validators=[InputRequired()])
    submit=SubmitField('Submit')

class UpdateForm(FlaskForm):
    pps=StringField('PPS Number of staff member: ', validators=[InputRequired()])
    startdate=DateField('Former start date: ',format='%Y-%m-%d')
    enddate=DateField('Former end date: ',format='%Y-%m-%d')
    newstartdate=DateField('Choose a new start date: ',format='%Y-%m-%d')
    newenddate=DateField('Choose a new end date: ',format='%Y-%m-%d')
    submit=SubmitField('Submit')

class DeleteForm(FlaskForm):
    pps=StringField('PPS Number of staff member: ', validators=[InputRequired()])
    startdate=DateField('Start date: ',format='%Y-%m-%d')
    enddate=DateField('End date: ',format='%Y-%m-%d')
    submit=SubmitField('Delete')

class PrescribeForm(FlaskForm):
    pps=StringField('PPS Number of patient: ', validators=[InputRequired()])
    medicine=StringField('Medicine: ', validators=[InputRequired()])
    submit=SubmitField('Prescribe')

class RemovePrescribeForm(FlaskForm):
    pps=StringField('PPS Number of patient: ', validators=[InputRequired()])
    medicine=StringField('Medicine: ', validators=[InputRequired()])
    submit=SubmitField('Unprescribe')

class DiagnoseForm(FlaskForm):
    pps=StringField('PPS Number of patient: ', validators=[InputRequired()])
    illness=StringField('illness: ', validators=[InputRequired()])
    submit=SubmitField('Diagnose')

class RemoveDiagnoseForm(FlaskForm):
    pps=StringField('PPS Number of patient: ', validators=[InputRequired()])
    illness=StringField('illness: ', validators=[InputRequired()])
    submit=SubmitField('Remove Diagnoses')

class NotesForm(FlaskForm):
    patientpps=StringField('PPS Number of patient: ', validators=[InputRequired()])
    note=StringField('Note on patient: ', validators=[InputRequired()])
    submit=SubmitField('Submit')