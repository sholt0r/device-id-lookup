#!/bin/python3
# usb-lookup.py

"""
This script allows you to search for USB device information using vendor and device IDs.
It provides functions to search for vendors, devices, and perform reverse device searches.
You can also update the USB IDs database and perform interactive searches.

Usage:
    usb-lookup.py [-u] [-v VENDOR] [-d DEVICE] [-c VENDOR DEVICE] [-i] [-h]
    usb-lookup.py

Options:
    -u          Update the USB IDs database.
    -v VENDOR   Perform a reverse device search for a vendor.
    -d DEVICE   Perform a device search.
    -c VENDOR DEVICE
                Perform a complete search for a vendor and device.
    -i          Enter interactive mode.
    -h          Show this help message and exit.

Examples:
    usb-lookup.py -u
    usb-lookup.py -v 8086
    usb-lookup.py -d 8086
    usb-lookup.py -c 8086 0a2b
    usb-lookup.py -i
    usb-lookup.py -h

Note:
    The USB IDs database is stored in usb_ids.db and is updated from http://www.linux-usb.org/usb.ids.
    The database is updated automatically when the script is run with the -u option.
    The -i option allows you to enter interactive mode to perform searches.

Author:
    sholt0r
"""

# Import libraries
import sys, os, ids, sqlite3 as sql, argparse


# Define consants
DEBUG = True
IDS_DB = 'usb_ids.db'


# Utility
def clear_screen():
    try:
        if DEBUG:
            return
        
        if sys.platform == 'win32':
            os.system('cls')
        else:
            os.system('clear')
    except Exception:
        return


def prompt_continue():
    try:
        input('\nPress enter to continue...')
        clear_screen()

    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f'\n{e}')
        return


# Define Functions
def check_db(con):
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vendors'")
    db_exists = cursor.fetchone()
    if db_exists:
        return True
    
    print('Database not found! Updating...')
    updated = ids.main(con)
    if updated:
        print('Database updated!')
    else:
        print('Database update failed!')

    return updated


def search_vendor(con, vendor_id):
    """
    Search for a vendor by ID.

    Args:
        con: A sqlite3 connection object.
        vendor_id: The vendor ID to search for.

    Returns:
        A Vendor object if the vendor is found, None otherwise.
    """
    try:
        cursor = con.cursor()
        cursor.execute('SELECT * FROM vendors WHERE id = ?', (vendor_id,))
        vendor = cursor.fetchone()
        if vendor:
            return ids.Vendor(vendor[0], vendor[1])
        else:
            return

    except Exception as e:
        print(f'An error occurred:\n{e}')
        return


def search_devices(con, device_id):
    """
    Search for devices by ID.

    Args:
        con: A sqlite3 connection object.
        device_id: The device ID to search for.

    Returns:
        A list of Device objects if devices are found, None otherwise.
    """
    try:
        cursor = con.cursor()
        cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        devices = cursor.fetchall()
        if devices:
            return [ids.Device(device[0], device[1], device[2]) for device in devices]
        else:
            return
    except Exception as e:
        print(f'An error occurred:\n{e}')
        return


def search_device(con, device_id, vendor_id=None):
    """
    Search for a device by ID.

    Args:
        con: A sqlite3 connection object.
        device_id: The device ID to search for.
        vendor_id: The vendor ID to search for. Optional.

    Returns:
        A Device object if the device is found, None otherwise.
    """
    try:
        cursor = con.cursor()
        if not vendor_id is None:
            cursor.execute('SELECT * FROM devices WHERE id = ? AND vendor = ?', (device_id, vendor_id))
        else:
            cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))

        device = cursor.fetchone()

        if device:
            return ids.Device(device[0], device[1], device[2])
        else:
            return
                
    except Exception as e:
        print(f'An error occurred:\n{e}')
        return


def reverse_device_search(con, vendor_id, device_name=None):
    """
    Perform a reverse device search for a vendor.
    
    Args:
        con: A sqlite3 connection object.
        vendor_id: The vendor ID to search for.
        device_name: The device name to search for. Optional.

    Returns:
        A list of Device objects if devices are found, None otherwise.
    """
    try:
        cursor = con.cursor()
        if not device_name is None:
            cursor.execute('SELECT * FROM devices WHERE name = ? AND vendor = ?', (device_name, vendor_id))
        else:
            cursor.execute('SELECT * FROM devices WHERE vendor = ?', (vendor_id,))
        devices = cursor.fetchall()
        if devices:
            return [ids.Device(device[0], device[1], device[2]) for device in devices]
        else:
            return
    except Exception as e:
        print(f'An error occurred:\n{e}')
        return


def search_complete(con, vendor_id, device_id):
    """
    Perform a complete search for a vendor and device.

    Args:
        con: A sqlite3 connection object.
        vendor_id: The vendor ID to search for.
        device_id: The device ID to search for.

    Returns:
        A tuple of Vendor and Device objects if the vendor and device are found, None otherwise.
    """
    try:
        vendor = search_vendor(con, vendor_id)
        device = search_device(con, device_id, vendor_id)
        return vendor, device
    
    except Exception as e:
        print(f'An error occurred:\n{e}')
        return


# Search Functions
def vendor_only(con, vendor_id):
    print('\nDatabase Reverse Device Search:')
    devices = reverse_device_search(con, vendor_id)
    vendor = search_vendor(con, vendor_id)
    print(f'\n{vendor.id} {vendor.name:100}')
    for device in devices:
        print(f'\t{device.id} {device.name}')


def device_only(con, device_id):
    print('\nDatabase Device Search:')
    devices = search_devices(con, device_id)
    for device in devices:
        vendor = search_vendor(con, device.vendor)
        if vendor:
            print(f'\n{vendor.id} {vendor.name}\n\t{device.id} {device.name}')
        else:
            print(f'\nUnknown Vendor\n\t{device.id} {device.name}')


def complete(con, vendor_id, device_id):
    print('\nDatabase Complete Search:')
    vendor, device = search_complete(con, vendor_id, device_id)
    print(f'\n{vendor.id} {vendor.name}\n\t{device.id} {device.name}')


def interactive_mode(con):
    """
    Enter interactive mode to perform searches.

    Args:
        con: A sqlite3 connection object.

    Returns:
        None
    """
    check_db(con)

    while True:
        vendor_id = input("\nEnter Vendor ID: ")
        device_id = input("Enter Device ID: ")

        if vendor_id and not device_id:
            try:
                vendor_only(con, vendor_id)
            except:
                print(f'\nVendor {vendor_id} not found!')

        if device_id and not vendor_id:
            try:
                device_only(con, device_id)
            except:
                print(f'\nDevice {device_id} not found!')

        if vendor_id and device_id:
            try:
                complete(con, vendor_id, device_id)
            except:
                print(f'\nVendor {vendor_id} and Device {device_id} not found!')

        if not vendor_id and not device_id:
            print('\nNo input provided!')

        prompt_continue()


def main(con):
    """
    Main function to run the program.

    Args:
        con: A sqlite3 connection object.

    Returns:
        None
    """
    try:
        parser = argparse.ArgumentParser(description='USB Lookup Tool')
        parser.add_argument('-u', action='store_true', 
                            help='Update the database with the latest vendor and device information. Usage: python usb-lookup.py -u')
        parser.add_argument('-v', metavar='vendor_id', 
                            help='Perform a reverse search in the database using a vendor id. '
                                'This will return the devices associated with the provided vendor. '
                                'Usage: python usb-lookup.py -v "Vendor ID"')
        parser.add_argument('-d', metavar='device_id', 
                            help='Search the database for a device using its ID. '
                                'This will return the name and vendor associated with the provided ID. '
                                'Usage: python usb-lookup.py -d "Device ID"')
        parser.add_argument('-c', nargs=2, metavar=('vendor_id', 'device_id'), 
                            help='Perform a complete search in the database using a vendor ID and device ID. '
                                'This will return the names associated with the provided IDs. '
                                'Usage: python usb-lookup.py -c "Vendor ID" "Device ID"')
        parser.add_argument('-i', action='store_true', 
                            help='Enter interactive mode. In this mode, the program will prompt you for input '
                                'and perform searches based on your responses. '
                                'Usage: python usb-lookup.py -i')
        args = parser.parse_args()

        if args.u:
            print('\nUpdating Database...')
            updated = ids.main(con)
            if updated:
                print('\nDatabase updated!')
            else:
                print('\nDatabase update failed!')
            return
        elif args.v:
            vendor_id= args.v
            vendor_only(con, vendor_id)
            return
        elif args.d:
            device_id = args.d
            device_only(con, device_id)
            return
        elif args.c:
            vendor_id, device_id = args.c
            complete(con, vendor_id, device_id)
            return
        elif args.i:
            interactive_mode(con)
        else:
            parser.print_help()
            return


    except KeyboardInterrupt:
        con.close()
        print('\n\nGoodbye!\n')
        sys.exit(0)
    except ValueError as ve:
        print(f'Invalid Input:\n{ve}')
    except Exception as e:
        print(f'An error occurred:\n{e}')


# Run program
if __name__ == "__main__":
    con = sql.connect(IDS_DB)
    check_db(con)
    clear_screen()
    main(con)
    con.close()
    print('')
