from psycopg2 import connect, OperationalError


def can_connect_to_postgres():
    try:
        connection = connect("postgresql://postgres:postgres@localhost:5432/postgres")
        connection.close()

        return True

    except OperationalError:
        return False
