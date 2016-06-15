from conftrak.client.api import (ConfigurationReference)


def test_api_smoke():
    c_create = ConfigurationReference.create
    c_find = ConfigurationReference.find
    c_update = ConfigurationReference.update
    c_delete = ConfigurationReference.delete
    c_get_schema = ConfigurationReference.get_schema
