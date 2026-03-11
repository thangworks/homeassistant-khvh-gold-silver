"""Sensor platform for Kim Khanh Viet Hung - Gia Vang Bac."""

from __future__ import annotations

from dataclasses import dataclass
import re

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import ATTR_GROUP, ATTR_LAST_FETCH, ATTR_SOURCE_URL, COORDINATOR, DEFAULT_NAME, DOMAIN
from .coordinator import KimKhanhPriceCoordinator


def _row_key(group: str, name: str) -> str:
    """Create stable row key."""
    return slugify(f"{group}_{name}")


def _compact_row_name(name: str) -> str:
    """Normalize row name for shorter, cleaner entity names."""
    normalized = re.sub(r"\s+", " ", name).strip()
    normalized = re.sub(r"\(\s*", "(", normalized)
    normalized = re.sub(r"\s*\)", ")", normalized)
    normalized = re.sub(r"^\s*khvh\s*", "", normalized, flags=re.IGNORECASE)
    return normalized


@dataclass(frozen=True, kw_only=True)
class KimKhanhSensorDescription(SensorEntityDescription):
    """Sensor description."""

    field: str


DESCRIPTIONS: tuple[KimKhanhSensorDescription, ...] = (
    KimKhanhSensorDescription(
        key="buy",
        name="Buy",
        field="buy",
        icon="mdi:cash-plus",
        native_unit_of_measurement="VND",
    ),
    KimKhanhSensorDescription(
        key="sell",
        name="Sell",
        field="sell",
        icon="mdi:cash-minus",
        native_unit_of_measurement="VND",
    ),
    KimKhanhSensorDescription(
        key="exchange",
        name="Exchange",
        field="exchange",
        icon="mdi:swap-horizontal",
        native_unit_of_measurement="VND",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from config entry."""
    coordinator: KimKhanhPriceCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    entities: list[KimKhanhPriceSensor] = []
    for row in coordinator.data["rows"]:
        row_id = _row_key(row.group, row.name)
        for desc in DESCRIPTIONS:
            entities.append(
                KimKhanhPriceSensor(
                    coordinator=coordinator,
                    entry_id=entry.entry_id,
                    row_id=row_id,
                    row_name=row.name,
                    group=row.group,
                    description=desc,
                )
            )

    async_add_entities(entities)


class KimKhanhPriceSensor(CoordinatorEntity[KimKhanhPriceCoordinator], SensorEntity):
    """Representation of Kim Khanh price sensor."""

    entity_description: KimKhanhSensorDescription

    def __init__(
        self,
        coordinator: KimKhanhPriceCoordinator,
        entry_id: str,
        row_id: str,
        row_name: str,
        group: str,
        description: KimKhanhSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._row_id = row_id
        self._group = group
        self._attr_has_entity_name = False
        self._attr_name = f"{_compact_row_name(row_name)} {description.name}"
        self._attr_unique_id = f"{entry_id}_{row_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=DEFAULT_NAME,
            manufacturer="Kim Khanh Viet Hung",
            model="KHVH Online Price Board",
            configuration_url=coordinator.url,
        )

    @property
    def native_value(self):
        """Return sensor value."""
        for row in self.coordinator.data["rows"]:
            if _row_key(row.group, row.name) == self._row_id:
                return getattr(row, self.entity_description.field)
        return None

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        return {
            ATTR_GROUP: self._group,
            ATTR_LAST_FETCH: self.coordinator.data.get("fetched_at"),
            ATTR_SOURCE_URL: self.coordinator.data.get("source_url"),
        }
