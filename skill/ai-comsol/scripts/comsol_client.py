"""Shared COMSOL mph server connection helpers."""
from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import time

import mph


DEFAULT_COMSOL_SERVER = (
    r"D:\Program Files\COMSOL\COMSOL64\Multiphysics\bin\win64\comsolmphserver.exe"
)
DEFAULT_COMSOL_PORT = 2036


def get_comsol_port() -> int:
    return int(os.environ.get("COMSOL_PORT", str(DEFAULT_COMSOL_PORT)))


def get_comsol_server() -> str:
    return os.environ.get("COMSOL_SERVER", DEFAULT_COMSOL_SERVER)


def port_is_open(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        return sock.connect_ex((host, port)) == 0


def start_comsol_server(port: int | None = None, server_path: str | None = None) -> None:
    port = get_comsol_port() if port is None else port
    server_path = get_comsol_server() if server_path is None else server_path

    if not Path(server_path).exists():
        raise FileNotFoundError(
            f"Cannot find comsolmphserver.exe: {server_path}\n"
            "Set COMSOL_SERVER to your comsolmphserver.exe path."
        )

    subprocess.Popen(
        [server_path, "-port", str(port)],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    for _ in range(90):
        if port_is_open(port):
            return
        time.sleep(1)

    raise TimeoutError(f"COMSOL mph server did not start on port {port}.")


def connect_client() -> mph.Client:
    port = get_comsol_port()
    server_path = get_comsol_server()

    try:
        if not port_is_open(port):
            start_comsol_server(port, server_path)
        return mph.Client(port=port)
    except Exception as exc:
        raise RuntimeError(
            "Cannot connect to COMSOL mph server.\n"
            f"Tried port {port} and server path: {server_path}\n"
            "If you use another port, set COMSOL_PORT before running the script.\n"
            "If COMSOL is installed elsewhere, set COMSOL_SERVER."
        ) from exc
