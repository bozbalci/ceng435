import sys
from datetime import datetime
import socket
import struct
import threading
from time import sleep

MESSAGE_COUNT = 100
BUFFER_SIZE = 4096


SENDER_IDS = {
    's': 0,
    'r1': 1,
    'r2': 2,
    'r3': 3,
    'd': 4,
}

# ALL_NEIGHBORS = {
#     's': ('r1', 'r2', 'r3'),
#     'r1': ('s', 'r2', 'd'),
#     'r2': ('s', 'r1', 'r3', 'd'),
#     'r3': ('s', 'r2', 'd'),
#     'd': ('r1', 'r2', 'r3'),
# }

ALL_NEIGHBORS = {  # TODO Debug
    's': ('r1',),
    'r1': ('s',),
    'r2': ('s', 'r1', 'r3', 'd'),
    'r3': ('s', 'r2', 'd'),
    'd': ('r1', 'r2', 'r3'),
}


def get_current_hostname():
    hostname = socket.gethostname()
    ident = hostname.split('.')[0]

    if ident not in SENDER_IDS:
        ident = 'd'

    return ident


HOSTNAME = get_current_hostname()
OWN_NEIGHBORS = ALL_NEIGHBORS[HOSTNAME]
OWN_SENDER_ID = SENDER_IDS[HOSTNAME]


class Message:
    def __init__(self, sender_id, index):
        self.sender_id = sender_id
        self.index = index

    @classmethod
    def from_binary(cls, binary):
        sender_id, message_index = struct.unpack('!ii', binary)
        return cls(sender_id, message_index)

    def to_binary(self):
        return struct.pack('!ii', self.sender_id, self.index)


class MessagingPair:
    def __init__(self, *, client_target_address, server_port, output_filename):
        self.client_target_address = client_target_address
        self.server_port = server_port
        self.packets_sent = {}
        self.packets_received = {}
        self.output_filename = output_filename
        self.client_thread = threading.Thread(target=self.client)
        self.server_thread = threading.Thread(target=self.server)
        self.packet_count = 0
        self.packet_count_mutex = threading.Lock()

        print(f'Initializing a MessagingPair, client_target_address: {client_target_address},'
              f' server port: {server_port}, output_filename: {output_filename}')

    def run(self):
        self.client_thread.start()
        self.server_thread.start()

    def save_rtt(self):
        print(f'Saving RTT to {self.output_filename}')

        rtt_sum = 0

        for index, received_timestamp in self.packets_received.items():
            sent_timestamp = self.packets_sent[index]
            rtt_sum += received_timestamp - sent_timestamp

        average_rtt = rtt_sum / MESSAGE_COUNT

        with open(self.output_filename, 'w') as outfile:
            outfile.write('{}\n'.format(average_rtt))

        print(f'Saved RTT. Hit Ctrl-C to kill process.')

    def server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('0.0.0.0', self.server_port)
        sock.bind(server_address)

        counter = 0

        while True:
            data_in, client_address = sock.recvfrom(BUFFER_SIZE)

            message = Message.from_binary(data_in)

            if message.sender_id == OWN_SENDER_ID and counter < MESSAGE_COUNT:
                counter += 1
                now = datetime.now()
                timestamp = now.timestamp()
                self.packets_received[message.index] = timestamp

                with self.packet_count_mutex:
                    self.packet_count += 1

                if counter == MESSAGE_COUNT:
                    self.save_rtt()
            else:
                sock.sendto(data_in, self.client_target_address)

    def client(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        index = 0

        with self.packet_count_mutex:
            received_count = self.packet_count

        while received_count < MESSAGE_COUNT:
            print(f'{received_count} packets received out of {MESSAGE_COUNT}')

            message = Message(OWN_SENDER_ID, index)
            data_out = message.to_binary()
            now = datetime.now()
            timestamp = now.timestamp()
            self.packets_sent[index] = timestamp
            sock.sendto(data_out, self.client_target_address)
            index += 1
            sleep(1/100)

            with self.packet_count_mutex:
                received_count = self.packet_count


if __name__ == '__main__':
    for neighbor_name in OWN_NEIGHBORS:
        neighbor_host = socket.gethostbyname(neighbor_name)
        neighbor_port = 10000 + OWN_SENDER_ID
        server_port = 10000 + SENDER_IDS[neighbor_name]

        mp = MessagingPair(client_target_address=(neighbor_host, neighbor_port),
                           server_port=server_port,
                           output_filename='link_costs_{}.txt'.format(neighbor_name))
        mp.run()
