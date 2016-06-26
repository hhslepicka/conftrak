import uuid
import ujson
import pytest
import time as ttime
from tornado.httputil import url_concat
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
    payload = dict(beamline_id='test_bl', uid=str(uuid.uuid4()),
                       active=True, time= ttime.time(),key='test_config',
                       params=dict(param1='test1', param2='test2'))
    url = '{}/{}'.format(base_url, 'configuration')
    body = ujson.dumps(payload)
    response = yield http_client.fetch(url, method='POST', body=body,
                                       raise_error=False)
    assert response.code == 200


@pytest.mark.gen_test
def test_configuration_get(http_server, http_client, base_url):
    payload = ujson.dumps(dict(active_only=True))
    url = '{}/{}?{}'.format(base_url, 'configuration', payload)
    body = None
    response = yield http_client.fetch(url, method='GET', body=body,
                                       raise_error=False)
    assert response.code == 200

@pytest.mark.gen_test
def test_configuration_put(http_server, http_client, base_url):
    payload_insert = dict(beamline_id='test_bl', uid=str(uuid.uuid4()),
                       active=True, time= ttime.time(),key='test_config',
                       params=dict(param1='test1', param2='test2'))
    url = '{}/{}'.format(base_url, 'configuration')
    body = ujson.dumps(payload_insert)
    response = yield http_client.fetch(url, method='POST', body=body,
                                       raise_error=False)

    payload_update = dict(query={'uid': payload_insert['uid']},
                          update={'key': 'updated_key'})
    body = ujson.dumps(payload_update)
    response = yield http_client.fetch(url, method='PUT', body=body,
                                       raise_error=False)

    assert response.code == 200

@pytest.mark.gen_test
def test_configuration_delete(http_server, http_client, base_url):
    payload_insert = dict(beamline_id='test_bl', uid=str(uuid.uuid4()),
                       active=True, time= ttime.time(),key='test_config',
                       params=dict(param1='test1', param2='test2'))
    url = '{}/{}'.format(base_url, 'configuration')
    body = ujson.dumps(payload_insert)
    response = yield http_client.fetch(url, method='POST', body=body,
                                       raise_error=False)

    payload_delete = dict(uid_list=[payload_insert['uid']])
    url = url+"?"+ujson.dumps(payload_delete)
    body = None
    response = yield http_client.fetch(url, method='DELETE', body=body,
                                       raise_error=False)

    assert response.code == 200


@pytest.mark.gen_test
def test_schema_get(http_server, http_client, base_url):
    url = '{}/{}'.format(base_url, 'schema')
    body = None
    url = url + '?'+ujson.dumps('configuration')
    response = yield http_client.fetch(url, method='GET', body=body,
                                       raise_error=False)
    assert response.code == 200


@pytest.mark.gen_test
def test_schema_put(http_server, http_client, base_url):
    url = '{}/{}'.format(base_url, 'schema')
    body = 'configuration'
    response = yield http_client.fetch(url, method='PUT', body=body,
                                       raise_error=False)
    assert response.code == 405


@pytest.mark.gen_test
def test_schema_post(http_server, http_client, base_url):
    url = '{}/{}'.format(base_url, 'schema')
    body = 'configuration'
    response = yield http_client.fetch(url, method='POST', body=body,
                                       raise_error=False)
    assert response.code == 405


