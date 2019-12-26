def _get_current_hostname() -> str:
    import socket
    hostname = socket.gethostname()
    ident = hostname.split('.')[0]
    return ident


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

SOURCE = 's'

DESTINATION = 'd'

ROUTERS = ['r1', 'r2', 'r3']

HOSTNAME = _get_current_hostname()

IS_ROUTER = HOSTNAME in ROUTERS

if HOSTNAME in ['s', 'r1', 'r2', 'r3', 'd']:
    OWN_NEIGHBORS = ALL_NEIGHBORS[HOSTNAME]
    OWN_SENDER_ID = SENDER_IDS[HOSTNAME]
else:
    OWN_NEIGHBORS = []
    OWN_SENDER_ID = -1

FILE_PAYLOAD_SIZE = 958

WINDOW_SIZE = 4

UDP_BUFFER_SIZE = 4096

BASE_PORT = 10000

TIMEOUT = 0.018  # seconds
