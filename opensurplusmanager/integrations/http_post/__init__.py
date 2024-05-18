from dataclasses import dataclass, field
from typing import Dict

import aiohttp

from opensurplusmanager.core import Core
from opensurplusmanager.integrations.http_post.entity import HTTPPostEntity
from opensurplusmanager.models.integration import ControlIntegration
from opensurplusmanager.utils import logger


@dataclass
class HTTPPost(ControlIntegration):
    core: Core
    client: aiohttp.ClientSession = None
    turn_on_entries: Dict[str, HTTPPostEntity] = field(default_factory=dict)
    turn_off_entries: Dict[str, HTTPPostEntity] = field(default_factory=dict)
    regulate_entries: Dict[str, HTTPPostEntity] = field(default_factory=dict)

    def __load_devices(self):
        for device in self.core.config.get("devices", []):
            entry_type = device["control_integration"]
            logger.debug("Loading device %s", device["name"])
            # Check if exists 'turn_on' in entry type
            if "turn_on" in entry_type and entry_type["turn_on"]["name"] == "http_post":
                self.turn_on_entries[device["name"]] = HTTPPostEntity(
                    name=device["name"],
                    path=entry_type["turn_on"]["path"],
                    method=entry_type["turn_on"]["method"],
                    headers=entry_type["turn_on"]["headers"],
                    body=entry_type["turn_on"]["body"],
                )

            # Check if exists 'turn_off' in entry type
            if (
                "turn_off" in entry_type
                and entry_type["turn_off"]["name"] == "http_post"
            ):
                self.turn_off_entries[device["name"]] = HTTPPostEntity(
                    name=device["name"],
                    path=entry_type["turn_off"]["path"],
                    method=entry_type["turn_off"]["method"],
                    headers=entry_type["turn_off"]["headers"],
                    body=entry_type["turn_off"]["body"],
                )

            # Check if exists 'regulate' in entry type
            if (
                "regulate" in entry_type
                and entry_type["regulate"]["name"] == "http_post"
            ):
                self.regulate_entries[device["name"]] = HTTPPostEntity(
                    name=device["name"],
                    path=entry_type["regulate"]["path"],
                    method=entry_type["regulate"]["method"],
                    headers=entry_type["regulate"]["headers"],
                    body=entry_type["regulate"]["body"],
                )
            device_name = device["name"]
            self.core.add_control_integration(device_name, self)

    def __init__(self, core: Core):
        logger.info("Initializing HTTP Post integration...")
        self.core = core
        self.turn_on_entries: Dict[str, HTTPPostEntity] = {}
        self.turn_off_entries: Dict[str, HTTPPostEntity] = {}
        self.regulate_entries: Dict[str, HTTPPostEntity] = {}
        self.__load_devices()
        # Load aiohttp client
        self.client = aiohttp.ClientSession()

    async def run(self) -> None:
        logger.info("Running HTTP Post integration...")

    async def turn_on(self, device_name):
        logger.info("Turning on device %s", device_name)

    async def turn_off(self, device_name):
        logger.info("Turning off device %s", device_name)
        entity = self.turn_off_entries.get(device_name)
        if entity:
            async with self.client.post(
                entity.path, headers=entity.headers, json=entity.body
            ) as response:
                logger.debug(
                    "Got response from device %s: %s", entity.name, response.status
                )
        else:
            logger.error("Device %s not found in control integration", device_name)

    async def regulate(self, device_name, power):
        pass


async def setup(core: Core) -> bool:
    HTTPPost(core)

    return True