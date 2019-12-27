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

    def run(self, count):
        results = []
        while count:
            if int(self.experiment_id) == 1:
                res = self.exp1()
                results.append(res)
            elif int(self.experiment_id) == 2:
                self.exp2()
            else:
                raise Exception("Invalid experiment ID passed to Source")
            count -= 1
        return results

    def exp1(self):
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        forwarding_host = socket.gethostbyname("r3")
        forwarding_port = constants.BASE_PORT + constants.SENDER_IDS["r3"]
        forwarding_address = forwarding_host, forwarding_port

        sock.bind(("", 10000))
        sock.settimeout(constants.TIMEOUT)

        done = False
        window_size = constants.WINDOW_SIZE
        last_sent = 0
        last_acked = 0
        last_seq = len(self.packets)

        while not done:
            while last_sent - last_acked < window_size and last_sent < last_seq:
                data_out = self.packets[last_sent]
                sock_out.sendto(data_out.to_binary(), forwarding_address)
                last_sent += 1

            try:
                data_in, client_address = sock.recvfrom(constants.UDP_BUFFER_SIZE)
                data_in = RDTPayload.from_binary(data_in)

                print(f"delivered packet {data_in.sequence_number}")

                if data_in.final and data_in.ack:
                    done = True

                last_acked = max(last_acked, data_in.sequence_number)
            except socket.timeout:
                for i in range(last_acked, last_sent):
                    data_out = self.packets[i]
                    sock_out.sendto(data_out.to_binary(), forwarding_address)

        end_time = time.time()
        took = end_time - start_time
        print(f"Finished uploading, took {took} secs")
        return took

    def exp2(self):
        start_time = time.time()

        r1_host = socket.gethostbyname("r1")
        r1_port = constants.BASE_PORT + constants.SENDER_IDS["r1"]
        r1_address = r1_host, r1_port
        r2_host = socket.gethostbyname("r2")
        r2_port = constants.BASE_PORT + constants.SENDER_IDS["r2"]
        r2_address = r2_host, r2_port

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", 10000))
        sock.settimeout(constants.TIMEOUT)

        done = False
        window_size = constants.WINDOW_SIZE
        last_sent = 0
        last_acked = 0
        last_seq = len(self.packets)

        while not done:
            while last_sent - last_acked < window_size and last_sent < last_seq:
                data_out = self.packets[last_sent]
                data_out_bytes = data_out.to_binary()
                sock_out.sendto(data_out_bytes, r1_address)
                sock_out.sendto(data_out_bytes, r2_address)
                last_sent += 1

            try:
                data_in, client_address = sock.recvfrom(constants.UDP_BUFFER_SIZE)
                data_in = RDTPayload.from_binary(data_in)
                client_host, _ = client_address
                if client_host == r1_host:
                    from_ = "r1"
                else:
                    from_ = "r2"

                print(f"delivered packet {data_in.sequence_number} over {from_}")

                if data_in.final and data_in.ack:
                    done = True

                last_acked = max(last_acked, data_in.sequence_number)
            except socket.timeout:
                for i in range(last_acked, last_sent):
                    data_out = self.packets[i]
                    data_out_bytes = data_out.to_binary()
                    sock_out.sendto(data_out_bytes, r1_address)
                    sock_out.sendto(data_out_bytes, r2_address)

        end_time = time.time()
        took = end_time - start_time
        print(f"Finished uploading, took {took} secs")
        return took
