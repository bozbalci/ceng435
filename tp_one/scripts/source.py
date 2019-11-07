from datetime import datetime
import socket
import struct
import threading

BUFFER_SIZE = 4096


def server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('localhost', 10000)  # TODO change this

    sock.bind(server_address)

    while True:
        data_in, client_address = sock.recvfrom(BUFFER_SIZE)
        # extracted_data_in = struct.unpack('!d', data_in)
        # client_timestamp = extracted_data_in[0]
        # now = datetime.now()
        # server_timestamp = now.timestamp()
        # rtt = server_timestamp - client_timestamp
        sock.sendto(data_in, client_address)
        # print(f'[SERVER] Sent message: {data_in}')


def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = ('localhost', 10000)  # TODO change this

    while True:
        now = datetime.now()
        timestamp = now.timestamp()
        message = struct.pack('!d', timestamp)
        data_out = sock.sendto(message, server_address)
        data_in, server_address = sock.recvfrom(BUFFER_SIZE)
        received_at = datetime.now()
        timestamp_received = received_at.timestamp()
        rtt = timestamp_received - timestamp
        print(f'[CLIENT] RTT: {rtt}')


if __name__ == '__main__':
    server_thread = threading.Thread(target=server)
    client_thread = threading.Thread(target=client)

    server_thread.start()
    client_thread.start()
