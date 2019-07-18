from adafruit_servokit import ServoKit
import time
import picamera
import numpy as np
import cv2
import matplotlib.pyplot as plt
from shutil import copyfile


'''
CAMERA
This class points and controls the camera used on the robot.
'''
class Camera:

    def __init__(self, ServoController, pitchServo, yawServo):
        # The port number for each servo.
        self._pitch = pitchServo
        self._yaw = yawServo

        # default state for pitch and yaw.
        self._default = [65, 90]
        self._servos = ServoController

        self._camera = picamera.PiCamera()
        self._seed = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


    def setUp(self):

        self._servos.servo[self._pitch].actuation_range = 90
        self._servos.servo[self._pitch].angle = self._default[self._pitch]
        self._servos.servo[self._yaw].angle = self._default[self._yaw]
        self._camera.resolution = (640, 480)

    def returnDefault(self):

        self._servos.servo[self._pitch].angle = self._default[self._pitch]
        self._servos.servo[self._yaw].angle = self._default[self._yaw]

    def scanLeft(self):
        for i in range(180, 0, -5):
            self._servos.servo[self._yaw].angle = i
            self._camera.capture('%dpick_left.jpg' % i)

    def scanRight(self):
        for i in range(0, 180, 5):
            self._servos.servo[self._yaw].angle = i
            self._camera.capture('%dpick_right.jpg' % i)

    def takePick(self, fileName):
        self._camera.capture('%s.jpg' % fileName)

    def detectPerson(self):
        self._camera.capture('temp.jpg')
        image = cv2.imread('temp.jpg')
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces_rect = self._seed.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=5)
        return len(faces_rect)

    def setCam(self, pitch, yaw):
        self._servos.servo[self._pitch].angle = pitch
        self._servos.servo[self._yaw].angle = yaw

    def retreaveLastImage(self, name):
        copyfile('temp.jpg', '{}' .format(name))