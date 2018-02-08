#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Connect arduino through a serial port and allow communication with TCP.

Implement a TCP socket server communicating with an arduio through serial
communication.
"""
# -------------------------------------------------------
# Module Name : socket server
# Version : 1.0.0
#
# Software Name : SerialCom
# Version : 1.0
#
# Copyright (c) 2015 Zorglub42
# This software is distributed under the Apache 2 license
# <http://www.apache.org/licenses/LICENSE-2.0.html>
#
# -------------------------------------------------------
# File Name   : /usr/local/bin/arduino_controller.py
#
# Created     : 2015-12
# Authors     : Zorglub42 <contact(at)zorglub42.fr>
#
# Description :
#     Connect arduino through a serial port and allow communication
#     with it from a TCP socket
# -------------------------------------------------------
# History     :
# 1.0.0 - 2015-12-03 : Release of the file
# 1.0.1 - 2018-01-18 : pep8/flake8

import logging
import logging.config
import os.path
import sys
import select
import socket
import time
import threading

import serial


def socket_receive(client_socket):
    """Get data from socket.

    socket.recv function overloading
    We are using here the recv exception mecanism to determine if there is
    some data to read

    @param socket Socket to read
    @return Data send by client
    """
    buf = ""  # Buffer to store data
    _has_data = True  # Is there some data to read?
    while _has_data:
        # Use socket as non blocking
        client_socket.setblocking(0)
        try:
            _data = client_socket.recv(256)
            if _data:
                buf += _data
            else:
                _has_data = False
        except Exception:  # pylint: disable=broad-except
            _has_data = False
    return buf


class Server(object):  # pylint: disable=too-many-instance-attributes
    """TCP gateway to arduino via serial connection."""

    # pylint: disable=too-many-arguments
    def __init__(self, address='', port=9999, listen=5,
                 device='/dev/ttyACM0', baud=9600):
        """Create Server class instance.

        @param port Listeing port
        @param listen Waiting connection queue size
        @param device Port serial port to communicate with the arduino
        @param baud Serial baud rate
        """
        self.sockets = []    # Connected clients socket list

        self.device = device
        self.baud = baud
        self.address = address
        self.port = port
        self.listen = listen

        # Creating server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Use socket as non blocking
        self.socket.setblocking(0)

        # Creating Semaphore to protect arduino access
        self.arduino = threading.BoundedSemaphore(1)

        self.logger = logging.getLogger(self.__class__.__name__)

    def send_to_clients(self, data, cur_client=False):
        """Send data to connected clients."""
        try:
            _, write, _ = select.select(self.sockets, self.sockets, [])

            for sock in write:
                if sock != self.socket and data and sock != cur_client:
                    sock.send(data)
        except select.error:
            return
        except socket.error:
            return

    def wait_for_response(self, sock, ser, clear_line):
        """Drop arduino data until response marker."""
        serial_line = ser.readline()
        clear_line = serial_line.replace("\n", "").replace("\r", "")
        while clear_line != "***START***":
            self.send_to_clients(serial_line, sock)
            self.logger.debug("ARDUINO.flushing: >%s<", clear_line)
            serial_line = ser.readline()
            clear_line = serial_line.replace("\n",
                                             "").replace("\r", "")
        return clear_line

    def manage_client_request(self, sock, ser):
        """Manage requests from TCP client."""
        try:
            data = socket_receive(sock).replace("\n", "").replace("\r", "")
            if data:

                self.logger.debug("Locking arduino")

                # Locking arduino
                self.arduino.acquire()
                self.logger.debug("TCP-CLIENT.send: %s", data)

                ser.write(data + "\n")
                ser.flush()

                # Hopefully, wait for an answer in the next comming lines.....
                clear_line = ""
                clear_line = self.wait_for_response(sock, ser, clear_line)

                # clear_line contains begin of answer marker
                # read the first line of the answer
                serial_line = ser.readline()
                clear_line = serial_line.replace("\n",
                                                 "").replace("\r", "")
                while clear_line != "***DONE***":
                    # Data send bny arduino is not the end of request
                    # marker: send data to client
                    if clear_line != '':
                        self.logger.debug("ARDUINO.answer: >%s<", clear_line)
                        sock.send(serial_line)
                    serial_line = ser.readline()
                    clear_line = serial_line.replace("\n",
                                                     "").replace("\r", "")

                self.logger.info("End connection")
                # Unlocking arduino
                self.logger.debug("Unlocking arduino")
                self.arduino.release()

            sock.close()
            # Remove client socket from the list of connected clients
            self.sockets.remove(sock)
            self.logger.debug("TCP-CLIENT.disconnect: ")

        except socket.error:
            self.logger.exception("socket error")
            self.sockets.remove(sock)
            self.arduino.release()

    def open_serial(self):
        """Open serial (ensure it's here)."""
        ser = None
        ser_was_not_here = False
        while not ser:
            self.logger.debug("Trying to open serial port %s", self.device)
            try:
                ser = serial.Serial(self.device, self.baud, timeout=0.1)
                if ser_was_not_here:
                    # Workaround to give time to USB/Serial to come up
                    # With arduino.org it's longer than arduino.cc
                    self.logger.debug(
                        "Serial device found, waiting to come up")
                    time.sleep(30)
                    ser.close()
                    self.logger.debug("Re-opening device")
                    ser = serial.Serial(self.device, self.baud, timeout=0.1)

            except serial.SerialException as exc:
                if exc.errno == 2:  # No such file or directory
                    self.logger.error(
                        "Device %s does not exists.... waiting....",
                        self.device)
                    ser_was_not_here = True
                    time.sleep(1)
                else:
                    raise exc
        self.logger.info("Serial port %s opened", self.device)
        return ser

    def run(self):
        """Run server.

        Main code for server implem.
        """
        # Open connection to the Serial device
        ser = self.open_serial()
        # Bind socket to listening port
        self.socket.bind((self.address, self.port))
        # Start listeing with the proper Q size
        self.socket.listen(self.listen)
        self.logger.debug("Sock server started")

        # Add server socket to socket list
        self.sockets.append(self.socket)
        # Let's go for ever
        while True:
            # Let's check for new connections
            try:
                read_ready, _, _ = select.select(self.sockets,
                                                 self.sockets, [])
            except select.error:
                self.logger.exception("SELECT error")
                break
            except socket.error:
                self.logger.exception("SOCKET error")
                break

            if self.socket in read_ready:
                # Server socket have received some data: new client
                # connection
                client, address = self.socket.accept()
                self.logger.info("TCP-CLIENT.connect: %s", address[0])
                # On ajoute le socket client dans la liste des sockets
                self.sockets.append(client)

            # Let's check if some clients are sending request
            try:
                read_ready, _, _ = select.select(self.sockets,
                                                 self.sockets, [])
            except select.error:
                self.logger.exception("SELECT error")
                break
            except socket.error:
                self.logger.exception("SOCKET error")
                break

            for sock in read_ready:
                if sock != self.socket:
                    self.manage_client_request(sock, ser)

            # At least,
            # Forward data comming from serial device to connected clients
            # still connected
            data = ser.readline()
            while data:
                self.send_to_clients(data)
                data = ser.readline()


def usage():
    """Display usage and exit."""
    print "usage: " + sys.argv[0] + \
        " [-a ADDRESS]" + \
        " [-p PORT]" + \
        " [-d DEVICE]" + \
        " [-b BAUD-RATE]" + \
        " [-v]" + \
        " [-h]"
    print "\t-a: listening address. default=" + ADDRESS + " *=all"
    print "\t-p: listeing port default=" + str(PORT)
    print "\t-d: serial device default=" + DEVICE
    print "\t-b: serial device baudrate default=" + str(BAUD_RATE)
    print "\t-v: vebose mode (note: this paramter is overloaded by " + \
        "/etc/arduino_controller/logs.conf when exists)"
    print "\t-h: this text"
    sys.exit(1)


# Default values
QUEUE_SIZE = 5

PORT = 9999
DEVICE = '/dev/ttyACM0'
BAUD_RATE = 9600
ADDRESS = 'localhost'


def start_server():
    """Start server."""
    # pylint: disable=global-statement
    log_level = logging.INFO
    global PORT, DEVICE, BAUD_RATE, ADDRESS
    # Parse command line parameters
    for i, arg in enumerate(sys.argv):
        if arg == '-p':
            PORT = int(sys.argv[i+1])
        elif arg == '-d':
            DEVICE = sys.argv[i+1]
        elif arg == '-b':
            BAUD_RATE = int(sys.argv[i+1])
        elif arg == '-v':
            log_level = logging.DEBUG
        elif arg == '-a':
            ADDRESS = sys.argv[i+1]
            if ADDRESS == "*":
                ADDRESS = ""
        elif arg == '-h':
            usage()

    if os.path.isfile("/etc/arduino_controller/logs.conf"):
        logging.config.fileConfig("/etc/arduino_controller/logs.conf")
        if log_level != logging.INFO:
            logging.warning("-v paramter may be oveloaded by"
                            "/etc/arduino_controller/logs.conf configuration")
    else:
        logging.basicConfig(level=log_level)

    logging.info("Socks arduino server starting:")
    logging.info("    Device=%s", DEVICE)
    logging.info("    Baud=%d", BAUD_RATE)
    logging.info("    Listeing=%s", ADDRESS)
    logging.info("    TCP Port=%d", PORT)

    server = Server(ADDRESS, PORT, QUEUE_SIZE, DEVICE, BAUD_RATE)
    server.run()


if __name__ == "__main__":
    start_server()
