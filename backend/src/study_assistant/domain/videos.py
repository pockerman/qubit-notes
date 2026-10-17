"""Reads a video's duration from its container, MP4 or WebM, without any media library."""

import struct

VIDEO_TYPES = {".mp4": "video/mp4", ".webm": "video/webm"}


def duration_seconds(content: bytes) -> float | None:
    """the video's duration, or None if it can't be read"""
    try:
        if content[4:8] == b"ftyp":
            return _mp4_duration(content)
        if content[:4] == b"\x1a\x45\xdf\xa3":
            return _webm_duration(content)
    except (IndexError, struct.error, ValueError):
        return None
    return None


def _mp4_boxes(data: bytes, start: int, end: int):
    """the (type, payload start, payload end) of each box between start and end"""
    position = start
    while position + 8 <= end:
        size, kind = struct.unpack(">I4s", data[position : position + 8])
        header = 8
        if size == 1:
            size = struct.unpack(">Q", data[position + 8 : position + 16])[0]
            header = 16
        elif size == 0:
            size = end - position
        if size < header:
            return
        yield kind, position + header, min(position + size, end)
        position += size


def _mp4_duration(data: bytes) -> float | None:
    for kind, start, end in _mp4_boxes(data, 0, len(data)):
        if kind != b"moov":
            continue
        for inner, payload, _ in _mp4_boxes(data, start, end):
            if inner != b"mvhd":
                continue
            version = data[payload]
            if version == 1:
                timescale, duration = struct.unpack(">IQ", data[payload + 20 : payload + 32])
            else:
                timescale, duration = struct.unpack(">II", data[payload + 12 : payload + 20])
            return duration / timescale if timescale else None
    return None


SEGMENT, INFO, TIMECODE_SCALE, DURATION = 0x18538067, 0x1549A966, 0x2AD7B1, 0x4489


def _ebml_id(data: bytes, position: int) -> tuple[int, int]:
    first = data[position]
    length = next(n for n in range(1, 5) if first & (0x80 >> (n - 1)))
    return int.from_bytes(data[position : position + length], "big"), position + length


def _ebml_size(data: bytes, position: int) -> tuple[int | None, int]:
    first = data[position]
    length = next(n for n in range(1, 9) if first & (0x80 >> (n - 1)))
    value = first & (0xFF >> length)
    for byte in data[position + 1 : position + length]:
        value = (value << 8) | byte
    unknown = value == (1 << (7 * length)) - 1
    return (None if unknown else value), position + length


def _ebml_elements(data: bytes, start: int, end: int):
    position = start
    while position < end:
        element, position = _ebml_id(data, position)
        size, position = _ebml_size(data, position)
        stop = end if size is None else position + size
        yield element, position, stop
        position = stop


def _webm_duration(data: bytes) -> float | None:
    for element, start, end in _ebml_elements(data, 0, len(data)):
        if element != SEGMENT:
            continue
        for inner, payload, stop in _ebml_elements(data, start, end):
            if inner != INFO:
                continue
            scale, duration = 1_000_000, None
            for field, value_start, value_end in _ebml_elements(data, payload, stop):
                value = data[value_start:value_end]
                if field == TIMECODE_SCALE:
                    scale = int.from_bytes(value, "big")
                elif field == DURATION:
                    duration = struct.unpack(">f" if len(value) == 4 else ">d", value)[0]
            return duration * scale / 1e9 if duration is not None else None
    return None
