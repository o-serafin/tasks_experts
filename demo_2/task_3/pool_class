import psycopg2
import threading
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
   
#DataBasePool class provides connection to postgres database, and allows to manage connections pool
class DataBasePool:
    
    """Classic Singleton __new__ function"""
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DataBasePool, cls).__new__(cls)
        return cls.instance


    '''Initialazing DataBasePool obcject.
       Creating defined by user number of initial connections and connecting to specified database.
       Defaulf parameters are: 'host': 'localhost', 'port': '5432', 'password': 'postgres', 'database': 'postgres', 'user': 'postgres'
       You can specify which of them need to be changed
    Parameters:
        - min_num - number of initial connections
        - max_num - maximal number of connections in pool
        - host - postgres host
        - port - postgres port
        - password - postgres password
        - database - postgres database name
        - user - postgres user
        
    Example:
           db_pool = DataBasePool(
                5,
                10,
                database="postgres_db",
                port=5431,)
           All connection arguments are the same as deafault except port and database
    '''
    def __init__(self, min_num: int, max_num: int, **kwargs):
        defaultKwargs = { 'host': 'localhost', 'port': '5432', 'password': 'postgres', 'database': 'postgres', 'user': 'postgres' }
        self.kwargs = { **defaultKwargs, **kwargs }

        if min_num < 0 or min_num > max_num:
            raise ValueError('Invalid initializing values')

        self.min_num = min_num
        self.max_num = max_num

        self.pool = []
        self.in_use = []

        for i in range(self.min_num):
            connection = psycopg2.connect(**self.kwargs)
            self.pool.append(connection)


    """Decorator function for thread locking"""
    def locking(fn):
        lock = threading.Lock()
        def wrapper(*args, **kwargs):
            lock.acquire()
            try:
                return fn(*args, **kwargs)
            finally:
                lock.release()
        return wrapper

    """Function returns us free connection from the pool."""
    @locking
    def get_connection(self):
        if (len(self.in_use) + len(self.pool)) < self.max_num:
            logging.info("Connection taken from pool")
            if self.pool != []:
                connection = self.pool.pop()
            else:
                connection = psycopg2.connect(**self.kwargs)
            self.in_use.append(connection)
            return connection
        logging.info("All connections are occupied")
        return None
        
    """returning given connection to the pool
        Parameter:
            connection - connection that we return
    """
    @locking
    def return_connection(self, connection):
        if connection not in self.used:
            raise ConnectionError('Connection does not come from this pool')
        self.pool.append(connection)
        self.in_use.remove(connection)
        logging.info("Connection returned to pool")

    """Closing all exisitng connections in a pool."""
    @locking
    def close_pool(self):
        for connection in self.pool:
            connection.close()
        for connection in self.in_use:
            connection.close()
        self.pool = None
        self.used = None
        logging.info("Pool was closed")
    
    """methods that allow us to use context manager"""
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        self.close_pool()
        return isinstance(value, TypeError)
