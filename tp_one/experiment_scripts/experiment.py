"""
November 21st, 2019

CENG435 - Data Comms. and Networking
Term Project - Part One: UDP Based Socket Application, Delay Measurements, Topology, etc.

This script contains application-level routing logic and end-to-end delay calculation.

Authors:
    Narmin Aliyeva - 2177269
    Berk Ozbalci - 2171791
"""
import json
import sys
from datetime import datetime
import socket
import struct
from time import sleep

# The number of messages to send before calculating RTT averages. The higher the number, the more
# accurate the result will be.
MESSAGE_COUNT = 100

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

# The output filename format. Extension is the file extension.
OUTPUT_FILENAME_FORMAT = 'end_to_end_costs.{extension}'

# The path to the routing information file.
ROUTE_FILE = 'route.json'

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
        double timestamp: The timestamp at which this message was generated.
    """
    structure = '!d'  # struct packing format, '!' indicates network byte-order

    def __init__(self, timestamp=None) -> None:
        if not timestamp:
            timestamp = get_now_timestamp()
        self.timestamp = timestamp

    @classmethod
    def from_binary(cls, binary: bytes) -> 'Message':
        timestamp, *_ = struct.unpack(cls.structure, binary)
        return cls(timestamp)

    def to_binary(self) -> bytes:
        return struct.pack(self.structure, self.timestamp)


def parse_routing_information(input_filename):
    with open(input_filename, 'r') as infile:
        route = json.load(infile)
    return route


def initial_node(next_hostname):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    next_host = socket.gethostbyname(next_hostname)
    next_port = BASE_PORT + OWN_SENDER_ID
    next_address = next_host, next_port

    while True:
        data_out = Message().to_binary()
        sock.sendto(data_out, next_address)
        sleep(CLIENT_SLEEP_INTERVAL)


def middle_node(prev_hostname, next_hostname):
    sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    prev_port = BASE_PORT + SENDER_IDS[prev_hostname]
    next_host = socket.gethostbyname(next_hostname)
    next_port = BASE_PORT + OWN_SENDER_ID
    next_address = next_host, next_port

    sock_in.bind((BIND_ADDRESS, prev_port))

    while True:
        data_in, client_address = sock_in.recvfrom(BUFFER_SIZE)
        sock_out.sendto(data_in, next_address)


def final_node(prev_hostname):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    prev_port = BASE_PORT + SENDER_IDS[prev_hostname]

    sock.bind((BIND_ADDRESS, prev_port))

    received_count = 0
    delays = []

    while received_count < MESSAGE_COUNT:
        data_in, client_address = sock.recvfrom(BUFFER_SIZE)
        received_timestamp = get_now_timestamp()
        message = Message.from_binary(data_in)
        sent_timestamp = message.timestamp
        delay = received_timestamp - sent_timestamp
        delays.append(delay)
        received_count += 1

    output_filename = OUTPUT_FILENAME_FORMAT.format(extension='json')

    with open(output_filename, 'w') as outfile:
        json.dump(delays, outfile)

    print(f'saved end-to-end delay data to {output_filename}')


if __name__ == '__main__':
    route = parse_routing_information(ROUTE_FILE)

    if HOSTNAME not in route:
        print(f'{HOSTNAME} was not found in route, exiting...')
        sys.exit(1)

    chain_index = route.index(HOSTNAME)

    if chain_index == 0:
        next_hostname = route[chain_index + 1]
        initial_node(next_hostname)
    elif chain_index == len(route) - 1:
        prev_hostname = route[chain_index - 1]
        final_node(prev_hostname)
    else:
        prev_hostname = route[chain_index - 1]
        next_hostname = route[chain_index + 1]
        middle_node(prev_hostname, next_hostname)
