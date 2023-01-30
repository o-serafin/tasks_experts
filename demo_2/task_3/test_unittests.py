import pytest
from singleton_db_pool import DataBasePool
from psycopg2.extensions import connection
import psycopg2



@pytest.fixture
def db_1():
    db_1 = DataBasePool(1,10, password='1234', database='test_database')
    yield db_1
    db_1.close_pool()
    
@pytest.fixture
def db_2():
    db_2 = DataBasePool(1,8, password='1234', database='test_database')
    yield db_2
    db_2.close_pool()



# checks if singleton is implemented properly
def test_singleton(db_2, db_1):
    assert db_1 is db_2


# checks that if lists for connections in pool list and used list are created correctly
def test_lists_creation(db_1):
    assert db_1.pool_len() == 1
    assert db_1.in_use_len() == 0


# checks if get_connections function returns a psycopg2 connection object
def test_get_connection(db_1):
    conn = db_1.get_connection()
    assert conn is not None
    assert isinstance(conn, connection)
    db_1.return_connection(conn)


# checks if error is raised when invalid number of connections is given
def test_invalid_values():
    with pytest.raises(ValueError, match='Invalid initializing values'):
        conn = DataBasePool(-1,10)


# checks if  raising exception works when someone tries to return foreign connection
def test_put_foreign_connection(db_1):
    with pytest.raises(ConnectionError, match="Connection does not come from this pool"):
        defaultKwargs = { 'host': 'localhost', 'port': '5432', 'password': 'postgres', 'database': 'test_database', 'user': 'postgres' }
        conn = psycopg2.connect(**defaultKwargs)
        db_1.return_connection(conn)

