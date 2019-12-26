import socket
import time

from . import constants
from .payload import ChunkIndexedFile, RDTPayload


class Source:
    def __init__(self, input_filename, experiment_id: int = 1):
        self.experiment_id = experiment_id
        self.chunk = ChunkIndexedFile(input_filename)
        self.packets = [
            RDTPayload(sequence_number=i, ack=False, final=False, payload=self.chunk[i])
            for i in range(len(self.chunk))
        ]
        self.packets[-1].final = True

    def run(self):
        if self.experiment_id == 1:
            self.exp1()
        elif self.experiment_id == 2:
            self.exp2()
        else:
            raise Exception("Invalid experiment ID passed to Source")

    def exp1(self):
        start_time = time.time()
        sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        forwarding_host = socket.gethostbyname("r3")
        forwarding_port = constants.BASE_PORT + constants.SENDER_IDS["r3"]
        forwarding_address = forwarding_host, forwarding_port

        sock_in.bind(("", 10000))
        sock_in.settimeout(constants.TIMEOUT)

        done = False
        window_size = constants.WINDOW_SIZE
        last_sent = 0
        last_acked = 0
        last_seq = len(self.packets)

        while not done:
            while last_sent - last_acked < window_size and last_sent < last_seq:
                data_out = self.packets[last_sent]
                sock_out.sendto(data_out.to_binary(), forwarding_address)
                print(f"transmitted packet {data_out.sequence_number}")
                last_sent += 1

            try:
                data_in, client_address = sock_in.recvfrom(constants.UDP_BUFFER_SIZE)
                data_in = RDTPayload.from_binary(data_in)

                print(f"received ack of packet {data_in.sequence_number}")

                if data_in.final and data_in.ack:
                    print("last ack was final, terminating...")
                    done = True

                last_acked = max(last_acked, data_in.sequence_number)
            except socket.timeout:
                for i in range(last_acked, last_sent):
                    print(f"timed out, re-transmitting packet {i}")
                    data_out = self.packets[i]
                    sock_out.sendto(data_out.to_binary(), forwarding_address)

        end_time = time.time()
        took = end_time - start_time
        print(f"Finished uploading, took {took} secs")

    def exp2(self):
        pass
