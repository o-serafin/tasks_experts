from singleton_db_pool import DataBasePool


class query_executor:

    #method for DQL statements
    def get_query(self, connection, querry):
        ps_cursor = connection.cursor()
        ps_cursor.execute(querry)
        mobile_records = ps_cursor.fetchall() 
        for row in mobile_records:
            print(row)
        print(' ')

    #method for DDL and DML statements
    def alter_querry(self, conn, querry):
        cursor = conn.cursor()
        cursor.execute(querry)
        conn.commit()
   

def main():
    exec = query_executor()
    with DataBasePool(1,10, password='****', database='test_database') as dbp:
        p = dbp.get_connection()
        exec.get_query(p, 'select * from employees')
        exec.alter_querry(p, "insert into employees values ('191351','divit','100000.0'), ('191352','rhea','70000.0');")
        exec.get_query(p, 'select * from employees')


if __name__ == "__main__":
    main()
