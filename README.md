# universityProjects
Projects completed for my university degree. All code was written within a 6 week window and all received at least 90%

CA1: A doctors website made with flask framework, html, css and python.
My app allows three types of users; administration, doctors and patients
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

Only the users allocated web pages are accessible to them. E.G a doctor may not go on the days off web page.  
