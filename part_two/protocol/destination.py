import socket

from . import constants
from .payload import RDTPayload


class Destination:
    def __init__(self, output_filename, experiment_id: int = 1):
        self.output_filename = output_filename
        self.experiment_id = experiment_id

    def run(self):
        if self.experiment_id == 1:
            self.exp1()
        elif self.experiment_id == 2:
            self.exp2()
        else:
            raise Exception("Invalid experiment ID passed to Source")

    def assemble_file(self, packets):
        file_bytes = b''
        for packet in packets:
            file_bytes += packet.payload
        with open(self.output_filename, 'wb') as outfile:
            outfile.write(file_bytes)

    def exp1(self):
        sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        forwarding_host = socket.gethostbyname("r3")
        forwarding_port = constants.BASE_PORT + constants.SENDER_IDS["r3"]
        forwarding_address = forwarding_host, forwarding_port

        sock_in.bind(("", 10004))

        received = []
        to_ack = 0
        done = False

        while not done:
            data_in, client_address = sock_in.recvfrom(constants.UDP_BUFFER_SIZE)
            packet = RDTPayload.from_binary(data_in)

            if packet.sequence_number == to_ack:
                print(f"received packet {packet.sequence_number}")

                to_ack += 1

                if packet.final:
                    done = True

                received.append(packet)
            else:
                print(f"packet discarded")

            ack = RDTPayload(
                sequence_number=to_ack,
                ack=True,
                final=done,
            )
            sock_out.sendto(ack.to_binary(), forwarding_address)
            print(f"acked {ack.sequence_number}")

        print("Assembling file...")
        self.assemble_file(received)
        print("Assembling finished.")

    def exp2(self):
        pass
