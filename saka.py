""" Connection pool class with singleton pattern"""
import psycopg2  

class DB_Pool:
    def __new__(cls, *args):
        """ Singleton pattern """
        if not hasattr(cls, 'instance'):
            cls.instance = super(DB_Pool, cls).__new__(cls)
        return cls.instance

    def __init__(self, conn_min, conn_max):
        self.__conn_min = conn_min
        self.__conn_max = conn_max
        self.__conn_current = 0
        self.__conn_list = []

        ''' Basic validation number of connection '''
        if (self.__conn_min < 0 or self.__conn_max < 0 or self.__conn_min > self.__conn_max):
            self.__conn_min = 0
            self.__conn_max = 10

        ''' Initializing connection list '''
        for i in range(0,self.__conn_min):
            self.__conn_list.append(psycopg2.connect(user ='username',
                                                     password ='secret',
                                                     database ='database',
                                                     host ='172.24.0.3',
                                                     port = '5432'))                                    
        ''' Set current number of connection '''
        self.__conn_current = self.__conn_min


    def __get_connection(self):
        ''' Function get free connection from pool '''

        # Free connections are available in connection list
        if len(self.__conn_list) > 0:
            connection = self.__conn_list.pop()

        # Free connections are NOT available
        # but it's possible to create new one
        elif self.__conn_current < self.__conn_max:
            connection = psycopg2.connect(user='username',
                                          password='secret',
                                          database='database',
                                          host='172.24.0.3',
                                          port = '5432')
            self.__conn_current+=1

        # Free connections are NOT available
        # Not possible to create new connection
        else:
            connection = None
        return connection


    def __return_connection(self, connection):
        ''' Function return connection to the pool '''
        self.__conn_list.append(connection)


    def send_to_db(self, query, list):
        ''' Function sending data to database'''
        connection = self.__get_connection()
        if connection is not None:
            with connection.cursor() as cursor:
                cursor.execute(query, list)
            connection.commit()
            self.__return_connection(connection)


    def load_from_db(self, query, list):
        ''' Function loading data from database'''
        received_data = None
        connection = self.__get_connection()
        if connection is not None:
            with connection.cursor() as cursor:
                cursor.execute(query, list)
                received_data = cursor.fetchone()
                print("Data", received_data)
            self.__return_connection(connection)
        return received_data
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      """
Name: db_connection.py
Module for managing database connection pool using psycopg2.
"""
import logging
import sys
from typing import List
import threading
import psycopg2


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger("database_connection_pool")
# TODO - Create some exceptions


class DBConnectionPoolMeta(type):
    """
    The Singleton meta class for DatabaseConnection class.
    This meta class ensures that only one instance of the connection pool is created,
    regardless of how many times the class is instantiated.
    Args:
        _instances(dict): A dictionary to store singletion instances.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DBConnectionPool(metaclass=DBConnectionPoolMeta):
    """The DatabaseConnectionPool class used to create and manage a pool of database connections
    with using the psycopg2 library.
    Attributes:
        minconn(int): minimum number of connections in pool.
        maxconn(int): maximum number of connections in pool.
        kwargs: host, port, db_user, user_pass
        _pool(list): list with available connections.
        _used(dict): dictionary with connections that are currently used by clients.
        lock(obj):
    Methods:
        __init__: creates DBConnectionPool instance.
        get_connection(): returns DB connection from the pool, or creates new when pool is empty.
        return_connection(): closes a single DB connection and store that into pool.
        close_all(): closes all DB connections.
        print_pool_content(): returns a string with _pool content.
        print_used_content(): returns a string with _used content.
    """

    def __init__(self, minconn: int, maxconn: int, **kwargs) -> None:
        """Creation of database connection pool.
            Args:
                :minconn(int): minimum number of connections.
                :maxconn(int): maximum number of connections.
            Example:
               db_pool_1 = DBConnectionPool(
                    5,
                    10,
                    host="localhost",
                    user="postgres_usr",
                    password="postgres_pass",
                    dbname="postgres_db",
                    port=5431,
        )
        """
        self.minconn = minconn
        self.maxconn = maxconn

        self._kwargs = kwargs

        self._pool = []
        self._used = []

        self.lock = threading.Lock()

        # Creation of the required number of connections, which will be stored in db pool.
        for _ in range(self.minconn):
            conn = psycopg2.connect(**self._kwargs)
            self._pool.append(conn)

    def get_connection(self) -> "psycopg2.extensions.connection":
        """Returns a database connection.
        Returns:
            psycopg2.extensions.connection: psycopg2.extensions.connection object.
        """
        with self.lock:
            if len(self._used) < self.maxconn:
                if self._pool:
                    conn = self._pool.pop()
                else:
                    conn = psycopg2.connect(**self._kwargs)
                self._used.append(conn)
                return conn

            print("too many connections")
            # raise Exception("Too many connections.")
            return None


    def return_connection(self, conn: "psycopg2.extensions.connection") -> None:
        """Closing a database connection."""

        with self.lock:
            self._used.remove(conn)
            self._pool.append(conn)

    def close_all(self) -> None:
        """Closes all existing database connections."""
        with self.lock:
            for connection in self._pool:
                connection.close()
            for connection in self._used:
                connection.close()
            self._pool = []
            self._used = []

    def execute_query(self, query: str) -> List:
        """Executes SQL query in database.
        Args:
            query (str): SQL query
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query)
            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()
            else:
                result = None
            connection.commit()
            cursor.close()
            self.return_connection(connection)
            return result

        except psycopg2.Error as err:
            log.error("Execute query error: %s", err)
            return None

    def __enter__(self):
        self.connection = self.get_connection()
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.return_connection(self.connection)
        self.connection = None
    
    
    def print_pool_content(self) -> str:
        """Returns a string with the content of the _pool variable for logging purposes.
        Returns:
            str: Content of _pool variable
        """
        return f"Pool List: {self._pool}\nLen of Pool: {len(self._pool)}"

    def print_used_content(self) -> str:
        """Returns a string with the content of the _used variable for logging purposes.
        Returns:
            str: Content of _used variable
        """
        return f"Used List: {self._used}\nLen of Used: {len(self._used)}"

    def check_status(self) -> dict:
        """Returns a dict with informations about available connections and in use connections
        Returns:
            dict: info about available and in use connections
        """
        return {"available connections (_pool)": len(self._pool), "in use connections (_used)": len(self._used)}
