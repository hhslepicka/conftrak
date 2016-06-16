from pymongo import MongoClient
import time as ttime
from conftrak.ignition import start_server
import uuid
import shutil

TESTING_CONFIG = {
    'database': 'conftrak_test_disposable_{}'.format(str(uuid.uuid4())),
    'mongo_server': 'localhost',
    'mongo_port': 27017,
    'host': 'localhost',
    'port': 7771,
    'timezone': 'US/Eastern'}

def conftrak_setup():
    # ensure tornado server started prior to tests
    ttime.sleep(1)

def conftrak_teardown():
    conn = MongoClient('{}:{}'.format(TESTING_CONFIG['mongo_server'],
                                      TESTING_CONFIG['mongo_port']))
    conn.conftrak.drop_collection('configuration')

class _baseSM:
        @classmethod  
        def test_create(self):
            db = self.db
            ast_uid = str(uuid.uuid4())
            db.create(name='obelix', location='gaul', occupation='hero',
                            uid=ast_uid)
