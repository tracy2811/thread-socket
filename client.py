#!/usr/bin/env python3

import socket
import sys
import os.path

BUFFER_SIZE = 1024

# check argv
if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'file domain-name|ip-address port-number')
        sys.exit(1)

filename, host, port = sys.argv[1:]

# check port
try:
        port = int(port)
except:
        print('port-number must be an integer')
        sys.exit(1)

# check if file exist
if not os.path.isfile(filename):
        print(filename, 'does not exist or is a directory')
        sys.exit(1)

# connect to server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        # send filename
        s.send(os.path.basename(filename).encode())

        # get saved name in server
        saved_name = s.recv(1024).decode()

        # send file
        with open(filename, 'rb') as fs:
                size = os.path.getsize(filename)
                _, columns = os.popen('stty size', 'r').read().split()
                columns = int(columns) if int(columns) > 10 else 94
                count = 0
                while True:
                        data = fs.read(BUFFER_SIZE)
                        if not data:
                            break

                        # send data
                        s.sendall(data)

                        # print progress
                        count += 1
                        progress = count*BUFFER_SIZE/size
                        fill_length = round(progress * (columns - 10))
                        space_length = columns - 10 - fill_length
                        if progress < 1:
                                print('%s>%s %3d%%' % ('='*fill_length, ' '*space_length, round(progress*100)), end='\r')
                        else:
                                print('%s  100%%' % ('='*(columns - 10)))
                                break
                fs.close()

        print('Uploaded', filename, 'as', repr(saved_name))
