""" Common logic for handling GPIO
"""

import logging
import signal
import time
import RPi.GPIO as GPIO
from constants import LOGGING_FORMAT, LOGGING_LEVEL

logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)

class GPIOinputHandler(object):
    """ Wrapper class to manage GPIO input
    """

    LOGGER = logging.getLogger('gpio_input_handler')

    def __init__(self, pin, callback, termination_handler=None):
        self.pin = pin
        self.callback = callback
        self.termination_handler = termination_handler
        self.state = {}

    def _end_program(self, signum, frame):
        GPIOinputHandler.LOGGER.debug("Received termination signal %i", signum)
        self._exit_program(0)

    def _exit_program(self, exit_code):
        if exit_code != 0:
            GPIOinputHandler.LOGGER.error("Exiting with error code %d", exit_code)
        else:
            GPIOinputHandler.LOGGER.info("Exiting normally")

        if self.termination_handler:
            self.termination_handler()

        GPIO.cleanup()

        GPIOinputHandler.LOGGER.info("Done")
        exit(exit_code)

    def _event_callback(self, channel):
        GPIOinputHandler.LOGGER.debug("GPIO input event received for channel %d", channel)
        self.callback(self.state)

    def run(self):
        """ Start GPIO input handling and run till interrupt
            or termination signal is received
        """

        signal.signal(signal.SIGINT, self._end_program)
        signal.signal(signal.SIGTERM, self._end_program)

        try:
            GPIOinputHandler.LOGGER.debug("Setting up input GPIO")
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            GPIOinputHandler.LOGGER.debug("Add event detect for input GPIO")
            GPIO.add_event_detect(self.pin, GPIO.FALLING, \
                              callback=self._event_callback, bouncetime=500)

            GPIOinputHandler.LOGGER.debug("Initialize state")
            # send initial state
            self.callback(self.state)

            GPIOinputHandler.LOGGER.debug("Start waiting for GPIO input events")
            while True:
                time.sleep(1e6)

        except Exception:
            GPIOinputHandler.LOGGER.error("Exception occurred", exc_info=True)
            self._exit_program(1)

class GPIOoutputHandler(object):
    """ Wrapper class to manage GPIO output
    """

    LOGGER = logging.getLogger('gpio_output_handler')

    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def set_output(self, output):
        """ Set output on pin
        """
        GPIOoutputHandler.LOGGER.debug("Set GPIO output to %s", output)
        GPIO.output(self.pin, output)

    def cleanup(self):
        """ Clean up on exit
        """
        GPIOoutputHandler.LOGGER.debug("Cleaning up output GPIO")
        GPIO.cleanup()


