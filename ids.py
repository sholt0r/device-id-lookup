#!/bin/python3
# ids.py

"""
This module contains functions for updating the USB IDs database.

The USB IDs database is a SQLite database that contains information about USB vendors and devices.
The database has two tables: vendors and devices.
The vendors table has two columns: id and name.
The devices table has three columns: id, name, and vendor.

The module contains the following functions:
- get_ids: Get the USB IDs from the server.
- parse_data: Parse the USB IDs data into a DataFrame.
- format_data: Format the data into a list of tuples.
- update_db: Update the database with the new data.
- main: Update the database with the latest USB IDs data.

The module also contains two classes:
- Vendor: Represents a vendor with an ID and a name.
- Device: Represents a device with an ID, a name, and a vendor ID.

The module can be run as a script to update the database with the latest USB IDs data.

Example:
    $ python ids.py
    Database updated successfully

Author:
    sholt0r
"""

import requests, pandas as pd, sqlite3 as sql


IDS_DB = 'usb_ids.db'


class Vendor:
    """
    Represents a vendor with an ID and a name.

    :param id: The vendor ID.
    :param name: The vendor name.
    """

    def __init__(self, id, name):
        self.id = id
        self.name = name


class Device:
    """
    Represents a device with an ID, a name, and a vendor ID.

    :param device_id: The device ID.
    :param device_name: The device name.
    :param vendor: The vendor ID.
    """

    def __init__(self, device_id, device_name, vendor=None):
        self.vendor = vendor
        self.id = device_id
        self.name = device_name


def get_ids():
    """
    Get the USB IDs from the server.

    :return: The response from the server.
    """

    url = 'http://www.linux-usb.org/usb.ids'
    response = requests.get(url)
    if response.status_code == 200:
        return response
    else:
        return


def parse_data(data):
    """
    Parse the USB IDs data into a DataFrame.

    :param data: The USB IDs data.

    :return: The parsed data as a DataFrame.
    """

    lines = data.split('\n')
    parsed_data = []
    current_vendor_id = None
    current_vendor_name = None

    for line in lines:
        if line.strip() == '# List of known device classes, subclasses and protocols':
            break
        elif line.startswith('#') or line.strip() == '':
            continue
        elif not line.startswith('\t'):
            current_vendor_id, current_vendor_name = line.split('  ', 1)
        else:
            device_id, device_name = line.strip().split('  ', 1)
            parsed_data.append([current_vendor_id, current_vendor_name, device_id, device_name])

    df = pd.DataFrame(parsed_data, columns=['Vendor ID', 'Vendor Name', 'Device ID', 'Device Name'])
    return df


def format_data(df):
    """
    Format the data into a list of tuples.

    :param df: The DataFrame of the USB IDs data.

    :return: The formatted data as a list of tuples.
    """

    data = []
    for index, row in df.iterrows():
        vendor = Vendor(row['Vendor ID'], row['Vendor Name'])
        device = Device(row['Device ID'], row['Device Name'], vendor.id)
        data.append((vendor, device))
    return data


def update_db(con, data):
    """
    Update the database with the new data.

    :param con: The database connection.
    :param data: The new data to add to the database.

    :return: True if the update was successful, False otherwise.
    """

    try:
        # Create cursor
        cursor = con.cursor()

        # Drop tables if they exist
        cursor.execute('DROP TABLE IF EXISTS vendors')
        cursor.execute('DROP TABLE IF EXISTS devices')

        # Create tables
        cursor.execute('CREATE TABLE vendors (id TEXT, name TEXT)')
        cursor.execute('CREATE TABLE devices (id TEXT, name TEXT, vendor TEXT)')

        for vendor, device in data:
            # Insert data
            cursor.execute('INSERT INTO vendors VALUES (?, ?)', (vendor.id, vendor.name))
            cursor.execute('INSERT INTO devices VALUES (?, ?, ?)', (device.id, device.name, vendor.id))

        con.commit()
        return True
    except Exception as e:
        print(f'An error occurred:\n{e}')
        return False


def main(con):
    """
    Update the database with the latest USB IDs data.

    :param con: The database connection.

    :return: True if the database was updated successfully, False otherwise.
    """

    updated = False

    if con is None:
        con = sql.connect(IDS_DB)

    response = get_ids()
    if response.status_code == 200:
        df = parse_data(response.text)
        data = format_data(df)
        updated = update_db(con, data)
        if updated:
            print('Database updated successfully')
        else:
            print('Failed to update database')

    else:
        print('Failed to get data from server')
    
    return updated
