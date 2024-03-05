    # USB Lookup

    USB Lookup is a Python application that allows you to search for USB vendors and devices using their IDs. The application uses a SQLite database to store the USB IDs data, which is fetched from the Linux USB ID Repository.

    ## Files

    The application consists of two main Python files:

    - `usb-lookup.py`: This file contains the main functionality of the application, including functions for searching for vendors and devices, updating the database, and handling user input.

    - `ids.py`: This file contains functions for fetching the USB IDs data from the server, parsing the data, formatting the data, and updating the database. It also contains the Vendor and Device classes, which represent a vendor and a device, respectively.

    ## Usage

    To use the application, you can run the `usb-lookup.py` script. The script will prompt you to enter a vendor ID and/or a device ID, and it will display the corresponding vendor and device information.

    ## Installation

    To install the application, you can clone the GitHub repository and run the `usb-lookup.py` script.

    ## Dependencies

    The application requires the following Python packages:

    - `requests`: For fetching the USB IDs data from the server.
    - `pandas`: For parsing and formatting the USB IDs data.
    - `sqlite3`: For interacting with the SQLite database.

    ## Contributing

    Contributions are welcome! Please feel free to submit a pull request.

    ## License

    This project is licensed under the terms of the MIT license.
