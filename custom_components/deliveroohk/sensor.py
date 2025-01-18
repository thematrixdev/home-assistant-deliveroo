"""Support for Deliveroo HK sensors."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
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
from homeassistant.util.dt import utcnow

from .const import (
    ACTIVE_ORDER_SCAN_INTERVAL,
    API_ENDPOINT,
    API_ORDER_STATUS_ENDPOINT,
    ADVISORY_MULTI_ORDER_TC,
    STATE_MULTI_ORDER_TC,
    STATE_MULTI_ORDER_EN,
    CONF_TOKEN,
    DEFAULT_TIMEZONE,
    DOMAIN,
    LANG_EN,
    LANG_TC,
    LOCALE_TC,
    SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Deliveroo HK sensor based on a config entry."""
    coordinator = DeliverooHKCoordinator(hass, entry.data[CONF_TOKEN], entry.data.get("locale", "en"))
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([DeliverooHKSensor(coordinator)], True)


class DeliverooHKCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, token: str, locale: str) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.token = token
        self.locale = locale
        self.session = aiohttp_client.async_get_clientsession(hass)
        self._active_order = False
        self._last_update = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via API."""
        try:
            current_time = utcnow()
            
            # If we have an active order and it's been less than SCAN_INTERVAL since last update,
            # but more than ACTIVE_ORDER_SCAN_INTERVAL, force an update
            if (self._active_order and self._last_update and 
                current_time - self._last_update > ACTIVE_ORDER_SCAN_INTERVAL):
                self.update_interval = ACTIVE_ORDER_SCAN_INTERVAL
            
            # Set language based on locale
            lang = LANG_TC if self.locale == LOCALE_TC else LANG_EN
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "accept-language": lang
            }
            params = {"limit": "1", "offset": "0", "include_ugc": "true"}

            _LOGGER.debug(
                "Requesting order history - URL: %s, Headers: %s, Params: %s",
                API_ENDPOINT,
                headers,
                params,
            )

            async with self.session.get(
                API_ENDPOINT, headers=headers, params=params
            ) as response:
                if response.status != 200:
                    _LOGGER.error("Failed to get order data: %s", response.status)
                    self._active_order = False
                    self.update_interval = SCAN_INTERVAL
                    return {}

                data = await response.json()
                _LOGGER.debug("Order history response: %s", data)

                if not data.get("orders"):
                    self._active_order = False
                    self.update_interval = SCAN_INTERVAL
                    return {"state": "IDLE"}

                order = data["orders"][0]
                if order.get("status") == "DELIVERED":
                    self._active_order = False
                    self.update_interval = SCAN_INTERVAL
                    return {"state": "IDLE"}

                # Get detailed order status
                order_id = order["id"]
                status_url = API_ORDER_STATUS_ENDPOINT.format(id=order_id)
                
                _LOGGER.debug(
                    "Requesting order status - URL: %s, Headers: %s",
                    status_url,
                    headers,
                )

                async with self.session.get(
                    status_url,
                    headers=headers,
                ) as status_response:
                    if status_response.status != 200:
                        _LOGGER.error(
                            "Failed to get order status: %s", status_response.status
                        )
                        return {}

                    status_data = await status_response.json()
                    _LOGGER.debug("Order status response: %s", status_data)
                    
                    attributes = {}
                    
                    if "data" in status_data and "attributes" in status_data["data"]:
                        attrs = status_data["data"]["attributes"]
                        
                        # Get processing steps
                        processing_steps = attrs.get("processing_steps", [])
                        
                        # Find current step based on is_current flag
                        current_step = None
                        for step in processing_steps:
                            if step.get("is_current", False):
                                current_step = step["title"]
                                # Check for multi-order delivery
                                if (current_step == "派送中" and 
                                    attrs.get("advisory", "").find(ADVISORY_MULTI_ORDER_TC) != -1):
                                    current_step = (STATE_MULTI_ORDER_TC 
                                                  if self.locale == LOCALE_TC 
                                                  else STATE_MULTI_ORDER_EN)
                                break
                        
                        # If no current step found (shouldn't happen), use first step
                        if current_step is None and processing_steps:
                            current_step = processing_steps[0]["title"]
                        
                        # Add optional attributes if they exist
                        for key in ["eta_message", "message", "fulfillment_type", "updated_at", "current_progress_percentage", "advisory"]:
                            if key in attrs:
                                attributes[key] = attrs[key]
                        
                        # Set active order flag and update interval
                        self._active_order = True
                        self.update_interval = ACTIVE_ORDER_SCAN_INTERVAL
                        self._last_update = current_time
                        
                        return {"state": current_step or "UNKNOWN", "attributes": attributes}

                    return {}

        except aiohttp.ClientError as error:
            _LOGGER.error("Error fetching data: %s", error)
            self._active_order = False
            self.update_interval = SCAN_INTERVAL
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
