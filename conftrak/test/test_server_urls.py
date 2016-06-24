import uuid
import ujson
import pytest
import time as ttime
from conftrak.ignition import Application
from conftrak.server.engine import (db_connect)
from .utils import testing_config as TESTING_CONFIG

try:
    from urllib import urlencode # Python 2
except ImportError:
    from urllib.parse import urlencode # Python 3

@pytest.fixture
def app():
    db = db_connect(TESTING_CONFIG['database'], TESTING_CONFIG['mongohost'],
                    TESTING_CONFIG['mongoport'])
    return Application(db)


@pytest.mark.gen_test
def test_configuration_post(http_server, http_client, base_url):
    config_data = dict(beamline_id='test_bl', uid=str(uuid.uuid4()),
                       active=True, time= ttime.time(),key='test_config',
                       params=dict(param1='test1', param2='test2'))
    url = '{}/{}'.format(base_url, 'configuration')
    body = ujson.dumps(config_data)
    response = yield http_client.fetch(url, method='POST', body=body)
    assert response.code == 200



