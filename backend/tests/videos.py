"""Writes minimal video files with a given duration, for tests: just enough container for the duration to be read."""

import struct


def _box(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", 8 + len(payload)) + kind + payload


def make_mp4(seconds: float) -> bytes:
    timescale = 1000
    # mvhd version 0: version and flags, creation and modification times, timescale, duration, then the rest
    mvhd = struct.pack(">I II II", 0, 0, 0, timescale, int(seconds * timescale)) + bytes(80)
    return _box(b"ftyp", b"isom\x00\x00\x02\x00isomiso2mp41") + _box(b"moov", _box(b"mvhd", mvhd)) + _box(b"mdat", b"")


def _ebml(element: int, payload: bytes) -> bytes:
    element_bytes = element.to_bytes((element.bit_length() + 7) // 8, "big")
    # an 8-byte size: 0x01 marker, then 7 bytes
    return element_bytes + b"\x01" + len(payload).to_bytes(7, "big") + payload


def make_webm(seconds: float) -> bytes:
    header = _ebml(0x1A45DFA3, _ebml(0x4282, b"webm"))
    info = _ebml(
        0x1549A966, _ebml(0x2AD7B1, (1_000_000).to_bytes(3, "big")) + _ebml(0x4489, struct.pack(">d", seconds * 1000))
    )
    return header + _ebml(0x18538067, info)
