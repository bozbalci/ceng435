"""
November 21st, 2019

CENG435 - Data Comms. and Networking
Term Project - Part One: UDP Based Socket Application, Delay Measurements, Topology, etc.

Authors:
    Narmin Aliyeva - 2177269
    Berk Ozbalci - 2171791
"""

from datetime import datetime
import socket
import struct
import threading
from time import sleep

# The number of messages to send before calculating RTT averages. The higher the number, the more
# accurate the result will be.
MESSAGE_COUNT = 1000

# UDP buffer size used in sockets.
BUFFER_SIZE = 4096

# The host to bind the socket onto.
BIND_ADDRESS = '0.0.0.0'

# The base port for servers. The range of ports [BASE_PORT, BASE_PORT + len(SENDER_IDS)] will be
# used in order to run the experiments across all nodes.
BASE_PORT = 10000

# The number in seconds to wait until sending a message to the server. Setting this to a number
# higher than the link delay helps reduce the number of excess packets sent. Setting this too low
# may cause flooding of UDP buffers, which may result in more packets getting lost.
CLIENT_SLEEP_INTERVAL = 1e-2

# The output filename format. Hostname is the neighboring hostname, extension is the file
# extension.
OUTPUT_FILENAME_FORMAT = 'link_costs_{hostname}.{extension}'

# Mapping of host names to integer indexes. Used for generating port numbers, identifying message
# sources and destinations, etc.
SENDER_IDS = {
    's': 0,
    'r1': 1,
    'r2': 2,
    'r3': 3,
    'd': 4,
}

# Adjacency list of all nodes within the network.
ALL_NEIGHBORS = {
    's': ('r1', 'r2', 'r3'),
    'r1': ('s', 'r2', 'd'),
    'r2': ('s', 'r1', 'r3', 'd'),
    'r3': ('s', 'r2', 'd'),
    'd': ('r1', 'r2', 'r3'),
}


def get_current_hostname() -> str:
    """
    Returns one of ('s', 'r1', 'r2', 'r3', 'd') depending on which machine this script is ran on.
    """
    hostname = socket.gethostname()
    ident = hostname.split('.')[0]

    if ident not in SENDER_IDS:  # for some reason, d's hostname is "pcvm5-24" instead of "d"
        ident = 'd'

    return ident


def get_now_timestamp() -> float:
    """
    Returns the current timestamp in seconds.
    """
    return datetime.now().timestamp()


HOSTNAME = get_current_hostname()
OWN_NEIGHBORS = ALL_NEIGHBORS[HOSTNAME]
OWN_SENDER_ID = SENDER_IDS[HOSTNAME]


class Message:
    """
    Represents the messages transferred over UDP sockets. Can be converted to and from binary.

    Structure:
        int sender_id: The sender ID of the source node.
        int index: An unique number representing the sequence order of the message.
    """
    structure = '!ii'  # struct packing format, '!' indicates network byte-order

    def __init__(self, sender_id: int, index: int) -> None:
        self.sender_id = sender_id
        self.index = index

    @classmethod
    def from_binary(cls, binary: bytes) -> 'Message':
        sender_id, message_index = struct.unpack(cls.structure, binary)
        return cls(sender_id, message_index)

    def to_binary(self) -> bytes:
        return struct.pack(self.structure, self.sender_id, self.index)


class MessagingPair:
    """
    Manages the server/client pair that is used for measuring RTT (round trip time) between
    two nodes.
    """
    def __init__(self, neighbor_hostname: str) -> None:
        self.neighbor_hostname = neighbor_hostname

        # First, calculate the neighbor server address. Each neighbor listens to another
        # neighbor from port: (BASE_PORT + NEIGHBOR_SENDER_ID). For example, if BASE_PORT
        # is 10000, every server listening to packets from the host r2 (sender_id: 2) will
        # be listening on port 10002.
        neighbor_host = socket.gethostbyname(neighbor_hostname)
        neighbor_port = BASE_PORT + OWN_SENDER_ID
        self.neighbor_address = neighbor_host, neighbor_port

        # We will listen to packets from sender N on port (BASE_PORT + N).
        self.neighbor_sender_id = SENDER_IDS[neighbor_hostname]
        self.own_port = BASE_PORT + self.neighbor_sender_id

        # Initialize packet histories. Both dictionaries map indexes to timestamps.
        self.packets_sent = dict()
        self.packets_received = dict()

        # e.g. for neighbor r2, this will be "link_costs_r2.txt"
        self.output_filename = OUTPUT_FILENAME_FORMAT.format(hostname=self.neighbor_hostname,
                                                             extension='txt')

        # Initialize threads.
        self.client_thread = threading.Thread(target=self.client)
        self.server_thread = threading.Thread(target=self.server)

        # Packet count is incremented every time a round trip is finished.
        self.packet_count = 0
        self.packet_count_mutex = threading.Lock()

        print(f'{self} has been initialized')

    def run(self) -> None:
        """
        Starts the threads.
        """
        self.client_thread.start()
        self.server_thread.start()

    def save_rtt(self) -> None:
        """
        For all received packets, calculates the RTT. Then calculates the average RTT and
        dumps this information in a text file.
        """
        # This function should never be called unless the number of packets received is equal
        # to MESSAGE_COUNT.
        assert len(self.packets_received) == MESSAGE_COUNT

        rtt_sum = sum(self.packets_received[index] - self.packets_sent[index]
                      for index in self.packets_received)
        rtt_average = rtt_sum / MESSAGE_COUNT

        with open(self.output_filename, 'w') as outfile:
            outfile.write('{}\n'.format(rtt_average))

        print(f'saved {self.output_filename}: {rtt_average}')

    def server(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((BIND_ADDRESS, self.own_port))

        while True:
            data_in, client_address = sock.recvfrom(BUFFER_SIZE)
            message = Message.from_binary(data_in)

            with self.packet_count_mutex:
                count = self.packet_count

            if message.sender_id != OWN_SENDER_ID:
                # The message was sent by the neighbor, so just echo it back.
                sock.sendto(data_in, self.neighbor_address)
            elif count < MESSAGE_COUNT:
                # The message was sent by us, and then received back from the neighbor node.
                # Record this packet's received timestamp in order to compute RTT later.
                self.packets_received[message.index] = get_now_timestamp()

                with self.packet_count_mutex:
                    self.packet_count += 1
                    count = self.packet_count
                if count == MESSAGE_COUNT:
                    self.save_rtt()

    def client(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        index = 0

        with self.packet_count_mutex:
            count = self.packet_count

        while count < MESSAGE_COUNT:
            data_out = Message(OWN_SENDER_ID, index).to_binary()
            self.packets_sent[index] = get_now_timestamp()
            sock.sendto(data_out, self.neighbor_address)
            index += 1

            # Sleep in order to prevent flooding.
            sleep(CLIENT_SLEEP_INTERVAL)

            with self.packet_count_mutex:
                count = self.packet_count

    def __str__(self):
        return f'MessagingPair(this: {HOSTNAME}, other: {self.neighbor_hostname})'


if __name__ == '__main__':
    for neighbor in OWN_NEIGHBORS:
        MessagingPair(neighbor).run()
