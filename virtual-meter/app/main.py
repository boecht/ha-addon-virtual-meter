"""Add-on entry point (stub)."""

from __future__ import annotations

import logging

from aiohttp import web

from .provider import create_app
from .config import load_settings
from .mdns import start_mdns
from .mock import create_app as create_mock_app


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
        "Starting add-on (mock_mode=%s, http_port=%s)",
        settings.mock_mode,
        settings.http_port,
    )

    if settings.mock_mode:
        app = create_mock_app(settings)
    else:
        app = create_app(settings)

    mdns = start_mdns(port=80)

    async def _cleanup(app: web.Application) -> None:
        mdns.close()
        from asyncio import sleep

        await sleep(0)

    app.on_cleanup.append(_cleanup)

    web.run_app(app, host="0.0.0.0", port=settings.http_port)


if __name__ == "__main__":
    main()
