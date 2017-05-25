""" Common logic for handling GPIO
"""
import signal
import RPi.GPIO as GPIO

class GPIOinputHandler(object):
    """ Wrapper class to manage GPIO input
    """

    def __init__(self, pin, callback, termination_handler=None):
        self.pin = pin
        self.callback = callback
        self.termination_handler = termination_handler
        self.state = {}

    def _signal_handling(self, signum, frame):
        print "Exiting... "+str(signum)+"/"+str(frame)
        if self.termination_handler:
            self.termination_handler()
        GPIO.cleanup()
        exit(0)

    def _event_callback(self, channel):
        print "Event received for channel "+str(channel)
        self.callback(self.state)

    def run(self):
        """ Start GPIO input handling and run till interrupt
            or termination signal is received
        """

        signal.signal(signal.SIGINT, self._signal_handling)
        signal.signal(signal.SIGTERM, self._signal_handling)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self._event_callback, bouncetime=500)

        # send initial state
        self.callback(self.state)

        while True:
            input('')

class GPIOoutputHandler(object):
    """ Wrapper class to manage GPIO output
    """
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def set_output(self, output):
        """ Set output on pin
        """
        GPIO.output(self.pin, output)

    def cleanup(self):
        """ Clean up on exit
        """
        GPIO.cleanup()


