from doct import Document
import time as ttime
import pytest
from .utils import conftrak_setup, conftrak_teardown
from .utils import testing_config as TESTING_CONFIG
from conftrak.client.commands import ConfigurationReference
from requests.exceptions import HTTPError, RequestException

import uuid
import ujson
import jsonschema

configs_uids = []
document_insertion_times = []


@pytest.fixture(scope='function')
def config_ref():
    c = ConfigurationReference()
    c.host = TESTING_CONFIG['mongohost']
    c.port = TESTING_CONFIG['serviceport']
    return c


class TestConfiguration:
    def setup_class(self):
        conftrak_setup()


    def teardown_class(self):
        conftrak_teardown()


    def test_commands_smoke(self):
        c_create = ConfigurationReference.create
        c_find = ConfigurationReference.find
        c_update = ConfigurationReference.update
        c_delete = ConfigurationReference.delete
        c_get_schema = ConfigurationReference.get_schema


    def test_configuration_constructor(self):
        c2 = ConfigurationReference()


    def test_connection_switch(self):
        c = ConfigurationReference()
        c.host = 'blah'
        pytest.raises(RequestException, c.create, 'test_beamline')
        c.host = TESTING_CONFIG['mongohost']
        c.create(beamline_id='lix')


    def test_configuration_create(self, config_ref):
        c1 = config_ref.create(beamline_id='test')
        c2 = config_ref.create(beamline_id='test', uid=str(uuid.uuid4()))
        c_kwargs = dict(key='detector', params={'model':'Pilatus1M',
                                                'vendor':'Dectris'})
        c3 = config_ref.create(beamline_id='test', **c_kwargs)


    def test_configuration_find(self, config_ref):
        config_data = dict(beamline_id='test_bl', uid=str(uuid.uuid4()),
                           active=True, time= ttime.time(),key='test_config',
                           params=dict(param1='test1', param2='test2'))

        config_ref.create(**config_data)
        c_ret = next(config_ref.find(uid=config_data['uid'], as_document=True))
        assert c_ret == Document('Configuration', config_data)


    def test_configuration_update(self, config_ref):
        config_data = dict(beamline_id='test_bl', uid=str(uuid.uuid4()),
                           active=True, time= ttime.time(),key='test_config',
                           params=dict(param1='test1', param2='test2'))
        config_ref.create(**config_data)
        config_ref.update(query={'uid': config_data['uid']},
                          update={'key': 'updated_key'})
        updated_conf = next(config_ref.find(uid=config_data['uid']))
        assert updated_conf['key'] == 'updated_key'


    def test_configuration_delete(self, config_ref):
        config_data = dict(beamline_id='test_bl', uid=str(uuid.uuid4()),
                           active=True, time= ttime.time(),key='test_config',
                           params=dict(param1='test1', param2='test2'))
        config_ref.create(**config_data)
        inserted = next(config_ref.find(uid=config_data['uid']))
        # Make sure that it was inserted
        assert inserted is not None
        config_ref.delete([config_data['uid']])
        with pytest.raises(StopIteration):
            deleted = next(config_ref.find(uid=config_data['uid']))


    def test_configuration_find_all(self, config_ref):
        config_data = dict(beamline_id='test_bl', uid=str(uuid.uuid4()),
                           active=True, time= ttime.time(),key='test_config',
                           params=dict(param1='test1', param2='test2'))
        config_ref.create(**config_data)
        inserted = next(config_ref.find(uid=config_data['uid']))
        # Make sure that it was inserted
        assert inserted is not None
        config_ref.delete([config_data['uid']])
        deleted = next(config_ref.find(active_only=False, uid=config_data['uid']))
        assert deleted is not None


    def test_configuration_schema(self, config_ref):
        config_data = dict(beamline_id='test_bl', uid=str(uuid.uuid4()),
                           active=True, time=ttime.time(),key='test_config',
                           params=dict(param1='test1', param2='test2'))
        schema = config_ref.get_schema()
        try:
            jsonschema.validate(config_data, schema)
        except:
            pytest.fail("test_configuration_schema failed on validate schema.")



