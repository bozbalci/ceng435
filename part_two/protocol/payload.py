import hashlib
import math
import struct

from .constants import FILE_PAYLOAD_SIZE


class ChunkIndexedFile:
    """
    Reads a binary file and provides an interface to access its chunks in an indexed fashion.

    >>> fp = ChunkIndexedFile("input.txt")
    >>> len(fp)
    10
    >>> for i in range(len(fp)):
    ...    chunk = fp[i]
    ...    # ... process chunk ...
    """
    def __init__(self, input_path):
        self.input_path = input_path
        self.slice_size = FILE_PAYLOAD_SIZE
        with open(self.input_path, 'rb') as infile:
            self.payload = infile.read()
        self.size = len(self.payload)
        self.slices = math.ceil(self.size / self.slice_size)

    def slice(self, n):
        start = n * self.slice_size
        end = (n + 1) * self.slice_size
        return self.payload[start:end]

    __getitem__ = slice

    def __len__(self):
        return self.slices


def checksum(s: bytes) -> str:
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


class RDTPayload:
    header_format = '!??LL'
    header_size = struct.calcsize(header_format)

    def __init__(
        self,
        sequence_number: int,
        ack: bool = False,
        final: bool = False,
        payload: bytes = b'',
    ):
        self.ack = ack
        self.final = final
        self.sequence_number = sequence_number
        self.payload = payload
        self.length = len(self.payload)
        self.checksum = checksum(self.payload).encode()

    def to_binary(self) -> bytes:
        header = struct.pack(self.header_format,
                             self.ack,
                             self.final,
                             self.sequence_number,
                             self.length)
        return header + self.payload + self.checksum

    @classmethod
    def from_binary(cls, data_in: bytes) -> 'RDTPayload':
        header_data = data_in[:cls.header_size]

        ack, final, sequence_number, length = struct.unpack(cls.header_format, header_data)
        payload = data_in[cls.header_size:cls.header_size+length]
        checksum_ = data_in[-32:]  # checksum is always 32 bytes

        obj = cls(
            sequence_number=sequence_number,
            ack=ack,
            final=final,
            payload=payload,
        )

        if obj.checksum != checksum_:
            raise ValueError("Checksum mismatch")
        return obj
