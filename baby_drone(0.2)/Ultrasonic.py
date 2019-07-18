import RPi.GPIO as GPIO
import time

class utrasonic:
    
    def __init__(self, trigger, echo):

        self.TRIG = trigger
        self.ECHO = echo

    def setUp(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
        GPIO.output(self.TRIG, False)

    def findDistence(self):
    
        GPIO.output(self.TRIG, True)
        time.sleep(0.0001)
        GPIO.output(self.TRIG, False)

        start = 0
        end = 0

        while GPIO.input(self.ECHO) == 0:
            start = time.time()

        while GPIO.input(self.ECHO) == 1:
            end = time.time()

        sig_time = end-start

        #cm:
        distance = (sig_time*17150)
        return distance

