import psycopg2
import psycopg2.extras

class DB:
    def __init__(self, db, dbpass, dbuser, host):
        self.conn = psycopg2.connect(
            dbname=db,
            user=dbuser,
            password=dbpass,
            host=host
        )

        self.cur = self.conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.conn.rollback()
        self.close()

    def query(self, sql, params=None):
        self.cur.execute(sql, params or ())
        return self.cur.fetchall()

    def execute(self, sql, params=None):
        self.cur.execute(sql, params or ())
        return self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()