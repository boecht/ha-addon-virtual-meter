"""Zeroconf mDNS advertising."""

from __future__ import annotations

import socket
from dataclasses import dataclass

from zeroconf import ServiceInfo, Zeroconf

SERVICE_TYPE = "_http._tcp.local."
SERVICE_NAME = "VirtualPro3EM"
TXT_RECORDS = {"gen": "2", "app": "Pro3EM"}


def _resolve_ip() -> str:
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
        if ip.startswith("127."):
            raise OSError
        return ip
    except OSError:
        return "0.0.0.0"


@dataclass
class MDNSAdvertiser:
    zeroconf: Zeroconf
    info: ServiceInfo

    def close(self) -> None:
        self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()


def start_mdns(port: int = 80) -> MDNSAdvertiser:
    """Start zeroconf service advertisement."""
    zeroconf = Zeroconf()
    ip = _resolve_ip()
    info = ServiceInfo(
        SERVICE_TYPE,
        f"{SERVICE_NAME}.{SERVICE_TYPE}",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties=TXT_RECORDS,
        server=f"{SERVICE_NAME}.local.",
    )
    zeroconf.register_service(info)
    return MDNSAdvertiser(zeroconf=zeroconf, info=info)
