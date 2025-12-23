"""Add-on entry point."""

from __future__ import annotations

import logging

from aiohttp import web

from .provider import create_app
from .config import load_settings
from . import mdns as mdns_module
from .shelly import device_id, device_mac


def main() -> None:
    """Entrypoint for the add-on.

    Pseudocode:
    - Load settings from /data/options.json
    - Initialize HTTP source consumer and start background polling
    - Start mDNS advertisement for discovery
    - Run aiohttp app on port 80 (host network)
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = load_settings()
    logging.getLogger().setLevel(
        logging.DEBUG if settings.debug_logging else logging.INFO
    )
    logging.getLogger("virtual_meter.startup").info(
        "Starting add-on (http_port=%s)",
        settings.http_port,
    )

    app = create_app(settings)

    mac = settings.device_mac or device_mac()
    mdns_module.SERVICE_NAME = device_id(mac)
    mdns = mdns_module.start_mdns(port=settings.http_port)

    async def _cleanup(app: web.Application) -> None:
        mdns.close()
        from asyncio import sleep

        await sleep(0)

    app.on_cleanup.append(_cleanup)

    web.run_app(app, host="0.0.0.0", port=settings.http_port)


if __name__ == "__main__":
    main()
