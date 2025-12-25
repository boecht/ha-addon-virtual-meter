"""Add-on entry point and pipeline wiring."""

from __future__ import annotations

import logging
from contextlib import suppress

from aiohttp import web

from .assembler import build_dynamic_payloads
from .cache import set_payloads
from .config import load_settings
from .consumer import HttpConsumer, ConsumerSnapshot
from .identity import device_id, device_mac
from .provider import create_app
from .serializer import decode, encode
from .payload_templates import (
    DEVICE_INFO_TEMPLATE,
    EMDATA_STATUS_TEMPLATE,
    EM_CONFIG_TEMPLATE,
)
from . import mdns as mdns_module


def normalize_device_mac(value: str | None) -> str:
    """Normalize a MAC address to the Shelly-style uppercase format."""
    mac = value or device_mac()
    return mac.replace(":", "").upper()


def main() -> None:
    """Entrypoint for the add-on."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    settings = load_settings()
    logging.getLogger().setLevel(
        logging.DEBUG if settings.debug_logging else logging.INFO
    )
    logging.getLogger("virtual_meter.startup").info(
        "Startup (http_port=%s)", settings.http_port
    )

    device_mac_value = normalize_device_mac(settings.device_mac)
    device_id_value = device_id(device_mac_value)

    static_device_info = dict(DEVICE_INFO_TEMPLATE)
    static_device_info["mac"] = device_mac_value
    static_device_info["id"] = device_id_value

    static_payloads_by_method = {
        "Shelly.GetDeviceInfo": static_device_info,
        "EMData.GetStatus": dict(EMDATA_STATUS_TEMPLATE),
        "EM.GetConfig": dict(EM_CONFIG_TEMPLATE),
    }
    set_payloads(
        {
            method: encode(payload)
            for method, payload in static_payloads_by_method.items()
        }
    )

    app = create_app(settings, device_id_value)

    consumer = HttpConsumer(
        settings.provider_endpoint,
        settings.poll_interval_ms,
        settings.provider_username,
        settings.provider_password,
    )

    async def _handle_snapshot(snapshot: ConsumerSnapshot) -> None:
        """Decode, assemble, serialize, and cache payloads for one poll tick."""
        logger = logging.getLogger("virtual_meter.pipeline")
        try:
            payload = decode(snapshot.raw)
        except Exception:
            logger.exception("Failed to decode provider payload")
            return
        if not isinstance(payload, dict):
            logger.warning("Provider payload is not a JSON object")
            return
        if "WARNING" in payload:
            logger.warning("Provider warning response: %s", payload)
        dynamic_payloads_by_method = build_dynamic_payloads(
            payload, snapshot.fetched_at, settings, device_mac_value
        )
        set_payloads(
            {
                method: encode(body)
                for method, body in dynamic_payloads_by_method.items()
            }
        )
        logger.debug(
            "Updated dynamic payloads (methods=%s)",
            sorted(dynamic_payloads_by_method.keys()),
        )

    async def _start_background(app: web.Application) -> None:
        """Start the consumer polling task."""
        from asyncio import sleep

        await sleep(0)
        app["consumer_task"] = app.loop.create_task(consumer.start(_handle_snapshot))
        logging.getLogger("virtual_meter.poller").info("Poller task started")

    async def _cleanup(app: web.Application) -> None:
        """Stop background tasks and close resources."""
        from asyncio import sleep

        await sleep(0)
        task = app.get("consumer_task")
        if task:
            task.cancel()
            with suppress(Exception):
                await task
        await consumer.stop()
        logging.getLogger("virtual_meter.poller").info("Poller task stopped")

    app.on_startup.append(_start_background)
    app.on_cleanup.append(_cleanup)

    mdns_module.SERVICE_NAME = device_id_value
    mdns = mdns_module.start_mdns(port=settings.http_port)

    async def _mdns_cleanup(app: web.Application) -> None:
        """Stop the mDNS broadcaster on shutdown."""
        mdns.close()
        from asyncio import sleep

        await sleep(0)

    app.on_cleanup.append(_mdns_cleanup)

    web.run_app(app, host="0.0.0.0", port=settings.http_port)


if __name__ == "__main__":
    main()
