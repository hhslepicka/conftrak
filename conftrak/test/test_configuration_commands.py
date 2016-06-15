from doct import Document
import time as ttime
import pytest
from conftrak.testing import conftrak_setup, conftrak_teardown
from conftrak.client.api import ConfigurationReference
from requests.exceptions import HTTPError, RequestException
from conftrak.testing import TESTING_CONFIG

import uuid

configs_uids = []
document_insertion_times = []


@pytest.fixture(scope='function')
def config_ref():
    c = ConfigurationReference()
    c.host = TESTING_CONFIG['host']
    c.port = TESTING_CONFIG['port']
    return c


def teardown():
    conftrak_teardown()


def test_configuration_constructor():
    c2 = ConfigurationReference()


def test_connection_switch():
    c = ConfigurationReference()
    c.host = 'blah'
    pytest.raises(RequestException, c.create, 'test_beamline')
    c.host = TESTING_CONFIG['host']
    c.create(beamline_id='lix')


def test_configuration_create(config_ref):
    c1 = config_ref.create(beamline_id='test')
    c2 = config_ref.create(beamline_id='test', uid=str(uuid.uuid4()))
    c_kwargs = dict(key='detector', params={'model':'Pilatus1M',
                                            'vendor':'Dectris'})
    c3 = config_ref.create(beamline_id='test', **c_kwargs)


def test_configuration_find(config_ref):
    config_data = dict(beamline_id='test_bl', uid=str(uuid.uuid4()),
                       active=True, time= ttime.time(),key='test_config',
                       params=dict(param1='test1', param2='test2'))

    config_ref.create(**config_data)
    c_ret = next(config_ref.find(uid=config_data['uid'], as_document=True))
    assert c_ret == Document('Configuration', config_data)


def test_configuration_update(config_ref):
    config_data = dict(beamline_id='test_bl', uid=str(uuid.uuid4()),
                       active=True, time= ttime.time(),key='test_config',
                       params=dict(param1='test1', param2='test2'))
    config_ref.create(**config_data)
    config_ref.update(query={'uid': config_data['uid']},
                      update={'key': 'updated_key'})
    updated_conf = next(config_ref.find(uid=config_data['uid']))
    assert updated_conf['key'] == 'updated_key'

def test_configuration_delete(config_ref):
    assert False


def test_configuration_find_all(config_ref):
    assert False


