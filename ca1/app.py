'''My app allows three types of users; administration, doctors and patients
I have already created some admin, doctors and patients but you can create some too if you'd like. 
Staff are registered by a member of admin.
for simplictiy I have made both the PPS Number and password of every user their first name all lower case.
E.G for administrator phil dunphy; his PPS Number is phil and his password is phil.
ADMIN:      phil dunphy
DOCTORS:    claire dunphy
            haley dunphy
PATIENTS:   jay pritchett
            joe pritchett
            gloria pritchett
            manny delgato

Admin can:  view appointments, staff and patients details.
            Add or remove members of staff.
            Create, update and delete days off for staff.
            Add or subtract money owed by a patient.
            Cannot see certain details of patients due to Doctor-Patient confidentiality.
Doctors can: View their patients information.
             Add and remove prescriptions.
             Add and remove illnesses.
             Write auto-dated notes on patients(cannot be editted for accountability).
Patients can: Register.
              view or update their details.
              make or cancel an appointment(taking into account the doctors schedule).

Only the users allocated web pages are accessible to them. E.G a doctor may not go on the days off web page.'''

from flask import Flask, render_template, redirect, url_for, session, request, g
from forms import PatientRegistrationForm, LoginForm, AppointmentForm, CancelForm, UpdateProfileForm,NewStaffForm, RemoveStaffForm, MoneyowedForm, DaysoffForm,UpdateDeleteForm, DeleteForm,UpdateForm, PrescribeForm,DiagnoseForm, RemovePrescribeForm,RemoveDiagnoseForm, NotesForm
from database import get_db, close_db
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app=Flask(__name__)

app.config['SESSION_PERMANENT']=False
app.config['SESSION_TYPE']='filesystem'
Session(app)

app.config['SECRET_KEY']='secret-key'

@app.teardown_appcontext
def close_db_at_end_of_request (e=None):
    close_db(e)

@app.before_request
def loadloggedinuser():
    g.user=session.get('user', None)

def loginrequired(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return view(**kwargs)
    return wrapped_view

@app.route('/')
def index():
    patient=''
    staff=''
    if g.user is not None:
        db=get_db()
        patient=db.execute('''SELECT * FROM patients
                         WHERE pps=?''',(session['user'],)).fetchall()
        staff=db.execute('''SELECT * FROM staff
                         WHERE pps=?''',(session['user'],)).fetchall()

    return render_template('index.html', patient=patient, staff=staff)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form=PatientRegistrationForm()
    if form.validate_on_submit():
        pps=form.pps.data
        name=form.name.data
        gender=form.gender.data
        dob=form.dob.data
        weight=form.weight.data
        height=form.height.data
        smoker=form.smoker.data
        email=form.email.data
        doctor=form.doctor.data
        doctorname=doctor.lower()
        number=form.number.data
        password=form.password.data
        db=get_db()
        if db.execute('''SELECT * FROM patients
                         WHERE pps=?''',(pps,)).fetchone() is not None:
            form.pps.errors.append('This person is already a patient')
        else: 
            doctorpps=db.execute('''SELECT pps FROM staff 
                            WHERE name=? and role='doctor';''',(doctorname,)).fetchone()['pps']
            if doctorpps is None:
                form.doctor.errors.append('Theres no doctor by that name')
                return render_template('register.html', form=form)
            else:
                db.execute('''INSERT INTO patients (pps, name, gender, dob, weight, height, smoker, email, number, password)
                        VALUES (?,?,?,?,?,?,?,?,?,?);''',(pps,name,gender,dob,weight,height,smoker,email,number, generate_password_hash(password)))
                db.commit()
            
                db.execute('''INSERT INTO doctopatient(patientpps, doctorpps)
                                VALUES(?,?);''',(pps,doctorpps))
                db.commit()
                db.execute('''INSERT INTO medicine(patientpps)
                                VALUES(?);''',(pps,))
                db.commit()
                db.execute('''INSERT INTO illness(patientpps)
                                VALUES(?);''',(pps,))
                db.commit()
                return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        pps=form.pps.data
        password=form.password.data
        db=get_db()
        patient=db.execute('''SELECT * FROM patients
                        WHERE pps=?''',(pps,)).fetchone()
        staff=db.execute('''SELECT * FROM staff
                        WHERE pps=?''',(pps,)).fetchone()
        if patient is None and staff is None:
            form.pps.errors.append('Unkown PPS Number')
        elif patient is not None and staff is None and not check_password_hash(patient['password'], password):
            form.password.errors.append('Incorrect password')
        elif patient is None and staff is not None and not check_password_hash(staff['password'], password):
            form.password.errors.append('Incorrect password')
        else:
            session.clear()
            session['user']=pps
            nextpage=request.args.get('next')
            if not nextpage:
                nextpage=url_for('index')
            return redirect(nextpage)
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/appointment', methods=['GET','POST'])
@loginrequired
def appointment():
    db=get_db()
    if db.execute('''SELECT * FROM patients
                         WHERE pps=?''',(session['user'],)).fetchone() is None:
            return redirect(url_for('error'))
    form=AppointmentForm()
    booked=''
    if form.validate_on_submit():
        appointment=form.appointment.data
        if appointment < datetime.now().date():
                form.appointment.errors.append("Date must be in the future")
        else:
            if db.execute('''SELECT nextappointment from patients
                                WHERE pps=?;''',(session['user'],)).fetchone()['nextappointment'] is not None:
                form.appointment.errors.append("You already have an appointment booked")
            else:
                doctorpps=db.execute('''SELECT doctorpps from doctopatient WHERE patientpps=?;''',(session['user'],)).fetchone()['doctorpps']
                if db.execute('''SELECT COUNT(*) as count FROM appointments 
                                WHERE appointment=? AND doctorpps=?;''',(appointment,doctorpps)).fetchone()['count']>=10:
                            form.appointment.errors.append('Your doctor is booked that day!')
                elif db.execute('''SELECT * FROM daysoff
                                WHERE pps=? AND startdate<=? AND enddate>=?;''',(doctorpps,appointment,appointment)).fetchone() is not None:
                    form.appointment.errors.append('Your doctor is booked that day!')
                else: 
                    patientnum=db.execute('''SELECT COUNT(*) as count FROM appointments 
                                            WHERE appointment=? AND doctorpps=?;''',(appointment,doctorpps)).fetchone()['count']
                    timeslots=['8:00am','9:00am','10:00am','11:00am','12:00pm','1:00pm','2:00pm','3:00pm','4:00pm','5:00pm','6:00pm']
                    patienttime=timeslots[patientnum]
                    while db.execute('''SELECT * FROM appointments WHERE appointment=? AND doctorpps=? AND time=?;''',(appointment,doctorpps,patienttime)).fetchone() is not None:
                        if patienttime=='6:00pm':
                            form.appointment.errors.append('Your doctor is booked that day!')
                        else:
                            patienttime=timeslots[patientnum+1]
                    db.execute('''INSERT INTO appointments(patientpps,doctorpps,appointment, time)
                                    VALUES(?,?,?,?);''',(session['user'],doctorpps,appointment, patienttime))
                    db.commit()
                    db.execute('''UPDATE patients
                                    SET nextappointment=?, appointmenttime=? WHERE pps=?;''',(appointment,patienttime,session['user']))
                    db.commit()
                    booked='Your appointment is booked!'
                    return render_template('appointment.html', form=form,appointment=appointment, booked=booked, patienttime=patienttime)
    return render_template('appointment.html', form=form, booked=booked)

@app.route('/patientprofile')
@loginrequired
def patientprofile():
    db=get_db()
    if db.execute('''SELECT * FROM patients
                         WHERE pps=?''',(session['user'],)).fetchone() is None:
            return redirect(url_for('error'))
    patient=db.execute('''SELECT * FROM patients
                        WHERE pps=?''',(session['user'],)).fetchall()
    doctorname=db.execute('''SELECT s.name as n FROM staff as s JOIN doctopatient as d 
                    ON s.pps=d.doctorpps WHERE d.patientpps=?;''',(session['user'],)).fetchone()['n']
    illness=db.execute('''SELECT * FROM illness
                        WHERE patientpps=?''',(session['user'],)).fetchall()
    medicine=db.execute('''SELECT * FROM medicine
                        WHERE patientpps=?''',(session['user'],)).fetchall()                  
    return render_template('patient.html', patient=patient, doctorname=doctorname, illness=illness, medicine=medicine)

@app.route('/cancel', methods=['GET','POST'])
@loginrequired
def cancel():
    db=get_db()
    if db.execute('''SELECT * FROM patients
                         WHERE pps=?''',(session['user'],)).fetchone() is None:
            return redirect(url_for('error'))
    message=''
    form=CancelForm()
    patient=db.execute('''SELECT * FROM patients
                        WHERE pps=?''',(session['user'],)).fetchall()
    doctorname=db.execute('''SELECT s.name as n FROM staff as s JOIN doctopatient as d 
                    ON s.pps=d.doctorpps WHERE d.patientpps=?;''',(session['user'],)).fetchone()['n']
    if form.validate_on_submit():
        cancel=form.cancel.data
        if cancel=='yes':
            if db.execute('''SELECT nextappointment from patients
                                        WHERE pps=?;''',(session['user'],)).fetchone()['nextappointment'] is None:
                        form.cancel.errors.append('You do not have an appointment booked')
            else:
                message='appointment cancelled'
                db.execute('''UPDATE patients
                                SET nextappointment=NULL, appointmenttime=NULL WHERE pps=?;''',(session['user'],))
                db.commit()
                db.execute('''DELETE FROM appointments
                               WHERE patientpps=?;''',(session['user'],))
                db.commit()
                return render_template('cancel.html',form=form, message=message, patient=patient, doctorname=doctorname)
        else:
            return redirect(url_for('profile'))
    return render_template('cancel.html', form=form, patient=patient, doctorname=doctorname)

@app.route('/updateprofile', methods=['GET','POST'])
@loginrequired
def updateprofile():
    db=get_db()
    if db.execute('''SELECT * FROM patients
                         WHERE pps=?''',(session['user'],)).fetchone() is None:
            return redirect(url_for('error'))
    form=UpdateProfileForm()
    if form.validate_on_submit():
        name=form.name.data
        gender=form.gender.data
        weight=form.weight.data
        height=form.height.data
        smoker=form.smoker.data
        email=form.email.data
        number=form.number.data
        password=form.password.data
        db.execute('''UPDATE patients 
                        SET name=?, gender=?, weight=?,height=?,smoker=?,email=?,number=?,password=? WHERE pps=?;''',(name,gender,weight,height,smoker,email,number, generate_password_hash(password),session['user']))
        db.commit()
        return redirect(url_for('patientprofile'))
    return render_template('updateprofile.html',form=form)

@app.route('/adminprofile')
@loginrequired
def adminprofile():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='admin':
        return redirect(url_for('error'))
    admin=db.execute('''SELECT * FROM staff
                        WHERE pps=?;''', (session['user'],)).fetchall()
    return render_template('admin.html',admin=admin)

@app.route('/newstaff', methods=['GET','POST'])
@loginrequired
def newstaff():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='admin':
        return redirect(url_for('error'))
    form=NewStaffForm()
    if form.validate_on_submit():
        pps=form.pps.data
        name=form.name.data
        name=name.lower()
        role=form.role.data
        password=form.password.data
        if db.execute('''SELECT * FROM staff WHERE pps=?;''',(pps,)).fetchone() is not None:
            form.pps.errors.append('This person is already a staff member')
        else:
            db.execute('''INSERT INTO staff(pps,name,role,password)
                        VALUES(?,?,?,?);''',(pps,name,role, generate_password_hash(password)))
            db.commit()

        return redirect(url_for('staff'))
    return render_template('newstaff.html', form=form)

@app.route('/removestaff', methods=['GET','POST'])
@loginrequired
def removestaff():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='admin':
        return redirect(url_for('error'))
    form=RemoveStaffForm()
    if form.validate_on_submit():
        pps=form.pps.data
        if db.execute('''SELECT * FROM staff WHERE pps=?;''',(pps,)).fetchone() is None:
            form.pps.errors.append('This person is not a staff member') 
        else:
            db.execute('''DELETE FROM staff WHERE pps=?;''',(pps,))
            db.commit()
            return redirect(url_for('staff'))
    return render_template('removestaff.html', form=form)

@app.route('/staff') 
@loginrequired
def staff():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='admin':
        return redirect(url_for('error'))
    staff=db.execute('''SELECT * FROM staff;''').fetchall()
    return render_template('staff.html', staff=staff)   

@app.route('/adminpatients')
@loginrequired
def adminpatients():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='admin':
        return redirect(url_for('error'))
    patients=db.execute('''SELECT * FROM patients;''').fetchall()
    return render_template('adminpatients.html', patients=patients)

@app.route('/calender')
@loginrequired
def calender():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='admin':
        return redirect(url_for('error'))
    appointments=db.execute('''SELECT * FROM appointments ORDER BY appointment ASC;''').fetchall()
    daysoff=db.execute('''SELECT * FROM daysoff;''').fetchall()
    return render_template('calender.html',appointments=appointments, daysoff=daysoff)

@app.route('/moneyowed', methods=['GET','POST'])
@loginrequired
def moneyowed():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='admin':
        return redirect(url_for('error'))
    form=MoneyowedForm()
    if form.validate_on_submit():
        pps=form.pps.data
        amount=form.amount.data
        operator=form.operator.data
        db=get_db()
        moneyowed=db.execute('''SELECT moneyowed FROM patients WHERE pps=?;''', (pps,)).fetchone()['moneyowed']
        print(moneyowed)
        if operator=='add':
            if moneyowed is not None:
                db.execute('''UPDATE patients 
                                SET moneyowed=? WHERE pps=?;''',(moneyowed+amount,pps))
                db.commit()
            else:
                db.execute('''UPDATE patients 
                                SET moneyowed=? WHERE pps=?;''',(amount,pps))
                db.commit()
            return redirect(url_for('adminpatients'))
        elif operator=='subtract':
            if moneyowed is None:
                form.amount.errors.append('This person does not owe any money')
            else:
                if (moneyowed-amount)==0:
                    db.execute('''UPDATE patients 
                                SET moneyowed=NULL WHERE pps=?;''',(pps,))
                    db.commit()
                else:
                    db.execute('''UPDATE patients 
                                    SET moneyowed=? WHERE pps=?;''',(moneyowed-amount,pps))
                    db.commit()
                return redirect(url_for('adminpatients'))
    return render_template('moneyowed.html', form=form)

@app.route('/daysoff', methods=['GET','POST'])
@loginrequired
def daysoff():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='admin':
        return redirect(url_for('error'))
    form=DaysoffForm()
    if form.validate_on_submit():
        pps=form.pps.data
        startdate=form.startdate.data
        enddate=form.enddate.data
        if db.execute('''SELECT pps FROM daysoff
                        WHERE ((startdate<=? AND enddate>=?) OR (startdate>=? AND enddate>=?)) AND pps=?;''',(startdate,startdate,startdate,startdate, pps)).fetchone() is not None:
            form.startdate.errors.append('These dates intersect already existing scheduled time off')
        elif db.execute('''SELECT * FROM appointments WHERE doctorpps=? AND appointment>=? AND appointment<=?''',(pps,startdate,enddate)).fetchone() is not None:
            form.pps.errors.append("This doctor has appointments booked in this time period.")
        else:
            db.execute('''INSERT INTO daysoff(pps,startdate,enddate)
                            VALUES(?,?,?);''',(pps,startdate,enddate))
            db.commit()
            return redirect(url_for('calender'))
    return render_template('daysoff.html',form=form)

@app.route('/updatedelete', methods=['GET','POST'])
@loginrequired
def updatedelete():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='admin':
        return redirect(url_for('error'))
    form=UpdateDeleteForm()
    if form.validate_on_submit():
        updateordelete=form.updateordelete.data
        if updateordelete=='delete':
            return redirect(url_for('delete'))
        elif updateordelete=='update':
            return redirect(url_for('update'))
    return render_template('updatedelete.html',form=form)

@app.route('/delete', methods=['GET','POST'])
@loginrequired
def delete():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='admin':
        return redirect(url_for('error'))
    form=DeleteForm()
    if form.validate_on_submit():
        pps=form.pps.data
        startdate=form.startdate.data
        enddate=form.enddate.data
        if db.execute('''SELECT * FROM daysoff WHERE pps=? AND startdate=? AND enddate=?;''',(pps,startdate,enddate)).fetchone() is not None:
            form.pps.errors.append('Could not find days off matching the information given.')
        elif db.execute('''SELECT * FROM daysoff WHERE pps=? AND startdate=? AND enddate=?;''',(pps,startdate,enddate)).fetchone() is None:
                    form.pps.errors.append('this person does not have days off matching these dates')
        else:
            db.execute('''DELETE FROM daysoff WHERE pps=? AND startdate=? AND enddate=?;''',(pps,startdate,enddate))
            db.commit()
            return redirect(url_for('calender'))
    return render_template('delete.html',form=form)

@app.route('/update', methods=['GET','POST'])
@loginrequired
def update():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='admin':
        return redirect(url_for('error'))
    form=UpdateForm()
    if form.validate_on_submit():
        pps=form.pps.data
        startdate=form.startdate.data
        enddate=form.enddate.data
        newstartdate=form.newstartdate.data
        newenddate=form.newenddate.data
        if db.execute('''SELECT * FROM daysoff WHERE pps=? AND startdate=? AND enddate=?;''',(pps,startdate,enddate)).fetchone() is None:
            form.pps.errors.append('Could not find days off matching the information given.')
            print(pps,startdate,enddate)
        elif  newstartdate<= datetime.now().date():
                form.newstartdate.errors.append("Date must be in the future")
        elif  newstartdate>newenddate:
                form.newenddate.errors.append("Date must be after start date")
        elif db.execute('''SELECT * FROM appointments WHERE doctorpps=? AND appointment>=? AND appointment<=?''',(pps,newstartdate,newenddate)).fetchone() is not None:
            form.pps.errors.append("This doctor has appointments booked in this time period.")
        else:
            db.execute('''UPDATE daysoff
                            SET startdate=?, enddate=? WHERE pps=? AND startdate=? AND enddate=?;''',(newstartdate,newenddate,pps,startdate,enddate))
            db.commit()
            return redirect(url_for('calender'))
    return render_template('update.html', form=form)

@app.route('/doctorprofile')
@loginrequired
def doctorprofile():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='doctor':
        return redirect(url_for('error'))
    doctor=db.execute('''SELECT * FROM staff
                        WHERE pps=?;''', (session['user'],)).fetchall()
    patientspps=db.execute('''SELECT patientpps FROM doctopatient
                        WHERE doctorpps=?;''', (session['user'],)).fetchall()
    patients=[]
    for pps in patientspps:
        patient=[]
        patientdets=db.execute('''SELECT * FROM patients
                            WHERE pps=?;''', (pps['patientpps'],)).fetchone()
        patient.append(patientdets)

        illness=db.execute('''SELECT illness FROM illness
                            WHERE patientpps=?;''', (pps['patientpps'],)).fetchall()
        for ill in illness:
            patient.append(ill)

        medicine=db.execute('''SELECT medicine FROM medicine
                            WHERE patientpps=?;''', (pps['patientpps'],)).fetchall()
        for med in medicine:
            patient.append(med)
        
        notespp=db.execute('''SELECT note,date FROM notes
                            WHERE patientpps=? ORDER BY date ASC;''', (pps['patientpps'],)).fetchall()
        for note in notespp:
            patient.append(note)
        patients.append(patient)
    return render_template('doctor.html',doctor=doctor,patients=patients)

@app.route('/prescribe', methods=['GET','POST'])
@loginrequired
def prescribe():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='doctor':
        return redirect(url_for('error'))
    form=PrescribeForm()
    doctor=db.execute('''SELECT * FROM staff
                        WHERE pps=?;''', (session['user'],)).fetchall()
    if form.validate_on_submit():
        pps=form.pps.data
        medicine=form.medicine.data
        if db.execute('''SELECT * FROM medicine WHERE patientpps=? AND medicine=?;''',(pps,medicine)).fetchone() is not None:
            form.medicine.errors.append('this person has already been prescribed this medicine')
        elif db.execute('''SELECT * FROM medicine WHERE patientpps=? AND medicine is NULL;''',(pps,)).fetchone() is not None:
            db.execute('''UPDATE medicine
                        SET medicine=? WHERE patientpps=?;''',(medicine,pps))
            db.commit()
            return redirect(url_for('doctorprofile'))
        else:
            db.execute('''INSERT INTO medicine(patientpps,medicine)
                        VALUES(?,?);''',(pps,medicine))
            db.commit()
            return redirect(url_for('doctorprofile'))
    return render_template('prescribe.html',form=form, doctor=doctor)

@app.route('/removeprescribe', methods=['GET','POST'])
@loginrequired
def removeprescribe():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='doctor':
        return redirect(url_for('error'))
    form=RemovePrescribeForm()
    doctor=db.execute('''SELECT * FROM staff
                        WHERE pps=?;''', (session['user'],)).fetchall()
    if form.validate_on_submit():
        pps=form.pps.data
        medicine=form.medicine.data
        if db.execute('''SELECT * FROM medicine WHERE patientpps=? AND medicine=?;''',(pps,medicine)).fetchone() is None:
                form.medicine.errors.append('this person has not been prescribed this medicine')
        elif db.execute('''SELECT COUNT(*) as count FROM medicine WHERE patientpps=?;''',(pps,)).fetchone()['count']==1:
                db.execute('''UPDATE medicine
                            SET medicine=NULL WHERE patientpps=?;''',(pps,))
                db.commit() 
        else:
            db.execute('''DELETE FROM medicine
                            WHERE patientpps=? AND medicine=?;''',(pps,medicine))
            db.commit()
        return redirect(url_for('doctorprofile'))
    return render_template('removeprescribe.html',form=form, doctor=doctor) 

@app.route('/diagnose', methods=['GET','POST'])
@loginrequired
def diagnose():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='doctor':
        return redirect(url_for('error'))
    form=DiagnoseForm()
    doctor=db.execute('''SELECT * FROM staff
                        WHERE pps=?;''', (session['user'],)).fetchall()
    if form.validate_on_submit():
        pps=form.pps.data
        illness=form.illness.data
        if db.execute('''SELECT * FROM illness WHERE patientpps=? AND illness=?;''',(pps,illness)).fetchone() is not None:
            form.illness.errors.append('this person has already been disgnosed with this illness')
        elif db.execute('''SELECT * FROM illness WHERE patientpps=? AND illness is NULL;''',(pps,)).fetchone() is not None:
            db.execute('''UPDATE illness
                        SET illness=? WHERE patientpps=?;''',(illness,pps))
            db.commit()
            return redirect(url_for('doctorprofile'))
        else:
            db.execute('''INSERT INTO illness(patientpps,illness)
                        VALUES(?,?);''',(pps,illness))
            db.commit()
            return redirect(url_for('doctorprofile'))
    return render_template('diagnose.html',form=form, doctor=doctor)

@app.route('/removediagnose', methods=['GET','POST'])
@loginrequired
def removediagnose():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='doctor':
        return redirect(url_for('error'))
    form=RemoveDiagnoseForm()
    doctor=db.execute('''SELECT * FROM staff
                        WHERE pps=?;''', (session['user'],)).fetchall()
    if form.validate_on_submit():
        pps=form.pps.data
        illness=form.illness.data
        if db.execute('''SELECT * FROM illness WHERE patientpps=? AND illness=?;''',(pps,illness)).fetchone() is None:
                form.illness.errors.append('this person has not been prescribed this medicine')
        elif db.execute('''SELECT COUNT(*) as count FROM illness WHERE patientpps=?;''',(pps,)).fetchone()['count']==1:
                db.execute('''UPDATE illness
                            SET illness=NULL WHERE patientpps=?;''',(pps,))
                db.commit() 
        else:
            db.execute('''DELETE FROM illness
                            WHERE patientpps=? AND illness=?;''',(pps,illness))
            db.commit()
        return redirect(url_for('doctorprofile'))
    return render_template('removediagnose.html',form=form, doctor=doctor) 



@app.route('/notes',methods=['GET','POST'])
@loginrequired
def notes():
    db=get_db()
    if db.execute('''SELECT * FROM staff WHERE pps=?;''',(session['user'],)).fetchone() is None:
        return redirect(url_for('error'))
    if db.execute('''SELECT role FROM staff WHERE pps=?;''',(session['user'],)).fetchone()['role']!='doctor':
        return redirect(url_for('error'))
    doctor=db.execute('''SELECT * FROM staff
                        WHERE pps=?;''', (session['user'],)).fetchall()
    form=NotesForm()
    if form.validate_on_submit():
        patientpps=form.patientpps.data
        note=form.note.data
        date=datetime.now().date()
        if db.execute('''SELECT * FROM doctopatient WHERE patientpps=? AND doctorpps=?;''',(patientpps,session['user'])).fetchone() is None:
            form.patientpps.errors.append('This pps does not match any of your patients')
        else:
            db.execute('''INSERT INTO notes(patientpps, doctorpps,date,note)
                        VALUES(?,?,?,?);''',(patientpps,session['user'],date,note))
            db.commit()
            return redirect(url_for('doctorprofile'))
    return render_template('notes.html',form=form,doctor=doctor)
    
@app.route('/error')
@loginrequired
def error():
    return render_template('error.html')