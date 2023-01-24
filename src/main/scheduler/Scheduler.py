from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Appointment import Appointment
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    patient = Patient(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        print("Please try again!")
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        print("Please try again!")
        return
    print("Created user ", username)


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE PUsername = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        print("Please try again!")
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
        print("Please try again!")
    finally:
        cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        print("Please try again!")
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        print("Please try again!")
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        print("Please try again!")
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
        print("Please try again!")
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        print("Please try again!")
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        print("Please try again!")
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        print("Please try again!")
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        print("Please try again!")
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    # check 1: Insure they are logged in
    if not((current_caregiver != None) or (current_patient != None)):
        print("Please log in first.")
        return

    # check 2: The number of tokens should be 2
    if len(tokens) != 2:
        print("Please try again!")
        return

    # assume input is hyphenated in the format mm-dd-yyyy
    date = tokens[1]
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    # check 3: check if the date is valid and get the available dates
    try:
        date = datetime.datetime(year, month, day)
        avaliableDates = Caregiver(date).get_availability(date)
    except pymssql.Error as e:
        print("Please try again!")
        return
    except ValueError:
        print("Please try again!")
        return
    except Exception as e:
        print("Please try again!")
        return

    # check 4: check if dates are returned
    if not avaliableDates:
        print("No available caregivers found for that date")
    else:
        print("Schedule search successful.")
        print("Avaliable caregivers:")

        for date in avaliableDates:
            print(date, end=" ")
        
        # Prints vaccines
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_vaccine = "SELECT * FROM Vaccines"
        print("========Avaliable Vaccines========")
        try:
            cursor.execute(get_vaccine)
            for row in cursor:
                print(str(row[0]) + ": " + str(row[1]))
        except pymssql.Error:
            # print("Error occurred when getting Vaccine")
            print("Please try again!")
            raise
        finally:
            cm.close_connection()
        return None



def reserve(tokens):
    # check 1: Insure they are logged in
    if ((current_caregiver == None) and (current_patient == None)):
        print("Please login first!")
        return
    elif current_patient == None:
        print("Please login as a patient!")
        return

    # check 2: The number of tokens should be 3
    if len(tokens) != 3:
        print("Reservation failed.")
        print("Incorrect number of inputs")
        return

    # Get the information from the tokens
    date = tokens[1]
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    Dose_name = tokens[2]
    # Find the available caregivers on the date
    try:
        date = datetime.datetime(year, month, day)
        avaliableCaregiver = Caregiver(date).get_availability(date)
    except pymssql.Error as e:
        print("Fetchings schedule failed.")
        print("Db-Error:", e)
        print("Please try again!")
        return
    except ValueError:
        print("Please enter a valid date!")
        print("Please try again!")
        return
    except Exception as e:
        print("Error occurred when fetching availability")
        print("Check your input and try again.")
        print(e)
        print("Please try again!")
        return
    
    if avaliableCaregiver==[]:
        print("No available caregivers found for that date")
        return
    else:    
        freeCaregiver = avaliableCaregiver[0] 

        # Get the appointment id
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_appointment_id = "SELECT COUNT(appointmentID) FROM Appointments "
        try:
            cm = ConnectionManager()
            conn = cm.create_connection()
            cursor = conn.cursor()
            cursor.execute(get_appointment_id)
            for row in cursor:
                id = row
        except pymssql.Error as e:
            print("Error occurred when getting appointment ID")
            print("Db-Error:", e)
            print("Please try again!")
            raise e
        

        # Reduce the vaccine count
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        get_vaccine_count = "SELECT Doses, Doses FROM Vaccines WHERE Name = %s"
        get_vaccine = "UPDATE Vaccines SET Doses = %s WHERE name = %s"
        try:
            cursor.execute(get_vaccine_count, (Dose_name))
            for row in cursor:
                count = row[0] - 1
            cursor.execute(get_vaccine, (count, Dose_name))
            conn.commit()
            if cursor.rowcount == 0:
                print("No such vaccine")
                return
        except pymssql.Error:
            # print("Error occurred when getting Vaccine")
            print("Please try again!")
            raise
        finally:
            cm.close_connection()
        
        # Create the appointment
        try:
            newAppointment = Appointment(id, current_patient.username, freeCaregiver, date) # Creates the appointment
            newAppointment.create() # Adds the appointment to the database
        except pymssql.Error as e:
            print("Error occurred when creating appointment")
            print("Db-Error:", e)
            print("Please try again!")
        except Exception as e:
            print("Error occurred when creating appointment")
            print("Check your input and try again.")
            print(e)
            print("Please try again!")
            return
        finally:
            cm.close_connection()

        print("“Appointment ID: {appointment_id}, Caregiver username: {username}".format(appointment_id=str(id).strip("(),"), username=freeCaregiver))

def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        print("Please try again!")
        quit()
    except ValueError:
        print("Please enter a valid date!")
        print("Please try again!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        print("Please try again!")
        return
    print("Availability uploaded!")


def cancel(tokens):
    if len(tokens) != 2:
        print("Please try again!")
        return

    # check 1: check if the current logged-in 
    if ((current_caregiver == None) and (current_patient == None)):
        print("Please login first!")
        return

    id = tokens[1]

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    upcomingAppointments = "DELETE FROM Appointments WHERE appointmentID = %s AND (PUsername = %s OR Username = %s)"
    try:
        if current_patient is None:
            patient = 'null'
            caregiver = current_caregiver.username
        else:
            patient = current_patient.username
            caregiver = 'null'

        cursor.execute(upcomingAppointments, (id, patient, caregiver))

        for row in cursor:
            for i in row:
                print(i,end=" ")
            print()
    except pymssql.Error:
        # print("Error occurred when getting Vaccine")
        print("Please try again!")
        raise
    finally:
        conn.commit()
        cm.close_connection()
        print("Appointment cancelled!")
    return None


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Db-Error:", e)
        print("Please try again!")
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        print("Please try again!")
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            print("Please try again!")
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            print("Please try again!")
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            print("Please try again!")
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            print("Please try again!")
            return
    print("Doses updated!")


def show_appointments(tokens):
    # First check if there are the right number of tokens
    if len(tokens) != 1:
        print("Appointment search failed.")
        print("Incorrect number of inputs")
        print("Please try again!")
        return

    # Check if logged in
    if ((current_caregiver == None) and (current_patient == None)):
        print("Please login first!")
        return

    # Get the appointments
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    upcomingAppointments = "SELECT * FROM Appointments WHERE Username = %s or PUsername = %s ORDER BY appointmentID"
    try:
        if current_patient is None:
            patient = 'null'
            caregiver = current_caregiver.username
        else:
            patient = current_patient.username
            caregiver = 'null'

        cursor.execute(upcomingAppointments, (caregiver, patient))

        for row in cursor:
            for i in row:
                print(i,end=" ")
            print()

    except pymssql.Error:
        # print("Error occurred when getting Vaccine")
        print("Please try again!")
        raise
    finally:
        cm.close_connection()
    return None


def logout(tokens):
    global current_patient
    global current_caregiver
    try:
        if current_patient is None and current_caregiver is None:
            print("Please login first.")
            return
        if current_patient is not None:
            current_patient = None
        if current_caregiver is not None:
            current_caregiver = None
        print("Successfully logged out!")
    except Exception as e:
        print("Please try again!")
        return


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>") 
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>") 
    print("> reserve <date> <vaccine>")
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout") 
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
