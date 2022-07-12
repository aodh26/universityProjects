
DROP TABLE IF EXISTS staff;

CREATE TABLE staff 
(
    pps TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS patients;

CREATE TABLE patients 
(
    pps TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT NOT NULL,
    dob DATE NOT NULL,
    weight TEXT NOT NULL,
    height TEXT NOT NULL,
    smoker TEXT NOT NULL,
    nextappointment DATE,
    appointmenttime TEXT,
    moneyowed DECIMAL,
    email TEXT NOT NULL,
    number INTEGER NOT NULL,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS doctopatient;

CREATE TABLE doctopatient 
(
    patientpps TEXT NOT NULL,
    doctorpps TEXT NOT NULL
);

DROP TABLE IF EXISTS daysoff;

CREATE TABLE daysoff 
(
    pps TEXT NOT NULL,
    startdate DATE NOT NULL,
    enddate DATE NOT NULL
);

DROP TABLE IF EXISTS medicine;

CREATE TABLE medicine 
(
    patientpps TEXT NOT NULL,
    medicine TEXT
);

DROP TABLE IF EXISTS illness;

CREATE TABLE illness 
(
    patientpps TEXT NOT NULL,
    illness TEXT
);

DROP TABLE IF EXISTS notes;

CREATE TABLE notes 
(
    patientpps TEXT NOT NULL,
    doctorpps TEXT NOT NULL,
    date DATE NOT NULL,
    note TEXT NOT NULL
);

DROP TABLE IF EXISTS appointments;

CREATE TABLE appointments 
(
    patientpps TEXT NOT NULL,
    doctorpps TEXT NOT NULL,
    appointment DATE NOT NULL,
    time TEXT NOT NULL
);

DELETE FROM staff 
WHERE pps!='phil';

SELECT *
FROM staff;