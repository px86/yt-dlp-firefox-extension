#!/usr/bin/env -S python -u

import json
import sys
import struct
import subprocess
from typing import TypedDict


class CapturedMessage(TypedDict):
    url: str


class ResponseMessage(TypedDict):
    message: str


def capture_message() -> CapturedMessage:
    """Read and decode message from stdin."""
    length_bytes = sys.stdin.buffer.read(4)
    if not length_bytes:
        sys.exit(0)
    message_length = struct.unpack("=I", length_bytes)[0]
    raw_message = sys.stdin.buffer.read(message_length)
    message = json.loads(raw_message)
    captured_message: CapturedMessage = {"url": message["url"]}
    return captured_message


def encode_message(message: str) -> bytes:
    """Encode message for transmission."""
    response: ResponseMessage = {"message": message}
    encoded_message = bytes(
        json.dumps(response, separators=(",", ":")),
        encoding="UTF-8",
    )
    return encoded_message


def send_message(encoded_message: bytes) -> None:
    """Write the encoded message to stdout."""
    encoded_length = struct.pack("=I", len(encoded_message))
    sys.stdout.buffer.write(encoded_length)
    sys.stdout.buffer.write(encoded_message)
    sys.stdout.flush()


def process(message: CapturedMessage) -> None:
    """Do something with the captured message."""
    subprocess.run(["notify-send", "URL Captured", message["url"]])


if __name__ == "__main__":
    while True:
        message = capture_message()
        process(message)
        send_message(encode_message(f"captured url: {message["url"]}"))
