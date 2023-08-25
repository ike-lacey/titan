import uuid

import pytest
from titan.client import get_session
from titan.resources import (
    Database,
    Role,
    Schema,
    Table,
    User,
    View,
    Warehouse,
)


@pytest.fixture(scope="session")
def suffix():
    return str(uuid.uuid4())[:8]


@pytest.fixture(scope="session")
def test_db(suffix):
    return f"TEST_DB_RUN_{suffix}"


@pytest.fixture(scope="session")
def marked_for_cleanup():
    """List to keep track of resources created during tests."""
    return []


@pytest.fixture(scope="session")
def cursor(suffix, test_db, marked_for_cleanup):
    session = get_session()
    with session.cursor() as cur:
        cur.execute(f"ALTER SESSION set query_tag='titan_package:test::{suffix}'")
        cur.execute(f"CREATE DATABASE {test_db}")
        cur.execute("USE ROLE ACCOUNTADMIN")
        yield cur
        for res in marked_for_cleanup:
            cur.execute(res.drop_sql(if_exists=True))
        cur.execute(f"DROP DATABASE {test_db}")


resources = [
    {"test": "database", "resource_cls": Database},
    {"test": "schema", "resource_cls": Schema},
    {"test": "role", "resource_cls": Role},
    {"test": "table", "resource_cls": Table, "data": {"columns": ["id int"]}},
    {"test": "user", "resource_cls": User},
    {"test": "view", "resource_cls": View, "data": {"as_": "SELECT 1::INT as col"}},
    {"test": "warehouse", "resource_cls": Warehouse},
]


@pytest.fixture(
    params=resources,
    ids=[f"test_{config['test']}" for config in resources],
    scope="function",
)
def resource(request, suffix, marked_for_cleanup):
    resource = request.param
    resource_cls = resource["resource_cls"]
    data = resource.get("data", {})
    res = resource_cls(name=f"test_{suffix}", **data)
    marked_for_cleanup.append(res)
    yield res


def test_create_drop(resource, test_db, cursor):
    cursor.execute(f"USE DATABASE {test_db}")
    cursor.execute(resource.create_sql())
    cursor.execute(resource.drop_sql())
