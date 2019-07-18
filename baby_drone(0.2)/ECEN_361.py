import RPi.GPIO as GPIO
from drivecontrol import DriveControl
from Ultrasonic import utrasonic
from Cammra import Camera
from adafruit_servokit import ServoKit
from position import Position
from person import Person
import math
import time


droneName = "KillDear"  # The name of the drone for referencing.
personNum = 0           # Number of images of people in them.

facing = 0              # The direction the drone is face starting at origin.
location = Position()   # Where the drones is current at starting at origin.

taskList = []

servos = ServoKit(channels=16)      # Servo controller for all objects that us servos
drive = DriveControl(servos, 2, 3)  # The drive system.
sonic = utrasonic(4, 17)            # The ultrasonic sensors controller.
cam = Camera(servos, 0, 1)          # The camera systems.

# Set up various systems.
sonic.setUp()
cam.setUp()

# List of people.
people = []


'''
CONTROLLER
This function controls the various tasks of the drone.
'''
def controller():
    global taskList
    run = 'n'
    duration = 0
    try:
        while(run != 'S'):
            # do nothing
            if (run == 'n'):
                drive.stop()

            # preform a scan.
            elif (run == 's'):
                scanArea()

            # move a specified amount
            elif (run == 'm'):
                move(duration)

            # turn a specified amount
            elif (run == 't'):
                turn(duration)

            elif (run == 'p'):
                drive.stop()

            # looks at the list of tasks.
            if (len(taskList) > 0):
                task = taskList.pop(0)
                split_task = task.split(" ")
                run = split_task[0]
                duration = float(split_task[1])

            else:
                with open('temp.txt', 'r+') as commends:
                    for line in commends:
                        taskList.append(line)

                    commends.truncate()

                with open('temp.txt', 'w') as clear:
                    clear = []

    except KeyboardInterrupt:
        print("ending task")
        drive.stop()
        cam.returnDefault()
        GPIO.cleanup()

'''
TIME STOP 
This function checks if the right amount of time has pass and 
stops the drone once time is up.
'''
def timedStop(startTime, runTime):

    # Checks if the time elapse is greater then the desired run time.
    if runTime <= (time.time() - startTime):
        drive.stop()
        return False

    else:
        return True


'''
SCAN AREA
Scans the area for people and stores if images and location of eny 
people found.
'''
def scanArea():
    global droneName
    global personNum
    global people
    faces = 0
    yaw = cam._default[0]

    # scan left at the up angel of zero.
    for pitch in range(180, 0, -20):
        cam.setCam(yaw, pitch)
        # Scans image for people.
        numFaces = cam.detectPerson()
        faces = faces + cam.detectPerson()

        # If a person is found an image is stored and location is noted.
        if numFaces > 0:
            name = ("tempImages/{}_{}.jpg" .format(droneName, personNum))
            personNum += 1
            cam.retreaveLastImage(name)
            # Add the person object to the list of people found.
            people.append(Person(location.x, location.y, name))

    # move yaw 10 degrease up
    yaw = yaw - 10

    # scan right at the up angel of 10 degrees.
    for pitch in range(0, 180, 20):
        cam.setCam(yaw, pitch)
        # Scans image for people.
        numFaces = cam.detectPerson()
        faces = faces + cam.detectPerson()

        # If a person is found an image is stored and location is noted.
        if numFaces > 0:
            name = ("tempImages/{}_{}.jpg".format(droneName, personNum))
            personNum += 1
            cam.retreaveLastImage(name)
            # Add the person object to the list of people found.
            people.append(Person(location.x, location.y, name))

    # move yaw 10 degrease up
    yaw = yaw - 10

    # scan left at the up angel of 20 degrees.
    for pitch in range(180, 0, -20):
        cam.setCam(yaw, pitch)
        # Scans image for people.
        numFaces = cam.detectPerson()
        faces = faces + cam.detectPerson()

        # If a person is found an image is stored and location is noted.
        if numFaces > 0:
            name = ("tempImages/{}_{}.jpg".format(droneName, personNum))
            personNum += 1
            cam.retreaveLastImage(name)
            # Add the person object to the list of people found.
            people.append(Person(location.x, location.y, name))

    # return camera to the default position.
    cam.returnDefault()

    # used for debugging.
    print("There are {} faces".format(faces))


'''
TURN
This turns the drone a specific amount 1 = pi/2 or 90 degrees and -1 = -pi/2.
'''
def turn(amount):
    global facing
    turnTime = 0.3 * abs(amount)  # The time need to turn pi/2
    startTime = 0
    endTurn = True

    # values grater then 0 turns the drone left.
    if amount > 0:
        startTime = time.time()
        drive.turnLeft()

    # values less then 0 turns the drone right.
    elif amount < 0:
        startTime = time.time()
        drive.turnRight()

    # values equal to 0 the drone does nothing.
    else:
        drive.stop()
        endTurn = False

    endTurn = timedStop(startTime, turnTime)

    # converts the input amount to radiance.
    angle = amount * math.pi * 0.5
    facing += angle  # add to the duration the drone is facing

    endTurn = timedStop(startTime, turnTime)

    # keeps the face angle to 0 to 2pi.
    facing = facing % (2*math.pi)

    endTurn = timedStop(startTime, turnTime)

    # will go until times up
    while endTurn:
        endTurn = timedStop(startTime, turnTime)


'''
MOVE 
Movies a specific a mount and stop if to close.
'''
def move(amount):
    global facing
    driveTime = 0
    startTime = 0
    endDrive = True

    # if the amount is greater then 0 go foreword
    if amount > 0:
        driveTime = amount * 4.55 # the time needed to go one meter
        startTime = time.time()
        drive.foreword()
        location.movePosition(facing, amount)

        # will move foreword  for a specific amount of time over stop before
        # colliding into objects.
        while endDrive:
            endDrive = timedStop(startTime, driveTime)
            distenc = sonic.findDistence()

            # If the distance is less 15 cm then the drone stops and returns
            # the remaining distance
            if distenc < 15:
                drive.stop()
                traviled = (driveTime - (time.time() - startTime)) * 0.22
                location.movePosition(facing, amount - traviled)
                return traviled

            endDrive = timedStop(startTime, driveTime)
            time.sleep(0.1)  # this is need for the functionality of the ultra sonic.

    # if the amount is less then 0 go backwards
    elif amount < 0:
        driveTime = abs(amount) * 4.26 # time need to go backwards 1 meter.
        startTime = time.time()
        drive.reverse()
        location.movePosition(facing, amount)

        # run till times up.
        while endDrive:
            endDrive = timedStop(startTime, driveTime)

    # if amount = 0 then stop.
    else:
        drive.stop

    location.movePosition(facing, amount)
    return 0
'''
holdTime = 0
test = 's'
while(test != 'q'):
    if(test == 'f'):
        drive.foreword()

    elif(test == 'b'):
        drive.reverse()

    elif(test == 'r'):
        drive.turnRight()

    elif(test == 'l'):
        drive.turnLeft()

    elif(test == 's'):
        drive.stop()

    else:
        print('what')

    time.sleep(float(holdTime))
    drive.stop()

    test = input("please put in a test value: ")
    holdTime = input("how long;")
'''
'''
try:
    while(True):
        distenc = sonic.findDistence()
        print("cm = {}".format(distenc))
        if(distenc < 10.0):
            drive.reverse()

        elif(distenc < 20.0):
            drive.stop()

        else:
            drive.foreword()
        time.sleep(0.1)

            
except KeyboardInterrupt:
    print("ending task")
    drive.stop()
    GPIO.cleanup()
'''



'''
cam.scanLeft()
cam.scanRight()
cam.returnDefault()
'''

'''
d = 'n'
while(d == 'n'):
    pitch = int(input("pitch: "))
    yaw = int(input("yaw: "))
    cam.setCam(yaw, pitch)
    faces = cam.detectPerson()
    print("There are {} faces" .format(faces))
    d = input('Done(y/n): ')
'''

controller()


