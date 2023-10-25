from psycopg2 import connect, OperationalError


def can_connect_to_postgres(
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432",
    database="postgres",
):
    try:
        connection = connect(
            f"postgresql://{user}:{password}@{host}:{port}/{database}"
        )
        connection.close()

        return True

    except OperationalError:
        return False
