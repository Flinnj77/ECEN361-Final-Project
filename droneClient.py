###########################################
#  Beatrice Client Drone program
#
#  Author: Cordelia RW Wilson
#
#  A bot client that connects to Madame server
#  and sends images of people
#
# THIS CODE COMPILES, BUT DOES NOT PERFORM AS EXPECTED
#
###########################################
# Protocol Codes:
#    Madame:
#       010 --
#       020 -- ready for next interaction
#       030 -- transmission temporarily unavailable
#       040 -- start transmitting data
#       050 -- finished sending data
#       060 --
#       070 -- there was an error, redo last interaction
#       075 -- the file transfer was successful
#       080 -- bots shut down, mother shutting down now
#       090 -- shutdown and exit
#       099 -- both bots have shut down
#    Drone:
#        *  -- name of drone sending information
#       100
#       110
#       120 -- confirm send command && something to send
#       130 -- confirm send command && nothing to send
#       140 -- done sending person && image files
#       150 -- ready to receive drive file
#       160 --
#       170 -- there was an error, resend last transmission
#       175 -- the file transfer was successful
#       180 --
#       190 -- confirm shutdown command
#    Human:
#       200 --
#       210 --
#       220 -- something to send
#       230 -- nothing to send
#       240 -- request location && image list
#       250 -- sending drive file
#       260 -- done sending data
#       270 --
#       280 --
#       290 -- shutdown and exit
#################################################
# import sys
# import io
import socket
# from path_lib import Path
import time
from typing import List, Any

# import ECEN_361
import person as Person
import position
# import threading
# import self as self

print('Hello World!')

# Connects to alternate IP addresses for testing
HOST_local = 'CORD-BASESTATION'  # 192.162.0.101
HOST_MMM = '192.168.0.100'
PORT = 5555

people = []
front_of_q = 0

droneName = b"Beatrice"
imageFile1 = "Sample-1mb.png"
imageFile2 = "Sample-200kb.png"


def main():
    # Run socket monitor on one thread
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall(droneName)
        while True:
            data = sock.recv(3)
            if data == b'020':  # command to send a Person object amd image
                sock.send(b'120')  # send ACK code
                if people:
                    print(people[front_of_q].image.get_size())
                    next_person = str(people[front_of_q].xPosition) + " " \
                                    + str(people[front_of_q].yPosition) + " " \
                                    + people[front_of_q].image + " " \
                                    + people[front_of_q].image.get_size()
                    sock.send(bytes(next_person, "utf8"))  # send Person object
                    if front_of_q < people.__len__() - 1:
                        front_of_q += 1
                    else:
                        front_of_q = 0
                    # send image in a loop
                    with open(imageFile1) as img:
                        line = img.read(1024)
                        while line:
                            sock.send(bytes(line, "utf8"))
                            line = img.read(1024)
                        pass
                    sock.send(b'140')  # send done code
                    pass
            if data == b'090':  # command to close connection and shutdown
                sock.send(b'190')  # confirmation of command
                data = sock.recv(4)
                while True:
                    if data == b'075':
                        sock.close()
                        exit(1)
                    sock.send(b'190')
                    data = sock.recv(4)
            if data == b'030':  # command to stop transmitting
                # return to while loop waiting for command to transmit
                pass

            # print(repr(data))
            # sock.send(b'Hello ' + bytes(str(count), "utf8"))
            # count += 1
            # time.sleep(2)


main()
