CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients (
    PUsername varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (PUsername)
);

CREATE TABLE Appointments (
    appointmentID int,
    Time date REFERENCES Availabilities,
    PUsername varchar(255) REFERENCES Patients,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (appointmentID)
);