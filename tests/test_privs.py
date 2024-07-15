from titan.privs import PRIVS_FOR_RESOURCE_TYPE
from titan.enums import ResourceType


def test_resource_privs_is_complete():
    for resource_type in ResourceType:
        assert resource_type in PRIVS_FOR_RESOURCE_TYPE, f"{resource_type} is missing from PRIVS_FOR_RESOURCE_TYPE"
