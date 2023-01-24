import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql


class Appointment:
    def __init__(self, id, patient, caregiver, date):
        self.id = id
        self.patient = patient
        self.caregiver = caregiver
        self.date = date

    def create(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_appointment = "INSERT INTO Appointments VALUES (%s, %s, %s, %s)"
        try:
            cursor.execute(add_appointment, (self.id, self.date, self.patient, self.caregiver))
            conn.commit()
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
