import socket
import time

from . import constants
from .payload import RDTPayload


class Destination:
    def __init__(self, output_filename):
        self.output_filename = output_filename

    def assemble_file(self, packets):
        packets.sort(key=lambda p: p.sequence_number)
        file_bytes = b''
        for packet in packets:
            file_bytes += packet.payload
        with open(self.output_filename, 'wb') as outfile:
            outfile.write(file_bytes)

    def run(self, count):
        assemble = True
        if count > 1:
            assemble = False
        while count:
            self.receive_file(assemble=assemble)
            count -= 1

    def receive_file(self, assemble=True):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", 10004))

        received = []
        to_ack = 0
        done = False
        start_time = None

        while not done:
            data_in, client_address = sock.recvfrom(constants.UDP_BUFFER_SIZE)
            start_time = start_time or time.time()
            packet = RDTPayload.from_binary(data_in)

            if packet.sequence_number == to_ack:
                print(f"received packet {packet.sequence_number}")

                to_ack += 1

                if packet.final:
                    done = True

                received.append(packet)

            ack = RDTPayload(
                sequence_number=to_ack,
                ack=True,
                final=done,
            )
            sock.sendto(ack.to_binary(), client_address)
        end_time = time.time()
        down_took = end_time - start_time
        print(f"Download complete in {down_took} secs")

        if assemble:
            print("Assembling file...")
            start_time = time.time()
            self.assemble_file(received)
            end_time = time.time()
            assembly_took = end_time - start_time
            print(f"Assembled file in {assembly_took} secs")
