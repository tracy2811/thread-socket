#!/usr/bin/env python3

# following code is edited from https://gist.github.com/gordinmitya/349f4abdc6b16dc163fa39b55544fd34

import socket
import glob
import os
import re
from threading import Thread

clients = []

# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        # get filename
        fullname = self.sock.recv(1024).decode()

        # check for duplicates
        name, extension = os.path.splitext(fullname)
        names = glob.glob(name + '*' + extension)
        if len(names) >= 1:
            numbers = [int(s) for name in names for s in re.findall(r'\d+', os.path.splitext(name)[0])]
            number = max(numbers) if len(numbers) else 1
            fullname = name + '_copy' + str(number) + extension

        with open(fullname, 'wb') as fs:
            # send file name to client
            self.sock.send(fullname.encode())

            # write file
            while True:
                # try to read 1024 bytes from user
                # this is blocking call, thread will be paused here
                data = self.sock.recv(1024)
                if data:
                    fs.write(data)
                else:
                    # if we got no data – client has disconnected
                    fs.close()
                    print(self.name, 'saved', fullname)
                    self._close()
                    # finish the thread
                    return

def main():
    next_name = 1

    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reuse address; in OS address will be reserved after app closed for a while
    # so if we close and imidiatly start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen to all interfaces at 65432 port
    sock.bind(('', 65432))
    sock.listen()
    print('Listening on port 65432...')
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        # start new thread to deal with client
        ClientListener(name, con).start()


if __name__ == "__main__":
    main()
