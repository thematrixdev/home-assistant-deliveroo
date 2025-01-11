"""Support for Deliveroo HK sensors."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    API_ENDPOINT,
    API_ORDER_STATUS_ENDPOINT,
    CONF_TOKEN,
    DEFAULT_TIMEZONE,
    DOMAIN,
    SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Deliveroo HK sensor based on a config entry."""
    coordinator = DeliverooHKCoordinator(hass, entry.data[CONF_TOKEN])
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([DeliverooHKSensor(coordinator)], True)


class DeliverooHKCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, token: str) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.token = token
        self.session = aiohttp_client.async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via API."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {"limit": "1", "offset": "0", "include_ugc": "true"}

            async with self.session.get(
                API_ENDPOINT, headers=headers, params=params
            ) as response:
                if response.status != 200:
                    _LOGGER.error("Failed to get order data: %s", response.status)
                    return {}

                data = await response.json()
                if not data.get("orders"):
                    return {"state": "IDLE"}

                order = data["orders"][0]
                if order.get("status") == "DELIVERED":
                    return {"state": "IDLE"}

                # Get detailed order status
                order_id = order["id"]
                async with self.session.get(
                    API_ORDER_STATUS_ENDPOINT.format(id=order_id),
                    headers=headers,
                ) as status_response:
                    if status_response.status != 200:
                        _LOGGER.error(
                            "Failed to get order status: %s", status_response.status
                        )
                        return {}

                    status_data = await status_response.json()
                    attributes = {}
                    
                    if "data" in status_data and "attributes" in status_data["data"]:
                        attrs = status_data["data"]["attributes"]
                        state = attrs.get("ui_status", "UNKNOWN")
                        
                        # Add optional attributes if they exist
                        for key in ["eta_message", "message", "fulfillment_type", "updated_at", "current_progress_percentage"]:
                            if key in attrs:
                                attributes[key] = attrs[key]
                        
                        return {"state": state, "attributes": attributes}

                    return {}

        except aiohttp.ClientError as error:
            _LOGGER.error("Error fetching data: %s", error)
            return {}


class DeliverooHKSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Deliveroo HK sensor."""

    def __init__(self, coordinator: DeliverooHKCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Deliveroo"
        self._attr_unique_id = "deliveroo"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("state")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data:
            return self.coordinator.data.get("attributes", {})
        return {}
