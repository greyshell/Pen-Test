#!/usr/bin/env python3

# author: greyshell
# description: setup mysql db connection

import mysql.connector
import os


class MySQLdb:
    instance = None

    # singleton class
    class __MySQLdb:
        def __init__(self):
            """
            create a database connection for MySQL database
            """
            try:
                import keyring
                username = keyring.get_password('mysql', 'username')
                password = keyring.get_password('mysql', 'password')
            except ImportError as err:
                print(f"inside the container: {err}")
                username = os.environ.get("username")
                password = os.environ.get("password")

            try:
                # pick database credentials from keyring
                self.conn = mysql.connector.connect(user=username,
                                                    password=password,
                                                    host='localhost',
                                                    database='vulnapp')

            except mysql.connector.Error as err:
                print(err)
                exit(0)

    def __init__(self):
        if MySQLdb.instance is None:
            MySQLdb.instance = MySQLdb.__MySQLdb()

    @property
    def conn(self):
        return MySQLdb.instance.conn

    @staticmethod
    def close():
        if MySQLdb.instance is not None:
            MySQLdb.instance.conn.close()
            MySQLdb.instance = None
