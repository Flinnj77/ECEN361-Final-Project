###########################################
#  Mad Madame Mim Server Drone program
#
#  Author: Cordelia RW Wilson
#
#  A server that accepts up to three of any
#  combination of human clients and bot clients.
#
#  THIS CODE COMPILES, BUT DOES NOT PERFORM AS EXPECTED
#
# ##########################################
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
import sys
import io
import socket
from pathlib import Path
from typing import List, Any

import person as Person
import position
import threading
import _thread
print('Hello Babies!')

# Testing required multiple IP addresses
HOST_MMM = '192.168.0.100'
HOST_local = 'CORD-BASESTATION'  # 192.162.0.101
PORT = 5555
server_port = int(sys.argv[1]) if len(sys.argv) == 2 else PORT

# critical variables
# # # # sem_People # # # #
people = []
image_list = []

# # # # sem_DriveFile # # # #
drive_name_list: List[str] = []

# # # # sem_Shutdown # # # #
shutdown = [False, False, False]

# # Semaphores # #
sem_people = threading.Semaphore()
sem_drivefile = threading.Semaphore()
sem_shutdown = threading.Semaphore()


def human_connection(connection, name):
    sem_shutdown.release()
    global people
    global image_list
    global drive_name_list
    global shutdown
    connection.send(b'020')
    while True:
        sem_shutdown.acquire()
        if shutdown[0]:
            sem_shutdown.release()
            while True:
                if shutdown[1] and shutdown[2]:
                    connection.send(b'099')
                    connection.close()
                    exit(1)
        data = connection.recv(3)
        if data == b'220':  # human has something to send or receive
            connection.send(b'040')
            connection.recv(4)
            if data == b'250':  # human will send drive file
                connection.send(b'040')
                drivefile_name = connection.recv(1024)
                with open(drivefile_name, 'w+') as f:
                    line = connection.recv(1024)
                    while line:
                        f.write(line)
                        line = connection.recv(1024)
            elif data == b'240':  # human requests location/image files
                sem_people.acquire()
                # ATERNATE: create local copy, send that, but delete both global and temp each iteration?
                for pos, img in (people, image_list):
                    location = str(pos.x) + str(pos.y) + pos.faces
                    connection.send(location)
                    with open(pos.faces, 'w+') as f:
                        line = f.read(1024)
                        while line:
                            connection.send(line)
                            line = f.read(1024)
                    # sem_people.acquire()
                    people.remove(pos)  # Once sent to human, remove from list
                    image_list.remove(img)
                    # sem_people.release()
                sem_people.release()
                connection.send(b'050')  # done sending data
        elif data == b'290':  # close all connections and shutdown
            sem_shutdown.acquire()
            shutdown[0] = True
            sem_shutdown.release()
        elif data == b'230':  # human has nothing to send
            pass  # check again at next loop
        else:
            print("Impossible state reached")
            return

        pass


def display(peep):
    print('x-position: %\n', peep.x)
    print('y-position: %\n', peep.y)
    print('Image file Name: %\n', peep.faces)


def baby_connection(connection, name):
    sem_shutdown.release()
    if name == b'Beatrice':
        num = 2
    else:
        num = 1

    while True:  # loop here forever until closed by outside force
        # check if shutdown command received
        sem_shutdown.acquire()
        if shutdown[0]:
            sem_shutdown.release()
            connection.send(b'090')
            while not shutdown[num]:
                data = connection.recv(4)
                if data == b'190':
                    shutdown[num] = True
                    connection.send(b'075')
        # proceed to protocol logic
        else:
            connection.send(b'020')  # ready to work with bot
            data = connection.recv(4)
            if data == b'120':  # incoming transmission of person and image
                connection.send(b'040')  # send person instance
                data = connection.recv(1024)
                # people.append(data)  # add new person to list of people
                tokens = " ".split(str(data))
                # xpos = tokens[0]
                # ypos = tokens[1]
                filename = tokens[2]  # the filename as it exists in the baby-drones files
                print(filename)
                temp_peep = Person
                temp_peep.x = int(tokens[0])
                temp_peep.y = int(tokens[1])
                temp_peep.faces = tokens[2]
                display(temp_peep)

                # image_name = temp_peep.faces  # ...Why can't you find the face?
                with open(filename, 'w+') as img:
                    # uploading the image file
                    data = connection.recv(1024)
                    while data:
                        img.write(str(data))
                        data = connection.recv(1024)

                # assert temp_peep is a person object
                # assert img is a image file

                # # # # Critical Section  # hold off until the image has been successfully downloaded as well
                sem_people.acquire()
                people.append(temp_peep)
                image_list.append(str(img))
                sem_people.release()
                # # # # Critical Section end

                with open(filename + ".png", 'w+') as img:
                    data = connection.recv(1024)
                    while data:
                        img.write(str(data))
                        data = connection.recv(1024)
            elif data == b'130':  # bot has nothing to send
                pass
            # elif data == b'140':  # wait for permission to transmit
            #     # test that person/image pair works
            #     pass
            # elif data == b'190':  # return to main() and close connection
            #     break
            else:
                print("Impossible state reached")
                return
    return


def main():
    client_list = []
    # Establish server for babies and human to connect to
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST_MMM, server_port))
        sock.listen(3)  # One for the human, one for each baby
        while True:
            conn, addr = sock.accept()
            sem_shutdown.acquire()
            client_list.append((conn, addr))  # A list of all the connections

            drone_name = conn.recv(1024)
            print(drone_name)

            if drone_name == b'Beatrice' or drone_name == b'KillDeer':
                function_name = baby_connection
            else:
                function_name = human_connection

            thread_arg = {}
            thread_arg["connection"] = (conn, addr)
            thread_arg["name"] = drone_name

            xthread = threading.Thread(target=function_name, name=str(drone_name), kwargs=thread_arg)
            xthread.start()
            # if connection returns, leave 'with' and close it.
            xthread.join()  # wait for threads to connect before exiting


main()
