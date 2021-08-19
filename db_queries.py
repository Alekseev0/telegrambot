import psycopg2

from constants import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE


def insert(records):
    try:
        connection = psycopg2.connect(user=DB_USER,
                                      password=DB_PASSWORD,
                                      host=DB_HOST,
                                      port=DB_PORT,
                                      database=DB_DATABASE)
        cursor = connection.cursor()

        postgres_insert_query = "INSERT INTO currencies (exchange_rate, last_update, name) VALUES (%s,%s,%s)"
        cursor.executemany(postgres_insert_query, records)

        connection.commit()
        count = cursor.rowcount
        print(count, "Record inserted successfully into currencies table")

    except (Exception, psycopg2.Error) as error:
        raise error

    finally:
        if connection:
            cursor.close()
            connection.close()



def update(records):
    try:
        connection = psycopg2.connect(user=DB_USER,
                                      password=DB_PASSWORD,
                                      host=DB_HOST,
                                      port=DB_PORT,
                                      database=DB_DATABASE)
        cursor = connection.cursor()

        postgres_update_query = "UPDATE currencies SET exchange_rate = %s, last_update = %s WHERE name = %s"
        cursor.executemany(postgres_update_query, records)

        connection.commit()
        count = cursor.rowcount
        print(count, "Record updated successfully into currencies table")

    except (Exception, psycopg2.Error) as error:
        print("Error while updating PostgreSQL table", error)

    finally:

         if connection:
            cursor.close()
            connection.close()



def select(*args):
    try:
        connection = psycopg2.connect(user=DB_USER,
                                      password=DB_PASSWORD,
                                      host=DB_HOST,
                                      port=DB_PORT,
                                      database=DB_DATABASE)

        cursor = connection.cursor()
        try:
            # This condition is used to receive last time when currency was requested from web service
            if type(args[0]) is int:
                postgres_select_query = "SELECT last_update FROM currencies LIMIT %s"
                cursor.execute(postgres_select_query, (*args, ))
                currency_records = cursor.fetchall()
        # Query to extract all names and rates from database
        except (Exception, psycopg2.Error):
            postgres_select_query = "SELECT name, exchange_rate FROM currencies"
            cursor.execute(postgres_select_query)
            currency_records = cursor.fetchall()


    except (Exception, psycopg2.Error) as error:
        print(error)

    finally:
        if connection:
            cursor.close()
            connection.close()

    if currency_records:
        return currency_records

