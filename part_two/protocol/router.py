import socket

from . import constants


class Router:
    """
    Sets the current node as a router (i.e. forwards packets from/to s and d).

    Should only be run on nodes r1, r2 and r3.

    s -> r1 -> d(10001), i.e. any packet sent from s to r1 will be forwarded to d,
    on port 10001.
    """
    def __init__(self):
        if not constants.IS_ROUTER:
            raise Exception("Router() should only be run on a router node")

        self.source_host = socket.gethostbyname(constants.SOURCE)
        self.source_address = self.source_host, 10000
        self.destination_host = socket.gethostbyname(constants.DESTINATION)
        self.destination_address = self.destination_host, 10004
        self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.forwarding_port = constants.BASE_PORT + constants.OWN_SENDER_ID

    def run(self):
        self.sock_in.bind(('', constants.BASE_PORT + constants.OWN_SENDER_ID))

        while True:
            data_in, client_address = self.sock_in.recvfrom(constants.UDP_BUFFER_SIZE)

            client_host, client_port = client_address

            if client_host == self.source_host:
                forwarding_address = self.destination_address
            elif client_host == self.destination_host:
                forwarding_address = self.source_address
            else:
                raise Exception("Router cannot receive packets from other nodes")

            print(f"from: {client_address}, to: {forwarding_address}, data: {len(data_in)} bytes")
            self.sock_out.sendto(data_in, forwarding_address)
