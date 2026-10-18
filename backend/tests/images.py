"""Builds small images of each type, for tests."""

import struct
import zlib


def make_png(red: int = 200, green: int = 80, blue: int = 40, size: int = 4) -> bytes:
    """a square PNG of one colour; different colours make different images"""

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    row = b"\x00" + bytes([red, green, blue]) * size
    header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(row * size)) + chunk(b"IEND", b"")
    )


# a 1x1 GIF
GIF = bytes.fromhex("47494638396101000100800000000000ffffff21f90401000000002c00000000010001000002024401003b")


def make_image(extension: str) -> bytes:
    """an image of the type the extension names; for a type that isn't accepted, a file of that type"""
    return {
        "png": make_png(),
        # the bytes a JPEG starts with are enough for the type check
        "jpg": b"\xff\xd8\xff\xe0" + b"\x00" * 64,
        "jpeg": b"\xff\xd8\xff\xe0" + b"\x00" * 64,
        "gif": GIF,
        "webp": b"RIFF" + struct.pack("<I", 26) + b"WEBPVP8 " + b"\x00" * 18,
        "svg": b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',
        "bmp": b"BM" + b"\x00" * 64,
    }[extension]
