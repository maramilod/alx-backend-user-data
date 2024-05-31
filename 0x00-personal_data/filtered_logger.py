#!/usr/bin/env python3
"""
Filtered Logger
"""
import re
from typing import List
import logging
import mysql.connector
import os
from datetime import datetime


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self._fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record by filtering the message.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log record with filtered fields.
        """
        original_message = super().format(record)
        filtered_message = filter_datum(self._fields, self.REDACTION,
                                        original_message, self.SEPARATOR)
        return filtered_message


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """
    Filter the given `message` by replacing the values of the fields given in
    `fields` with the `redaction` string. Separate the fields with `separator`.

    Args:
        fields (List[str]): List of field names to filter.
        redaction (str): String to replace the field values with.
        message (str): String to filter.
        separator (str): String used to separate fields in the message.

    Returns:
        str: Filtered message.
    """
    for field in fields:
        message = re.sub(field + "=.*?" + separator,
                         field + "=" + redaction + separator, message)
    return message


def get_logger() -> logging.Logger:
    """
    Returns a logger with a RedactingFormatter.

    Returns:
        logging.Logger: A logger with a RedactingFormatter.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.addHandler(handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Returns a MySQL connection object.

    This function reads the database credentials from the environment variables
    and creates a MySQL connection object. If the environment variables are not
    set, it uses default values.

    Args:
        None

    Returns:
        mysql.connector.connection.MySQLConnection: A MySQL connection object.
    """
    user = os.getenv('PERSONAL_DATA_DB_USERNAME', 'root')
    password = os.getenv('PERSONAL_DATA_DB_PASSWORD', '')
    host = os.getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    database = os.getenv('PERSONAL_DATA_DB_NAME', '')

    connection = mysql.connector.connect(
        user=user,
        password=password,
        host=host,
        database=database
    )
    return connection


def main():
    '''
    Main function
    '''
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")

    for row in cursor:
        message = "name={}; email={}; phone={}; ssn={}; password={};\
ip={}; last_login={}; user_agent={};".format(*tuple(row))
        get_logger().info(message)

    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
