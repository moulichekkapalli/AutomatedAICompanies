from datetime import datetime, timezone
import psycopg2
import psycopg2.extras
import os
from app import app
hostname = os.environ.get("DB_HOSTNAME")
database = os.environ.get("DB_NAME")
username = os.environ.get("DB_USERNAME")
pwd = os.environ.get("DB_PASSWORD")
port_id = os.environ.get("DB_PORTID")
connection = None


def pg_connection():
    try:
        connection = psycopg2.connect(
            host=hostname,
            dbname=database,
            user=username,
            password=pwd,
            port=port_id)
        print("Connected to db", connection.get_dsn_parameters()["dbname"])
        return connection
    except(Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL database", error)
        connection = None
        raise Exception(error)


def bulkstore(new_urls):
    try:
        connection = pg_connection()
        if not connection:
            raise Exception('Error connecting to db')
        cursor = connection.cursor()
        # cursor.mogrify() to insert multiple values
        args = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s)",
                        i).decode('utf-8') for i in new_urls)
        # executing the insert statement
        cursor.execute("INSERT INTO companyinfo VALUES " + (args))
        connection.commit()
        count = cursor.rowcount
        print(count, "Record inserted successfully into table")
        return new_urls

    except Exception as error:
        print("Error in bulkstore method: ", error)
        raise Exception(error)

    finally:
        if connection is not None:
            connection.close()
            print("Connection closed: ", connection.closed)


def check(url):
    try:
        connection = pg_connection()
        if not connection:
            raise Exception('Error connecting to db')
        cursor = connection.cursor()
        fetch_url = "select category from companyinfo where url='" + url + "'"
        cursor.execute(fetch_url)
        url_record = cursor.fetchone()
        print("url_record: ", url_record)
        if url_record is not None:
            return url_record[0]
        else:
            url_record
    except Exception as error:
        print("Error in check(url) method: ", error)
        url_record = None
        raise Exception(error)
    finally:
        if connection is not None:
            connection.close()
            print("Connection closed: ", connection.closed)


def fetchURLs():
    try:
        connection = pg_connection()
        if not connection:
            raise Exception('Error connecting to db')
        cursor = connection.cursor()
        select_urls = """ select url from companyinfo """
        cursor.execute(select_urls)
        existing_urls = cursor.fetchall()
        existing_urls = [tup[0] for tup in existing_urls]
        print("existing_urls: ", existing_urls)
        return existing_urls
    except Exception as error:
        print("Error in fetchURLs method", error)
        existing_urls = None
        raise Exception(error)
    finally:
        if connection is not None:
            connection.close()
            print("Connection closed: ", connection.closed)


def store(res):
    try:
        connection = pg_connection()
        if not connection:
            raise Exception('Error connecting to db')
        cursor = connection.cursor()
        title = res["title"]
        url = res["url"]
        extracteddata = res["data"]
        summary = res["summary"]
        category = res["PCClass"]
        dt = datetime.now(timezone.utc)
        insert_query = """ INSERT INTO companyinfo (title,url, extracteddata, category,summary,created_on) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (url) DO NOTHING"""
        record_to_insert = (title, url, extracteddata,
                            category, summary, dt)
        r = cursor.execute(insert_query, record_to_insert)
        connection.commit()
        count = cursor.rowcount
        print(count, "Record inserted successfully into companyinfo table")

    except Exception as error:
        print(error)
        raise Exception(error)
    finally:
        if connection is not None:
            connection.close()
            print("Connection closed: ", connection.closed)
