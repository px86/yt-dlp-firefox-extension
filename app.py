#!/usr/bin/env -S python -u

import json
import os
import sys
import struct
import subprocess
import configparser
import logging
from typing import TypedDict, Literal


class CapturedMessage(TypedDict):
    action: Literal["video", "audio-only"]
    url: str


class ResponseMessage(TypedDict):
    message: str


class Config(TypedDict):
    DownloadDir: str
    LogFile: str


def capture_message() -> CapturedMessage:
    """Read and decode message from stdin."""
    length_bytes = sys.stdin.buffer.read(4)
    if not length_bytes:
        sys.exit(0)
    message_length = struct.unpack("=I", length_bytes)[0]
    raw_message = sys.stdin.buffer.read(message_length)
    message = json.loads(raw_message)
    captured_message: CapturedMessage = {
        "url": message["url"],
        "action": message["action"],
    }
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

    if os.fork() > 0:
        send_message(encode_message(f"captured url: {message["url"]}"))
        sys.exit(0)

    config = parse_config()

    logging.basicConfig(
        filename=config["LogFile"],
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s: %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("starting download for %s", message["url"])
    subprocess.run(["notify-send", "Downloading...", message["url"]])

    proc_args = ["yt-dlp", message["url"]]
    if message["action"] == "audio-only":
        proc_args.append("--extract-audio")
    proc = subprocess.run(proc_args, cwd=config["DownloadDir"])
    logger.info("yt-dlp subprocess exited with code %i", proc.returncode)

    if proc.returncode == 0:
        subprocess.run(["notify-send", "Download completed!", f"for {message["url"]}"])
        logger.info("exiting with code 0")
        sys.exit(0)

    subprocess.run(["notify-send", "Download failed!", f"for {message["url"]}"])
    logger.info("exiting with code 1")
    sys.exit(1)


def parse_config() -> Config:
    parent_dir = os.path.dirname(__file__)
    default_download_dir = os.path.join(parent_dir, "downloads")
    default_log_file = os.path.join(parent_dir, "log.txt")

    cp = configparser.ConfigParser()
    cp.read(os.path.join(os.path.dirname(__file__), "config.ini"))
    download_dir = os.path.expanduser(
        cp.get("DEFAULT", "DownloadDir", fallback=default_download_dir)
    )
    os.makedirs(download_dir, exist_ok=True)

    log_file = os.path.expanduser(
        cp.get("DEFAULT", "LogFile", fallback=default_log_file)
    )

    config: Config = {"DownloadDir": download_dir, "LogFile": log_file}

    return config


if __name__ == "__main__":
    message = capture_message()
    process(message)
