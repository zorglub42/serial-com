# This sample demonstrator how to establish a direct link from your python
# program to the arduino without using a scoket server

# While arduino_controller is not yet a regular pipy lib,
# ensure arduibo_controller.py from sock_server/usr/local/bin is in PYTHONPATH
# or copy it in your project

import logging
import time
from arduino_controller import ArduinoLink


class MyController(ArduinoLink):
    """Implementation of abstract class ArduinoLink for demo purpose."""

    def on_message_received(self, message):
        self.logger.info("Message received: %s", message)


def main():
    """Main program."""
    logging.basicConfig(level=logging.DEBUG)
    ard = MyController("/dev/ttyACM0", 9600)

    ard.start()
    while not ard.running:
        time.sleep(0.01)
    logging.info(ard.send_request("V"))
    try:
        ard.join()
    except KeyboardInterrupt:
        ard.stop()


if __name__ == "__main__":
    main()