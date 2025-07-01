from django.test import TestCase
from django.db import connections
from django.db.utils import OperationalError

class DatabaseConnectionTest(TestCase):
    def test_secondary_database_connection(self):
        db_conn = connections['oracle_p']
        try:
            c = db_conn.cursor()
        except OperationalError:
            connected = False
        else:
            connected = True
        self.assertTrue(connected)


